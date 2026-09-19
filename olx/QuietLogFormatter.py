from scrapy.logformatter import LogFormatter
import scrapy
import logging

class QuietLogFormatter(scrapy.logformatter.LogFormatter):
    """Be quieter about scraped items."""
    def scraped(self, item, response, spider):
        return (
            super().scraped(item, response, spider)
            if spider.settings.getbool("LOG_SCRAPED_ITEMS")
            else None
        )
    def crawled(self, item, response, spider):
        return (
            super().crawled(item, response, spider)
            if spider.settings.getbool("LOG_SCRAPED_ITEMS")
            else None
        )

    # def scraped(self, item, response, spider):
    #     return {
    #         "level": logging.INFO,
    #         "msg": "None",
    #         "args": {
    #             "src": "None",
    #             "item": "None",
    #         }
    #     }