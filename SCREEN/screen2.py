from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QPainter, QPen, QColor, QPainterPath
from PyQt5.QtCore import Qt, QPointF, QTimer
from SCREEN.screen1 import HeatingModel


class Rura:
    def __init__(self, punkty, grubosc=14, plynie=False, zawsze=True):
        self.punkty = [QPointF(p[0], p[1]) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = Qt.gray
        self.kolor_wody = QColor(0, 170, 255)
        self.czy_plynie = plynie
        self.zawsze=zawsze


    def draw(self, painter):
        if len(self.punkty) < 2:
            return

        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty:
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
        self.zaw1_otwarty = self.model.zaw1_otwarty
        self.zaw2_otwarty = self.model.zaw2_otwarty
        self.zaw3_otwarty = self.model.zaw3_otwarty
        self.bojler_fill = self.model.bojler_fill
        self.spust_otwarty = self.model.spust_otwarty
        self.przepust= self.model.przepust

        self.goto_ekran1_btn = QPushButton("Ekran z piecem", self)
        self.goto_ekran1_btn.setStyleSheet("background-color: darkCyan;")
        self.goto_ekran1_btn.setGeometry(50, 350, 150, 50)
        self.goto_ekran1_btn.raise_()
        self.goto_ekran1_btn.clicked.connect(self.goto_ekran1)


                #przyciski zaworow obiegu
        self.zaw1_btn = QPushButton("Zaw I obieg", self)
        self.zaw1_btn.setGeometry(50, 400, 150, 50)
        self.zaw1_btn.raise_()
        self.zaw2_btn = QPushButton("Zaw II obieg", self)
        self.zaw2_btn.setGeometry(200, 400, 150, 50)
        self.zaw2_btn.raise_()
        self.zaw3_btn = QPushButton("Zaw III obieg", self)
        self.zaw3_btn.setGeometry(350, 400, 150, 50)
        self.zaw3_btn.raise_()

                #przycisk zaworu spustu
        self.spust_btn = QPushButton("Zaw spustu", self)
        self.spust_btn.setStyleSheet("background-color: magenta;")
        self.spust_btn.setGeometry(202, 350, 150, 50)
        self.spust_btn.raise_()



        self.zaw1_btn.clicked.connect(self.wlaczeniezaw1)
        self.zaw2_btn.clicked.connect(self.wlaczeniezaw2)
        self.zaw3_btn.clicked.connect(self.wlaczeniezaw3)
        self.spust_btn.clicked.connect(self.wlaczeniespust)

        y = 250

        self.angle=0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)

        # Ustawilem rury w tablicy aby móc konkretne wymieniac uzyte przy rurkach przy zbiorniku
        self.rury = []


        # rura wejściowa
        self.rury.append(Rura([(50, y), (120, y)], plynie=True))

        # po zaworze do pompy
        self.rury.append(Rura([(160, y), (220, y)], plynie=self.model.pompa_on()))

        # po pompie
        self.rury.append(Rura([(280, y), (330, y)], plynie=self.model.pompa_on()))

        # do bojlera
        self.rury.append(Rura([(370, y), (420, y)], plynie=self.model.pompa_on() or self.model.bojler_fill > 0 ))

        # do rozgałęzienia
        self.rury.append(Rura([(500, y), (550, y)], plynie=self.model.pompa_on() ))

        # obiegi
        self.rury.append(Rura([(550, y), (550, y - 100)],plynie=self.model.pompa_on() or self.model.bojler_fill > 0 ))
        self.rury.append(Rura([(550, y), (550, y + 100)], plynie=self.model.pompa_on() or self.model.bojler_fill > 0))
        self.rury.append(Rura([(550, y - 100), (610, y - 100)], plynie=self.model.pompa_on() or self.model.bojler_fill > 0))
        self.rury.append(Rura([(480, y), (610, y)], plynie=self.model.pompa_on() or self.model.bojler_fill > 0))
        self.rury.append(Rura([(550, y + 100), (610, y + 100)], plynie=self.model.pompa_on() or self.model.bojler_fill > 0))





    def update_animation(self):
        if self.model.pompa_on() and self.model.stan_popiol()<100:
            self.angle += 5  # pręty kręcą się o 5 stopni co tick
            self.angle %= 360

        for rura in self.rury:
            if rura in [self.rury[3],self.rury[5], self.rury[6], self.rury[7], self.rury[8], self.rury[9]]:
                rura.czy_plynie = self.model.bojler_fill > 0
            else:
                rura.czy_plynie = self.model.pompa_on()

        self.update_bojler()
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

        painter.setBrush(Qt.lightGray)
        painter.drawEllipse(220, y - 30, 60, 60)
        painter.drawText(220, y + 50, "Pompa")
        x= 220
        radius = 30

        # zapamiętujemy aktualny stan painter
        painter.save()

        # przesuwamy środek układu współrzędnych do środka pompy
        center_x, center_y = x + radius, y
        painter.translate(center_x, center_y)

        # obrót o self.angle jeśli pompa działa
        if self.model.pompa_on():  # True/False
            painter.rotate(self.angle)  # obrót

        # narysuj dwa pręty względem środka
        if self.model.pompa_on():
            colorp=Qt.darkGreen
        else:
            colorp=Qt.red
        pen = QPen(colorp, 4)
        painter.setPen(pen)
        length = 25
        painter.drawLine(-length, 0, length, 0)  # poziomy
        painter.drawLine(0, -length, 0, length)  # pionowy

        # przywracamy poprzedni stan painter
        painter.restore()

        # ================= ZAWÓR SPUSTU =================
        #painter.drawLine(280, y, 330, y)
        self.draw_valve(painter, 330, y, "        Spust", open= self.spust_otwarty)
        Rura([(349, 260), (349, 330)], plynie= not self.spust_otwarty).draw(painter)

        # ================= BOJLER =================
        #painter.drawLine(370, y, 420, y)
        self.draw_bojler(painter, 420, y - 80)



        # ================= OBIEGI =================
        self.draw_circuit(painter, 550, y - 100, "              Obieg 1")
        self.draw_circuit(painter, 550, y,       "              Obieg 2")
        self.draw_circuit(painter, 550, y + 100, "              Obieg 3")

        # krótkie rurki po zaworach obiegów
        Rura([(710, y - 100), (630, y - 100)], plynie=self.zaw1_otwarty).draw(painter)
        Rura([(710, y), (630, y)], plynie=self.zaw2_otwarty).draw(painter)
        Rura([(710, y + 100), (630, y + 100)], plynie=self.zaw3_otwarty).draw(painter)

        # ================= ZAWORY OBIEGÓW =================
        self.draw_valve(painter, 600, y - 100, "", open=self.zaw1_otwarty)
        self.draw_valve(painter, 600, y, "", open=self.zaw2_otwarty)
        self.draw_valve(painter, 600, y + 100, "", open=self.zaw3_otwarty)

    # ================= ELEMENTY =================



    def draw_bojler(self, painter, x, y):
        width = 60
        height = 160

        painter.setBrush(Qt.gray)
        painter.setPen(Qt.black)
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
        painter.drawText(x - 10, y - 10, f"Bojler {int(self.bojler_fill)}%")


    def update_bojler(self):
                        #wartosci predkosci zmiany zbiornika gdy uzywamy z niego wode
                    #Najwieksza predkosc/wszystkie otwarte

        if self.zaw1_otwarty==True and self.zaw2_otwarty==True and self.zaw3_otwarty==True:
            wartosc=0.4

                    #Średnia predkosc 2 otwarte
        elif ((self.zaw1_otwarty==True and self.zaw2_otwarty==True) or (self.zaw1_otwarty==True and self.zaw3_otwarty==True)
                            or (self.zaw2_otwarty==True and self.zaw3_otwarty==True)):
            wartosc=0.1
                    #Najmniejsza predkosc 1 otwarty
        elif self.zaw1_otwarty==True or self.zaw2_otwarty==True or self.zaw3_otwarty==True:
            wartosc=0.01





        if self.model.pompa_on() and self.model.stan_popiol()<100:
            if self.bojler_fill <100:
                self.bojler_fill +=0.08
                self.model.bojler_fill = self.bojler_fill
        elif not self.model.pompa_on() and self.bojler_fill >0 and self.spust_otwarty==True:
            if self.zaw1_otwarty==True or self.zaw2_otwarty==True or self.zaw3_otwarty==True :
                self.bojler_fill -= wartosc
                self.model.bojler_fill = self.bojler_fill

        if not self.spust_otwarty:
            wartosc_spust=2
            self.przepust= 0
            self.bojler_fill -= wartosc_spust
            self.bojler_fill = max(self.bojler_fill, 0)
            self.model.bojler_fill = self.bojler_fill
        self.update()

    def draw_circuit(self, painter, x, y, name):
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

    def wlaczeniezaw1(self):
        self.zaw1_otwarty = not self.zaw1_otwarty
        self.model.zaw1_otwarty = self.zaw1_otwarty
        self.aktuprzeplyw()

    def wlaczeniezaw2(self):
        self.zaw2_otwarty = not self.zaw2_otwarty
        self.model.zaw2_otwarty = self.zaw2_otwarty
        self.aktuprzeplyw()

    def wlaczeniezaw3(self):
        self.zaw3_otwarty = not self.zaw3_otwarty
        self.model.zaw3_otwarty = self.zaw3_otwarty
        self.aktuprzeplyw()

    def wlaczeniespust(self):
        self.spust_otwarty = not self.spust_otwarty
        self.model.spust_otwarty = self.spust_otwarty
        if  self.spust_otwarty:
            color = QColor(0, 160, 0)  # zielony = otwarty
        else:
            color = QColor(180, 0, 0)  # czerwony = zamknięty
        self.aktuprzeplyw()

    def aktuprzeplyw(self):
        if not self.spust_otwarty:
            self.model.przepust = 0
        elif self.zaw1_otwarty==True and self.zaw2_otwarty==True and self.zaw3_otwarty==True:
            self.model.przepust = 100


        elif ((self.zaw1_otwarty==True and self.zaw2_otwarty==True) or (self.zaw1_otwarty==True and self.zaw3_otwarty==True)
                            or (self.zaw2_otwarty==True and self.zaw3_otwarty==True)):
            self.model.przepust = 66
                    #Najmniejsza predkosc 1 otwarty
        elif self.zaw1_otwarty==True or self.zaw2_otwarty==True or self.zaw3_otwarty==True:
            self.model.przepust = 33
        else:
            self.model.przepust = 0



    def goto_ekran1(self):
        from SCREEN.screen1 import PiecScreen
        self.ekran1 = PiecScreen(self.model)
        self.ekran1.show()
        self.hide()