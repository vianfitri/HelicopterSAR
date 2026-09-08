import time
import threading
import wx
from pymodbus.client import ModbusTcpClient

# ----------------------------------------------------------------------
# THREAD UNTUK KONEKSI MODBUS & PERHITUNGAN COUNTER
# ----------------------------------------------------------------------
class ModbusWorker(threading.Thread):
    def __init__(self, host, port, notify_window):
        super().__init__()
        self.host = host
        self.port = port
        self.notify_window = notify_window
        self.daemon = True  # Thread otomatis mati saat UI ditutup
        self.running = False
        
        # Kecepatan: 4 meter / menit = 4/60 meter per detik (~0.0667 m/s)
        self.SPEED_PER_SEC = 4.0 / 60.0 
        self.length = 0.0

    def run(self):
        self.running = True
        client = ModbusTcpClient(self.host, port=self.port, timeout=2)
        
        if not client.connect():
            wx.CallAfter(self.notify_window.update_status, False, "Gagal terhubung ke PLC")
            return

        wx.CallAfter(self.notify_window.update_status, True, "Terhubung ke PLC")
        
        last_time = time.time()

        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            try:
                # Membaca 2 Digital Input (Discrete Inputs / Discrete Coils tergantung pemetaan PLC)
                # Sesuaikan address Modbus PLC Haiwell Anda (contoh berikut membaca dari Address 0, count 2)
                rr = client.read_discrete_inputs(address=0, count=2)
                
                if not rr.isError():
                    status_up = rr.bits[0]    # Bit 0: Status UP
                    status_down = rr.bits[1]  # Bit 1: Status DOWN
                    
                    # Logika Timer & Counter
                    if status_down and not status_up:
                        # Status DOWN: Menambah counter length berdasarkan waktu berlalu (dt)
                        self.length += self.SPEED_PER_SEC * dt
                    elif status_up and not status_down:
                        # Status UP: Mengurangi counter length hingga minimal 0
                        self.length -= self.SPEED_PER_SEC * dt
                        if self.length < 0.0:
                            self.length = 0.0
                    
                    # Kirim data ke UI
                    wx.CallAfter(
                        self.notify_window.update_ui_data, 
                        status_up, 
                        status_down, 
                        self.length
                    )
                else:
                    wx.CallAfter(self.notify_window.update_status, False, "Error membaca data Modbus")

            except Exception as e:
                wx.CallAfter(self.notify_window.update_status, False, f"Koneksi Terputus: {str(e)}")
                break

            # Polling interval 100ms agar respon timer & kalkulasi halus
            time.sleep(0.1)

        client.close()

    def stop(self):
        self.running = False


# ----------------------------------------------------------------------
# USER INTERFACE (wxPython)
# ----------------------------------------------------------------------
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="PLC Haiwell AT16S0R - Modbus TCP Monitor", size=(400, 320))
        
        self.worker = None
        self.init_ui()
        self.Centre()

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Status Koneksi
        self.lbl_status = wx.StaticText(panel, label="Status: Terputus", style=wx.ALIGN_LEFT)
        self.lbl_status.SetForegroundColour(wx.Colour(200, 0, 0))
        vbox.Add(self.lbl_status, 0, wx.ALL | wx.EXPAND, 10)

        # Indicator Status Input
        grid = wx.FlexGridSizer(2, 2, 10, 20)
        grid.Add(wx.StaticText(panel, label="Input UP:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.lbl_up = wx.StaticText(panel, label="OFF")
        self.lbl_up.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        grid.Add(self.lbl_up, 0, wx.ALIGN_CENTER_VERTICAL)

        grid.Add(wx.StaticText(panel, label="Input DOWN:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.lbl_down = wx.StaticText(panel, label="OFF")
        self.lbl_down.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        grid.Add(self.lbl_down, 0, wx.ALIGN_CENTER_VERTICAL)

        vbox.Add(grid, 0, wx.ALL, 15)

        # Display Counter / Length
        vbox.Add(wx.StaticText(panel, label="Parameter Length:"), 0, wx.LEFT | wx.RIGHT, 15)
        self.lbl_length = wx.StaticText(panel, label="0.00 m")
        self.lbl_length.SetFont(wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.lbl_length.SetForegroundColour(wx.Colour(0, 100, 200))
        vbox.Add(self.lbl_length, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)

        # Control Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_start = wx.Button(panel, label="Start Monitoring")
        self.btn_stop = wx.Button(panel, label="Stop")
        self.btn_stop.Disable()

        btn_sizer.Add(self.btn_start, 1, wx.RIGHT, 5)
        btn_sizer.Add(self.btn_stop, 1, wx.LEFT, 5)
        vbox.Add(btn_sizer, 0, wx.ALL | wx.EXPAND, 15)

        panel.SetSizer(vbox)

        # Event Binds
        self.btn_start.Bind(wx.EVT_BUTTON, self.on_start)
        self.btn_stop.Bind(wx.EVT_BUTTON, self.on_stop)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_start(self, event):
        # Masukkan IP Address dan Port PLC Haiwell Anda
        plc_ip = "192.168.1.10"  # Sesuaikan IP PLC
        plc_port = 502

        self.btn_start.Disable()
        self.btn_stop.Enable()
        self.lbl_status.SetLabel("Status: Menghubungkan...")
        
        self.worker = ModbusWorker(plc_ip, plc_port, self)
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

    def update_ui_data(self, status_up, status_down, length_val):
        # Update Status Visual UP/DOWN
        self.lbl_up.SetLabel("ON" if status_up else "OFF")
        self.lbl_up.SetForegroundColour(wx.Colour(0, 150, 0) if status_up else wx.Colour(100, 100, 100))

        self.lbl_down.SetLabel("ON" if status_down else "OFF")
        self.lbl_down.SetForegroundColour(wx.Colour(0, 150, 0) if status_down else wx.Colour(100, 100, 100))

        # Update Tampilan Length (Format 2 Desimal)
        self.lbl_length.SetLabel(f"{length_val:.1f} m")

    def on_close(self, event):
        if self.worker:
            self.worker.stop()
        self.Destroy()


# ----------------------------------------------------------------------
# MAIN PROGRAM
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()