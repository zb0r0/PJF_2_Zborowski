import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QApplication, QVBoxLayout, QLineEdit, QPushButton, QListWidget



class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomoc SCRUM")

        self.zadania = []

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.dodawanie_zadania = QLineEdit()
        self.dodaj_zadanie_przycisk = QPushButton("Dodaj zadanie")
        self.dodaj_zadanie_przycisk.clicked.connect(self.dodaj_zadanie)

        self.dodawanie_zadania = QListWidget()

        self.usun_zadanie_przycisk = QPushButton('Usun zadanie')
        self.usun_zadanie_przycisk.clicked.connect(self.usun_zadanie)

        self.layout.addWidget(self.dodawanie_zadania)
        self.layout.addWidget(self.dodaj_zadanie_przycisk)
        self.layout.addWidget(self.zadania)
        self.layout.addWidget(self.usun_zadanie_przycisk)

    def dodaj_zadanie(self):
        pass

    def usun_zadanie(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWidget()
    window.resize(700, 500)
    window.show()
    sys.exit(app.exec())
