import sys
import os
import tempfile
import importlib.util

def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
src_path = os.path.join(base_path, 'src')

main_window = _load_module('main_window', os.path.join(src_path, 'ui', 'main_window.py'))
settings_dialog = _load_module('settings_dialog', os.path.join(src_path, 'ui', 'settings_dialog.py'))
widgets_module = _load_module('widgets', os.path.join(src_path, 'ui', 'widgets.py'))
config_module = _load_module('config', os.path.join(src_path, 'core', 'config.py'))

WorkerThread = main_window.WorkerThread
SettingsDialog = settings_dialog.SettingsDialog
LogWidget = widgets_module.LogWidget
ProgressWidget = widgets_module.ProgressWidget
VideoInfoWidget = widgets_module.VideoInfoWidget
StatusBarWidget = widgets_module.StatusBarWidget
ConfigManager = config_module.ConfigManager
get_ffmpeg_path = main_window.get_ffmpeg_path
check_ffmpeg = main_window.check_ffmpeg

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QLabel, QPushButton, QLineEdit,
                              QMessageBox, QMenuBar, QMenu, QStatusBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon, QFont


class ClipFlowApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.config_manager = ConfigManager()
        self.worker = None
        self.output_dir = self._get_output_dir()
        
        self.init_ui()
        self.create_menu()
        
    def _get_output_dir(self):
        output_dir = self.config_manager.get('output_dir')
        if not output_dir or not os.path.exists(output_dir):
            output_dir = os.path.join(tempfile.gettempdir(), 'ClipFlow')
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def init_ui(self):
        self.setWindowTitle("ClipFlow - AI视频二创工具")
        self.setMinimumSize(800, 600)
        self.setFont(QFont("Microsoft YaHei", 10))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title_label = QLabel("ClipFlow - AI视频二创工具")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        input_group = QWidget()
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入视频链接 (YouTube/TikTok/Bilibili等)")
        self.url_input.setMinimumHeight(40)
        input_layout.addWidget(self.url_input)
        
        self.start_btn = QPushButton("开始处理")
        self.start_btn.setMinimumSize(120, 40)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.start_btn.clicked.connect(self.start_processing)
        input_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setMinimumSize(80, 40)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_processing)
        input_layout.addWidget(self.stop_btn)
        
        layout.addWidget(input_group)
        input_group.setLayout(input_layout)
        
        self.video_info = VideoInfoWidget()
        layout.addWidget(self.video_info)
        
        self.progress_widget = ProgressWidget()
        layout.addWidget(self.progress_widget)
        
        log_label = QLabel("处理日志")
        log_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(log_label)
        
        self.log_widget = LogWidget()
        layout.addWidget(self.log_widget, 1)
        
        self.status_bar_widget = StatusBarWidget()
        layout.addWidget(self.status_bar_widget)
        
        central_widget.setLayout(layout)

    def create_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("文件")
        
        open_output_action = QAction("打开输出目录", self)
        open_output_action.triggered.connect(self.open_output_dir)
        file_menu.addAction(open_output_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        settings_menu = menubar.addMenu("设置")
        
        preferences_action = QAction("首选项", self)
        preferences_action.triggered.connect(self.open_settings)
        settings_menu.addAction(preferences_action)
        
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def start_processing(self):
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "提示", "请输入视频链接")
            return
        
        if not self._is_supported_url(url):
            QMessageBox.warning(self, "提示", "不支持的视频链接，请输入YouTube/TikTok/Bilibili等链接")
            return
        
        self.log_widget.clear()
        self.log_widget.append_log(f"输入URL: {url}")
        self.log_widget.append_log(f"输出目录: {self.output_dir}")
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.url_input.setEnabled(False)
        self.progress_widget.reset()
        self.status_bar_widget.set_processing()
        
        self.worker = WorkerThread(url, self.output_dir, self.config_manager)
        self.worker.progress_update.connect(self.on_progress_update)
        self.worker.log_message.connect(self.on_log_message)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def stop_processing(self):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        self.reset_ui()
        self.log_widget.append_log("处理已取消")
        self.status_bar_widget.set_status("已取消", "orange")

    def on_progress_update(self, text, value):
        self.progress_widget.set_progress(value, text)

    def on_log_message(self, message):
        self.log_widget.append_log(message)

    def on_finished(self, success, result):
        self.reset_ui()
        
        if success:
            self.status_bar_widget.set_success()
            self.log_widget.append_log("=" * 50)
            self.log_widget.append_log("处理完成!")
            self.log_widget.append_log(f"输出文件: {result}")
            
            reply = QMessageBox.information(
                self, "完成",
                f"视频处理完成！\n\n输出文件: {result}\n\n是否打开输出目录？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.open_output_dir()
        else:
            self.status_bar_widget.set_error(result)
            self.log_widget.append_log("=" * 50)
            self.log_widget.append_log(f"处理失败: {result}")
            
            QMessageBox.critical(self, "错误", f"处理失败: {result}")

    def reset_ui(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.url_input.setEnabled(True)
        self.worker = None

    def _is_supported_url(self, url):
        supported = ['youtube.com', 'youtu.be', 'tiktok.com', 'bilibili.com', 
                     'twitter.com', 'x.com', 'instagram.com']
        return any(site in url.lower() for site in supported)

    def open_settings(self):
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            self.output_dir = self._get_output_dir()
            self.log_widget.append_log(f"输出目录已更新: {self.output_dir}")

    def open_output_dir(self):
        try:
            os.startfile(self.output_dir) if sys.platform == 'win32' else None
        except Exception:
            pass

    def show_about(self):
        QMessageBox.about(
            self, "关于 ClipFlow",
            "<h3>ClipFlow - AI视频二创工具</h3>"
            "<p>版本: 1.0.0</p>"
            "<p>基于AI的视频二次创作自动化工具</p>"
            "<p>支持: YouTube, TikTok, Bilibili等平台</p>"
            "<hr>"
            "<p>功能: 视频下载 → 语音识别 → AI改写 → 自动配音 → 视频导出</p>"
        )

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    ffmpeg_ok = check_ffmpeg()
    if not ffmpeg_ok:
        QMessageBox.warning(
            None, "警告",
            "未找到ffmpeg或ffmpeg配置不正确！\n\n"
            "请确保ffmpeg文件夹与ClipFlow.exe在同一目录下。\n"
            "某些功能可能无法正常工作。"
        )
    
    window = ClipFlowApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()