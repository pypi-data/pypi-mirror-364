# Scrapy settings for hget_audio project
import os
import logging

BOT_NAME = 'hget_audio'

SPIDER_MODULES = ['hget_audio.spiders']
NEWSPIDER_MODULE = 'hget_audio.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 0.5

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 2

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1',
}

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
    'hget_audio.middlewares.RandomUserAgentMiddleware': 400,
    'hget_audio.middlewares.ProxyMiddleware': 410,
}

# Enable or disable extensions
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapy.extensions.logstats.LogStats': None,
    'scrapy.extensions.corestats.CoreStats': 500,
    'scrapy.extensions.throttle.AutoThrottle': 600,
}

# Configure item pipelines
ITEM_PIPELINES = {
    'hget_audio.pipelines.AudioDownloadPipeline': 300,
    'hget_audio.pipelines.AudioProcessingPipeline': 400,
    'hget_audio.pipelines.AudioStatsPipeline': 500,
}

# Enable and configure the AutoThrottle extension
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2.0
AUTOTHROTTLE_MAX_DELAY = 30.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0
AUTOTHROTTLE_DEBUG = True

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0  # Never expire
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

# Custom settings for audio scraping
AUDIO_OUTPUT_DIR = 'hget.output'
AUDIO_FORMATS = ['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac']
AUDIO_MAX_SIZE = 100 * 1024 * 1024  # 100 MB
AUDIO_MIN_SIZE = 1 * 1024  # 1 KB
DEPTH_LIMIT = 2
INCLUDE_PATTERNS = []
EXCLUDE_PATTERNS = ['logout', 'admin', 'login']
DRY_RUN = False

# Logging configuration
LOG_ENABLED = True
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FILE = None  # 'hget_audio.log' to log to file

# Proxy settings (optional)
ROTATING_PROXY_LIST = [
    # 'ip:port', 
    # 'username:password@ip:port'
]

# User agent rotation
USER_AGENT = 'Mozilla/5.0 (compatible; hget-audio/1.0; +https://github.com/hget-audio)'
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
]

# Retry settings
RETRY_TIMES = 2
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408]

# Timeout settings
DOWNLOAD_TIMEOUT = 30
DNS_TIMEOUT = 10

# Advanced settings
AJAX_CRAWL_ENABLED = True
DEPTH_STATS_VERBOSE = True
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 512
REACTOR_THREADPOOL_MAXSIZE = 20

# Security settings
DOWNLOAD_MAXSIZE = 1024 * 1024 * 100  # 100 MB
DOWNLOAD_WARNSIZE = 1024 * 1024 * 50   # 50 MB
DNSCACHE_ENABLED = True
DNS_RESOLVER = 'scrapy.resolver.CachingThreadedResolver'

# Telnet settings (if enabled)
TELNETCONSOLE_PORT = [6023, 6073]

# Stats collection
STATS_DUMP = True
STATS_CLASS = 'scrapy.statscollectors.MemoryStatsCollector'

# Persistent job storage
JOBDIR = 'crawls/hget_audio'

# Enable feed exports
FEED_FORMAT = 'jsonlines'
FEED_URI = 'results.jsonl'
FEED_EXPORT_ENCODING = 'utf-8'
FEED_EXPORT_FIELDS = ['url', 'filename', 'path', 'size', 'format', 'depth']

# Custom command settings
COMMANDS_MODULE = 'hget_audio.commands'

# Performance optimization
CONCURRENT_ITEMS = 100
SCHEDULER_PRIORITY_QUEUE = 'scrapy.pqueues.DownloaderAwarePriorityQueue'
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'