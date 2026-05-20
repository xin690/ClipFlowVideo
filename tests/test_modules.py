import sys
import os
import pytest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.downloader.youtube_dl import VideoDownloader, VideoInfo, DownloadResult
from src.audio.extractor import AudioExtractor
from src.subtitle.srt_gen import SRTSubtitle, SubtitleLine
from src.llm.base import SubtitleItem, LLMPromptBuilder
from src.editor.clipper import VideoClipper, VideoEffects, TimeSyncer
from src.exporter.video_export import VideoExporter


class TestDownloader:
    def test_init(self):
        downloader = VideoDownloader()
        assert downloader is not None
        assert len(downloader.SUPPORTED_PLATFORMS) > 0

    def test_check_supported_platforms(self):
        downloader = VideoDownloader()
        assert 'youtube' in downloader.SUPPORTED_PLATFORMS
        assert 'tiktok' in downloader.SUPPORTED_PLATFORMS


class TestAudioExtractor:
    def test_init(self):
        extractor = AudioExtractor()
        assert extractor is not None


class TestSRTSubtitle:
    def test_create_subtitle(self):
        subtitle = SRTSubtitle()
        subtitle.add(0.0, 2.5, "Hello World")
        subtitle.add(2.5, 5.0, "This is a test")
        
        assert len(subtitle.subs) == 2
        assert subtitle.subs[0].text == "Hello World"
        assert subtitle.subs[1].start == 2.5

    def test_to_srt(self):
        subtitle = SRTSubtitle()
        subtitle.add(0.0, 2.5, "Hello")
        subtitle.add(2.5, 5.0, "World")
        
        srt_content = subtitle.to_srt()
        
        assert "1" in srt_content
        assert "00:00:00,000" in srt_content
        assert "Hello" in srt_content
        assert "World" in srt_content

    def test_load_srt(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False) as f:
            f.write("""1
00:00:00,000 --> 00:00:02,500
Hello

2
00:00:02,500 --> 00:00:05,000
World
""")
            temp_path = f.name
        
        try:
            subtitle = SRTSubtitle.load(temp_path)
            assert len(subtitle.subs) == 2
        finally:
            os.unlink(temp_path)


class TestLLMPromptBuilder:
    def test_build_rewrite_prompt(self):
        builder = LLMPromptBuilder()
        subtitles = [
            SubtitleItem(start=0.0, end=2.0, text="Hello everyone"),
            SubtitleItem(start=2.0, end=4.0, text="Welcome to my channel")
        ]
        
        prompt = builder.build_rewrite_prompt(subtitles)
        
        assert "Hello everyone" in prompt
        assert "Welcome to my channel" in prompt

    def test_build_commentary_prompt(self):
        builder = LLMPromptBuilder()
        prompt = builder.build_commentary_prompt("AI technology", 60.0, "exciting")
        
        assert "AI technology" in prompt


class TestVideoClipper:
    def test_init(self):
        clipper = VideoClipper()
        assert clipper is not None


class TestVideoEffects:
    def test_init(self):
        effects = VideoEffects()
        assert effects is not None


class TestTimeSyncer:
    def test_adjust_tts_to_video(self):
        syncer = TimeSyncer()
        
        tts_segments = [
            {'text': 'Hello', 'duration': 2.0},
            {'text': 'World', 'duration': 2.0}
        ]
        
        adjusted = syncer.adjust_tts_to_video(tts_segments, 10.0)
        
        assert len(adjusted) == 2
        assert adjusted[0]['start'] == 0
        assert adjusted[1]['duration'] > 0


class TestVideoExporter:
    def test_init(self):
        exporter = VideoExporter()
        assert exporter is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])