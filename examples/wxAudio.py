import wx
import pygame
import os
import random

class AudioEngine:
    def __init__(self):
        # Inisialisasi audio engine pygame
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(10)
        
        # Channel Audio
        self.ch_heli = pygame.mixer.Channel(0)
        self.ch_wind = pygame.mixer.Channel(1)
        self.ch_waves = pygame.mixer.Channel(2)
        self.ch_raindrop = pygame.mixer.Channel(3)
        self.ch_rainhiss = pygame.mixer.Channel(4)
        self.ch_thunder = pygame.mixer.Channel(5)
        
        # Volume Master & Individu (0.0 - 1.0)
        self.master_vol = 0.85
        self.heli_vol = 0.75
        self.wind_vol = 0.55
        self.waves_vol = 0.40
        self.rain_vol = 0.70
        self.thunder_vol = 0.80
        
        # State Enable/Disable (Toggle ON/OFF) per SFX
        self.enabled = {
            'master': True,
            'heli': True,
            'wind': True,
            'waves': True,
            'rain': True,
            'thunder': True
        }
        
        # Rasio Hujan Internal (Raindrop vs Rain Hiss)
        self.rain_drop_ratio = 0.80
        self.rain_hiss_ratio = 0.50

        self.target_drop_ratio = 0.80
        self.target_hiss_ratio = 0.50
        
        # Preset Interval Petir (Min Sec, Max Sec)
        self.thunder_presets = {
            'light': (45, 90),     # Petir jarang
            'moderate': (25, 50),  # Petir sedang
            'heavy': (10, 25)      # Petir sering (badai)
        }
        self.current_thunder_preset = 'moderate'

        self.load_sounds()

    def load_sounds(self):
        """ Memuat dummy sound jika file lokal tidak ditemukan """
        def get_sound(filename):
            if os.path.exists(filename):
                return pygame.mixer.Sound(filename)
            return pygame.mixer.Sound(buffer=bytes([0] * 44100))

        self.snd_heli = get_sound("examples/audio/bell412_hover.wav")
        self.snd_wind = get_sound("examples/audio/wind.wav")
        self.snd_waves = get_sound("examples/audio/ocean_waves.wav")
        self.snd_raindrop = get_sound("examples/audio/rain_drop.wav")
        self.snd_rainhiss = get_sound("examples/audio/rain_hiss.wav")
        
        self.snd_thunders = [
            get_sound("examples/audio/thunder_1.wav"),
            get_sound("examples/audio/thunder_2.wav"),
            get_sound("examples/audio/thunder_3.wav")
        ]

    def start_all_loops(self):
        """ Memulai seluruh audio loop utama """
        self.ch_heli.play(self.snd_heli, loops=-1)
        self.ch_wind.play(self.snd_wind, loops=-1)
        self.ch_waves.play(self.snd_waves, loops=-1)
        self.ch_raindrop.play(self.snd_raindrop, loops=-1)
        self.ch_rainhiss.play(self.snd_rainhiss, loops=-1)
        self.update_volumes()

    def play_random_thunder(self):
        """ Memainkan variasi petir jika aktif """
        if not self.enabled['master'] or not self.enabled['thunder']:
            return

        selected_thunder = random.choice(self.snd_thunders)
        vol_variation = random.uniform(0.85, 1.0)
        final_vol = self.master_vol * self.thunder_vol * vol_variation
        
        self.ch_thunder.set_volume(final_vol)
        self.ch_thunder.play(selected_thunder)

    def set_rain_target(self, mode):
        """ menentukan target rasio hujan baru untuk dituju oleh transisi halus"""
        if mode == 'light':
            self.target_drop_ratio = 0.60
            self.target_hiss_ratio = 0.15
        elif mode == 'moderate':
            self.target_drop_ratio = 0.80
            self.target_hiss_ratio = 0.50
        elif mode == 'heavy':
            self.target_drop_ratio = 1.00
            self.target_hiss_ratio = 0.95

        self.current_thunder_preset = mode

    def step_rain_transition(self, step_speed=0.02):
        """ Menggeser rasio hujan mendekati target secara bertahap (Smooth Crossfade)"""
        # Transisi Drop Ratio
        if abs(self.rain_drop_ratio - self.target_drop_ratio) > step_speed:
            if self.rain_drop_ratio < self.target_drop_ratio:
                self.rain_drop_ratio += step_speed
            else:
                self.rain_drop_ratio -= step_speed
        else:
            self.rain_drop_ratio = self.target_drop_ratio

        # Transisi Hiss Ratio
        if abs(self.rain_hiss_ratio - self.target_hiss_ratio) > step_speed:
            if self.rain_hiss_ratio < self.target_hiss_ratio:
                self.rain_hiss_ratio += step_speed
            else:
                self.rain_hiss_ratio -= step_speed
        else:
            self.rain_hiss_ratio = self.target_hiss_ratio

        self.update_volumes()

        # Return True jika transisi sudah selesai sepenuhnya
        return (self.rain_drop_ratio == self.target_drop_ratio) and (self.rain_hiss_ratio == self.target_hiss_ratio)

    #def set_rain_preset(self, mode):
    #    """ Pengaturan rasio hujan & preset petir sinkron """
    #    if mode == 'light':
    #        self.rain_drop_ratio = 0.60
    #        self.rain_hiss_ratio = 0.15
    #    elif mode == 'moderate':
    #        self.rain_drop_ratio = 0.80
    #        self.rain_hiss_ratio = 0.50
    #    elif mode == 'heavy':
    #        self.rain_drop_ratio = 1.00
    #        self.rain_hiss_ratio = 0.95
    #        
    #    self.current_thunder_preset = mode
    #    self.update_volumes()

    def get_next_thunder_interval(self):
        """ Mengambil jeda detik acak berdasarkan preset aktif """
        min_sec, max_sec = self.thunder_presets[self.current_thunder_preset]
        return random.randint(min_sec, max_sec)

    def update_volumes(self):
        """ Kalkulasi akhir volume real-time per-channel """
        if not self.enabled['master']:
            self.ch_heli.set_volume(0)
            self.ch_wind.set_volume(0)
            self.ch_waves.set_volume(0)
            self.ch_raindrop.set_volume(0)
            self.ch_rainhiss.set_volume(0)
            return

        m = self.master_vol
        
        # 1. Helicopter
        v_heli = (m * self.heli_vol) if self.enabled['heli'] else 0
        self.ch_heli.set_volume(v_heli)

        # 2. Wind
        v_wind = (m * self.wind_vol) if self.enabled['wind'] else 0
        self.ch_wind.set_volume(v_wind)

        # 3. Waves
        v_waves = (m * self.waves_vol) if self.enabled['waves'] else 0
        self.ch_waves.set_volume(v_waves)

        # 4. Rain (Raindrop + Rain Hiss)
        if self.enabled['rain']:
            v_drop = m * self.rain_vol * self.rain_drop_ratio
            v_hiss = m * self.rain_vol * self.rain_hiss_ratio
        else:
            v_drop, v_hiss = 0, 0
            
        self.ch_raindrop.set_volume(v_drop)
        self.ch_rainhiss.set_volume(v_hiss)


class AudioSettingsFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Helicopter Rescue Simulator - Audio Settings", size=(1000, 720))
        self.audio = AudioEngine()
        
        # Timer untuk memicu suara petir
        self.thunder_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_thunder_timer, self.thunder_timer)

        # Timer untuk transisi halus preset hujan (50ms interval update)
        self.transition_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_transition_step, self.transition_timer)
        
        # UI Palette
        self.BG_COLOR = wx.Colour(11, 18, 26)
        self.PANEL_BG = wx.Colour(18, 28, 38)
        self.ACCENT_BLUE = wx.Colour(24, 119, 242)
        self.TEXT_COLOR = wx.Colour(230, 235, 240)
        self.MUTED_TEXT = wx.Colour(140, 155, 170)
        
        self.SetBackgroundColour(self.BG_COLOR)
        self.init_ui()
        self.audio.start_all_loops()
        self.schedule_next_thunder()
        self.Center()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # --- Header ---
        header_sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="AUDIO SETTINGS")
        title.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        title.SetForegroundColour(self.TEXT_COLOR)
        
        subtitle = wx.StaticText(self, label="Configure simulation sound levels, toggles, and environmental presets.")
        subtitle.SetForegroundColour(self.MUTED_TEXT)
        
        header_sizer.Add(title, 0, wx.BOTTOM, 2)
        header_sizer.Add(subtitle, 0, wx.BOTTOM, 15)
        main_sizer.Add(header_sizer, 0, wx.ALL | wx.EXPAND, 20)

        # --- Content Grid (2 Kolom) ---
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Panel Kiri (Master & Core)
        left_panel = wx.Panel(self)
        left_panel.SetBackgroundColour(self.PANEL_BG)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        left_title = wx.StaticText(left_panel, label="Master & Core Audio")
        left_title.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        left_title.SetForegroundColour(self.TEXT_COLOR)
        left_sizer.Add(left_title, 0, wx.BOTTOM, 15)
        
        self.sld_master = self.add_audio_control(left_panel, left_sizer, "Master Volume", 85, 
                                                 self.on_master_change, 'master', self.on_toggle_sfx)
        self.sld_heli = self.add_audio_control(left_panel, left_sizer, "Helicopter Engine", 75, 
                                               self.on_heli_change, 'heli', self.on_toggle_sfx)
        
        left_panel.SetSizer(left_sizer)
        
        # Panel Kanan (Environment & Weather)
        right_panel = wx.Panel(self)
        right_panel.SetBackgroundColour(self.PANEL_BG)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        right_title = wx.StaticText(right_panel, label="Environment & Weather SFX")
        right_title.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        right_title.SetForegroundColour(self.TEXT_COLOR)
        right_sizer.Add(right_title, 0, wx.BOTTOM, 15)
        
        # Preset Hujan & Petir
        rain_lbl = wx.StaticText(right_panel, label="Rain & Thunder Intensity Preset")
        rain_lbl.SetForegroundColour(self.TEXT_COLOR)
        right_sizer.Add(rain_lbl, 0, wx.BOTTOM, 8)
        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_light = wx.Button(right_panel, label="🌧️ Light", size=(90, 35))
        self.btn_mod = wx.Button(right_panel, label="🌧️ Moderate", size=(90, 35))
        self.btn_heavy = wx.Button(right_panel, label="⛈️ Heavy", size=(90, 35))
        
        for btn in [self.btn_light, self.btn_mod, self.btn_heavy]:
            btn.SetBackgroundColour(self.BG_COLOR)
            btn.SetForegroundColour(self.TEXT_COLOR)
            btn_sizer.Add(btn, 1, wx.RIGHT, 5)
            
        self.btn_light.Bind(wx.EVT_BUTTON, lambda e: self.set_rain('light'))
        self.btn_mod.Bind(wx.EVT_BUTTON, lambda e: self.set_rain('moderate'))
        self.btn_heavy.Bind(wx.EVT_BUTTON, lambda e: self.set_rain('heavy'))
        
        right_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.BOTTOM, 15)
        
        # Slider & Checkbox SFX Lingkungan
        self.sld_rain = self.add_audio_control(right_panel, right_sizer, "Rain Effect", 70, 
                                               self.on_rain_change, 'rain', self.on_toggle_sfx)
        self.sld_wind = self.add_audio_control(right_panel, right_sizer, "Wind SFX", 55, 
                                               self.on_wind_change, 'wind', self.on_toggle_sfx)
        self.sld_waves = self.add_audio_control(right_panel, right_sizer, "Ocean Waves", 40, 
                                                self.on_waves_change, 'waves', self.on_toggle_sfx)
        self.sld_thunder = self.add_audio_control(right_panel, right_sizer, "Thunder SFX", 80, 
                                                  self.on_thunder_change, 'thunder', self.on_toggle_sfx)
        
        right_panel.SetSizer(right_sizer)
        
        content_sizer.Add(left_panel, 1, wx.EXPAND | wx.RIGHT, 10)
        content_sizer.Add(right_panel, 1, wx.EXPAND | wx.LEFT, 10)
        
        main_sizer.Add(content_sizer, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 20)

        # --- Footer ---
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

    def add_audio_control(self, parent, target_sizer, label_text, default_val, slider_cb, sfx_key, toggle_cb):
        """ Membuat Komponen UI Gabungan: Checkbox (Enable/Disable) + Slider Volume """
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Checkbox Enable/Disable
        chk = wx.CheckBox(parent, label="")
        chk.SetValue(True)
        chk.sfx_key = sfx_key
        chk.Bind(wx.EVT_CHECKBOX, toggle_cb)
        
        lbl = wx.StaticText(parent, label=label_text, size=(120, -1))
        lbl.SetForegroundColour(self.TEXT_COLOR)
        
        slider = wx.Slider(parent, value=default_val, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)
        slider.Bind(wx.EVT_SLIDER, slider_cb)
        
        val_lbl = wx.StaticText(parent, label=f"{default_val}%", size=(40, -1))
        val_lbl.SetForegroundColour(self.TEXT_COLOR)
        slider.val_lbl = val_lbl 
        
        row_sizer.Add(chk, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        row_sizer.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        row_sizer.Add(slider, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        row_sizer.Add(val_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        
        target_sizer.Add(row_sizer, 0, wx.EXPAND | wx.BOTTOM, 12)
        return slider

    # --- Callbacks Enable/Disable ---
    def on_toggle_sfx(self, event):
        chk = event.GetEventObject()
        key = chk.sfx_key
        self.audio.enabled[key] = chk.IsChecked()
        
        if key == 'thunder' and chk.IsChecked():
            self.schedule_next_thunder()
            
        self.audio.update_volumes()

    # --- Callbacks Slider Volume ---
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

    def on_rain_change(self, event):
        val = self.sld_rain.GetValue()
        self.sld_rain.val_lbl.SetLabel(f"{val}%")
        self.audio.rain_vol = val / 100.0
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

    def on_thunder_change(self, event):
        val = self.sld_thunder.GetValue()
        self.sld_thunder.val_lbl.SetLabel(f"{val}%")
        self.audio.thunder_vol = val / 100.0

    # --- Transisi Preset Hujan ---
    def trigger_rain_transition(self, mode):
        self.audio.set_rain_target(mode)
        self.schedule_next_thunder()

        # Mulai timer transisi halus (setiap 50ms)
        if not self.transition_timer.IsRunning():
            self.transition_timer.Start(50)

    def on_transition_step(self, event):
        """ Callback timer yang memperbarui slider/volume secara bertahap """
        is_complete = self.audio.step_rain_transition(step_speed=0.03)
        if is_complete:
            self.transition_timer.Stop()

    #def set_rain(self, mode):
    #    self.audio.set_rain_preset(mode)
    #    self.schedule_next_thunder()

    # --- Pengatur Interval Petir ---
    def schedule_next_thunder(self):
        if not self.audio.enabled['thunder']:
            self.thunder_timer.Stop()
            return
            
        interval_sec = self.audio.get_next_thunder_interval()
        self.thunder_timer.StartOnce(interval_sec * 1000)

    def on_thunder_timer(self, event):
        if self.audio.enabled['thunder']:
            self.audio.play_random_thunder()
            self.schedule_next_thunder()

if __name__ == "__main__":
    app = wx.App()
    frame = AudioSettingsFrame()
    frame.Show()
    app.MainLoop()