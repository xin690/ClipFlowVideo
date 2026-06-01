# ClipFlow 开发进度记录

## 项目信息
- **项目名称**: ClipFlow (AI视频二创工具)
- **开始日期**: 2026-05-20
- **当前版本**: v1.0.2
- **状态**: ✅ 功能完善中

---

## 功能完成状态

### 核心功能

| 功能 | 模块 | 状态 | 说明 |
|------|------|------|------|
| 视频下载 | yt-dlp | ✅ 完成 | 支持 YouTube/TikTok/Bilibili 等 |
| 音频提取 | ffmpeg | ✅ 完成 | 提取 wav 格式 |
| 语音识别 | faster-whisper | ✅ 完成 | small 模型 |
| AI 改写 | DeepSeek/OpenAI | ✅ 完成 | 中文解说风格 |
| AI 配音 | edge-tts | ✅ 完成 | 晓晓女声 |
| 音频替换 | ffmpeg -map | ✅ 完成 | 移除原音，替换新音 |
| 字幕生成 | SRT/ASS | ✅ 完成 | 保存到文件 |
| 字幕烧录 | ffmpeg libass | ✅ 完成 | 中英双字幕 ASS，相对路径+original_size |
| 日志系统 | logging | ✅ 完成 | 文件+控制台双输出 |

### UI 功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 视频链接输入 | ✅ 完成 | |
| 输出目录设置 | ✅ 完成 | |
| 设置保存 | ✅ 完成 | |
| 处理进度显示 | ✅ 完成 | |
| 日志显示 | ✅ 完成 | |
| API 配置 | ✅ 完成 | |

---

## 开发阶段

### 阶段1: 项目初始化 ✅
- [x] 创建项目目录结构
- [x] 初始化 Python 包结构
- [x] 配置文件设置
- [x] 依赖清单生成

### 阶段2: 核心模块开发 ✅
| 模块 | 文件 | 状态 |
|------|------|------|
| downloader | youtube_dl.py | ✅ 完成 |
| audio | extractor.py | ✅ 完成 |
| asr | whisperx.py / faster-whisper | ✅ 完成 |
| llm | base.py, openai_llm.py | ✅ 完成 |
| tts | edge_tts.py | ✅ 完成 |
| subtitle | srt_gen.py, subtitle_saver.py | ✅ 完成 |
| editor | clipper.py | ✅ 完成 |
| exporter | video_export.py | ✅ 完成 |

### 阶段3: UI 开发 ✅
| 文件 | 说明 | 状态 |
|------|------|------|
| app.py | 应用入口 | ✅ 完成 |
| main_window.py | 主窗口+工作线程 | ✅ 完成 |
| settings_dialog.py | 设置对话框 | ✅ 完成 |
| widgets.py | 自定义组件 | ✅ 完成 |
| logger.py | 日志模块 | ✅ 完成 |
| subtitle_saver.py | 字幕保存 | ✅ 完成 | 新增 save_bilingual_ass 双字幕 |

### 阶段4: 打包配置 ✅
| 文件 | 说明 | 状态 |
|------|------|------|
| clipflow.spec | PyInstaller 配置 | ✅ 完成 |
| run.py | 程序入口 | ✅ 完成 |
| build/instal_deps.bat | 依赖安装脚本 | ✅ 完成 |
| build/download_ffmpeg.bat | ffmpeg 下载脚本 | ✅ 完成 |
| build/build.bat | 打包脚本 | ✅ 完成 |
| installer/ClipFlow.iss | Inno Setup 配置 | ✅ 完成 |

---

## 文件结构

```
ClipFlow/
├── src/
│   ├── core/
│   │   ├── pipeline.py       # 主流程编排
│   │   └── config.py         # 配置管理
│   ├── downloader/
│   │   └── youtube_dl.py     # 视频下载
│   ├── audio/
│   │   └── extractor.py      # 音频提取
│   ├── asr/
│   │   └── whisperx.py       # 语音识别
│   ├── llm/
│   │   ├── base.py           # LLM接口
│   │   └── openai_llm.py     # LLM实现
│   ├── tts/
│   │   └── edge_tts.py       # 配音生成
│   ├── subtitle/
│   │   ├── srt_gen.py        # 字幕生成
│   │   └── converter.py      # 字幕转换
│   ├── editor/
│   │   └── clipper.py        # 视频剪辑
│   ├── exporter/
│   │   └── video_export.py   # 视频导出
│   ├── utils/
│   │   └── logger.py         # 日志模块
│   └── ui/
│       ├── __init__.py
│       ├── app.py             # 应用入口
│       ├── main_window.py     # 主窗口+工作线程
│       ├── settings_dialog.py # 设置对话框
│       ├── widgets.py         # 自定义组件
│       └── subtitle_saver.py  # 字幕保存
├── build/
│   ├── clipflow.spec          # PyInstaller 配置
│   ├── install_deps.bat       # 依赖安装脚本
│   ├── download_ffmpeg.bat    # ffmpeg 下载脚本
│   ├── build.bat              # 打包脚本
│   └── ffmpeg/                # ffmpeg 二进制
├── dist/
│   ├── ClipFlow.exe           # 可执行文件
│   └── ffmpeg/                # ffmpeg 目录
├── installer/
│   ├── ClipFlow.iss            # Inno Setup
│   └── make_installer.bat      # 安装包脚本
├── tests/
│   └── test_modules.py        # 单元测试
├── docs/
│   ├── DEVELOPMENT_PROGRESS.md # 本文档
│   ├── USER_GUIDE.md          # 用户指南
│   ├── WINDOWS_BUILD_GUIDE.md  # 打包指南
│   └── DEVLOPMENT_PROGRESS.md  # 开发进度
├── resources/
├── main.py                    # 命令行入口
├── run.py                    # GUI入口
├── README.md
├── LICENSE
├── requirements.txt
└── clipflow.spec
```

