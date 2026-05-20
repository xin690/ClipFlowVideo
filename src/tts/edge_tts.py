import asyncio
import os
import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import edge_tts


@dataclass
class TTSResult:
    audio_path: str
    text: str
    start_time: float
    end_time: float


@dataclass
class TTSSegment:
    text: str
    start: float
    end: float
    duration: float


class EdgeTTS:
    VOICE_MAP = {
        'zh-CN': {
            'female': 'zh-CN-XiaoxiaoNeural',
            'male': 'zh-CN-YunxiNeural',
            'young_female': 'zh-CN-XiaoyiNeural',
            'older_male': 'zh-CN-YunyangNeural'
        },
        'en-US': {
            'female': 'en-US-JennyNeural',
            'male': 'en-US-GuyNeural',
            'young_female': 'en-US-AriaNeural'
        }
    }

    def __init__(self, voice: str = 'zh-CN-XiaoxiaoNeural', rate: str = '+0%', 
                 volume: str = '+0%', output_dir: Optional[str] = None):
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.output_dir = output_dir or tempfile.mkdtemp(prefix='clipflow_tts_')
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    async def _synthesize_async(self, text: str, output_path: str) -> float:
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, volume=self.volume)
        await communicate.save(output_path)
        
        duration = await communicate.get_duration()
        return duration / 1_000_000

    def synthesize(self, text: str, output_path: Optional[str] = None) -> str:
        if output_path is None:
            output_path = os.path.join(self.output_dir, f"tts_{len(text)}.mp3")
        
        asyncio.run(self._synthesize_async(text, output_path))
        return output_path

    def synthesize_segments(self, segments: List[TTSSegment], 
                           output_dir: Optional[str] = None) -> List[TTSResult]:
        output_dir = output_dir or self.output_dir
        results = []

        for i, seg in enumerate(segments):
            output_path = os.path.join(output_dir, f"segment_{i:04d}.mp3")
            try:
                duration = asyncio.run(self._synthesize_async(seg.text, output_path))
                results.append(TTSResult(
                    audio_path=output_path,
                    text=seg.text,
                    start_time=seg.start,
                    end_time=seg.start + duration
                ))
            except Exception as e:
                print(f"Error synthesizing segment {i}: {e}")
                results.append(TTSResult(
                    audio_path="",
                    text=seg.text,
                    start_time=seg.start,
                    end_time=seg.start
                ))

        return results

    def synthesize_to_wav(self, text: str, output_path: Optional[str] = None) -> str:
        mp3_path = self.synthesize(text)
        
        if output_path is None:
            output_path = mp3_path.replace('.mp3', '.wav')
        
        import subprocess
        subprocess.run([
            'ffmpeg', '-i', mp3_path, 
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-y', output_path
        ], check=True, capture_output=True)
        
        return output_path

    @staticmethod
    def get_available_voices(language: Optional[str] = None) -> List[Dict[str, str]]:
        voices = asyncio.run(edge_tts.list_voices())
        
        if language:
            voices = [v for v in voices if v['Locale'].startswith(language)]
        
        return voices

    @staticmethod
    def get_chinese_voices() -> Dict[str, str]:
        return {
            '晓晓': 'zh-CN-XiaoxiaoNeural',
            '云希': 'zh-CN-YunxiNeural',
            '云扬': 'zh-CN-YunyangNeural',
            '晓伊': 'zh-CN-XiaoyiNeural',
            '云野': 'zh-CN-YunyeNeural'
        }

    @staticmethod
    def get_english_voices() -> Dict[str, str]:
        return {
            'Jenny': 'en-US-JennyNeural',
            'Guy': 'en-US-GuyNeural',
            'Aria': 'en-US-AriaNeural',
            'Roger': 'en-US-RogerNeural'
        }

    def set_voice(self, voice: str):
        self.voice = voice

    def set_rate(self, rate: str):
        self.rate = rate

    def set_volume(self, volume: str):
        self.volume = volume