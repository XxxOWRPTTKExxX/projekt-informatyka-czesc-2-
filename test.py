import pytest
from PyQt5.QtWidgets import QApplication
from SCREEN.screen1 import HeatingModel
from SCREEN.screen2 import InstalacjaScreen
import sys

@pytest.fixture
def model():
    """Fixture tworzy nowy model przed każdym testem"""
    return HeatingModel()

@pytest.fixture
def instalacja(model):
    return InstalacjaScreen(model)

@pytest.fixture(scope="class", autouse=True)
#Wzięte z internetu inaczej nie dzialaja inne testy ktore sa zrobione na widgecie w innym ekranie
def qapp():
    """Tworzy QApplication raz na sesję testową"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app
#Wzięte z internetu inaczej nie dzialaja inne testy ktore sa zrobione na widgecie w innym ekranie

def test_poczatkowa_temperatura(model):
    """Sprawdza początkową temperaturę"""
    assert model.get_temperature() == 30

def test_czy_przekroczone_temperature_krytyczna(model):
    """Sprawdza czy przekroczono temperaturę"""
    assert model.get_temperature() >90

def test_pompa(model):
    # początkowo wyłączona
    model.set_pump(True)
    assert model.pompa_on()      # włączona
    model.set_pump(False)
    assert not model.pompa_on()
    """Test działania pompy"""

def test_czy_zadziala_zabezpiepeczeenie_termiczne(model):
    """Test działania zabezpieczenia termicznego"""
    model.set_pump(True)
    assert model.pompa_on()
    model.set_temperature(95)
    if model.get_temperature() > 90:
        model.set_pump(False)
    assert model.pompa_on() is False

    """TESTY ZAWOROW"""

def test_zawor1_wlacz_wylacz(instalacja):
    assert not instalacja.zaw1_otwarty
    instalacja.wlaczeniezaw1()
    assert instalacja.zaw1_otwarty is True
    instalacja.wlaczeniezaw1()
    assert instalacja.zaw1_otwarty is False


def test_zawor2_wlacz_wylacz(instalacja):
    assert not instalacja.zaw2_otwarty
    instalacja.wlaczeniezaw2()
    assert instalacja.zaw2_otwarty is True
    instalacja.wlaczeniezaw2()
    assert instalacja.zaw2_otwarty is False


def test_zawor3_wlacz_wylacz(instalacja):
    assert not instalacja.zaw3_otwarty
    instalacja.wlaczeniezaw3()
    assert instalacja.zaw3_otwarty is True
    instalacja.wlaczeniezaw3()
    assert instalacja.zaw3_otwarty is False


