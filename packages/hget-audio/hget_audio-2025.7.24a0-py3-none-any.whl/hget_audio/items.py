import scrapy

class AudioItem(scrapy.Item):
    # The URL of the audio file
    url = scrapy.Field()
    
    # The original filename from the URL
    filename = scrapy.Field()
    
    # The path where the file is saved (relative to output directory)
    path = scrapy.Field()
    
    # The referring page URL
    referer = scrapy.Field()
    
    # The depth at which this audio was found
    depth = scrapy.Field()
    
    # File size in bytes (after download)
    size = scrapy.Field()
    
    # Audio format (mp3, wav, etc.)
    format = scrapy.Field()
    
    # Download status code
    status = scrapy.Field()
    
    # File checksum (MD5)
    checksum = scrapy.Field()
    
    # Additional metadata
    metadata = scrapy.Field()
    
    # Timestamps
    timestamp = scrapy.Field()
    
    # Error information if download failed
    error = scrapy.Field()
    
    # Content type
    content_type = scrapy.Field()
    
    # Headers
    headers = scrapy.Field()
    
    # Download duration
    duration = scrapy.Field()
    
    # Content length from headers
    content_length = scrapy.Field()
    
    # Content encoding
    content_encoding = scrapy.Field()
    
    # File extension
    extension = scrapy.Field()
    
    # Domain of the audio file
    domain = scrapy.Field()
    
    # Path on the server
    server_path = scrapy.Field()
    
    # Query parameters
    query = scrapy.Field()
    
    # Fragment identifier
    fragment = scrapy.Field()
    
    # Was the file downloaded from a secure connection?
    is_secure = scrapy.Field()
    
    # File modification time (if available from headers)
    last_modified = scrapy.Field()
    
    # ETag (if available from headers)
    etag = scrapy.Field()
    
    # Content language (if available from headers)
    content_language = scrapy.Field()
    
    # Server information
    server = scrapy.Field()
    
    # Content disposition
    content_disposition = scrapy.Field()
    
    # Download location (absolute path)
    absolute_path = scrapy.Field()
    
    # Download status (success/failure)
    download_status = scrapy.Field()
    
    # Download error message
    error_message = scrapy.Field()
    
    # Download start time
    start_time = scrapy.Field()
    
    # Download end time
    end_time = scrapy.Field()
    
    # Redirect history
    redirect_urls = scrapy.Field()
    
    # Redirect reasons
    redirect_reasons = scrapy.Field()
    
    # Downloader middleware information
    downloader_info = scrapy.Field()