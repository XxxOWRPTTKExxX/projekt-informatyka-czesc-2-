from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QPainter, QPen, QColor, QPainterPath
from PyQt5.QtCore import Qt, QPointF, QTimer
from SCREEN.screen1 import HeatingModel


class Rura:
    def __init__(self, punkty, grubosc=14, plynie=False):
        self.punkty = [QPointF(p[0], p[1]) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = Qt.gray
        self.kolor_wody = QColor(0, 170, 255)
        self.czy_plynie = plynie


    def draw(self, painter):
        if len(self.punkty) < 2:
            return

        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]:
            path.lineTo(p)

        # obudowa rury
        painter.setPen(QPen(self.kolor_rury, self.grubosc, Qt.SolidLine,
                                Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(path)

        if self.czy_plynie:
            painter.setPen(QPen(self.kolor_wody, self.grubosc - 6, Qt.SolidLine,
                                Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(path)


class InstalacjaScreen(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowTitle("Schemat instalacji CO")
        self.setMinimumSize(900, 600)
        self.goto_ekran1_btn = QPushButton("Ekran z piecem", self)
        self.goto_ekran1_btn.setGeometry(50, 350, 150, 50)
        self.goto_ekran1_btn.raise_()
        self.goto_ekran1_btn.clicked.connect(self.goto_ekran1)
        self.rury = []

        y = 250

        self.pompa_on = self.model.pump_on()
        self.angle=0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)




        # rura wejściowa
        self.rury.append(Rura([(50, y), (120, y),], plynie=True))

        # po zaworze do pompy
        self.rury.append(Rura([(160, y), (220, y)], plynie=self.model.pump_on()))

        # po pompie
        self.rury.append(Rura([(280, y), (330, y)], plynie=self.model.pump_on()))

        # do bojlera
        self.rury.append(Rura([(370, y), (420, y)], plynie=self.model.pump_on()))

        # do rozgałęzienia
        self.rury.append(Rura([(500, y), (550, y)], plynie=self.model.pump_on()))

        # obiegi
        self.rury.append(Rura([(550, y), (550, y - 100)]))
        self.rury.append(Rura([(550, y), (550, y + 100)]))
        self.rury.append(Rura([(550, y - 100), (610, y - 100)]))
        self.rury.append(Rura([(550, y), (610, y)]))
        self.rury.append(Rura([(550, y + 100), (610, y + 100)]))

        # przykładowy stan bojlera (0–100%)
        self.bojler_fill = 60

    def update_animation(self):
        if self.pompa_on:
            self.angle += 5  # pręty kręcą się o 5 stopni co tick
            self.angle %= 360
        self.update()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for rura in self.rury:
            rura.draw(painter)
        pen = QPen(Qt.black, 3)
        painter.setPen(pen)

        y = 250




        # ================= ZAWÓR DOLEWANIA =================
        self.draw_valve(painter, 120, y, "Dolewanie", open=True)


        # ================= POMPA =================
        #painter.drawLine(160, y, 220, y)
        #painter.drawEllipse(220, y - 30, 60, 60)
        painter.drawText(220, y + 50, "Pompa")
        x= 220
        radius = 30

        # zapamiętujemy aktualny stan painter
        painter.save()

        # przesuwamy środek układu współrzędnych do środka pompy
        center_x, center_y = x + radius, y
        painter.translate(center_x, center_y)

        # obrót o self.angle jeśli pompa działa
        if self.pompa_on:  # True/False
            painter.rotate(self.angle)  # obrót w stopniach

        # narysuj dwa pręty względem środka
        pen = QPen(Qt.red, 4)
        painter.setPen(pen)
        length = 25
        painter.drawLine(-length, 0, length, 0)  # poziomy
        painter.drawLine(0, -length, 0, length)  # pionowy

        # przywracamy poprzedni stan painter
        painter.restore()

        # ================= ZAWÓR BEZPIECZEŃSTWA =================
        #painter.drawLine(280, y, 330, y)
        self.draw_valve(painter, 330, y, "Spust", open=False)

        # ================= BOJLER =================
        #painter.drawLine(370, y, 420, y)
        self.draw_bojler(painter, 420, y - 80)



        # ================= OBIEGI =================
        self.draw_circuit(painter, 550, y - 100, "Obieg 1")
        self.draw_circuit(painter, 550, y, "Obieg 2")
        self.draw_circuit(painter, 550, y + 100, "Obieg 3")

    # ================= ELEMENTY =================



    def draw_bojler(self, painter, x, y):
        width = 60
        height = 160

        painter.drawRect(x, y, width, height)

        # wypełnienie bojlera
        fill_height = int(height * self.bojler_fill / 100)
        painter.setBrush(QColor("lightblue"))
        painter.drawRect(
            x,
            y + height - fill_height,
            width,
            fill_height
        )

        painter.setBrush(Qt.NoBrush)
        painter.drawText(x - 10, y - 10, f"Bojler {self.bojler_fill}%")

    def draw_circuit(self, painter, x, y, name):
        self.draw_valve(painter, x + 60, y, "")
        painter.drawText(x + 110, y + 5, name)

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
            QPointF(x, y-size),
            QPointF(x, y + size),
            QPointF(x + size, y)
        ]

        # prawy trójkąt ◀
        right_triangle = [
            QPointF(x + size, y),
            QPointF(x + 2*size, y - size),
            QPointF(x + 2 * size, y+size)
        ]

        painter.drawPolygon(left_triangle)
        painter.drawPolygon(right_triangle)

        painter.setPen(Qt.black)
        if text:
            painter.drawText(x - 10, y + 35, text)

    def goto_ekran1(self):
        from SCREEN.screen1 import PiecScreen
        self.ekran1 = PiecScreen(self.model)
        self.ekran1.show()
        self.hide()