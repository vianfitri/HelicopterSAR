import time
import threading
import struct
import wx
from pymodbus.client import ModbusTcpClient

# ----------------------------------------------------------------------
# THREAD UNTUK KONEKSI MODBUS & READ DATA (ENCODER + 4 SWITCH REDUNDANCY)
# ----------------------------------------------------------------------
class ModbusWorker(threading.Thread):
    def __init__(self, host, port, wheel_diameter_m, ppr, notify_window):
        super().__init__()
        self.host = host
        self.port = port
        self.notify_window = notify_window
        self.daemon = True
        self.running = False
        
        # Parameter Fisik Encoder & Roda
        self.wheel_diameter = wheel_diameter_m  # Meter
        self.ppr = ppr                          # Pulse Per Revolution (Autonics: 1024)
        
        # Variabel Kalkulasi
        self.last_counter = 0
        self.last_time = time.time()
        self.distance = 0.0                     # Meter
        self.speed = 0.0                        # Meter / Menit

    def run(self):
        self.running = True
        client = ModbusTcpClient(self.host, port=self.port, timeout=2)
        
        if not client.connect():
            wx.CallAfter(self.notify_window.update_status, False, "Gagal terhubung ke PLC")
            return

        wx.CallAfter(self.notify_window.update_status, True, "Terhubung ke PLC")
        
        self.last_time = time.time()

        while self.running:
            current_time = time.time()
            dt = current_time - self.last_time

            try:
                # ------------------------------------------------------
                # READ DISCRETE INPUTS (6 Bits total: Address 0 s/d 5)
                # Bit 0: Status UP
                # Bit 1: Status DOWN
                # Bit 2: HOME MAX 1 (Utama)
                # Bit 3: HOME MAX 2 (Cadangan)
                # Bit 4: LIMIT MAX 1 (Utama)
                # Bit 5: LIMIT MAX 2 (Cadangan)
                # ------------------------------------------------------
                rr_coils = client.read_discrete_inputs(address=0, count=6)
                
                # Membaca Register HSC Encoder 32-bit (V0 & V1)
                rr_regs = client.read_holding_registers(address=0, count=2)

                if not rr_coils.isError() and not rr_regs.isError():
                    status_up = rr_coils.bits[0]
                    status_down = rr_coils.bits[1]

                    # Read Individual Switches
                    sw_home_1 = rr_coils.bits[2]
                    sw_home_2 = rr_coils.bits[3]
                    sw_limit_max_1 = rr_coils.bits[4]
                    sw_limit_max_2 = rr_coils.bits[5]

                    # LOGIKA REDUDANSI (OR Logic)
                    # Aktif jika Sensor 1 OR Sensor 2 menyala
                    active_home = sw_home_1 or sw_home_2
                    active_limit_max = sw_limit_max_1 or sw_limit_max_2

                    # Parse 2 Register (16-bit x 2) menjadi 32-bit Signed Integer
                    reg_raw = rr_regs.registers
                    raw_bytes = struct.pack('>HH', reg_raw[0], reg_raw[1])
                    current_counter = struct.unpack('>i', raw_bytes)[0]

                    # Reset counter & jarak ke 0 saat menyentuh HOME Switch (Utama / Cadangan)
                    if active_home:
                        self.last_counter = current_counter

                    # Hitung Kecepatan & Jarak berdasarkan Encoder
                    if dt > 0:
                        delta_pulses = current_counter - self.last_counter
                        wheel_circumference = 3.14159265359 * self.wheel_diameter
                        
                        # Jarak total (m) dari titik Homing 0
                        self.distance = (current_counter / self.ppr) * wheel_circumference
                        
                        # Kecepatan linier (Meter / Menit)
                        rpm = ((delta_pulses / self.ppr) / dt) * 60.0
                        self.speed = rpm * wheel_circumference

                        self.last_counter = current_counter
                        self.last_time = current_time

                    # Kirim data ke UI
                    wx.CallAfter(
                        self.notify_window.update_ui_data,
                        status_up, status_down,
                        sw_home_1, sw_home_2, active_home,
                        sw_limit_max_1, sw_limit_max_2, active_limit_max,
                        current_counter, self.distance, self.speed
                    )
                else:
                    wx.CallAfter(self.notify_window.update_status, False, "Error membaca data Modbus")

            except Exception as e:
                wx.CallAfter(self.notify_window.update_status, False, f"Koneksi Terputus: {str(e)}")
                break

            time.sleep(0.1)

        client.close()

    def stop(self):
        self.running = False


