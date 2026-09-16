import threading
import time
import wx
from pymodbus.client import ModbusTcpClient

# Konfigurasi Koneksi PLC Haiwell AT16S0R
#PLC_IP = "192.168.1.111"
PLC_IP = "127.0.0.1"
PLC_PORT = 502

class ModbusWorkerThread(threading.Thread):
    """
    Thread khusus di background untuk melakukan polling data Modbus TCP.
    Mencegah GUI wxPython mengalami freeze saat terjadi delay/timeout jaringan.
    """
    def __init__(self, notify_window, ip, port):
        super().__init__()
        self.notify_window = notify_window
        self.ip = ip
        self.port = port
        self.client = None
        self.running = False
        self.daemon = True  # Thread otomatis berhenti saat aplikasi ditutup

    def run(self):
        self.client = ModbusTcpClient(self.ip, port=self.port, timeout=2)
        
        if not self.client.connect():
            # Beritahu UI jika koneksi awal gagal
            wx.CallAfter(self.notify_window.on_connection_status, False, f"Gagal terhubung ke {self.ip}:{self.port}")
            return

        self.running = True
        wx.CallAfter(self.notify_window.on_connection_status, True, f"Terhubung ke {self.ip}:{self.port}")

        while self.running:
            try:
                # 1. Baca Discrete Inputs X7 - X10 (FC 02, Offset Modbus = 7)
                res_x = self.client.read_discrete_inputs(address=7, count=4)
                
                # 2. Baca Coils Y8 - Y11 (FC 01, Offset Modbus = 8)
                res_y = self.client.read_coils(address=8, count=4)

                # 3. Baca Holding Registers V32 s.d V102 (FC 03, Offset 32, Jumlah 71)
                res_v = self.client.read_holding_registers(address=32, count=71)

                if not (res_x.isError() or res_y.isError() or res_v.isError()):
                    x_vals = res_x.bits[:4]
                    y_vals = res_y.bits[:4]
                    
                    # Ambil nilai berdasarkan offset relatif dari index 0 (register 32)
                    v32_val = res_v.registers[0]    # V32 (RPM)
                    v34_val = res_v.registers[2]    # V34 (SPEED2)
                    v102_val = res_v.registers[70]  # V102 (Hoist Load)

                    # Kirim data ke Main UI Thread secara aman
                    wx.CallAfter(
                        self.notify_window.update_ui_data,
                        x_vals, y_vals, v32_val, v34_val, v102_val
                    )
                else:
                    wx.CallAfter(self.notify_window.log_error, "Gagal membaca beberapa register (Modbus Error)")

            except Exception as e:
                wx.CallAfter(self.notify_window.log_error, f"Error Komunikasi: {str(e)}")

            # Interval Polling (300 ms)
            time.sleep(0.3)

        # Tutup koneksi saat loop selesai
        if self.client:
            self.client.close()

    def stop(self):
        self.running = False


