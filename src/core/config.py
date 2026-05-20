import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class AppSettings:
    api_keys: Dict[str, str]
    llm_provider: str
    llm_model: str
    tts_voice: str
    asr_model: str
    output_dir: str
    quality: str
    ffmpeg_path: str

    @staticmethod
    def default() -> 'AppSettings':
        return AppSettings(
            api_keys={},
            llm_provider='deepseek',
            llm_model='deepseek-chat',
            tts_voice='zh-CN-XiaoxiaoNeural',
            asr_model='base',
            output_dir=str(Path.home() / 'ClipFlow' / 'output'),
            quality='best',
            ffmpeg_path='ffmpeg'
        )


class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            self.config_path = Path.home() / '.clipflow' / 'config.json'
        else:
            self.config_path = Path(config_path)
        
        self._ensure_config_dir()
        self.settings = self._load()

    def _ensure_config_dir(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> AppSettings:
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # 合并默认配置和已保存配置
                default_data = asdict(AppSettings.default())
                merged_data = {**default_data, **data}
                return AppSettings(**merged_data)
            except Exception as e:
                print(f"加载配置失败: {e}, 使用默认配置")
        return AppSettings.default()

    def _save(self):
        try:
            os.makedirs(self.config_path.parent, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.settings), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self.settings, key, default)

    def set(self, key: str, value: Any):
        setattr(self.settings, key, value)
        self._save()

    def set_api_key(self, provider: str, api_key: str):
        self.settings.api_keys[provider] = api_key
        self._save()

    def get_api_key(self, provider: str) -> Optional[str]:
        return self.settings.api_keys.get(provider)

    def get_all_api_keys(self) -> Dict[str, str]:
        env_keys = {
            'openai': os.getenv('OPENAI_API_KEY', ''),
            'deepseek': os.getenv('DEEPSEEK_API_KEY', ''),
            'openrouter': os.getenv('OPENROUTER_API_KEY', '')
        }
        return {**env_keys, **self.settings.api_keys}

    def reset(self):
        self.settings = AppSettings.default()
        self._save()


DEFAULT_CONFIG = {
    'version': '1.0.0',
    'output_dir': '~/ClipFlow/output',
    'ffmpeg_path': 'ffmpeg',
    'quality': 'best',
    'asr': {
        'model': 'base',
        'device': 'cpu'
    },
    'tts': {
        'voice': 'zh-CN-XiaoxiaoNeural',
        'rate': '+0%',
        'volume': '+0%'
    },
    'llm': {
        'provider': 'deepseek',
        'model': 'deepseek-chat',
        'temperature': 0.8
    },
    'editor': {
        'default_scale': 1.1,
        'subtitle_font': 'Arial',
        'subtitle_size': 20
    }
}