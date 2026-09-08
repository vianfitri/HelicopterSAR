import asyncio
import select
import sys
import threading
import time

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.server import StartAsyncTcpServer

# 1. Inisialisasi Data Block (Address 0, isi 2 boolean [UP, DOWN])
data_block = ModbusSequentialDataBlock(0, [False] * 100)

# 2. Inisialisasi Slave Context & Server Context (Sintaks Standar Pymodbus 3.6.8)
slave_context = ModbusSlaveContext(
    di=data_block,  # Function Code 2 (Discrete Input)
    co=data_block,  # Function Code 1 (Coils)
)
context = ModbusServerContext(slaves=slave_context, single=True)


def update_modbus_status(up_state, down_state):
    """Memperbarui nilai Discrete Inputs dan Coils di Modbus Server."""
    # Mengambil slave context (single=True otomatis memetakan ke slave 0/1)
    slave = context[0]
    
    # setValues(function_code, address, values)
    slave.setValues(2, 0, [up_state, down_state])  # 2 = Discrete Input
    slave.setValues(1, 0, [up_state, down_state])  # 1 = Coils


def keyboard_control_loop():
    """Loop penanganan input keyboard untuk simulasi tombol UP/DOWN."""
    up = False
    down = False

    print("\n" + "=" * 50)
    print("      PLC HAIWELL MODBUS TCP SIMULATOR (v3.6.8)     ")
    print("=" * 50)
    print("Gunakan kontrol keyboard berikut:")
    print("  [ u ] -> Toggle Status UP   (ON/OFF)")
    print("  [ d ] -> Toggle Status DOWN (ON/OFF)")
    print("  [ r ] -> Reset semua ke OFF")
    print("  [ q ] -> Keluar dari simulator")
    print("=" * 50)
    print("Status Saat Ini -> UP: OFF | DOWN: OFF\n")

    is_windows = sys.platform.startswith("win")
    if is_windows:
        import msvcrt

    while True:
        key = None
        if is_windows:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode("utf-8", errors="ignore").lower()
        else:
            dr, _, _ = select.select([sys.stdin], [], [], 0.1)
            if dr:
                key = sys.stdin.read(1).lower()

        if key:
            if key == "u":
                up = not up
                if up:
                    down = False  # Matikan DOWN jika UP aktif
            elif key == "d":
                down = not down
                if down:
                    up = False  # Matikan UP jika DOWN aktif
            elif key == "r":
                up = False
                down = False
            elif key == "q":
                print("\nMenghentikan Simulator...")
                sys.exit(0)

            # Update nilai ke server Modbus
            update_modbus_status(up, down)

            # Cetak status ke konsol
            str_up = "ON " if up else "OFF"
            str_down = "ON " if down else "OFF"
            print(
                f"\rStatus Saat Ini -> UP: {str_up} | DOWN: {str_down}  ",
                end="",
                flush=True,
            )

        time.sleep(0.05)


async def main():
    # Jalankan controller keyboard di background thread
    control_thread = threading.Thread(target=keyboard_control_loop, daemon=True)
    control_thread.start()

    print("Menjalankan Modbus TCP Server pada 0.0.0.0:502 ...")
    
    # Jalankan Async Modbus TCP Server
    await StartAsyncTcpServer(
        context=context,
        address=("0.0.0.0", 502),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except PermissionError:
        print("\n[ERROR] Port 502 membutuhkan hak akses Administrator/Root.")
        print("Silakan run terminal sebagai Administrator, atau ganti port ke 5020.")
    except Exception as e:
        print(f"\n[ERROR] Server berhenti: {e}")