# objective: scrape top articles from webpage https://citizen.co.za 

from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import pandas as pd
from datetime import date

page = requests.get('https://citizen.co.za')

soup = BeautifulSoup(page.text, "html.parser")

title = []
links = []

# headline 
for link in soup.find_all('h1', {'class': re.compile('homelead1-headline')}):
    # link
    links.append(link.find('a').get('href'))
    # title
    title.append(link.get_text())

# 24 grid under multimeadia
for link in soup.find_all('a', {'class': re.compile('headline*')}):
    # link
    links.append(link.get('href'))
    # title
    title.append(link.get_text())

# 14 grid before multimedia
for link in soup.find_all('div', {'class': re.compile('headline') } ):
    #link
    links.append(link.findAll('a')[1].get('href'))
    #title
    title.append(link.findAll('a')[1].get_text())

# 5 editors choice
for link in soup.find_all('div', {'class':  re.compile('article-list') } ):
    for p in link.find_all('p'):
        #link
        links.append(p.findAll('a')[1].get('href'))
        #title
        title.append(p.findAll('a')[1].get_text())

# find category, date of article, author, excerpt, article, prem indicator
category = []
article_date = []
article_author = []
single_excerpt = []
article_body = []
premium = []

for link in links:
    page = requests.get(link)
    soup = BeautifulSoup(page.text, "html.parser")

    category.append(soup.find('span', {'class': re.compile('article-category*')}).text.rstrip('\n').lstrip('\n'))

    article_date.append(soup.find('span', {'class': re.compile('article-date*')}).text)
    
    try:
        article_author.append(soup.find('div', {'class': re.compile('article-byline')}).get_text().rstrip('\t').lstrip('\n\t'))
    except:
        article_author.append(np.nan)

    single_excerpt.append(soup.find('h2', {'class': re.compile('single-excerpt')}).text.replace('\t','').replace('\n',''))

    # check if the article is a premium version 
    # premium versions don't allow the full article
    if soup.find('div', {'id', 'fire-login'}):    
        premium.append(1)    
        article_body.append(np.nan)    
    else:    
        premium.append(0)    
        for body in soup.find_all('div', {'class': re.compile('single-content')}):    
            full_body = []    
            for p in body.find_all('p')[:-1]:    
                full_body.append(str(p).replace('<p>', '').replace('</p>', ''))

        article_body.append(' '.join(full_body))



# create final dataframe
data = pd.DataFrame(data = {'ArticleTitle':title, 'Link':links,'Category':category, 'Premium':premium,
                            'Excerpt':single_excerpt, 'ArticleDate':article_date, 
                            'ArticleAuthor':article_author, 'Article':article_body})

data['Date_Scraped'] = date.today().strftime('%Y-%m-%d')

data.to_excel('Data_output.xlsx', index=False)
