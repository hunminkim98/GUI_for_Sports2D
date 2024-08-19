import sys
import os
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtCore import Qt

class MinicondaInstaller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Sports2D Environment Setup')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.info_label = QLabel("Setup Sports2D Environment", self)
        layout.addWidget(self.info_label, alignment=Qt.AlignCenter)

        self.check_conda_btn = QPushButton('Check Miniconda & Setup Environment', self)
        self.check_conda_btn.clicked.connect(self.check_and_setup_environment)
        layout.addWidget(self.check_conda_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def check_and_setup_environment(self):
        if not self.is_conda_installed():
            self.prompt_miniconda_installation()
        else:
            self.setup_environment()

    def is_conda_installed(self):
        try:
            subprocess.run(["conda", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def prompt_miniconda_installation(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Miniconda Not Found")
        msg_box.setText("Miniconda is not installed on this system. Please install it from the official website.")
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        install_button = msg_box.button(QMessageBox.Ok)
        install_button.setText("Download Miniconda")

        if msg_box.exec_() == QMessageBox.Ok:
            os.system("start https://docs.conda.io/en/latest/miniconda.html")

    def setup_environment(self):
        try:
            subprocess.run(["conda", "create", "-n", "Sports2D", "python=3.10", "-y"], check=True)
            if os.name == 'nt':
                activate_command = "conda activate Sports2D && pip install sports2d"
                subprocess.run(["cmd", "/c", activate_command], check=True)
            else:
                subprocess.run(["conda", "activate", "Sports2D"], shell=True)
                subprocess.run(["pip", "install", "sports2d"], shell=True)

            QMessageBox.information(self, "Success", "Sports2D environment setup completed successfully.")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    installer = MinicondaInstaller()
    installer.show()
    sys.exit(app.exec())
