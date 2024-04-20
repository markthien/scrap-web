import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse
import json
import validators
import replace
import sys
from pathlib import Path
from scrapy.utils.log import configure_logging
import re
import datetime

stock_analysis = {}

###############################
# Extract EPS from some website
###############################
class EPSGrowthSpiderFromWeb(scrapy.Spider):
    name = 'eps_growth_spider'

    def __init__(self, url=None, scrap_pattern=None, domain_name=None, *args, **kwargs):
        super(EPSGrowthSpiderFromWeb, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.scrap_pattern = scrap_pattern
        self.domain_name = domain_name

    def parse(self, response):     
        if self.domain_name == 'finviz.com':
            eps_growth_percent = response.xpath(self.scrap_pattern).get()
        if self.domain_name == 'zacks.com':
            eps_growth_percent = response.css(self.scrap_pattern).get()
        if self.domain_name == 'stockanalysis.com':
            eps_growth_percent = response.xpath(self.scrap_pattern).extract_first() 
        if self.domain_name == 'finance.yahoo.com':
            eps_growth_percent = response.xpath(self.scrap_pattern).get()
        stock_analysis['eps_growth_rate']['from_site'].append({'domain_name':self.start_urls[0], 'eps':eps_growth_percent})

############################################
# Extract outstanding share from a website
############################################
class OutstandingShare(scrapy.Spider):
    name = 'outstanding_share'

    def __init__(self, url=None, scrap_pattern=None, domain_name=None, *args, **kwargs):
        super(OutstandingShare, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.scrap_pattern = scrap_pattern
        self.domain_name = domain_name

    def parse(self, response):
        outstanding_share = response.xpath(self.scrap_pattern).get()
        if outstanding_share.endswith('M'):
            outstanding_share = outstanding_share[:-1]
            outstanding_share = '{:,.0f}'.format(float(outstanding_share) * 1000000)
        if outstanding_share.endswith('B'):
            outstanding_share = outstanding_share[:-1]
            outstanding_share = '{:,.0f}'.format(float(outstanding_share) * 1000000000)            
        stock_analysis['outstanding_share'] = outstanding_share

############################################
# Extract current price from a website
############################################
class CurrentPrice(scrapy.Spider):
    name = 'current_price'

    def __init__(self, url=None, scrap_pattern=None, domain_name=None, *args, **kwargs):
        super(CurrentPrice, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.scrap_pattern = scrap_pattern
        self.domain_name = domain_name

    def parse(self, response):
        stock_analysis['current_price'] = response.xpath(self.scrap_pattern).get()        

############################################
# Extract Beta from a website
############################################
class Beta(scrapy.Spider):
    name = 'beta'

    def __init__(self, url=None, scrap_pattern=None, domain_name=None, *args, **kwargs):
        super(Beta, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.scrap_pattern = scrap_pattern
        self.domain_name = domain_name

    def parse(self, response):     
        stock_analysis['beta'] = response.xpath(self.scrap_pattern).get()        

###############################
# Extract Operating Cash Flow
###############################
class OperatingCashFlow(scrapy.Spider):
    name = 'operating_cash_flow'

    def __init__(self, url=None, scrap_pattern=None, *args, **kwargs):
        super(OperatingCashFlow, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.scrap_pattern = scrap_pattern

    def parse(self, response):
        # result = response.xpath(self.scrap_pattern).get()
        stock_analysis['operating_cash_flow'] = response.xpath(self.scrap_pattern).get()

##############################################################
# Extract Cash Flow from Continuing Operating Activities
##############################################################
class CashFlowFromContinuingOperatingActivities(scrapy.Spider):
    name = 'cash_flow_from_continuing_operating_activities'

    def __init__(self, url=None, scrap_pattern=None, *args, **kwargs):
        super(CashFlowFromContinuingOperatingActivities, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.scrap_pattern = scrap_pattern
        print(f'self.start_urls301: {self.start_urls}')
        print(f'self.scrap_pattern301: {self.scrap_pattern}')

    def parse(self, response):
        result = response.xpath(self.scrap_pattern).get()
        stock_analysis['cash_flow_from_continuing_operating_activities'] = result   

##############################################################
# Extract Net Income 
##############################################################
class NetIncome(scrapy.Spider):
    name = 'net_income'

    def __init__(self, url=None, scrap_pattern=None, *args, **kwargs):
        super(NetIncome, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.scrap_pattern = scrap_pattern

    def parse(self, response):   
        # result = response.xpath(self.scrap_pattern).get()
        stock_analysis['net_income'] = response.xpath(self.scrap_pattern).get()

###############################
# Extract Free Cash Flow
###############################
class FreeCashFlow(scrapy.Spider):
    name = 'free_cash_flow'

    def __init__(self, url=None, scrap_pattern=None, *args, **kwargs):
        super(FreeCashFlow, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.scrap_pattern = scrap_pattern
        print(f'result400  : {self.start_urls}')
        print(f'result401  : {self.scrap_pattern}')

    def parse(self, response):
        result = response.xpath(self.scrap_pattern).get()
        print(f'result free_cash_flow : {result}')
        stock_analysis['free_cash_flow'] = result

#######################
# start of the program
#######################
def start():
    input_file = open ('setting_site_scrap.json')
    json_object = json.load(input_file)

    site_to_get_eps_growth = json_object['site_to_get_eps_growth']

    stock_analysis['stock_symbol'] = json_object['stock_symbol']
    stock_analysis['eps_growth_rate'] = {}
    stock_analysis['eps_growth_rate']['from_site'] = []

    # Run the Spider
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'HTTPCACHE_ENABLED': True,
        'HTTPCACHE_EXPIRATION_SECS': 604800,  # 24 hours
        'HTTPCACHE_STORAGE': 'scrapy.extensions.httpcache.FilesystemCacheStorage',
        'HTTPCACHE_DIR': 'httpcache',
    })

    for item in site_to_get_eps_growth:
        url = item['url'].replace('STOCK_SYMBOL', json_object['stock_symbol'])
        if not validators.url(url):
            print(f'Invalid url: {url}')
            sys.exit(1)
        domain_name = urlparse(url).netloc
        domain_name = domain_name.replace('www.', '')
        process.crawl(EPSGrowthSpiderFromWeb, url=url, scrap_pattern=item['scrap_pattern'], domain_name=domain_name)

    process.crawl(OperatingCashFlow, url=json_object['operating_cash_flow']['url'].replace('STOCK_SYMBOL', json_object['stock_symbol']), scrap_pattern=json_object['operating_cash_flow']['scrap_pattern'])
    process.crawl(NetIncome, url=json_object['net_income']['url'].replace('STOCK_SYMBOL', json_object['stock_symbol']), scrap_pattern=json_object['net_income']['scrap_pattern'])
    process.crawl(OutstandingShare, url=json_object['outstanding_share']['url'].replace('STOCK_SYMBOL', json_object['stock_symbol']), scrap_pattern=json_object['outstanding_share']['scrap_pattern'])
    process.crawl(Beta, url=json_object['beta']['url'].replace('STOCK_SYMBOL', json_object['stock_symbol']), scrap_pattern=json_object['beta']['scrap_pattern'])
    process.crawl(CurrentPrice, url=json_object['current_price']['url'].replace('STOCK_SYMBOL', json_object['stock_symbol']), scrap_pattern=json_object['current_price']['scrap_pattern'])
    process.crawl(FreeCashFlow, url=json_object['current_price']['url'].replace('STOCK_SYMBOL', json_object['stock_symbol']), scrap_pattern=json_object['free_cash_flow']['scrap_pattern'])
    # process.crawl(CashFlowFromContinuingOperatingActivities, url=json_object['cash_flow_from_continuing_operating_activities']['url'].replace('STOCK_SYMBOL', json_object['stock_symbol']), scrap_pattern=json_object['cash_flow_from_continuing_operating_activities']['scrap_pattern'])
    
    process.start()

    # Use discounted cash flow or discounted free cash flow method
    divide_result = 0
    if not stock_analysis['operating_cash_flow'] is None:
        divide_result = round(int(stock_analysis['operating_cash_flow'].replace(',', ''))/int(stock_analysis['net_income'].replace(',', '')), 2)
    stock_analysis['valuation_method'] = 'Discounted Cash Flow'
    if divide_result > 1.5:
        stock_analysis['valuation_method'] = 'Discounted Free Cash Flow'

    # Calculate the average eps growth
    total_eps = 0
    num_of_eps_obtained = 0
    for item in stock_analysis['eps_growth_rate']['from_site']:
        if item['eps'] is not None:
            eps = re.findall('\d+\.\d+', item['eps'])
            if len(eps) > 0:
                eps = float(eps[0])
                if eps > 0:
                    num_of_eps_obtained = num_of_eps_obtained + 1
                    total_eps = total_eps + eps
    average = round(total_eps/num_of_eps_obtained, 2)

    stock_analysis['eps_growth_rate']['average'] = f'{average}%'

    with open(f"output_stock_analysis_{json_object['stock_symbol']}.json", "w") as write_file:
        json.dump(stock_analysis, write_file, indent=4)

# start this program
start()