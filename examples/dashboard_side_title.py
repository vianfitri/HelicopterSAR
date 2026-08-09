import wx
import time

class DashboardFrame(wx.Frame):
    def __init__(self, parent, title):
        # Buat Frame tanpa titlebar bawaan OS jika ingin custom total, 
        # atau gunakan wx.DEFAULT_FRAME_STYLE untuk tampilan standar window.
        super().__init__(parent, title=title, size=(1000, 650))
        
        # Simpan waktu awal aplikasi berjalan
        self.start_time = time.time()
        
        # Set background utama
        self.SetBackgroundColour(wx.Colour(245, 246, 250))
        
        # Sizer Utama (Vertikal: Titlebar di atas, Content Area di bawah)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 1. Buat Titlebar Kustom
        titlebar = self.create_titlebar()
        main_sizer.Add(titlebar, 0, wx.EXPAND)
        
        # 2. Buat Body (Sidebar + Main Content Area)
        body_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sidebar = self.create_sidebar()
        content_area = self.create_content_area()
        
        body_sizer.Add(sidebar, 0, wx.EXPAND)
        body_sizer.Add(content_area, 1, wx.EXPAND | wx.ALL, 20)
        
        main_sizer.Add(body_sizer, 1, wx.EXPAND)
        
        self.SetSizer(main_sizer)
        
        # Timer untuk meng-update Waktu Elapsed
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_update_timer, self.timer)
        self.timer.Start(1000)  # Trigger setiap 1 detik (1000 ms)
        
        self.Centre()

    
    def create_titlebar(self):
        # Panel Titlebar Kustom
        titlebar_panel = wx.Panel(self, size=(-1, 60))
        titlebar_panel.SetBackgroundColour(wx.Colour(30, 41, 59))  # Warna gelap (Dark Slate)
        
        titlebar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # --- SISI KIRI: Logo + Title ---
        left_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Generasi/Load Gambar Logo (Membuat bitmap dummy jika tidak ada file lokal)
        logo_bitmap = self.get_logo_bitmap()
        logo_img = wx.StaticBitmap(titlebar_panel, bitmap=logo_bitmap)
        left_sizer.Add(logo_img, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        
        # Text Title
        title_text = wx.StaticText(titlebar_panel, label="Helicopter Rescue Simulator")
        title_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title_text.SetFont(title_font)
        title_text.SetForegroundColour(wx.Colour(255, 255, 255))
        left_sizer.Add(title_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 12)
        
        # --- DI TENGAH: Elapsed Time (Rounded Rectangle) ---
        self.time_panel = ElapsedTimePanel(titlebar_panel)
        
        # --- SUSUN LAYOUT TITLEBAR ---
        # left_sizer di kiri, time_panel di tengah dengan stretch spacer
        titlebar_sizer.Add(left_sizer, 1, wx.ALIGN_CENTER_VERTICAL)
        titlebar_sizer.Add(self.time_panel, 0, wx.ALIGN_CENTER_VERTICAL)
        
        # Spacer kanan agar posisi Timer berada benar-benar di tengah
        titlebar_sizer.AddSpacer(250) 

        titlebar_panel.SetSizer(titlebar_sizer)
        return titlebar_panel
    

    """
    def create_titlebar(self):
        # Panel Titlebar Kustom
        titlebar_panel = wx.Panel(self, size=(-1, 60))
        titlebar_panel.SetBackgroundColour(wx.Colour(30, 41, 59))  # Warna gelap (Dark Slate)
        
        titlebar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # --- 1. SISI KIRI: Logo + Title ---
        left_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Logo Image
        logo_bitmap = self.get_logo_bitmap()
        logo_img = wx.StaticBitmap(titlebar_panel, bitmap=logo_bitmap)
        left_sizer.Add(logo_img, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        
        # Text Title
        title_text = wx.StaticText(titlebar_panel, label="Helicopter Rescue Simulator")
        title_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title_text.SetFont(title_font)
        title_text.SetForegroundColour(wx.Colour(255, 255, 255))
        left_sizer.Add(title_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 12)
        
        # --- 2. DI TENGAH: Elapsed Time (Rounded Rectangle) ---
        self.time_panel = ElapsedTimePanel(titlebar_panel)
        
        # --- 3. SISI KANAN: Tombol Exit ---
        btn_exit = wx.Button(titlebar_panel, label="✕", size=(36, 36), style=wx.BORDER_NONE)
        btn_exit.SetBackgroundColour(wx.Colour(220, 38, 38))  # Warna merah (Crimson Red)
        btn_exit.SetForegroundColour(wx.Colour(255, 255, 255))  # Warna teks putih
        btn_exit.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        # Bind event klik tombol Exit ke fungsi penutup jendela
        btn_exit.Bind(wx.EVT_BUTTON, self.on_exit)

        # --- SUSUN LAYOUT TITLEBAR ---
        # 1. Tambah Kiri (Width dinamis)
        titlebar_sizer.Add(left_sizer, 1, wx.ALIGN_CENTER_VERTICAL)
        
        # 2. Tambah Elapsed Time di Tengah
        titlebar_sizer.Add(self.time_panel, 0, wx.ALIGN_CENTER_VERTICAL)
        
        # 3. Spacer transparan dengan proporsi 1 agar posisi Elapsed Time tetap berada di tengah rata
        titlebar_sizer.AddSpacer(0)
        titlebar_sizer.SetItemMinSize(left_sizer, (0, 0)) # Memastikan proporsi rata kiri-kanan
        
        # Buat wrapper sizer kanan agar tombol exit berada persis di pojok kanan dengan margin
        right_sizer = wx.BoxSizer(wx.HORIZONTAL)
        right_sizer.Add(btn_exit, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)
        
        titlebar_sizer.Add(right_sizer, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)

        titlebar_panel.SetSizer(titlebar_sizer)
        return titlebar_panel
    """

    """
    def on_exit(self, event):
        #Handler saat tombol Exit diklik
        self.Close(True)
    """

    def create_sidebar(self):
        sidebar_panel = wx.Panel(self, size=(220, -1))
        sidebar_panel.SetBackgroundColour(wx.Colour(15, 23, 42))  # Darker Blue/Navy
        
        sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Judul Menu Sidebar
        menu_label = wx.StaticText(sidebar_panel, label="NAVIGATION")
        menu_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        menu_label.SetForegroundColour(wx.Colour(100, 116, 139))
        sidebar_sizer.Add(menu_label, 0, wx.ALL, 15)
        
        # Menu Items
        menus = ["Dashboard", "Mission Control", "Helicopter Status", "Weather Info", "Settings"]
        for idx, item in enumerate(menus):
            btn = wx.Button(sidebar_panel, label=item, style=wx.BORDER_NONE)
            btn.SetForegroundColour(wx.Colour(241, 245, 249) if idx == 0 else wx.Colour(148, 163, 184))
            btn.SetBackgroundColour(wx.Colour(30, 41, 59) if idx == 0 else wx.Colour(15, 23, 42))
            sidebar_sizer.Add(btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
            
        sidebar_panel.SetSizer(sidebar_sizer)
        return sidebar_panel

    def create_content_area(self):
        content_panel = wx.Panel(self)
        content_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(content_panel, label="Main Dashboard View")
        text.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(text, 0, wx.ALL, 20)
        
        content_panel.SetSizer(sizer)
        return content_panel

    def on_update_timer(self, event):
        # Hitung durasi elapsed time
        elapsed_seconds = int(time.time() - self.start_time)
        hrs = elapsed_seconds // 3600
        mins = (elapsed_seconds % 3600) // 60
        secs = elapsed_seconds % 60
        
        time_str = f"Elapsed Time: {hrs:02d}:{mins:02d}:{secs:02d}"
        self.time_panel.update_time(time_str)

    def get_logo_bitmap(self):
        """
        Membuat bitmap sampel. 
        Ganti baris di bawah dengan file gambar Anda sendiri:
        return wx.Bitmap("path/to/your/logo.png", wx.BITMAP_TYPE_PNG)
        """
        bmp = wx.Bitmap(32, 32)
        dc = wx.MemoryDC(bmp)
        dc.SetBackground(wx.Brush(wx.Colour(239, 68, 68))) # Merah
        dc.Clear()
        dc.SetTextForeground(wx.Colour(255, 255, 255))
        dc.DrawText("H", 10, 6)
        dc.SelectObject(wx.NullBitmap)
        return bmp


class ElapsedTimePanel(wx.Panel):
    """ Custom Panel menggunakan wx.GraphicsContext untuk membuat Rounded Rectangle """
    def __init__(self, parent):
        super().__init__(parent, size=(200, 36))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.time_text = "Elapsed Time: 00:00:00"
        
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def update_time(self, new_time_str):
        self.time_text = new_time_str
        self.Refresh() # Trigger EVT_PAINT

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            # Menggambar Rounded Rectangle
            width, height = self.GetClientSize()
            gc.SetBrush(wx.Brush(wx.Colour(51, 65, 85)))       # Warna fill (Slate Gray)
            gc.SetPen(wx.Pen(wx.Colour(71, 85, 105), 1))       # Border outline
            gc.DrawRoundedRectangle(2, 2, width - 4, height - 4, 12)  # Corner radius = 12

            # Menulis Teks di Tengah Rounded Rectangle
            font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            gc.SetFont(font, wx.Colour(56, 189, 248))  # Warna teks cyan/biru terang
            
            w, h, _, _ = gc.GetFullTextExtent(self.time_text)
            text_x = (width - w) / 2
            text_y = (height - h) / 2
            gc.DrawText(self.time_text, text_x, text_y)


if __name__ == '__main__':
    app = wx.App(False)
    frame = DashboardFrame(None, title="Helicopter Rescue Simulator Dashboard")
    frame.Show()
    app.MainLoop()