"""
hget-audio API 接口模块
提供编程式访问音频下载功能的接口
"""

import os
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from .spiders.audio_spider import AudioSpider

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('hget-audio-api')

def download_audio(
    url,
    output_dir="hget.output",
    depth=2,
    concurrency=16,
    formats="mp3,wav,ogg,m4a,flac,aac",
    ignore_robots=False,
    user_agent=None,
    delay=0.5,
    max_size=100,
    min_size=1,
    include_patterns="",
    exclude_patterns="logout,admin,login",
    dry_run=False,
    verbose=False
):
    """
    下载网站上的所有音频文件
    
    参数:
    url (str): 要爬取的网站URL
    output_dir (str): 音频文件输出目录 (默认: "hget.output")
    depth (int): 爬取深度 (默认: 2)
    concurrency (int): 并发请求数 (默认: 16)
    formats (str): 要下载的音频格式 (逗号分隔) (默认: "mp3,wav,ogg,m4a,flac,aac")
    ignore_robots (bool): 是否忽略robots.txt规则 (默认: False)
    user_agent (str): 自定义User-Agent字符串
    delay (float): 请求之间的延迟(秒) (默认: 0.5)
    max_size (int): 最大音频文件大小(MB) (默认: 100)
    min_size (int): 最小音频文件大小(KB) (默认: 1)
    include_patterns (str): 包含的URL模式 (逗号分隔的正则表达式)
    exclude_patterns (str): 排除的URL模式 (逗号分隔的正则表达式) (默认: "logout,admin,login")
    dry_run (bool): 模拟运行(不实际下载文件) (默认: False)
    verbose (bool): 启用详细日志输出 (默认: False)
    
    返回:
    dict: 包含下载统计信息的字典
    """
    # 创建输出目录
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"输出目录: {output_dir}")
    
    # 配置Scrapy设置
    settings = get_project_settings()
    
    # 应用参数设置
    settings.set("AUDIO_OUTPUT_DIR", output_dir)
    settings.set("DEPTH_LIMIT", depth)
    settings.set("CONCURRENT_REQUESTS", concurrency)
    settings.set("DOWNLOAD_TIMEOUT", 30)
    settings.set("RETRY_TIMES", 3)
    settings.set("AUDIO_FORMATS", [f.strip() for f in formats.split(",")])
    settings.set("ROBOTSTXT_OBEY", not ignore_robots)
    
    if user_agent:
        settings.set("USER_AGENT", user_agent)
    
    settings.set("DOWNLOAD_DELAY", delay)
    settings.set("AUDIO_MAX_SIZE", max_size * 1024 * 1024)  # MB to bytes
    settings.set("AUDIO_MIN_SIZE", min_size * 1024)  # KB to bytes
    
    if include_patterns:
        settings.set("INCLUDE_PATTERNS", [p.strip() for p in include_patterns.split(",")])
    
    if exclude_patterns:
        settings.set("EXCLUDE_PATTERNS", [p.strip() for p in exclude_patterns.split(",")])
    
    settings.set("DRY_RUN", dry_run)
    
    # 配置日志级别
    if verbose:
        settings.set("LOG_LEVEL", "DEBUG")
    else:
        settings.set("LOG_LEVEL", "INFO")
        settings.set("LOG_ENABLED", True)
    
    # 配置管道
    if not dry_run:
        settings.set("ITEM_PIPELINES", {
            'hget_audio.pipelines.AudioDownloadPipeline': 300,
            'hget_audio.pipelines.AudioProcessingPipeline': 400,
            'hget_audio.pipelines.AudioStatsPipeline': 500,
        })
    
    # 创建并运行爬虫
    process = CrawlerProcess(settings)
    process.crawl(AudioSpider, start_urls=[url])
    process.start()
    
    # 收集统计信息
    stats = process.stats.get_stats()
    result = {
        'website': url,
        'output_dir': output_dir,
        'pages_crawled': stats.get('response_received_count', 0),
        'audio_found': stats.get('audio/found_count', 0),
        'audio_downloaded': stats.get('audio/downloaded_count', 0),
        'audio_skipped': stats.get('audio/skipped_count', 0),
        'errors': stats.get('log_count/ERROR', 0),
        'total_size': stats.get('audio/total_size', 0),
        'formats': stats.get('audio/count_by_format', {}),
    }
    
    # 添加跳过的文件信息
    skipped_files = stats.get('audio/skipped_files', {})
    if skipped_files:
        result['skipped_files'] = {}
        for reason, files in skipped_files.items():
            result['skipped_files'][reason] = files[:5]  # 只显示前5个
    
    logger.info("=" * 50)
    logger.info("音频下载完成!")
    logger.info(f"网站: {url}")
    logger.info(f"爬取页面: {result['pages_crawled']}")
    logger.info(f"发现音频: {result['audio_found']}")
    logger.info(f"下载音频: {result['audio_downloaded']}")
    logger.info(f"跳过音频: {result['audio_skipped']}")
    
    if dry_run:
        logger.info("模拟运行模式 - 未实际下载文件")
    
    return result

if __name__ == "__main__":
    # 示例用法
    result = download_audio(
        url="https://example.com/audio-page",
        output_dir="my_audios",
        depth=1,
        formats="mp3,wav",
        verbose=True
    )
    print("\n下载结果:")
    for key, value in result.items():
        print(f"{key}: {value}")