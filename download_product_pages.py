#################################
###          IMPORTS          ###
#################################

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import sys
import time
import os
from contextlib import contextmanager
import logging
import pandas as pd

from pathlib import Path
import re
from datetime import datetime
import pause

#import MyUtilities
sys.path.append('../utils/')
import MyUtilities


driver_path = MyUtilities.getParentDirectory() + '/tools/geckodriver'
products_list_path = MyUtilities.getParentDirectory() + '/results/search_2020_01_21/top50_serp_results_unique.xlsx'
results_path = MyUtilities.getParentDirectory() + '/data/pages/products/'

scrolldown_count = 1
scrolldown_results_waiting_time = 10

start = 0
end = 1000

def get_driver():
    browserOptions = webdriver.FirefoxOptions()
    browserOptions.add_argument("--incognito")
    browserOptions.add_argument('--headless')

    #start the web driver
    driver = webdriver.Firefox(options = browserOptions, executable_path=driver_path)
    driver.maximize_window()
    return driver

def download_products_pages(pages_list_path, page_path):
    driver = get_driver()
    
    products = pd.read_excel(pages_list_path)
    for i, row in products.iterrows():
        if i < start:# or i > end:
            continue
        if i > end:
            break;
        asin = str(row['asin'])
        url = row['product_url']
        driver.get(url)
        # scroll down to end of page to get more results
        for i in range(0,scrolldown_count):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(scrolldown_results_waiting_time)
        
        product_page_path = page_path + asin + '.html'
        html = driver.page_source
        file = open(product_page_path,"w+")
        file.write(html)
        file.close()
        
    driver.close()
    return

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
    
    download_products_pages(products_list_path, results_path)
main()