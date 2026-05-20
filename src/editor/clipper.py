import subprocess
import os
from pathlib import Path
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass


@dataclass
class ClipSegment:
    start: float
    end: float
    text: Optional[str] = None
    effect: Optional[str] = None


class VideoClipper:
    def __init__(self, ffmpeg_path: str = 'ffmpeg'):
        self.ffmpeg_path = ffmpeg_path

    def cut_segment(self, input_path: str, start: float, end: float, 
                   output_path: Optional[str] = None) -> str:
        if output_path is None:
            input_dir = os.path.dirname(input_path)
            input_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(input_dir, f"{input_name}_clip_{start}_{end}.mp4")

        duration = end - start
        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-ss', str(start),
            '-t', str(duration),
            '-c', 'copy',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def concat_segments(self, input_paths: List[str], output_path: str,
                       concat_file: Optional[str] = None) -> str:
        if len(input_paths) < 2:
            raise ValueError("Need at least 2 segments to concatenate")

        if concat_file is None:
            concat_file = os.path.join(os.path.dirname(output_path), 'concat_list.txt')

        with open(concat_file, 'w', encoding='utf-8') as f:
            for path in input_paths:
                f.write(f"file '{path}'\n")

        cmd = [
            self.ffmpeg_path,
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def split_by_segments(self, input_path: str, segments: List[ClipSegment],
                         output_dir: Optional[str] = None) -> List[str]:
        output_dir = output_dir or os.path.dirname(input_path)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        output_paths = []
        for i, seg in enumerate(segments):
            output_path = os.path.join(output_dir, f"segment_{i:04d}.mp4")
            self.cut_segment(input_path, seg.start, seg.end, output_path)
            output_paths.append(output_path)
        
        return output_paths


class VideoEffects:
    def __init__(self, ffmpeg_path: str = 'ffmpeg'):
        self.ffmpeg_path = ffmpeg_path

    def scale(self, input_path: str, output_path: str, scale_factor: float = 1.1) -> str:
        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-vf', f'scale=iw*{scale_factor}:ih*{scale_factor}',
            '-c:a', 'copy',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def crop_center(self, input_path: str, output_path: str, 
                   crop_width: int, crop_height: int) -> str:
        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-vf', f'crop={crop_width}:{crop_height}',
            '-c:a', 'copy',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def zoom_pan(self, input_path: str, output_path: str,
                zoom_in: bool = True, duration: float = 5.0) -> str:
        zoom_level = 1.5 if zoom_in else 0.7
        direction = 'in' if zoom_in else 'out'
        
        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-vf', f'zoompan=z=\'{zoom_level}\':d={int(duration*25)}:s=iw*2:ih*2,trim=0:{duration}',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def adjust_speed(self, input_path: str, output_path: str, speed_factor: float) -> str:
        pts = 1.0 / speed_factor
        
        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-filter:v', f'setpts={pts}*PTS',
            '-af', f'atempo={speed_factor}',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def add_subtitles(self, input_path: str, output_path: str, 
                     subtitle_path: str, style: str = 'default') -> str:
        if style == 'burned':
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-vf', f'subtitles=\'{subtitle_path}\'',
                '-c:a', 'copy',
                '-y',
                output_path
            ]
        else:
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-vf', f'subtitles=\'{subtitle_path}\':force_style=\'FontSize=24,PrimaryColour=&HFFFFFF\'',
                '-c:a', 'copy',
                '-y',
                output_path
            ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path


class TimeSyncer:
    def __init__(self, ffmpeg_path: str = 'ffmpeg'):
        self.ffmpeg_path = ffmpeg_path

    def adjust_tts_to_video(self, tts_segments: List[dict], 
                           video_duration: float) -> List[dict]:
        adjusted_segments = []
        
        tts_total = sum(seg.get('duration', 0) for seg in tts_segments)
        if tts_total == 0:
            return tts_segments
        
        scale_factor = video_duration / tts_total
        
        current_time = 0
        for seg in tts_segments:
            duration = seg.get('duration', 1.0) * scale_factor
            adjusted_segments.append({
                'text': seg.get('text', ''),
                'start': current_time,
                'end': current_time + duration,
                'duration': duration
            })
            current_time += duration
        
        return adjusted_segments

    def adjust_speed_to_fit(self, audio_path: str, output_path: str,
                           target_duration: float) -> str:
        cmd = [
            self.ffmpeg_path,
            '-i', audio_path,
            '-filter:a', f'rubberband=tempo={target_duration}',
            '-y',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            cmd = [
                self.ffmpeg_path,
                '-i', audio_path,
                '-filter:a', f'atempo={target_duration}',
                '-y',
                output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
        
        return output_path

    def get_audio_duration(self, audio_path: str) -> float:
        cmd = [
            self.ffmpeg_path,
            '-i', audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stderr
        
        for line in output.split('\n'):
            if 'Duration:' in line:
                duration_str = line.split('Duration:')[1].split(',')[0].strip()
                parts = duration_str.split(':')
                if len(parts) == 3:
                    h, m, s = parts
                    return float(h) * 3600 + float(m) * 60 + float(s.split('.')[0])
        
        return 0.0