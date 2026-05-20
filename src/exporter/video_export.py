import subprocess
import os
from pathlib import Path
from typing import List, Optional, Tuple


class VideoExporter:
    def __init__(self, ffmpeg_path: str = 'ffmpeg'):
        self.ffmpeg_path = ffmpeg_path

    def export_h264(self, input_path: str, output_path: Optional[str] = None,
                   quality: str = 'medium', preset: str = 'medium') -> str:
        if output_path is None:
            input_dir = os.path.dirname(input_path)
            input_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(input_dir, f"{input_name}_export.mp4")

        crf_values = {
            'low': '18',
            'medium': '23',
            'high': '28'
        }
        crf = crf_values.get(quality, '23')

        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-c:v', 'libx264',
            '-preset', preset,
            '-crf', crf,
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def export_with_subtitle(self, video_path: str, subtitle_path: str,
                           output_path: Optional[str] = None) -> str:
        if output_path is None:
            video_dir = os.path.dirname(video_path)
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(video_dir, f"{video_name}_subtitled.mp4")

        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
            '-vf', f'subtitles=\'{subtitle_path}\'',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def export_no_audio(self, input_path: str, output_path: Optional[str] = None) -> str:
        if output_path is None:
            input_dir = os.path.dirname(input_path)
            input_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(input_dir, f"{input_name}_no_audio.mp4")

        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-c:v', 'copy',
            '-an',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def export_audio_only(self, input_path: str, output_path: Optional[str] = None,
                         audio_format: str = 'mp3') -> str:
        if output_path is None:
            input_dir = os.path.dirname(input_path)
            input_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(input_dir, f"{input_name}.{audio_format}")

        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-vn',
            '-acodec', 'libmp3lame' if audio_format == 'mp3' else audio_format,
            '-ab', '192k',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def merge_video_audio(self, video_path: str, audio_path: str,
                         output_path: Optional[str] = None) -> str:
        if output_path is None:
            video_dir = os.path.dirname(video_path)
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(video_dir, f"{video_name}_merged.mp4")

        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def compress(self, input_path: str, output_path: Optional[str] = None,
                target_size_mb: int = 50) -> str:
        if output_path is None:
            input_dir = os.path.dirname(input_path)
            input_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(input_dir, f"{input_name}_compressed.mp4")

        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-c:v', 'libx264',
            '-preset', 'faster',
            '-crf', '28',
            '-c:a', 'aac',
            '-b:a', '96k',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        if file_size > target_size_mb:
            print(f"Warning: Output file ({file_size:.1f}MB) exceeds target ({target_size_mb}MB)")
        
        return output_path

    def get_video_info(self, video_path: str) -> dict:
        cmd = [self.ffmpeg_path, '-i', video_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stderr
        
        info = {
            'duration': 0.0,
            'width': 0,
            'height': 0,
            'fps': 0.0,
            'codec': 'unknown'
        }
        
        for line in output.split('\n'):
            if 'Duration:' in line:
                duration_str = line.split('Duration:')[1].split(',')[0].strip()
                parts = duration_str.split(':')
                if len(parts) == 3:
                    h, m, s = parts
                    info['duration'] = float(h) * 3600 + float(m) * 60 + float(s.split('.')[0])
            
            if 'Video:' in line:
                parts = line.split(',')
                for part in parts:
                    part = part.strip()
                    if 'x' in part and part[0].isdigit():
                        dimensions = part.split('x')
                        info['width'] = int(dimensions[0])
                        info['height'] = int(dimensions[1])
                    elif 'fps' in part.lower():
                        fps = part.lower().split('fps')[0].strip()
                        info['fps'] = float(fps)
        
        return info