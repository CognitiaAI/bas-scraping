import scrapy
import pandas as pd
import numpy as np
from pydispatch import dispatcher
from scrapy import signals
import unidecode
import re
from bs4 import BeautifulSoup
import json
from utils.spec_table_to_json import get_extra_spec, get_section_data_spec, get_about_section_spec


def convert_list_to_dict(lst):
    if len(lst) % 2 != 0:
        lst = lst[:-1]
    res_dct = {str.rstrip(str.strip(lst[i])): str.rstrip(str.strip(lst[i + 1])) for i in range(0, len(lst), 2)}
    return res_dct


class BastrucksSpider(scrapy.Spider):
    name = 'bastrucks'
    page_number = 1
    main_link = 'https://www.bastrucks.com/search?page='
    links_df = pd.read_excel('./BAS_FINAL_SCRAPE_SAMPLE.xlsx')
    links_df['Machine Location'] = 'Veghel, Netherlands'
    links_df['Dealer Type'] = 'Dealer / Distributor'
    links_df['Member Since'] = 'Reliable | More than 14 years with Aggrio'
    links_df['Dealer Name'] = 'BAS World'
    links_df['Dealer Country'] = 'Netherlands'
    links_df['Dealer Logo'] = 'bas-world-logo.jpg'
    links_df['Contact'] = 'Paul van Loon'
    links_df['Mobile No.'] = '+316XX XXXXX'
    links_df['Contact Email'] = 'paul.bas@aggriomachinery.com'
    links_df['Contact Language'] = 'Dutch, English, German'
    links_df['Specification HTML 1'] = ''
    links_df['Specification HTML 2'] = ''
    links_df['Loading HTML'] = ''
    links_df['Receive Discount'] = ''
    links_df['Loading capacity'] = ''
    links_df['Total weight'] = ''
    links_df['Superstructure'] = ''
    links_df['Number of seats'] = ''
    links_df['Length Dimension'] = ''
    links_df['Breadth Dimension'] = ''
    links_df['Wheelbase Dimension'] = ''
    links_df['Height Dimension'] = ''
    links_df['Inner URL'] = ''
    links_df['Specs HTML'] = ''
    all_columns = list(links_df.columns)
    ref_counter = 0
    pre_url = 'https://www.bastrucks.com/'
    all_spec_headings = ['About this vehicle', 'General specifications', 'Technical specifications',
                         'Vehicle Dimensions', 'Crane', 'Boom and stick', 'Undercarriage', 'Blade',
                         'Equipment', 'Drum Brakes', 'Trailer', 'Axles and tyres', 'Axles and tyres of trailer',
                         'Superstructure specifications', 'Extras']

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        print("Spider closing: ", self.counter)
        BastrucksSpider.links_df.to_excel('./BasTrucks_Sample.xlsx', index=False)

    def start_requests(self):
        yield scrapy.Request(url='https://www.google.com/', callback=self.parse_main_page,
                             dont_filter=True)

    def parse_main_page(self, response):
        total_length = len(BastrucksSpider.links_df)
        for i in range(0, total_length):
            link = BastrucksSpider.links_df['URL'].iloc[i]
            yield scrapy.Request(url=link, callback=self.parse_attrs,
                                 headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                                                        ' (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'
                                          }, dont_filter=True, meta={'url': link, 'index': i})

    def get_string_from_xpath(self, response, xpath):
        title = response.xpath(xpath).extract_first()
        if title is not None:
            return re.sub(' +', ' ', (str.strip(str.rstrip(title)).replace('\n', ' ')))
        return ''

    def get_specs_json(self, response):
        specifications_html = response.xpath("//div[@class='col-8 ml-0 pl-0']").extract_first()
        final_dictionary = []
        if specifications_html is not None:
            spec_soup = BeautifulSoup(specifications_html, 'lxml')
            all_sections = spec_soup.find_all('h2')
            sections_text = []
            for section in all_sections:
                section_text = re.sub(' +', ' ', str.strip(section.text).replace('\n', ' '))
                sections_text.append(section_text)
            for heading in self.all_spec_headings:
                if heading in sections_text:
                    if heading == 'About this vehicle':
                        final_dictionary.append(
                            get_about_section_spec(spec_soup, "vehicle-detail-accordion", "About this vehicle"))
                    elif heading == 'General specifications':
                        final_dictionary.append(
                            get_section_data_spec(spec_soup, "General specifications", id_="generalSpecAccordion"))
                    elif heading == 'Technical specifications':
                        final_dictionary.append(
                            get_section_data_spec(spec_soup, "Technical specifications", id_="techSpecAccordion"))
                    elif heading == 'Vehicle Dimensions':
                        final_dictionary.append(
                            get_section_data_spec(spec_soup, "Vehicle dimensions", id_="dimensionSpecAccordion"))
                    elif heading == 'Crane':
                        final_dictionary.append(get_section_data_spec(spec_soup, "Crane", id_="craneSpecAccordion"))
                    elif heading == 'Boom and stick':
                        final_dictionary.append(
                            get_section_data_spec(spec_soup, "Boom and stick", id_="combiSpecAccordion"))
                    elif heading == 'Undercarriage':
                        final_dictionary.append(
                            get_section_data_spec(spec_soup, "Undercarriage", id_="undercarriageAccordion"))
                    elif heading == 'Blade':
                        final_dictionary.append(get_section_data_spec(spec_soup, "Blade", id_="bladeAccordion"))
                    elif heading == 'Equipment':
                        final_dictionary.append(
                            get_section_data_spec(spec_soup, "Equipment", id_="equipmentAccordion"))
                    elif heading == 'Drum Brakes':
                        final_dictionary.append(
                            get_section_data_spec(spec_soup, "Drum Brakes", id_="drumAccordion"))
                    elif heading == 'Trailer':
                        final_dictionary.append(
                            get_section_data_spec(spec_soup, "Trailer", id_="combiSpecAccordion"))
                    elif heading == 'Axles and tyres':
                        final_dictionary.append(
                            get_section_data_spec(spec_soup, "Axles and tyres", id_="axlesSpecAccordion"))
                    elif heading == 'Axles and tyres of trailer':
                        final_dictionary.append(get_section_data_spec(spec_soup, "Axles and tyres of trailer",
                                                                      id_="combiAxlesSpecAccordion"))
                    elif heading == 'Superstructure specifications':
                        final_dictionary.append(get_section_data_spec(spec_soup, "Superstructure specifications",
                                                                      id_="superstructureSpecAccordion"))
                    elif heading == 'Extras':
                        final_dictionary.append(get_extra_spec(spec_soup, "extras", "extraSpecAccordion"))
                    else:
                        print("Heading: ", heading)
        return json.dumps(final_dictionary)

    def parse_attrs(self, response):
        index = response.meta['index']
        self.links_df['Title'].iloc[index] = self.get_string_from_xpath(response,
                                                                        "//h1[@class='float-left vehicle-title bold']/text()")
        self.links_df['Sub title'].iloc[index] = self.get_string_from_xpath(response,
                                                                            "//h4[@class='grey vehicle-sub-title']/text()")

        specifications = response.xpath("//div[@id='generalSpecAccordion']/div/div/div/text()").extract()
        specs_dictionary = convert_list_to_dict(specifications)
        specs_mapping = {'Serial number': 'Serial', 'Brand': 'Make', 'Type': 'Model', 'Production date': 'Year',
                         'Total weight': 'Weight', 'Hours': 'Engine Hours', 'Mileage (km)': 'Mileage',
                         'Type extended': 'Type extended',
                         'Reference nr': 'Reference nr'}

        for key in list(specs_dictionary.keys()):
            if key in list(specs_mapping.keys()):
                self.links_df[specs_mapping[key]].iloc[index] = re.sub(' +', ' ',
                                                                       (specs_dictionary[key].replace('\n', ' ')))
            else:
                if key not in list(self.links_df.columns):
                    self.links_df[key] = ''
                self.links_df[key].iloc[index] = re.sub(' +', ' ', (specs_dictionary[key].replace('\n', ' ')))

        specs_html = response.xpath("//div[@class='col-8 ml-0 pl-0']").extract_first()
        if specs_html is not None:
            half_length = int(len(specs_html) / 2)
            self.links_df['Specification HTML 1'].iloc[index] = specs_html[:half_length]
            self.links_df['Specification HTML 2'].iloc[index] = specs_html[half_length:]
            self.links_df['Specification JSON'].iloc[index] = self.get_specs_json(response)
        specs_html = response.xpath("//ul[@class='vehicle-attribute-block']").extract_first()
        if specs_html is not None:
            self.links_df['Specs HTML'].iloc[index] = specs_html
            if self.links_df['1st Registration spec'].iloc[index] is np.nan or \
                    self.links_df['1st Registration spec'].iloc[index] == '':
                try:
                    spec_soup = BeautifulSoup(specs_html, 'lxml')
                    rows = spec_soup.find_all('li')
                    year_ = ''
                    if len(rows) > 0:
                        year_ = str(rows[0].text)
                        year_ = re.sub(' +', ' ', (year_.replace('\n', ' ')))
                        self.links_df['1st Registration spec'].iloc[index] = str.rstrip(str.strip(year_))
                except:
                    print(" ====== Index : ", index, " URL: ", self.links_df['URL'].iloc[index])
        else:
            self.links_df['Specs HTML'].iloc[index] = ''
        tech_specs = response.xpath("//div[@id='techSpecAccordion']/div/div/div/text()").extract()
        tech_dict = convert_list_to_dict(tech_specs)

        engine_attr = 'Engine'

        interested_attr = 'Engine power'
        if interested_attr in tech_dict:
            value = tech_dict[interested_attr]
        elif engine_attr in tech_dict:
            value = tech_dict[engine_attr]
        else:
            value = ''
        self.links_df['Max HP'].iloc[index] = re.sub(' +', ' ', (value.replace('\n', ' ')))
        tech_keys = ['Chassis height', 'Gearbox', 'Towing capacity (kg.)', 'Driven wheels', 'Fifth wheel height']
        for key in tech_keys:
            if key in list(tech_dict.keys()):
                if key not in list(self.links_df.columns):
                    self.links_df[key] = ''
                self.links_df[key].iloc[index] = re.sub(' +', ' ', (tech_dict[key].replace('\n', ' ')))
        loading_html = response.xpath(
            '//div[@class="light-grey-bas-bg padding5 mbottom float-left row"]').extract_first()
        if loading_html is not None:
            self.links_df['Loading HTML'].iloc[index] = loading_html
        receive_discounts = response.xpath("//h4[@class='text-center colorGreen']/text()").extract()
        if len(receive_discounts) > 0:
            receive_dis = str.rstrip(str.strip(receive_discounts[-1]))
            i = 0
            while len(receive_dis) < 3 and i < len(receive_discounts):
                receive_dis = str.rstrip(str.strip(receive_discounts[i]))
                i += 1
        else:
            receive_dis = ''

        self.links_df['Receive Discount'].iloc[index] = receive_dis

        axle_specs = response.xpath("//div[@id='axlesSpecAccordion']/div/div/div/text()").extract()
        axle_dict = convert_list_to_dict(axle_specs)
        if 'Loading capacity' in list(axle_dict.keys()):
            self.links_df['Loading capacity'].iloc[index] = re.sub(' +', ' ', (
                str.rstrip(str.strip(axle_dict['Loading capacity'])).replace('\n', ' ')))
        if 'Total weight' in list(axle_dict.keys()):
            self.links_df['Total weight'].iloc[index] = re.sub(' +', ' ', (
                str.rstrip(str.strip(axle_dict['Total weight'])).replace('\n', ' ')))

        sup_specs = response.xpath("//div[@id='superstructureSpecAccordion']/div/div/div/text()").extract()
        sup_dict = convert_list_to_dict(sup_specs)
        if 'Superstructure' in list(sup_dict.keys()):
            self.links_df['Superstructure'].iloc[index] = sup_dict['Superstructure']
        if 'Number of seats' in list(sup_dict.keys()):
            self.links_df['Number of seats'].iloc[index] = sup_dict['Number of seats']

        self.parse_dimensions(response, index)

        description = response.xpath("//div[@id='aboutVehicleAccordion']/text()").extract_first()
        if description is not None:
            self.links_df['Description'].iloc[index] = str.strip(str.rstrip(description))
        video_links = response.xpath(
            "//div[@class='gallery-img photoswipe-wrapper']/div/span/@data-iframe-src").extract()
        for video in video_links:
            if 'youtube' in video:
                key = 'YouTube'
            else:
                key = '3D'
            self.links_df[key].iloc[index] = video

        self.links_df['Inner URL'].iloc[index] = response.request.url

        ref = self.links_df['Reference nr'].iloc[index]
        if ref == '':
            BastrucksSpider.ref_counter += 1
            ref = 'no-reference_nr-' + str(BastrucksSpider.ref_counter)

        title = self.links_df['Title'].iloc[index]

        pre_image = str(title) + '-' + str(ref)
        pre_image = unidecode.unidecode(pre_image)
        pre_image = pre_image.replace(' ', '-').replace(',', '-').replace('.', '-').replace('/', '-')
        pre_image = pre_image.replace('?', '-').replace('\\', '-').replace(':', '-').replace('*', '-')
        pre_image = pre_image.replace('<', '-').replace('>', '-').replace('|', '-').replace('\n', '-')
        for k in range(0, 50):
            pre_image = pre_image.replace('--', '-')
        if pre_image[0] == '-':
            pre_image = pre_image[1:]
        images_links = response.xpath("//div[@class='gallery-img photoswipe-wrapper']/div/a/@href").extract()
        all_columns = list(self.links_df.columns)
        for k in range(0, len(images_links)):
            file_name = pre_image + '-' + str(k + 1) + '.jpg'
            if 'Image ' + str(k + 1) not in all_columns:
                self.links_df['Image ' + str(k + 1)] = ''
            if 'Image Link ' + str(k + 1) not in all_columns:
                self.links_df['Image Link ' + str(k + 1)] = ''
            self.links_df['Image ' + str(k + 1)].iloc[index] = file_name
            self.links_df['Image Link ' + str(k + 1)].iloc[index] = images_links[k]

    def parse_dimensions(self, response, index):
        length = response.xpath("//div[@class='vans-design']/div[@class='length dimensions']/text()").extract_first()
        if length is not None:
            self.links_df['Length Dimension'].iloc[index] = str.rstrip(str.strip(length))
        breadth = response.xpath("//div[@class='vans-design']/div[@class='breadth dimensions']/text()").extract_first()
        if breadth is not None:
            self.links_df['Breadth Dimension'].iloc[index] = str.rstrip(str.strip(breadth))
        wheelbase = response.xpath(
            "//div[@class='vans-design']/div[@class='wheelbase dimensions']/text()").extract_first()
        if wheelbase is not None:
            self.links_df['Wheelbase Dimension'].iloc[index] = str.rstrip(str.strip(wheelbase))
        height = response.xpath(
            "//div[@class='vans-design']/div[@class='height dimensions']/div/text()").extract_first()
        if height is None:
            height = response.xpath(
                "//div[@class='vans-design']/div[@class='height dimensions']/text()").extract_first()
        if height is not None:
            height = str.rstrip(str.strip(height))
        else:
            height = ''
        self.links_df['Height Dimension'].iloc[index] = height
