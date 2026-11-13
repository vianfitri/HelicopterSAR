import sys
import asyncio
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGroupBox, QGridLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QSpinBox
)
from PySide6.QtCore import Signal, QObject, Qt, QThread, QTimer

from pymodbus.server.async_io import StartAsyncTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock


# Helper konversi ASCII <-> Register
def ascii_to_adam_registers(ascii_str):
    if not ascii_str.endswith('\r'):
        ascii_str += '\r'
    if len(ascii_str) % 2 != 0:
        ascii_str += '\x00'
    registers = []
    for i in range(0, len(ascii_str), 2):
        val = (ord(ascii_str[i]) << 8) | ord(ascii_str[i+1])
        registers.append(val)
    return registers


def adam_registers_to_ascii(registers):
    ascii_chars = []
    for val in registers:
        hb, lb = (val >> 8) & 0xFF, val & 0xFF
        if hb != 0: ascii_chars.append(chr(hb))
        if lb != 0: ascii_chars.append(chr(lb))
    return "".join(ascii_chars)

class SafeDataBlock(ModbusSequentialDataBlock):
    def __init__(self, name, default_val=0, update_callback=None):
        super().__init__(0, [default_val] * 65536)
        self.name = name
        self.update_callback = update_callback

    def getValues(self, address, count=1):
        values = super().getValues(address, count)
        if address >= 9000 and self.name == "HR":
            ascii_out = adam_registers_to_ascii(values)
            signals.log_event.emit(
                f"[READ {self.name}] Addr: {address} | Cnt: {count} | ASCII: '{ascii_out.strip()}' | Raw: {[hex(v) for v in values]}"
            )
        return values

    def setValues(self, address, values):
        super().setValues(address, values)
        
        if address >= 9900 and self.name == "HR":
            raw_str = adam_registers_to_ascii(values)
            signals.log_event.emit(f"[WRITE Mailbox] Addr: {address} | Raw Regs: {values} | ASCII: '{raw_str.strip()}'")

            # Cari awalan command '$', '~', atau '#'
            cmd_start = -1
            for prefix in ('$', '~', '#'):
                if prefix in raw_str:
                    cmd_start = raw_str.find(prefix)
                    break

            cmd_str = raw_str[cmd_start:].strip('\r\n\x00') if cmd_start != -1 else raw_str.strip('\r\n\x00')
            
            if not cmd_str:
                return

            signals.log_event.emit(f"[ASCII CMD PARSED] -> '{cmd_str}'")

            # =========================================================
            # 1. PENANGANAN SET ANALOG OUTPUT ADAM-5024 (#01S0C2+20.000)
            # =========================================================
            if cmd_str.startswith("#") and "S" in cmd_str and "C" in cmd_str:
                try:
                    s_idx = cmd_str.find("S")
                    c_idx = cmd_str.find("C")
                    slot = int(cmd_str[s_idx + 1 : c_idx])
                    chan = int(cmd_str[c_idx + 1])
                    
                    # Ambil nilai arus (mA) dari sisa string (misal '+20.000')
                    ao_ma = float(cmd_str[c_idx + 2 :])

                    # Konversi 4.0 - 20.0 mA ke Raw 12-bit (0 - 4095)
                    ma_clamped = max(4.0, min(ao_ma, 20.0))
                    raw_val = int(round(((ma_clamped - 4.0) / 16.0) * 4095.0))

                    # Update GUI & Datastore register AO
                    signals.ao_updated.emit(slot, chan, raw_val)
                    reg_addr = (slot * 8) + chan + 1
                    self.values[reg_addr] = raw_val

                    signals.log_event.emit(
                        f"[ADAM-5024 SET] Slot {slot} Ch {chan} -> {ao_ma:.2f} mA (Raw: {raw_val})"
                    )
                    response_str = ">"  # Balasan wajib Advantech jika perintah '#' sukses
                except Exception as e:
                    signals.log_event.emit(f"[ERROR Parse # CMD] '{cmd_str}' -> {e}")
                    response_str = "?01"

            # =========================================================
            # 2. PENANGANAN KONFIGURASI RANGE & STATUS ($ / ~)
            # =========================================================
            else:
                response_str = "!01"
                slot = None
                if "S" in cmd_str:
                    s_idx = cmd_str.find("S")
                    if s_idx + 1 < len(cmd_str) and cmd_str[s_idx + 1].isdigit():
                        slot = int(cmd_str[s_idx + 1])

                if cmd_str == "$01M":
                    response_str = "!0115000"     # Identitas Main Unit ADAM-5000/TCP
                elif cmd_str in ("$01S", "$01T"): # Peta 8 Slot untuk GetSlotInfo ($01T)
                    response_str = "!0124242456178018FF"  
                elif "S" in cmd_str and cmd_str.endswith("6") and "C" not in cmd_str:
                    response_str = "!01FF"        # Channel Enable Mask: FF = semua 8 channel aktif (True)
                elif "C" in cmd_str and cmd_str.endswith("B"):
                    if slot in (0, 1, 2):
                        response_str = "!013100"   # 0x31 = 49 Desimal (mA_4To20 ADAM-5024)
                    elif slot == 4:
                        response_str = "!010A00"   # 0x0A = 10 Desimal (mA_4To20 ADAM-5017)
                    elif slot == 6:
                        response_str = "!010E00"   # 0x0E = 14 Desimal (TC Type K ADAM-5018)
                    else:
                        response_str = "!010C00"
                elif cmd_str.endswith("B") and "C" not in cmd_str:
                    # Balasan Read Module Configuration ($01S4B / $01S6B) -> Range + Integration + DataFormat
                    if slot == 4:
                        response_str = "!010000"           # Byte ke-3 = 00 (Engineering Units)
                    elif slot == 6:
                        response_str = "!010000"           # Byte ke-3 = 00 (Engineering Units)
                    else:
                        response_str = "!010000"
                elif cmd_str.endswith("M"):
                    if slot in (0, 1, 2):
                        response_str = "!0124"   # ADAM-5024
                    elif slot == 3:
                        response_str = "!0156"   # ADAM-5056
                    elif slot == 4:
                        response_str = "!0117"   # ADAM-5017
                    elif slot == 5:
                        response_str = "!0180"   # ADAM-5080
                    elif slot == 6:
                        response_str = "!0118"   # ADAM-5018
                    else:
                        response_str = "!01FF"
                elif cmd_str.endswith("B") or cmd_str.endswith("F"):
                    response_str = "!0100"

            # =========================================================
            # 3. TULIS BALASAN BERSIH TEPAT DI `address` (9999)
            # =========================================================
            resp_regs = ascii_to_adam_registers(response_str)

            # Bersihkan 50 register mulai dari address (9999 s/d 10048) agar sisa karakter lama hilang
            for offset in range(50):
                self.values[address + offset] = 0

            # Tulis balasan HANYA tepat di address (9999), TANPA loop offset 9998/10000
            for idx, val in enumerate(resp_regs):
                self.values[address + idx] = val

            signals.log_event.emit(
                f"[ASCII RESP READY] Addr {address} -> '{response_str}' | Regs: {[hex(r) for r in resp_regs]}"
            )

        if self.update_callback:
            self.update_callback(address, values)

