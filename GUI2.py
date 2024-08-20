import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QSlider, QCheckBox, QRadioButton, 
                               QLineEdit, QGroupBox, QStackedWidget, QMessageBox, QGridLayout, QComboBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QMovie
import subprocess
import requests

class InstallationPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Install button
        install_btn = QPushButton("Install Sports2D")
        install_btn.setStyleSheet(self.custom_button_style("#4CAF50", "#FFFFFF"))
        install_btn.clicked.connect(self.install_package)
        install_btn.setFixedHeight(60)
        layout.addWidget(install_btn, 0, 0, 1, 2)

        # Remove button
        remove_btn = QPushButton("Remove Sports2D")
        remove_btn.setStyleSheet(self.custom_button_style("#F44336", "#FFFFFF"))
        remove_btn.clicked.connect(self.remove_package)
        remove_btn.setFixedHeight(60)
        layout.addWidget(remove_btn, 1, 0, 1, 2)

        # GPU checkbox
        self.gpu_checkbox = QCheckBox("Faster inference with GPU")
        self.gpu_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 16px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        layout.addWidget(self.gpu_checkbox, 2, 0, 1, 2)

        # Note message (always visible)
        note_message = QLabel(
            "Note: For faster inference, you can run on the GPU.\n"
            "Install pyTorch with CUDA and cuDNN support, and ONNX Runtime with GPU support (not available on MacOS).\n"
            "Be aware that GPU support takes an additional 6 GB on disk."
        )
        note_message.setWordWrap(True)
        note_message.setStyleSheet("color: #CCCCCC; font-size: 14px; margin-top: 10px;")
        note_message.setContentsMargins(0, 0, 0, 300)
        layout.addWidget(note_message, 3, 0, 1, 2)

        # Back button
        back_button = QPushButton("Back")
        back_button.setStyleSheet(self.custom_button_style("#555555", "#FFFFFF"))
        back_button.clicked.connect(self.main_window.show_main_panel)
        back_button.setFixedSize(100, 40)

        # Place the back button in the bottom-right corner
        layout.addWidget(back_button, 5, 1, 1, 1, Qt.AlignRight | Qt.AlignBottom)

    def custom_button_style(self, bg_color, font_color):
        return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {font_color};
            border-radius: 10px;
            border: none;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {self.lighten_color(bg_color)};
        }}
        QPushButton:pressed {{
            background-color: {self.darken_color(bg_color)};
        }}
        """

    @staticmethod
    def lighten_color(color):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        return f"#{min(int(r*1.2), 255):02x}{min(int(g*1.2), 255):02x}{min(int(b*1.2), 255):02x}"

    @staticmethod
    def darken_color(color):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        return f"#{int(r*0.8):02x}{int(g*0.8):02x}{int(b*0.8):02x}"

    def install_package(self):
        try:
            subprocess.run(["pip", "install", "git+https://github.com/hunminkim98/Sports2D.git"], check=True)
            if self.gpu_checkbox.isChecked():
                subprocess.run(["pip3", "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu124"], check=True)
                subprocess.run(["pip", "install", "onnxruntime-gpu"], check=True)
            QMessageBox.information(self, "Success", "Sports2D package installed successfully.")
        except subprocess.CalledProcessError:
            QMessageBox.warning(self, "Error", "Failed to install Sports2D package.")

    def remove_package(self):
        try:
            subprocess.run(["pip", "uninstall", "Sports2D", "-y"], check=True)
            if self.gpu_checkbox.isChecked():
                subprocess.run(["pip", "uninstall", "torch", "torchvision", "torchaudio", "onnxruntime-gpu", "-y"], check=True)
            QMessageBox.information(self, "Success", "Sports2D package removed successfully.")
        except subprocess.CalledProcessError:
            QMessageBox.warning(self, "Error", "Failed to remove Sports2D package.")

class MainPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout(self)

        # Label
        label = QLabel("Compute 2D joint and segment angles of your athletes and patients from real-time video streams or video files!")
        label.setFixedHeight(60)
        label.setStyleSheet(self.main_window.label_style())
        layout.addWidget(label)

        # Download the GIF from GitHub
        gif_url = "https://raw.githubusercontent.com/davidpagnon/Sports2D/main/Content/demo_gif.gif"
        gif_data = requests.get(gif_url).content
        # Save GIF to a temporary file
        gif_path = "temp_gif.gif"
        with open(gif_path, "wb") as gif_file:
            gif_file.write(gif_data)

        # Add the GIF animation
        gif_label = QLabel(self)
        gif_label.setFixedSize(1000, 600)  # Set the fixed size for the QLabel

        gif_movie = QMovie(gif_path)
        gif_movie.setScaledSize(QSize(1000, 600))  # Set the size for the QMovie
        gif_label.setMovie(gif_movie)
        gif_movie.start()  # Start the GIF animation
        layout.addWidget(gif_label)

        # Ensure the temporary file is deleted when the program closes
        self.gif_path = gif_path

        # Slider 1 & 2
        for _ in range(2):
            slider = QSlider(Qt.Horizontal)
            slider.setStyleSheet(self.main_window.slider_style())
            layout.addWidget(slider)

        # Checkbox layout
        checkbox_layout = QHBoxLayout()
        disabled_checkbox = QCheckBox("CheckBox disabled")
        disabled_checkbox.setEnabled(False)
        enabled_checkbox = QCheckBox("CTkCheckBox")
        enabled_checkbox.setChecked(True)
        for cb in (disabled_checkbox, enabled_checkbox):
            cb.setStyleSheet(self.main_window.checkbox_style())
            checkbox_layout.addWidget(cb)
        layout.addLayout(checkbox_layout)

        # Entry (QLineEdit)
        line_edit = QLineEdit("CTkEntry")
        line_edit.setStyleSheet(self.main_window.entry_style())
        layout.addWidget(line_edit)

        # Radio buttons
        radio_group = QGroupBox("CTkRadioButton Group:")
        radio_layout = QVBoxLayout()
        for i in range(3):
            rb = QRadioButton(f"CTkRadioButton {i+1}")
            rb.setStyleSheet(self.main_window.radio_button_style())
            radio_layout.addWidget(rb)
        radio_group.setLayout(radio_layout)
        layout.addWidget(radio_group)

        # Bottom buttons
        bottom_button_layout = QHBoxLayout()
        button_texts = ["Disabled Button", "CTkButton", "CTkButton"]
        for text in button_texts:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.setStyleSheet(self.main_window.button_style())
            if text == "Disabled Button":
                btn.setEnabled(False)
            bottom_button_layout.addWidget(btn)
        layout.addLayout(bottom_button_layout)

class CustomStyleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sports2D")
        self.setGeometry(100, 100, 800, 600)
        self.current_theme = "Dark"

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left side layout
        left_widget = QWidget()
        left_widget.setFixedWidth(200)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(10, 10, 10, 10)

        # Sports2D Title
        title_label = QLabel("Sports2D")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_label.setContentsMargins(40, 0, 0, 10)
        left_layout.addWidget(title_label)

        # Buttons
        btn_texts = ["Installation", "Real-time Analysis", "Video Analysis", "Settings"]
        for text in btn_texts:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.setStyleSheet(self.button_style())
            left_layout.addWidget(btn)
            if text == "Installation":
                btn.clicked.connect(self.show_installation_panel)

        left_layout.addStretch(1)

        # Appearance Mode
        appearance_label = QLabel("Appearance Mode")
        appearance_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        appearance_label.setContentsMargins(22, 0, 0, 0)
        left_layout.addWidget(appearance_label)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "White"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        left_layout.addWidget(self.theme_combo)

        main_layout.addWidget(left_widget)

        # Right side stacked widget
        self.right_stack = QStackedWidget()
        main_layout.addWidget(self.right_stack)

        self.main_panel = MainPanel(self)
        self.right_stack.addWidget(self.main_panel)

        self.apply_theme()

    def show_installation_panel(self):
        self.installation_panel = InstallationPanel(self)
        self.right_stack.addWidget(self.installation_panel)
        self.right_stack.setCurrentWidget(self.installation_panel)

    def show_main_panel(self):
        self.right_stack.setCurrentWidget(self.main_panel)

    def change_theme(self, theme):
        self.current_theme = theme
        self.apply_theme()

    def apply_theme(self):
        if self.current_theme == "Dark":
            self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2B2B2B;
                color: #FFFFFF;
            }
            QGroupBox {
                border: 1px solid #555555;
                margin-top: 0.5em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            """)
        else:  # White theme
            self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #FFFFFF;
                color: #000000;
            }
            QGroupBox {
                border: 1px solid #CCCCCC;
                margin-top: 0.5em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            """)
        
        # Update all widgets to reflect the new theme
        self.main_panel.setStyleSheet(self.main_panel.styleSheet())
        if hasattr(self, 'installation_panel'):
            self.installation_panel.setStyleSheet(self.installation_panel.styleSheet())

    def button_style(self, color=None):
        if self.current_theme == "Dark":
            return """
            QPushButton {
                background-color: #333333;
                color: white;
                border-radius: 10px;
                border: 5px solid #555555;
                padding: 5px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton:pressed {
                background-color: #222222;
            }
            QPushButton:disabled {
                background-color: #2A2A2A;
                color: #666666;
                border: 2px solid #444444;
            }
            """
        else:
            return """
            QPushButton {
                background-color: #E0E0E0;
                color: black;
                border-radius: 10px;
                border: 2px solid #CCCCCC;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
            QPushButton:pressed {
                background-color: #C0C0C0;
            }
            QPushButton:disabled {
                background-color: #F0F0F0;
                color: #999999;
                border: 2px solid #DDDDDD;
            }
            """

    def label_style(self):
        if self.current_theme == "Dark":
            return """
            QLabel {
                color: #FFFFFF;
                background-color: #3E3E3E;
                padding: 10px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            """
        else:
            return """
            QLabel {
                color: #333333;
                background-color: #F0F0F0;
                padding: 10px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            """

    def slider_style(self):
        if self.current_theme == "Dark":
            return """
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: #3E3E3E;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #3A82E4;
                border: 1px solid #777;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4A4A4A;
                border: 1px solid #3E3E3E;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            """
        else:
            return """
            QSlider::groove:horizontal {
                border: 1px solid #999;
                background: #F0F0F0;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #3A82E4;
                border: 1px solid #777;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #FFFFFF;
                border: 1px solid #999999;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            """

    def checkbox_style(self):
        if self.current_theme == "Dark":
            return """
            QCheckBox {
                color: #CCCCCC;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #3A82E4;
                border: 1px solid #555;
                border-radius: 5px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #3E3E3E;
                border: 1px solid #555;
                border-radius: 5px;
            }
            QCheckBox::indicator:disabled {
                background-color: #555555;
                border: 1px solid #777;
                border-radius: 5px;
            }
            """
        else:
            return """
            QCheckBox {
                color: #333333;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #3A82E4;
                border: 1px solid #999;
                border-radius: 5px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #FFFFFF;
                border: 1px solid #999;
                border-radius: 5px;
            }
            QCheckBox::indicator:disabled {
                background-color: #DDDDDD;
                border: 1px solid #BBBBBB;
                border-radius: 5px;
            }
            """

    def entry_style(self):
        if self.current_theme == "Dark":
            return """
            QLineEdit {
                background-color: #3E3E3E;
                color: #CCCCCC;
                border: 2px solid #555555;
                border-radius: 10px;
                padding: 5px;
            }
            """
        else:
            return """
            QLineEdit {
                background-color: #FFFFFF;
                color: #333333;
                border: 2px solid #CCCCCC;
                border-radius: 10px;
                padding: 5px;
            }
            """
        
    def radio_button_style(self):
        if self.current_theme == "Dark":
            return """
            QRadioButton {
                color: #CCCCCC;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator::checked {
                background-color: #3A82E4;
                border: 1px solid #555555;
                border-radius: 10px;
            }
            QRadioButton::indicator::unchecked {
                background-color: #3E3E3E;
                border: 1px solid #555555;
                border-radius: 10px;
            }
            """
        else:
            return """
            QRadioButton {
                color: #333333;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator::checked {
                background-color: #3A82E4;
                border: 1px solid #999999;
                border-radius: 10px;
            }
            QRadioButton::indicator::unchecked {
                background-color: #FFFFFF;
                border: 1px solid #999999;
                border-radius: 10px;
            }
            """

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = CustomStyleWindow()
    window.show()

    sys.exit(app.exec())