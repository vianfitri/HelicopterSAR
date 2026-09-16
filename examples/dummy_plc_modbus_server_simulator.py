import random
import threading
import time
import keyboard  # Mengontrol keyboard langsung dari Server
from pymodbus.datastore import (
    ModbusServerContext,
    ModbusSequentialDataBlock,
    ModbusSlaveContext,
)
from pymodbus.server import StartTcpServer

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 502

# Inisialisasi Data Block Modbus (200 register)
coils = ModbusSequentialDataBlock(0, [False] * 200)
discrete_inputs = ModbusSequentialDataBlock(0, [False] * 200)
holding_registers = ModbusSequentialDataBlock(0, [0] * 200)

# Masukkan ke Slave Context
slave_store = ModbusSlaveContext(
    di=discrete_inputs,    # FC 2 (Discrete Inputs / X)
    co=coils,              # FC 1 (Coils / Y)
    hr=holding_registers,  # FC 3 (Holding Registers / V)
    zero_mode=True
)

context = ModbusServerContext(slaves=slave_store, single=True)


def get_interlocked_y8_y9():
    """Simulasi acak Y8 (FRWD Lamp) & Y9 (RVRS Lamp) dengan interlock."""
    choice = random.choice(["OFF_OFF", "Y8_ON", "Y9_ON"])
    if choice == "Y8_ON":
        return True, False
    elif choice == "Y9_ON":
        return False, True
    else:
        return False, False


def check_keyboard_hoist_control():
    """
    Membaca tombol keyboard server dan mengembalikan nilai Y10 (Hoist Up) & Y11 (Hoist Down)
    dengan aturan Interlock (TIDAK BISA ON BERSAMAAN).
    """
    up_pressed = keyboard.is_pressed('w') or keyboard.is_pressed('up')
    down_pressed = keyboard.is_pressed('s') or keyboard.is_pressed('down')

    # Logika Interlock:
    # Jika Panah Atas/W ditekan -> Y10 = True, Y11 = False
    # Jika Panah Bawah/S ditekan -> Y10 = False, Y11 = True
    # Jika keduanya ditekan atau tidak ditekan -> Y10 = False, Y11 = False
    if up_pressed and not down_pressed:
        return True, False
    elif down_pressed and not up_pressed:
        return False, True
    else:
        return False, False


def simulate_plc_data():
    """Thread simulator data PLC di Server."""
    print("[Simulator] Simulasi data PLC & Listener Keyboard berjalan...")

    rpm = 1200
    speed2 = 50
    hoist_load = 450

    while True:
        try:
            # 1. Update Discrete Inputs X7 - X10 (FC 2 / Discrete Inputs) secara acak
            x_values = [
                random.choice([True, False]),  # X7 (FRWD1)
                random.choice([True, False]),  # X8 (FRWD2)
                random.choice([True, False]),  # X9 (RVRS1)
                random.choice([True, False]),  # X10 (RVRS2)
            ]
            slave_store.setValues(2, 7, x_values)

            # 2. Update Y8 & Y9 secara acak (dengan interlock)
            y8_state, y9_state = get_interlocked_y8_y9()

            # 3. Update Y10 & Y11 dari KONTROL KEYBOARD SERVER (dengan interlock)
            y10_state, y11_state = check_keyboard_hoist_control()

            # Tulis Y8, Y9, Y10, Y11 ke Modbus Data Store (FC 1, Offset 8)
            y_values = [y8_state, y9_state, y10_state, y11_state]
            slave_store.setValues(1, 8, y_values)

            # 4. Update Register V32, V34, V102 (FC 3 / Holding Registers)
            rpm = max(800, min(1800, rpm + random.randint(-20, 20)))
            speed2 = max(10, min(100, speed2 + random.randint(-2, 2)))
            hoist_load = max(100, min(1000, hoist_load + random.randint(-10, 10)))

            slave_store.setValues(3, 32, [rpm])         # V32 (RPM)
            slave_store.setValues(3, 34, [speed2])      # V34 (SPEED2)
            slave_store.setValues(3, 102, [hoist_load]) # V102 (Hoist Load)

            time.sleep(0.1) # Responsivitas keyboard cepat (100ms)

        except Exception as e:
            print(f"[Simulator Error] {e}")
            break


if __name__ == "__main__":
    # Jalankan background thread untuk simulasi & keyboard reader
    sim_thread = threading.Thread(target=simulate_plc_data, daemon=True)
    sim_thread.start()

    print("==========================================================")
    print("  Modbus TCP Server Simulator PLC Haiwell (Keyboard Server)")
    print(f"  Host: {SERVER_HOST} | Port: {SERVER_PORT}               ")
    print("----------------------------------------------------------")
    print("  KONTROL KEYBOARD SERVER:                                ")
    print("   - Tahan 'W' atau 'Panah Atas'  : Y10 (Hoist Up) ON     ")
    print("   - Tahan 'S' atau 'Panah Bawah' : Y11 (Hoist Down) ON   ")
    print("   - Lepas Tombol                 : Y10 & Y11 OFF         ")
    print("==========================================================")

    try:
        StartTcpServer(context=context, address=(SERVER_HOST, SERVER_PORT))
    except PermissionError:
        print("\n[Error] Membaca keyboard & port 502 memerlukan hak akses Administrator/Root.")
        print("Silakan jalankan Command Prompt / Terminal sebagai Administrator.")