class SimulatorSignals(QObject):
    ao_updated = Signal(int, int, int)
    do_updated = Signal(int, int, bool)
    ai_updated = Signal(int, int, int)
    counter_updated = Signal(int, int, int)
    tc_updated = Signal(int, int, int)
    log_event = Signal(str)

signals = SimulatorSignals()


# --- Modbus Server Thread ---
class ModbusServerThread(QThread):
    def __init__(self, host="0.0.0.0", port=502):
        super().__init__()
        self.host = host
        self.port = port

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        hr_block = SafeDataBlock("HR", default_val=0, update_callback=self._on_hr_write)
        ir_block = SafeDataBlock("IR", default_val=0, update_callback=self._on_ir_write)
        co_block = SafeDataBlock("CO", default_val=False, update_callback=self._on_co_write)
        di_block = SafeDataBlock("DI", default_val=False)

        slave_store = ModbusSlaveContext(
            hr=hr_block, ir=ir_block, co=co_block, di=di_block, zero_mode=True
        )
        self.context = ModbusServerContext(slaves=slave_store, single=True)

        signals.log_event.emit(f"Server Modbus TCP aktif di {self.host}:{self.port}")
        
        try:
            self.loop.run_until_complete(
                StartAsyncTcpServer(context=self.context, address=(self.host, self.port))
            )
        except Exception as e:
            signals.log_event.emit(f"Error Server: {e}")

    # Fungsi penulisan langsung ke DataStore dari Server GUI
    def update_server_datastore(self, register_type, address, value_or_values):
        if not hasattr(self, 'context'):
            return
        
        # 3 = Holding Register (HR), 4 = Input Register (IR), 1 = Coils (CO)
        fx_code = 3 if register_type == "HR" else (4 if register_type == "IR" else 1)
        values = value_or_values if isinstance(value_or_values, list) else [value_or_values]
        
        self.context[0].setValues(fx_code, address, values)

    def _on_hr_write(self, address, values):
        offset = address - 1 if address > 0 else 0
        for idx, val in enumerate(values):
            curr_offset = offset + idx
            slot = curr_offset // 8
            chan_offset = curr_offset % 8

            if slot in (0, 1, 2) and chan_offset < 4:
                signals.ao_updated.emit(slot, chan_offset, val)
            elif slot == 4 and chan_offset < 8:
                signals.ai_updated.emit(slot, chan_offset, val)
            elif slot == 5 and chan_offset < 8:
                chan = chan_offset // 2
                reg_base = (5 * 8) + (chan * 2) + 1
                low_val = self.context[0].getValues(3, reg_base, count=1)[0]
                high_val = self.context[0].getValues(3, reg_base + 1, count=1)[0]
                val_32bit = (high_val << 16) | low_val
                signals.counter_updated.emit(slot, chan, val_32bit)
            elif slot == 6 and chan_offset < 7:
                signals.tc_updated.emit(slot, chan_offset, val)

    def _on_ir_write(self, address, values):
        self._on_hr_write(address, values)

    def _on_co_write(self, address, values):
        offset = address - 1 if address > 0 else 0
        for idx, val in enumerate(values):
            curr_offset = offset + idx
            slot, chan = curr_offset // 16, curr_offset % 16
            if slot == 3 and chan < 16:
                signals.do_updated.emit(slot, chan, bool(val))


