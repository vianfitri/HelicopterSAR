import math
import wx
import wx.grid as gridlib

# Data Dummy
ALL_DATA = [
    ("#014", "19 May 2024", "10:20:03", "00:04:32", "4.72 m", "12.84 m", "2"),
    ("#013", "19 May 2024", "09:45:11", "00:05:18", "4.95 m", "13.20 m", "3"),
    ("#012", "18 May 2024", "15:12:57", "00:03:47", "3.86 m", "10.42 m", "2"),
    ("#011", "18 May 2024", "14:01:22", "00:06:03", "4.20 m", "14.15 m", "4"),
    ("#010", "17 May 2024", "11:22:10", "00:04:55", "3.74 m", "11.30 m", "2"),
    ("#009", "17 May 2024", "09:18:35", "00:03:28", "2.95 m", "9.11 m", "1"),
    ("#008", "16 May 2024", "16:40:12", "00:08:11", "5.10 m", "15.00 m", "5"),
    ("#007", "16 May 2024", "13:10:00", "00:02:45", "3.20 m", "8.50 m", "1"),
    ("#006", "15 May 2024", "10:05:30", "00:05:00", "4.12 m", "11.20 m", "3"),
    ("#005", "15 May 2024", "08:30:15", "00:04:10", "3.90 m", "10.10 m", "2"),
    ("#004", "14 May 2024", "17:20:00", "00:06:50", "4.80 m", "13.40 m", "4"),
    ("#003", "14 May 2024", "14:15:22", "00:03:15", "2.85 m", "9.00 m", "1"),
    ("#002", "13 May 2024", "11:00:10", "00:05:40", "4.30 m", "12.00 m", "3"),
    ("#001", "13 May 2024", "09:00:00", "00:02:50", "3.00 m", "8.00 m", "1"),
]