---

## 打包产出

| 文件 | 路径 | 大小 | 说明 |
|------|------|------|------|
| ClipFlow.exe | dist/ClipFlow.exe | ~548 MB | 主程序 |
| ffmpeg.exe | dist/ffmpeg/ | ~193 MB | 视频处理 |
| ffplay.exe | dist/ffmpeg/ | ~195 MB | 视频播放 |
| ffprobe.exe | dist/ffmpeg/ | ~193 MB | 视频分析 |
| **总计** | | **~1.13 GB** | |

---

## 已集成的依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| PyQt6 | 6.x | GUI 界面 |
| yt-dlp | 2026.x | 视频下载 |
| edge-tts | 7.x | 配音生成 |
| openai | 2.x | AI 接口 |
| torch | 2.x | AI 框架 |
| faster-whisper | 0.9.x | 语音识别 |
| pysrt | 1.x | 字幕处理 |
| ffmpeg | latest | 视频处理 |

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-05-20 | v1.0.0 | 项目初始化，核心模块开发完成 |
| 2026-05-20 | v1.0.0 | GUI 界面开发完成 |
| 2026-05-20 | v1.0.0 | 打包配置完成，首版 exe 生成 |
| 2026-05-20 | v1.0.0 | 修复导入错误，打包完成 |
| 2026-05-20 | v1.0.1 | 添加日志系统，修复 ffmpeg 路径问题 |
| 2026-05-20 | v1.0.1 | 修复设置保存功能 |
| 2026-05-20 | v1.0.1 | 优化 AI 改写提示词 |
| 2026-05-20 | v1.0.1 | 添加音频替换功能（-map 命令） |
| 2026-05-20 | v1.0.1 | 更新打包脚本和文档 |
| 2026-06-01 | v1.0.2 | 中英双字幕（ASS双Style + 相对路径修复ffmpeg冒号解析） |
| 2026-06-01 | v1.0.2 | 新增 save_bilingual_ass 方法 |
| 2026-06-01 | v1.0.2 | 新增 rewritten_zh.srt/txt 单独保存 |
| 2026-06-01 | v1.0.2 | 修复 ffprobe 分辨率检测 PATH 回退 |
| 2026-06-01 | v1.0.2 | 重新打包，exe ~548MB + ffmpeg ~581MB |

---

## 技术实现

### 音频替换命令
```bash
ffmpeg -i video.webm -i tts.mp3 \
  -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k \
  -shortest -y output.mp4
```

### 字幕烧录（中英双字幕）
```bash
# 1. 将字幕拷贝到输出目录 → 用相对路径避免冒号解析
cp bilingual.ass /output/dir/

# 2. 在输出目录执行 ffmpeg
cd /output/dir
ffmpeg -i input.mp4 -i tts.mp3 \
  -map 0:v -map 1:a \
  -vf subtitles=bilingual.ass:original_size=1920x1080 \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 192k \
  -shortest -y output.mp4
```
> 注：ffmpeg 将 Windows 路径 `C:\...` 中的冒号解析为选项分隔符，导致 original_size 解析失败。
> 解决方案：将字幕文件拷贝到输出目录，使用相对路径引用，并设置 `cwd=video_dir`。

### 日志文件位置
```
C:\Users\<用户名>\AppData\Local\Temp\ClipFlow\logs\
clipflow_YYYYMMDD_HHMMSS.log
```

---

## 待优化项

1. **体积优化** - 排除不必要的 torch 模块（当前 548MB）
2. **图标** - 添加自定义应用图标
3. **安装包** - 使用 Inno Setup 制作专业安装程序
4. **软字幕** - 添加可选的软字幕输出

---

## 已知问题

| 问题 | 状态 | 解决方案 |
|------|------|------|
| ffmpeg `C:\` 冒号解析 | ✅ 已修复 | 相对路径 + original_size + cwd |
| whisperx 未安装 | ⚠️ 运行时下载 | 使用 faster-whisper 替代 |
| 包体积较大 | ⚠️ 包含 torch | 可选优化 |

---

## 使用流程

```
1. 输入视频链接
2. 设置输出目录（可选）
3. 配置 API Key（可选，用于 AI 改写）
4. 点击开始处理
5. 等待处理完成
6. 查看输出目录获取结果
   ├── *_merged.mp4       # 最终视频（中英双字幕+AI配音）
   ├── *.wav             # 提取的音频
   ├── tts_output.mp3    # AI 配音
   ├── bilingual.ass     # 中英双字幕ASS（烧录用）
   ├── rewritten_zh.srt  # 改写后中文SRT
   ├── rewritten_zh.txt  # 改写后中文纯文本
   ├── subtitles.srt     # 原始识别SRT
   ├── subtitles.ass     # 原始识别ASS
   └── subtitles.txt     # 原始识别纯文本
```

---

### 中英双字幕 ASS 格式
```ass
[V4+ Styles]
Style: EnSub,Arial,24,&H99FFFFFF,...,Alignment=2,MarginV=95,1
Style: ZhSub,Arial,36,&H00FFFFFF,...,Alignment=2,MarginV=30,1

[Events]
Dialogue: 0,...,EnSub,,0,0,0,,English text     ← 24px 半透白, 距底95px
Dialogue: 0,...,ZhSub,,0,0,0,,中文文本           ← 36px 纯白, 距底30px
```

---

## 下一步计划

1. 添加软字幕选项
2. 测试更多视频源
3. 优化处理速度