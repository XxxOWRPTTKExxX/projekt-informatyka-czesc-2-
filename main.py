from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QPushButton, QSlider, QSizePolicy
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QPointF
from SCREEN.screen1 import HeatingModel
from SCREEN.screen2 import InstalacjaScreen
import sys

# ------------------------- OKNO RUR -------------------------
class RuryScreen(QWidget):
    def __init__(self, model):
        super().__init__()
        self.setMinimumSize(900, 600)
        self.model = model
        self.setWindowTitle("Ekran glowny")

        self.temp_label = QLabel(f"Temperatura: {self.model.get_temperature()}°C")
        self.temp_label.setAlignment(Qt.AlignCenter)


        self.status = QLabel("Brak przepływu")
        self.status.setAlignment(Qt.AlignCenter)

        self.goto_piec_btn = QPushButton("Przejdź do ekranu z Piecem")
        self.goto_piec_btn.clicked.connect(self.open_piec_screen)



        layout = QVBoxLayout()
        layout.addWidget(QLabel("Rurociągi:"))
        layout.addWidget(self.status)
        layout.addWidget(self.temp_label)
        layout.addWidget(self.goto_piec_btn)
        self.setLayout(layout)

        self.rect_status_text = ""

        self.model.temperatureChanged.connect(self.update_flow)
        self.model.pumpchanged.connect(self.update_flow)

        # Aktualizacja statusu przy starcie
        self.update_flow()

    def update_flow(self, *_):
        temp = self.model.get_temperature()
        pompa = self.model.pompa_on()


        if self.model.przepust !=0:
            self.status.setText(f"Przepływ – {self.model.przepust}%")
        else:
            self.status.setText("Brak przepływu")

        self.temp_label.setText(f"Temperatura: {temp}°C")
        self.update()


    def open_piec_screen(self):
        from SCREEN.screen1 import PiecScreen  # import tutaj, żeby uniknąć cyklicznego importu
        self.piec_window = PiecScreen(self.model)
        self.piec_window.show()
        self.hide()

    def toggle_pump(self):
        self.model.set_pump(not self.model.pompa_on())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect_height = self.height() - 50

        # Pasek temperatury
        bar_left = 50
        bar_width = self.width() - 100
        bar_height = 20
        bar_margin = 50
        bar_top = self.height() - bar_height - bar_margin

        painter.setBrush(QColor("lightgray"))
        painter.setPen(Qt.black)
        painter.drawRect(bar_left, bar_top, bar_width, bar_height)

        temp = self.model.get_temperature()
        fill_width = int((temp - 20) / (100 - 20) * bar_width)
        painter.setBrush(QColor("orange"))
        painter.drawRect(bar_left, bar_top, fill_width, bar_height)



                        #ZAWORY DO SPRAWDZANIA STANU

        #self.draw_valve(painter, 50, 100, text="Dolewanie", open=True)
        self.draw_valve(painter, 150, 100, text="Spust", open=self.model.spust_otwarty)
        self.draw_valve(painter, 300, 100, text="Obieg 1", open=self.model.zaw1_otwarty)
        self.draw_valve(painter, 450, 100, text="Obieg 2", open=self.model.zaw2_otwarty)
        self.draw_valve(painter, 600, 100, text="Obieg 3", open=self.model.zaw3_otwarty)

    def draw_valve(self, painter, x, y, text="", open=True):
        size = 19

        if open:
            color = QColor(0, 160, 0)  # zielony = otwarty
        else:
            color = QColor(180, 0, 0)  # czerwony = zamknięty

        painter.setPen(Qt.NoPen)
        painter.setBrush(color)

        # lewy trójkąt ▶
        left_triangle = [
            QPointF(x, y - size),
            QPointF(x, y + size),
            QPointF(x + size, y)
        ]

        # prawy trójkąt ◀
        right_triangle = [
            QPointF(x + size, y),
            QPointF(x + 2 * size, y - size),
            QPointF(x + 2 * size, y + size)
        ]

        painter.drawPolygon(left_triangle)
        painter.drawPolygon(right_triangle)

        painter.setPen(Qt.black)
        if text:
            painter.drawText(x - 10, y + 35, text)


# ------------------------- URUCHOMIENIE -------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = HeatingModel()
    window = RuryScreen(model)
    window.show()
    sys.exit(app.exec_())
