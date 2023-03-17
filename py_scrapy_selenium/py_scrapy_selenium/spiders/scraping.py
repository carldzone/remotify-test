import os
import re
import time
import scrapy
import datetime
from py_scrapy_selenium.items import PyScrapySeleniumItem
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox


class ScrapingSpider(scrapy.Spider):
    name = "scraping"
    
    def start_requests(self):
        driver_path = os.getcwd() + '\geckodriver\geckodriver.exe'
        options = Options()
        # windows
        options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
        # linux
        # options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
        # or put your own binary location
        # options.binary_location = r''

        options.headless = True
        driver = Firefox(options=options, executable_path=driver_path)
        driver.get('https://rewardsforjustice.net/index/?jsf=jet-engine:rewards-grid&tax=crime-category:1070%2C1071%2C1073%2C1072%2C1074')
        time.sleep(15)

        wanted_items = driver.find_elements_by_xpath("//*[contains(@class,'jet-listing-grid__item jet-listing-dynamic-post')]")
        for item in wanted_items:
            items = PyScrapySeleniumItem()

            page_url = item.find_element_by_tag_name('a').get_attribute('href')
            h2_tags = item.find_elements_by_tag_name('h2')
            category = h2_tags[0].text
            title = h2_tags[1].text
            items['page_url'] = page_url
            items['category'] = category
            items['title'] = title
            yield scrapy.Request(url=page_url, meta=dict(scraped_items=items),)
        
        driver.quit()
    

    def parse(self, response):
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