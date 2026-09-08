import asyncio
import select
import sys
import threading
import time

# Impor Pymodbus v3.8+ yang valid
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext
from pymodbus.server import StartAsyncTcpServer

# Setup Data Store untuk Discrete Input (di) dan Coils (co)
# Inisialisasi address 0 dan 1 dengan nilai False
data_block = ModbusSequentialDataBlock(1, [False, False])

# Pada Pymodbus 3.8+, ModbusServerContext dapat langsung menerima data block
# di=Discrete Inputs, co=Coils
context = ModbusServerContext(
    slaves={
        1: ModbusServerContext(
            di=data_block,
            co=data_block,
        )
    },
    single=True,
)


def update_modbus_status(up_state, down_state):
    """Memperbarui nilai Discrete Inputs dan Coils di Modbus Server."""
    # Memperbarui Discrete Inputs (Address 0 & 1)
    context[1].setValues(2, 1, [up_state, down_state])  # 2 = Discrete Input
    # Memperbarui Coils (Address 0 & 1)
    context[1].setValues(1, 1, [up_state, down_state])  # 1 = Coils


def keyboard_control_loop():
    """Loop untuk membaca input keyboard tanpa memblokir Modbus Server."""
    up = False
    down = False

    print("\n" + "=" * 50)
    print("      PLC HAIWELL MODBUS TCP SIMULATOR (Pymodbus 3.x)      ")
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

            # Update status ke server Modbus
            update_modbus_status(up, down)

            # Tampilkan status terbaru di konsol
            str_up = "ON " if up else "OFF"
            str_down = "ON " if down else "OFF"
            print(
                f"\rStatus Saat Ini -> UP: {str_up} | DOWN: {str_down}  ",
                end="",
                flush=True,
            )

        time.sleep(0.05)


async def main():
    # Jalankan Keyboard Controller di thread terpisah
    control_thread = threading.Thread(target=keyboard_control_loop, daemon=True)
    control_thread.start()

    print("Menjalankan Modbus TCP Server pada 0.0.0.0:502 ...")
    
    # Jalankan Modbus Async TCP Server tanpa memerlukan parameter identity
    await StartAsyncTcpServer(
        context=context,
        address=("0.0.0.0", 502),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except PermissionError:
        print("\n[ERROR] Port 502 membutuhkan hak akses Administrator/Root.")
        print(
            "Silakan jalankan terminal sebagai Administrator, atau gunakan port 5020."
        )
    except Exception as e:
        print(f"\n[ERROR] Server berhenti: {e}")