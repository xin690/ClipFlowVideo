from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path
import os
import tempfile

from ..downloader.youtube_dl import VideoDownloader, DownloadResult, VideoInfo
from ..audio.extractor import AudioExtractor
from ..asr.whisperx import WhisperASR, TranscriptionResult
from ..llm.base import SubtitleItem, RewriteResult
from ..llm.openai_llm import OpenAILLM, DeepSeekLLM, OpenRouterLLM
from ..tts.edge_tts import EdgeTTS, TTSSegment, TTSResult
from ..subtitle.srt_gen import SRTSubtitle
from ..editor.clipper import VideoClipper, VideoEffects, TimeSyncer
from ..exporter.video_export import VideoExporter


LLM_PROVIDERS = {
    'openai': OpenAILLM,
    'deepseek': DeepSeekLLM,
    'openrouter': OpenRouterLLM
}


@dataclass
class PipelineConfig:
    output_dir: str
    llm_provider: str = 'deepseek'
    llm_api_key: Optional[str] = None
    llm_model: str = 'deepseek-chat'
    tts_voice: str = 'zh-CN-XiaoxiaoNeural'
    asr_model: str = 'base'
    quality: str = 'best'
    ffmpeg_path: str = 'ffmpeg'


@dataclass
class PipelineResult:
    success: bool
    original_video: Optional[str] = None
    audio_path: Optional[str] = None
    subtitles: Optional[TranscriptionResult] = None
    rewritten_subtitles: Optional[List[RewriteResult]] = None
    tts_audios: Optional[List[TTSResult]] = None
    final_video: Optional[str] = None
    error: Optional[str] = None
    info: Optional[VideoInfo] = None


class ClipFlowPipeline:
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig(output_dir=tempfile.mkdtemp(prefix='clipflow_'))
        
        self.downloader = VideoDownloader(
            output_dir=self.config.output_dir,
            quality=self.config.quality
        )
        self.audio_extractor = AudioExtractor(ffmpeg_path=self.config.ffmpeg_path)
        self.asr = WhisperASR(model_name=self.config.asr_model)
        self.tts = EdgeTTS(voice=self.config.tts_voice, output_dir=self.config.output_dir)
        self.clipper = VideoClipper(ffmpeg_path=self.config.ffmpeg_path)
        self.effects = VideoEffects(ffmpeg_path=self.config.ffmpeg_path)
        self.syncer = TimeSyncer(ffmpeg_path=self.config.ffmpeg_path)
        self.exporter = VideoExporter(ffmpeg_path=self.config.ffmpeg_path)
        
        self.llm = self._init_llm()

    def _init_llm(self):
        provider_class = LLM_PROVIDERS.get(self.config.llm_provider, DeepSeekLLM)
        if self.config.llm_provider == 'openai':
            return provider_class(api_key=self.config.llm_api_key, model=self.config.llm_model)
        elif self.config.llm_provider == 'deepseek':
            return provider_class(api_key=self.config.llm_api_key, model=self.config.llm_model)
        else:
            return provider_class(api_key=self.config.llm_api_key)

    def run(self, url: str, rewrite: bool = True, add_subtitle: bool = True) -> PipelineResult:
        try:
            result = PipelineResult(success=True)
            
            download_result = self.downloader.download(url)
            if not download_result.success:
                return PipelineResult(success=False, error=f"Download failed: {download_result.error}")
            
            result.original_video = download_result.video_path
            result.info = download_result.info
            
            audio_path = self.audio_extractor.extract_audio_wav(download_result.video_path)
            result.audio_path = audio_path
            
            transcription = self.asr.transcribe(audio_path)
            result.subtitles = transcription
            
            subtitle_items = [
                SubtitleItem(start=seg.start, end=seg.end, text=seg.text)
                for seg in transcription.segments
            ]
            
            if rewrite and self.llm.is_available():
                rewritten = self.llm.rewrite(subtitle_items, style='commentary')
                result.rewritten_subtitles = rewritten
                
                tts_segments = [
                    TTSSegment(
                        text=rw.rewritten,
                        start=rw.start,
                        end=rw.end,
                        duration=rw.end - rw.start
                    )
                    for rw in rewritten
                ]
            else:
                tts_segments = [
                    TTSSegment(
                        text=seg.text,
                        start=seg.start,
                        end=seg.end,
                        duration=seg.end - seg.start
                    )
                    for seg in transcription.segments
                ]
            
            tts_results = self.tts.synthesize_segments(tts_segments)
            result.tts_audios = tts_results
            
            srt_subtitle = SRTSubtitle()
            for seg in transcription.segments:
                srt_subtitle.add(seg.start, seg.end, seg.text)
            
            srt_path = os.path.join(self.config.output_dir, 'subtitles.srt')
            srt_subtitle.to_srt(srt_path)
            
            merged_video = self.exporter.merge_video_audio(
                download_result.video_path,
                tts_results[0].audio_path if tts_results else audio_path
            )
            
            if add_subtitle:
                final_video = self.exporter.export_with_subtitle(merged_video, srt_path)
            else:
                final_video = merged_video
            
            result.final_video = final_video
            
            return result
            
        except Exception as e:
            return PipelineResult(success=False, error=str(e))

    def download_only(self, url: str) -> DownloadResult:
        return self.downloader.download(url)

    def transcribe_only(self, video_path: str) -> TranscriptionResult:
        audio_path = self.audio_extractor.extract_audio_wav(video_path)
        return self.asr.transcribe(audio_path)

    def rewrite_subtitles(self, subtitles: List[SubtitleItem], 
                         style: str = 'commentary') -> List[RewriteResult]:
        return self.llm.rewrite(subtitles, style=style)

    def generate_tts(self, segments: List[TTSSegment]) -> List[TTSResult]:
        return self.tts.synthesize_segments(segments)

    def export_final(self, video_path: str, audio_path: str, 
                    subtitle_path: Optional[str] = None) -> str:
        merged = self.exporter.merge_video_audio(video_path, audio_path)
        
        if subtitle_path:
            return self.exporter.export_with_subtitle(merged, subtitle_path)
        return merged


def create_pipeline(output_dir: str = None, **kwargs) -> ClipFlowPipeline:
    config = PipelineConfig(
        output_dir=output_dir or tempfile.mkdtemp(prefix='clipflow_'),
        **kwargs
    )
    return ClipFlowPipeline(config)