from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QSlider, QSizePolicy
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer
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

        if 40 < temp < 60:
            painter.setBrush(Qt.darkRed)
        elif temp >=60:
            painter.setBrush(Qt.red)
        elif temp < 40:
            painter.setBrush(Qt.lightGray)

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

        # zaokraglenie u gory
        painter.drawArc(tx - 15, ty - 10, 30, 30, 0 * 16, 180 * 16)

        # zaokraglenie na dole
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

        popiol_procent = self.model.stan_popiol()


        if popiol_procent == 100:
            color = Qt.magenta
        elif popiol_procent >80:
            import time
            if int(time.time()*2)%2 ==0:
                color = Qt.red
            else:
                color = Qt.white
        else:
            color = Qt.gray


        painter.setBrush(color)
        painter.setPen(Qt.black)
        painter.drawRect(280, 490, 80, 50)
        painter.drawText(280,490,80,50, Qt.AlignCenter, f"{popiol_procent}")



class PiecScreen(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowTitle("Piec")

        self.view = HeatingView(model)

            #slider do temperaturki

        self.temp_label = QLabel(f"Temp: {self.model.get_temperature()}°C")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(20, 100)
        self.slider.setValue(self.model.get_temperature())
        self.slider.valueChanged.connect(self.model.set_temperature)

            #przycisk do aktywacji pompy grzewczej
        self.pump_btn = QPushButton("Pompa ON/OFF")
        self.pump_btn.clicked.connect(self.switch_pump)



        self.goto_ekrangl_btn = QPushButton("Przejdź do ekranu glownego")
        self.goto_ekrangl_btn.clicked.connect(self.open_mainscreen)

        self.goto_rury_btn = QPushButton("Przejdź do instalacji")
        self.goto_rury_btn.clicked.connect(self.open_rury_screen)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.temp_label)
        layout.addWidget(self.slider)
        layout.addWidget(self.pump_btn)
        layout.addWidget(self.goto_ekrangl_btn)
        layout.addWidget(self.goto_rury_btn)
        self.setLayout(layout)

        # przycisk do aktywacji auto grzania
        self.auto_btn = QPushButton("Auto grzanie", self)
        self.auto_btn.setGeometry(145, 405, 250, 70)
        self.auto_btn.raise_()
        self.auto_btn.clicked.connect(self.tryb_auto_grzanie)

                # przycisk do popiolu
        self.popiol_btn = QPushButton("Oproznij popiol", self)
        self.popiol_btn.setGeometry(130, 505, 150, 50)
        self.popiol_btn.raise_()
        self.popiol_btn.clicked.connect(self.reset_popiol)

        self.model.temperatureChanged.connect(self.update_temp)
        self.model.temperatureChanged.connect(self.update_pump_button)
        self.model.pumpchanged.connect(self.update_pump_button)
        self.update_pump_button(self.model.pompa_on())
        self.model.popiolchanged.connect(self.update)


    def tryb_auto_grzanie(self):
        self.model.auto_grzanie()

    def reset_popiol(self):
        self.model.reset_popiol()


    def open_mainscreen(self):
        from main import RuryScreen  # brak cyklicznego ladowaania
        self.mainwindow = RuryScreen(self.model)
        self.mainwindow.show()
        self.hide()

    def update_temp(self, value):
        self.temp_label.setText(f"Temp: {value}°C")
        self.slider.setValue(value)
        if value >= 90:
            if self.model.pompa_on():
                self.model.set_pump(False)  # wymuszone wyłączenie
            self.update_pump_button(False)
        if value <= 30:
            if self.model.pompa_on():
                self.model.set_pump(False)  # wymuszone wyłączenie
            self.update_pump_button(False)


    def switch_pump(self):
        if not self.model.pompa_on() and self.model.get_temperature() < 40:
            self.update_pump_button(self.model.pompa_on())
            return
        self.model.set_pump(not self.model.pompa_on())

        if self.model.get_temperature() > 90:
            self.update_pump_button(self.model.pompa_on())
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
            return

        if  self.model.get_temperature() >= 90:
            self.pump_btn.setStyleSheet("background-color: pink; color: black;")
            self.pump_btn.setText("Temperatura za wysoka, bezpiecznik termiczny zadzialal")
            return

        if not self.model.pompa_on():
            self.pump_btn.setStyleSheet("background-color: lightgrey; color: black;")
            self.pump_btn.setText("Możliwość załączenia pompy")
            return

        if self.model.pompa_on():
            self.pump_btn.setStyleSheet("background-color: green; color: white;")
            self.pump_btn.setText("Pompa ON")
            return

    def open_rury_screen(self):
        from SCREEN.screen2 import InstalacjaScreen
        self.rury = InstalacjaScreen(self.model)
        self.rury.show()
        self.close()

    def tryb_auto_grzanie(self):
        if not self.model.czyauto_grzanie:
            self.model.auto_grzanie()
            self.auto_btn.setText("Stop automatyczne grzanie")
        else:
            self.model.stop_auto_grzanie()
            self.auto_btn.setText("Automatyczne grzanie")