# --- PySide6 GUI ---
class ADAM5000GUI(QMainWindow):
    def __init__(self, server_thread):
        super().__init__()
        self.server_thread = server_thread
        self.setWindowTitle("Advantech ADAM-5000/TCP Server Simulator + Manual Control Panel")
        self.resize(1250, 850)
        
        self.ao_widgets = {}
        self.do_labels = {}
        self.ai_widgets = {}
        self.counter_widgets = {}
        self.tc_widgets = {}

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        # --- PANEL KONTROL INPUT MANUAL SERVER ---
        ctrl_grp = QGroupBox("🎮 Panel Inject Data Manual (Server Side)")
        ctrl_grid = QGridLayout(ctrl_grp)

        # Controls untuk Slot Target & Channel
        ctrl_grid.addWidget(QLabel("<b>Target Modul / Slot:</b>"), 0, 0)
        self.spn_slot = QSpinBox()
        self.spn_slot.setRange(0, 6)
        self.spn_slot.setValue(5) # Default Slot 5 (ADAM-5080 Counter)
        ctrl_grid.addWidget(self.spn_slot, 0, 1)

        ctrl_grid.addWidget(QLabel("<b>Channel:</b>"), 0, 2)
        self.spn_chan = QSpinBox()
        self.spn_chan.setRange(0, 15)
        ctrl_grid.addWidget(self.spn_chan, 0, 3)

        ctrl_grid.addWidget(QLabel("<b>Nilai Input (Raw / 32-bit):</b>"), 0, 4)
        self.spn_val = QSpinBox()
        self.spn_val.setRange(0, 2147483647)
        self.spn_val.setValue(300) # Default nilai 300
        ctrl_grid.addWidget(self.spn_val, 0, 5)

        btn_apply = QPushButton("Inject to Server Datastore")
        btn_apply.setStyleSheet("background-color: #0277bd; color: white; font-weight: bold;")
        btn_apply.clicked.connect(self.inject_manual_value)
        ctrl_grid.addWidget(btn_apply, 0, 6)

        layout.addWidget(ctrl_grp)

        # --- DASHBOARD MONITORING REGISTERS ---
        row1_layout = QHBoxLayout()

        # Slot 0-2 (AO)
        for slot in range(3):
            grp = QGroupBox(f"Slot {slot}: ADAM-5024 (AO)")
            grid = QGridLayout(grp)
            grid.addWidget(QLabel("<b>Ch</b>"), 0, 0)
            grid.addWidget(QLabel("<b>Raw</b>"), 0, 1)
            grid.addWidget(QLabel("<b>mA</b>"), 0, 2)

            self.ao_widgets[slot] = []
            for ch in range(4):
                lbl_ch = QLabel(f"{ch}:")
                txt_raw = QLineEdit("0")
                txt_ma = QLineEdit("4.00 mA")
                for txt in (txt_raw, txt_ma):
                    txt.setReadOnly(True)
                    txt.setAlignment(Qt.AlignmentFlag.AlignCenter)

                grid.addWidget(lbl_ch, ch + 1, 0)
                grid.addWidget(txt_raw, ch + 1, 1)
                grid.addWidget(txt_ma, ch + 1, 2)
                self.ao_widgets[slot].append({"raw": txt_raw, "ma": txt_ma})
            row1_layout.addWidget(grp, stretch=2)

        # Slot 3 (DO)
        grp_do = QGroupBox("Slot 3: ADAM-5056 (DO)")
        grid_do = QGridLayout(grp_do)
        self.do_labels[3] = []
        for ch in range(16):
            row, col_offset = ch % 8, (ch // 8) * 2
            grid_do.addWidget(QLabel(f"Ch {ch}:"), row, col_offset)
            lbl = QLabel("OFF")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("background-color: #444; color: white; font-weight: bold; border-radius: 3px;")
            grid_do.addWidget(lbl, row, col_offset + 1)
            self.do_labels[3].append(lbl)
        row1_layout.addWidget(grp_do, stretch=1)
        layout.addLayout(row1_layout)

        # Slot 4 (AI), Slot 5 (Counter), Slot 6 (TC)
        row2_layout = QHBoxLayout()

        # Slot 4 (AI)
        grp_ai = QGroupBox("Slot 4: ADAM-5017 (8-Ch AI)")
        grid_ai = QGridLayout(grp_ai)
        grid_ai.addWidget(QLabel("<b>Ch</b>"), 0, 0)
        grid_ai.addWidget(QLabel("<b>Raw</b>"), 0, 1)
        grid_ai.addWidget(QLabel("<b>mA</b>"), 0, 2)
        self.ai_widgets[4] = []
        for ch in range(8):
            txt_raw, txt_ma = QLineEdit("0"), QLineEdit("4.00 mA")
            for txt in (txt_raw, txt_ma):
                txt.setReadOnly(True); txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid_ai.addWidget(QLabel(f"{ch}:"), ch + 1, 0)
            grid_ai.addWidget(txt_raw, ch + 1, 1)
            grid_ai.addWidget(txt_ma, ch + 1, 2)
            self.ai_widgets[4].append({"raw": txt_raw, "ma": txt_ma})
        row2_layout.addWidget(grp_ai, stretch=1)

        # Slot 5 (Counter)
        grp_cnt = QGroupBox("Slot 5: ADAM-5080 (4-Ch Counter 32-bit)")
        grid_cnt = QGridLayout(grp_cnt)
        grid_cnt.addWidget(QLabel("<b>Ch</b>"), 0, 0)
        grid_cnt.addWidget(QLabel("<b>32-bit Value</b>"), 0, 1)
        self.counter_widgets[5] = []
        for ch in range(4):
            txt_val = QLineEdit("0")
            txt_val.setReadOnly(True); txt_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid_cnt.addWidget(QLabel(f"Ch {ch}:"), ch + 1, 0)
            grid_cnt.addWidget(txt_val, ch + 1, 1)
            self.counter_widgets[5].append(txt_val)
        row2_layout.addWidget(grp_cnt, stretch=1)

        # Slot 6 (TC)
        grp_tc = QGroupBox("Slot 6: ADAM-5018 (7-Ch TC)")
        grid_tc = QGridLayout(grp_tc)
        grid_tc.addWidget(QLabel("<b>Ch</b>"), 0, 0)
        grid_tc.addWidget(QLabel("<b>Raw</b>"), 0, 1)
        grid_tc.addWidget(QLabel("<b>Suhu (°C)</b>"), 0, 2)
        self.tc_widgets[6] = []
        for ch in range(7):
            txt_raw, txt_temp = QLineEdit("0"), QLineEdit("0.0 °C")
            for txt in (txt_raw, txt_temp):
                txt.setReadOnly(True); txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid_tc.addWidget(QLabel(f"{ch}:"), ch + 1, 0)
            grid_tc.addWidget(txt_raw, ch + 1, 1)
            grid_tc.addWidget(txt_temp, ch + 1, 2)
            self.tc_widgets[6].append({"raw": txt_raw, "temp": txt_temp})
        row2_layout.addWidget(grp_tc, stretch=1)

        layout.addLayout(row2_layout)

        # Event Log Terminal
        log_grp = QGroupBox("Terminal Output & Event Log")
        log_layout = QVBoxLayout(log_grp)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas;")
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_grp)

        self.setCentralWidget(main_widget)

    def inject_manual_value(self):
        """Mengirimkan nilai dari panel manual ke Modbus Datastore."""
        slot = self.spn_slot.value()
        chan = self.spn_chan.value()
        val = self.spn_val.value()

        # 1. Handling ADAM-5080 (Slot 5 - Counter 32-bit)
        if slot == 5:
            if chan >= 4:
                signals.log_event.emit("[ERROR] Slot 5 hanya mendukung Channel 0 - 3!")
                return
            
            # Hitung Register Address Modbus Advantech: iStart = (5 * 8) + (chan * 2) + 1
            address = (5 * 8) + (chan * 2) + 1
            low_word = val & 0xFFFF
            high_word = (val >> 16) & 0xFFFF

            # Update ke tabel Holding Register (HR) & Input Register (IR) sekaligus
            self.server_thread.update_server_datastore("HR", address, [low_word, high_word])
            self.server_thread.update_server_datastore("IR", address, [low_word, high_word])
            
            signals.log_event.emit(
                f"[MANUAL INJECT] ADAM-5080 (Slot 5 Ch {chan}) -> 32-bit Value: {val} (Low Reg {address}: {low_word}, High Reg {address+1}: {high_word})"
            )

        # 2. Handling Slot 0-2 (AO), Slot 4 (AI), Slot 6 (TC) - 16-bit
        elif slot in (0, 1, 2, 4, 6):
            address = (slot * 8) + chan + 1
            val_16bit = min(val, 65535)

            self.server_thread.update_server_datastore("HR", address, val_16bit)
            self.server_thread.update_server_datastore("IR", address, val_16bit)
            
            signals.log_event.emit(
                f"[MANUAL INJECT] Slot {slot} Ch {chan} -> Address {address} Value: {val_16bit}"
            )

        # 3. Handling Slot 3 (DO - Coil)
        elif slot == 3:
            address = (3 * 16) + chan + 1
            state = bool(val)
            self.server_thread.update_server_datastore("CO", address, state)
            signals.log_event.emit(f"[MANUAL INJECT] Slot 3 DO Ch {chan} -> State: {state}")

    def _connect_signals(self):
        signals.ao_updated.connect(self.update_ao_ui)
        signals.do_updated.connect(self.update_do_ui)
        signals.ai_updated.connect(self.update_ai_ui)
        signals.counter_updated.connect(self.update_counter_ui)
        signals.tc_updated.connect(self.update_tc_ui)
        signals.log_event.connect(self.append_log)

    def update_ao_ui(self, slot, chan, val):
        if slot in self.ao_widgets and chan < len(self.ao_widgets[slot]):
            val_clamped = max(0, min(val, 4095))
            ma = 4.0 + (val_clamped / 4095.0) * 16.0
            self.ao_widgets[slot][chan]["raw"].setText(str(val))
            self.ao_widgets[slot][chan]["ma"].setText(f"{ma:.2f} mA")

    def update_do_ui(self, slot, chan, state):
        if slot in self.do_labels and chan < len(self.do_labels[slot]):
            lbl = self.do_labels[slot][chan]
            lbl.setText("ON" if state else "OFF")
            lbl.setStyleSheet(f"background-color: {'#00aa00' if state else '#444'}; color: white; font-weight: bold;")

    def update_ai_ui(self, slot, chan, val):
        if slot in self.ai_widgets and chan < len(self.ai_widgets[slot]):
            val_clamped = max(0, min(val, 65535))
            ma = 4.0 + (val_clamped / 65535.0) * 16.0
            self.ai_widgets[slot][chan]["raw"].setText(str(val))
            self.ai_widgets[slot][chan]["ma"].setText(f"{ma:.2f} mA")

    def update_counter_ui(self, slot, chan, val):
        if slot in self.counter_widgets and chan < len(self.counter_widgets[slot]):
            self.counter_widgets[slot][chan].setText(str(val))

    def update_tc_ui(self, slot, chan, val):
        if slot in self.tc_widgets and chan < len(self.tc_widgets[slot]):
            val_clamped = max(0, min(val, 65535))
            temp = (val_clamped / 65535.0) * 1370.0
            self.tc_widgets[slot][chan]["raw"].setText(str(val))
            self.tc_widgets[slot][chan]["temp"].setText(f"{temp:.1f} °C")

    def append_log(self, text):
        self.log_text.append(text)

    def closeEvent(self, event):
        if self.server_thread.isRunning():
            self.server_thread.terminate()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    server_thread = ModbusServerThread(host="0.0.0.0", port=502)
    server_thread.start()

    gui = ADAM5000GUI(server_thread)
    gui.show()
    sys.exit(app.exec())