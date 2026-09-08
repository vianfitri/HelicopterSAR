#import asyncio
#import math
#import struct
#import sys
#import termios
#import tty
#from pymodbus.datastore import (
#    ModbusDataBlock,
#    ModbusServerContext,
#    ModbusSlaveContext,
#)
#from pymodbus.server import StartAsyncTcpServer


# --- Data Block Kustom untuk Intersepsi Penulisan Register ---
#class HaiwellDataBlock(ModbusDataBlock):
#    def __init__(self, reset_callback):
#        super().__init__()
#        self.reset_callback = reset_callback
#        # Menyiapkan V-Register Haiwell (V0 - V9)
#        self.registers = [0] * 10

#    def getValues(self, address, count=1):
#        idx = address - 1
#        return self.registers[idx : idx + count]

#    def setValues(self, address, values):
#        idx = address - 1
#        for i, val in enumerate(values):
#            self.registers[idx + i] = val
#            # Memeriksa Command Register V6 (Index 6)
#            if (idx + i) == 6 and val == 1:
#                self.reset_callback()
#                self.registers[6] = 0  # Auto-reset command register


# --- Utility untuk Non-Blocking Keyboard Input ---
#class KeyReader:
#    def __enter__(self):
#        self.old_settings = termios.tcgetattr(sys.stdin)
#        tty.setcbreak(sys.stdin.fileno())
#        return self

#    def __exit__(self, type, value, traceback):
#Berikut adalah kode Python simulasi **Modbus TCP Server** yang disesuaikan dengan arsitektur memori PLC Haiwell (menggunakan *Register V* dan *Bit M*) serta kontrol interaktif menggunakan **keyboard**.

#---

### Mapping Alamat Register & Bit (PLC Haiwell Standard)

'''
PLC Haiwell menggunakan peta register standar Modbus berikut:

| Alamat Modbus | Komponel / Variabel | Tipe Data | Deskripsi |
| :--- | :--- | :--- | :--- |
| **V0 (HR 40001 / Addr 0)** | Encoder Counter (High Word) | INT32 | Pulsa akumulasi quadrature ($1024 \times 4 = 4096$ CPR) |
| **V1 (HR 40002 / Addr 1)** | Encoder Counter (Low Word) | | |
| **V2 (HR 40003 / Addr 2)** | Kecepatan RPM | INT16 | RPM aktual (Positif: Maju, Negatif: Mundur) |
| **V3 (HR 40004 / Addr 3)** | Jarak Tempuh (cm) | UINT16 | Jarak tempuh dalam centimeter (Misal: $150 = 1,50$ m) |
| **M0 (Coil 00001 / Addr 0)** | Status Homing Sensor 1 | BIT | Redundansi Sensor Homing Utama |
| **M1 (Coil 00002 / Addr 1)** | Status Homing Sensor 2 | BIT | Redundansi Sensor Homing Sekunder |
| **M2 (Coil 00003 / Addr 2)** | Status Limit Switch Max 1 | BIT | Redundansi Limit Switch Maksimum Utama |
| **M3 (Coil 00004 / Addr 3)** | Status Limit Switch Max 2 | BIT | Redundansi Limit Switch Maksimum Sekunder |

---

### Kode Python Simulasi (Pymodbus v3.6.8)

> **Catatan Sebelum Mengalankan Script:**
> Script ini menggunakan *library* `pynput` untuk membaca *keystroke* keyboard secara *real-time*. Install terlebih dahulu via terminal jika belum ada:
> ```bash
> pip install pynput pymodbus
> ```
'''

#python
import asyncio
import math
import struct
from pynput import keyboard
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.server import StartAsyncTcpServer


