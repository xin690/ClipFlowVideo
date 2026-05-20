from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QProgressBar, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QTextCursor


class LogWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumHeight(200)
        self.setFont(QFont("Consolas", 9))
        self.document().setMaximumBlockCount(1000)

    def append_log(self, message):
        self.append(message)
        self.moveCursor(QTextCursor.MoveOperation.End)


class ProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)
        
        self.label = QLabel("就绪")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% - %s")
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
    
    def set_progress(self, value, text=""):
        self.progress_bar.setValue(value)
        if text:
            self.progress_bar.setFormat(f"%p% - {text}")
            self.label.setText(text)

    def set_status(self, text):
        self.label.setText(text)

    def reset(self):
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.label.setText("就绪")


class VideoInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VideoInfoWidget")
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            #VideoInfoWidget {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel("等待输入视频...")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)
        
        info_layout = QHBoxLayout()
        
        self.duration_label = QLabel("时长: --")
        self.duration_label.setStyleSheet("color: gray;")
        info_layout.addWidget(self.duration_label)
        
        info_layout.addStretch()
        
        self.size_label = QLabel("大小: --")
        self.size_label.setStyleSheet("color: gray;")
        info_layout.addWidget(self.size_label)
        
        layout.addLayout(info_layout)
        self.setLayout(layout)

    def set_video_info(self, title="", duration="", size=""):
        if title:
            self.title_label.setText(title)
        if duration:
            self.duration_label.setText(f"时长: {duration}")
        if size:
            self.size_label.setText(f"大小: {size}")

    def clear(self):
        self.title_label.setText("等待输入视频...")
        self.duration_label.setText("时长: --")
        self.size_label.setText("大小: --")


class StatusBarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: green;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        self.version_label = QLabel("v1.0.0")
        self.version_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.version_label)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #f0f0f0; border-top: 1px solid #ccc;")

    def set_status(self, text, color="green"):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color};")

    def set_ready(self):
        self.set_status("就绪", "green")

    def set_processing(self):
        self.set_status("处理中...", "orange")

    def set_error(self, message=""):
        self.set_status(f"错误: {message}" if message else "错误", "red")

    def set_success(self):
        self.set_status("完成", "green")