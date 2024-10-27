# securipaperbot/cli.py

import argparse
import asyncio
from typing import Dict, Any
import sys
from pathlib import Path
import json
from datetime import datetime

from .core.workflow import WorkflowCoordinator
from .config.settings import settings
from .utils.logger import setup_logger


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="SecuriPaperBot - Security Conference Paper Analysis Tool"
    )

    # 主要命令
    parser.add_argument(
        '--conference',
        type=str,
        choices=['ccs', 'sp', 'ndss', 'usenix'],
        help='Conference name'
    )

    parser.add_argument(
        '--year',
        type=str,
        help='Conference year (e.g., "23" for 2023)'
    )

    # 配置选项
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom config file'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for analysis results'
    )

    # 分析选项
    parser.add_argument(
        '--depth',
        choices=['basic', 'detailed', 'comprehensive'],
        default='detailed',
        help='Analysis depth'
    )

    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Enable parallel processing'
    )

    # 输出选项
    parser.add_argument(
        '--format',
        choices=['markdown', 'html', 'pdf'],
        default='markdown',
        help='Output format'
    )

    # 调试选项
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )

    parser.add_argument(
        '--clean-cache',
        action='store_true',
        help='Clean cache before running'
    )

    return parser.parse_args()


async def main_async(args: argparse.Namespace) -> int:
    """异步主函数"""
    try:
        # 设置日志
        logger = setup_logger(
            __name__,
            level="DEBUG" if args.debug else "INFO"
        )

        # 加载配置
        if args.config:
            config_path = Path(args.config)
            if not config_path.exists():
                logger.error(f"Config file not found: {args.config}")
                return 1

        # 更新配置
        config = {
            'analysis': {
                'depth': args.depth,
                'parallel_processing': args.parallel
            },
            'output': {
                'format': args.format
            }
        }

        if args.output_dir:
            config['output']['path'] = args.output_dir

        # 创建工作流协调器
        coordinator = WorkflowCoordinator(config)

        # 清理缓存
        if args.clean_cache:
            logger.info("Cleaning cache...")
            # 实现缓存清理逻辑

        # 执行分析
        logger.info(f"Starting analysis for {args.conference} {args.year}")
        results = await coordinator.process_papers(
            args.conference,
            args.year
        )

        # 保存结果
        output_path = Path(config['output'].get('path', './output'))
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = output_path / f"analysis_{timestamp}.{args.format}"

        with open(result_file, 'w', encoding='utf-8') as f:
            if args.format == 'markdown':
                f.write(results['documentation']['content'])
            else:
                json.dump(results, f, indent=2)

        logger.info(f"Analysis completed. Results saved to {result_file}")
        return 0

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        return 1


def main():
    """命令行入口点"""
    args = parse_args()

    if not args.conference or not args.year:
        print("Error: Both --conference and --year are required")
        sys.exit(1)

    if sys.platform == 'win32':
        # Windows特定的异步事件循环策略
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    exit_code = asyncio.run(main_async(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()