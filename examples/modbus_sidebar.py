import wx
import threading
import time
import socket
from pymodbus.client import ModbusTcpClient

# Custom Event untuk memposting status koneksi dari background thread ke UI
EVT_STATUS_UPDATE_ID = wx.NewIdRef()

class StatusUpdateEvent(wx.PyEvent):
    def __init__(self, connected):
        super().__init__()
        self.SetEventType(EVT_STATUS_UPDATE_ID)
        self.connected = connected

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Modbus TCP Controller", size=(800, 600))
        
        # Konfigurasi Default Modbus Server
        self.ip_address = "127.0.0.1"
        self.port = 502
        self.is_connected = False
        
        # Flag/Event untuk mengontrol Thread
        self.running = True
        
        # Init UI
        self.init_ui()
        
        # Bind Custom Event
        self.Connect(-1, -1, EVT_STATUS_UPDATE_ID, self.on_status_update)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Jalankan Thread Pengecekan Koneksi (Non-blocking)
        self.monitor_thread = threading.Thread(target=self.bg_connection_monitor, daemon=True)
        self.monitor_thread.start()

    def init_ui(self):
        # Panel utama
        main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # -------------------------------------------------------------
        # 1. TOP TITLEBAR / HEADER
        # -------------------------------------------------------------
        top_panel = wx.Panel(main_panel)
        top_panel.SetBackgroundColour(wx.Colour(30, 40, 55)) # Warna gelap
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)

        title_label = wx.StaticText(top_panel, label="MODBUS TCP MONITORING & CONFIGURATION")
        title_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title_label.SetFont(title_font)
        title_label.SetForegroundColour(wx.Colour(255, 255, 255))

        top_sizer.Add(title_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 15)
        top_panel.SetSizer(top_sizer)

        # -------------------------------------------------------------
        # BODY AREA (LEFT SIDEBAR + RIGHT CONTENT)
        # -------------------------------------------------------------
        body_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 2. LEFT SIDEBAR (Lebar 200px)
        sidebar_panel = wx.Panel(main_panel, size=(200, -1))
        sidebar_panel.SetMinSize((200, -1))
        sidebar_panel.SetMaxSize((200, -1))
        sidebar_panel.SetBackgroundColour(wx.Colour(240, 242, 245))

        sidebar_sizer = wx.BoxSizer(wx.VERTICAL)

        sidebar_title = wx.StaticText(sidebar_panel, label="STATUS KONEKSI")
        sidebar_title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        # Indicator Status (Pill Badge)
        self.status_badge = wx.StaticText(sidebar_panel, label=" Checking... ", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.status_badge.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.status_badge.SetBackgroundColour(wx.Colour(180, 180, 180))
        self.status_badge.SetForegroundColour(wx.Colour(255, 255, 255))

        self.lbl_current_ip = wx.StaticText(sidebar_panel, label=f"Target: {self.ip_address}:{self.port}")
        self.lbl_current_ip.SetForegroundColour(wx.Colour(100, 100, 100))

        sidebar_sizer.Add(sidebar_title, 0, wx.ALL | wx.EXPAND, 15)
        sidebar_sizer.Add(self.status_badge, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 15)
        sidebar_sizer.Add(self.lbl_current_ip, 0, wx.ALL | wx.EXPAND, 15)

        sidebar_panel.SetSizer(sidebar_sizer)

        # 3. RIGHT MAIN CONTENT
        content_panel = wx.Panel(main_panel)
        content_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        content_sizer = wx.BoxSizer(wx.VERTICAL)

        # Section Header Content
        section_title = wx.StaticText(content_panel, label="Pengaturan Koneksi Modbus Server")
        section_title.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        content_sizer.Add(section_title, 0, wx.ALL, 20)

        # Form Grid
        form_sizer = wx.FlexGridSizer(rows=2, cols=2, vgap=15, hgap=10)

        lbl_ip = wx.StaticText(content_panel, label="IP Address Server:")
        self.txt_ip = wx.TextCtrl(content_panel, value=self.ip_address, size=(180, -1))

        lbl_port = wx.StaticText(content_panel, label="Port Modbus:")
        self.txt_port = wx.TextCtrl(content_panel, value=str(self.port), size=(80, -1))

        form_sizer.Add(lbl_ip, 0, wx.ALIGN_CENTER_VERTICAL)
        form_sizer.Add(self.txt_ip, 0)
        form_sizer.Add(lbl_port, 0, wx.ALIGN_CENTER_VERTICAL)
        form_sizer.Add(self.txt_port, 0)

        content_sizer.Add(form_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)

        # Button Simpan
        self.btn_save = wx.Button(content_panel, label="Simpan Pengaturan", size=(150, 35))
        self.btn_save.Bind(wx.EVT_BUTTON, self.on_save_settings)
        content_sizer.Add(self.btn_save, 0, wx.LEFT, 20)

        content_panel.SetSizer(content_sizer)

        # Gabungkan Sidebar & Content ke Body
        body_sizer.Add(sidebar_panel, 0, wx.EXPAND)
        body_sizer.Add(content_panel, 1, wx.EXPAND)

        # Gabungkan Top Titlebar & Body ke Layout Utama
        main_sizer.Add(top_panel, 0, wx.EXPAND)
        main_sizer.Add(body_sizer, 1, wx.EXPAND)

        main_panel.SetSizer(main_sizer)

    # -------------------------------------------------------------
    # THREAD BACKGROUND (NON-BLOCKING WORKER)
    # -------------------------------------------------------------
    def bg_connection_monitor(self):
        """Thread background untuk cek koneksi tanpa mengganggu/freeze UI."""
        while self.running:
            try:
                # Menghubungkan ke Modbus TCP Server menggunakan PyModbus
                client = ModbusTcpClient(self.ip_address, port=self.port, timeout=1.5)
                connected = client.connect()
                if connected:
                    client.close()
            except Exception:
                connected = False

            # Kirim event ke UI thread secara aman
            wx.PostEvent(self, StatusUpdateEvent(connected))
            
            # Interval pengecekan setiap 2 detik
            time.sleep(2)

    # -------------------------------------------------------------
    # EVENT HANDLERS
    # -------------------------------------------------------------
    def on_status_update(self, event):
        """Dijalankan di UI thread saat event kiriman background thread diterima."""
        self.is_connected = event.connected
        
        if self.is_connected:
            self.status_badge.SetLabel(" CONNECTED ")
            self.status_badge.SetBackgroundColour(wx.Colour(40, 167, 69)) # Hijau
        else:
            self.status_badge.SetLabel(" NOT CONNECTED ")
            self.status_badge.SetBackgroundColour(wx.Colour(220, 53, 69)) # Merah
            
        self.status_badge.Refresh()

    def on_save_settings(self, event):
        """Menyimpan IP dan Port baru."""
        new_ip = self.txt_ip.GetValue().strip()
        new_port_str = self.txt_port.GetValue().strip()

        if not new_ip:
            wx.MessageBox("IP Address tidak boleh kosong!", "Error", wx.OK | wx.ICON_ERROR)
            return

        if not new_port_str.isdigit():
            wx.MessageBox("Port harus berupa angka integer valid!", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Update variabel (Thread background otomatis membaca nilai terbaru ini)
        self.ip_address = new_ip
        self.port = int(new_port_str)
        
        self.lbl_current_ip.SetLabel(f"Target: {self.ip_address}:{self.port}")
        wx.MessageBox("Pengaturan IP dan Port berhasil disimpan!", "Info", wx.OK | wx.ICON_INFORMATION)

    def on_close(self, event):
        """Menghentikan thread saat jendela aplikasi ditutup."""
        self.running = False
        self.Destroy()

if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()