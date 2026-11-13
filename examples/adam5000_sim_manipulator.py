import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGroupBox, QGridLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QSpinBox
)
from PySide6.QtCore import Qt, QThread, Signal

from pymodbus.client import ModbusTcpClient


class ModbusWorker(QThread):
    log_signal = Signal(str)
    read_signal = Signal(dict)

    def __init__(self, host="127.0.0.1", port=5020):
        super().__init__()
        self.host = host
        self.port = port
        self.client = None

    def connect_server(self):
        self.client = ModbusTcpClient(self.host, port=self.port)
        if self.client.connect():
            self.log_signal.emit(f"Terhubung ke Modbus Server {self.host}:{self.port}")
            return True
        else:
            self.log_signal.emit(f"Gagal terhubung ke {self.host}:{self.port}")
            return False

    def write_holding_register(self, address, value):
        if self.client and self.client.connected:
            res = self.client.write_register(address=address, value=value, slave=1)
            if not res.isError():
                self.log_signal.emit(f"[SUCCESS] Write HR Address {address} -> Value: {value}")
            else:
                self.log_signal.emit(f"[ERROR] Write HR Address {address} gagal")
        else:
            self.log_signal.emit("[ERROR] Client belum terhubung!")

    def write_coil(self, address, state):
        if self.client and self.client.connected:
            res = self.client.write_coil(address=address, value=state, slave=1)
            if not res.isError():
                self.log_signal.emit(f"[SUCCESS] Write Coil Address {address} -> State: {state}")
            else:
                self.log_signal.emit(f"[ERROR] Write Coil Address {address} gagal")
        else:
            self.log_signal.emit("[ERROR] Client belum terhubung!")

    def write_input_register(self, address, value):
        """Menulis ke Input Register server (simulasi inject sensor data)."""
        if self.client and self.client.connected:
            # Pada pymodbus server standard, me-write IR dari client menggunakan custom function/write_register 
            # jika server mengizinkan data block IR diperbarui via holding/register set.
            res = self.client.write_register(address=address, value=value, slave=1)
            if not res.isError():
                self.log_signal.emit(f"[SUCCESS] Update Register Address {address} -> Value: {value}")
            else:
                self.log_signal.emit(f"[ERROR] Update Register Address {address} gagal")
        else:
            self.log_signal.emit("[ERROR] Client belum terhubung!")

    def disconnect_server(self):
        if self.client:
            self.client.close()
            self.log_signal.emit("Koneksi diputus.")


class ADAMClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADAM-5000 TCP Register Controller / Tester")
        self.resize(850, 650)

        self.worker = ModbusWorker()
        self.worker.log_signal.connect(self.append_log)

        self._init_ui()

    def _init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        # --- Connection Panel ---
        conn_grp = QGroupBox("Koneksi Modbus TCP Server")
        conn_layout = QHBoxLayout(conn_grp)

        conn_layout.addWidget(QLabel("IP Address:"))
        self.txt_ip = QLineEdit("127.0.0.1")
        conn_layout.addWidget(self.txt_ip)

        conn_layout.addWidget(QLabel("Port:"))
        self.txt_port = QLineEdit("502")
        self.txt_port.setFixedWidth(60)
        conn_layout.addWidget(self.txt_port)

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.btn_connect)

        layout.addWidget(conn_grp)

        # --- Control Panels ---
        ctrl_layout = QGridLayout()

        # 1. Analog Output (Slot 0-2: Address 1 - 12)
        ao_grp = QGroupBox("Write AO (Slot 0-2 / HR 1-12)")
        ao_grid = QGridLayout(ao_grp)

        ao_grid.addWidget(QLabel("Slot (0-2):"), 0, 0)
        self.spn_ao_slot = QSpinBox()
        self.spn_ao_slot.setRange(0, 2)
        ao_grid.addWidget(self.spn_ao_slot, 0, 1)

        ao_grid.addWidget(QLabel("Channel (0-3):"), 1, 0)
        self.spn_ao_ch = QSpinBox()
        self.spn_ao_ch.setRange(0, 3)
        ao_grid.addWidget(self.spn_ao_ch, 1, 1)

        ao_grid.addWidget(QLabel("Raw Value (0-4095):"), 2, 0)
        self.spn_ao_val = QSpinBox()
        self.spn_ao_val.setRange(0, 4095)
        ao_grid.addWidget(self.spn_ao_val, 2, 1)

        btn_write_ao = QPushButton("Write AO Register")
        btn_write_ao.clicked.connect(self.send_ao_write)
        ao_grid.addWidget(btn_write_ao, 3, 0, 1, 2)

        ctrl_layout.addWidget(ao_grp, 0, 0)

        # 2. Digital Output (Slot 3: Address 49 - 64)
        do_grp = QGroupBox("Write DO (Slot 3 / Coil 49-64)")
        do_grid = QGridLayout(do_grp)

        do_grid.addWidget(QLabel("Channel (0-15):"), 0, 0)
        self.spn_do_ch = QSpinBox()
        self.spn_do_ch.setRange(0, 15)
        do_grid.addWidget(self.spn_do_ch, 0, 1)

        btn_do_on = QPushButton("Set ON")
        btn_do_on.setStyleSheet("background-color: #2e7d32; color: white;")
        btn_do_on.clicked.connect(lambda: self.send_do_write(True))
        do_grid.addWidget(btn_do_on, 1, 0)

        btn_do_off = QPushButton("Set OFF")
        btn_do_off.setStyleSheet("background-color: #c62828; color: white;")
        btn_do_off.clicked.connect(lambda: self.send_do_write(False))
        do_grid.addWidget(btn_do_off, 1, 1)

        ctrl_layout.addWidget(do_grp, 0, 1)

        # 3. Inject Sensor Data (Slot 4: AI, Slot 5: Counter, Slot 6: TC)
        input_grp = QGroupBox("Simulasi Input (Slot 4 AI, Slot 5 Counter, Slot 6 TC)")
        input_grid = QGridLayout(input_grp)

        input_grid.addWidget(QLabel("Module Target:"), 0, 0)
        self.spn_mod_target = QSpinBox()
        self.spn_mod_target.setRange(4, 6)
        self.spn_mod_target.setValue(4)
        input_grid.addWidget(self.spn_mod_target, 0, 1)

        input_grid.addWidget(QLabel("Channel:"), 1, 0)
        self.spn_mod_ch = QSpinBox()
        self.spn_mod_ch.setRange(0, 7)
        input_grid.addWidget(self.spn_mod_ch, 1, 1)

        input_grid.addWidget(QLabel("Raw Value:"), 2, 0)
        self.spn_mod_val = QSpinBox()
        self.spn_mod_val.setRange(0, 65535)
        input_grid.addWidget(self.spn_mod_val, 2, 1)

        btn_write_input = QPushButton("Update Register Value")
        btn_write_input.clicked.connect(self.send_input_write)
        input_grid.addWidget(btn_write_input, 3, 0, 1, 2)

        ctrl_layout.addWidget(input_grp, 1, 0, 1, 2)

        layout.addLayout(ctrl_layout)

        # Terminal Log
        log_grp = QGroupBox("Client Event Log")
        log_layout = QVBoxLayout(log_grp)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas;")
        log_layout.addWidget(self.log_text)

        layout.addWidget(log_grp)
        self.setCentralWidget(main_widget)

    def toggle_connection(self):
        if self.btn_connect.text() == "Connect":
            self.worker.host = self.txt_ip.text().strip()
            self.worker.port = int(self.txt_port.text().strip())
            if self.worker.connect_server():
                self.btn_connect.setText("Disconnect")
                self.btn_connect.setStyleSheet("background-color: #c62828; color: white;")
        else:
            self.worker.disconnect_server()
            self.btn_connect.setText("Connect")
            self.btn_connect.setStyleSheet("")

    def send_ao_write(self):
        slot = self.spn_ao_slot.value()
        ch = self.spn_ao_ch.value()
        val = self.spn_ao_val.value()
        
        # Formula Address Holding Register: (Slot * 16) + Channel + 1
        address = (slot * 16) + ch + 1
        self.worker.write_holding_register(address, val)

    def send_do_write(self, state):
        ch = self.spn_do_ch.value()
        
        # Formula Address Coil: (Slot 3 * 16) + Channel + 1 = 49 + Channel
        address = (3 * 16) + ch + 1
        self.worker.write_coil(address, state)

    def send_input_write(self):
        slot = self.spn_mod_target.value()
        ch = self.spn_mod_ch.value()
        val = self.spn_mod_val.value()

        address = (slot * 16) + ch + 1
        self.worker.write_holding_register(address, val)

    def append_log(self, msg):
        self.log_text.append(msg)

    def closeEvent(self, event):
        self.worker.disconnect_server()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ADAMClientGUI()
    gui.show()
    sys.exit(app.exec())