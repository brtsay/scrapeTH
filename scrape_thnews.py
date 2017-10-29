#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Parsing Tsinghua news.

This module contains functions that parse the basic Tsinghua news
page that contains all its summaries as well as functions that will
parse the actual news article themselves. Most of these functions
are created from code used in Brian's guest lecture for Professor
Meng's class on November 29, 2016. 

Examples:
    This can be used to get article news.

        import scrape_thnews

        requests_results = scrape_thnews.basic_scrape()
        selenium_results = scrape_thnews.basic_scrape(use_selenium=True)

    This can be used to parse an article.

        from scrape_thnews import parse_th_article

        an_article_url = 'http://news.tsinghua.edu.cn/publish/thunews/9648/2016/20161125111440926399642/20161125111440926399642_.html'
        an_article_data = parse_th_article(an_article_url)

Todo:
    * Make the parse_th_article() function more robust to inconsistencies
"""
import csv
import re
import time
import requests
from lxml import html
from selenium import webdriver

def load_page(use_selenium=False):
    """
    Loads the Tsinghua news page into Python

    Args:
        use_selenium: Set to True to use selenium instead of requests
            for loading the web page.
    
    Returns:
        The html as parsed by lxml.

    Raises:
        ConnectionError: If requests can't load the URL at all.
        TimeoutError: If requests can connect with the server but
            can't get the data.
    """
    th_url = 'http://news.tsinghua.edu.cn/publish/thunews/9648/index.html'
    if use_selenium:
        driver = webdriver.Firefox()
        driver.get(th_url)
        th_html = html.fromstring(driver.page_source)
        driver.quit()
    else:
        # set timeout to 30s, after which requests should give up
        try:
            th_page = requests.get(th_url, timeout=30)
        except requests.exceptions.Timeout:
            print('Timeout error. Trying once more')
            th_page = requests.get(th_url, timeout=30)
        th_html = html.fromstring(th_page.content)

    return th_html

def get_views(use_selenium, pic_paths, th_html):
    """
    Retrives the number of views per news article

    Args:
        use_selenium: True if selenium was used to load the page

    Returns:
        A list with the number of views each article received.
    """
    # get the unique article IDs out of the article thumbnail paths
    if use_selenium:
        # get the nodes that define articles
        article_nodes = th_html.xpath('//li[@class="clearfix"]')
        # use these nodes as the root for selecting the number of views
        views = [article.xpath('.//font[contains(@id, "itemlist_total_")]//text()')
                 for article in article_nodes]
        # replace articles with no visible views with the word 'unknown'
        views = [int(view[0]) if view else 'unknown' for view in views]
    else:
        # get the unique article_ids
        article_ids = [re.search(r'/\d+?/(\d+)', pic_path).group(1) for pic_path in pic_paths]
        # define the URL that will be prepended to article IDs
        view_url_pre = 'http://news.tsinghua.edu.cn/application/visitor/article_list_visitors_2.jsp?articleID='
        # get the full URLs that will get the views
        view_urls = [view_url_pre+article_id for article_id in article_ids]
        views = []
        for view_url in view_urls:
            try:
                view_page = requests.get(view_url, timeout=30)
                # can get the views directly w/o first parsing with lxml
                views.append(view_page.text)
            except ConnectionError:
                print('Failed to find views for URL', view_url)
                views.append('unknown') # note this is not very robust
            # be an ethical scraper!
            # though in this case, the sleep time is probably not needed
            # your browser calls nearly every article view instantaneously
            time.sleep(1)

    return views

def write_csv(use_selenium=False, *args):
    """
    Writes out a .csv file containing the info scraped from the 
    Tsinghua news archives.

    Args:
        While the function accepts an arbitrary number of arguments,
        it expects lists of the same length that contain the article
        titles, URLs, summaries, dates, thumbnail URLs, and the 
        number of views.

    Returns:
        Nothing. The byproduct is writing out the .csv.
    """
    # get the current time for when the function is run and
    # create a list that has the same number of elements as there are number of articles
    # and make each element the current time
    current_time = [time.strftime("%Y-%m-%d %H:%M:%S")]*len(args[0])
    # add the source (selenium or requests) to the filename
    results = zip(*args, current_time)
    name_add = 'Selenium' if use_selenium else 'Requests'
    with open('thNews'+name_add+'.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['title', 'url', 'summary', 'date', 'pic', 'writetime'])
        writer.writerows(results)


def basic_scrape(use_selenium=False):
    """
    Scrapes the Tsinghua news page and writes it out as a .csv

    Args:
        use_selenium: set to True to use selenium instead of requests
            to load the Tsinghua news page. Defaults to False.

    Returns:
        A list that contains the article titles, article URLs, 
        summaries, publication dates, thumbnail pics, and views.
    """
    # get tsinghua news URL and parse
    th_html = load_page(use_selenium)

    # extract the article titles
    titles = th_html.xpath('//a[@class="jiequ"]/text()')

    # extract the article URLs (連接)
    # get the elements that contain the url for the newsitem
    url_paths = th_html.xpath('//a[@class="jiequ"]/@href')
    # urlPaths is a list of strings like this:
    # '/publish/thunews/9648/2016/20161122202918632829820/20161122202918632829820_.html'
    # turn each element of urlPaths into an actual url
    urls = ['http://news.tsinghua.edu.cn'+url for url in url_paths]

    if use_selenium:
        # extract the summaries for each article
        summaries = th_html.xpath('//div[@class="contentwraper"]/p/text()')
        # extract the day of the article e.g. the 25th
        days = th_html.xpath('//font[@class="dd"]/text()')
        # extract the year-month nodes of the article e.g. 2016.11
        ym_nodes = th_html.xpath('//font[@class="ym"]')
        # get the actual year-month
        yms = [ym_node.text_content() for ym_node in ym_nodes]
        # combine to get full date
        dates = [ym+'.'+day for ym, day in zip(yms, days)]
    else:
        # get the javascript summary call
        summaries_pre = th_html.xpath('//div[@class="contentwraper"]/p//text()')
        # summariesPre is a list of strings that look like this:
        # 'cutSummary("清华大学航天航空学院李群仰课题组与合作者于11月24日在《自然》在线发表题为“石墨烯摩擦接触界面的状态演化”...上来调控其摩擦性能。",180);'
        # use regex to extract the actual summaries
        summaries = [re.search('"(.*)"', summary).group(1) for summary in summaries_pre]
        # extract the dates that the article was published
        # get the javascript function that generates the date
        dates_pre = th_html.xpath('//font[@class="dd"]//text()')
        # use regex to extract the actual dates
        dates = [re.search('"(.*?)"', date).group(1) for date in dates_pre]


    # extract the thumbnail URLs associated with each article
    # get the end of the URL e.g.
    # /publish/thunews/9648/2016/20161125111440926399642/20161125111440926399642_.html
    pic_paths = th_html.xpath(
        '//li[@class="clearfix"]//img[contains(@src, "/publish/thunews")]/@src')
    # create full URL
    pics = ['http://news.tsinghua.edu.cn'+pic for pic in pic_paths]

    # get the number of views for each article
    # views = get_views(use_selenium, pic_paths, th_html)
    # news site appears to no longer display views

    write_csv(use_selenium, titles, urls, summaries, dates, pics)

    return([titles, urls, summaries, dates, pics])

def parse_th_article(url):
    """Takes a Tsinghua news article URL and gets the article info.
    
    Args:
        url: A string that indicates a Tsinghua news article for
           to extract info from.

    Returns:
        A dictionary where the keys are 
            'refLink': a list of links to other papers or None
            'images': a list of tuples with the image URL in the
                first element and description text in the second
            'editors': a list of strings with the names of editors
            'paperLink': a string that contains the original paper
                or None
            'articleText': a string that contains the article text
            'provider': a string that shows who provided the article
                or None
    """
    # load the article page
    article_page = requests.get(url)
    article_html = html.fromstring(article_page.content)

    # get the xpath that would get article-nodes
    article_node_xpath = '//article[@class="article"]'
    article_text = article_html.xpath(article_node_xpath+
                                      '//p[not(descendant::span)][not(contains(@style, "text-align") or contains(@style, "TEXT-ALIGN"))]//text()')
    # text-align gets the editors
    # the style is inconsistent, sometimes text-align is capitalized
    # span descendant is the paper links
    article_text = ' '.join(article_text)



    # some articles link to an original paper if the article is about a new paper
    # links to the actual paper are inconsistently located
    # multiple if statements used to find them
    # not robust, only tested on first few articles
    paper_link = article_html.xpath('//article[@class="article"]//p/span[text()="本文链接："]/following-sibling::a[1]/@href')
    if paper_link:
        paper_link = paper_link[0]
    else:
        paper_link = article_html.xpath(article_node_xpath +
                                        '//p[descendant::span[text()="论文链接："]]/following-sibling::p[1]/a/@href')
        if paper_link:
            paper_link = paper_link[0]
        else:
            paper_link = article_html.xpath(article_node_xpath+
                                            '//p[text()="论文链接："]/a/@href')
            if paper_link:
                paper_link = paper_link[0]
            else:
                paper_link = None

    ref_links = article_html.xpath(article_node_xpath+
                                   '//p[descendant::span[contains(text(), "参考文献链接：") or contains(text(), "相关论文链接：")]]/following-sibling::p/a[@href]/@href')
    if not ref_links:
        ref_links = None

    # get the text that contains news provider and editors
    editors_all = article_html.xpath(article_node_xpath+
                                     '//p[contains(@style, "text-align") or contains(@style, "TEXT-ALIGN")][contains(text(), "编辑")]/text()')
    assert len(editors_all) == 1
    # use regex to get only the editors
    editors = re.search('编辑：(.*)', editors_all[0]).group(1)
    # split into list so each element is an editor name
    editors = editors.split(' ')
    try:
        # get the news provider
        provider = re.search('供稿：(.*?)编辑：', editors_all[0]).group(1)
    except AttributeError:
        # not all articles have a news provider
        provider = None

    # get all the article images
    image_pre = article_html.xpath('//article[@class="article"]//img/@src')
    # combine to make full URL
    images = ['http://news.tsinghua.edu.cn/'+image for image in image_pre]
    # get all the image descriptors
    image_text_paths = article_html.xpath(article_node_xpath+
                                          '//p[descendant::img]/following-sibling::p[1]')
    image_texts = [imageTextPath.text_content() for imageTextPath in image_text_paths]
    assert len(images) == len(image_texts)

    result_dict = {}
    result_dict['articleText'] = article_text
    result_dict['paperLink'] = paper_link
    result_dict['refLink'] = ref_links
    result_dict['editors'] = editors
    result_dict['provider'] = provider
    result_dict['images'] = list(zip(images, image_texts))

    return result_dict
