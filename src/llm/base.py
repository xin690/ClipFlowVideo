from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class SubtitleItem:
    start: float
    end: float
    text: str


@dataclass
class RewriteResult:
    original: str
    rewritten: str
    start: float
    end: float


class BaseLLM(ABC):
    @abstractmethod
    def rewrite(self, subtitles: List[SubtitleItem], style: str = 'commentary') -> List[RewriteResult]:
        pass

    @abstractmethod
    def generate_commentary(self, topic: str, duration: float, style: str = 'exciting') -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass


DEFAULT_REWRITE_PROMPT = """你是短视频解说创作者。

请将以下英文字幕改写成中文短视频解说风格：
1. 更口语化，符合中国观众习惯
2. 增强情绪表达，更吸引人
3. 保持原视频核心信息
4. 每句长度适合配音（建议5-15字）
5. 添加适当的语气词和感叹
6. 保持解说风格，不是翻译

原文字幕:
{original_text}

请直接输出改写后的内容，每句一行：
"""


class LLMPromptBuilder:
    def __init__(self):
        self.style_templates = {
            'commentary': DEFAULT_REWRITE_PROMPT,
            'funny': """你是幽默短视频创作者。请将以下内容改写成搞笑解说风格，加入适当的幽默元素和反转。""",
            'educational': """你是科普短视频创作者。请将以下内容改写成科普风格，语言严谨但生动易懂。""",
            'emotional': """你是情感类短视频创作者。请将以下内容改写成情感共鸣风格，增强感染力。"""
        }

    def build_rewrite_prompt(self, subtitles: List[SubtitleItem], style: str = 'commentary') -> str:
        original_text = '\n'.join([f"[{sub.start:.1f}s-{sub.end:.1f}s] {sub.text}" for sub in subtitles])
        
        template = self.style_templates.get(style, DEFAULT_REWRITE_PROMPT)
        return template.format(original_text=original_text)

    def build_commentary_prompt(self, topic: str, duration: float, style: str = 'exciting') -> str:
        style_hints = {
            'exciting': '充满激情，节奏快，适合娱乐类视频',
            'calm': '冷静沉稳，逻辑清晰，适合知识类视频',
            'humorous': '幽默风趣，适当搞笑，适合搞笑类视频'
        }
        
        hint = style_hints.get(style, style_hints['exciting'])
        estimated_duration = int(duration * 3)
        
        return f"""你是短视频解说创作者。

主题: {topic}
目标时长: 约{estimated_duration}字
风格: {hint}

请生成一段短视频解说文案，要求：
1. 开场要有吸引力（Hook）
2. 中间内容有信息量
3. 结尾有总结或引导
4. 语言口语化，适合配音

请直接输出文案内容：
"""