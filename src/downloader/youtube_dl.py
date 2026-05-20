import os
import tempfile
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path
import yt_dlp


@dataclass
class VideoInfo:
    title: str
    duration: float
    width: int
    height: int
    fps: float
    filesize: int
    url: str
    thumbnail: Optional[str] = None
    description: Optional[str] = None


@dataclass
class DownloadResult:
    success: bool
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    info: Optional[VideoInfo] = None
    error: Optional[str] = None


class VideoDownloader:
    SUPPORTED_PLATFORMS = [
        'youtube', 'tiktok', 'bilibili', 'twitter', 'instagram', 'xvideos', 'pornhub'
    ]

    def __init__(self, output_dir: Optional[str] = None, quality: str = 'best'):
        self.output_dir = output_dir or tempfile.mkdtemp(prefix='clipflow_')
        self.quality = quality
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def _get_ydl_opts(self, format_spec: str = 'best') -> Dict[str, Any]:
        return {
            'format': format_spec,
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'writeinfojson': True,
            'writethumbnail': True,
            'embedthumbnail': True,
            'postprocessors': [{
                'key': 'FFmpegEmbedSubtitle',
            }],
            'ignoreerrors': False,
            'no_warnings': False,
            'quiet': False,
        }

    def get_info(self, url: str) -> VideoInfo:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return VideoInfo(
                title=info.get('title', 'Unknown'),
                duration=info.get('duration', 0.0),
                width=info.get('width', 0),
                height=info.get('height', 0),
                fps=info.get('fps', 0),
                filesize=info.get('filesize', 0),
                url=url,
                thumbnail=info.get('thumbnail'),
                description=info.get('description', '')
            )

    def download(self, url: str, format_spec: Optional[str] = None) -> DownloadResult:
        format_spec = format_spec or self._get_default_format()
        
        ydl_opts = self._get_ydl_opts(format_spec)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                video_path = ydl.prepare_filename(info)
                if not os.path.exists(video_path):
                    for ext in ['mp4', 'mkv', 'webm']:
                        alt_path = video_path.rsplit('.', 1)[0] + '.' + ext
                        if os.path.exists(alt_path):
                            video_path = alt_path
                            break

                return DownloadResult(
                    success=True,
                    video_path=video_path,
                    info=VideoInfo(
                        title=info.get('title', 'Unknown'),
                        duration=info.get('duration', 0.0),
                        width=info.get('width', 0),
                        height=info.get('height', 0),
                        fps=info.get('fps', 0),
                        filesize=info.get('filesize', 0),
                        url=url,
                        thumbnail=info.get('thumbnail'),
                        description=info.get('description', '')
                    )
                )
        except Exception as e:
            return DownloadResult(success=False, error=str(e))

    def download_audio_only(self, url: str, output_format: str = 'mp3') -> DownloadResult:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': output_format,
                'preferredquality': '192',
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                audio_path = ydl.prepare_filename(info)
                if output_format != info.get('ext', 'mp3'):
                    audio_path = audio_path.rsplit('.', 1)[0] + '.' + output_format

                return DownloadResult(
                    success=True,
                    audio_path=audio_path,
                    info=VideoInfo(
                        title=info.get('title', 'Unknown'),
                        duration=info.get('duration', 0.0),
                        width=info.get('width', 0),
                        height=info.get('height', 0),
                        fps=info.get('fps', 0),
                        filesize=0,
                        url=url
                    )
                )
        except Exception as e:
            return DownloadResult(success=False, error=str(e))

    def _get_default_format(self) -> str:
        if self.quality == 'best':
            return 'bestvideo+bestaudio/best'
        elif self.quality == '720p':
            return 'bestvideo[height<=720]+bestaudio/best[height<=720]'
        elif self.quality == '480p':
            return 'bestvideo[height<=480]+bestaudio/best[height<=480]'
        return 'bestvideo+bestaudio/best'

    def is_supported(self, url: str) -> bool:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            try:
                ydl.extract_info(url, download=False)
                return True
            except Exception:
                return False