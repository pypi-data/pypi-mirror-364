import random
import logging
from urllib.parse import urlparse
from scrapy import Request, signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from .settings import USER_AGENTS, ROTATING_PROXY_LIST

class RandomUserAgentMiddleware(UserAgentMiddleware):
    """Rotate user agents for requests"""
    
    def __init__(self, user_agents):
        self.user_agents = user_agents
        
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        user_agents = settings.getlist('USER_AGENTS', USER_AGENTS)
        return cls(user_agents)
        
    def process_request(self, request, spider):
        if self.user_agents:
            request.headers['User-Agent'] = random.choice(self.user_agents)
            
    def process_response(self, request, response, spider):
        return response
        
    def process_exception(self, request, exception, spider):
        pass


class ProxyMiddleware:
    """Rotate proxies for requests"""
    
    def __init__(self, proxy_list):
        self.proxy_list = proxy_list
        self.proxy_index = 0
        
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        proxy_list = settings.getlist('ROTATING_PROXY_LIST', ROTATING_PROXY_LIST)
        return cls(proxy_list)
        
    def process_request(self, request, spider):
        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            request.meta['proxy'] = f"http://{proxy}"
            
    def process_response(self, request, response, spider):
        return response
        
    def process_exception(self, request, exception, spider):
        # Rotate proxy on failure
        if 'proxy' in request.meta and self.proxy_list:
            old_proxy = request.meta['proxy']
            new_proxy = random.choice(self.proxy_list)
            while new_proxy == old_proxy and len(self.proxy_list) > 1:
                new_proxy = random.choice(self.proxy_list)
            request.meta['proxy'] = new_proxy
            return request


class CustomRetryMiddleware(RetryMiddleware):
    """Custom retry middleware with enhanced logging"""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.logger = logging.getLogger('RetryMiddleware')
        
    def process_response(self, request, response, spider):
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response
        
    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            return self._retry(request, exception, spider)
            
    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1
        retry_times = self.max_retry_times
        
        if retries <= retry_times:
            self.logger.debug(f"Retrying {request.url} (failed {retries} times): {reason}")
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            return retryreq
        else:
            self.logger.error(f"Gave up retrying {request.url} (failed {retries} times): {reason}")


class DomainDepthMiddleware:
    """Limit crawling depth per domain"""
    
    def __init__(self, max_depth):
        self.max_depth = max_depth
        self.depth_stats = {}
        
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        max_depth = settings.getint('DEPTH_LIMIT', 3)
        return cls(max_depth)
        
    def process_spider_output(self, response, result, spider):
        # Track depth per domain
        domain = urlparse(response.url).netloc
        current_depth = response.meta.get('depth', 0)
        
        # Initialize domain stats
        if domain not in self.depth_stats:
            self.depth_stats[domain] = {'max_depth': 0, 'pages': 0}
            
        # Update stats
        self.depth_stats[domain]['pages'] += 1
        if current_depth > self.depth_stats[domain]['max_depth']:
            self.depth_stats[domain]['max_depth'] = current_depth
            
        # Filter requests that exceed max depth
        for item in result:
            if isinstance(item, Request):
                item_depth = item.meta.get('depth', 0)
                if item_depth > self.max_depth:
                    spider.logger.debug(f"Skipping {item.url} (depth {item_depth} > max {self.max_depth})")
                    continue
            yield item
            
    def spider_closed(self, spider, reason):
        # Log depth statistics
        spider.logger.info("Domain Depth Statistics:")
        for domain, stats in self.depth_stats.items():
            spider.logger.info(f"  {domain}: {stats['pages']} pages, max depth {stats['max_depth']}")


class AudioDetectionMiddleware:
    """Early detection of audio responses"""
    
    def process_response(self, request, response, spider):
        content_type = response.headers.get('Content-Type', b'').decode('utf-8', 'ignore').lower()
        
        # Check if this is an audio response
        if 'audio' in content_type:
            spider.logger.debug(f"Audio response detected: {request.url}")
            # Mark as audio in request meta
            request.meta['is_audio'] = True
            
        return response