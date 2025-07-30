import os
import re
import argparse
import logging
from urllib.parse import urlparse
from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError
from scrapy.utils.project import get_project_settings
from ..pipelines import AudioDownloadPipeline
from ..spiders.audio_spider import AudioSpider

class Command(ScrapyCommand):
    requires_project = True
    default_settings = {'LOG_ENABLED': True}
    
    def syntax(self):
        return "[options] <url>"
    
    def short_desc(self):
        return "Download all audio files from a website"
    
    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_argument("url", nargs="?", help="URL to scrape")
        parser.add_argument("-o", "--output", metavar="DIR", default="hget.output", 
                          help="output directory (default: hget.output)")
        parser.add_argument("-d", "--depth", type=int, default=2,
                          help="max depth for crawling (default: 2)")
        parser.add_argument("-c", "--concurrency", type=int, default=16,
                          help="max concurrent requests (default: 16)")
        parser.add_argument("-t", "--timeout", type=int, default=10,
                          help="request timeout in seconds (default: 10)")
        parser.add_argument("-r", "--retries", type=int, default=2,
                          help="max retries for failed requests (default: 2)")
        parser.add_argument("-f", "--formats", default="mp3,wav,ogg,m4a,flac,aac",
                          help="audio formats to download (comma separated)")
        parser.add_argument("--ignore-robots", action="store_true",
                          help="ignore robots.txt rules")
        parser.add_argument("--user-agent", default="Mozilla/5.0 (compatible; hget-audio/1.0)",
                          help="custom user agent string")
        parser.add_argument("--delay", type=float, default=0.5,
                          help="delay between requests in seconds (default: 0.5)")
        parser.add_argument("--max-size", type=int, default=100,
                          help="max audio file size in MB (default: 100)")
        parser.add_argument("--min-size", type=int, default=1,
                          help="min audio file size in KB (default: 1)")
        parser.add_argument("--include", default="",
                          help="URL patterns to include (comma separated regex)")
        parser.add_argument("--exclude", default="logout,admin,login",
                          help="URL patterns to exclude (comma separated regex)")
        parser.add_argument("--verbose", action="store_true",
                          help="enable verbose logging")
        parser.add_argument("--dry-run", action="store_true",
                          help="simulate without downloading files")
    
    def run(self, args, opts):
        if not opts.url:
            raise UsageError("Please provide a URL to scrape")
        
        # Validate and normalize URL
        parsed_url = urlparse(opts.url)
        if not parsed_url.scheme:
            opts.url = "http://" + opts.url
            parsed_url = urlparse(opts.url)
        
        if not parsed_url.netloc:
            raise UsageError("Invalid URL format")
        
        # Create output directory
        output_dir = os.path.abspath(opts.output)
        os.makedirs(output_dir, exist_ok=True)
        
        # Configure project settings
        settings = get_project_settings()
        
        # Apply command-line options to settings
        settings.set("AUDIO_OUTPUT_DIR", output_dir)
        settings.set("DEPTH_LIMIT", opts.depth)
        settings.set("CONCURRENT_REQUESTS", opts.concurrency)
        settings.set("DOWNLOAD_TIMEOUT", opts.timeout)
        settings.set("RETRY_TIMES", opts.retries)
        settings.set("AUDIO_FORMATS", [f.strip() for f in opts.formats.split(",")])
        settings.set("ROBOTSTXT_OBEY", not opts.ignore_robots)
        settings.set("USER_AGENT", opts.user_agent)
        settings.set("DOWNLOAD_DELAY", opts.delay)
        settings.set("AUDIO_MAX_SIZE", opts.max_size * 1024 * 1024)  # MB to bytes
        settings.set("AUDIO_MIN_SIZE", opts.min_size * 1024)  # KB to bytes
        settings.set("INCLUDE_PATTERNS", [p.strip() for p in opts.include.split(",")] if opts.include else [])
        settings.set("EXCLUDE_PATTERNS", [p.strip() for p in opts.exclude.split(",")] if opts.exclude else [])
        settings.set("DRY_RUN", opts.dry_run)
        
        # Configure logging
        log_level = logging.DEBUG if opts.verbose else logging.INFO
        settings.set("LOG_LEVEL", log_level)
        
        # Configure pipelines
        if not opts.dry_run:
            settings.set("ITEM_PIPELINES", {
                'hget_audio.pipelines.AudioDownloadPipeline': 300,
            })
        
        # Create and configure spider
        spider = AudioSpider(
            start_urls=[opts.url],
            settings=settings
        )
        
        # Configure crawler
        crawler = self.crawler_process.create_crawler(
            spidercls=AudioSpider, 
            settings=settings
        )
        
        # Add the spider to the crawler
        crawler.crawl(spider)
        
        # Start the crawling process
        self.crawler_process.start()
        
        # Print summary
        stats = crawler.stats.get_stats()
        print("\n" + "="*50)
        print("Scraping Summary")
        print("="*50)
        print(f"Website: {opts.url}")
        print(f"Output Directory: {output_dir}")
        print(f"Total Pages Crawled: {stats.get('response_received_count', 0)}")
        print(f"Audio Files Found: {stats.get('audio/found_count', 0)}")
        print(f"Audio Files Downloaded: {stats.get('audio/downloaded_count', 0)}")
        print(f"Audio Files Skipped: {stats.get('audio/skipped_count', 0)}")
        print(f"Errors Encountered: {stats.get('log_count/ERROR', 0)}")
        
        # Print skipped files if any
        skipped_files = stats.get('audio/skipped_files', [])
        if skipped_files:
            print("\nSkipped Files:")
            for reason, files in skipped_files.items():
                print(f"  {reason}:")
                for file in files[:5]:
                    print(f"    - {file}")
                if len(files) > 5:
                    print(f"    ... and {len(files)-5} more")
        
        # Print success message
        if stats.get('audio/downloaded_count', 0) > 0:
            print("\nSuccess: Audio files downloaded to output directory.")
        elif stats.get('audio/found_count', 0) > 0:
            print("\nNote: Audio files found but not downloaded (dry run mode).")
        else:
            print("\nWarning: No audio files found on the website.")


