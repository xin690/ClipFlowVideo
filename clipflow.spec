# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

project_root = os.path.dirname(os.path.abspath(SPEC)) if hasattr(sys, 'frozen') else os.getcwd()
build_dir = os.path.join(project_root, 'build')
ffmpeg_dir = os.path.join(build_dir, 'ffmpeg')
src_dir = os.path.join(project_root, 'src')
resources_dir = os.path.join(project_root, 'resources')
run_py = os.path.join(project_root, 'run.py')

a = Analysis(
    [run_py],
    pathex=[project_root],
    binaries=[
        (ffmpeg_dir, 'ffmpeg'),
    ],
    datas=[
        (src_dir, 'src'),
        (resources_dir, 'resources'),
    ],
    hiddenimports=[
        # 核心依赖
        'yt_dlp',
        'yt_dlp.compat',
        'yt_dlp.utils',
        'edge_tts',
        'openai',
        'openai._base_client',
        'torch',
        'torch.cuda',
        'torch.nn',
        'numpy',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtNetwork',
        'pysrt',
        # 异步相关
        'asyncio',
        'asyncio.runners',
        # 语音识别
        'faster_whisper',
        'faster_whisper.utils',
        'whisperx',
        'whisperx.align',
        'ctranslate2',
        'ctranslate2.spec',
        # 数据处理
        'pandas',
        'scipy',
        'librosa',
        # 音视频处理
        'cv2',
        'moviepy',
        'PIL',
        'PIL.Image',
        # 网络请求
        'requests',
        'urllib3',
        'certifi',
        # 加密与安全
        'cryptography',
        'cryptography.x509',
        # 日志与配置
        'logging',
        'json',
        'yaml',
        # Windows相关
        'win32api',
        'win32con',
        'win32gui',
        'win32com',
        # 其他必要依赖
        'queue',
        'threading',
        'subprocess',
        'shutil',
        'tempfile',
        're',
        'datetime',
        'pathlib',
        # 补充模块
        'mutagen',
        'brotli',
        'ctypes',
        'struct',
        'pickle',
        'zipfile',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch.utils.tensorboard',
        'torch.utils.checkpoint',
        'torch.utils.mobile_optimizer',
        'torch.distributed',
        'torch.profiler',
        'torch.cuda.amp',
        'matplotlib',
        'ipython',
        'notebook',
        'jupyter',
        'sphinx',
        'test',
        'unittest',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ClipFlow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)