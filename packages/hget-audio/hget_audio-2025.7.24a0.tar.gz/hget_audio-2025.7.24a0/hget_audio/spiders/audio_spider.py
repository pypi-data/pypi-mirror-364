import re
import os
import logging
from urllib.parse import urljoin, urlparse
from scrapy import Spider, Request
from scrapy.http import HtmlResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.response import get_base_url
from ..items import AudioItem
from ..settings import AUDIO_FORMATS, INCLUDE_PATTERNS, EXCLUDE_PATTERNS

class AudioSpider(Spider):
    name = "audio_spider"
    custom_settings = {
        'DEPTH_PRIORITY': 1,
        'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
        'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue',
    }
    
    def __init__(self, start_urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = start_urls or []
        self.allowed_domains = self.extract_domains(start_urls)
        self.audio_formats = set(fmt.lower() for fmt in AUDIO_FORMATS)
        self.audio_ext_pattern = re.compile(
            r'\.({})$'.format('|'.join(self.audio_formats)), 
            re.IGNORECASE
        )
        self.include_patterns = [re.compile(p, re.I) for p in INCLUDE_PATTERNS] if INCLUDE_PATTERNS else []
        self.exclude_patterns = [re.compile(p, re.I) for p in EXCLUDE_PATTERNS] if EXCLUDE_PATTERNS else []
        self.link_extractor = LinkExtractor(
            deny_extensions=[],
            tags=('a', 'area', 'iframe'),
            attrs=('href', 'src')
        )
        self.seen_audio = set()
        self.logger.setLevel(logging.DEBUG)
        
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=Spider.spider_closed)
        return spider
        
    def spider_closed(self, spider):
        self.logger.info(f"Spider closed: {spider.name}")
        stats = spider.crawler.stats.get_stats()
        self.logger.info(f"Total pages crawled: {stats.get('response_received_count', 0)}")
        self.logger.info(f"Audio files found: {stats.get('audio/found_count', 0)}")
        self.logger.info(f"Audio files downloaded: {stats.get('audio/downloaded_count', 0)}")
        
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse, meta={'depth': 0})
            
    def parse(self, response):
        # Log progress
        depth = response.meta.get('depth', 0)
        self.logger.debug(f"Parsing page (depth={depth}): {response.url}")
        
        # Extract all links from the page
        base_url = get_base_url(response)
        links = self.link_extractor.extract_links(response)
        
        # Process links for further crawling
        for link in links:
            if self.should_follow(link.url, response):
                yield Request(
                    link.url, 
                    callback=self.parse, 
                    meta={'depth': depth + 1}
                )
        
        # Find and process audio files
        yield from self.find_audio_files(response)
        
    def find_audio_files(self, response):
        """Find all audio files in the page"""
        base_url = get_base_url(response)
        
        # Find audio links in <a> tags
        for a_tag in response.css('a'):
            href = a_tag.attrib.get('href', '')
            if self.is_audio_url(href):
                yield self.build_audio_item(href, base_url, response)
        
        # Find audio elements
        for audio_tag in response.css('audio'):
            src = audio_tag.attrib.get('src', '')
            if src and self.is_audio_url(src):
                yield self.build_audio_item(src, base_url, response)
            
            # Audio sources
            for source in audio_tag.css('source'):
                src = source.attrib.get('src', '')
                if src and self.is_audio_url(src):
                    yield self.build_audio_item(src, base_url, response)
        
        # Find object embeds
        for object_tag in response.css('object'):
            data = object_tag.attrib.get('data', '')
            if data and self.is_audio_url(data):
                yield self.build_audio_item(data, base_url, response)
        
        # Find embed tags
        for embed_tag in response.css('embed'):
            src = embed_tag.attrib.get('src', '')
            if src and self.is_audio_url(src):
                yield self.build_audio_item(src, base_url, response)
        
        # Find video tags that might contain audio
        for video_tag in response.css('video'):
            src = video_tag.attrib.get('src', '')
            if src and self.is_audio_url(src):
                yield self.build_audio_item(src, base_url, response)
                
            for source in video_tag.css('source'):
                src = source.attrib.get('src', '')
                if src and self.is_audio_url(src):
                    yield self.build_audio_item(src, base_url, response)
        
        # Find JavaScript data sources (common patterns)
        script_text = response.text
        js_patterns = [
            r'["\'](https?://[^"\']+?\.(?:{}))["\']'.format('|'.join(self.audio_formats)),
            r'url\(["\']?(https?://[^"\'\)]+?\.(?:{}))["\']?\)'.format('|'.join(self.audio_formats)),
            r'["\'](?:filePath|audioUrl|soundFile|src|url)\s*["\']?\s*:\s*["\'](https?://[^"\']+?\.(?:{}))["\']'.format('|'.join(self.audio_formats))
        ]
        
        for pattern in js_patterns:
            for match in re.finditer(pattern, script_text, re.IGNORECASE):
                audio_url = match.group(1)
                if self.is_audio_url(audio_url):
                    yield self.build_audio_item(audio_url, base_url, response)
    
    def build_audio_item(self, audio_url, base_url, response):
        """Build an AudioItem from a URL"""
        # Make absolute URL
        audio_url = urljoin(base_url, audio_url)
        
        # Extract filename
        filename = os.path.basename(urlparse(audio_url).path)
        
        # Create item
        item = AudioItem()
        item['url'] = audio_url
        item['filename'] = filename
        item['referer'] = response.url
        item['depth'] = response.meta.get('depth', 0)
        
        # Add stats
        self.crawler.stats.inc_value('audio/found_count')
        
        return item
    
    def is_audio_url(self, url):
        """Check if URL points to an audio file"""
        # Skip empty URLs
        if not url:
            return False
            
        # Skip non-HTTP URLs
        if not url.startswith(('http://', 'https://')):
            return False
            
        # Check if we've seen this audio before
        if url in self.seen_audio:
            return False
            
        # Check extension
        if not self.audio_ext_pattern.search(url):
            return False
            
        # Check include/exclude patterns
        if not self.should_process(url):
            return False
            
        # Add to seen set
        self.seen_audio.add(url)
        return True
        
    def should_follow(self, url, response):
        """Determine whether to follow a link"""
        # Skip non-HTTP URLs
        if not url.startswith(('http://', 'https://')):
            return False
            
        # Check if URL is within allowed domains
        parsed = urlparse(url)
        if not any(parsed.netloc.endswith(d) for d in self.allowed_domains):
            return False
            
        # Check depth limit
        depth = response.meta.get('depth', 0)
        if depth >= self.settings.getint('DEPTH_LIMIT'):
            self.logger.debug(f"Reached depth limit at {url} (depth={depth})")
            return False
            
        # Check include/exclude patterns
        if not self.should_process(url):
            return False
            
        return True
        
    def should_process(self, url):
        """Check URL against include and exclude patterns"""
        # Apply include patterns (if any)
        if self.include_patterns:
            if not any(pattern.search(url) for pattern in self.include_patterns):
                return False
                
        # Apply exclude patterns
        if any(pattern.search(url) for pattern in self.exclude_patterns):
            return False
            
        return True
        
    def extract_domains(self, urls):
        """Extract base domains from start URLs"""
        domains = set()
        for url in urls:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            domains.add(domain)
        return list(domains)


