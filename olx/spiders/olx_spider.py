import scrapy
from scrapy.selector import Selector
from scrapy.utils.response import open_in_browser
from scrapy_playwright.page import PageMethod
import datetime
import re
import os
import uuid
import portalocker
import subprocess
import json
import random
from .my_colored_log import *


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
    Default      = "\033[39m"
    Black        = "\033[30m"
    Red          = "\033[31m"
    Green        = "\033[32m"
    Yellow       = "\033[33m"
    Blue         = "\033[34m"
    Magenta      = "\033[35m"
    Cyan         = "\033[36m"
    LightGray    = "\033[37m"
    DarkGray     = "\033[90m"
    LightRed     = "\033[91m"
    LightGreen   = "\033[92m"
    LightYellow  = "\033[93m"
    LightBlue    = "\033[94m"
    LightMagenta = "\033[95m"
    LightCyan    = "\033[96m"
    White        = "\033[97m"    
import re
import logging
import time

class OlxSpiderSpider(scrapy.Spider):
    name = 'olx_spider'

    logging.getLogger('boto3').setLevel(logging.INFO)
    logging.getLogger('botocore').setLevel(logging.INFO)
    logging.getLogger('s3transfer').setLevel(logging.INFO)  
    logging.getLogger('scrapy-playwright').setLevel(logging.INFO)
    logging.getLogger('asyncio').setLevel(logging.FATAL)  

    ## Get partitions attributes
    start_crawling_time = datetime.datetime.now()
    year   = datetime.datetime.now().year
    month  = datetime.datetime.now().month
    day    = datetime.datetime.now().day
    hour   = datetime.datetime.now().hour
    min    = datetime.datetime.now().minute

    partition = f"{year}/{month:0>2}/{day:0>2}"   

    is_aws  = True if os.environ.get("AWS_DEFAULT_REGION") else False
    taskno  =  os.environ.get("TASKNO") if "TASKNO" in os.environ else "ac"
    session =  os.environ.get("SESSION") if "SESSION" in os.environ else str(uuid.uuid4())
    path    =  "/tricarros_commons" if is_aws else "./tricarros_commons"
    url     =  f"https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/estado-{taskno}"
    output_file = re.search(r'([a-z\-]+)$', url).group()
    time_last_update = datetime.datetime.now()
    
    if not is_aws and not os.path.exists(f"{path}"):
        os.mkdir(f"{path}")

    if not os.path.exists(f"{path}/{name}"):
        os.mkdir(f"{path}/{name}")

    if not os.path.exists(f"{path}/{name}/{session}"):
        os.mkdir(f"{path}/{name}/{session}")
    path    = f"{path}/{name}"
    
    custom_settings = { 
        "RETRY_ENABLED": False,        
        "DOWNLOAD_DELAY": 0, 
        'FEEDS': {
                    f's3://tweets2/tricarros/data/{name}/{partition}/{name}_{hour:0>2}{min:0>2}_{taskno:0>2}.json': {'format': 'json', 'overwrite': True},
                    f'./data/{output_file}.json': {'format': 'json', 'overwrite': True},
                    f'./data/{output_file}.csv': {'format': 'csv', 'overwrite': True}
                  },
        #'FEEDS': {f'{output_file}.json': {'format': 'json', 'overwrite': True}},        
        'USER_AGENT': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }     
    handle_httpstatus_list = [200, 400]
    print_info(json.dumps(custom_settings['FEEDS']))
    #Start a local webserver to watch crawling status
    if is_aws: 
        subprocess.Popen("pm2 start app.py --interpreter /usr/bin/python3", shell=True)

    def save_stats(self):
        with portalocker.Lock(f'{self.path}/{self.session}/page_crawled_times_{self.taskno}.json', 'w', encoding='utf-8', timeout=60) as meta_file4:                                                 
            elapsed_crawling_time = datetime.datetime.now(self.crawler.stats.get_stats()['start_time'].tzinfo) - self.crawler.stats.get_stats()['start_time']     
            estimated_crawling_time = elapsed_crawling_time / (self.crawler.stats.get_stats()['downloader/request_count']/self.crawler.stats.get_stats()['scheduler/enqueued'])   
            remaining_crawling_time = estimated_crawling_time - elapsed_crawling_time

            page_crawled_times = {
                                  "start_crawling_time": f"{self.start_crawling_time}", 
                                  "current_time": f"{datetime.datetime.now()}", 
                                  "elapsed_crawling_time": f"{elapsed_crawling_time}", 
                                  "estimated_crawling_time": f"{estimated_crawling_time}", 
                                  "remaining_crawling_time": f"{remaining_crawling_time}", 
                                  "crawled_pages": f"{self.crawler.stats.get_stats()['downloader/request_count']}", 
                                  "total_pages": f"{self.crawler.stats.get_stats()['scheduler/enqueued']}", 
                                  "percentage": f"{int(100*self.crawler.stats.get_stats()['downloader/request_count']/self.crawler.stats.get_stats()['scheduler/enqueued'])}",
                                  "page_speed": f"{elapsed_crawling_time/int(self.crawler.stats.get_stats()['downloader/request_count'])}",
                                  "page_duplicated_filtered": f"{self.crawler.stats.get_stats()['dupefilter/filtered']}" if 'dupefilter/filtered' in self.crawler.stats.get_stats() else 0, 
                                  }
            json.dump(page_crawled_times, meta_file4, indent=4)  
            meta_file4.flush()
            os.fsync(meta_file4.fileno())         

    def start_requests(self):
        #self.save_stats()
        yield scrapy.Request(url=self.url, callback=self.parse_category_page, meta={"playwright": True, "playwright_include_page": True})
        
    async def parse_category_page(self, response): 
        self.save_stats()
        playwright_page = response.meta['playwright_page']
        print(bcolors.LightMagenta + bcolors.BOLD  + f"parse_category_page({bcolors.ENDC}{response.url}{bcolors.LightMagenta})" + bcolors.ENDC)
        xdrilldown  = '//a[@*="linkshelf_item"]'
        drilldown = response.xpath(xdrilldown)
        
        if response.status > 300:
            print(response.body)

        if len(drilldown) == 0:
            # Checking how many pages there are
            text = response.css("li.cOoFTP span::text").get() 
            page_list = response.xpath('//a[@data-ds-component="DS-Button"]').css('::attr(href)')
            if len(page_list) > 0:
                last_page = page_list[len(page_list) - 1].get()
                base_link = re.search(r'^([\s\S]*)\?o=(\d+)$', last_page)[1]
                last_page_number = int(re.search(r'(\d+)$', last_page).group())
                for page in range(1, last_page_number+1):
                    link = f"{base_link}?o={page}"                                
                    print(bcolors.WARNING + text + f" ({page}) " + bcolors.OKBLUE + link + bcolors.ENDC)     
                    yield scrapy.Request(link, callback=self.parse_listpage, priority=10, errback=self.close_page_error)

        for i, ad in enumerate(drilldown):
            link  = response.xpath(xdrilldown)[i].css('a::attr(href)').get()            
            text  = response.xpath(xdrilldown)[i].css('a::text').get()  
            print(bcolors.WARNING + text + " " + bcolors.OKBLUE + link + bcolors.ENDC)
            yield scrapy.Request(url=link, callback=self.parse_category_page, priority=100, errback=self.close_page_error, meta={
                "playwright": True,
                "playwright_include_page": True
                })
            
        await playwright_page.close()
    
    def parse_listpage(self, response):      
        self.save_stats()
        ########################################################
        # Parse the page (actualy send request for detail page)
        ########################################################
        ad_div = '//section[@data-ds-component="DS-AdCard"]'

        print(bcolors.LightCyan + f"parse_listpage({response.url[:10]}...{response.url[-67:]}) {bcolors.Black} >> {bcolors.LightCyan} response(selector) {len(response.xpath(ad_div))}" + bcolors.ENDC)
        
        if len(response.xpath(ad_div)) == 0:
            print(bcolors.OKCYAN + f"STILL ZERO ITENS: {response.url[:10]}...{response.url[-67:]}" + bcolors.ENDC)  
            #redirecting to playwright
            yield scrapy.Request(url=response.url+'?getcontent=true', priority=10, callback=self.parse_listpage_playwright, errback=self.close_page_error, meta={
                "playwright": True,
                "playwright_include_page": True
                })

            return
                
        for item in response.xpath(ad_div):
            answer =  {
                'id': re.search(r"([0-9]+)$", item.css("a::attr(href)").get()).group(),
                'link': item.css("a::attr(href)").get(),
                'title': item.css("h2::text").get()
            }
            yield scrapy.Request(url=item.css("a::attr(href)").get(), priority=1, callback=self.parse_detailpage)            
            #yield answer
            
    async def parse_listpage_playwright(self, response):      
        page = response.meta['playwright_page']
        self.save_stats()
        
        ########################################################
        # Move page down to load other Ads
        ########################################################
        await page.evaluate("window.scrollBy(0, 1000)")
        time.sleep(100 / 1000)
        await page.evaluate("window.scrollBy(0, 2000)")
        time.sleep(100 / 1000)   
        selector = Selector(text=await page.content())
        await page.close()
        await page.context.close()


        ########################################################
        # Parse the page (actualy send request for detail page)
        ########################################################
        ad_div = '//section[@data-ds-component="DS-AdCard"]'

        print(bcolors.LightGreen + f"parse_listpage({response.url[:10]}...{response.url[-67:]}) {bcolors.Black} >> {bcolors.LightCyan} response(selector) {len(response.xpath(ad_div))}({len(selector.xpath(ad_div))})" + bcolors.ENDC)
        
        if len(selector.xpath(ad_div)) == 0:
            #print(response.text)
            print(bcolors.OKCYAN + f"STILL ZERO ITENS: {response.url[:10]}...{response.url[-67:]}" + bcolors.ENDC)      
        for item in selector.xpath(ad_div):
            answer =  {
                'id': re.search(r"([0-9]+)$", item.css("a::attr(href)").get()).group(),
                'link': item.css("a::attr(href)").get(),
                'title': item.css("h2::text").get()
            }
            #print(answer)
            yield answer
        #############################################################################################            
        # NEXT PAGEs
        #############################################################################################
        # It will call the same page multiple times, but scrapy handle it properly.
        # It is preferable do it than getting only next page. If the crawller get an error
        # chances are good the next page was already piped. In case for some reason you need 
        # just next page, use commented code:
        #
        # total_links = len(selector.xpath('//a[@data-ds-component="DS-Button"]').css("::attr(href)"))
        # next_page = selector.xpath('//a[@data-ds-component="DS-Button"]').css("::attr(href)")[total_links - 2].get()
        # print_sucess(next_page)
        for link in selector.xpath('//a[@data-ds-component="DS-Button"]').css("::attr(href)"):
            yield scrapy.Request(link.get(), callback=self.parse_listpage, priority=10, errback=self.close_page_error)        

    async def parse_detailpage(self, response):
        if random.random() > 0.95:  
            self.save_stats()        
        # item_id = str(self.crawler.stats.get_stats()['item_scraped_count']+1) if "item_scraped_count" in self.crawler.stats.get_stats() else "1"
        # print(bcolors.LightGreen + item_id + f" - {bcolors.Blue} {response.url}" + bcolors.ENDC)
        
        modelo               = ""
        marca                = ""
        tipo_veiculo         = ""
        ano_veiculo          = ""
        quilometragem        = ""
        potencia_motor       = ""
        tipo_combustivel     = ""
        kit_gnv              = ""
        tipo_cambio          = ""
        cor_veiculo          = ""
        numero_portas        = ""
        final_placa_veiculo  = ""
        tipo_direcao_veiculo = ""
        for item in response.css(".fzAouC"):
            label = item.css("::text").get()
            value = item.xpath("..").css("a::text").get() or item.xpath('../span[2]/text()').get()
            if label == "Modelo"  : modelo = value
            if label == "Marca" : marca = value
            if label == "Tipo de veículo" : tipo_veiculo = value
            if label == "Ano" : ano_veiculo = value
            if label == "Quilometragem" : quilometragem = value
            if label == "Potência do motor" : potencia_motor = value
            if label == "Combustível" : tipo_combustivel = value
            if label == "Possui Kit GNV" : kit_gnv = value
            if label == "Câmbio" : tipo_cambio = value
            if label == "Cor" : cor_veiculo = value
            if label == "Portas" : numero_portas = value
            if label == "Final de placa" : final_placa_veiculo = value
            if label == "Tipo de direção" : tipo_direcao_veiculo = value

        answer =  {
            "id":                   re.search(r"([0-9]){5,}", response.url).group(),  
            "link":                 response.url,
            "data_anuncio":         response.css(".dHNWJq::text")[5].get(),
            "titulo_anuncio":       response.css("h1::text").get(),                        
            "descricao_anuncio":    response.css("span.jcyavR::text").getall()[1],
            "valor_veiculo":        int(response.css("h2.honhBH::text").get()[3:].replace('.', '')) if response.css("h2.honhBH::text") else "", 
            #"valor_veiculo":        int(response.css("span.jcyavR::text").getall()[0][3:].replace('.', '')),
            "cep_anuncio":          response.css(".fIggF::text")[0].get(),
            "cidade_anuncio":       response.css(".fIggF::text")[1].get(),
            "uf_anuncio":           re.search(r"https:\/\/([a-z]{2})[\s\S]+", response.url)[1], #self.taskno,
            "bairro_anuncio":       response.css(".fIggF::text")[2].get(),
            
            "tipo_anuncio":         response.css(".bKbCBo::text")[1].get(),
            "modelo_veiculo":       modelo,
            "marca_veiculo":        marca,
            "ano_fabricacao":       ano_veiculo,
            "tipo_combustivel":     tipo_combustivel,

            "tipo_veiculo":         tipo_veiculo,
            "quilometragem":        quilometragem,
            "potencia_motor":       potencia_motor,
            "possui_kit_gnv":       kit_gnv,
            "tipo_cambio":          tipo_cambio,
            "cor_veiculo":          cor_veiculo,
            "numero_portas":        numero_portas,
            "numero_final_placa":   final_placa_veiculo,
            "tipo_direcao":         tipo_direcao_veiculo
        }
        yield answer

    async def close_page_error(self, failure):
        self.save_stats()
        if "playwright_page" in failure.request.meta:
            page = failure.request.meta['playwright_page']        
            await page.close()
            await page.context.close()
            retries = 1 if "retries" not in failure.request.meta else int(failure.request.meta['retries']) + 1
            print_error(f"ERROR - Retentando a página {bcolors.Blue} {failure.request.url} {bcolors.Red} pela {int(retries+1)}ª vez")
            yield scrapy.Request(failure.request.url, 
                                dont_filter = True,
                                errback=self.close_page_error,
                                priority=1000,
                                callback=failure.request.callback, 
                                meta={"retries": retries, "playwright": True, "playwright_include_page": True})


        self.logger.error(repr(failure))

    def closed(self, reason):
        self.save_stats()
        if self.is_aws: 
            subprocess.Popen("pm2 stop app.py", shell=True)        