class MainWindow(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Haiwell PLC AT16S0R Monitor", size=(600, 520))
        
        self.worker = None
        self.is_connected = False

        self.init_ui()
        self.Centre()

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # ==========================================
        # 1. KONEKSI MODBUS TCP
        # ==========================================
        conn_box = wx.StaticBox(panel, label="Koneksi Modbus TCP")
        conn_sizer = wx.StaticBoxSizer(conn_box, wx.HORIZONTAL)

        self.btn_connect = wx.Button(panel, label="Hubungkan", size=(100, 30))
        self.btn_connect.Bind(wx.EVT_BUTTON, self.on_toggle_connect)

        self.lbl_status = wx.StaticText(panel, label="Status: Terputus")
        self.lbl_status.SetForegroundColour(wx.Colour(200, 0, 0))

        conn_sizer.Add(self.btn_connect, 0, wx.ALL, 5)
        conn_sizer.Add(self.lbl_status, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        main_sizer.Add(conn_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # ==========================================
        # 2. STATUS INPUT DIGITAL (X7 - X10)
        # ==========================================
        input_box = wx.StaticBox(panel, label="Status Limit Switch (Discrete Input X)")
        input_sizer = wx.StaticBoxSizer(input_box, wx.HORIZONTAL)

        self.lbl_x7 = self.create_indicator(panel, "FRWD1 (X7)", input_sizer)
        self.lbl_x8 = self.create_indicator(panel, "FRWD2 (X8)", input_sizer)
        self.lbl_x9 = self.create_indicator(panel, "RVRS1 (X9)", input_sizer)
        self.lbl_x10 = self.create_indicator(panel, "RVRS2 (X10)", input_sizer)
        main_sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # ==========================================
        # 3. STATUS OUTPUT DIGITAL (Y8 - Y11)
        # ==========================================
        output_box = wx.StaticBox(panel, label="Status Lampu (Coil Output Y)")
        output_sizer = wx.StaticBoxSizer(output_box, wx.HORIZONTAL)

        self.lbl_y8 = self.create_indicator(panel, "FRWD Lamp (Y8)", output_sizer)
        self.lbl_y9 = self.create_indicator(panel, "RVRS Lamp (Y9)", output_sizer)
        self.lbl_y10 = self.create_indicator(panel, "Hoist Up (Y10)", output_sizer)
        self.lbl_y11 = self.create_indicator(panel, "Hoist Down (Y11)", output_sizer)
        main_sizer.Add(output_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # ==========================================
        # 4. DATA REGISTER ANALOG (V32, V34, V102)
        # ==========================================
        v_box = wx.StaticBox(panel, label="Data Register V (Holding Register)")
        v_sizer = wx.FlexGridSizer(rows=3, cols=2, vgap=12, hgap=30)

        v_sizer.Add(wx.StaticText(panel, label="RPM (V32):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.val_v32 = wx.StaticText(panel, label="0")
        v_sizer.Add(self.val_v32, 0, wx.ALIGN_CENTER_VERTICAL)

        v_sizer.Add(wx.StaticText(panel, label="SPEED2 (V34):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.val_v34 = wx.StaticText(panel, label="0")
        v_sizer.Add(self.val_v34, 0, wx.ALIGN_CENTER_VERTICAL)

        v_sizer.Add(wx.StaticText(panel, label="Hoist Load (V102):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.val_v102 = wx.StaticText(panel, label="0")
        v_sizer.Add(self.val_v102, 0, wx.ALIGN_CENTER_VERTICAL)

        # Styling Font Angka
        bold_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.val_v32.SetFont(bold_font)
        self.val_v34.SetFont(bold_font)
        self.val_v102.SetFont(bold_font)

        v_box_sizer = wx.StaticBoxSizer(v_box, wx.VERTICAL)
        v_box_sizer.Add(v_sizer, 0, wx.ALL, 10)
        main_sizer.Add(v_box_sizer, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(main_sizer)

        # Event ketika jendela ditutup
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def create_indicator(self, panel, label_text, parent_sizer):
        """Membuat widget indikator status ON/OFF visual."""
        box = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(panel, label=label_text, style=wx.ALIGN_CENTER)
        status = wx.StaticText(panel, label="OFF", style=wx.ALIGN_CENTER)
        status.SetBackgroundColour(wx.Colour(210, 210, 210))
        status.SetMinSize((100, 28))
        
        box.Add(text, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        box.Add(status, 0, wx.ALIGN_CENTER)
        parent_sizer.Add(box, 1, wx.EXPAND | wx.ALL, 5)
        return status

    # ==========================================
    # LOGIKA KONEKSI & HANDLER THREAD
    # ==========================================
    def on_toggle_connect(self, event):
        if not self.is_connected:
            self.btn_connect.Disable()
            self.lbl_status.SetLabel("Menghubungkan...")
            self.lbl_status.SetForegroundColour(wx.Colour(200, 150, 0))
            
            # Start Worker Thread
            self.worker = ModbusWorkerThread(self, PLC_IP, PLC_PORT)
            self.worker.start()
        else:
            self.stop_worker()

    def on_connection_status(self, success, message):
        """Dipanggil oleh thread untuk mengabarkan status koneksi."""
        self.btn_connect.Enable()
        if success:
            self.is_connected = True
            self.btn_connect.SetLabel("Putuskan")
            self.lbl_status.SetLabel(f"Status: {message}")
            self.lbl_status.SetForegroundColour(wx.Colour(0, 150, 0))
        else:
            self.is_connected = False
            self.btn_connect.SetLabel("Hubungkan")
            self.lbl_status.SetLabel(f"Status: {message}")
            self.lbl_status.SetForegroundColour(wx.Colour(200, 0, 0))
            wx.MessageBox(message, "Error Koneksi", wx.OK | wx.ICON_ERROR)

    def update_ui_data(self, x_vals, y_vals, v32, v34, v102):
        """Dipanggil dari background thread menggunakan wx.CallAfter."""
        if not self.is_connected:
            return

        # Update Indikator X (Input)
        inputs = [self.lbl_x7, self.lbl_x8, self.lbl_x9, self.lbl_x10]
        for lbl, state in zip(inputs, x_vals):
            lbl.SetLabel("ON" if state else "OFF")
            lbl.SetBackgroundColour(wx.Colour(46, 204, 113) if state else wx.Colour(210, 210, 210))

        # Update Indikator Y (Output)
        outputs = [self.lbl_y8, self.lbl_y9, self.lbl_y10, self.lbl_y11]
        for lbl, state in zip(outputs, y_vals):
            lbl.SetLabel("ON" if state else "OFF")
            lbl.SetBackgroundColour(wx.Colour(241, 196, 15) if state else wx.Colour(210, 210, 210))

        # Update Nilai Register V
        self.val_v32.SetLabel(str(v32))
        self.val_v34.SetLabel(str(v34))
        self.val_v102.SetLabel(str(v102))

        self.Refresh()

    def log_error(self, err_msg):
        print(f"[Modbus Error]: {err_msg}")

    def stop_worker(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
        self.is_connected = False
        self.btn_connect.SetLabel("Hubungkan")
        self.lbl_status.SetLabel("Status: Terputus")
        self.lbl_status.SetForegroundColour(wx.Colour(200, 0, 0))

    def on_close(self, event):
        self.stop_worker()
        self.Destroy()

if __name__ == "__main__":
    app = wx.App()
    frame = MainWindow()
    frame.Show()
    app.MainLoop()