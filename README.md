# ClipFlow - AI视频二创工具

基于 AI 的本地视频二次创作自动化工具，支持视频下载、语音识别、AI改写、自动配音和视频导出。

## 功能特性

| 功能 | 状态 | 说明 |
|------|------|------|
| 多平台视频下载 | ✅ | YouTube, TikTok, Bilibili 等 |
| 语音识别 | ✅ | faster-whisper (支持中英文) |
| AI智能改写 | ✅ | DeepSeek / OpenAI / OpenRouter |
| 自动中文配音 | ✅ | Edge-TTS (晓晓女声) |
| 音频替换 | ✅ | 移除原音，替换为AI配音 |
| 字幕生成 | ✅ | SRT/ASS/TXT 格式 |
| 字幕烧录 | ✅ | 中英双字幕 ASS 烧录 |
| 日志系统 | ✅ | 文件+控制台双输出 |

## 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10/11 x64 |
| 内存 | 8GB+ 推荐 |
| 磁盘 | 至少 2GB 可用空间 |

## 快速开始

### 下载发布版

1. 下载 `dist/ClipFlow.exe`
2. 下载 `dist/ffmpeg/` 文件夹
3. 将 ffmpeg 文件夹放在 ClipFlow.exe 同目录下
4. 双击运行 ClipFlow.exe

### 使用流程

1. 在输入框粘贴视频链接
2. 设置输出目录（可选）
3. 配置 API Key（可选，用于 AI 改写）
4. 点击"开始处理"
5. 等待处理完成
6. 查看输出目录获取结果

## 处理流程

```
视频下载 → 音频提取 → 语音识别 → AI改写 → AI配音 → 音频替换 → 输出视频
```

## 输出文件

处理完成后，输出目录包含：

```
<视频ID>/
├── *_merged.mp4         # 最终视频（中英双字幕+AI配音）
├── *.webm              # 原始视频
├── *.wav               # 提取的音频
├── tts_output.mp3      # AI 配音文件
├── bilingual.ass       # 中英双字幕ASS（烧录用）
├── rewritten_zh.srt    # 改写后中文SRT
├── rewritten_zh.txt    # 改写后中文纯文本
├── subtitles.srt       # 原始识别SRT
├── subtitles.ass       # 原始识别ASS
└── subtitles.txt       # 原始识别纯文本
```

## 配置说明

### API Key 配置

程序支持多种 AI 服务，按需配置：

| 服务 | 说明 | 获取地址 |
|------|------|----------|
| DeepSeek | 推荐，便宜快速 | https://platform.deepseek.com |
| OpenAI | GPT 系列模型 | https://platform.openai.com |
| OpenRouter | 聚合多个模型 | https://openrouter.ai |

### 配音音色

Edge-TTS 提供多种中文音色：
- 晓晓（女声）- zh-CN-XiaoxiaoNeural
- 云希（男声）- zh-CN-YunxiNeural
- 云扬（男声）- zh-CN-YunyangNeural

## 技术架构

| 模块 | 技术方案 |
|------|---------|
| GUI | PyQt6 |
| 视频下载 | yt-dlp |
| 视频处理 | FFmpeg |
| 语音识别 | faster-whisper |
| AI改写 | DeepSeek / OpenAI / OpenRouter |
| 配音 | Edge-TTS |
| 打包 | PyInstaller |

## 开发

### 环境要求

- Python 3.10+
- Windows 10/11

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行开发版

```bash
python run.py
```

### 打包

```bash
build\build.bat
```

## 项目结构

```
ClipFlow/
├── src/                  # 源代码
│   ├── core/            # 核心模块
│   ├── downloader/      # 视频下载
│   ├── audio/           # 音频处理
│   ├── asr/             # 语音识别
│   ├── llm/             # AI改写
│   ├── tts/             # 配音生成
│   ├── subtitle/        # 字幕处理
│   ├── editor/          # 视频剪辑
│   ├── exporter/       # 视频导出
│   ├── utils/           # 工具模块
│   └── ui/              # 界面
├── build/               # 构建脚本
├── dist/                # 发布文件
├── installer/           # 安装包配置
├── tests/               # 测试代码
└── docs/                # 文档
```

## 文档

| 文档 | 说明 |
|------|------|
| [USER_GUIDE.md](docs/USER_GUIDE.md) | 用户使用指南 |
| [WINDOWS_BUILD_GUIDE.md](docs/WINDOWS_BUILD_GUIDE.md) | Windows 打包指南 |
| [DEVELOPMENT_PROGRESS.md](docs/DEVELOPMENT_PROGRESS.md) | 开发进度记录 |

## 常见问题

### Q: 程序无法启动？

确保 ffmpeg 文件夹与 ClipFlow.exe 在同一目录。

### Q: 视频下载失败？

- 检查网络连接
- 确认视频链接有效
- 部分平台可能需要 Cookie 认证

### Q: API 调用失败？

- 检查 API Key 是否正确
- 确认 API 余额充足
- 检查网络代理设置

### Q: 如何查看日志？

日志文件位于：
```
C:\Users\<用户名>\AppData\Local\Temp\ClipFlow\logs\
```

## 更新日志

### v1.0.2 (2026-06-01)
- 中英双字幕烧录（ASS双Style + 相对路径修复ffmpeg冒号解析）
- 新增 save_bilingual_ass 方法生成双字幕ASS
- 新增 rewritten_zh.srt/txt 单独保存
- 修复 ffprobe 分辨率检测 PATH 回退
- 重新打包 ~1.13GB

### v1.0.1 (2026-05-20)
- 添加日志系统（文件+控制台双输出）
- 修复 ffmpeg 路径查找问题
- 修复设置保存功能
- 优化 AI 改写提示词
- 添加音频替换功能（-map 命令）
- 更新打包脚本和文档

### v1.0.0 (2026-05-20)
- 初始版本发布
- 支持多平台视频下载
- 支持语音识别和字幕生成
- 支持 AI 改写和配音
- PyQt6 图形界面

## 许可证

MIT License - 详见 LICENSE 文件