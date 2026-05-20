# ClipFlow Windows 打包指南

## 目录

- [环境要求](#环境要求)
- [快速打包](#快速打包)
- [手动打包](#手动打包)
- [制作安装包](#制作安装包)
- [常见问题](#常见问题)

---

## 环境要求

- Windows 10/11 x64
- Python 3.10+ (本项目使用 Python 3.14)
- 至少 15GB 可用磁盘空间
- 网络连接（用于下载 ffmpeg 和安装依赖）

---

## 快速打包

### 方式一：使用打包脚本（推荐）

1. **安装依赖**
   ```
   双击运行 build\install_deps.bat
   ```

2. **下载 ffmpeg**
   ```
   双击运行 build\download_ffmpeg.bat
   ```

3. **执行打包**
   ```
   双击运行 build\build.bat
   ```

4. **输出文件**
   - `dist\ClipFlow.exe` - 主程序
   - `dist\ffmpeg\` - ffmpeg 依赖

### 方式二：执行完整打包（一步到位）

```powershell
# 在项目根目录执行
build\build.bat
```

---

## 手动打包

### 1. 安装 Python 依赖

```powershell
# 安装核心依赖
pip install PyQt6>=6.0.0

# 安装音视频处理依赖
pip install yt-dlp>=2024.0.0 ffmpeg-python>=0.2.0

# 安装 AI 相关依赖
pip install openai>=1.0.0 edge-tts>=6.0.0 pysrt>=1.1.2

# 安装语音识别依赖
pip install faster-whisper>=0.9.0

# 安装打包工具
pip install pyinstaller
```

### 2. 下载 ffmpeg

从以下地址下载：
```
https://github.com/BtbN/FFmpeg-Builds/releases
```

下载 `ffmpeg-master-latest-win64-gpl.zip`，解压后将 `bin` 目录下的文件复制到 `build/ffmpeg/` 目录。

需要的文件：
- ffmpeg.exe
- ffplay.exe
- ffprobe.exe

### 3. 确认 clipflow.spec 配置

编辑项目根目录的 `clipflow.spec`：

```python
# 入口文件
run_py = os.path.join(project_root, 'run.py')

# ffmpeg 路径
ffmpeg_dir = os.path.join(project_root, 'build', 'ffmpeg')

# 源码路径
src_dir = os.path.join(project_root, 'src')

# 资源路径
resources_dir = os.path.join(project_root, 'resources')

# 二进制文件（包含 ffmpeg）
binaries=[
    (ffmpeg_dir, 'ffmpeg'),
]

# 数据文件（包含源码和资源）
datas=[
    (src_dir, 'src'),
    (resources_dir, 'resources'),
]
```

### 4. 执行打包

```powershell
cd ClipFlow
python -m PyInstaller clipflow.spec --clean --noconfirm
```

### 5. 复制 ffmpeg 到 dist

```powershell
xcopy /e /y "build\ffmpeg" "dist\ffmpeg"
```

---

## 打包脚本说明

### build\install_deps.bat

安装所有 Python 依赖：
- PyQt6 - GUI 界面
- yt-dlp - 视频下载
- ffmpeg-python - ffmpeg 接口
- openai - AI 接口
- edge-tts - 语音合成
- pysrt - 字幕处理
- faster-whisper - 语音识别

### build\download_ffmpeg.bat

自动下载并配置 ffmpeg：
- 从 GitHub 下载最新 ffmpeg
- 解压到 `build/ffmpeg/` 目录
- 验证文件完整性

### build\build.bat

完整打包流程：
- 验证环境（Python、ffmpeg）
- 安装 PyInstaller（如需要）
- 执行 PyInstaller 打包
- 复制 ffmpeg 到 dist 目录

可选参数：
- `build\build.bat clean` - 清理旧构建后重新打包

---

## 打包配置说明

### clipflow.spec 关键配置

```python
# ========================================
# 入口文件
# ========================================
a = Analysis(
    ['run.py'],  # 使用 run.py 作为入口
    ...
)

# ========================================
# 包含 ffmpeg 二进制
# ========================================
binaries=[
    ('build/ffmpeg', 'ffmpeg'),  # 二进制文件
]

# ========================================
# 包含源代码和资源
# ========================================
datas=[
    ('src', 'src'),  # 源代码目录
    ('resources', 'resources'),  # 资源目录
]

# ========================================
# 隐藏导入（确保 PyInstaller 能找到）
# ========================================
hiddenimports=[
    # 核心依赖
    'yt_dlp',
    'edge_tts',
    'openai',
    'torch',
    'PyQt6',
    'pysrt',
    # 语音识别
    'faster_whisper',
    'whisperx',
    'ctranslate2',
    # 数据处理
    'pandas',
    'scipy',
    # 音视频处理
    'cv2',
    'moviepy',
    'PIL',
    # ... 其他依赖
]
```

### 入口文件说明

程序使用 `run.py` 作为入口，而不是 `src/ui/app.py`，原因：

1. **相对导入问题**：PyInstaller 打包后，`src/ui/app.py` 中的 `from .main_window import ...` 等相对导入会失败
2. **运行时加载**：`run.py` 在运行时动态加载 UI 模块，避免打包问题

---

## 制作安装包

### 安装 Inno Setup

1. 下载：https://jrsoftware.org/isdl.php
2. 安装时建议选择中文语言

### 编辑安装脚本

编辑 `installer/ClipFlow.iss`：

```iss
#define MyAppVersion "1.0.0"           // 版本号
DefaultDirName={autopf}\ClipFlow       // 安装目录
OutputBaseFilename=ClipFlow_Setup_v1.0.0  // 输出文件名
```

### 编译安装包

方式一：双击 `build\make_installer.bat`

方式二：手动执行

```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\ClipFlow.iss
```

### 输出

安装包将生成在 `dist/` 目录：

- `ClipFlow_Setup_v1.0.0.exe`

---

## 打包后测试

### 测试可执行文件

```powershell
.\dist\ClipFlow.exe
```

预期结果：
1. 弹出 GUI 窗口
2. 无控制台输出（console=False）
3. ffmpeg 被正确调用

### 检查依赖

打开任务管理器，查看内存占用：
- 正常启动：约 200-400MB
- 处理视频时：可能达 1-2GB

---

## 体积优化

### 当前体积分布

| 组件 | 大小 | 说明 |
|------|------|------|
| ClipFlow.exe | ~240-260 MB | 包含 Python 运行时和大部分依赖 |
| ffmpeg | ~580 MB | 三个 exe 文件 |
| **总计** | ~820-840 MB | |

### 优化建议

1. **排除 torch**（如不需要 WhisperX）
   - 移除 `torch` 依赖
   - 体积减少约 500MB
   - ASR 功能需要运行时下载

2. **使用 UPX 压缩**
   - PyInstaller 已启用 UPX
   - 可进一步减少 10-20%

3. **分离 ffmpeg**
   - 让用户自行下载 ffmpeg
   - 减少约 580MB
   - 需要配置 PATH

4. **精简 torch**
   ```python
   excludes=[
       'torch.utils.tensorboard',
       'torch.optim',
       # ...其他不用的模块
   ]
   ```

---

## 常见问题

### Q1: PyInstaller 报错 "script not found"

检查 `run.py` 路径是否正确：

```python
run_py = os.path.join(project_root, 'run.py')
```

确保 `run.py` 存在且路径正确。

### Q2: 运行时报错 "No module named xxx"

在 `clipflow.spec` 的 `hiddenimports` 中添加缺失的模块：

```python
hiddenimports=[
    'your_module',
    ...
]
```

### Q3: ffmpeg 无法找到

确保 `ffmpeg/` 目录与 `ClipFlow.exe` 在同一目录：

```
dist/
├── ClipFlow.exe
└── ffmpeg/
    ├── ffmpeg.exe
    ├── ffplay.exe
    └── ffprobe.exe
```

### Q4: PyQt6 样式异常

确保 PyInstaller 包含 Qt 平台插件：

```python
# 通常自动处理，如有问题检查 hook
```

### Q5: 打包后无法启动（无错误提示）

1. 添加控制台查看错误：
   ```python
   console=True,  # 临时改为 True
   ```

2. 检查依赖是否完整

3. 检查 datas 路径是否正确

### Q6: 下载 ffmpeg 失败

- 检查网络连接
- 手动下载后放置到 `build/ffmpeg/` 目录
- GitHub 下载链接：https://github.com/BtbN/FFmpeg-Builds/releases

### Q7: PyInstaller 打包后缺少依赖

确保在打包前安装了所有依赖：

```powershell
pip install -r requirements.txt
```

### Q8: 字幕烧录失败

**问题**: `[Parsed_ass_0] Unable to parse "original_size" option value`

**解决方案**:
1. 确保 ASS 字幕文件包含 `PlayResX` 和 `PlayResY` 字段
2. 优先使用 SRT 格式进行烧录
3. 代码中已自动处理此问题

### Q9: 日志文件位置

日志文件保存在：
```
C:\Users\<用户名>\AppData\Local\Temp\ClipFlow\logs\
clipflow_YYYYMMDD_HHMMSS.log
```

---

## CI/CD 自动化打包

### GitHub Actions 示例

```yaml
name: Build

on:
  release:
    types: [created]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install pyinstaller PyQt6 yt-dlp edge-tts openai pysrt faster-whisper
      
      - name: Download ffmpeg
        run: |
          # 下载并解压 ffmpeg 到 build/ffmpeg/
      
      - name: Build
        run: |
          pyinstaller clipflow.spec --noconfirm
      
      - name: Copy ffmpeg
        run: |
          xcopy /e /y "build\ffmpeg" "dist\ffmpeg"
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: ClipFlow
          path: dist/
```

---

## 更新日志

### v1.0.0 (2026-05-20)
- 实现视频下载功能
- 实现语音识别功能 (faster-whisper)
- 实现 AI 改写功能 (DeepSeek/OpenAI)
- 实现 AI 配音功能 (Edge TTS)
- 实现字幕烧录功能
- 实现日志系统
- 优化 ffmpeg 路径查找逻辑

---

## 参考资料

- [PyInstaller 文档](https://pyinstaller.org/)
- [Inno Setup 文档](https://jrsoftware.org/ishelp/)
- [yt-dlp 文档](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg 文档](https://ffmpeg.org/documentation.html)
- [ffmpeg-windows 下载](https://github.com/BtbN/FFmpeg-Builds/releases)