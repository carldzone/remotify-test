import scrapy
from scrapy_playwright.page import PageMethod
from scrapy_playwright_linux.items import ScrapyPlaywrightLinuxItem
import regex as re
import datetime


class ScrapingSpider(scrapy.Spider):
    
    name = "scraping"
    
    def start_requests(self):
        yield scrapy.Request('https://rewardsforjustice.net/index/?jsf=jet-engine:rewards-grid&tax=crime-category:1070%2C1071%2C1073%2C1072%2C1074', 
                             meta=dict(
                                 playwright = True,
                                 playwright_include_page = True,
                                 playwright_page_methods = [
                                     PageMethod('waitForLoadState', 'div.elementor:nth-child(12)'),
                                     PageMethod('evaluate', "window.scrollBy(0, document.body.scrollHeight)"),
                                     PageMethod('wait_for_selector', 'div.jet-filters-pagination__item:nth-child(1)'),
                                     ],
                                 errback = self.errback
                             )
                             )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()
        
        reward_items = response.xpath("//*[contains(@class,'jet-listing-grid__item jet-listing-dynamic-post')]")
        for item in reward_items:
            items = ScrapyPlaywrightLinuxItem()
            page_url = item.css('div:nth-child(2) > a:nth-child(2)::attr(href)').get()
            items['page_url'] = page_url
            items['category'] = item.css('h2::text').get()
            items['title'] = item.css('div:nth-child(2) > div:nth-child(1) > section:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > section:nth-child(3) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > h2:nth-child(1)::text').get()
            yield scrapy.Request(
                page_url,
                meta=dict(
                    scraped_items = items,
                    playwright = True,
                    playwright_include_page = True,
                    playwright_page_methods = [
                        PageMethod('wait_for_selector', '#reward-fields'),
                    ],
                ),
                errback = self.errback,
                callback=self.parse_request,
            )

    async def parse_request(self, response):
        page = response.meta["playwright_page"]
        await page.close()
        
        items = response.meta.get('scraped_items')
        
        items['reward_amount'] = response.css('.elementor-element-5e60756 > div:nth-child(1) > h2:nth-child(1)::text').get().split('Up to')[-1].strip()
        org = response.css('div.elementor-element:nth-child(20) > div:nth-child(1)::text').get()
        if org is not None:
            assoc_org = str(org).replace('\t', '').replace('\n', '')
        else:
            assoc_org = None
        items['associated_organizations'] = assoc_org
        items['associated_locations'] = response.css('.elementor-element-0fa6be9 > div:nth-child(1) > div:nth-child(1) > span:nth-child(1)::text').get()
        about = ''
        about_text = response.css('.elementor-element-52b1d20 > div:nth-child(1) > p::text').getall()
        for p in about_text:
            about = about + ' ' + p
        items['about'] = about
        items['image_urls'] = response.css('#gallery-1 > figure:nth-child(1) > div:nth-child(1) > a::attr(href)').getall()
        date_of_birth = response.css('div.elementor-element:nth-child(10) > div:nth-child(1)::text').get()
        date_of_birth_clean = str(date_of_birth).replace('\t', '').replace('\n', '').strip()
        year_pattern = re.findall(r'\d{4}', date_of_birth_clean)
        try:
            if date_of_birth_clean == "None":
                iso_date_of_birth = None
            else:
                iso_date_of_birth = datetime.datetime.strptime(date_of_birth_clean, "%B %d, %Y").isoformat()
        except ValueError:
            try:
                iso_date_of_birth = datetime.datetime.strptime(year_pattern[0], '%Y').isoformat()
            except IndexError:
                iso_date_of_birth = None
            
        items['date_of_birth'] = iso_date_of_birth
        
        yield items

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()