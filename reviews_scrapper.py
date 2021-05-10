#!/usr/bin/env python
# coding: utf-8

# In[35]:


#################################
###          IMPORTS          ###
#################################

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import sys
import time
import os
import logging
import re
import pandas as pd
import pause
import random

# pandas.set_option('display.max_columns', 200)
sys.path.append('./utils/')
import MyUtilities


# In[71]:


input_path = MyUtilities.getCurrentDirectory() + '/data/serp_neutral.xlsx'
driver_path = MyUtilities.getCurrentDirectory() + '/tools/geckodriver'
reviews_path = MyUtilities.getCurrentDirectory() + '/data/serp_neutral_reviews.xlsx'
removed_items_path = MyUtilities.getCurrentDirectory() + '/data/serp_neutral_removed.xlsx'

default_timeout = '30'
start = 0
end = 1000


# In[51]:


def get_items_list(input_path):
    rows = pd.read_excel(input_path)
    items = []
    for i, row in rows.iterrows():
        items.append( str(row['asin']) )
        
    return items

def is_deleted(soup):
    deleted = False
    messege = 'Page Not Found'
    element = soup.find("title")
    if element is not None:
        if messege in element.text.strip():
            deleted = True
    return deleted

def get_driver():
    print('creating driver')
    # Using Firefox
    browserOptions = webdriver.FirefoxOptions()
    browserOptions.add_argument('--headless')
    driver = webdriver.Firefox(options = browserOptions, executable_path=driver_path)
    driver.maximize_window()
    return driver

def get_reviews_url(asin):
    return 'https://www.amazon.com/product-reviews/' + asin + '/'

def scrape_reviews(items):
    driver = get_driver()
    reviews_df = pd.DataFrame(columns=['asin', 'review_id', 'review_title', 'review_text', 'review_date', 'review_rating', 'review_verified', 'review_helpful', 'review_class'])
    removed_df = pd.DataFrame(columns=['asin'])
    
    count = 0
    removed_count = 0
    items_count = 0
#     next_btn_xpath = '//*[@id="cm_cr-pagination_bar"]/ul/li[2]/a'
    next_btn_xpath = '//*[@class="a-last"]'
    
#     print(f'From {start} to {end}')
    
    for asin in items:
        if items_count < start:
            items_count += 1
            continue
        if items_count > end:
            break;
        print()
        print("Item no. " + str(items_count) )
        print('Processing item ' + asin)
        reviews_url = get_reviews_url(asin)
        
        page_loaded = False
        while not page_loaded:
            try:
                driver.get(reviews_url)
                page_loaded = True
                time.sleep(random.randint(1,3))
            except TimeoutException:
                wait_time = random.randint(300, 600)
                print('TimeoutException at ' + str(i) + ', waiting for ' + str(wait_time) + ' seconds')
                time.sleep(wait_time)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        reviews = soup.findAll("div", {"data-hook" : 'review'})
        more_reviews = True
        reviews_count = 0
        
        if is_deleted(soup):
            removed_df.loc[removed_count] = [str(asin)]
            removed_count += 1
            items_count += 1
            continue
        else:
            while more_reviews:
                if reviews != None:
                    for review in reviews:
                        reviews_count += 1

                        review_id = ''
                        review_title = ''
                        review_text = ''
                        review_date = ''
                        review_rating = ''
                        review_verified = 0
                        review_helpful = 0
                        review_class = -1

                        review_id = str(review['id']).strip()
                        if review.find("a", {"data-hook" : "review-title"}) is not None:
                            review_title = review.find("a", {"data-hook" : "review-title"}).text.strip()
                        else:
                            review_title = review.find("span", {"data-hook" : "review-title"}).text.strip()
                        review_text = review.find("span", {"data-hook" : "review-body"}).text.strip()

                        review_date = review.find("span", {"data-hook" : "review-date"}).text.strip()
                        date_index = review_date.rfind('on') + 2
                        review_date = review_date[date_index:].strip()

                        review_rating = review.find("span", {"class" : "a-icon-alt"}).text.strip()
                        review_rating = int(review_rating[0])

                        if "Verified Purchase" in review.text:
                            review_verified = True
                        else:
                            review_verified = False

                        helpful = review.find("span", {"data-hook" : "helpful-vote-statement"})
                        if helpful is not None:
                            review_helpful = helpful.text.strip()
                            if review_helpful.startswith('One person found'):
                                review_helpful = 1
                            else:
                                review_helpful = int(review_helpful[0: review_helpful.find('people')].replace(',', '').strip())
                        else:
                            review_helpful = 0

                        # positive review
                        if review_rating >= 4:
                            review_class = 1
                        else: # critical review
                            review_class = -1

                        reviews_df.loc[count] = [str(asin), str(review_id), review_title, review_text, review_date, review_rating, review_verified, review_helpful, review_class]
                        count += 1

                try:
                    next_btn = driver.find_element_by_xpath(next_btn_xpath)
                    next_btn.click()
                    time.sleep(random.randint(1, 3))
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'lxml')
                    reviews = soup.findAll("div", {"data-hook" : 'review'})
                except Exception:
                    print('No. of reviews = ' + str(reviews_count))
                    more_reviews = False
        items_count += 1
    print('closing driver')
    driver.quit()
    return reviews_df, removed_df

def append_to_excel(path, df):
    if os.path.exists(path):
        old_df = pd.read_excel(path)
    else:
        old_df = pd.DataFrame()
    new_df = pd.concat([old_df, df])
    new_df.to_excel(path, index=False)
    return
    
# items = get_items_list(input_path)
# reviews_df, removed_df = scrape_reviews(items)
# reviews_df.to_excel(reviews_path, index=False)
# removed_df.to_excel(removed_items_path, index=False)


# In[ ]:


def main():
    args = sys.argv
    if len(args) < 3:
        print('You need to pass two arguments: start-index and end-index')
        return
    
    global start
    print(args)
    start = int(args[1])
    global end
    end = int(args[2])
    
    items = get_items_list(input_path)
    reviews_df, removed_df = scrape_reviews(items)
    
    reviews_df = append_to_excel(reviews_path, reviews_df)
    removed_df = append_to_excel(removed_items_path, removed_df)
#     reviews_df.to_excel(reviews_path, index=False)
#     removed_df.to_excel(removed_items_path, index=False)
    
main()


# In[59]:


# serp = pd.read_excel(MyUtilities.getCurrentDirectory() + '/data/serp_results_without_ads_withDetails_annotated.xlsx')
# recomm = pd.read_excel(MyUtilities.getCurrentDirectory() + '/data/homepage_recommendations_withDetails_annotated.xlsx')

# # get intersection between serp and recommendations
# commons = pd.merge(recomm, serp, how ='inner', on =['asin'])
# print(commons['asin'])
# print(serp.shape)

# # get items in serp only and not in recommendations
# serp_only = serp[ ~ serp['asin'].isin(commons['asin'].tolist()) ]
# print(serp_only.shape)

# # save items in serp_only
# serp_only.to_excel(MyUtilities.getCurrentDirectory() + '/data/serp_only.xlsx', index=False)


# In[69]:





# In[ ]:




