import struct
import threading
import time
import wx

# Import Pymodbus RTU Client (Kompatibel dengan pymodbus v3.x)
from pymodbus.client import ModbusSerialClient


# Frame Kustom untuk Komponen GUI Modbus
class ModbusMonitorFrame(wx.Frame):

    def __init__(self, parent, title):
        super(ModbusMonitorFrame, self).__init__(
            parent,
            title=title,
            size=(500, 520),
            style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX,
        )

        # State & Control Variables
        self.client = None
        self.is_running = False
        self.worker_thread = None

        self.init_ui()
        self.Centre()

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # -------------------------------------------------------------
        # 1. Panel Koneksi Serial
        # -------------------------------------------------------------
        conn_box = wx.StaticBox(panel, label=" Pengaturan Serial RS485 ")
        conn_sizer = wx.StaticBoxSizer(conn_box, wx.VERTICAL)

        grid_conn = wx.FlexGridSizer(rows=2, cols=4, vgap=8, hgap=10)

        grid_conn.Add(wx.StaticText(panel, label="Port COM:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_port = wx.TextCtrl(panel, value="COM3", size=(80, -1))
        grid_conn.Add(self.txt_port, 0)

        grid_conn.Add(wx.StaticText(panel, label="Baudrate:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_baud = wx.TextCtrl(panel, value="38400", size=(80, -1))
        grid_conn.Add(self.txt_baud, 0)

        grid_conn.Add(wx.StaticText(panel, label="Slave ID:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_slave = wx.TextCtrl(panel, value="1", size=(80, -1))
        grid_conn.Add(self.txt_slave, 0)

        grid_conn.Add(wx.StaticText(panel, label="Interval (ms):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_interval = wx.TextCtrl(panel, value="100", size=(80, -1))
        grid_conn.Add(self.txt_interval, 0)

        conn_sizer.Add(grid_conn, 0, wx.ALL | wx.EXPAND, 5)

        # Tombol Connect / Disconnect
        self.btn_connect = wx.Button(panel, label="Hubungkan RS485")
        self.btn_connect.Bind(wx.EVT_BUTTON, self.on_toggle_connect)
        conn_sizer.Add(self.btn_connect, 0, wx.TOP | wx.EXPAND, 5)

        main_sizer.Add(conn_sizer, 0, wx.ALL | wx.EXPAND, 10)

        # -------------------------------------------------------------
        # 2. Panel Monitor Data Realtime
        # -------------------------------------------------------------
        data_box = wx.StaticBox(panel, label=" Telemetri STM32 ")
        data_sizer = wx.StaticBoxSizer(data_box, wx.VERTICAL)

        grid_data = wx.FlexGridSizer(rows=5, cols=2, vgap=12, hgap=20)
        grid_data.AddGrowableCol(1, 1)

        # Font Styling
        val_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        # Register 0-1: Total Counter
        grid_data.Add(wx.StaticText(panel, label="Total Pulse Count:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.lbl_counter = wx.StaticText(panel, label="0 Pulse")
        self.lbl_counter.SetFont(val_font)
        grid_data.Add(self.lbl_counter, 0, wx.ALIGN_CENTER_VERTICAL)

        # Register 2-3: Jarak (mm)
        grid_data.Add(wx.StaticText(panel, label="Jarak Pengukuran:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.lbl_distance = wx.StaticText(panel, label="0.000 m (0 mm)")
        self.lbl_distance.SetFont(val_font)
        grid_data.Add(self.lbl_distance, 0, wx.ALIGN_CENTER_VERTICAL)

        # Register 4: Status Homing
        grid_data.Add(wx.StaticText(panel, label="Status Homing Switch:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.lbl_homing = wx.StaticText(panel, label="IDLE")
        self.lbl_homing.SetFont(val_font)
        self.lbl_homing.SetForegroundColour(wx.Colour(120, 120, 120))
        grid_data.Add(self.lbl_homing, 0, wx.ALIGN_CENTER_VERTICAL)

        # Register 5-6: Kecepatan Linier (m/s)
        grid_data.Add(wx.StaticText(panel, label="Kecepatan Linier:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.lbl_speed = wx.StaticText(panel, label="0.00 m/s")
        self.lbl_speed.SetFont(val_font)
        grid_data.Add(self.lbl_speed, 0, wx.ALIGN_CENTER_VERTICAL)

        # Register 7-8: RPM
        grid_data.Add(wx.StaticText(panel, label="Kecepatan Putar:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.lbl_rpm = wx.StaticText(panel, label="0.0 RPM")
        self.lbl_rpm.SetFont(val_font)
        grid_data.Add(self.lbl_rpm, 0, wx.ALIGN_CENTER_VERTICAL)

        data_sizer.Add(grid_data, 0, wx.ALL | wx.EXPAND, 10)
        main_sizer.Add(data_sizer, 0, wx.ALL | wx.EXPAND, 10)

        # Status Bar Footer
        self.CreateStatusBar()
        self.SetStatusText("Siap terhubung ke STM32 Modbus Slave.")

        panel.SetSizer(main_sizer)

        # Bind event penutupan window agar thread berhenti bersih
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_toggle_connect(self, event):
        if not self.is_running:
            # Mulai Koneksi & Thread
            port = self.txt_port.GetValue()
            try:
                baud = int(self.txt_baud.GetValue())
            except ValueError:
                wx.MessageBox("Baudrate harus berupa angka!", "Error", wx.OK | wx.ICON_ERROR)
                return

            self.client = ModbusSerialClient(
                port=port,
                baudrate=baud,
                parity="N",
                stopbits=1,
                bytesize=8,
                timeout=0.5,
            )

            if not self.client.connect():
                wx.MessageBox(
                    f"Gagal membuka serial port {port}!", "Error", wx.OK | wx.ICON_ERROR
                )
                return

            self.is_running = True
            self.btn_connect.SetLabel("Putuskan Koneksi")
            self.SetStatusText(f"Terhubung ke {port} @ {baud} bps.")

            # Jalankan Thread Pembaca Modbus
            self.worker_thread = threading.Thread(target=self.modbus_polling_thread, daemon=True)
            self.worker_thread.start()
        else:
            # Hentikan Thread & Disconnect
            self.stop_thread()

    def stop_thread(self):
        self.is_running = False
        if self.client:
            self.client.close()
            self.client = None

        self.btn_connect.SetLabel("Hubungkan RS485")
        self.SetStatusText("Koneksi terputus.")

    def modbus_polling_thread(self):
        """Thread terpisah khusus polling Modbus RTU agar UI tidak freeze."""
        while self.is_running:
            try:
                slave_id = int(self.txt_slave.GetValue())
                interval = float(self.txt_interval.GetValue()) / 1000.0

                # Baca 9 Holding Register (Address 0x0000 - 0x0008)
                response = self.client.read_holding_registers(address=0, count=9, slave=slave_id)

                if not response.isError():
                    regs = response.registers

                    # Parsing data 32-bit (Kombinasi High & Low Word)
                    # 1. Counter (Int32)
                    raw_counter = (regs[0] << 16) | regs[1]
                    counter = struct.unpack(">i", struct.pack(">I", raw_counter))[0]

                    # 2. Jarak mm (UInt32)
                    distance_mm = (regs[2] << 16) | regs[3]

                    # 3. Status Homing (UInt16)
                    homing_flag = regs[4]

                    # 4. Kecepatan (Int32, Skala x100) -> cm/s atau 0.01 m/s
                    raw_speed = (regs[5] << 16) | regs[6]
                    speed_cms = struct.unpack(">i", struct.pack(">I", raw_speed))[0]
                    speed_ms = speed_cms / 100.0

                    # 5. RPM (Int32, Skala x10)
                    raw_rpm = (regs[7] << 16) | regs[8]
                    rpm_x10 = struct.unpack(">i", struct.pack(">I", raw_rpm))[0]
                    rpm = rpm_x10 / 10.0

                    # Update UI secara aman menggunakan wx.CallAfter
                    wx.CallAfter(
                        self.update_ui_data, counter, distance_mm, homing_flag, speed_ms, rpm
                    )
                else:
                    wx.CallAfter(self.SetStatusText, "Modbus Error: No response / Invalid CRC")

            except Exception as e:
                wx.CallAfter(self.SetStatusText, f"Error: {str(e)}")

            time.sleep(interval)

    def update_ui_data(self, counter, distance_mm, homing_flag, speed_ms, rpm):
        """Dijalankan di Main UI Thread melalui wx.CallAfter."""
        self.lbl_counter.SetLabel(f"{counter:,} Pulse")

        dist_m = distance_mm / 1000.0
        self.lbl_distance.SetLabel(f"{dist_m:.3f} m ({distance_mm} mm)")

        if homing_flag == 1:
            self.lbl_homing.SetLabel("HOMING TRIGGERED (RESET)")
            self.lbl_homing.SetForegroundColour(wx.Colour(200, 0, 0))  # Merah
        else:
            self.lbl_homing.SetLabel("NORMAL")
            self.lbl_homing.SetForegroundColour(wx.Colour(0, 150, 0))  # Hijau

        self.lbl_speed.SetLabel(f"{speed_ms:.2f} m/s")
        self.lbl_rpm.SetLabel(f"{rpm:.1f} RPM")

    def on_close(self, event):
        self.stop_thread()
        event.Skip()


if __name__ == "__main__":
    app = wx.App(False)
    frame = ModbusMonitorFrame(None, title="STM32F103 Encoder Monitor via Modbus RTU")
    frame.Show()
    app.MainLoop()