import json

import scrapy.extensions.httpcache


class CachePolicy(scrapy.extensions.httpcache.DummyPolicy):
    def __init__(self, settings):
        super().__init__(settings)

    def should_cache_response(self, response, request):
        if super().should_cache_response(response, request):
            status = json.loads(response.text)['status']
            if status == '1':
                return True
        return False
