import random
import threading
import time
import keyboard
from pymodbus.datastore import (
    ModbusServerContext,
    ModbusSequentialDataBlock,
    ModbusSlaveContext,
)
from pymodbus.server import StartTcpServer

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 502

# Inisialisasi Data Block Modbus NC: Default True (Idle)
coils = ModbusSequentialDataBlock(0, [True] * 200)
discrete_inputs = ModbusSequentialDataBlock(0, [True] * 200)
holding_registers = ModbusSequentialDataBlock(0, [0] * 200)

slave_store = ModbusSlaveContext(
    di=discrete_inputs,    # FC 2 (Discrete Inputs / X)
    co=coils,              # FC 1 (Coils / Y)
    hr=holding_registers,  # FC 3 (Holding Registers / V)
    zero_mode=True
)

context = ModbusServerContext(slaves=slave_store, single=True)


def get_interlocked_y8_y9_nc():
    """
    Simulasi Y8 & Y9 untuk kontak Normally Closed (NC).
    Kondisi idle / tidak aktif = True (HIGH).
    Kondisi aktif = False (LOW).
    """
    choice = random.choice(["IDLE", "Y8_ACTIVE", "Y9_ACTIVE"])
    if choice == "Y8_ACTIVE":
        return False, True   # Y8 Aktif (False), Y9 Idle (True)
    elif choice == "Y9_ACTIVE":
        return True, False   # Y8 Idle (True), Y9 Aktif (False)
    else:
        return True, True    # Kedua Lampu Idle (True)


def check_keyboard_hoist_control_nc():
    """
    KONTROL KEYBOARD NC:
    Secara default (tombol dilepas) -> Sinyal Modbus = True (Idle / Visual OFF)
    Saat tombol ditekan -> Sinyal Modbus = False (Aktif / Visual ON)
    """
    up_pressed = keyboard.is_pressed('w') or keyboard.is_pressed('up')
    down_pressed = keyboard.is_pressed('s') or keyboard.is_pressed('down')

    if up_pressed and not down_pressed:
        return False, True   # Y10 Aktif (False), Y11 Idle (True)
    elif down_pressed and not up_pressed:
        return True, False   # Y10 Idle (True), Y11 Aktif (False)
    else:
        return True, True    # Keduanya Idle / Lepas Tombol (True)


def simulate_plc_data():
    print("[Simulator NC] Simulasi data PLC (Normally Closed) berjalan...")

    rpm = 1200
    speed2 = 50
    hoist_load = 450

    while True:
        try:
            # 1. Update Discrete Inputs X7 - X10 (NC logic)
            # True = Idle (Visual OFF), False = Terpicu (Visual ON)
            x_values = [
                random.choice([True, False]),  # X7 (FRWD1)
                random.choice([True, False]),  # X8 (FRWD2)
                random.choice([True, False]),  # X9 (RVRS1)
                random.choice([True, False]),  # X10 (RVRS2)
            ]
            slave_store.setValues(2, 7, x_values)

            # 2. Update Y8 & Y9 (NC)
            y8_state, y9_state = get_interlocked_y8_y9_nc()

            # 3. Update Y10 & Y11 (NC dari Keyboard)
            y10_state, y11_state = check_keyboard_hoist_control_nc()

            # Tulis Y8, Y9, Y10, Y11 ke Modbus Data Store (FC 1, Offset 8)
            y_values = [y8_state, y9_state, y10_state, y11_state]
            slave_store.setValues(1, 8, y_values)

            # 4. Update Holding Registers V32, V34, V102
            rpm = max(800, min(1800, rpm + random.randint(-20, 20)))
            speed2 = max(10, min(100, speed2 + random.randint(-2, 2)))
            hoist_load = max(100, min(1000, hoist_load + random.randint(-10, 10)))

            slave_store.setValues(3, 32, [rpm])
            slave_store.setValues(3, 34, [speed2])
            slave_store.setValues(3, 102, [hoist_load])

            time.sleep(0.1)

        except Exception as e:
            print(f"[Simulator Error] {e}")
            break


if __name__ == "__main__":
    sim_thread = threading.Thread(target=simulate_plc_data, daemon=True)
    sim_thread.start()

    print("==========================================================")
    print("  Modbus TCP Server Simulator PLC (Normally Closed Mode)  ")
    print(f"  Host: {SERVER_HOST} | Port: {SERVER_PORT}               ")
    print("==========================================================")

    try:
        StartTcpServer(context=context, address=(SERVER_HOST, SERVER_PORT))
    except PermissionError:
        print("\n[Error] Jalankan sebagai Administrator/Root.")