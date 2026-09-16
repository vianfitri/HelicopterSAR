import time
import random
import threading
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

# IP dan Port Server Simulator
# Pakai "0.0.0.0" agar server menerima koneksi dari IP apa saja (termasuk 127.0.0.1 dan 192.168.1.111)
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 502

# Inisialisasi Data Block Modbus
# FX 01 (Coils) - Y
coils = ModbusSequentialDataBlock(0, [False] * 200)

# FX 02 (Discrete Inputs) - X
discrete_inputs = ModbusSequentialDataBlock(0, [False] * 200)

# FX 03 (Holding Registers) - V
holding_registers = ModbusSequentialDataBlock(0, [0] * 200)

# Gabungkan ke context Modbus Slave
store = ModbusSlaveContext(
    di=discrete_inputs, # Discrete Inputs (X)
    co=coils,           # Coils (Y)
    hr=holding_registers# Holding Registers (V)
)
context = ModbusServerContext(slaves=store, single=True)

def simulate_plc_data():
    """Thread untuk mensimulasikan perubahan data pada PLC (Limit Switch, Lampu, dan Register V)."""
    print("[Simulator] Simulasi data PLC berjalan...")
    
    # Nilai awal simulasi
    rpm = 1200
    speed2 = 50
    hoist_load = 450

    while True:
        try:
            # 1. Simulasi Input Limit Switch (X7 - X10) -> Alamat offset 7-10
            # Data diubah-ubah secara acak setiap beberapa detik
            x_values = [
                random.choice([True, False]),  # X7 (FRWD1)
                random.choice([True, False]),  # X8 (FRWD2)
                random.choice([True, False]),  # X9 (RVRS1)
                random.choice([True, False])   # X10 (RVRS2)
            ]
            store.setValues(fx=2, address=7, values=x_values)

            # 2. Simulasi Output Lampu (Y8 - Y11) -> Alamat offset 8-11
            y_values = [
                random.choice([True, False]),  # Y8 (FRWD Lamp)
                random.choice([True, False]),  # Y9 (RVRS Lamp)
                random.choice([True, False]),  # Y10 (Hoist Up Lamp)
                random.choice([True, False])   # Y11 (Hoist Down Lamp)
            ]
            store.setValues(fx=1, address=8, values=y_values)

            # 3. Simulasi Data Analog/Register V (V32, V34, V102)
            rpm = max(800, min(1800, rpm + random.randint(-50, 50)))
            speed2 = max(10, min(100, speed2 + random.randint(-5, 5)))
            hoist_load = max(100, min(1000, hoist_load + random.randint(-20, 20)))

            # Tulis nilai ke Holding Register Modbus (FX 03)
            store.setValues(fx=3, address=32, values=[rpm])         # V32 (RPM)
            store.setValues(fx=3, address=34, values=[speed2])      # V34 (SPEED2)
            store.setValues(fx=3, address=102, values=[hoist_load]) # V102 (Hoist Load)

            time.sleep(1) # Perbarui data simulator setiap 1 detik
            
        except Exception as e:
            print(f"[Simulator Error] {e}")
            break

if __name__ == "__main__":
    # Jalankan simulator data di background thread
    sim_thread = threading.Thread(target=simulate_plc_data, daemon=True)
    sim_thread.start()

    print(f"==================================================")
    print(f" Modbus TCP Server Simulator PLC Haiwell Running  ")
    print(f" Host: {SERVER_HOST} | Port: {SERVER_PORT}       ")
    print(f" Tekan Ctrl+C untuk menghentikan server           ")
    print(f"==================================================")

    # Jalankan Modbus TCP Server
    try:
        StartTcpServer(context=context, address=(SERVER_HOST, SERVER_PORT))
    except PermissionError:
        print("\n[Error] Menjalankan port 502 memerlukan hak akses Administrator/Root.")
        print("Silakan jalankan script ini dengan Terminal/CMD sebagai Administrator.")