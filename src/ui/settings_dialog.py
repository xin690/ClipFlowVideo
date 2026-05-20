from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QComboBox, QGroupBox,
                              QFormLayout, QTabWidget, QWidget, QCheckBox,
                              QSpinBox, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
import os


class SettingsDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.tabs_widget = None
        try:
            self.init_ui()
            self.load_settings()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"初始化设置失败: {str(e)}")
            raise

    def init_ui(self):
        self.setWindowTitle("设置")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        self.tabs_widget = QTabWidget()
        self.tabs_widget.addTab(self.create_api_tab(), "API配置")
        self.tabs_widget.addTab(self.create_tts_tab(), "配音设置")
        self.tabs_widget.addTab(self.create_asr_tab(), "语音识别")
        self.tabs_widget.addTab(self.create_output_tab(), "输出设置")
        
        layout.addWidget(self.tabs_widget)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def create_api_tab(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.llm_provider_combo = QComboBox()
        self.llm_provider_combo.addItems(["DeepSeek", "OpenAI", "OpenRouter"])
        layout.addRow("LLM提供商:", self.llm_provider_combo)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("输入API Key（可选，不填则使用环境变量）")
        layout.addRow("API Key:", self.api_key_input)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "deepseek-chat",
            "gpt-3.5-turbo",
            "gpt-4",
            "claude-3-sonnet"
        ])
        layout.addRow("模型:", self.model_combo)
        
        self.test_api_btn = QPushButton("测试连接")
        self.test_api_btn.clicked.connect(self.test_api_connection)
        layout.addRow("", self.test_api_btn)
        
        widget.setLayout(layout)
        return widget

    def create_tts_tab(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.voice_combo = QComboBox()
        self.voice_combo.addItems([
            "zh-CN-XiaoxiaoNeural (女声-晓晓)",
            "zh-CN-YunxiNeural (男声-云希)",
            "zh-CN-XiaoyiNeural (女声-晓伊)",
            "zh-CN-YunyangNeural (男声-云扬)",
            "zh-CN-YunyeNeural (男声-云野)",
        ])
        layout.addRow("配音音色:", self.voice_combo)
        
        self.rate_spin = QSpinBox()
        self.rate_spin.setRange(-100, 100)
        self.rate_spin.setSuffix(" %")
        self.rate_spin.setValue(0)
        layout.addRow("语速调整:", self.rate_spin)
        
        self.volume_spin = QSpinBox()
        self.volume_spin.setRange(-100, 100)
        self.volume_spin.setSuffix(" %")
        self.volume_spin.setValue(0)
        layout.addRow("音量调整:", self.volume_spin)
        
        widget.setLayout(layout)
        return widget

    def create_asr_tab(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.asr_model_combo = QComboBox()
        self.asr_model_combo.addItems([
            "tiny (最快，准确率较低)",
            "base (快速，准确率一般)",
            "small (中等速度，准确率较高)",
            "medium (较慢，准确率高)",
            "large (最慢，准确率最高)",
        ])
        self.asr_model_combo.setCurrentIndex(1)
        layout.addRow("识别模型:", self.asr_model_combo)
        
        self.device_combo = QComboBox()
        self.device_combo.addItems(["CPU", "GPU (CUDA)"])
        layout.addRow("运行设备:", self.device_combo)
        
        widget.setLayout(layout)
        return widget

    def create_output_tab(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setReadOnly(True)
        layout.addRow("输出目录:", self.output_dir_input)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_output_dir)
        layout.addRow("", browse_btn)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["最佳质量", "720p", "480p"])
        self.quality_combo.setCurrentIndex(0)
        layout.addRow("视频质量:", self.quality_combo)
        
        self.subtitle_check = QCheckBox("自动生成字幕")
        self.subtitle_check.setChecked(True)
        layout.addRow("字幕选项:", self.subtitle_check)
        
        self.rewrite_check = QCheckBox("AI改写解说")
        self.rewrite_check.setChecked(True)
        layout.addRow("", self.rewrite_check)
        
        widget.setLayout(layout)
        return widget

    def load_settings(self):
        provider = self.config_manager.get('llm_provider', 'deepseek')
        provider_map = {'deepseek': 0, 'openai': 1, 'openrouter': 2}
        index = provider_map.get(provider.lower(), 0)
        self.llm_provider_combo.setCurrentIndex(index)
        
        api_key = self.config_manager.get_api_key(provider) or ""
        self.api_key_input.setText(api_key)
        
        voice = self.config_manager.get('tts_voice', 'zh-CN-XiaoxiaoNeural')
        for i in range(self.voice_combo.count()):
            if voice in self.voice_combo.itemText(i):
                self.voice_combo.setCurrentIndex(i)
                break
        
        output_dir = self.config_manager.get('output_dir', '')
        self.output_dir_input.setText(output_dir)
        
        quality = self.config_manager.get('quality', 'best')
        quality_map = {'best': 0, '720p': 1, '480p': 2}
        q_index = quality_map.get(quality.lower(), 0)
        self.quality_combo.setCurrentIndex(q_index)

    def save_settings(self):
        try:
            providers = ['deepseek', 'openai', 'openrouter']
            provider = providers[self.llm_provider_combo.currentIndex()]
            self.config_manager.set('llm_provider', provider)
            
            api_key = self.api_key_input.text().strip()
            if api_key:
                self.config_manager.set_api_key(provider, api_key)
            
            voice_text = self.voice_combo.currentText()
            voice = voice_text.split(" ")[0]
            self.config_manager.set('tts_voice', voice)
            
            qualities = ['best', '720p', '480p']
            quality = qualities[self.quality_combo.currentIndex()]
            self.config_manager.set('quality', quality)
            
            output_dir = self.output_dir_input.text().strip()
            if output_dir:
                self.config_manager.set('output_dir', output_dir)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")
            self.reject()

    def browse_output_dir(self):
        try:
            current = self.output_dir_input.text()
            if not current:
                current = os.path.expanduser("~")
            
            dir_path = QFileDialog.getExistingDirectory(
                self, "选择输出目录", current
            )
            if dir_path:
                self.output_dir_input.setText(dir_path)
                self.config_manager.set('output_dir', dir_path)
        except Exception as e:
            QMessageBox.warning(self, "警告", f"选择目录失败: {str(e)}")

    def test_api_connection(self):
        try:
            api_key = self.api_key_input.text().strip()
            if not api_key:
                QMessageBox.warning(self, "提示", "请先输入API Key")
                return
            
            providers = ['deepseek', 'openai', 'openrouter']
            provider = providers[self.llm_provider_combo.currentIndex()]
            
            if provider == 'deepseek':
                from openai import OpenAI
                client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                client.models.list()
                QMessageBox.information(self, "成功", "DeepSeek API连接测试成功！")
                
            elif provider == 'openai':
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                client.models.list()
                QMessageBox.information(self, "成功", "OpenAI API连接测试成功！")
                
            elif provider == 'openrouter':
                from openai import OpenAI
                client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
                client.models.list()
                QMessageBox.information(self, "成功", "OpenRouter API连接测试成功！")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"连接失败: {str(e)}")