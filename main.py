import sys
import sqlite3

from PySide6 import QtGui, QtCore
from PySide6.QtWidgets import (QMainWindow, QWidget, QApplication, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QMessageBox,
                               QHBoxLayout, QLabel, QComboBox, QListWidgetItem, QRadioButton, QButtonGroup, QDateEdit, QTabWidget, QTableWidgetItem, QTableWidget)
from collections import defaultdict

class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomoc SCRUM")

        self.conn_tasks = sqlite3.connect("tasks.db")
        self.cur_tasks = self.conn_tasks.cursor()

        self.conn_employees = sqlite3.connect("employees.db")
        self.cur_employees = self.conn_employees.cursor()

        self.cur_tasks.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, name TEXT, project TEXT, status TEXT, poker_points INTEGER)''')
        self.conn_tasks.commit()

        self.cur_employees.execute('''CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, imie TEXT, nazwisko TEXT)''')
        self.conn_employees.commit()

        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)

        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.central_widget.addTab(self.tab1, "Zadania")
        self.central_widget.addTab(self.tab2, "Zarządzanie pracownikami")

        self.layout1 = QVBoxLayout()
        self.tab1.setLayout(self.layout1)

        self.layout2 = QVBoxLayout()
        self.tab2.setLayout(self.layout2)

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

        self.wczytaj_projekty()

        self.status_label = QLabel("Status:")
        self.status_combobox = QComboBox()
        self.status_combobox.addItems(["Do zrobienia", "W trakcie", "Wykonane"])
        self.status_combobox.currentIndexChanged.connect(self.zmien_status)
        self.status_layout = QHBoxLayout()
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addWidget(self.status_combobox)

        self.layout1.addWidget(self.dodawanie_projektu)
        self.layout1.addWidget(self.dodaj_projekt_przycisk)
        self.layout1.addLayout(self.projekt_layout)
        self.layout1.addWidget(self.dodawanie_zadania)
        self.layout1.addWidget(self.dodaj_zadanie_przycisk)
        self.layout1.addWidget(self.lista_zadan)
        self.layout1.addWidget(self.usun_zadanie_przycisk)
        self.layout1.addLayout(self.status_layout)

        # Przyciski do pokera
        self.poker_planning_label = QLabel("Poker Planning:")
        self.poker_planning_layout = QHBoxLayout()
        self.poker_planning_layout.addWidget(self.poker_planning_label)

        self.poker_points_group = QButtonGroup()

        points_buttons = ["0", "0.5", "1", "2", "3", "5", "8", "13", "20", "40", "100"]
        for points in points_buttons:
            button = QRadioButton(points)
            self.poker_points_group.addButton(button)
            self.poker_planning_layout.addWidget(button)

        self.layout1.addLayout(self.poker_planning_layout)
        self.poker_points_group.buttonClicked.connect(self.handle_poker_points)

        # Zarządzanie pracownikami
        self.lista_pracownikow = QTableWidget()
        self.lista_pracownikow.setColumnCount(3)
        self.lista_pracownikow.setHorizontalHeaderLabels(["ID", "Imię", "Nazwisko"])
        self.wczytaj_pracownikow()

        self.layout2.addWidget(self.lista_pracownikow)

        self.imie_input = QLineEdit(placeholderText="Imie pracownika...")
        self.nazwisko_input = QLineEdit(placeholderText="Nazwisko pracownika...")
        dodaj_pracownika_przycisk = QPushButton("Dodaj pracownika")
        dodaj_pracownika_przycisk.clicked.connect(self.dodaj_pracownika)

        self.usun_pracownika_przycisk = QPushButton("Usuń pracownika")
        self.usun_pracownika_przycisk.clicked.connect(self.usun_pracownika)

        self.layout2.addWidget(self.imie_input)
        self.layout2.addWidget(self.nazwisko_input)
        self.layout2.addWidget(dodaj_pracownika_przycisk)
        self.layout2.addWidget(self.usun_pracownika_przycisk)

        # Generowanie raportu
        self.generuj_raport_button = QPushButton("Generuj raport")
        self.generuj_raport_button.clicked.connect(self.generuj_raport)

        # Pola wyboru pracownika i zakresu dat
        self.pracownik_label_raport = QLabel("Pracownik:")
        self.pracownik_combobox_raport = QComboBox()
        self.data_poczatkowa_label = QLabel("Data początkowa:")
        self.data_poczatkowa = QDateEdit()
        self.data_koncowa_label = QLabel("Data końcowa:")
        self.data_koncowa = QDateEdit()

        # Układ dla pól wyboru pracownika i zakresu dat oraz przycisku generowania raportu
        self.raport_layout = QHBoxLayout()
        self.raport_layout.addWidget(self.pracownik_label_raport)
        self.raport_layout.addWidget(self.pracownik_combobox_raport)
        self.raport_layout.addWidget(self.data_poczatkowa_label)
        self.raport_layout.addWidget(self.data_poczatkowa)
        self.raport_layout.addWidget(self.data_koncowa_label)
        self.raport_layout.addWidget(self.data_koncowa)
        self.raport_layout.addWidget(self.generuj_raport_button)

        self.layout2.addLayout(self.raport_layout)

        self.tab3 = QWidget()  # Nowa karta
        self.central_widget.addTab(self.tab3, "Przypisywanie pracowników do projektów")

        self.layout3 = QVBoxLayout()
        self.tab3.setLayout(self.layout3)

        self.pracownik_label = QLabel("Pracownik:")
        self.pracownik_combobox = QComboBox()
        self.projekt3_label = QLabel("Projekt:")
        self.projekt3_combobox = QComboBox()
        self.godziny_label = QLabel("Godziny pracy:")
        self.godziny_input = QLineEdit()
        self.data_label = QLabel("Data pracy:")
        self.data_edit = QDateEdit()

        self.dodaj_pracownika_do_projektu_przycisk = QPushButton("Dodaj godziny pracy")
        self.dodaj_pracownika_do_projektu_przycisk.clicked.connect(self.dodaj_pracownika_do_projektu)

        self.layout3.addWidget(self.pracownik_label)
        self.layout3.addWidget(self.pracownik_combobox)
        self.layout3.addWidget(self.projekt3_label)
        self.layout3.addWidget(self.projekt3_combobox)
        self.layout3.addWidget(self.godziny_label)
        self.layout3.addWidget(self.godziny_input)
        self.layout3.addWidget(self.data_label)
        self.layout3.addWidget(self.data_edit)
        self.layout3.addWidget(self.dodaj_pracownika_do_projektu_przycisk)

        self.conn_time_reports = sqlite3.connect("time_reports.db")
        self.cur_time_reports = self.conn_time_reports.cursor()

        self.cur_time_reports.execute('''CREATE TABLE IF NOT EXISTS time_reports(id INTEGER PRIMARY KEY, employee TEXT, project TEXT, hours INTEGER, date TEXT)''')
        self.conn_time_reports.commit()

        # Wywołanie funkcji wczytaj_pracownikow_do_projektu w __init__

        self.wczytaj_pracownikow()
        self.wczytaj_pracownikow_raport()
        self.wczytaj_pracownikow_do_projektu()
        self.wczytaj_projekty_do_projektu()

    def wczytaj_pracownikow_do_projektu(self):
        self.pracownik_combobox.clear()
        self.cur_employees.execute('''SELECT imie, nazwisko FROM employees''')
        pracownicy = self.cur_employees.fetchall()
        for pracownik in pracownicy:
            imie_nazwisko = f"{pracownik[0]} {pracownik[1]}"
            self.pracownik_combobox.addItem(imie_nazwisko)

    def wczytaj_projekty_do_projektu(self):
        self.projekt3_combobox.clear()
        self.cur_tasks.execute('''SELECT DISTINCT project FROM tasks''')
        projekty = self.cur_tasks.fetchall()
        for projekt in projekty:
            self.projekt3_combobox.addItem(projekt[0])

    def dodaj_pracownika_do_projektu(self):
        pracownik = self.pracownik_combobox.currentText()
        projekt = self.projekt3_combobox.currentText()
        godziny = self.godziny_input.text()
        data = self.data_edit.date().toString("yyyy-MM-dd")

        if pracownik and projekt and godziny and data:
            self.cur_time_reports.execute(
                '''INSERT INTO time_reports (employee, project, hours, date) VALUES (?, ?, ?, ?)''',
                (pracownik, projekt, godziny, data))
            self.conn_time_reports.commit()
            QMessageBox.information(self, "Sukces", "Pracownik został pomyślnie przypisany do projektu.")
            self.godziny_input.clear()
            self.data_edit.setDate(QtCore.QDate.currentDate())
        else:
            QMessageBox.warning(self, "Błąd", "Wypełnij wszystkie pola.")

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
            self.cur_tasks.execute('''INSERT INTO tasks (name, project, status, poker_points) VALUES (?, ?, ?, 0)''',
                             (zadanie_do_dodania, projekt, "Do zrobienia"))
            self.conn_tasks.commit()
            self.wczytaj_zadania()
            self.dodawanie_zadania.clear()
            self.wczytaj_projekty_do_projektu()
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
                self.cur_tasks.execute('''DELETE FROM tasks WHERE name = ? AND project = ?''', (name, projekt))
            elif len(zadanie_parts) == 2:
                self.cur_tasks.execute('''DELETE FROM tasks WHERE name = ? AND project IS NULL''', (name,))
            self.conn_tasks.commit()
            self.wczytaj_zadania()
            self.wczytaj_projekty()
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
                self.cur_tasks.execute('''UPDATE tasks SET status = ? WHERE name = ? AND project = ?''', (nowy_status, name, projekt))
            elif len(zadanie_parts) == 2:
                zadanie_nazwa = zadanie_parts[0]
                self.cur_tasks.execute('''UPDATE tasks SET status = ? WHERE name = ? AND project IS NULL''', (nowy_status, name))
            self.conn_tasks.commit()
            self.wczytaj_zadania()

    def wczytaj_projekty(self):
        self.projekt_combobox.clear()
        self.cur_tasks.execute('''SELECT DISTINCT project FROM tasks''')
        projekty = self.cur_tasks.fetchall()
        for projekt in projekty:
            self.projekt_combobox.addItem(projekt[0])

    def wczytaj_zadania(self):
        self.lista_zadan.clear()
        projekt = self.projekt_combobox.currentText()

        statuses = ["Do zrobienia", "W trakcie", "Wykonane"]
        for status in statuses:
            self.cur_tasks.execute('''SELECT name, poker_points FROM tasks WHERE project = ? AND status = ?''',
                                   (projekt, status))
            zadania = self.cur_tasks.fetchall()
            if zadania:
                column_header = QListWidgetItem(status)
                column_header.setFlags(column_header.flags() & ~QtCore.Qt.ItemIsSelectable)
                column_header.setBackground(QtGui.QColor("lightgray"))
                self.lista_zadan.addItem(column_header)

                for zadanie in zadania:
                    item = QListWidgetItem(f"{zadanie[0]} - {zadanie[1]}")
                    self.lista_zadan.addItem(item)

    def handle_poker_points(self, button):
        selected_item = self.lista_zadan.currentItem()
        if selected_item is not None:
            selected_task = selected_item.text()
            selected_task_parts = selected_task.split(" - ")
            name = f"{selected_task_parts[0]} - {selected_task_parts[1]}"
            projekt = selected_task_parts[1]
            poker_points = button.text() if button.isChecked() else "0"
            self.cur_tasks.execute('''UPDATE tasks SET poker_points = ? WHERE name = ? AND project = ?''',
                             (poker_points, name, projekt))
            self.conn_tasks.commit()
            QMessageBox.information(self, "Poker Planning",
                                    f"Zadanie: {selected_task}\n\nPunkty Poker Planning: {poker_points}")
            self.wczytaj_zadania()
        else:
            QMessageBox.warning(self, "Błąd", "Wybierz zadanie")

    def wczytaj_pracownikow(self):
        self.lista_pracownikow.setRowCount(0)
        self.cur_employees.execute('''SELECT * FROM employees''')
        pracownicy = self.cur_employees.fetchall()
        for row, pracownik in enumerate(pracownicy):
            self.lista_pracownikow.insertRow(row)
            for col, dane in enumerate(pracownik):
                item = QTableWidgetItem(str(dane))
                self.lista_pracownikow.setItem(row, col, item)

    def dodaj_pracownika(self):
        imie = self.imie_input.text()
        nazwisko = self.nazwisko_input.text()
        if imie and nazwisko:
            self.cur_employees.execute('''INSERT INTO employees (imie, nazwisko) VALUES (?, ?)''', (imie, nazwisko))
            self.conn_employees.commit()
            self.wczytaj_pracownikow()
            self.wczytaj_pracownikow_raport()
            self.wczytaj_pracownikow_do_projektu()
        else:
            QMessageBox.warning(self, "Błąd", "Wypełnij wszystkie pola")

    def usun_pracownika(self):
        zaznaczony_wiersz = self.lista_pracownikow.currentRow()
        if zaznaczony_wiersz != -1:
            id_pracownika = self.lista_pracownikow.item(zaznaczony_wiersz, 0).text()
            self.cur_employees.execute('''DELETE FROM employees WHERE id = ?''', (id_pracownika,))
            self.conn_employees.commit()
            self.wczytaj_pracownikow()
            self.wczytaj_pracownikow_raport()
        else:
            QMessageBox.warning(self, "Błąd", "Wybierz pracownika do usunięcia")

    def generuj_raport(self):
        pracownik = self.pracownik_combobox_raport.currentText()
        data_poczatkowa = self.data_poczatkowa.date().toString("yyyy-MM-dd")
        data_koncowa = self.data_koncowa.date().toString("yyyy-MM-dd")

        self.cur_time_reports.execute(
            '''SELECT project, hours FROM time_reports WHERE employee = ? AND date BETWEEN ? AND ?''',
            (pracownik, data_poczatkowa, data_koncowa))
        raport = self.cur_time_reports.fetchall()

        # Tworzenie słownika, w którym kluczem będzie nazwa projektu, a wartością suma godzin przepracowanych na projekcie
        raport_projektow = defaultdict(int)
        for projekt, godziny in raport:
            raport_projektow[projekt] += godziny

        # Wyświetlanie raportu
        raport_text = f"Raport dla pracownika: {pracownik}\n"
        raport_text += f"Data początkowa: {data_poczatkowa}, Data końcowa: {data_koncowa}\n\n"
        raport_text += "Projekt | Suma godzin\n"
        raport_text += "-" * 30 + "\n"
        for projekt, suma_godzin in raport_projektow.items():
            raport_text += f"{projekt} | {suma_godzin}\n"

        QMessageBox.information(self, "Raport", raport_text)

    def wczytaj_pracownikow_raport(self):
        self.pracownik_combobox_raport.clear()
        self.cur_employees.execute('''SELECT imie, nazwisko FROM employees''')
        pracownicy = self.cur_employees.fetchall()
        for pracownik in pracownicy:
            imie_nazwisko = f"{pracownik[0]} {pracownik[1]}"
            self.pracownik_combobox_raport.addItem(imie_nazwisko)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWidget()
    window.resize(700, 500)
    window.show()
    sys.exit(app.exec())