# ----------------------------------------------------------------------
# USER INTERFACE (wxPython)
# ----------------------------------------------------------------------
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="PLC Haiwell - 4-Switch Redundancy & Encoder Monitor", size=(540, 580))
        self.worker = None
        self.init_ui()
        self.Centre()

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Status Koneksi
        self.lbl_status = wx.StaticText(panel, label="Status: Terputus")
        self.lbl_status.SetForegroundColour(wx.Colour(200, 0, 0))
        main_sizer.Add(self.lbl_status, 0, wx.ALL | wx.EXPAND, 10)

        # Box 1: Status Redundant Switches
        sb_switches = wx.StaticBox(panel, label="Status Switch (2 Home & 2 Limit MAX Redundant)")
        grid_sw = wx.FlexGridSizer(5, 4, 8, 12)

        # Header Table UI
        grid_sw.Add(wx.StaticText(panel, label="Fungsi"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid_sw.Add(wx.StaticText(panel, label="Sensor 1"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid_sw.Add(wx.StaticText(panel, label="Sensor 2 (Backup)"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid_sw.Add(wx.StaticText(panel, label="Status Logika"), 0, wx.ALIGN_CENTER_VERTICAL)

        self.lbl_up = self._add_switch_row(panel, grid_sw, "Motor UP:", single=True)
        self.lbl_down = self._add_switch_row(panel, grid_sw, "Motor DOWN:", single=True)
        
        self.lbl_hm1, self.lbl_hm2, self.lbl_hm_act = self._add_switch_row(panel, grid_sw, "Home (Reset 0):")
        self.lbl_lm_max1, self.lbl_lm_max2, self.lbl_lm_max_act = self._add_switch_row(panel, grid_sw, "Limit MAX:")

        box_sw_sizer = wx.StaticBoxSizer(sb_switches, wx.VERTICAL)
        box_sw_sizer.Add(grid_sw, 0, wx.EXPAND | wx.ALL, 8)
        main_sizer.Add(box_sw_sizer, 0, wx.ALL | wx.EXPAND, 10)

        # Box 2: Encoder & Speed Parameters
        sb_encoder = wx.StaticBox(panel, label="Data Encoder Autonics E58SC10")
        grid_enc = wx.FlexGridSizer(3, 2, 8, 20)

        grid_enc.Add(wx.StaticText(panel, label="Raw Counter Pulse:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.lbl_counter = wx.StaticText(panel, label="0")
        self.lbl_counter.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        grid_enc.Add(self.lbl_counter, 0, wx.ALIGN_CENTER_VERTICAL)

        grid_enc.Add(wx.StaticText(panel, label="Jarak (Distance):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.lbl_distance = wx.StaticText(panel, label="0.000 m")
        self.lbl_distance.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.lbl_distance.SetForegroundColour(wx.Colour(0, 100, 200))
        grid_enc.Add(self.lbl_distance, 0, wx.ALIGN_CENTER_VERTICAL)

        grid_enc.Add(wx.StaticText(panel, label="Kecepatan (Speed):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.lbl_speed = wx.StaticText(panel, label="0.00 m/min")
        self.lbl_speed.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.lbl_speed.SetForegroundColour(wx.Colour(0, 150, 50))
        grid_enc.Add(self.lbl_speed, 0, wx.ALIGN_CENTER_VERTICAL)

        box_enc_sizer = wx.StaticBoxSizer(sb_encoder, wx.VERTICAL)
        box_enc_sizer.Add(grid_enc, 0, wx.EXPAND | wx.ALL, 8)
        main_sizer.Add(box_enc_sizer, 0, wx.ALL | wx.EXPAND, 10)

        # Control Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_start = wx.Button(panel, label="Start Monitoring")
        self.btn_stop = wx.Button(panel, label="Stop")
        self.btn_stop.Disable()

        btn_sizer.Add(self.btn_start, 1, wx.RIGHT, 5)
        btn_sizer.Add(self.btn_stop, 1, wx.LEFT, 5)
        main_sizer.Add(btn_sizer, 0, wx.ALL | wx.EXPAND, 10)

        panel.SetSizer(main_sizer)

        # Events
        self.btn_start.Bind(wx.EVT_BUTTON, self.on_start)
        self.btn_stop.Bind(wx.EVT_BUTTON, self.on_stop)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def _add_switch_row(self, panel, grid, label_text, single=False):
        grid.Add(wx.StaticText(panel, label=label_text), 0, wx.ALIGN_CENTER_VERTICAL)
        
        lbl1 = wx.StaticText(panel, label="OFF")
        lbl1.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        lbl1.SetForegroundColour(wx.Colour(120, 120, 120))
        grid.Add(lbl1, 0, wx.ALIGN_CENTER_VERTICAL)

        if single:
            grid.Add(wx.StaticText(panel, label="-"), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(wx.StaticText(panel, label="-"), 0, wx.ALIGN_CENTER_VERTICAL)
            return lbl1

        lbl2 = wx.StaticText(panel, label="OFF")
        lbl2.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        lbl2.SetForegroundColour(wx.Colour(120, 120, 120))
        grid.Add(lbl2, 0, wx.ALIGN_CENTER_VERTICAL)

        lbl_act = wx.StaticText(panel, label="INACTIVE")
        lbl_act.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        lbl_act.SetForegroundColour(wx.Colour(120, 120, 120))
        grid.Add(lbl_act, 0, wx.ALIGN_CENTER_VERTICAL)

        return lbl1, lbl2, lbl_act

    def on_start(self, event):
        plc_ip = "127.0.0.1"
        plc_port = 5020
        wheel_diameter = 0.1   # Diameter roda (meter)
        ppr = 1024             # PPR Encoder Autonics E58SC10

        self.btn_start.Disable()
        self.btn_stop.Enable()
        self.lbl_status.SetLabel("Status: Menghubungkan...")
        
        self.worker = ModbusWorker(plc_ip, plc_port, wheel_diameter, ppr, self)
        self.worker.start()

    def on_stop(self, event):
        if self.worker:
            self.worker.stop()
            self.worker = None
        self.btn_start.Enable()
        self.btn_stop.Disable()
        self.lbl_status.SetLabel("Status: Dihentikan")
        self.lbl_status.SetForegroundColour(wx.Colour(200, 0, 0))

    def update_status(self, connected, message):
        self.lbl_status.SetLabel(f"Status: {message}")
        if connected:
            self.lbl_status.SetForegroundColour(wx.Colour(0, 150, 0))
        else:
            self.lbl_status.SetForegroundColour(wx.Colour(200, 0, 0))
            self.btn_start.Enable()
            self.btn_stop.Disable()

    def _update_sensor_pair(self, lbl1, lbl2, lbl_act, state1, state2, is_active, active_color):
        lbl1.SetLabel("ON" if state1 else "OFF")
        lbl1.SetForegroundColour(wx.Colour(0, 150, 0) if state1 else wx.Colour(120, 120, 120))

        lbl2.SetLabel("ON" if state2 else "OFF")
        lbl2.SetForegroundColour(wx.Colour(0, 150, 0) if state2 else wx.Colour(120, 120, 120))

        lbl_act.SetLabel("ACTIVE" if is_active else "INACTIVE")
        lbl_act.SetForegroundColour(active_color if is_active else wx.Colour(120, 120, 120))

    def update_ui_data(self, up, down, 
                       hm1, hm2, hm_act,
                       lm_max1, lm_max2, lm_max_act,
                       counter, distance, speed):
        
        # Status Motor UP/DOWN
        self.lbl_up.SetLabel("ON" if up else "OFF")
        self.lbl_up.SetForegroundColour(wx.Colour(0, 150, 0) if up else wx.Colour(120, 120, 120))

        self.lbl_down.SetLabel("ON" if down else "OFF")
        self.lbl_down.SetForegroundColour(wx.Colour(0, 150, 0) if down else wx.Colour(120, 120, 120))

        # Status Switch Redundancy (Home & Limit MAX)
        self._update_sensor_pair(self.lbl_hm1, self.lbl_hm2, self.lbl_hm_act, hm1, hm2, hm_act, wx.Colour(0, 100, 200))
        self._update_sensor_pair(self.lbl_lm_max1, self.lbl_lm_max2, self.lbl_lm_max_act, lm_max1, lm_max2, lm_max_act, wx.Colour(200, 0, 0))

        # Value Encoder & Kalkulasi
        self.lbl_counter.SetLabel(f"{counter}")
        self.lbl_distance.SetLabel(f"{distance:.3f} m")
        self.lbl_speed.SetLabel(f"{abs(speed):.2f} m/min")

    def on_close(self, event):
        if self.worker:
            self.worker.stop()
        self.Destroy()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()