#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.pipeline import ClipFlowPipeline, PipelineConfig, create_pipeline
from src.core.config import ConfigManager


def main():
    print("=" * 50)
    print("ClipFlow - AI视频二创工具")
    print("=" * 50)
    
    config_manager = ConfigManager()
    output_dir = config_manager.get('output_dir')
    
    api_key = config_manager.get_api_key('deepseek')
    if not api_key:
        api_key = os.getenv('DEEPSEEK_API_KEY')
    
    config = PipelineConfig(
        output_dir=output_dir,
        llm_provider='deepseek' if api_key else 'none',
        llm_api_key=api_key,
        tts_voice='zh-CN-XiaoxiaoNeural',
        asr_model='base'
    )
    
    pipeline = ClipFlowPipeline(config)
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"\n正在处理: {url}")
        result = pipeline.run(url, rewrite=True, add_subtitle=True)
        
        if result.success:
            print("\n处理完成!")
            print(f"原视频: {result.original_video}")
            print(f"最终视频: {result.final_video}")
        else:
            print(f"\n处理失败: {result.error}")
    else:
        print("\n用法: python main.py <视频URL>")
        print("\n示例:")
        print("python main.py https://youtube.com/watch?v=...")
        print("python main.py https://www.tiktok.com/...")


if __name__ == '__main__':
    main()