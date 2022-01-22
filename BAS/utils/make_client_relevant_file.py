import numpy as np
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

if __name__ == '__main__':
    df = pd.read_excel('./Docs_sample.xlsx')
    price_array = df['Price'].str.split('€')
    indices_to_take = []

    for index, price in enumerate(price_array):
        if price is not np.nan and len(price) > 1:
            if int(price[1].replace(',', '')) >= 10000:
                indices_to_take.append(index)

    scrape_df = df.iloc[indices_to_take].reset_index(drop=True)
    if scrape_df['Documents for this vehicle 14'].isnull().all():
        for i in range(15, 21):
            del scrape_df['Documents Link ' + str(i)]
            del scrape_df['Documents for this vehicle ' + str(i)]

    sample_df = pd.read_excel('./Sample_Client.xlsx')
    columns = list(sample_df.columns)
    sample_df['URL'] = scrape_df['URL']
    for i in range(1, 15):
        sample_df['Documents for this vehicle ' + str(i)] = scrape_df['Documents for this vehicle ' + str(i)]
        sample_df['Documents Link ' + str(i)] = scrape_df['Documents Link ' + str(i)]
    sample_df['RRP'] = scrape_df['Price']
    sample_df['HTML'] = scrape_df['HTML']
    sample_df['YouTube Publication'] = scrape_df['Published At']
    sample_df['Type extended'] = ''
    regs = []

    for i in range(0, len(sample_df)):
        html = sample_df['HTML'].iloc[i]
        reg = ''
        if html is not np.nan:
            spec_soup = BeautifulSoup(html, 'lxml')
            main_div = spec_soup.find('div', {'class': 'sv__card__attribs mt-2'})
            all_divs = main_div.find_all('div')
            for div in all_divs:
                check = div.find_all('span',
                                     {'class': 'vehicle-list-icon border-none align-middle icon-1st-registration'})
                if len(check) > 0:
                    reg_html = spec_soup.find('span', {'class': 'vehicle-list-text float-none'})
                    reg = str.strip(reg_html.text)
        regs.append(reg)
    sample_df['1st Registration spec'] = regs
    sample_df.drop_duplicates().reset_index(drop=True, inplace=True)
    sample_df.to_excel('./BAS_FINAL_SCRAPE_SAMPLE.xlsx', index=False)