class HaiwellPLCSimulation:

    def __init__(self):
        # --- Parameter Fisik & Encoder ---
        self.ppr = 1024
        self.cpr = self.ppr * 4  # Quadrature encoder = 4096 CPR
        self.wheel_diameter = 0.25  # 25 cm = 0.25 meter
        self.wheel_circumference = math.pi * self.wheel_diameter  # ~0.7854 m

        # --- Internal States ---
        self.counter = 0
        self.rpm = 0.0
        self.distance_m = 0.0

        # Redundansi Status Sensor (M0 - M3)
        self.homing_1 = False
        self.homing_2 = False
        self.limit_max_1 = False
        self.limit_max_2 = False

        # Status Kontrol Tombol Keyboard
        self.key_forward = False
        self.key_reverse = False

        # Speed setting simulasi (RPM)
        self.target_rpm_fwd = 15.0  # RPM Rendah Maju
        self.target_rpm_rev = -15.0  # RPM Rendah Mundur

        # --- Inisialisasi DataStore Modbus ---
        # Holding Registers (V-Registers Haiwell: V0-V9)
        # Parameter pertama adalah address awal (0), kedua adalah list nilai awal
        self.hr_block = ModbusSequentialDataBlock(0, [0] * 10)
        #self.hr_block.registers = [0] * 10

        # Coils (M-Bits Haiwell: M0-M9)
        self.coils_block = ModbusSequentialDataBlock(0, [0] * 10)
        #self.coils_block.registers = [0] * 10

        # Create Slave Context
        slave_context = ModbusSlaveContext(
            hr=self.hr_block,
            co=self.coils_block,
            zero_mode=True,  # 0-based indexing (Standard Haiwell)
        )
        self.context = ModbusServerContext(slaves=slave_context, single=True)

    def trigger_homing(self, state: bool):
        """Aktifkan/nonaktifkan kedua sensor homing (Redundansi)."""
        self.homing_1 = state
        self.homing_2 = state

        if state:
            # Menghentikan gerakan mundur, reset counter & jarak tempuh ke 0
            self.counter = 0
            self.distance_m = 0.0

    def trigger_limit_max(self, state: bool):
        """Aktifkan/nonaktifkan kedua limit switch max (Redundansi)."""
        self.limit_max_1 = state
        self.limit_max_2 = state

    def update_modbus_registers(self):
        """Memperbarui nilai V-Register & M-Bits di Modbus Server."""
        # 1. Convert INT32 Counter ke dua INT16 Register (High Word, Low Word)
        packed_counter = struct.pack(">i", self.counter)
        hi_word, lo_word = struct.unpack(">HH", packed_counter)

        # 2. Convert RPM ke INT16
        rpm_val = int(self.rpm) & 0xFFFF

        # 3. Convert Jarak Tempuh ke UINT16 (Skala cm: x100)
        dist_val = int(self.distance_m * 100) & 0xFFFF

        # Map V-Registers (V0 - V3)
        #self.hr_block.registers[0] = hi_word  # V0 (Address 0)
        #self.hr_block.registers[1] = lo_word  # V1 (Address 1)
        #self.hr_block.registers[2] = rpm_val  # V2 (Address 2)
        #self.hr_block.registers[3] = dist_val  # V3 (Address 3)

        # Set nilai V-Registers (V0 - V3) di Address 1 (0-based: address=1)
        self.hr_block.setValues(1, [hi_word, lo_word, rpm_val, dist_val])

        # Map M-Bits Coils (M0 - M3)
        #self.coils_block.registers[0] = 1 if self.homing_1 else 0  # M0
        #self.coils_block.registers[1] = 1 if self.homing_2 else 0  # M1
        #self.coils_block.registers[2] = 1 if self.limit_max_1 else 0  # M2
        #self.coils_block.registers[3] = 1 if self.limit_max_2 else 0  # M3

        # Set nilai M-Bits Coils (M0 - M3) di Address 1 (0-based: address=1)
        m0 = 1 if self.homing_1 else 0
        m1 = 1 if self.homing_2 else 0
        m2 = 1 if self.limit_max_1 else 0
        m3 = 1 if self.limit_max_2 else 0
        self.coils_block.setValues(1, [m0, m1, m2, m3])

    async def simulation_loop(self):
        """Loop kalkulasi fisik encoder & eksekusi logika interlock."""
        dt = 0.05  # Refresh rate per 50 ms

        while True:
            # --- Interlock & Logika Pergerakan ---
            # Homing aktif jika minimal salah satu sensor Redundant M0/M1 menyala
            is_homing_active = self.homing_1 or self.homing_2

            # Limit Max aktif jika minimal salah satu sensor Redundant M2/M3 menyala
            is_limit_max_active = self.limit_max_1 or self.limit_max_2

            current_rpm = 0.0

            # Gerakan MAJU
            if self.key_forward and not self.key_reverse:
                if is_limit_max_active:
                    # Hentikan simulasi maju jika menyentuh Maximum Limit Switch
                    current_rpm = 0.0
                else:
                    current_rpm = self.target_rpm_fwd

            # Gerakan MUNDUR
            elif self.key_reverse and not self.key_forward:
                if is_homing_active:
                    # Hentikan simulasi mundur jika menyentuh Sensor Homing
                    current_rpm = 0.0
                else:
                    current_rpm = self.target_rpm_rev

            self.rpm = current_rpm

            # --- Kalkulasi Pulsa & Jarak ---
            if self.rpm != 0:
                delta_counts = (self.rpm / 60.0) * self.cpr * dt
                self.counter += int(delta_counts)

                revolutions = self.counter / self.cpr
                self.distance_m = revolutions * self.wheel_circumference

            # Update ke memory PLC
            self.update_modbus_registers()

            await asyncio.sleep(dt)

    def print_status(self):
        """Menampilkan log status simulasi pada terminal."""
        is_h = "AKTIF" if (self.homing_1 or self.homing_2) else "OFF"
        is_l = "AKTIF" if (self.limit_max_1 or self.limit_max_2) else "OFF"
        print(
            f"\r[Simulasi PLC] Counter: {self.counter:<8} | RPM: {self.rpm:<5.1f} | "
            f"Jarak: {self.distance_m:.2f}m | Homing(M0/M1): {is_h:<5} | LimitMax(M2/M3): {is_l:<5}",
            end="",
        )


