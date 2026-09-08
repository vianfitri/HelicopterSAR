import wx
import cv2
import numpy as np
import datetime

class StaticNoisePanel(wx.Panel):
    def __init__(self, parent, channel_num):
        super().__init__(parent)
        self.channel_num = channel_num
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        
        # Ukuran buffer noise (dibuat lebih kecil dari layar lalu di-scale agar performa di Pi 4 tinggi)
        self.noise_w = 320
        self.noise_h = 240
        
        self.bmp = None
        
        # Timer untuk pembaruan frame bersemut (~20 FPS)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(50)  # 50 ms = 20 FPS
        
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        
        # Toggle untuk efek blink indikator REC
        self.rec_blink = True
        self.blink_counter = 0

    def generate_noise_frame(self):
        # Generate random static noise
        noise = np.random.randint(0, 256, (self.noise_h, self.noise_w), dtype=np.uint8)
        
        # Konversi ke BGR/RGB
        noise_bgr = cv2.cvtColor(noise, cv2.COLOR_GRAY2BGR)
        
        # Tambahkan Text overlay "NO SIGNAL" di tengah
        text = "NO SIGNAL"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.8
        thick = 2
        size = cv2.getTextSize(text, font, scale, thick)[0]
        x = (self.noise_w - size[0]) // 2
        y = (self.noise_h + size[1]) // 2
        
        # Teks NO SIGNAL dengan outline hitam dan isi merah/putih
        cv2.putText(noise_bgr, text, (x, y), font, scale, (0, 0, 0), thick + 2)
        cv2.putText(noise_bgr, text, (x, y), font, scale, (0, 0, 255), thick)

        # OSD: Nama Channel (Kiri Atas)
        ch_text = f"CAM 0{self.channel_num}"
        cv2.putText(noise_bgr, ch_text, (10, 25), font, 0.5, (0, 0, 0), 2)
        cv2.putText(noise_bgr, ch_text, (10, 25), font, 0.5, (255, 255, 255), 1)

        # OSD: Timestamp / Tanggal & Waktu (Kanan Atas)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(noise_bgr, now, (self.noise_w - 180, 25), font, 0.4, (0, 0, 0), 2)
        cv2.putText(noise_bgr, now, (self.noise_w - 180, 25), font, 0.4, (255, 255, 255), 1)

        # OSD: Indikator REC Kedip (Kiri Bawah)
        if self.rec_blink:
            cv2.circle(noise_bgr, (15, self.noise_h - 15), 5, (0, 0, 255), -1)
            cv2.putText(noise_bgr, "REC", (25, self.noise_h - 10), font, 0.4, (0, 0, 0), 2)
            cv2.putText(noise_bgr, "REC", (25, self.noise_h - 10), font, 0.4, (255, 255, 255), 1)

        # OSD: Info Bitrate/FPS (Kanan Bawah)
        info_text = "Kbps: 0 | 0fps"
        cv2.putText(noise_bgr, info_text, (self.noise_w - 120, self.noise_h - 10), font, 0.35, (255, 255, 255), 1)

        # Konversi OpenCV image (BGR) ke wx.Bitmap
        rgb = cv2.cvtColor(noise_bgr, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb.shape
        image = wx.Image(w, h, rgb.tobytes())
        
        # Resize bitmap sesuai ukuran panel saat ini
        pw, ph = self.GetClientSize()
        if pw > 0 and ph > 0:
            image = image.Scale(pw, ph, wx.IMAGE_QUALITY_NORMAL)
            
        return wx.Bitmap(image)

    def on_timer(self, event):
        self.blink_counter += 1
        if self.blink_counter % 10 == 0:  # Berkedip setiap detik
            self.rec_blink = not self.rec_blink
            
        self.bmp = self.generate_noise_frame()
        self.Refresh(eraseBackground=False)

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        if self.bmp:
            dc.DrawBitmap(self.bmp, 0, 0)

    def on_size(self, event):
        self.Refresh()
        event.Skip()


class DVRMainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="HIKVISION / DAHUA DVR - DUMMY CCTV SYSTEM", size=(1024, 768))
        
        self.SetBackgroundColour(wx.Colour(10, 10, 10))  # Garis pemisah hitam gelap

        # Grid Sizer 2x2 untuk 4 Kotak CCTV
        grid = wx.GridSizer(2, 2, 2, 2)  # 2 baris, 2 kolom, gap 2px

        for i in range(1, 5):
            panel = StaticNoisePanel(self, channel_num=i)
            grid.Add(panel, 1, wx.EXPAND)

        self.SetSizer(grid)
        
        # Shortcut Keyboard: Tekan 'F' untuk Fullscreen, 'Esc' / 'Q' untuk Keluar
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

    def on_key(self, event):
        key = event.GetKeyCode()
        if key == ord('F') or key == ord('f'):
            self.ShowFullScreen(not self.IsFullScreen())
        elif key == wx.WXK_ESCAPE or key == ord('Q') or key == ord('q'):
            self.Close()
        else:
            event.Skip()


class CCTVApp(wx.App):
    def OnInit(self):
        frame = DVRMainFrame()
        frame.Show()
        # Aktifkan mode Fullscreen secara default jika diinginkan:
        # frame.ShowFullScreen(True)
        return True


if __name__ == '__main__':
    app = CCTVApp()
    app.MainLoop()