# -*- coding: utf-8 -*-
# http://doc.scrapy.org/en/latest/topics/settings.html

BOT_NAME = 'blatt'

SPIDER_MODULES = ['blatt.scrapers.spiders']
NEWSPIDER_MODULE = 'blatt.scrapers.spiders'

USER_AGENT = 'blatt news scraper'

ITEM_PIPELINES = {
    'blatt.scrapers.pipelines.BlattPipeline': 300,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.httpcache.HttpCacheMiddleware': 300,
}
HTTPCACHE_ENABLED = True
HTTPCACHE_STORAGE = 'scrapy.contrib.httpcache.FilesystemCacheStorage'
EXTENSIONS = {
    'scrapy.contrib.closespider.CloseSpider': 300,
}
HTTP_CACHE_POLICY = 'scrapy.contrib.httpcache.RFC2616Policy'
CLOSESPIDER_ERRORCOUNT = 1
