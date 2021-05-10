
from selenium import webdriver
from selenium.webdriver.common.by import By
from googleapiclient.discovery import build 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import urllib.request
import json
import requests
import re
import time
import csv
#import pandas as pd




#1-20 minutes wait 
def main():
    #takes in two search inputs to perform the youtube search
    stringSearch = input("Enter your search term here: ")
    stringSearch2 = input("Enter your second search term here: ")
    
    minuteCount = 1
    for i in range(60, 1200, 60):

        #Three dictionaries to hold all of the values
        youTubeQ1 = {

        } 
        youTubeQ2 = {

        }
        inCognitoQ2 = {

        }

        #Chrome options for the first browser in selenium in order to keep the browser always open
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)

        #Chrome options for the first browser in selenium in order to open the browser as incognito
        inCogOptions = webdriver.ChromeOptions()
        inCogOptions.add_argument("--incognito")

        #driver for the first browser gets path of the chrome executable
        #specify your path for the chrome executable when running code
        driver = webdriver.Chrome(options=options, executable_path='/mnt/c/Users/joshu/seleniumProj/drivers/chromedriver.exe')

        #first selenium browser enters search query into youtube
        driver.get("http://youtube.com/")
        driver.find_element_by_name("search_query").send_keys(stringSearch)
        driver.find_element_by_name("search_query").send_keys(Keys.ENTER)
   
        time.sleep(5)
        #gets the youtube results (title and url) and puts it into the first dictionary
        names = driver.find_elements_by_xpath('//a[@id="video-title"]')
        #names = driver.find_elements_by_xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/div/div[1]/div/h3/a')
        for name in names:
            youTubeQ1[name.get_attribute('title')] = name.get_attribute('href')
    
        #loop from 1-20 minutes
        time.sleep(i)

        #resets the browser and puts in the second search query into the same browser
        driver.find_element_by_name("search_query").clear()
        driver.find_element_by_name("search_query").send_keys(stringSearch2)
        driver.find_element_by_name("search_query").send_keys(Keys.ENTER)

        #sets up the incognito selenium driver
        incognitoDriver = webdriver.Chrome(options=inCogOptions, executable_path='/mnt/c/Users/joshu/seleniumProj/drivers/chromedriver.exe')
        incognitoDriver.get("http://youtube.com/")
         
        #searches the second search query in the incognito browser
        incognitoDriver.find_element_by_name("search_query").send_keys(stringSearch2)
        incognitoDriver.find_element_by_name("search_query").send_keys(Keys.ENTER)

        time.sleep(5)
        #gets the titles and urls from the same browser for search query 2
        names2 = driver.find_elements_by_xpath('//a[@id="video-title"]')
        #names2 = driver.find_elements_by_xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/div/div[1]/div/h3/a')
        for name2 in names2:
            youTubeQ2[name2.get_attribute('title')] = name2.get_attribute('href')


        #gets the titles and urls from the incognito browser for search query 2
        names3 = driver.find_elements_by_xpath('//a[@id="video-title"]')
        #names3 = driver.find_elements_by_xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/div/div[1]/div/h3/a')
        for name3 in names3:
            inCognitoQ2[name3.get_attribute('title')] = name3.get_attribute('href')
           

        #quit both the browsers
        incognitoDriver.quit()
        driver.quit()

        
        #outputs the Q1 search results to 1st CSV file
        header = ['Youtube Search Suggestions for Query: {}'.format(stringSearch)]
        with open('youTubeQ1-{}minutes.csv'.format(minuteCount), mode='w') as csvfile:
            csvwriter = csv.DictWriter(csvfile, fieldnames=header)
            csvwriter.writeheader()
            csvwriter.writerow({
                    header[0] : ''
            })
            entryCounter = 0
            for key in youTubeQ1:
                if (entryCounter < 20):
                    csvwriter.writerow({
                        header[0] : key
                    })
                    csvwriter.writerow({
                        header[0] : youTubeQ1[key]
                    })
                    csvwriter.writerow({
                        header[0] : ''
                    })
                    entryCounter = entryCounter + 1
                
        #outputs the Q2 search results to 2nd CSV file
        header2 = ['Youtube Search Suggestions for Query: {}'.format(stringSearch2)]
        with open('youTubeQ2-{}minutes.csv'.format(minuteCount), mode='w') as csvfile:
            csvwriter = csv.DictWriter(csvfile, fieldnames=header2)
            csvwriter.writeheader()
            csvwriter.writerow({
                    header2[0] : ''
            })
            entryCounter = 0
            for key in youTubeQ2:
                if (entryCounter < 20):
                    csvwriter.writerow({
                        header2[0] : key
                    })
                    csvwriter.writerow({
                        header2[0] : youTubeQ2[key]
                    })
                    csvwriter.writerow({
                        header2[0] : ''
                    })
                    entryCounter = entryCounter + 1
                
        
        #outputs the Q2 Incognito browser search results to 3rd CSV file
        header3 = ['Incognito Youtube Search Suggestions for Query: {}'.format(stringSearch2)]
        with open('inCognitoQ2-{}minutes.csv'.format(minuteCount), mode='w') as csvfile:
            csvwriter = csv.DictWriter(csvfile, fieldnames=header3)
            csvwriter.writeheader()
            csvwriter.writerow({
                    header3[0] : ''
            })
            entryCounter = 0
            for key in inCognitoQ2:
                if (entryCounter < 20):
                    csvwriter.writerow({
                        header3[0] : key
                    })
                    csvwriter.writerow({
                        header3[0] : inCognitoQ2[key]
                    })
                    csvwriter.writerow({
                        header3[0] : ''
                    })
                    entryCounter = entryCounter + 1

        minuteCount = minuteCount + 1

main()
