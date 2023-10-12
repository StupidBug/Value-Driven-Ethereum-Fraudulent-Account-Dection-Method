import json

import scrapy.extensions.httpcache


class CachePolicy(scrapy.extensions.httpcache.DummyPolicy):
    def __init__(self, settings):
        super().__init__(settings)

    def should_cache_response(self, response, request):
        if super().should_cache_response(response, request):
            data = json.loads(response.text)
            if isinstance(data.get('result'), list):
                return True
        return False

    def is_cached_response_fresh(self, cachedresponse, request):
        data = json.loads(cachedresponse.text)
        if isinstance(data.get('result'), list):
            return True
        return False
