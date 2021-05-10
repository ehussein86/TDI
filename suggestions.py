from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import urllib.request
import json
import requests
import re
import csv

#gets the search suggestions for a search query in YouTube
def youtubeSuggestions(lookup):

    #specific URL that has information about any search query in Google
    url = "https://suggestqueries.google.com/complete/search"
    #sets the parameters of the request to use firefox as well as reference YouTube 
    # and have the lookup query
    params = {
        "client" : "youtube",
        "ds" : "yt",
        "client" : "firefox",
        "q" : lookup
    }

    #uses requests library to get the HTML of the website
    r = requests.get(url, params = params)
    if(r.status_code == 200):
        #preparing to write to CSV file
        header = ['Youtube Search Suggestions for Query: {}'.format(lookup)]
        with open('youtubeSearchSuggest.csv', 'w') as csvfile:
            csvwriter = csv.DictWriter(csvfile, fieldnames=header)
            csvwriter.writeheader()
            csvwriter.writerow({
                    header[0] : '----------------------------------------------------'
            })
            #writes the json of the website at index 1 which 
            #returns all of the search predictions for any search query
            for i in range(0, len(r.json()[1])):
                csvwriter.writerow({
                    header[0] : r.json()[1][i]
                })



#dead code for right now, am not able to find a way to 
#get search suggestions for google News
'''
def googleNews(lookup):
    
    #driver = webdriver.Chrome("drivers/chromedriver.exe")

    #driver.get("https://news.google.com/")#topstories?hl=en-US&gl=US&ceid=US:en")
    
    #search = driver.find_element_by_class_name('Ax4B8 ZAGvjd')
    #search = driver.find_element_by_class_name('Ax4B8 ZAGvjd')
    
    #url = "https://news.google.com/search/"#?q={}&hl=en-US&gl=US&ceid=US%3Aen".format(lookup)
    url = "https://www.google.com/search?client=firefox-b-1-d&q={}".format(lookup)
    params = {
        "client" : "firefox",
        "q" : lookup
    }

    r = requests.get(url, params = params)
    if(r.status_code == 200):
        soup = BeautifulSoup(r.content, "html.parser")

        #search = soup.find('div', class_='u3WVdc jBmls')
        
        print(soup.prettify())
        results = []
        
        for searchResult in soup.find_all('div', class_='aajZCb'):
            if searchResult:
                print("hey")
        
        
        #for searchResult in soup.find_all('div', class_='u3WVdc jBmls'):
        #for searchResult in soup.find_all('div', class_='AOl7G eejsDc'):
        #for searchResult in soup.find_all('div', class_='KfXsid vkVJac'):

            print(searchResult)
            info = searchResult.find_all('div', class_='fDdcdd j61Coc')
            if info:
                print("hey")
            
        
    else:
        print("invalid url")
'''

#gets the search suggestions for a search query in Google
def googleSuggestions(lookup):
    #specific URL that has information about any search query in Google
    url = "https://suggestqueries.google.com/complete/search"
    #sets the parameters of the request to use firefox and have the lookup query
    params = {
        "client" : "firefox",
        "q" : lookup
    }

    #uses requests library to get the URL
    r = requests.get(url, params = params)
    if(r.status_code == 200):
        #preparing to write to CSV file
        header = ['Google Search Suggestions for Query: {}'.format(lookup)]
        with open('googleSearchSuggest.csv', 'w') as csvfile:
            csvwriter = csv.DictWriter(csvfile, fieldnames=header)
            csvwriter.writeheader()
            csvwriter.writerow({
                    header[0] : '----------------------------------------------------'
            })
            #writes the json of the website at index 1 which 
            #returns all of the search predictions for any search query
            for i in range(0, len(r.json()[1])):
                csvwriter.writerow({
                    header[0] : r.json()[1][i]
                })
        
    

def main():
    stringSearch = input("Enter your search term here: ")
    youtubeSuggestions(stringSearch)
    googleSuggestions(stringSearch)
    #googleNews(stringSearch)

main()




