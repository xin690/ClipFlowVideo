from dataclasses import dataclass
from typing import List, Optional
import os


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str
    words: Optional[List[dict]] = None

    def to_dict(self) -> dict:
        return {
            'start': self.start,
            'end': self.end,
            'text': self.text
        }


@dataclass
class TranscriptionResult:
    segments: List[TranscriptSegment]
    language: str
    full_text: str

    def to_json(self) -> List[dict]:
        return [seg.to_dict() for seg in self.segments]

    def to_srt_format(self) -> str:
        import srt
        
        subs = []
        for i, seg in enumerate(self.segments, 1):
            start_t = srt.timedelta(seconds=max(0, seg.start))
            end_t = srt.timedelta(seconds=seg.end)
            subs.append(srt.Subtitle(index=i, start=start_t, end=end_t, content=seg.text))
        
        return srt.compose(subs)


class WhisperASR:
    def __init__(self, model_name: str = 'base', device: str = 'cpu', compute_type: str = 'float32'):
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.model = None
        self._available = None

    def _check_availability(self) -> bool:
        if self._available is not None:
            return self._available
        
        try:
            import whisperx
            self._available = True
        except ImportError:
            try:
                import faster_whisper
                self._available = True
            except ImportError:
                self._available = False
        
        return self._available

    def is_available(self) -> bool:
        return self._check_availability()

    def load_model(self):
        if self.model is not None:
            return
        
        if not self._check_availability():
            raise RuntimeError("WhisperX和faster-whisper都未安装。请运行: pip install faster-whisper")

        try:
            import whisperx
            self.model = whisperx.load_model(self.model_name, self.device, compute_type=self.compute_type)
            self.model_type = 'whisperx'
        except ImportError:
            import faster_whisper
            model_size = self._get_faster_whisper_model()
            self.model = faster_whisper.BetterTransformer.load(model_size)
            self.model_type = 'faster_whisper'

    def _get_faster_whisper_model(self) -> str:
        model_map = {
            'tiny': 'tiny',
            'base': 'base',
            'small': 'small',
            'medium': 'medium',
            'large': 'large-v3'
        }
        return model_map.get(self.model_name, 'base')

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> TranscriptionResult:
        if not self._check_availability():
            raise RuntimeError("WhisperX和faster-whisper都未安装。ASR功能不可用。")

        self.load_model()
        
        if self.model_type == 'whisperx':
            return self._transcribe_whisperx(audio_path, language)
        else:
            return self._transcribe_faster_whisper(audio_path, language)

    def _transcribe_whisperx(self, audio_path: str, language: Optional[str] = None) -> TranscriptionResult:
        import whisperx
        
        audio = whisperx.load_audio(audio_path)
        result = self.model.transcribe(audio, language=language, batch_size=16)
        
        segments = []
        full_text_parts = []
        
        for seg in result.get('segments', []):
            text = seg.get('text', '').strip()
            if text:
                segments.append(TranscriptSegment(
                    start=seg.get('start', 0.0),
                    end=seg.get('end', 0.0),
                    text=text
                ))
                full_text_parts.append(text)
        
        return TranscriptionResult(
            segments=segments,
            language=result.get('language', 'en'),
            full_text=' '.join(full_text_parts)
        )

    def _transcribe_faster_whisper(self, audio_path: str, language: Optional[str] = None) -> TranscriptionResult:
        import faster_whisper
        
        lang_code = language.split('-')[0] if language else None
        
        segments, info = self.model.transcribe(
            audio_path,
            language=lang_code,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        result_segments = []
        full_text_parts = []
        
        for seg in segments:
            text = seg.text.strip()
            if text:
                result_segments.append(TranscriptSegment(
                    start=seg.start,
                    end=seg.end,
                    text=text
                ))
                full_text_parts.append(text)
        
        return TranscriptionResult(
            segments=result_segments,
            language=info.language if info else 'en',
            full_text=' '.join(full_text_parts)
        )

    def transcribe_with_timestamps(self, audio_path: str, language: Optional[str] = None) -> List[dict]:
        result = self.transcribe(audio_path, language)
        return result.to_json()

    def batch_transcribe(self, audio_paths: List[str], language: Optional[str] = None) -> List[TranscriptionResult]:
        self.load_model()
        results = []
        
        for audio_path in audio_paths:
            try:
                result = self.transcribe(audio_path, language)
                results.append(result)
            except Exception as e:
                print(f"Error transcribing {audio_path}: {e}")
                results.append(TranscriptionResult(segments=[], language='en', full_text=''))
        
        return results

    @staticmethod
    def get_available_models() -> List[str]:
        return ['tiny', 'base', 'small', 'medium', 'large']

    @staticmethod
    def get_available_devices() -> List[str]:
        return ['cpu', 'cuda']


def create_asr(model_name: str = 'base', device: str = 'cpu') -> WhisperASR:
    asr = WhisperASR(model_name=model_name, device=device)
    if not asr.is_available():
        print("警告: WhisperX和faster-whisper都不可用，ASR功能将受限")
    return asr