# Utility functions for URL validation
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def normalize_url(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        return "http://" + url
    return url


# Extended help documentation
HELP_DOCUMENTATION = """
hget-audio - Comprehensive Website Audio Scraper

Description:
  This tool crawls websites and downloads all audio files found in common formats.
  It intelligently follows links within the same domain while respecting robots.txt
  and common web scraping best practices.

Features:
  - Recursive crawling with configurable depth
  - Audio format detection (MP3, WAV, OGG, M4A, FLAC, AAC)
  - Customizable inclusion/exclusion patterns
  - Size filtering for audio files
  - Respect for robots.txt rules
  - Custom user agent support
  - Concurrent downloads with rate limiting
  - Comprehensive logging and statistics

Examples:
  1. Basic usage:
     hget-audio "https://example.com/podcasts" -o "my_audios"
  
  2. Limit crawling depth and concurrency:
     hget-audio "https://example.com" -d 1 -c 8 -o "shallow_crawl"
  
  3. Specific audio formats only:
     hget-audio "https://example.com" --formats "mp3,wav" -o "mp3_wav_only"
  
  4. Exclude certain paths:
     hget-audio "https://example.com" --exclude "admin,private" -o "public_audios"
  
  5. Dry run (find but don't download):
     hget-audio "https://example.com" --dry-run -v

Configuration Tips:
  - For large sites, increase depth (-d) and concurrency (-c) values
  - For sites with anti-scraping measures, increase delay (--delay)
  - Use --ignore-robots only if you have permission to scrape the site
  - Use --verbose to see detailed scraping progress

Legal Considerations:
  Always respect website terms of service and copyright laws. Only download
  content that you have permission to access and use.

Version: 1.0.0
"""

def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(
            description="Download audio files from websites",
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=HELP_DOCUMENTATION
        )
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument("-o", "--output", default="hget.output", 
                        help="output directory (default: hget.output)")
    parser.add_argument("-d", "--depth", type=int, default=2,
                        help="max depth for crawling (default: 2)")
    parser.add_argument("-c", "--concurrency", type=int, default=16,
                        help="max concurrent requests (default: 16)")
    parser.add_argument("-t", "--timeout", type=int, default=10,
                        help="request timeout in seconds (default: 10)")
    parser.add_argument("-r", "--retries", type=int, default=2,
                        help="max retries for failed requests (default: 2)")
    parser.add_argument("-f", "--formats", default="mp3,wav,ogg,m4a,flac,aac",
                        help="audio formats to download (comma separated)")
    parser.add_argument("--ignore-robots", action="store_true",
                        help="ignore robots.txt rules")
    parser.add_argument("--user-agent", default="Mozilla/5.0 (compatible; hget-audio/1.0)",
                        help="custom user agent string")
    parser.add_argument("--delay", type=float, default=0.5,
                      help="delay between requests in seconds (default: 0.5)")
    parser.add_argument("--max-size", type=int, default=100,
                      help="max audio file size in MB (default: 100)")
    parser.add_argument("--min-size", type=int, default=1,
                      help="min audio file size in KB (default: 1)")
    parser.add_argument("--include", default="",
                      help="URL patterns to include (comma separated regex)")
    parser.add_argument("--exclude", default="logout,admin,login",
                      help="URL patterns to exclude (comma separated regex)")
    parser.add_argument("--verbose", action="store_true",
                      help="enable verbose logging")
    parser.add_argument("--dry-run", action="store_true",
                      help="simulate without downloading files")
    
    args = parser.parse_args()
    
    # Create and run command
    cmd = Command()
    cmd.run([], args)

if __name__ == "__main__":
    # This section is for direct debugging of the command
    main()