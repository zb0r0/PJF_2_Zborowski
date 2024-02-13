import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QApplication



class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomoc SCRUM")

        self.zadania = []

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWidget()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())
