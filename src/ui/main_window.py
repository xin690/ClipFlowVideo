from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QTextEdit, QLineEdit, QProgressBar,
                              QGroupBox, QComboBox, QCheckBox, QFileDialog, QMessageBox,
                              QStatusBar, QMenuBar, QMenu)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon, QFont
import os
import sys
import subprocess
import re

# 导入日志模块
try:
    from src.utils.logger import get_log_file, log_debug, log_info, log_error
except ImportError:
    try:
        from utils.logger import get_log_file, log_debug, log_info, log_error
    except ImportError:
        # 如果日志模块不可用，定义空函数
        def get_log_file():
            return None
        def log_debug(msg): pass
        def log_info(msg): pass
        def log_error(msg): pass


def get_ffmpeg_path():
    """获取ffmpeg可执行文件路径"""
    # 检查多个可能的路径
    possible_paths = []
    
    if getattr(sys, 'frozen', False):
        # 1. exe同级目录下的ffmpeg（最优先）
        exe_dir = os.path.dirname(sys.executable)
        possible_paths.append(os.path.join(exe_dir, 'ffmpeg', 'ffmpeg.exe'))
        # 2. PyInstaller临时解压目录
        possible_paths.append(os.path.join(sys._MEIPASS, 'ffmpeg', 'ffmpeg.exe'))
        # 3. exe目录下直接
        possible_paths.append(os.path.join(exe_dir, 'ffmpeg.exe'))
    else:
        # 开发环境
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        possible_paths.append(os.path.join(src_dir, 'ffmpeg', 'ffmpeg.exe'))
        possible_paths.append(os.path.join(src_dir, '..', 'build', 'ffmpeg', 'ffmpeg.exe'))
    
    # 测试PATH中的ffmpeg
    possible_paths.append('ffmpeg')
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return 'ffmpeg'


