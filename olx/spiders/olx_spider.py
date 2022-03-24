import scrapy
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
import re

    

class OlxSpiderSpider(scrapy.Spider):
    name = 'olx_spider'
    # allowed_domains = ['olx.com.br']
    # start_urls = ['http://olx.com.br/']
    

    def start_requests(self):
        _start_urls = ['http://olx.com.br/']        
        # yield scrapy.Request(url=_start_urls[0], callback=self.parse)       
        # url = 'https://sp.olx.com.br/sao-paulo-e-regiao/animais-de-estimacao/cachorros'
        url = 'https://sp.olx.com.br/animais-de-estimacao/cachorros'

        yield scrapy.Request(url=url, callback=self.parse_category_page)
        

    def parse_category_page(self, response): 
        
        xdrilldown  = '//a[@*="linkshelf_item"]'
        drilldown = response.xpath(xdrilldown)

        if len(drilldown) == 0:
            print(bcolors.WARNING + " Yielding  " + bcolors.OKBLUE + response.url + bcolors.ENDC)            
            yield scrapy.Request(url=response.url+'?getcontent=true', callback=self.parse_listpage)

        for i, ad in enumerate(drilldown):
            link  = response.xpath(xdrilldown)[i].css('a::attr(href)').get()            
            text  = response.xpath(xdrilldown)[i].css('a::text').get()  
            print(bcolors.WARNING + text + " " + bcolors.OKBLUE + link + bcolors.ENDC)
            yield scrapy.Request(url=link, callback=self.parse_category_page)

    def parse_listpage(self, response):
        # XPath for itens on page
        ad_div = '//div[@class="fnmrjs-1 gIEtsI"]'
        xtitle  = '//div[@class="fnmrjs-1 gIEtsI"]//h2[@title]'
        xlink   = '//div[@class="fnmrjs-1 gIEtsI"]/parent::a'
        xprice  = '//div[@class="fnmrjs-1 gIEtsI"]//div[@class="aoie8y-0 hRScWw"]'
        xplace  = '//div[@class="fnmrjs-1 gIEtsI"]//div[@class="sc-7l84qu-0 gmtqTp"]'
        xtype   = '//div[@class="fnmrjs-8 jdXcwM"]'
                
        ad_divs = response.xpath(ad_div)
        # for ad in ad_divs:   
        for i, ad in enumerate(ad_divs):
            link  = ad.xpath(xlink)[i].css('a::attr(href)').get()            
            id = re.search(r"([0-9]+)$", link).group()
            #alternative way in XPATH  ad.xpath(xtitle+"/text()").get()
            title = ad.xpath(xtitle)[i].css('::text').get()  
            try:
                price = re.search(r"[0-9.,]+$", ad.xpath(xprice)[i].css('::text').get()).group().replace('.', '').replace(',', '')
            except:
                price = ''
            type  = ad.xpath(xtype)[i].css('::text').get()
            place  = ad.xpath(xplace)[i].css('::text').get()

            yield {
                'id': id,
                'link': link,
                'title': title,
                'type': type,
                'place': place,
                'price': price
            }

        # next page (if avaiable)
        xnext_page = '//a[@data-lurker-detail="next_page"]'
        next_page  = response.xpath(xnext_page).css('a::attr(href)').get()
        yield scrapy.Request(next_page, callback=self.parse_listpage)
            

    def parse_detailpage(self, response):
        print(bcolors.WARNING + f"HTTP Status Code: {response.status}" + bcolors.ENDC)        
        print(response.text)

        # //li[@class="list-inline-item "]
        links = '//li[@class="list-inline-item "]'
        for li in response.xpath(links):
            a = li.css('a::attr(href)').get()        
        print(a)
        pass
