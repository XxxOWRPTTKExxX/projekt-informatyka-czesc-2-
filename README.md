# projekt-informatyka_Instalacja Centralnego Ogrzewania

Na pomysl wpadlem samodzielnie, ponieważ sami w domu aktualnie robimy rennowacje CO. Aplikacja symulującą działanie uproszczonej instalacji centralnego ogrzewania. Program posiada współpracę miedzy elementami.
Piec:
-regulacja temperatury (20-100 stopni)
-Wizualny termometr
-Automatyczne zabezpieczenia:
    -Automatyczna blokada pompy poniżej 30. stopni
    -Zabezpieczenie termiczne i wyłączenie. pompy powyzej 90 stopni
-Symulacja narastanie popiołu
 -Reczne opróżnianie popiołu

Pompa:
-Zabezpieczenia jak w/w
-Animacia pracy pompy
-Wylaczenie gdy popioł osiagnie 100%

Instalacja hydrauliczna:
-Wizualny schemat rur
- Kolory rur sygnalizujące czy jest przepływ
- Bojler z dynamicznym napełnianiem
-Zawor awaryjny(spust)
-Trzy niezależne obiegi wody

Zawory:
-Zawór spustu/bezpieczeństwa
-3 zawory obiegów grzewczych
-Kolorystyka sygnalizujące stan(otwarcia/zamkniecia) zaworów

Przepływ:
-Obliczany dynamicznie na podstawie ilości otwartych zaworów obiegu:
    -3 otwarte obiegi 100%           
    -2 otwarte obiegi 66%           
    -1 otwarty obiegi 33% 
    informacja ta jest wyświetlana na ekranie głównym

Projekt wykorzystuje dodatkowo model danych, który umożliwił mi przekazywanie informacji pomierzy ekranami. Użyto również pyqtSignal, aby móc od razu wysyłać sygnał przy każdej zmianie.

Program posiada 3 ekrany:
- Informacyjny
- Z wizualizacja pieca
- Z wizualizacja instalacji