class HeatingModel(QObject):
    temperatureChanged = pyqtSignal(int)
    pumpchanged = pyqtSignal(bool)
    popiolchanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._temperature = 30
        self._pump = False
        self.popiol = 0
        self.popiol_timer = QTimer(self)
        self.popiol_timer.timeout.connect(self.zwieksz_popiol)
        self.popiol_timer.start(700)
        self.zaw1_otwarty = False
        self.zaw2_otwarty = False
        self.zaw3_otwarty = False
        self.bojler_fill = 0
        self.spust_otwarty = True
        self.przepust = 0
        self.czyauto_grzanie = False
        self.przegrzanie = False

                #Timery do automatycznego grzania do symul
        self.temp_timer = QTimer(self)
        self.temp_timer.timeout.connect(self.auto_grzanie_sym1)
        self.cool_timer = QTimer(self)
        self.cool_timer.timeout.connect(self.auto_grzanie_sym2)

            #POPIÓŁ
    def zwieksz_popiol(self):
        if self.popiol == 100:
            self.set_pump(False)

        if self.popiol < 100:
            self.popiol += 1
            self.popiolchanged.emit(self.popiol)

    def stan_popiol(self):
        return self.popiol

    def reset_popiol(self):
        self.popiol = 0
        self.popiolchanged.emit(self.popiol)


            #TEMPERATURA
    def set_temperature(self, value):
        self._temperature = value
        self.temperatureChanged.emit(value)  # wysyła event

    def get_temperature(self):
        return self._temperature

    def auto_grzanie(self):
        if not self.czyauto_grzanie:
            self.czyauto_grzanie = True
            self.temp_timer.start(300)
            self.cool_timer.start(4000)

    def stop_auto_grzanie(self):
        self.czyauto_grzanie = False
        self.temp_timer.stop()
        self.cool_timer.stop()

    def auto_grzanie_sym1(self): #dodawanie
        if not self.przegrzanie:
            if self._temperature < 100:
                self._temperature +=1
            if self._temperature >= 100:
                self._temperature = 100
                self.przegrzanie = True
                self.spust_otwarty = False

        self.temperatureChanged.emit(self._temperature)

    def auto_grzanie_sym2(self): #odejmowanie
        self._temperature -=3
        if self._temperature <= 30:
            self._temperature = 30
            self.przegrzanie = False
            self.spust_otwarty = True
        self.temperatureChanged.emit(self._temperature)

            #POMPA
    def set_pump(self, state):
        self._pump = state
        self.pumpchanged.emit(state)

    def pompa_on(self):
        return self._pump





if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = HeatingModel()
    window = PiecScreen(model)
    window.show()
    sys.exit(app.exec())