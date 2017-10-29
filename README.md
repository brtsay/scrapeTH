# Scraping Tsinghua News
This is the companion repo for a short guest lecture/workshop I did on web scraping for Professor MENG Tianguang's class at Tsinghua University. The goal was to get the students started on scraping information from web pages (Tsinghua University's news site in this case) using Python and the requests and lxml packages, with a focus on generating XPATH expressions. Some of the students were somewhat new to Python and perhaps programming languages in general, so I included a short bit on working in Python with the basics required to follow along with the workshop. The Jupyter notebooks were used to demonstrate basic Python usage and some basic web scraping techniques. The companion slides are found [here](http://pages.ucsd.edu/~brtsay/teaching/scrapeLecture.html). I walked through with students how to get article titles, URLs, summaries, dates, and associated images from the Tsinghua news site into a CSV file.

## Getting Started
The main parts of this repo are the Jupyter notebooks. 

### Prerequisites
- Python 3 (was not tested in Python 2)
- requests
- lxml
- selenium
- Firefox (hard-coded in but can be modified)
- Jupyter (for modifying the notebooks)

### Installing
After cloning the repo, you should be good to go.

## Usage
The main goal of this project was to get beginner students started on scraping using Tsinghua's news site as the example. Therefore, functionality is fairly limited to just getting the first page of articles from Tsinghua's news site.

First, import the module.
```python
import scrape_thnews
```
To use requests to get the page:
```python
requests_results = scrape_thnews.basic_scrape()
```
The alternative is to use selenium and Firefox to get the page
```python
selenium_results = scrape_thnews.basic_scrape(use_selenium=True)
```
Note that there was originally functionality to count the number of views each news item received. However, when I checked on October 29 2017, the views appear to be gone. An original page from Fall 2016 is included in the repo as thNews.html.

There is also a function to parse a news article itself, given its URL. 
```python
from scrape_thnews import parse_th_article

an_article_url = 'http://news.tsinghua.edu.cn/publish/thunews/9648/2016/20161125111440926399642/20161125111440926399642_.html'
an_article_data = parse_th_article(an_article_url)
```
Ostensibly, it will find the full article text, links to any papers and other materials referenced in the news (the news site generally announces research produced by its faculty), the editors of the news item, the news "provider" (generally what department the finding is from), and images inside the article. I did not test this function rigorously, so there is no guarantee that this function will be able to parse every Tsinghua news article. 
