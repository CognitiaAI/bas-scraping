import scrapy
from scrapy_selenium import SeleniumRequest
import pandas as pd
from pydispatch import dispatcher
from scrapy import signals


def convert_list_to_dict(lst):
    if len(lst) % 2 != 0:
        lst = lst[:-1]
    res_dct = {str.rstrip(str.strip(lst[i])): str.rstrip(str.strip(lst[i + 1])) for i in range(0, len(lst), 2)}
    return res_dct


class JavascriptRenderedSpider(scrapy.Spider):
    name = 'javascript_rendered'
    main_link = 'https://www.bastrucks.com/search?page=1'
    final_df = pd.read_excel('./links_extraction/YouTube.xlsx')
    final_df['HTML'] = ''
    for i in range(1, 21):
        final_df['Documents for this vehicle ' + str(i)] = ''
        final_df['Documents Link ' + str(i)] = ''
    final_df['Price'] = ''

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        self.final_df.to_excel('./BasTrucksFinalDocs.xlsx', index=False)

    def start_requests(self):
        yield SeleniumRequest(
            url=self.main_link, wait_time=10, screenshot=True, callback=self.parse_main_page)

    def parse_main_page(self, response):
        driver = response.request.meta['driver']
        for i in range(0, len(self.final_df)):
            link = self.final_df['URL'].iloc[i]
            if 'basworld' in link:
                link = link.replace('basworld', 'bastrucks')
                print("LINK: ", link)
                self.final_df['URL'].iloc[i] = link
            print("Documents progress -> ", i, " / ", len(self.final_df))
            check = True
            while check:
                try:
                    driver.get(link)
                    driver.implicitly_wait(2)
                    check = False
                except:
                    print("Loading exception occured: ", i, " ", link)
            href_elements = driver.find_elements_by_xpath("//div[@class='vehicle-document']/a")
            name_elements = driver.find_elements_by_xpath("//div[@class='vehicle-document']/a/span[@"
                                                          "class='vehicle-document-info']")
            for k in range(1, len(href_elements) + 1):
                document_link = href_elements[k - 1].get_attribute('href')
                doc_name = name_elements[k - 1].text
                self.final_df['Documents for this vehicle ' + str(k)].iloc[i] = doc_name
                self.final_df['Documents Link ' + str(k)].iloc[i] = document_link
            orig_price = ''
            try:
                orig_price = driver.find_element_by_xpath("//h2[@class='vdp-price bold']").text
                print("Setting ander waala: ", orig_price)
            except:
                price = driver.find_elements_by_xpath(
                    "//div[@class='sv__list__card sv__list__card_base js-similar-vehicle-card']/div/div[@class='priceinfo mainprice p-2']/h2")
                if len(price) > 0:
                    orig_price = price[0].text
                    print("Price: ", orig_price)
            self.final_df['Price'].iloc[i] = orig_price
            html = ''
            try:
                element = driver.find_element_by_xpath(
                    "//div[@class='sv__list__card sv__list__card_base js-similar-vehicle-card']")
                html = element.get_attribute('innerHTML')
            except:
                print("No HTML")
            self.final_df['HTML'].iloc[i] = html
        driver.close()
        self.final_df.to_excel('./BasTruckDocuments.xlsx', index=False)
