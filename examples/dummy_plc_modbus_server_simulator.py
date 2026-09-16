import random
import threading
import time
from pymodbus.datastore import (
    ModbusServerContext,
    ModbusSequentialDataBlock,
    ModbusSlaveContext,
)
from pymodbus.server import StartTcpServer

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 502

# Inisialisasi Data Block Modbus
coils = ModbusSequentialDataBlock(0, [False] * 200)
discrete_inputs = ModbusSequentialDataBlock(0, [False] * 200)
holding_registers = ModbusSequentialDataBlock(0, [0] * 200)

# Masukkan ke Slave Context
slave_store = ModbusSlaveContext(
    di=discrete_inputs,    # FC 2 / Discrete Inputs (X)
    co=coils,              # FC 1 / Coils (Y)
    hr=holding_registers,  # FC 3 / Holding Registers (V)
    zero_mode=True
)

context = ModbusServerContext(slaves=slave_store, single=True)


def simulate_plc_data():
    """Thread untuk mensimulasikan perubahan data PLC."""
    print("[Simulator] Simulasi data PLC berjalan...")

    rpm = 1200
    speed2 = 50
    hoist_load = 450

    while True:
        try:
            # 1. Update Discrete Inputs X7 - X10 (FC 2)
            x_values = [
                random.choice([True, False]),  # X7 (FRWD1)
                random.choice([True, False]),  # X8 (FRWD2)
                random.choice([True, False]),  # X9 (RVRS1)
                random.choice([True, False]),  # X10 (RVRS2)
            ]
            # Di pymodbus 3.6.8 gunakan fc=2
            slave_store.setValues(fc=2, address=7, values=x_values)

            # 2. Update Output Lampu Y8 - Y11 (FC 1)
            y_values = [
                random.choice([True, False]),  # Y8 (FRWD Lamp)
                random.choice([True, False]),  # Y9 (RVRS Lamp)
                random.choice([True, False]),  # Y10 (Hoist Up Lamp)
                random.choice([True, False]),  # Y11 (Hoist Down Lamp)
            ]
            slave_store.setValues(fc=1, address=8, values=y_values)

            # 3. Update Register V32, V34, V102 (FC 3)
            rpm = max(800, min(1800, rpm + random.randint(-50, 50)))
            speed2 = max(10, min(100, speed2 + random.randint(-5, 5)))
            hoist_load = max(
                100, min(1000, hoist_load + random.randint(-20, 20))
            )

            slave_store.setValues(fc=3, address=32, values=[rpm])         # V32 (RPM)
            slave_store.setValues(fc=3, address=34, values=[speed2])      # V34 (SPEED2)
            slave_store.setValues(fc=3, address=102, values=[hoist_load]) # V102 (Hoist Load)

            time.sleep(1)

        except Exception as e:
            print(f"[Simulator Error] {e}")
            break


if __name__ == "__main__":
    sim_thread = threading.Thread(target=simulate_plc_data, daemon=True)
    sim_thread.start()

    print("==================================================")
    print(" Modbus TCP Server Simulator PLC Haiwell Running  ")
    print(f" Host: {SERVER_HOST} | Port: {SERVER_PORT}       ")
    print(" Tekan Ctrl+C untuk menghentikan server           ")
    print("==================================================")

    try:
        StartTcpServer(context=context, address=(SERVER_HOST, SERVER_PORT))
    except PermissionError:
        print(
            "\n[Error] Menjalankan port 502 memerlukan hak akses Administrator/Root."
        )
        print(
            "Silakan jalankan script ini dengan Terminal/CMD sebagai Administrator."
        )