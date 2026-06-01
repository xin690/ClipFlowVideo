#!/usr/bin/env python3
"""ClipFlow 测试脚本 - 验证所有核心功能"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("[测试1] 检查模块导入...")
    try:
        from src.ui.widgets import LogWidget, ProgressWidget, VideoInfoWidget, StatusBarWidget
        print("  [OK] widgets 模块导入成功")
    except Exception as e:
        print(f"  [FAIL] widgets 模块导入失败: {e}")
        return False
    
    try:
        from src.core.config import ConfigManager
        print("  [OK] config 模块导入成功")
    except Exception as e:
        print(f"  [FAIL] config 模块导入成功: {e}")
        return False
    
    return True


def test_config_manager():
    """测试配置管理器"""
    print("\n[测试2] 检查配置管理器...")
    try:
        from src.core.config import ConfigManager
        config = ConfigManager()
        
        # 测试默认配置
        output_dir = config.get('output_dir')
        print(f"  [OK] 输出目录: {output_dir}")
        
        llm_provider = config.get('llm_provider')
        print(f"  [OK] LLM提供商: {llm_provider}")
        
        tts_voice = config.get('tts_voice')
        print(f"  [OK] TTS音色: {tts_voice}")
        
        return True
    except Exception as e:
        print(f"  [FAIL] 配置管理器测试失败: {e}")
        return False


def test_ffmpeg_path():
    """测试ffmpeg路径检测"""
    print("\n[测试3] 检查ffmpeg路径检测...")
    try:
        from src.ui.main_window import get_ffmpeg_path, check_ffmpeg
        
        ffmpeg_path = get_ffmpeg_path()
        print(f"  ffmpeg路径: {ffmpeg_path}")
        
        # 检查文件是否存在
        if os.path.exists(ffmpeg_path):
            print(f"  [OK] ffmpeg文件存在")
        else:
            print(f"  [WARN] ffmpeg文件不存在，将使用系统PATH")
        
        # 检查ffmpeg是否可用
        ffmpeg_available = check_ffmpeg()
        if ffmpeg_available:
            print(f"  [OK] ffmpeg可用")
        else:
            print(f"  [WARN] ffmpeg不可用")
        
        return True
    except Exception as e:
        print(f"  [FAIL] ffmpeg检测失败: {e}")
        return False


def test_widgets():
    """测试UI组件"""
    print("\n[测试4] 检查UI组件...")
    try:
        from src.ui.widgets import LogWidget, ProgressWidget, VideoInfoWidget, StatusBarWidget
        
        # 创建实例测试
        widget = VideoInfoWidget()
        widget.set_video_info("测试视频", "10:30", "500MB")
        print("  [OK] VideoInfoWidget 创建成功")
        
        progress = ProgressWidget()
        progress.set_progress(50, "测试中...")
        print("  [OK] ProgressWidget 创建成功")
        
        status = StatusBarWidget()
        status.set_status("就绪", "green")
        print("  [OK] StatusBarWidget 创建成功")
        
        log = LogWidget()
        log.append_log("测试日志")
        print("  [OK] LogWidget 创建成功")
        
        return True
    except Exception as e:
        print(f"  [FAIL] UI组件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_settings_dialog():
    """测试设置对话框"""
    print("\n[测试5] 检查设置对话框...")
    try:
        from src.ui.settings_dialog import SettingsDialog
        from src.core.config import ConfigManager
        
        config = ConfigManager()
        dialog = SettingsDialog(config)
        print("  [OK] SettingsDialog 创建成功")
        
        return True
    except Exception as e:
        print(f"  [FAIL] SettingsDialog测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_window():
    """测试主窗口"""
    print("\n[测试6] 检查主窗口...")
    try:
        from src.ui.main_window import WorkerThread, get_ffmpeg_path, check_ffmpeg
        
        print("  [OK] WorkerThread 类存在")
        print(f"  [OK] ffmpeg路径: {get_ffmpeg_path()}")
        print(f"  [OK] ffmpeg可用: {check_ffmpeg()}")
        
        return True
    except Exception as e:
        print(f"  [FAIL] 主窗口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies():
    """测试外部依赖"""
    print("\n[测试7] 检查外部依赖...")
    
    deps = [
        ('yt_dlp', 'yt-dlp'),
        ('edge_tts', 'edge-tts'),
        ('openai', 'openai'),
        ('pysrt', 'pysrt'),
        ('whisperx', 'whisperx'),
        ('torch', 'torch'),
    ]
    
    all_ok = True
    for module_name, package_name in deps:
        try:
            __import__(module_name)
            print(f"  [OK] {package_name}")
        except ImportError:
            print(f"  [WARN] {package_name} 未安装")
            all_ok = False
    
    return all_ok


def main():
    print("=" * 60)
    print("ClipFlow 测试脚本")
    print("=" * 60)
    
    results = []
    
    results.append(("模块导入", test_imports()))
    results.append(("配置管理器", test_config_manager()))
    results.append(("ffmpeg检测", test_ffmpeg_path()))
    results.append(("UI组件", test_widgets()))
    results.append(("设置对话框", test_settings_dialog()))
    results.append(("主窗口", test_main_window()))
    results.append(("外部依赖", test_dependencies()))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "通过" if result else "失败"
        symbol = "[OK]" if result else "[FAIL]"
        print(f"  {symbol} {name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n所有测试通过! 可以进行打包。")
        return 0
    else:
        print(f"\n{total - passed} 项测试失败，请修复后再打包。")
        return 1


if __name__ == '__main__':
    sys.exit(main())