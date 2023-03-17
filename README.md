# remotify-test
If you want to run it on your local machine, follow these setup to succesfully run the scraper.

## Installation guide

### Install virtualenv if not installed on your machine
For Windows
```
py -m pip install --user virtualenv
```
For Linux
```
pip3 install virtualenv
```

### Create your virtual environment first
For Windows
```
py -m venv venv
```
For Linux
```
python3 -m venv venv
```

### Activate your venv
For Windows
```
source venv/Scripts/activate
```
For Linux
```
source venv/bin/activate
```

### Install necessary scraper requirements
For Windows and Linux
```
pip install -r requirements.txt
```

# Running the scrapers

## 1. Able to create a complete scraping bot and; 2. Able to Send concurrent requests
***NOTE: Make sure that your own Mozilla Firefox web browser is installed.***
```
cd py_scrapy_selenium
scrapy crawl scraping -O ScrapingSpider_`date +\%Y\%m\%d_\%H\%M\%S`.json
```
Also make sure that you put your own firfox binary location. Set it up on scrapy.py under py_scraping_selenium folder on line 22.

### If you want an .xlsx output:
Go to settings.py and uncomment this line. Make sure to uncomment it out after using it so that the settings won't get messed up
```
## For xlsx output 
FEED_EXPORTERS = {
    'xlsx': 'scrapy_xlsx.XlsxItemExporter',
}
```
And the run this line of code
```
scrapy crawl scraping -O ScrapingSpider_`date +\%Y\%m\%d_\%H\%M\%S`.xlsx
```


## 3. Able to collect all data without Selenium
This is only possible for Linux OS to run scrapy-playwright solution for scraping the data **WITHOUT SELENIUM**.
In [the link to the Python docs that you posted](https://docs.python.org/3/library/asyncio-platforms.html#asyncio-windows-subprocess), it says that
> On Windows, the default event loop ProactorEventLoop supports subprocesses, whereas SelectorEventLoop does not.

### Install necessary packages such as Playwright
```
playwright install
```
### If you want to run the crawler to produce your own output. Make sure you are in the scrapy_playwright_linux folder
```
cd scrapy_playwright_linux
scrapy crawl scraping -O ScrapingSpider_`date +\%Y\%m\%d_\%H\%M\%S`.json
```
### If you want an .xlsx output:
Go to settings.py and uncomment this line. Make sure to uncomment it out after using it so that the settings won't get messed up
```
## For xlsx output 
FEED_EXPORTERS = {
    'xlsx': 'scrapy_xlsx.XlsxItemExporter',
}
```
And the run this line of code
```
scrapy crawl scraping -O ScrapingSpider_`date +\%Y\%m\%d_\%H\%M\%S`.xlsx
```