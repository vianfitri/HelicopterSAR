import wx
import pygame
import os

class AudioEngine:
    def __init__(self):
        # Inisialisasi audio engine wx/pygame
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        
        # Alokasi channel audio independen
        pygame.mixer.set_num_channels(8)
        
        self.ch_heli = pygame.mixer.Channel(0)
        self.ch_wind = pygame.mixer.Channel(1)
        self.ch_waves = pygame.mixer.Channel(2)
        self.ch_raindrop = pygame.mixer.Channel(3)
        self.ch_rainhiss = pygame.mixer.Channel(4)
        
        # Master & Sub-group Volume (0.0 - 1.0)
        self.master_vol = 0.85
        self.heli_vol = 0.75
        self.env_vol = 0.70
        self.wind_vol = 0.55
        self.waves_vol = 0.40
        
        # Presentase rain internal (drop %, hiss %)
        self.rain_drop_ratio = 0.5
        self.rain_hiss_ratio = 0.5
        
        # State Mute
        self.is_muted = {
            'master': False, 'heli': False, 'env': False,
            'wind': False, 'waves': False
        }

        self.load_sounds()

    def load_sounds(self):
        """ Memuat dummy sound jika file lokal tidak ditemukan """
        def get_sound(filename):
            if os.path.exists(filename):
                return pygame.mixer.Sound(filename)
            # fallback silent sound untuk testing jika file belum ada
            return pygame.mixer.Sound(buffer=bytes([0] * 44100))

        self.snd_heli = get_sound("examples/audio/bell412_hover.wav")
        self.snd_wind = get_sound("examples/audio/wind.wav")
        self.snd_waves = get_sound("examples/audio/ocean_waves.wav")
        self.snd_raindrop = get_sound("examples/audio/rain_drop.wav")
        self.snd_rainhiss = get_sound("examples/audio/rain_hiss.wav")

    def start_all_loops(self):
        """ Memulai seluruh audio secara simultan dalam keadaan loop """
        self.ch_heli.play(self.snd_heli, loops=-1)
        self.ch_wind.play(self.snd_wind, loops=-1)
        self.ch_waves.play(self.snd_waves, loops=-1)
        self.ch_raindrop.play(self.snd_raindrop, loops=-1)
        self.ch_rainhiss.play(self.snd_rainhiss, loops=-1)
        self.update_volumes()

    def set_rain_preset(self, mode):
        """ Formula kombinasi suara Raindrop + Rain Hiss """
        if mode == 'light':
            self.rain_drop_ratio = 0.60
            self.rain_hiss_ratio = 0.15
        elif mode == 'moderate':
            self.rain_drop_ratio = 0.80
            self.rain_hiss_ratio = 0.50
        elif mode == 'heavy':
            self.rain_drop_ratio = 1.00
            self.rain_hiss_ratio = 0.95
        self.update_volumes()

    def update_volumes(self):
        """ Kalkulasi akhir volume real-time per-channel """
        if self.is_muted['master']:
            pygame.mixer.stop()
            return

        m = self.master_vol
        
        # Heli
        v_heli = 0 if self.is_muted['heli'] else m * self.heli_vol
        self.ch_heli.set_volume(v_heli)

        # Environmental Base (Wind & Waves)
        env_mult = 0 if self.is_muted['env'] else m * self.env_vol
        
        v_wind = 0 if self.is_muted['wind'] else env_mult * self.wind_vol
        v_waves = 0 if self.is_muted['waves'] else env_mult * self.waves_vol
        
        self.ch_wind.set_volume(v_wind)
        self.ch_waves.set_volume(v_waves)

        # Dynamic Rain Mixing
        v_drop = env_mult * self.rain_drop_ratio
        v_hiss = env_mult * self.rain_hiss_ratio
        self.ch_raindrop.set_volume(v_drop)
        self.ch_rainhiss.set_volume(v_hiss)


class AudioSettingsFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Helicopter Rescue Simulator - Audio Settings", size=(960, 560))
        self.audio = AudioEngine()
        
        # Color Palette sesuai desain (#0b121a)
        self.BG_COLOR = wx.Colour(11, 18, 26)
        self.PANEL_BG = wx.Colour(18, 28, 38)
        self.ACCENT_BLUE = wx.Colour(24, 119, 242)
        self.TEXT_COLOR = wx.Colour(230, 235, 240)
        self.MUTED_TEXT = wx.Colour(140, 155, 170)
        
        self.SetBackgroundColour(self.BG_COLOR)
        self.init_ui()
        self.audio.start_all_loops()
        self.Center()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # --- Header Section ---
        header_sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="AUDIO SETTINGS")
        title.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        title.SetForegroundColour(self.TEXT_COLOR)
        
        subtitle = wx.StaticText(self, label="Configure simulation sound levels and environmental effects.")
        subtitle.SetForegroundColour(self.MUTED_TEXT)
        
        header_sizer.Add(title, 0, wx.BOTTOM, 2)
        header_sizer.Add(subtitle, 0, wx.BOTTOM, 15)
        main_sizer.Add(header_sizer, 0, wx.ALL | wx.EXPAND, 20)

        # --- Middle Layout (2 Columns) ---
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Left Panel (Master & Core Audio)
        left_panel = self.create_card_panel("Master & Core Audio")
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.sld_master = self.add_audio_row(left_panel, left_sizer, "Master Volume", 85, self.on_master_change)
        self.sld_heli = self.add_audio_row(left_panel, left_sizer, "Helicopter Engine", 75, self.on_heli_change)
        self.sld_env = self.add_audio_row(left_panel, left_sizer, "Environmental SFX", 70, self.on_env_change)
        
        left_panel.SetSizer(left_sizer)
        
        # Right Panel (Weather & Ambient SFX)
        right_panel = self.create_card_panel("Weather & Ambient SFX")
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Rainfall Buttons (Light, Moderate, Heavy)
        rain_lbl = wx.StaticText(right_panel, label="Rainfall")
        rain_lbl.SetForegroundColour(self.TEXT_COLOR)
        right_sizer.Add(rain_lbl, 0, wx.BOTTOM, 8)
        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_light = wx.Button(right_panel, label="🌧️ Light", size=(90, 45))
        self.btn_mod = wx.Button(right_panel, label="🌧️ Moderate", size=(90, 45))
        self.btn_heavy = wx.Button(right_panel, label="⛈️ Heavy", size=(90, 45))
        
        for btn in [self.btn_light, self.btn_mod, self.btn_heavy]:
            btn.SetBackgroundColour(self.BG_COLOR)
            btn.SetForegroundColour(self.TEXT_COLOR)
            btn_sizer.Add(btn, 1, wx.RIGHT, 5)
            
        self.btn_light.Bind(wx.EVT_BUTTON, lambda e: self.set_rain('light'))
        self.btn_mod.Bind(wx.EVT_BUTTON, lambda e: self.set_rain('moderate'))
        self.btn_heavy.Bind(wx.EVT_BUTTON, lambda e: self.set_rain('heavy'))
        
        right_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.BOTTOM, 15)
        
        self.sld_wind = self.add_audio_row(right_panel, right_sizer, "Wind Intensity", 55, self.on_wind_change)
        self.sld_waves = self.add_audio_row(right_panel, right_sizer, "Ocean Waves", 40, self.on_waves_change)
        
        right_panel.SetSizer(right_sizer)
        
        content_sizer.Add(left_panel, 1, wx.EXPAND | wx.RIGHT, 10)
        content_sizer.Add(right_panel, 1, wx.EXPAND | wx.LEFT, 10)
        
        main_sizer.Add(content_sizer, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 20)

        # --- Footer Actions ---
        footer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_reset = wx.Button(self, label="RESET TO DEFAULT", size=(140, 35))
        btn_apply = wx.Button(self, label="APPLY CHANGES", size=(140, 35))
        btn_apply.SetBackgroundColour(self.ACCENT_BLUE)
        btn_apply.SetForegroundColour(wx.WHITE)
        
        footer_sizer.Add(btn_reset, 0, wx.RIGHT, 10)
        footer_sizer.AddStretchSpacer()
        footer_sizer.Add(btn_apply, 0)
        
        main_sizer.Add(footer_sizer, 0, wx.ALL | wx.EXPAND, 20)
        self.SetSizer(main_sizer)

    def create_card_panel(self, title_text):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(self.PANEL_BG)
        return panel

    def add_audio_row(self, parent, target_sizer, label_text, default_val, callback):
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        lbl = wx.StaticText(parent, label=label_text, size=(120, -1))
        lbl.SetForegroundColour(self.TEXT_COLOR)
        
        slider = wx.Slider(parent, value=default_val, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)
        slider.Bind(wx.EVT_SLIDER, callback)
        
        val_lbl = wx.StaticText(parent, label=f"{default_val}%", size=(40, -1))
        val_lbl.SetForegroundColour(self.TEXT_COLOR)
        slider.val_lbl = val_lbl 
        
        row_sizer.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        row_sizer.Add(slider, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        row_sizer.Add(val_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        
        target_sizer.Add(row_sizer, 0, wx.EXPAND | wx.BOTTOM, 12)
        return slider

    # --- Callbacks ---
    def on_master_change(self, event):
        val = self.sld_master.GetValue()
        self.sld_master.val_lbl.SetLabel(f"{val}%")
        self.audio.master_vol = val / 100.0
        self.audio.update_volumes()

    def on_heli_change(self, event):
        val = self.sld_heli.GetValue()
        self.sld_heli.val_lbl.SetLabel(f"{val}%")
        self.audio.heli_vol = val / 100.0
        self.audio.update_volumes()

    def on_env_change(self, event):
        val = self.sld_env.GetValue()
        self.sld_env.val_lbl.SetLabel(f"{val}%")
        self.audio.env_vol = val / 100.0
        self.audio.update_volumes()

    def on_wind_change(self, event):
        val = self.sld_wind.GetValue()
        self.sld_wind.val_lbl.SetLabel(f"{val}%")
        self.audio.wind_vol = val / 100.0
        self.audio.update_volumes()

    def on_waves_change(self, event):
        val = self.sld_waves.GetValue()
        self.sld_waves.val_lbl.SetLabel(f"{val}%")
        self.audio.waves_vol = val / 100.0
        self.audio.update_volumes()

    def set_rain(self, mode):
        self.audio.set_rain_preset(mode)

if __name__ == "__main__":
    app = wx.App()
    frame = AudioSettingsFrame()
    frame.Show()
    app.MainLoop()