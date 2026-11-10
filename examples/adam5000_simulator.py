import sys
import asyncio
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGroupBox, QGridLayout, QLabel, QLineEdit, QTextEdit
)
from PySide6.QtCore import Signal, QObject, Qt, QThread

from pymodbus.server.async_io import StartAsyncTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock

# Helper konversi String ASCII -> Register uint16 (Big-Endian per Word)
def ascii_to_adam_registers(ascii_str):
    if not ascii_str.endswith('\r'):
        ascii_str += '\r'

    if len(ascii_str) % 2 != 0:
        ascii_str += '\x00'

    registers = []
    for i in range(0, len(ascii_str), 2):
        high_byte = ord(ascii_str[i])
        low_byte = ord(ascii_str[i+1])
        val = (high_byte << 8) | low_byte
        registers.append(val)
        
    return registers


# Helper konversi Register uint16 -> String ASCII
def adam_registers_to_ascii(registers):
    ascii_chars = []
    for val in registers:
        high_byte = (val >> 8) & 0xFF
        low_byte = val & 0xFF
        if high_byte != 0:
            ascii_chars.append(chr(high_byte))
        if low_byte != 0:
            ascii_chars.append(chr(low_byte))
    return "".join(ascii_chars)


# --- Custom DataBlock ADAM Protocol Emulator ---
class SafeDataBlock(ModbusSequentialDataBlock):
    def __init__(self, name, default_val=0, update_callback=None):
        super().__init__(0, [default_val] * 65536)
        self.name = name
        self.update_callback = update_callback

    def getValues(self, address, count=1):
        values = super().getValues(address, count)
        if address >= 9900 and self.name == "HR":
            signals.log_event.emit(
                f"[READ ASCII Mailbox] Address: {address} | Count: {count} | Data: {values[:count]}"
            )
        return values

    def setValues(self, address, values):
        super().setValues(address, values)
        
        if address >= 9900 and self.name == "HR":
            # 1. Ambil string ASCII murni dari register
            raw_str = adam_registers_to_ascii(values)
            
            # 2. Cari karakter awal command '$' atau '~'
            cmd_start = -1
            if '$' in raw_str:
                cmd_start = raw_str.find('$')
            elif '~' in raw_str:
                cmd_start = raw_str.find('~')

            if cmd_start != -1:
                cmd_str = raw_str[cmd_start:].strip('\r\n\x00')
            else:
                cmd_str = raw_str.strip('\r\n\x00')

            signals.log_event.emit(f"[ASCII CMD RECEIVED] -> '{cmd_str}'")

            response_str = "!01"

            # 3. Ekstrak nomor slot (contoh: $01S4C0B -> slot 4)
            slot = None
            if "S" in cmd_str:
                s_idx = cmd_str.find("S")
                if s_idx + 1 < len(cmd_str) and cmd_str[s_idx + 1].isdigit():
                    slot = int(cmd_str[s_idx + 1])

            # 4. Tentukan Balasan ASCII Spesifik per Slot
            if "C" in cmd_str and cmd_str.endswith("B"):
                if slot in (0, 1, 2):
                    response_str = "!0130"   # ADAM-5024 (AO 4-20mA)
                elif slot == 4:
                    response_str = "!0107"   # ADAM-5017 (AI 4-20mA)
                elif slot == 6:
                    response_str = "!010E"   # ADAM-5018 (TC Type K)
                else:
                    response_str = "!010C"

            elif cmd_str.endswith("M"):
                if slot == 3:
                    response_str = "!01FFFF" # ADAM-5056 (16-Ch DO)
                elif slot == 5:
                    response_str = "!010F"   # ADAM-5080 (4-Ch Counter)
                else:
                    response_str = "!01FF"

            elif cmd_str.endswith("B") or cmd_str.endswith("F"):
                response_str = "!0100"

            # 5. Tulis balasan ke mailbox (offset address) + padding null byte
            resp_regs = ascii_to_adam_registers(response_str)
            
            for offset in range(16):
                self.values[address + offset] = 0

            for idx, val in enumerate(resp_regs):
                self.values[address + idx] = val

            signals.log_event.emit(
                f"[ASCII RESP PREPARED] Slot {slot} -> '{response_str}' (Regs: {resp_regs})"
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
        self.loop = None

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        hr_block = SafeDataBlock("HR", default_val=0, update_callback=self._on_hr_write)
        ir_block = SafeDataBlock("IR", default_val=0, update_callback=self._on_ir_write)
        co_block = SafeDataBlock("CO", default_val=False, update_callback=self._on_co_write)
        di_block = SafeDataBlock("DI", default_val=False)

        slave_store = ModbusSlaveContext(
            hr=hr_block,
            ir=ir_block,
            co=co_block,
            di=di_block,
            zero_mode=True
        )

        self.context = ModbusServerContext(slaves=slave_store, single=True)

        signals.log_event.emit(f"Server Modbus TCP aktif di {self.host}:{self.port}")
        
        try:
            self.loop.run_until_complete(
                StartAsyncTcpServer(
                    context=self.context,
                    address=(self.host, self.port)
                )
            )
        except Exception as e:
            signals.log_event.emit(f"Error Server: {e}")

    def _on_hr_write(self, address, values):
        offset = address - 1 if address > 0 else 0
        for idx, val in enumerate(values):
            curr_offset = offset + idx
            slot = curr_offset // 16
            chan = curr_offset % 16

            if slot in (0, 1, 2) and chan < 4:
                signals.ao_updated.emit(slot, chan, val)

    def _on_ir_write(self, address, values):
        offset = address - 1 if address > 0 else 0
        for idx, val in enumerate(values):
            curr_offset = offset + idx
            slot = curr_offset // 16
            chan = curr_offset % 16

            if slot == 4 and chan < 8:
                signals.ai_updated.emit(slot, chan, val)
            elif slot == 5 and chan < 4:
                signals.counter_updated.emit(slot, chan, val)
            elif slot == 6 and chan < 7:
                signals.tc_updated.emit(slot, chan, val)

    def _on_co_write(self, address, values):
        offset = address - 1 if address > 0 else 0
        for idx, val in enumerate(values):
            curr_offset = offset + idx
            slot = curr_offset // 16
            chan = curr_offset % 16

            if slot == 3 and chan < 16:
                signals.do_updated.emit(slot, chan, bool(val))


# --- PySide6 GUI ---
class ADAM5000GUI(QMainWindow):
    def __init__(self, server_thread):
        super().__init__()
        self.server_thread = server_thread
        self.setWindowTitle("Advantech ADAM-5000/TCP Simulator (Slot 0 - 6)")
        self.resize(1200, 800)
        
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

        row1_layout = QHBoxLayout()

        for slot in range(3):
            grp = QGroupBox(f"Slot {slot}: ADAM-5024 (AO)")
            grid = QGridLayout(grp)
            
            grid.addWidget(QLabel("<b>Ch</b>"), 0, 0)
            grid.addWidget(QLabel("<b>Raw</b>"), 0, 1)
            grid.addWidget(QLabel("<b>%</b>"), 0, 2)
            grid.addWidget(QLabel("<b>mA</b>"), 0, 3)

            self.ao_widgets[slot] = []
            for ch in range(4):
                lbl_ch = QLabel(f"{ch}:")
                txt_raw = QLineEdit("0")
                txt_pct = QLineEdit("0.0%")
                txt_ma = QLineEdit("4.00 mA")

                for txt in (txt_raw, txt_pct, txt_ma):
                    txt.setReadOnly(True)
                    txt.setAlignment(Qt.AlignmentFlag.AlignCenter)

                grid.addWidget(lbl_ch, ch + 1, 0)
                grid.addWidget(txt_raw, ch + 1, 1)
                grid.addWidget(txt_pct, ch + 1, 2)
                grid.addWidget(txt_ma, ch + 1, 3)
                
                self.ao_widgets[slot].append({
                    "raw": txt_raw, "pct": txt_pct, "ma": txt_ma
                })
            row1_layout.addWidget(grp, stretch=2)

        grp_do = QGroupBox("Slot 3: ADAM-5056 (DO)")
        grid_do = QGridLayout(grp_do)
        self.do_labels[3] = []
        for ch in range(16):
            row = ch % 8
            col_offset = (ch // 8) * 2
            grid_do.addWidget(QLabel(f"Ch {ch}:"), row, col_offset)
            lbl = QLabel("OFF")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("background-color: #444; color: white; font-weight: bold; border-radius: 3px;")
            grid_do.addWidget(lbl, row, col_offset + 1)
            self.do_labels[3].append(lbl)

        row1_layout.addWidget(grp_do, stretch=1)
        layout.addLayout(row1_layout)

        row2_layout = QHBoxLayout()

        grp_ai = QGroupBox("Slot 4: ADAM-5017 (8-Ch AI)")
        grid_ai = QGridLayout(grp_ai)
        grid_ai.addWidget(QLabel("<b>Ch</b>"), 0, 0)
        grid_ai.addWidget(QLabel("<b>Raw (16-bit)</b>"), 0, 1)
        grid_ai.addWidget(QLabel("<b>mA</b>"), 0, 2)

        self.ai_widgets[4] = []
        for ch in range(8):
            lbl_ch = QLabel(f"{ch}:")
            txt_raw = QLineEdit("0")
            txt_ma = QLineEdit("4.00 mA")
            for txt in (txt_raw, txt_ma):
                txt.setReadOnly(True)
                txt.setAlignment(Qt.AlignmentFlag.AlignCenter)

            grid_ai.addWidget(lbl_ch, ch + 1, 0)
            grid_ai.addWidget(txt_raw, ch + 1, 1)
            grid_ai.addWidget(txt_ma, ch + 1, 2)
            self.ai_widgets[4].append({"raw": txt_raw, "ma": txt_ma})
        row2_layout.addWidget(grp_ai, stretch=1)

        grp_cnt = QGroupBox("Slot 5: ADAM-5080 (4-Ch Counter)")
        grid_cnt = QGridLayout(grp_cnt)
        grid_cnt.addWidget(QLabel("<b>Ch</b>"), 0, 0)
        grid_cnt.addWidget(QLabel("<b>Value</b>"), 0, 1)

        self.counter_widgets[5] = []
        for ch in range(4):
            lbl_ch = QLabel(f"Ch {ch}:")
            txt_val = QLineEdit("0")
            txt_val.setReadOnly(True)
            txt_val.setAlignment(Qt.AlignmentFlag.AlignCenter)

            grid_cnt.addWidget(lbl_ch, ch + 1, 0)
            grid_cnt.addWidget(txt_val, ch + 1, 1)
            self.counter_widgets[5].append(txt_val)
        row2_layout.addWidget(grp_cnt, stretch=1)

        grp_tc = QGroupBox("Slot 6: ADAM-5018 (7-Ch TC)")
        grid_tc = QGridLayout(grp_tc)
        grid_tc.addWidget(QLabel("<b>Ch</b>"), 0, 0)
        grid_tc.addWidget(QLabel("<b>Raw</b>"), 0, 1)
        grid_tc.addWidget(QLabel("<b>Suhu (°C)</b>"), 0, 2)

        self.tc_widgets[6] = []
        for ch in range(7):
            lbl_ch = QLabel(f"{ch}:")
            txt_raw = QLineEdit("0")
            txt_temp = QLineEdit("0.0 °C")
            for txt in (txt_raw, txt_temp):
                txt.setReadOnly(True)
                txt.setAlignment(Qt.AlignmentFlag.AlignCenter)

            grid_tc.addWidget(lbl_ch, ch + 1, 0)
            grid_tc.addWidget(txt_raw, ch + 1, 1)
            grid_tc.addWidget(txt_temp, ch + 1, 2)
            self.tc_widgets[6].append({"raw": txt_raw, "temp": txt_temp})
        row2_layout.addWidget(grp_tc, stretch=1)

        layout.addLayout(row2_layout)

        log_grp = QGroupBox("Terminal Output & Event Log")
        log_layout = QVBoxLayout(log_grp)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas, Monospace;")
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_grp)
        self.setCentralWidget(main_widget)

    def _connect_signals(self):
        signals.ao_updated.connect(self.update_ao_ui)
        signals.do_updated.connect(self.update_do_ui)
        signals.ai_updated.connect(self.update_ai_ui)
        signals.counter_updated.connect(self.update_counter_ui)
        signals.tc_updated.connect(self.update_tc_ui)
        signals.log_event.connect(self.append_log)

    def update_ao_ui(self, slot, chan, val):
        if slot in self.ao_widgets and chan < len(self.ao_widgets[slot]):
            widgets = self.ao_widgets[slot][chan]
            val_clamped = max(0, min(val, 4095))
            pct = (val_clamped / 4095.0) * 100.0
            ma = 4.0 + (val_clamped / 4095.0) * 16.0

            widgets["raw"].setText(str(val))
            widgets["pct"].setText(f"{pct:.1f}%")
            widgets["ma"].setText(f"{ma:.2f} mA")

    def update_do_ui(self, slot, chan, state):
        if slot in self.do_labels and chan < len(self.do_labels[slot]):
            lbl = self.do_labels[slot][chan]
            if state:
                lbl.setText("ON")
                lbl.setStyleSheet("background-color: #00aa00; color: white; font-weight: bold; border-radius: 3px;")
            else:
                lbl.setText("OFF")
                lbl.setStyleSheet("background-color: #444; color: white; font-weight: bold; border-radius: 3px;")

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