from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QSlider, QSizePolicy
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QObject, pyqtSignal
import sys



class HeatingView(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.model.temperatureChanged.connect(self.update)
        self.setMinimumSize(900, 600)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(Qt.black, 3)
        painter.setPen(pen)

        temp = self.model.get_temperature()

        # ===== WYMIARY PIEC =====
        x = 100
        y = 100
        width = 300
        height = 450

        # główny prostokąt
        painter.drawRect(x, y, width, height)

        # podziały pieca
        painter.drawLine(x, y + 200, x + width, y + 200)
        painter.drawLine(x, y + 380, x + width, y + 380)

        # podstawa
        painter.drawRect(x, y + height, width, 0)

        # ===== TERMOMETR =====
        tx = 650
        ty = 60

        # rurka termometru
        painter.drawLine(tx, ty, tx, ty+270 + 200)

        # zaokrąglenie u góry
        painter.drawArc(tx - 15, ty - 10, 30, 30, 0 * 16, 180 * 16)

        # zbiornik na dole
        painter.drawArc(tx - 25, ty + 450, 50, 50, 55 * 16, -290 * 16)
        painter.drawLine(tx-15, ty+5 , tx-15, ty + 455)
        painter.drawLine(tx + 15, ty + 5, tx + 15, ty + 455)

        #kolor temp
        if temp < 40:
            painter.setBrush(Qt.blue)
        else:
            painter.setBrush(Qt.red)

        max_temp = 100
        min_temp = 20

        thermo_height = 465
        filled_height = int((temp - min_temp) / (max_temp - min_temp) * thermo_height)
        painter.drawEllipse(625,510,50,50)
        painter.drawRect(tx - 10,ty + 460 - filled_height,20,filled_height-10)


class PiecScreen(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowTitle("Piec")

        self.view = HeatingView(model)

            #slider do temperaturki

        self.temp_label = QLabel(f"Temp: {self.model.get_temperature()}°C")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(20, 100)
        slider.setValue(self.model.get_temperature())
        slider.valueChanged.connect(self.model.set_temperature)

            #przycisk do aktywacji pompy grzewczej
        self.pump_btn = QPushButton("Pompa ON/OFF")
        self.pump_btn.clicked.connect(self.switch_pump)

        self.goto_ekrangl_btn = QPushButton("Przejdź do ekranu glownego")
        self.goto_ekrangl_btn.clicked.connect(self.open_mainscreen)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.temp_label)
        layout.addWidget(slider)
        layout.addWidget(self.pump_btn)
        layout.addWidget(self.goto_ekrangl_btn)
        self.setLayout(layout)

        self.model.temperatureChanged.connect(self.update_temp)
        self.model.pumpchanged.connect(self.update_pump_button)
        self.update_pump_button(self.model.pump_on())

    def open_mainscreen(self):
        from main import RuryScreen  # import tutaj, żeby uniknąć cyklicznego importu
        self.mainwindow = RuryScreen(self.model)
        self.mainwindow.show()
        self.hide()

    def update_temp(self, value):
        self.temp_label.setText(f"Temp: {value}°C")
        if value >= 90:
            if self.model.pump_on():
                self.model.set_pump(False)  # wymuszone wyłączenie
            self.update_pump_button(False)
        if value <= 30:
            if self.model.pump_on():
                self.model.set_pump(False)  # wymuszone wyłączenie
            self.update_pump_button(False)


    def switch_pump(self):
        if not self.model.pump_on() and self.model.get_temperature() < 40:
            self.update_pump_button(self.model.pump_on())
            return
        self.model.set_pump(not self.model.pump_on())

        if self.model.get_temperature() > 90:
            self.update_pump_button(self.model.pump_on())
            return


    def update_pump_button(self, state):

        if state:
            self.pump_btn.setStyleSheet("background-color: green; color: white;")
            self.pump_btn.setText("Pompa ON")
        else:
            self.pump_btn.setStyleSheet("background-color: red; color: white;")
            self.pump_btn.setText("Pompa OFF")

        if  self.model.get_temperature() < 40:
            self.pump_btn.setStyleSheet("background-color: yellow; color: black;")
            self.pump_btn.setText("Za niska temperatura, zwieksz aby zalaczyc pompe")

        if  self.model.get_temperature() >= 90:
            self.pump_btn.setStyleSheet("background-color: pink; color: black;")
            self.pump_btn.setText("Temperatura za wysoka, bezpiecznik termiczny zadzialal")


class HeatingModel(QObject):
    temperatureChanged = pyqtSignal(int)
    pumpchanged = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._temperature = 30
        self._pump = False

    def set_temperature(self, value):
        self._temperature = value
        self.temperatureChanged.emit(value)  # wysyła event

    def get_temperature(self):
        return self._temperature

    def set_pump(self, state):
        self._pump = state
        self.pumpchanged.emit(state)

    def pump_on(self):
        return self._pump





if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = HeatingModel()
    window = PiecScreen(model)
    window.show()
    sys.exit(app.exec())