# Audio detection utilities
class AudioDetector:
    """Advanced audio file detection"""
    AUDIO_MIME_TYPES = {
        'audio/mpeg': 'mp3',
        'audio/wav': 'wav',
        'audio/ogg': 'ogg',
        'audio/mp4': 'm4a',
        'audio/flac': 'flac',
        'audio/aac': 'aac',
        'audio/x-m4a': 'm4a',
        'audio/x-aiff': 'aiff',
        'audio/x-wav': 'wav',
    }
    
    @classmethod
    def is_audio_content_type(cls, content_type):
        """Check if content type is audio"""
        return content_type.split(';')[0] in cls.AUDIO_MIME_TYPES
    
    @classmethod
    def get_extension_from_content_type(cls, content_type):
        """Get file extension from content type"""
        base_type = content_type.split(';')[0]
        return cls.AUDIO_MIME_TYPES.get(base_type)


# URL processing utilities
class URLProcessor:
    """Advanced URL processing and normalization"""
    @staticmethod
    def normalize_url(url, base_url):
        """Normalize and clean URL"""
        # Basic joining
        url = urljoin(base_url, url)
        
        # Remove fragments
        parsed = urlparse(url)
        url = parsed._replace(fragment='').geturl()
        
        # Normalize case
        url = re.sub(r'%[0-9a-f]{2}', lambda m: m.group(0).upper(), url)
        
        # Remove duplicate slashes
        if parsed.scheme:
            url = re.sub(r'(?<!:)//+', '/', url)
        
        return url
    
    @staticmethod
    def get_filename_from_url(url):
        """Extract filename from URL"""
        parsed = urlparse(url)
        path = parsed.path
        filename = os.path.basename(path)
        
        # Clean filename
        if not filename:
            filename = "audio"
        
        # Add extension if missing
        if '.' not in filename:
            filename += ".audio"
            
        return filename


