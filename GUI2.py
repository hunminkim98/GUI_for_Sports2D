import os
import sys
import toml
import subprocess
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QPushButton, QLabel, QSlider, QCheckBox, QRadioButton, 
                               QLineEdit, QGroupBox, QStackedWidget, QMessageBox, QGridLayout, QStyle,
                               QComboBox, QToolButton, QSpinBox, QDoubleSpinBox, QScrollArea, QFormLayout, QListWidget)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QMovie, QIcon, QFontMetrics, QFont

def find_config_file():
    try:
        import Sports2D
        package_dir = os.path.dirname(Sports2D.__file__)
        config_path = os.path.join(package_dir, 'Demo', 'Config_demo.toml')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found at {config_path}")
        return config_path
    except (ImportError, KeyError, FileNotFoundError) as e:
        print(f"Error: {e}")
        config_path = input("Please enter the full path to the Config_demo.toml file: ")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found at {config_path}")
        return config_path

class CollapsibleGroupBox(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)

        self.toggle_button = QPushButton(title)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                text-align: Middle;
                padding: 10px;
                border: none;
                background-color: #2C3E50;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 5px;
                border: 2px solid #34495E;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
            QPushButton:pressed {
                background-color: #2C3E50;
                border: 2px solid #2980B9;
            }
        """)
        self.toggle_button.setIcon(self.style().standardIcon(QStyle.SP_ToolBarHorizontalExtensionButton))
        self.toggle_button.clicked.connect(self.toggle_content)

        self.content_area = QWidget()
        self.content_area.setMaximumHeight(0)
        self.content_area.setStyleSheet("""
            background-color: #34495E;
            border-radius: 5px;
            padding: 10px;
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.content_area)
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.content_layout = QVBoxLayout(self.content_area)

    def toggle_content(self):
        collapsed_height = self.sizeHint().height() - self.content_area.maximumHeight()
        content_height = self.content_layout.sizeHint().height()
        
        if self.content_area.maximumHeight() == 0:
            self.animation.setStartValue(collapsed_height)
            self.animation.setEndValue(collapsed_height + content_height)
            self.toggle_button.setIcon(self.style().standardIcon(QStyle.SP_ToolBarVerticalExtensionButton))
        else:
            self.animation.setStartValue(collapsed_height + content_height)
            self.animation.setEndValue(collapsed_height)
            self.toggle_button.setIcon(self.style().standardIcon(QStyle.SP_ToolBarHorizontalExtensionButton))
        
        self.animation.start()

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

class SettingsPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.config_path = find_config_file()
        self.config_data = self.load_config()
        self.setup_ui()

    def load_config(self):
        return toml.load(self.config_path)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Basic Settings
        basic_group = CollapsibleGroupBox("Basic Settings")
        basic_layout = QVBoxLayout()

        # Pose Settings
        pose_layout = QVBoxLayout()
        self.display_detection_checkbox = QCheckBox("Display Detection")
        self.display_detection_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        self.display_detection_checkbox.setChecked(self.config_data['pose']['display_detection'])
        pose_layout.addWidget(self.display_detection_checkbox)

        time_range_label = QLabel("Time Range:")
        time_range_label.setStyleSheet("color: white; font-size: 14px;")
        time_range_layout = QHBoxLayout()
        self.time_range_start = QLineEdit(str(self.config_data['pose']['time_range'][0]) if self.config_data['pose']['time_range'] else "")
        self.time_range_end = QLineEdit(str(self.config_data['pose']['time_range'][1]) if self.config_data['pose']['time_range'] else "")
        for widget in (self.time_range_start, self.time_range_end):
            widget.setStyleSheet("""
                QLineEdit {
                    background-color: #2C3E50;
                    color: white;
                    border: 1px solid #34495E;
                    padding: 5px;
                    border-radius: 3px;
                }
            """)
        time_range_layout.addWidget(self.time_range_start)
        time_range_layout.addWidget(QLabel("-", styleSheet="color: white;"))
        time_range_layout.addWidget(self.time_range_end)
        pose_layout.addWidget(time_range_label)
        pose_layout.addLayout(time_range_layout)

        basic_layout.addLayout(pose_layout)

        # Compute Angles Settings
        angles_layout = QVBoxLayout()
        joint_angles_label = QLabel("Select Joint Angles:")
        joint_angles_label.setStyleSheet("color: white; font-size: 14px;")
        angles_layout.addWidget(joint_angles_label)
        self.joint_angles_list = QListWidget()
        self.joint_angles_list.setStyleSheet("""
            QListWidget {
                background-color: #2C3E50;
                color: white;
                border: 1px solid #34495E;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #3498DB;
            }
        """)
        self.joint_angles_list.setSelectionMode(QListWidget.MultiSelection)
        self.joint_angles_list.addItems([
            'Right ankle', 'Left ankle', 'Right knee', 'Left knee', 'Right hip',
            'Left hip', 'Right shoulder', 'Left shoulder', 'Right elbow', 'Left elbow',
            'Right wrist', 'Left wrist'
        ])
        for i in range(self.joint_angles_list.count()):
            item = self.joint_angles_list.item(i)
            if item.text() in self.config_data['compute_angles']['joint_angles']:
                item.setSelected(True)
        angles_layout.addWidget(self.joint_angles_list)

        segment_angles_label = QLabel("Select Segment Angles:")
        segment_angles_label.setStyleSheet("color: white; font-size: 14px;")
        angles_layout.addWidget(segment_angles_label)
        self.segment_angles_list = QListWidget()
        self.segment_angles_list.setStyleSheet("""
            QListWidget {
                background-color: #2C3E50;
                color: white;
                border: 1px solid #34495E;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #3498DB;
            }
        """)
        self.segment_angles_list.setSelectionMode(QListWidget.MultiSelection)
        self.segment_angles_list.addItems([
            'Right foot', 'Left foot', 'Right shank', 'Left shank', 'Right thigh',
            'Left thigh', 'Trunk', 'Right arm', 'Left arm', 'Right forearm',
            'Left forearm', 'Right hand', 'Left hand'
        ])
        for i in range(self.segment_angles_list.count()):
            item = self.segment_angles_list.item(i)
            if item.text() in self.config_data['compute_angles']['segment_angles']:
                item.setSelected(True)
        angles_layout.addWidget(self.segment_angles_list)

        basic_layout.addLayout(angles_layout)
        basic_group.setLayout(basic_layout)
        scroll_layout.addWidget(basic_group)

        # Advanced Pose Settings
        advanced_pose_group = CollapsibleGroupBox("Advanced Pose Settings")
        advanced_pose_layout = QFormLayout()
        advanced_pose_layout.setVerticalSpacing(10)

        self.webcam_id = QSpinBox()
        self.webcam_id.setStyleSheet(self.spinbox_style())
        self.webcam_id.setValue(self.config_data['pose_advanced']['webcam_id'])
        advanced_pose_layout.addRow(self.create_label("Webcam ID:"), self.webcam_id)

        self.input_size = QLineEdit(str(self.config_data['pose_advanced']['input_size']))
        self.input_size.setStyleSheet(self.lineedit_style())
        advanced_pose_layout.addRow(self.create_label("Input Size:"), self.input_size)

        self.overwrite_pose = QCheckBox()
        self.overwrite_pose.setStyleSheet(self.checkbox_style())
        self.overwrite_pose.setChecked(self.config_data['pose_advanced']['overwrite_pose'])
        advanced_pose_layout.addRow(self.create_label("Overwrite Pose:"), self.overwrite_pose)

        self.det_frequency = QSpinBox()
        self.det_frequency.setStyleSheet(self.spinbox_style())
        self.det_frequency.setValue(self.config_data['pose_advanced']['det_frequency'])
        advanced_pose_layout.addRow(self.create_label("Detection Frequency:"), self.det_frequency)

        self.mode = QComboBox()
        self.mode.setStyleSheet(self.combobox_style())
        self.mode.addItems(["lightweight", "balanced", "performance"])
        self.mode.setCurrentText(self.config_data['pose_advanced']['mode'])
        advanced_pose_layout.addRow(self.create_label("Mode:"), self.mode)

        self.keypoints_threshold = QDoubleSpinBox()
        self.keypoints_threshold.setStyleSheet(self.spinbox_style())
        self.keypoints_threshold.setRange(0, 1)
        self.keypoints_threshold.setSingleStep(0.1)
        self.keypoints_threshold.setValue(self.config_data['pose_advanced']['keypoints_threshold'])
        advanced_pose_layout.addRow(self.create_label("Keypoints Threshold:"), self.keypoints_threshold)

        advanced_pose_group.setLayout(advanced_pose_layout)
        scroll_layout.addWidget(advanced_pose_group)

        # Advanced Angles Settings
        advanced_angles_group = CollapsibleGroupBox("Advanced Angles Settings")
        advanced_angles_layout = QFormLayout()
        advanced_angles_layout.setVerticalSpacing(10)

        self.show_angles_on_img = QCheckBox()
        self.show_angles_on_img.setStyleSheet(self.checkbox_style())
        self.show_angles_on_img.setChecked(self.config_data['compute_angles_advanced']['show_angles_on_img'])
        advanced_angles_layout.addRow(self.create_label("Show Angles on Image:"), self.show_angles_on_img)

        self.show_angles_on_vid = QCheckBox()
        self.show_angles_on_vid.setStyleSheet(self.checkbox_style())
        self.show_angles_on_vid.setChecked(self.config_data['compute_angles_advanced']['show_angles_on_vid'])
        advanced_angles_layout.addRow(self.create_label("Show Angles on Video:"), self.show_angles_on_vid)

        self.filter_checkbox = QCheckBox()
        self.filter_checkbox.setStyleSheet(self.checkbox_style())
        self.filter_checkbox.setChecked(self.config_data['compute_angles_advanced']['filter'])
        advanced_angles_layout.addRow(self.create_label("Apply Filter:"), self.filter_checkbox)

        self.show_plots = QCheckBox()
        self.show_plots.setStyleSheet(self.checkbox_style())
        self.show_plots.setChecked(self.config_data['compute_angles_advanced']['show_plots'])
        advanced_angles_layout.addRow(self.create_label("Show Plots:"), self.show_plots)

        self.flip_left_right = QCheckBox()
        self.flip_left_right.setStyleSheet(self.checkbox_style())
        self.flip_left_right.setChecked(self.config_data['compute_angles_advanced']['flip_left_right'])
        advanced_angles_layout.addRow(self.create_label("Flip Left/Right:"), self.flip_left_right)

        self.filter_type = QComboBox()
        self.filter_type.setStyleSheet(self.combobox_style())
        self.filter_type.addItems(["butterworth", "gaussian", "LOESS", "median"])
        self.filter_type.setCurrentText(self.config_data['compute_angles_advanced']['filter_type'])
        advanced_angles_layout.addRow(self.create_label("Filter Type:"), self.filter_type)

        advanced_angles_group.setLayout(advanced_angles_layout)
        scroll_layout.addWidget(advanced_angles_group)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Bottom buttons
        button_layout = QHBoxLayout()
        
        apply_button = self.create_styled_button("Apply", "#2980B9", self.apply_settings)
        apply_button.setFixedSize(100, 40)

        back_button = self.create_styled_button("Back", "#34495E", self.main_window.show_main_panel)
        back_button.setFixedSize(100, 40)

        button_layout.addStretch()
        button_layout.addWidget(apply_button)
        button_layout.addWidget(back_button)
        main_layout.addLayout(button_layout)

    def create_styled_button(self, text, color, callback):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 20px;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(color)};
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    @staticmethod
    def lighten_color(color):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        factor = 1.2
        r, g, b = [min(int(x * factor), 255) for x in (r, g, b)]
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def darken_color(color):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        factor = 0.8
        r, g, b = [max(int(x * factor), 0) for x in (r, g, b)]
        return f"#{r:02x}{g:02x}{b:02x}"

    def create_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("""
            color: white;
            font-size: 14px;
        """)
        return label

    def spinbox_style(self):
        return """
            QSpinBox, QDoubleSpinBox {
                background-color: #2C3E50;
                color: white;
                border: 1px solid #34495E;
                padding: 5px;
                border-radius: 3px;
            }
            QSpinBox::up-button, QDoubleSpinBox::up-button, 
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                width: 20px;
            }
        """

    def lineedit_style(self):
        return """
            QLineEdit {
                background-color: #2C3E50;
                color: white;
                border: 1px solid #34495E;
                padding: 5px;
                border-radius: 3px;
            }
        """

    def checkbox_style(self):
        return """
            QCheckBox {
                color: white;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #34495E;
                background-color: #2C3E50;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #3498DB;
                background-color: #3498DB;
            }
        """

    def combobox_style(self):
        return """
            QComboBox {
                background-color: #2C3E50;
                color: white;
                border: 1px solid #34495E;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #34495E;
                border-left-style: solid;
            }
        """

    def apply_settings(self):
        # Basic Settings
        self.config_data['pose']['display_detection'] = self.display_detection_checkbox.isChecked()
        
        time_range = [
            float(self.time_range_start.text()) if self.time_range_start.text() else None,
            float(self.time_range_end.text()) if self.time_range_end.text() else None
        ]
        self.config_data['pose']['time_range'] = time_range if any(time_range) else []

        self.config_data['compute_angles']['joint_angles'] = [
            item.text() for item in self.joint_angles_list.selectedItems()
        ]
        self.config_data['compute_angles']['segment_angles'] = [
            item.text() for item in self.segment_angles_list.selectedItems()
        ]

        # Advanced Pose Settings
        self.config_data['pose_advanced']['webcam_id'] = self.webcam_id.value()
        self.config_data['pose_advanced']['input_size'] = eval(self.input_size.text())
        self.config_data['pose_advanced']['overwrite_pose'] = self.overwrite_pose.isChecked()
        self.config_data['pose_advanced']['det_frequency'] = self.det_frequency.value()
        self.config_data['pose_advanced']['mode'] = self.mode.currentText()
        self.config_data['pose_advanced']['keypoints_threshold'] = self.keypoints_threshold.value()

        # Advanced Angles Settings
        self.config_data['compute_angles_advanced']['show_angles_on_img'] = self.show_angles_on_img.isChecked()
        self.config_data['compute_angles_advanced']['show_angles_on_vid'] = self.show_angles_on_vid.isChecked()
        self.config_data['compute_angles_advanced']['filter'] = self.filter_checkbox.isChecked()
        self.config_data['compute_angles_advanced']['show_plots'] = self.show_plots.isChecked()
        self.config_data['compute_angles_advanced']['flip_left_right'] = self.flip_left_right.isChecked()
        self.config_data['compute_angles_advanced']['filter_type'] = self.filter_type.currentText()

        # Save updated config to file
        try:
            with open(self.config_path, 'w') as f:
                toml.dump(self.config_data, f)
            QMessageBox.information(self, "Settings", "Configuration updated successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save configuration: {str(e)}")

    def go_back(self):
        self.main_window.show_main_panel()


class InstallationPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        install_btn = self.create_styled_button("Install Sports2D", "#2ECC71", self.install_package)
        remove_btn = self.create_styled_button("Remove Sports2D", "#E74C3C", self.remove_package)
        
        layout.addWidget(install_btn)
        layout.addWidget(remove_btn)

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
        layout.addWidget(self.gpu_checkbox)

        note_message = QLabel(
            "Note: For faster inference, you can run on the GPU.\n"
            "Install pyTorch with CUDA and cuDNN support, and ONNX Runtime with GPU support (not available on MacOS).\n"
            "Be aware that GPU support takes an additional 6 GB on disk."
        )
        note_message.setWordWrap(True)
        note_message.setStyleSheet("color: #CCCCCC; font-size: 14px; margin-top: 10px;")
        layout.addWidget(note_message)

        back_button = self.create_styled_button("Back", "#34495E", self.main_window.show_main_panel)
        back_button.setFixedSize(100, 40)
        layout.addWidget(back_button, alignment=Qt.AlignRight | Qt.AlignBottom)

    def create_styled_button(self, text, color, callback):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 20px;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(color)};
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    @staticmethod
    def lighten_color(color):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        return f"#{min(int(r*1.2), 255):02x}{min(int(g*1.2), 255):02x}{min(int(b*1.2), 255):02x}"

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
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # 마진 제거
        self.setup_ui()

    def setup_ui(self):
        # 전체 배경 프레임 생성
        self.background_frame = QFrame(self)
        self.background_frame.setObjectName("backgroundFrame")
        self.background_frame.setStyleSheet("""
            #backgroundFrame {
                background-color: #34495e;
                border-radius: 20px;
            }
        """)
        self.main_layout.addWidget(self.background_frame)

        # 배경 프레임 내부 레이아웃
        self.content_layout = QVBoxLayout(self.background_frame)
        self.content_layout.setSpacing(20)  # 요소 간 간격 설정

        # 상단 라벨 생성
        self.info_label = QLabel("Compute 2D joint and segment angles of your athletes or patients from real-time video streams or video files!")
        self.info_label.setWordWrap(True)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 16px;
            padding: 20px;
            border-radius: 20px;
        """)
        self.content_layout.addWidget(self.info_label)

        # GIF 레이블 생성 및 중앙 정렬
        self.gif_label = QLabel()
        self.gif_movie = QMovie("temp_gif.gif")
        self.gif_label.setMovie(self.gif_movie)
        self.gif_movie.start()
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setStyleSheet("""
            border: none;
            background: transparent;
        """)
        self.content_layout.addWidget(self.gif_label)

        # 여백 추가
        self.content_layout.addStretch(1)

    def resizeEvent(self, event):
        new_size = self.size()
        
        # GIF 크기 조정
        gif_width = int(new_size.width() * 0.95)
        gif_height = int(new_size.height() * 0.6)
        self.gif_movie.setScaledSize(QSize(gif_width, gif_height))

        super().resizeEvent(event)

class CustomStyleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sports2D")
        self.resize(1200, 720)
        self.setMinimumSize(600, 400)
        self.current_theme = "Dark"

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_widget = self.create_left_panel()
        main_layout.addWidget(left_widget)

        self.right_stack = QStackedWidget()
        main_layout.addWidget(self.right_stack)

        self.main_panel = MainPanel(self)
        self.right_stack.addWidget(self.main_panel)

        self.settings_panel = None
        self.installation_panel = None

        self.apply_theme()

    def create_left_panel(self):
        left_widget = QWidget()
        left_widget.setFixedWidth(200)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel("Sports2D")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #3498db;")
        title_label.setContentsMargins(40, 0, 0, 10)
        left_layout.addWidget(title_label)

        btn_texts = ["Installation", "Real-time Analysis", "Video Analysis", "Settings"]
        for text in btn_texts:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.setStyleSheet(self.button_style())
            left_layout.addWidget(btn)
            if text == "Installation":
                btn.clicked.connect(self.show_installation_panel)
            elif text == "Settings":
                btn.clicked.connect(self.show_settings_panel)

        left_layout.addStretch(1)

        appearance_label = QLabel("Appearance Mode")
        appearance_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        appearance_label.setContentsMargins(22, 0, 0, 0)
        left_layout.addWidget(appearance_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setStyleSheet(self.combobox_style())
        left_layout.addWidget(self.theme_combo)

        return left_widget

    def show_installation_panel(self):
        if not self.installation_panel:
            self.installation_panel = InstallationPanel(self)
            self.right_stack.addWidget(self.installation_panel)
        self.right_stack.setCurrentWidget(self.installation_panel)

    def show_settings_panel(self):
        if not self.settings_panel:
            self.settings_panel = SettingsPanel(self)  # self를 전달하여 main_window 참조 제공
            self.right_stack.addWidget(self.settings_panel)
        self.right_stack.setCurrentWidget(self.settings_panel)

    def show_main_panel(self):
        self.right_stack.setCurrentWidget(self.main_panel)

    def change_theme(self, theme):
        self.current_theme = theme
        self.apply_theme()

    def apply_theme(self):
        if self.current_theme == "Dark":
            self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2C3E50;
                color: #ECF0F1;
            }
            QGroupBox {
                border: 1px solid #34495E;
                margin-top: 0.5em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            """)
        else:  # Light theme
            self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #ECF0F1;
                color: #2C3E50;
            }
            QGroupBox {
                border: 1px solid #BDC3C7;
                margin-top: 0.5em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            """)

        self.main_panel.setStyleSheet(self.main_panel.styleSheet())
        if self.installation_panel:
            self.installation_panel.setStyleSheet(self.installation_panel.styleSheet())
        if self.settings_panel:
            self.settings_panel.setStyleSheet(self.settings_panel.styleSheet())

    def button_style(self):
        if self.current_theme == "Dark":
            return """
            QPushButton {
                background-color: #34495E;
                color: #ECF0F1;
                border-radius: 20px;
                border: none;
                padding: 5px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #2C3E50;
            }
            QPushButton:disabled {
                background-color: #7F8C8D;
                color: #BDC3C7;
            }
            """
        else:
            return """
            QPushButton {
                background-color: #3498DB;
                color: #FFFFFF;
                border-radius: 20px;
                border: none;
                padding: 5px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
            }
            """

    def label_style(self):
        if self.current_theme == "Dark":
            return """
            QLabel {
                color: #ECF0F1;
                background-color: #34495E;
                padding: 10px;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            """
        else:
            return """
            QLabel {
                color: #2C3E50;
                background-color: #BDC3C7;
                padding: 10px;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            """


    def checkbox_style(self):
        if self.current_theme == "Dark":
            return """
            QCheckBox {
                color: #ECF0F1;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #3498DB;
                border: 1px solid #2980B9;
                border-radius: 5px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #34495E;
                border: 1px solid #2980B9;
                border-radius: 5px;
            }
            QCheckBox::indicator:disabled {
                background-color: #7F8C8D;
                border: 1px solid #BDC3C7;
                border-radius: 5px;
            }
            """
        else:
            return """
            QCheckBox {
                color: #2C3E50;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #3498DB;
                border: 1px solid #2980B9;
                border-radius: 5px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #ECF0F1;
                border: 1px solid #2980B9;
                border-radius: 5px;
            }
            QCheckBox::indicator:disabled {
                background-color: #BDC3C7;
                border: 1px solid #7F8C8D;
                border-radius: 5px;
            }
            """

    
    def combobox_style(self):
        if self.current_theme == "Dark":
            return """
            QComboBox {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #2980B9;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #2980B9;
                border-left-style: solid;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QComboBox::down-arrow {
                image: url(path_to_down_arrow_icon.png);
            }
            """
        else:
            return """
            QComboBox {
                background-color: #ECF0F1;
                color: #2C3E50;
                border: 1px solid #3498DB;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #3498DB;
                border-left-style: solid;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QComboBox::down-arrow {
                image: url(path_to_down_arrow_icon.png);
            }
            """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomStyleWindow()
    window.show()
    sys.exit(app.exec())