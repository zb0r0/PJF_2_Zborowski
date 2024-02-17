import sys
import sqlite3
from PySide6.QtWidgets import QMainWindow, QWidget, QApplication, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QMessageBox, QHBoxLayout, QLabel, QComboBox


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomoc SCRUM")

        # Połączenie z bazą danych SQLite
        self.conn = sqlite3.connect("tasks.db")
        self.cur = self.conn.cursor()

        # Tworzenie tabeli tasks, jeśli nie istnieje
        self.cur.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, name TEXT, project TEXT)''')
        self.conn.commit()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.dodawanie_projektu = QLineEdit(placeholderText="Dodaj nowy projekt...")
        self.dodaj_projekt_przycisk = QPushButton("Dodaj projekt")
        self.dodaj_projekt_przycisk.clicked.connect(self.dodaj_projekt)

        self.projekt_label = QLabel("Projekt:")
        self.projekt_combobox = QComboBox()
        self.projekt_combobox.currentIndexChanged.connect(self.wczytaj_zadania)
        self.projekt_layout = QHBoxLayout()
        self.projekt_layout.addWidget(self.projekt_label)
        self.projekt_layout.addWidget(self.projekt_combobox)

        self.dodawanie_zadania = QLineEdit(placeholderText="Dodaj nowe zadanie...")
        self.dodaj_zadanie_przycisk = QPushButton("Dodaj zadanie")
        self.dodaj_zadanie_przycisk.clicked.connect(self.dodaj_zadanie)

        self.lista_zadan = QListWidget()

        self.usun_zadanie_przycisk = QPushButton('Usun zadanie')
        self.usun_zadanie_przycisk.clicked.connect(self.usun_zadanie)

        self.layout.addWidget(self.dodawanie_projektu)
        self.layout.addWidget(self.dodaj_projekt_przycisk)
        self.layout.addLayout(self.projekt_layout)
        self.layout.addWidget(self.dodawanie_zadania)
        self.layout.addWidget(self.dodaj_zadanie_przycisk)
        self.layout.addWidget(self.lista_zadan)
        self.layout.addWidget(self.usun_zadanie_przycisk)

        # Wczytaj projekty z bazy danych i dodaj je do listy
        self.wczytaj_projekty()

    def dodaj_projekt(self):
        projekt_nazwa = self.dodawanie_projektu.text()
        if projekt_nazwa:
            self.projekt_combobox.addItem(projekt_nazwa)
            self.dodawanie_projektu.clear()
        else:
            QMessageBox.warning(self, "Błąd", "Nazwa projektu nie może być pusta")

    def dodaj_zadanie(self):
        zadanie_nazwa = self.dodawanie_zadania.text()
        projekt = self.projekt_combobox.currentText()
        if zadanie_nazwa:
            zadanie_do_dodania = f"{zadanie_nazwa} - {projekt}"  # Dodanie separatora między zadaniem a projektem
            self.cur.execute('''INSERT INTO tasks (name, project) VALUES (?, ?)''', (zadanie_do_dodania, projekt))
            self.conn.commit()
            self.wczytaj_zadania()  # Odśwież listę zadań
            self.dodawanie_zadania.clear()
        else:
            QMessageBox.warning(self, "Błąd", "Nazwa zadania nie może być pusta")

    def usun_zadanie(self):
        zaznaczone_zadanie = self.lista_zadan.currentItem()
        if zaznaczone_zadanie is not None:
            zadanie_text = zaznaczone_zadanie.text()
            zadanie_parts = zadanie_text.split(" - ")
            if len(zadanie_parts) == 2:
                zadanie_nazwa, projekt = zadanie_parts
                self.cur.execute('''DELETE FROM tasks WHERE name = ? AND project = ?''', (zadanie_text, projekt))
                print(zadanie_nazwa, projekt)
            elif len(zadanie_parts) == 1:
                zadanie_nazwa = zadanie_parts[0]
                self.cur.execute('''DELETE FROM tasks WHERE name = ? AND project IS NULL''', (zadanie_nazwa,))

            self.conn.commit()
            self.wczytaj_zadania()  # Odśwież listę zadań
        else:
            QMessageBox.warning(self, "Błąd", "Wybierz zadanie do usunięcia")

    def wczytaj_projekty(self):
        self.cur.execute('''SELECT DISTINCT project FROM tasks''')
        projekty = self.cur.fetchall()
        for projekt in projekty:
            self.projekt_combobox.addItem(projekt[0])

    def wczytaj_zadania(self):
        self.lista_zadan.clear()
        projekt = self.projekt_combobox.currentText()
        self.cur.execute('''SELECT name FROM tasks WHERE project = ?''', (projekt,))
        zadania = self.cur.fetchall()
        for zadanie in zadania:
            self.lista_zadan.addItem(zadanie[0])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWidget()
    window.resize(700, 500)
    window.show()
    sys.exit(app.exec())
