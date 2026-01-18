from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPointF, QTimer
from SCREEN.screen1 import HeatingModel
from SCREEN.screen2 import InstalacjaScreen
import sys

# ------------------------- OKNO RUR -------------------------
class Infoekran(QWidget):
    def __init__(self, model):
        super().__init__()
        self.setMinimumSize(900, 600)
        self.model = model
        self.setWindowTitle("Ekran glowny")
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_info)
        self.refresh_timer.start(200)

        self.temp_label = QLabel(f"Temperatura: {self.model.get_temperature()}°C")
        self.temp_label.setAlignment(Qt.AlignCenter)


        self.status = QLabel("Brak przeplywu")
        self.status.setAlignment(Qt.AlignCenter)

        self.zbiornik_label = QLabel()
        self.zbiornik_label.setAlignment(Qt.AlignCenter)

        self.goto_piec_btn = QPushButton("Przejdz do ekranu z Piecem")
        self.goto_piec_btn.clicked.connect(self.open_piec_screen)

        self.goto_instalacja_btn = QPushButton("Przejdz do ekranu z instalacja")
        self.goto_instalacja_btn.clicked.connect(self.open_instalacja_screen)


        layout = QVBoxLayout()
        layout.addWidget(QLabel("Rurociagi: "))
        layout.addWidget(self.status)
        layout.addWidget(self.zbiornik_label)
        layout.addWidget(self.temp_label)
        layout.addWidget(self.goto_piec_btn)
        layout.addWidget(self.goto_instalacja_btn)
        self.setLayout(layout)

        """Polaczenie sygnalow po to aby informacje byly przekazywane miedzy ekranami, inaczej nie beda one plynne,
             niby mozna przez QTimer ale słabo to działalo, wiec postanowiłem zrobic z niektórch zmiennych sygnału,dzięki
            bibliotece pyqtSignal i wtedy jezeli cos sie zmienia mozemy samemu reczenie wymusic wyemitowanie/przeslanie
            sygnalu aby na inne ekrany rowniez dostaly ten sygnal, jeżeli sygnal się pojawi program od razu wykonuje funkcje
            aktualizacji"""


        self.model.temperatureChanged.connect(self.update_info)
        self.model.pumpchanged.connect(self.update_info)


        # Aktualizacja statusu przy starcie
        self.update_info()

    def update_bojler(self, value):
        self.zbiornik_label.setText(f"Zbiornik: {int(value)}%")
        self.update()

    def update_spust(self, state):
        self.update()

    def update_info(self, *_):
        temp = self.model.get_temperature()


        if self.model.przepust !=0:
            self.status.setText(f"Przepływ – {self.model.przepust}%")
        else:
            self.status.setText("Brak przepływu")

        self.temp_label.setText(f"Temperatura: {temp}°C")

        self.zbiornik_label.setText(f"Zbiornik: {int(self.model.bojler_fill)}%")
        self.update()



    def toggle_pump(self):
        self.model.set_pump(not self.model.pompa_on())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)


            # Pasek temperatury

        painter.setBrush(QColor("lightgray"))
        painter.setPen(Qt.black)
        painter.drawRect(50, 475, 800, 25)

        temp = self.model.get_temperature()
        wypelnienie = int((temp - 20) / 80 * 800)
        painter.setBrush(QColor("orange"))
        painter.drawRect(50, 475, wypelnienie, 25)

            #=============== ZBIORNIK ============

        painter.setPen(QPen(Qt.black,2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(405, 340, 80, 80)
        wypelnieniebojler= int(80*self.model.bojler_fill/100)
        painter.setBrush(QColor(0, 170, 255))
        painter.setPen(Qt.NoPen)
        painter.drawRect(405, 340+80-wypelnieniebojler, 80, wypelnieniebojler)




                        #ZAWORY DO SPRAWDZANIA STANU

        self.draw_valve(painter, 150, 100, text="Spust", open=self.model.spust_otwarty)
        self.draw_valve(painter, 300, 100, text="Obieg 1", open=self.model.zaw1_otwarty)
        self.draw_valve(painter, 450, 100, text="Obieg 2", open=self.model.zaw2_otwarty)
        self.draw_valve(painter, 600, 100, text="Obieg 3", open=self.model.zaw3_otwarty)

        if self.model.pompa_on():
            color = QColor(0, 200, 0)
        else:
            color = QColor(200, 0, 0)

        painter.setBrush(color)
        painter.setPen(Qt.black)
        painter.drawEllipse(750, 76,50,50)
        painter.drawText(725,140,100,20, Qt.AlignCenter, "Stan Pompy")

    def draw_valve(self, painter, x, y, text="", open=True):
        size = 19

        if open:
            color = QColor(0, 160, 0)  # zielony = otwarty
        else:
            color = QColor(180, 0, 0)  # czerwony = zamknięty

        painter.setPen(Qt.NoPen)
        painter.setBrush(color)

        # lewy trójkąt ▶
        lewy_trojkat = [
            QPointF(x, y - size),
            QPointF(x, y + size),
            QPointF(x + size, y)
        ]

        # prawy trójkąt ◀
        prawy_trojkat = [
            QPointF(x + size, y),
            QPointF(x + 2 * size, y - size),
            QPointF(x + 2 * size, y + size)
        ]

        painter.drawPolygon(lewy_trojkat)
        painter.drawPolygon(prawy_trojkat)

        painter.setPen(Qt.black)
        if text:
            painter.drawText(x - 10, y + 35, text)

    def open_piec_screen(self):
        from SCREEN.screen1 import PiecScreen  # import tutaj, żeby uniknąć cyklicznego importu
        self.piec_okno = PiecScreen(self.model)
        self.piec_okno.show()
        self.hide()

    def open_instalacja_screen(self):
        self.instalacja_okno = InstalacjaScreen(self.model)
        self.instalacja_okno.show()
        self.hide()


# ------------------------- URUCHOMIENIE -------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = HeatingModel()
    window = Infoekran(model)
    window.show()
    sys.exit(app.exec_())
