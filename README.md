# bas-scraping
A web scraper for bastrucks.com which extracts all the relevant information.

# Implementation Details
This channel i.e. https://www.youtube.com/c/BASWorld/videos has more than 30K videos. We needed to extract the links from the description of each video and collect all the data from the original website i.e. www.bastrucks.com and provide it in excel format.

# How to run the scraper
1. Clone the repo.
2. Run yt_links_extractor.py. It will generate an excel file named YouTube.xlsx having all the relevant columns being scraped from YouTube. Just need to add google api_key on line number 68.
3. Run the command scrapy crawl javascript_rendered to generate an excel file named BasTrucksFinalDocs.xlsx which will be having the documents links.
4. Run the command python make_client_relevant_file.py to generate the excel file whose format will be same as to the required file.
5. Run scrapy crawl bastrucks which will scrape whole website to generate an excel file having all the relevant data being populated.
6. Run scrapy crawl docdownloader to download all the documents.
7. Run scrapy crawl imagedownloader to download all the images.