class SessionHistoryFrame(wx.Frame):

    def __init__(self):
        super().__init__(
            None, title="Session History", size=(850, 520)
        )

        # Warna Tema Dark
        self.BG_COLOR = wx.Colour(19, 24, 32)
        self.CARD_BG = wx.Colour(23, 29, 38)
        self.TEXT_COLOR = wx.Colour(220, 225, 230)
        self.MUTED_TEXT = wx.Colour(130, 140, 150)
        self.ACCENT_COLOR = wx.Colour(217, 119, 6)

        self.SetBackgroundColour(self.BG_COLOR)

        # Konfigurasi Pagination
        self.page_size = 6
        self.current_page = 1
        self.total_items = len(ALL_DATA)
        self.total_pages = math.ceil(self.total_items / self.page_size)

        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Container Utama (Card Look)
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(self.CARD_BG)
        card_sizer = wx.BoxSizer(wx.VERTICAL)

        # --- 1. HEADER SECTION ---
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)

        title = wx.StaticText(self.panel, label="SESSION HISTORY")
        title.SetFont(
            wx.Font(
                13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
            )
        )
        title.SetForegroundColour(self.TEXT_COLOR)

        header_sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL)
        header_sizer.AddStretchSpacer()

        # Filter Dropdown & Search Bar
        filter_cb = wx.ComboBox(
            self.panel,
            value="All Sessions",
            choices=["All Sessions", "Active"],
            style=wx.CB_READONLY,
        )
        filter_cb.SetBackgroundColour(self.CARD_BG)
        filter_cb.SetForegroundColour(self.TEXT_COLOR)

        search_ctrl = wx.TextCtrl(
            self.panel, value="Search...", style=wx.TE_PROCESS_ENTER
        )
        search_ctrl.SetBackgroundColour(self.BG_COLOR)
        search_ctrl.SetForegroundColour(self.MUTED_TEXT)

        header_sizer.Add(filter_cb, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        header_sizer.Add(search_ctrl, 0, wx.ALIGN_CENTER_VERTICAL)

        card_sizer.Add(header_sizer, 0, wx.EXPAND | wx.ALL, 15)

        # --- 2. GRID / TABLE SECTION ---
        self.grid = gridlib.Grid(self.panel)
        self.grid.CreateGrid(self.page_size, 8)
        self.grid.SetGridLineColour(wx.Colour(35, 42, 52))
        self.grid.SetDefaultCellBackgroundColour(self.CARD_BG)
        self.grid.SetDefaultCellTextColour(self.TEXT_COLOR)

        # Sembunyikan Header Bawaan Grid
        self.grid.HideRowLabels()
        self.grid.SetColLabelSize(35)

        headers = [
            "Session ID",
            "Date",
            "Start Time",
            "Duration",
            "Max Position",
            "Max Hoist",
            "Hoist Cycles",
            "",
        ]
        for col, h in enumerate(headers):
            self.grid.SetColLabelValue(col, h)

        # Styling Custom Header Grid
        self.grid.SetLabelBackgroundColour(self.CARD_BG)
        self.grid.SetLabelTextColour(self.MUTED_TEXT)
        self.grid.SetLabelFont(
            wx.Font(
                9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
            )
        )

        # Penyesuaian Lebar Kolom & Alignment
        for i in range(7):
            self.grid.SetColSize(i, 105)
        self.grid.SetColSize(7, 30)

        for r in range(self.page_size):
            self.grid.SetRowSize(r, 42)

        card_sizer.Add(self.grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)

        # --- 3. PAGINATION FOOTER ---
        footer_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.info_text = wx.StaticText(self.panel, label="")
        self.info_text.SetForegroundColour(self.MUTED_TEXT)
        footer_sizer.Add(self.info_text, 0, wx.ALIGN_CENTER_VERTICAL)

        footer_sizer.AddStretchSpacer()

        # Tombol Pagination
        self.btn_first = wx.Button(self.panel, label="|<", size=(32, 28))
        self.btn_prev = wx.Button(self.panel, label="<", size=(32, 28))
        self.btn_next = wx.Button(self.panel, label=">", size=(32, 28))
        self.btn_last = wx.Button(self.panel, label=">|", size=(32, 28))

        # Binder Tombol Navigasi
        self.btn_first.Bind(wx.EVT_BUTTON, lambda e: self.go_to_page(1))
        self.btn_prev.Bind(
            wx.EVT_BUTTON, lambda e: self.go_to_page(self.current_page - 1)
        )
        self.btn_next.Bind(
            wx.EVT_BUTTON, lambda e: self.go_to_page(self.current_page + 1)
        )
        self.btn_last.Bind(
            wx.EVT_BUTTON, lambda e: self.go_to_page(self.total_pages)
        )

        nav_btns = [self.btn_first, self.btn_prev]
        for btn in nav_btns:
            footer_sizer.Add(btn, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 4)

        # Wadah Tombol Angka Halaman
        self.page_numbers_sizer = wx.BoxSizer(wx.HORIZONTAL)
        footer_sizer.Add(self.page_numbers_sizer, 0, wx.ALIGN_CENTER_VERTICAL)

        nav_btns_end = [self.btn_next, self.btn_last]
        for btn in nav_btns_end:
            footer_sizer.Add(
                btn, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 4
            )

        card_sizer.Add(footer_sizer, 0, wx.EXPAND | wx.ALL, 15)

        self.panel.SetSizer(card_sizer)
        main_sizer.Add(self.panel, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(main_sizer)

        self.update_grid()

    def update_grid(self):
        """Memuat ulang data ke grid berdasarkan halaman saat ini."""
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, self.total_items)
        page_data = ALL_DATA[start_idx:end_idx]

        # Reset Grid
        self.grid.ClearGrid()

        for row in range(self.page_size):
            if row < len(page_data):
                item = page_data[row]
                for col in range(7):
                    self.grid.SetCellValue(row, col, item[col])
                    self.grid.SetCellAlignment(
                        row, col, wx.ALIGN_CENTER, wx.ALIGN_CENTER
                    )
                self.grid.SetCellValue(row, 7, ">")
                self.grid.SetCellAlignment(
                    row, 7, wx.ALIGN_CENTER, wx.ALIGN_CENTER
                )
            else:
                for col in range(8):
                    self.grid.SetCellValue(row, col, "")

        # Highlight Baris Pertama (Meniru Gambar)
        for col in range(8):
            self.grid.SetCellTextColour(0, col, self.ACCENT_COLOR)

        # Update Teks Footer Info
        self.info_text.SetLabel(
            f"{start_idx + 1} - {end_idx} of {self.total_items} sessions"
        )

        self.update_pagination_buttons()
        self.Layout()

    def update_pagination_buttons(self):
        """Memperbarui tombol angka dan status tombol navigasi."""
        self.page_numbers_sizer.Clear(True)

        for p in range(1, self.total_pages + 1):
            btn = wx.Button(self.panel, label=str(p), size=(32, 28))
            if p == self.current_page:
                btn.SetForegroundColour(self.ACCENT_COLOR)
                btn.SetFont(
                    wx.Font(
                        9,
                        wx.FONTFAMILY_DEFAULT,
                        wx.FONTSTYLE_NORMAL,
                        wx.FONTWEIGHT_BOLD,
                    )
                )
            else:
                btn.SetForegroundColour(self.TEXT_COLOR)

            # Assign event untuk tombol angka
            btn.Bind(wx.EVT_BUTTON, lambda evt, page=p: self.go_to_page(page))
            self.page_numbers_sizer.Add(btn, 0, wx.RIGHT | wx.LEFT, 2)

        # Status aktif/non-aktif tombol navigasi
        self.btn_first.Enable(self.current_page > 1)
        self.btn_prev.Enable(self.current_page > 1)
        self.btn_next.Enable(self.current_page < self.total_pages)
        self.btn_last.Enable(self.current_page < self.total_pages)

        self.page_numbers_sizer.Layout()

    def go_to_page(self, page):
        """Pindah ke halaman tertentu."""
        if 1 <= page <= self.total_pages:
            self.current_page = page
            self.update_grid()


if __name__ == "__main__":
    app = wx.App(False)
    frame = SessionHistoryFrame()
    frame.Show()
    app.MainLoop()