import subprocess
import os
from pathlib import Path
from typing import Optional, Tuple


class AudioExtractor:
    def __init__(self, ffmpeg_path: str = 'ffmpeg'):
        self.ffmpeg_path = ffmpeg_path

    def extract_audio(self, video_path: str, output_path: Optional[str] = None, 
                     format: str = 'mp3', bitrate: str = '192k') -> str:
        if output_path is None:
            video_dir = os.path.dirname(video_path)
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(video_dir, f"{video_name}.{format}")

        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
            '-vn',
            '-acodec', 'libmp3lame' if format == 'mp3' else format,
            '-ab', bitrate,
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def extract_audio_wav(self, video_path: str, output_path: Optional[str] = None) -> str:
        if output_path is None:
            video_dir = os.path.dirname(video_path)
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(video_dir, f"{video_name}.wav")

        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def get_audio_info(self, audio_path: str) -> dict:
        cmd = [
            self.ffmpeg_path,
            '-i', audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {'output': result.stderr}

    def split_audio(self, audio_path: str, start: float, duration: float, 
                   output_path: Optional[str] = None) -> str:
        if output_path is None:
            audio_dir = os.path.dirname(audio_path)
            audio_name = os.path.splitext(os.path.basename(audio_path))[0]
            output_path = os.path.join(audio_dir, f"{audio_name}_split.wav")

        cmd = [
            self.ffmpeg_path,
            '-i', audio_path,
            '-ss', str(start),
            '-t', str(duration),
            '-acodec', 'pcm_s16le',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path