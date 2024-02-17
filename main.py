import sys
import sqlite3

from PySide6 import QtGui, QtCore
from PySide6.QtWidgets import QMainWindow, QWidget, QApplication, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QMessageBox, QHBoxLayout, QLabel, QComboBox, QListWidgetItem

class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomoc SCRUM")

        self.conn = sqlite3.connect("tasks.db")
        self.cur = self.conn.cursor()

        self.cur.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, name TEXT, project TEXT, status TEXT)''')
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

        self.usun_zadanie_przycisk = QPushButton('Usuń zadanie')
        self.usun_zadanie_przycisk.clicked.connect(self.usun_zadanie)

        self.status_label = QLabel("Status:")
        self.status_combobox = QComboBox()
        self.status_combobox.addItems(["Do zrobienia", "W trakcie", "Wykonane"])
        self.status_combobox.currentIndexChanged.connect(self.zmien_status)
        self.status_layout = QHBoxLayout()
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addWidget(self.status_combobox)

        self.layout.addWidget(self.dodawanie_projektu)
        self.layout.addWidget(self.dodaj_projekt_przycisk)
        self.layout.addLayout(self.projekt_layout)
        self.layout.addWidget(self.dodawanie_zadania)
        self.layout.addWidget(self.dodaj_zadanie_przycisk)
        self.layout.addWidget(self.lista_zadan)
        self.layout.addWidget(self.usun_zadanie_przycisk)
        self.layout.addLayout(self.status_layout)

        self.poker_planning_label = QLabel("Poker Planning:")
        self.poker_planning_edit = QLineEdit()
        self.poker_planning_layout = QHBoxLayout()
        self.poker_planning_layout.addWidget(self.poker_planning_label)
        self.poker_planning_layout.addWidget(self.poker_planning_edit)

        self.poker_planning_button = QPushButton("Start Poker Planning")
        self.poker_planning_button.clicked.connect(self.start_poker_planning)

        self.layout.addLayout(self.poker_planning_layout)
        self.layout.addWidget(self.poker_planning_button)

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
            zadanie_do_dodania = f"{zadanie_nazwa} - {projekt}"
            self.cur.execute('''INSERT INTO tasks (name, project, status) VALUES (?, ?, ?)''',
                             (zadanie_do_dodania, projekt, "Do zrobienia"))
            self.conn.commit()
            self.wczytaj_zadania()
            self.dodawanie_zadania.clear()
        else:
            QMessageBox.warning(self, "Błąd", "Nazwa zadania nie może być pusta")

    def usun_zadanie(self):
        zaznaczone_zadanie = self.lista_zadan.currentItem()
        if zaznaczone_zadanie is not None:
            zadanie_text = zaznaczone_zadanie.text()
            zadanie_parts = zadanie_text.split(" - ")
            name = f"{zadanie_parts[0]} - {zadanie_parts[1]}"
            projekt = zadanie_parts[1]
            if len(zadanie_parts) == 3:
                self.cur.execute('''DELETE FROM tasks WHERE name = ? AND project = ?''', (name, projekt))
            elif len(zadanie_parts) == 2:
                self.cur.execute('''DELETE FROM tasks WHERE name = ? AND project IS NULL''', (name,))
            self.conn.commit()
            self.wczytaj_zadania()
        else:
            QMessageBox.warning(self, "Błąd", "Wybierz zadanie do usunięcia")

    def zmien_status(self):
        zaznaczone_zadanie = self.lista_zadan.currentItem()
        if zaznaczone_zadanie is not None:
            nowy_status = self.status_combobox.currentText()
            zadanie_text = zaznaczone_zadanie.text()
            zadanie_parts = zadanie_text.split(" - ")
            name = f"{zadanie_parts[0]} - {zadanie_parts[1]}"
            projekt = zadanie_parts[1]
            if len(zadanie_parts) == 3:
                self.cur.execute('''UPDATE tasks SET status = ? WHERE name = ? AND project = ?''', (nowy_status, name, projekt))
            elif len(zadanie_parts) == 2:
                zadanie_nazwa = zadanie_parts[0]
                self.cur.execute('''UPDATE tasks SET status = ? WHERE name = ? AND project IS NULL''', (nowy_status, name))
            self.conn.commit()
            self.wczytaj_zadania()

    def wczytaj_projekty(self):
        self.projekt_combobox.clear()
        self.cur.execute('''SELECT DISTINCT project FROM tasks''')
        projekty = self.cur.fetchall()
        for projekt in projekty:
            self.projekt_combobox.addItem(projekt[0])

    def start_poker_planning(self):
        selected_item = self.lista_zadan.currentItem()
        if selected_item is not None:
            poker_points = self.poker_planning_edit.text()
            if poker_points.strip():
                selected_task = selected_item.text()
                selected_task_parts = selected_task.split(" - ")
                name = f"{selected_task_parts[0]} - {selected_task_parts[1]}"
                projekt = selected_task_parts[1]
                self.cur.execute('''UPDATE tasks SET poker_points = ? WHERE name = ? AND project = ?''',
                                 (poker_points, name, projekt))
                self.conn.commit()
                QMessageBox.information(self, "Poker Planning",
                                        f"Zadanie: {selected_task}\n\nPunkty Poker Planning: {poker_points}")
                self.poker_planning_edit.clear()
            else:
                QMessageBox.warning(self, "Błąd", "Podaj punkty Poker Planning")
        else:
            QMessageBox.warning(self, "Błąd", "Wybierz zadanie")
        self.wczytaj_zadania()

    def wczytaj_zadania(self):

        self.lista_zadan.clear()
        projekt = self.projekt_combobox.currentText()

        statuses = ["Do zrobienia", "W trakcie", "Wykonane"]
        for status in statuses:
            self.cur.execute('''SELECT name, poker_points FROM tasks WHERE project = ? AND status = ?''', (projekt, status))
            zadania = self.cur.fetchall()
            if zadania:
                column_header = QListWidgetItem(status)
                column_header.setFlags(column_header.flags() & ~QtCore.Qt.ItemIsSelectable)
                column_header.setBackground(QtGui.QColor("lightgray"))
                self.lista_zadan.addItem(column_header)

                for zadanie in zadania:
                    item = QListWidgetItem(f"{zadanie[0]} - {zadanie[1]}")
                    self.lista_zadan.addItem(item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWidget()
    window.resize(700, 500)
    window.show()
    sys.exit(app.exec())