# --- Keyboard Listener Callback ---
def setup_keyboard_listener(sim: HaiwellPLCSimulation):

    def on_press(key):
        try:
            if key.char == "w":
                sim.key_forward = True
            elif key.char == "s":
                sim.key_reverse = True
            elif key.char == "h":
                sim.trigger_homing(True)
            elif key.char == "l":
                sim.trigger_limit_max(True)
        except AttributeError:
            pass

    def on_release(key):
        try:
            if key.char == "w":
                sim.key_forward = False
            elif key.char == "s":
                sim.key_reverse = False
            elif key.char == "h":
                sim.trigger_homing(False)
            elif key.char == "l":
                sim.trigger_limit_max(False)
        except AttributeError:
            pass

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()


# --- Main Runner ---
async def main():
    sim = HaiwellPLCSimulation()

    # Jalankan listener keyboard
    setup_keyboard_listener(sim)

    # Task simulasi encoder fisik
    asyncio.create_task(sim.simulation_loop())

    print("======================================================================")
    print("       SIMULASI PLC HAIWELL AT16S0R - MODBUS TCP ENCODER SERVER       ")
    print("======================================================================")
    print(" Server Running pada IP: 127.0.0.1 | Port: 5020")
    print(" Address V-Register: V0-V1 (Counter), V2 (RPM), V3 (Jarak cm)")
    print(" Address M-Bits    : M0/M1 (Homing), M2/M3 (Limit Max)")
    print("----------------------------------------------------------------------")
    print(" KONTROL SIMULASI KEYBOARD (Tekan dan Tahan / Hold):")
    print("  [W] : Putar Maju (RPM +15)")
    print("  [S] : Putar Mundur (RPM -15)")
    print("  [H] : Sensor Homing Trigger (Reset Counter & Lock Mundur)")
    print("  [L] : Limit Switch Max Trigger (Lock Maju)")
    print("======================================================================\n")

    # Display update loop
    async def display_task():
        while True:
            sim.print_status()
            await asyncio.sleep(0.1)

    asyncio.create_task(display_task())

    # Start Modbus TCP Server
    await StartAsyncTcpServer(
        context=sim.context, address=("127.0.0.1", 5020)
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nSimulasi PLC Haiwell Dihentikan.")