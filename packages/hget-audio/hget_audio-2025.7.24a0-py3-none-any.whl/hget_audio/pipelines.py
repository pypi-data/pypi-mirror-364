import os
import re
import logging
import hashlib
import mimetypes
from urllib.parse import urlparse
from scrapy import Request
from scrapy.pipelines.files import FilesPipeline
from scrapy.exceptions import DropItem
from scrapy.utils.misc import md5sum
from .settings import AUDIO_OUTPUT_DIR, AUDIO_MAX_SIZE, AUDIO_MIN_SIZE
from .items import AudioItem

class AudioDownloadPipeline(FilesPipeline):
    """Custom pipeline for downloading audio files"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger('AudioPipeline')
        self.skipped_files = {}
        
    @classmethod
    def from_settings(cls, settings):
        store_uri = settings['AUDIO_OUTPUT_DIR']
        return cls(store_uri=store_uri, settings=settings)
        
    def get_media_requests(self, item, info):
        """Generate a media request for the audio file"""
        if info.spider.settings.getbool('DRY_RUN'):
            # In dry run mode, don't actually download
            info.spider.crawler.stats.inc_value('audio/skipped_count')
            return []
            
        # Skip if URL is invalid
        if not self.is_valid_url(item['url']):
            self.skip_item(item, "Invalid URL", info)
            return []
            
        # Create request
        headers = {'Referer': item.get('referer', '')}
        yield Request(
            item['url'], 
            headers=headers,
            meta={'filename': item['filename'], 'item': item}
        )
        
    def item_completed(self, results, item, info):
        """Handle completed download"""
        # Check download results
        if not results:
            return item
            
        success, result_info = results[0]
        if not success:
            self.skip_item(item, "Download failed", info)
            return item
            
        # Get file info
        path = result_info['path']
        checksum = result_info['checksum']
        status = result_info['status']
        
        # Update stats
        info.spider.crawler.stats.inc_value('audio/downloaded_count')
        
        # Update item with file info
        item['path'] = path
        item['checksum'] = checksum
        item['status'] = status
        
        self.logger.info(f"Downloaded audio: {item['url']} -> {path}")
        return item
        
    def file_path(self, request, response=None, info=None, *, item=None):
        """Determine file path for downloaded audio"""
        # Get filename from request meta or URL
        filename = request.meta.get('filename', '')
        if not filename:
            filename = os.path.basename(urlparse(request.url).path)
            
        # Clean filename
        filename = self.clean_filename(filename)
        
        # Create directory structure based on domain
        parsed_url = urlparse(request.url)
        domain = parsed_url.netloc.replace('www.', '')
        domain_path = domain.replace('.', '_')
        
        # Final path
        path = os.path.join(domain_path, filename)
        
        # Ensure unique filename
        if os.path.exists(os.path.join(self.store.basedir, path)):
            base, ext = os.path.splitext(filename)
            counter = 1
            while True:
                new_filename = f"{base}_{counter}{ext}"
                new_path = os.path.join(domain_path, new_filename)
                if not os.path.exists(os.path.join(self.store.basedir, new_path)):
                    path = new_path
                    break
                counter += 1
                
        return path
        
    def media_downloaded(self, response, request, info, *, item=None):
        """Custom media download handling with size validation"""
        # Check content type
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        if not self.is_audio_content_type(content_type):
            self.skip_item(item, "Invalid content type: " + content_type, info)
            raise DropItem(f"Invalid content type: {content_type}")
            
        # Check file size
        content_length = response.headers.get('Content-Length')
        if content_length:
            file_size = int(content_length)
            if file_size > AUDIO_MAX_SIZE:
                self.skip_item(item, "File too large", info)
                raise DropItem(f"File too large: {file_size} bytes")
            if file_size < AUDIO_MIN_SIZE:
                self.skip_item(item, "File too small", info)
                raise DropItem(f"File too small: {file_size} bytes")
        
        # Continue with default processing
        return super().media_downloaded(response, request, info, item=item)
        
    def is_audio_content_type(self, content_type):
        """Check if content type is audio"""
        if not content_type:
            return False
            
        # Common audio MIME types
        audio_types = [
            'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4', 
            'audio/flac', 'audio/aac', 'audio/x-m4a', 'audio/x-wav'
        ]
        
        # Check if it's an audio type
        return any(at in content_type for at in audio_types)
        
    def is_valid_url(self, url):
        """Validate URL"""
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
        
    def clean_filename(self, filename):
        """Clean filename to remove invalid characters"""
        # Remove invalid characters
        filename = re.sub(r'[^\w\-_.() ]', '_', filename)
        
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        
        # Truncate long filenames
        if len(filename) > 150:
            name, ext = os.path.splitext(filename)
            name = name[:150 - len(ext)]
            filename = name + ext
            
        return filename
        
    def skip_item(self, item, reason, info):
        """Handle skipped items"""
        info.spider.crawler.stats.inc_value('audio/skipped_count')
        self.logger.info(f"Skipping audio: {item['url']} - {reason}")
        
        # Record skipped file
        if reason not in self.skipped_files:
            self.skipped_files[reason] = []
        self.skipped_files[reason].append(item['url'])
        
        # Update stats
        info.spider.crawler.stats.set_value('audio/skipped_files', self.skipped_files)
        raise DropItem(reason)


class AudioProcessingPipeline:
    """Post-processing for audio files"""
    def __init__(self):
        self.logger = logging.getLogger('AudioProcessing')
        
    def process_item(self, item, spider):
        """Process downloaded audio item"""
        # Verify file content
        if 'path' in item:
            file_path = os.path.join(spider.settings['AUDIO_OUTPUT_DIR'], item['path'])
            if os.path.exists(file_path):
                # Add file size to item
                item['size'] = os.path.getsize(file_path)
                
                # Verify audio signature
                with open(file_path, 'rb') as f:
                    header = f.read(100)
                    signature = self.detect_audio_signature(header)
                    if signature:
                        item['format'] = signature
                    else:
                        spider.crawler.stats.inc_value('audio/invalid_files')
                        self.logger.warning(f"Invalid audio signature: {file_path}")
        
        return item
        
    def detect_audio_signature(self, data):
        """Detect audio signature from first few bytes"""
        signatures = {
            b'ID3': 'mp3',       # MP3 with ID3 tag
            b'\xff\xfb': 'mp3',  # MP3 without ID3 tag
            b'RIFF': 'wav',      # WAV file
            b'OggS': 'ogg',      # OGG file
            b'ftypM4A': 'm4a',   # M4A file
            b'fLaC': 'flac',     # FLAC file
        }
        
        for sig, fmt in signatures.items():
            if data.startswith(sig):
                return fmt
        return None


class AudioStatsPipeline:
    """Pipeline to collect statistics about audio files"""
    def __init__(self, stats):
        self.stats = stats
        self.logger = logging.getLogger('AudioStats')
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)
        
    def process_item(self, item, spider):
        """Process item and update stats"""
        if 'size' in item:
            self.stats.inc_value('audio/total_size', item['size'])
            self.stats.inc_value('audio/count_by_format/{}'.format(item.get('format', 'unknown')))
        
        return item