# Content analysis for audio detection
class ContentAnalyzer:
    """Analyze content for audio signatures"""
    AUDIO_SIGNATURES = {
        b'ID3': 'mp3',       # MP3 with ID3 tag
        b'\xff\xfb': 'mp3',  # MP3 without ID3 tag
        b'RIFF': 'wav',      # WAV file
        b'OggS': 'ogg',      # OGG file
        b'ftypM4A': 'm4a',   # M4A file
        b'fLaC': 'flac',     # FLAC file
    }
    
    @classmethod
    def detect_audio_signature(cls, data):
        """Detect audio signature from first few bytes"""
        for signature, fmt in cls.AUDIO_SIGNATURES.items():
            if data.startswith(signature):
                return fmt
        return None


# Advanced link extraction
class AdvancedLinkExtractor:
    """Extract links with additional heuristics"""
    @staticmethod
    def extract_links(response):
        """Extract links from various sources"""
        links = set()
        
        # Standard HTML links
        links.update(LinkExtractor().extract_links(response))
        
        # JavaScript links
        links.update(AdvancedLinkExtractor.extract_js_links(response))
        
        # CSS links
        links.update(AdvancedLinkExtractor.extract_css_links(response))
        
        # Meta refresh redirects
        links.update(AdvancedLinkExtractor.extract_meta_refresh(response))
        
        return list(links)
    
    @staticmethod
    def extract_js_links(response):
        """Extract links from JavaScript code"""
        links = set()
        script_text = response.text
        
        # Common patterns for URLs in JS
        patterns = [
            r'window\.location\s*=\s*["\']([^"\']+)["\']',
            r'window\.location\.href\s*=\s*["\']([^"\']+)["\']',
            r'window\.location\.replace\(["\']([^"\']+)["\']\)',
            r'window\.open\(["\']([^"\']+)["\']',
            r'["\'](https?://[^"\']+)["\']',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, script_text, re.IGNORECASE):
                url = match.group(1)
                url = urljoin(response.url, url)
                links.add(url)
                
        return links
    
    @staticmethod
    def extract_css_links(response):
        """Extract links from CSS"""
        links = set()
        css_text = response.text
        
        # Background images, @import, etc.
        patterns = [
            r'url\(["\']?([^)"\']+)["\']?\)',
            r'@import\s+["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, css_text, re.IGNORECASE):
                url = match.group(1)
                url = urljoin(response.url, url)
                links.add(url)
                
        return links
    
    @staticmethod
    def extract_meta_refresh(response):
        """Extract URLs from meta refresh tags"""
        links = set()
        for meta in response.css('meta[http-equiv="refresh"]'):
            content = meta.attrib.get('content', '')
            match = re.search(r'url\s*=\s*([^\s]+)', content, re.IGNORECASE)
            if match:
                url = match.group(1)
                url = urljoin(response.url, url)
                links.add(url)
        return links