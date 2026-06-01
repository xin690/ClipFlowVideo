"""字幕保存工具 - 支持ASS/SRT/TXT格式"""

import os
from typing import List, Dict, Optional


class SubtitleSaver:
    """字幕文件保存工具"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save_all_formats(self, subtitles: List[Dict], 
                        base_name: str = "subtitles") -> Dict[str, str]:
        """保存所有格式的字幕文件"""
        results = {}
        
        # 保存ASS格式（带样式）
        ass_path = os.path.join(self.output_dir, f"{base_name}.ass")
        self.save_ass(subtitles, ass_path)
        results['ass'] = ass_path
        
        # 保存SRT格式
        srt_path = os.path.join(self.output_dir, f"{base_name}.srt")
        self.save_srt(subtitles, srt_path)
        results['srt'] = srt_path
        
        # 保存纯文本
        txt_path = os.path.join(self.output_dir, f"{base_name}.txt")
        self.save_txt(subtitles, txt_path)
        results['txt'] = txt_path
        
        return results
    
    def save_ass(self, subtitles: List[Dict], output_path: str) -> str:
        """生成带样式的ASS字幕"""
        ass_content = self._generate_ass_content(subtitles)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)
        return output_path
    
    def save_srt(self, subtitles: List[Dict], output_path: str) -> str:
        """生成SRT格式字幕"""
        srt_content = self._generate_srt_content(subtitles)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        return output_path
    
    def save_txt(self, subtitles: List[Dict], output_path: str) -> str:
        """保存纯文本"""
        text = '\n'.join([s['text'] for s in subtitles])
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return output_path
    
    def _generate_ass_content(self, subtitles: List[Dict]) -> str:
        """生成ASS字幕内容"""
        header = """[Script Info]
Title: ClipFlow Subtitle
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,32,&H00FFFFFF,&H000088EF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        for i, sub in enumerate(subtitles):
            start = self._format_ass_time(sub['start'])
            end = self._format_ass_time(sub['end'])
            text = self._escape_ass_text(sub['text'])
            events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")
        
        return header + '\n'.join(events)
    
    def _generate_srt_content(self, subtitles: List[Dict]) -> str:
        """生成SRT字幕内容"""
        lines = []
        for i, sub in enumerate(subtitles, 1):
            start = self._format_srt_time(sub['start'])
            end = self._format_srt_time(sub['end'])
            text = sub['text'].strip()
            lines.append(f"{i}\n{start} --> {end}\n{text}\n")
        return '\n'.join(lines)
    
    def _format_ass_time(self, seconds: float) -> str:
        """格式化ASS时间码 (H:MM:SS.CC)"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds % 1) * 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
    
    def _format_srt_time(self, seconds: float) -> str:
        """格式化SRT时间码 (HH:MM:SS,mmm)"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    
    def save_bilingual_ass(self, en_subtitles: List[Dict], zh_subtitles: List[Dict],
                           output_path: str = None) -> str:
        """生成中英双字幕ASS文件（英文在上、中文在下）"""
        if output_path is None:
            output_path = os.path.join(self.output_dir, "bilingual.ass")

        header = """[Script Info]
Title: ClipFlow Bilingual Subtitles
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: EnSub,Arial,24,&H99FFFFFF,&H000088EF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,2,2,20,20,95,1
Style: ZhSub,Arial,36,&H00FFFFFF,&H000088EF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,2,2,20,20,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        min_len = min(len(en_subtitles), len(zh_subtitles))
        for i in range(min_len):
            en = en_subtitles[i]
            zh = zh_subtitles[i]
            start = self._format_ass_time(en['start'])
            end = self._format_ass_time(en['end'])
            en_text = self._escape_ass_text(en['text'])
            zh_text = self._escape_ass_text(zh['text'])
            events.append(f"Dialogue: 0,{start},{end},EnSub,,0,0,0,,{en_text}")
            events.append(f"Dialogue: 0,{start},{end},ZhSub,,0,0,0,,{zh_text}")

        content = header + '\n'.join(events)
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return output_path

    def _escape_ass_text(self, text: str) -> str:
        """转义ASS特殊字符"""
        text = text.replace('\\', '\\\\')
        text = text.replace('{', '\\{')
        text = text.replace('}', '\\}')
        text = text.replace('\n', '\\N')
        return text


def download_youtube_subtitles(url: str, output_dir: str) -> Optional[List[Dict]]:
    """尝试从YouTube下载字幕"""
    try:
        import yt_dlp
        
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['zh-Hans', 'zh-Hant', 'en', 'zh'],
            'subtitlesformat': 'srt',
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 检查是否有字幕
            subtitles = info.get('subtitles') or {}
            auto_subs = info.get('automatic_captions') or {}
            
            # 优先使用手动字幕
            all_subs = {**auto_subs, **subtitles}
            
            for lang in ['zh-Hans', 'zh-Hant', 'zh', 'en']:
                if lang in all_subs:
                    # 下载字幕
                    ydl.download([url])
                    
                    # 查找下载的字幕文件
                    video_id = info.get('id', 'subtitle')
                    srt_file = os.path.join(output_dir, f"{video_id}.{lang}.srt")
                    
                    if os.path.exists(srt_file):
                        return parse_srt_file(srt_file)
            
            return None
    except Exception:
        return None


def parse_srt_file(srt_path: str) -> List[Dict]:
    """解析SRT文件"""
    try:
        import pysrt
        subs = pysrt.open(srt_path, encoding='utf-8')
        result = []
        for sub in subs:
            text = sub.text.strip()
            if text:
                result.append({
                    'start': sub.start.ordinal / 1000.0,
                    'end': sub.end.ordinal / 1000.0,
                    'text': text
                })
        return result
    except Exception:
        return []