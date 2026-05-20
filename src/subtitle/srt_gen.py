from dataclasses import dataclass
from typing import List, Optional
import pysrt


@dataclass
class SubtitleLine:
    index: int
    start: float
    end: float
    text: str
    style: Optional[dict] = None


class SRTSubtitle:
    def __init__(self):
        self.subs = []

    def add(self, start: float, end: float, text: str, style: Optional[dict] = None):
        self.subs.append(SubtitleLine(
            index=len(self.subs) + 1,
            start=start,
            end=end,
            text=text,
            style=style
        ))

    def add_from_segments(self, segments: List[dict]):
        for seg in segments:
            self.add(
                start=seg.get('start', 0),
                end=seg.get('end', 0),
                text=seg.get('text', ''),
                style=seg.get('style')
            )

    def to_srt(self, path: Optional[str] = None) -> str:
        subs = pysrt.SubRipFile()
        
        for sub in self.subs:
            start = pysrt.SubRipTime(seconds=max(0, sub.start))
            end = pysrt.SubRipTime(seconds=max(0, sub.end))
            
            item = pysrt.SubRipItem(
                index=sub.index,
                start=start,
                end=end,
                text=sub.text
            )
            subs.append(item)
        
        srt_content = pysrt.compose(subs)
        
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
        
        return srt_content

    def to_ass(self, path: Optional[str] = None) -> str:
        ass_content = self._generate_ass()
        
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(ass_content)
        
        return ass_content

    def _generate_ass(self) -> str:
        styles = """[Script Info]
Title: ClipFlow Subtitle
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000088EF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,30,1
Style: Highlight,Arial,22,&H00FFFFFF,&H0000FFFF,&H00FF0000,&H00000000,-1,0,0,0,100,100,0,0,1,3,2,2,10,10,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        for sub in self.subs:
            start_t = self._format_ass_time(sub.start)
            end_t = self._format_ass_time(sub.end)
            text = sub.text.replace('\n', '\\N')
            style = 'Highlight' if sub.style and sub.style.get('highlight') else 'Default'
            events.append(f"Dialogue: 0,{start_t},{end_t},{style},,0,0,0,,{text}")
        
        return styles + '\n'.join(events)

    def _format_ass_time(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds % 1) * 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    def export(self, path: str, format: str = 'srt'):
        if format.lower() == 'srt':
            self.to_srt(path)
        elif format.lower() == 'ass':
            self.to_ass(path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def load(path: str) -> 'SRTSubtitle':
        subs = pysrt.open(path, encoding='utf-8')
        subtitle = SRTSubtitle()
        
        for sub in subs:
            subtitle.add(
                start=sub.start.ordinal / 1000,
                end=sub.end.ordinal / 1000,
                text=str(sub.text).replace('<i>', '').replace('</i>', '')
            )
        
        return subtitle

    def split_long_lines(self, max_chars: int = 20):
        new_subs = []
        
        for sub in self.subs:
            if len(sub.text) <= max_chars:
                new_subs.append(sub)
            else:
                words = sub.text.split()
                current_line = []
                current_len = 0
                
                for word in words:
                    if current_len + len(word) + 1 <= max_chars:
                        current_line.append(word)
                        current_len += len(word) + 1
                    else:
                        if current_line:
                            line_text = ' '.join(current_line)
                            duration = sub.end - sub.start
                            mid = sub.start + duration * (len(current_line) / len(words))
                            new_subs.append(SubtitleLine(
                                index=sub.index,
                                start=sub.start,
                                end=mid,
                                text=line_text,
                                style=sub.style
                            ))
                        current_line = [word]
                        current_len = len(word)
                        sub.start = mid
                
                if current_line:
                    new_subs.append(SubtitleLine(
                        index=sub.index,
                        start=sub.start,
                        end=sub.end,
                        text=' '.join(current_line),
                        style=sub.style
                    ))
        
        self.subs = new_subs
        for i, sub in enumerate(self.subs):
            sub.index = i + 1

    def get_duration(self) -> float:
        if not self.subs:
            return 0.0
        return max(sub.end for sub in self.subs)