def check_ffmpeg():
    """检查ffmpeg是否可用"""
    try:
        result = subprocess.run(
            [get_ffmpeg_path(), '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def get_llm_client(config_manager=None):
    """获取LLM客户端"""
    if config_manager is None:
        return None
    
    provider = config_manager.get('llm_provider', 'deepseek')
    api_key = config_manager.get_api_key(provider)
    
    if not api_key:
        return None
    
    try:
        if provider == 'deepseek':
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            client.models.list()
            return client
        elif provider == 'openai':
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            client.models.list()
            return client
        elif provider == 'openrouter':
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
            client.models.list()
            return client
    except Exception as e:
        return None
    
    return None


def get_llm_model(config_manager=None):
    """获取LLM模型名"""
    if config_manager is None:
        return 'deepseek-chat'
    
    provider = config_manager.get('llm_provider', 'deepseek')
    
    model_map = {
        'deepseek': 'deepseek-chat',
        'openai': 'gpt-3.5-turbo',
        'openrouter': 'openai/gpt-3.5-turbo'
    }
    
    return model_map.get(provider, 'deepseek-chat')


class WorkerThread(QThread):
    progress_update = pyqtSignal(str, int)
    finished = pyqtSignal(bool, str)
    log_message = pyqtSignal(str)

    def __init__(self, url, output_dir, config_manager=None, parent=None):
        super().__init__(parent)
        self.url = url
        self.output_dir = output_dir
        self.config_manager = config_manager
        self._init_log()

    def _init_log(self):
        """初始化日志文件"""
        log_file = get_log_file()
        if log_file:
            self.log_message.emit(f"日志文件: {log_file}")
            log_info(f"=== 开始处理视频: {self.url} ===")

    def _emit_log(self, msg):
        """同时输出到UI和日志文件"""
        self.log_message.emit(msg)
        log_info(msg)

    def run(self):
        try:
            self._emit_log(f"开始处理视频: {self.url}")
            self.progress_update.emit("正在下载视频...", 10)
            log_info(f"输出目录: {self.output_dir}")
            
            if not check_ffmpeg():
                self._emit_log("警告: ffmpeg未正确配置，某些功能可能受限")
            
            # 下载视频，获取视频ID和目录
            download_result = self._download_video(self.url)
            if not download_result[0]:
                self.finished.emit(False, "视频下载失败")
                return
            
            video_path, video_dir, video_id, download_subtitles = download_result
            
            if download_subtitles:
                self._emit_log(f"视频下载完成（含字幕: {len(download_subtitles)}条）")
                subtitles = download_subtitles
                need_full_processing = True
            else:
                self._emit_log(f"视频下载完成")
                need_full_processing = False
            
            # 提取音频
            self.progress_update.emit("正在提取音频...", 30)
            audio_path = self._extract_audio_to_dir(video_path, video_dir, video_id)
            if not audio_path:
                self.finished.emit(False, "音频提取失败")
                return
            self._emit_log("音频提取完成")
            
            if not download_subtitles:
                # 使用faster-whisper识别
                self.progress_update.emit("正在进行语音识别...", 50)
                subtitles = self._transcribe_audio(audio_path)
                
                if subtitles:
                    self._emit_log(f"识别到 {len(subtitles)} 条字幕")
                    need_full_processing = True
                    
                    # 保存字幕文件
                    self._emit_log("正在保存字幕文件...")
                    self._save_subtitles(subtitles, video_dir)
                else:
                    self._emit_log("提示: 未识别到字幕，将保留原视频音频")
            
            # AI改写（保存原文用于双字幕）
            en_subtitles = None
            if need_full_processing and subtitles:
                self.progress_update.emit("正在进行AI改写...", 60)
                en_subtitles = [dict(s) for s in subtitles]
                subtitles = self._rewrite_with_llm(subtitles)
            
            # 生成配音
            self.progress_update.emit("正在生成配音...", 70)
            
            tts_path = None
            if need_full_processing and subtitles:
                self._emit_log(f"准备生成TTS，共 {len(subtitles)} 条字幕")
                tts_path = self._generate_tts_to_dir(subtitles, video_dir)
                if tts_path and os.path.exists(tts_path):
                    tts_size = os.path.getsize(tts_path)
                    self._emit_log(f"TTS文件已生成: {tts_size} bytes")
                    self._emit_log("配音生成完成")
                else:
                    self._emit_log("配音生成失败，回退到保留原音频")
                    need_full_processing = False
                    tts_path = audio_path
            else:
                tts_path = audio_path
                self._emit_log("使用原视频音频")
            
            # 生成中英双字幕用于烧录
            subtitle_burn_path = None
            if need_full_processing and subtitles and en_subtitles:
                try:
                    from src.ui.subtitle_saver import SubtitleSaver
                    saver = SubtitleSaver(video_dir)
                    # 保存改写后的中文单独SRT/TXT
                    saver.save_srt(subtitles, os.path.join(video_dir, "rewritten_zh.srt"))
                    saver.save_txt(subtitles, os.path.join(video_dir, "rewritten_zh.txt"))
                    # 生成中英双字幕ASS
                    bilingual_ass = saver.save_bilingual_ass(en_subtitles, subtitles)
                    if os.path.exists(bilingual_ass):
                        subtitle_burn_path = bilingual_ass
                        self._emit_log(f"中英双字幕已生成: {bilingual_ass}")
                    else:
                        self._emit_log("双字幕文件生成失败，跳过烧录")
                except Exception as e:
                    self._emit_log(f"双字幕生成失败: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 合成视频（包含字幕烧录）
            self.progress_update.emit("正在合成最终视频...", 90)
            self._emit_log("=== 开始视频合成 ===")
            self._emit_log(f"  视频: {video_path}")
            self._emit_log(f"  音频: {tts_path}")
            self._emit_log(f"  字幕: {subtitle_burn_path}")
            final_path = self._merge_video_to_dir(video_path, tts_path, video_dir, video_id, subtitle_burn_path)
            if not final_path:
                self.finished.emit(False, "视频合成失败")
                return
            
            mode = "AI配音" if need_full_processing else "原音保留"
            self._emit_log(f"处理完成! (模式: {mode})")
            self._emit_log(f"输出: {final_path}")
            self.progress_update.emit("完成", 100)
            self.finished.emit(True, final_path)
            
        except Exception as e:
            self._emit_log(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()
            log_error(f"处理异常: {str(e)}")
            log_error(traceback.format_exc())
            self.finished.emit(False, str(e))

    def _extract_audio_to_dir(self, video_path, video_dir, video_id):
        """提取音频到指定目录"""
        try:
            audio_path = os.path.join(video_dir, f"{video_id}.wav")
            cmd = [
                get_ffmpeg_path(), '-i', video_path,
                '-vn', '-acodec', 'pcm_s16le',
                '-ar', '16000', '-ac', '1',
                '-y', audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.log_message.emit(f"ffmpeg错误: {result.stderr}")
                return None
            return audio_path
        except FileNotFoundError:
            self.log_message.emit("错误: 找不到ffmpeg.exe")
            return None
        except Exception as e:
            self._emit_log(f"音频提取错误: {e}")
            return None

    def _save_subtitles(self, subtitles, video_dir):
        """保存字幕文件"""
        try:
            # 尝试多种导入方式
            try:
                from src.ui.subtitle_saver import SubtitleSaver
            except ImportError:
                try:
                    from .subtitle_saver import SubtitleSaver
                except ImportError:
                    import sys
                    import os
                    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    if parent_dir not in sys.path:
                        sys.path.insert(0, parent_dir)
                    from subtitle_saver import SubtitleSaver
            
            saver = SubtitleSaver(video_dir)
            results = saver.save_all_formats(subtitles, "subtitles")
            
            for fmt, path in results.items():
                self._emit_log(f"已保存 {fmt.upper()} 字幕: {path}")
                
        except Exception as e:
            self._emit_log(f"字幕保存错误: {e}")

    def _generate_tts_to_dir(self, subtitles, video_dir):
        """生成配音到指定目录"""
        try:
            import asyncio
            import edge_tts
            
            output_path = os.path.join(video_dir, "tts_output.mp3")
            
            if subtitles:
                all_text = ' '.join([s['text'] for s in subtitles])
            else:
                self._emit_log("警告: 无字幕文本，跳过TTS生成")
                return None
            
            self._emit_log(f"TTS文本长度: {len(all_text)} 字符")
            
            async def main():
                communicate = edge_tts.Communicate(
                    all_text,
                    "zh-CN-XiaoxiaoNeural"
                )
                await communicate.save(output_path)
            
            asyncio.run(main())
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                self._emit_log(f"TTS文件已生成: {file_size} bytes")
                return output_path
            else:
                self._emit_log("错误: TTS文件未生成")
                return None
            
        except ImportError:
            self._emit_log("错误: edge-tts未安装")
            return None
        except Exception as e:
            self._emit_log(f"TTS错误: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _get_video_resolution(self, video_path):
        """用ffprobe获取视频分辨率"""
        ffmpeg_path = get_ffmpeg_path()
        ffprobe_path = ffmpeg_path.replace('ffmpeg.exe', 'ffprobe.exe')
        if not os.path.exists(ffprobe_path):
            for alt in ['ffprobe.exe', 'ffprobe',
                        os.path.join(os.path.dirname(ffmpeg_path), 'ffprobe.exe')]:
                if os.path.exists(alt):
                    ffprobe_path = alt
                    break
            else:
                ffprobe_path = 'ffprobe'
        try:
            cmd = [ffprobe_path, '-v', 'error', '-select_streams', 'v:0',
                   '-show_entries', 'stream=width,height', '-of', 'csv=p=0', video_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            out = result.stdout.strip()
            if not out or ',' not in out:
                return 1920, 1080
            w, h = out.split(',')
            return int(w), int(h)
        except Exception:
            return 1920, 1080

    def _merge_video_to_dir(self, video_path, audio_path, video_dir, video_id, subtitle_path=None):
        """合并视频到指定目录，支持字幕烧录"""
        if not audio_path:
            self._emit_log("错误: audio_path为空")
            return None
        
        try:
            merged_path = os.path.join(video_dir, f"{video_id}_merged.mp4")
            
            self._emit_log("检查文件...")
            self._emit_log(f"  视频: {video_path} ({os.path.exists(video_path)})")
            self._emit_log(f"  音频: {audio_path} ({os.path.exists(audio_path)})")
            if subtitle_path:
                self._emit_log(f"  字幕: {subtitle_path} ({os.path.exists(subtitle_path)})")
            
            if subtitle_path and os.path.exists(subtitle_path):
                self._emit_log(f"烧录中英双字幕并替换音频")
                # 获取视频分辨率
                width, height = self._get_video_resolution(video_path)
                self._emit_log(f"  视频分辨率: {width}x{height}")
                # 拷贝字幕到输出目录 → 用相对路径避免冒号解析问题
                burn_name = "bilingual.ass"
                burn_dest = os.path.join(video_dir, burn_name)
                if os.path.normpath(subtitle_path) != os.path.normpath(burn_dest):
                    import shutil
                    shutil.copy2(subtitle_path, burn_dest)
                    self._emit_log(f"  字幕已拷贝: {burn_dest}")
                else:
                    self._emit_log(f"  字幕已在目标目录，跳过拷贝")
                cmd = [
                    get_ffmpeg_path(), '-hide_banner', '-loglevel', 'error',
                    '-i', video_path, '-i', audio_path,
                    '-map', '0:v', '-map', '1:a',
                    '-vf', f'subtitles={burn_name}:original_size={width}x{height}',
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                    '-c:a', 'aac', '-b:a', '192k',
                    '-shortest', '-y', merged_path
                ]
            else:
                self._emit_log("替换音频（无字幕）")
                cmd = [
                    get_ffmpeg_path(), '-hide_banner', '-loglevel', 'error',
                    '-i', video_path, '-i', audio_path,
                    '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k',
                    '-shortest', '-y', merged_path
                ]
            
            self._emit_log(f"执行ffmpeg合并...")
            self._emit_log(f"ffmpeg命令: {' '.join(cmd[:12])}...")
            log_info(f"完整命令: {' '.join(cmd)}")
            
            cwd = video_dir if subtitle_path and os.path.exists(subtitle_path) else None
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=600)
            
            if result.returncode != 0:
                error_msg = result.stderr
                self._emit_log(f"ffmpeg错误: {error_msg[:3000]}")
                log_error(f"ffmpeg失败，返回码: {result.returncode}")
                
                # 回退到纯音频合并
                self._emit_log("回退：简单替换音频")
                cmd = [
                    get_ffmpeg_path(), '-hide_banner', '-loglevel', 'error',
                    '-i', video_path, '-i', audio_path,
                    '-map', '0:v',
                    '-map', '1:a',
                    '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k',
                    '-shortest', '-y', merged_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                if result.returncode != 0:
                    self._emit_log(f"回退也失败: {result.stderr[:500]}")
                    return None
            
            self._emit_log(f"视频已生成: {merged_path}")
            return merged_path
        except FileNotFoundError:
            self._emit_log("错误: 找不到ffmpeg.exe")
            return None
        except subprocess.TimeoutExpired:
            self._emit_log("错误: ffmpeg处理超时")
            return None
        except Exception as e:
            self._emit_log(f"合并错误: {e}")
            import traceback
            traceback.print_exc()
            log_error(f"合并异常: {e}")
            return None

    def _download_video(self, url):
        try:
            import yt_dlp
            import re
            
            # 清理非法文件名字符
            def clean_filename(name):
                return re.sub(r'[\\/:*?"<>|]', '', name)
            
            # 先获取视频信息
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                video_id = info.get('id', 'unknown')
                video_title = info.get('title', video_id)
            
            # 创建以视频ID命名的文件夹（标准化路径分隔符）
            video_dir = os.path.normpath(os.path.join(self.output_dir, video_id))
            os.makedirs(video_dir, exist_ok=True)
            self.log_message.emit(f"工作目录: {video_dir}")
            
            # 下载视频到该文件夹
            video_output = os.path.join(video_dir, f'{video_id}.%(ext)s')
            ffmpeg_path = get_ffmpeg_path()
            
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': video_output,
                'quiet': True,
                'no_warnings': True,
                'ffmpeg_location': ffmpeg_path,
                'prefer_free_formats': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                
                if not os.path.exists(video_path):
                    for ext in ['mp4', 'mkv', 'webm']:
                        alt = video_path.rsplit('.', 1)[0] + '.' + ext
                        if os.path.exists(alt):
                            video_path = alt
                            break
            
            return video_path, video_dir, video_id, None
        except Exception as e:
            self.log_message.emit(f"下载错误: {e}")
            import traceback
            traceback.print_exc()
            return None, None, None, None

    def _transcribe_audio(self, audio_path):
        try:
            try:
                import whisperx
                self.log_message.emit("加载WhisperX模型...")
                model = whisperx.load_model("base", "cpu")
                
                self.log_message.emit("开始识别...")
                audio = whisperx.load_audio(audio_path)
                result = model.transcribe(audio, batch_size=16)
                
                segments = []
                for seg in result.get('segments', []):
                    text = seg.get('text', '').strip()
                    if text:
                        segments.append({
                            'start': seg.get('start', 0),
                            'end': seg.get('end', 0),
                            'text': text
                        })
                
                return segments
            except ImportError:
                self.log_message.emit("WhisperX未安装，尝试使用faster-whisper...")
                return self._transcribe_faster_whisper(audio_path)
        except Exception as e:
            self.log_message.emit(f"识别错误: {e}")
            return []

    def _transcribe_faster_whisper(self, audio_path):
        try:
            from faster_whisper import WhisperModel
            
            self.log_message.emit("加载faster-whisper small模型...")
            model = WhisperModel("small", device="cpu", compute_type="float32")
            
            self.log_message.emit("开始识别（自动检测语言）...")
            segments, info = model.transcribe(
                audio_path,
                vad_filter=False
            )
            
            if info.language:
                self.log_message.emit(f"检测到语言: {info.language}")
            
            result = []
            for seg in segments:
                text = seg.text.strip()
                if text:
                    result.append({
                        'start': seg.start,
                        'end': seg.end,
                        'text': text
                    })
            
            return result
        except ImportError:
            self.log_message.emit("警告: faster-whisper也未安装，跳过语音识别")
            return []
        except Exception as e:
            self.log_message.emit(f"faster-whisper识别错误: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _rewrite_with_llm(self, subtitles):
        """使用LLM改写字幕"""
        try:
            client = get_llm_client(self.config_manager)
            if not client:
                self.log_message.emit("未配置API Key，跳过AI改写")
                return subtitles
            
            provider = self.config_manager.get('llm_provider', 'deepseek')
            model = self.config_manager.get('llm_model', 'deepseek-chat') if provider == 'deepseek' else 'gpt-3.5-turbo'
            
            self.log_message.emit(f"使用{provider}进行AI改写...")
            
            original_text = '\n'.join([f"{i+1}. {s['text']}" for i, s in enumerate(subtitles)])
            
            prompt = f"""你是一个专业的短视频解说文案专家。请将以下英文视频字幕改写成吸引人的中文短视频解说风格。

要求：
1. 每句5-15字，简洁有力
2. 口语化、接地气、有感染力
3. 可以添加感叹词、语气词增强情感（哇、哎呀、太牛了等）
4. 保持原意，提取精华信息
5. 适当夸张、戏剧化表达
6. 不要编号，直接输出改写后的内容
7. 如果原内容是英文，改写成中文

原文字幕：
{original_text}

直接输出改写后的中文内容（每句一行）："""

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个专业的短视频解说文案专家，擅长将内容改写成吸引人的短视频风格。输出要简洁有力、口语化、有感染力。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.9
            )
            
            rewritten = response.choices[0].message.content
            lines = [line.strip() for line in rewritten.split('\n') if line.strip()]
            
            # 如果返回数量少于原字幕，补充缺失部分
            result = []
            for i, line in enumerate(lines):
                if i < len(subtitles):
                    result.append({
                        'start': subtitles[i]['start'],
                        'end': subtitles[i]['end'],
                        'text': line
                    })
            
            self.log_message.emit(f"AI改写完成: {len(result)} 条")
            return result
            
        except Exception as e:
            self.log_message.emit(f"AI改写失败: {e}")
            return subtitles