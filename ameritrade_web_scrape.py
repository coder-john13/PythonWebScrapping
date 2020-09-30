#web scrapping

#NOTES
#this code assumes you have an ameritrade brokerage account, and are able to login.
#put login info in the username and password sections in the mainloop
#all stock information that you want scraped is in a watchlist, and you use an xpath to get to it
#the field names for the data is hard coded in, so you'll have to change that for your specific instance


import requests
import urllib.request
import time
import csv
import re
import pandas
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import schedule
import lxml.html as lh

def ameritrade_login(username, password):
    # must have the following imports:
    #       import requests
    #       from selenium import webdriver
    #       from selenium.webdriver.common.keys import Keys

    # this code successfully logins to my ameritrade account
    #     2 inputs
    #     username: a string containing the username of an ameritrade account
    #     password: a string containing the password of an ameritrade account
    # note: this code assumes no second layer of protection when logging in. i.e no security questions

    # login info
    driver = webdriver.Chrome(executable_path=r'Path to the updated chrome driver for selenium on your machine')
    driver.get('https://invest.ameritrade.com/grid/p/login')  # put here the adress of your page
    # username
    time.sleep(2)
    elem = driver.find_element_by_name('tbUsername')
    elem.clear()  # clears the current input
    elem.send_keys(username)  # inputs the username
    elem.send_keys(Keys.RETURN)  # return for input
    # password
    elem = driver.find_element_by_name('tbPassword')
    elem.clear()  # clears the current input
    elem.send_keys(password)  # inputs the password
    elem.send_keys(Keys.RETURN)  # return for input
    time.sleep(2)
    return driver


def go_to_watchlist_page(driver):
    #goes to the watchlist page
    #must be passed in the driver for the web browser that is being used
    time.sleep(2)
    driver.get('https://invest.ameritrade.com/grid/p/site#r=watchlist')
    return driver

def find_stock_data(driver):
    #finds stock data that is in a table in my ameritrade account
    #passed in a driver to the webpage
    #returns a string with the stock name and several variable of the stock in stock_data
    #must have the correct xpath -> inspect webpage -> Find table with wanted info -> cope xpath
    time.sleep(2)
    page = requests.get(driver.current_url)
    #find the xpath that you want on the page
    elem = driver.find_element_by_xpath('//*[@id="retail_layout_Scrollable_2"]/div[3]/div/div/table/tbody')
    stock_data = elem.text
    return stock_data


def write_stocks2list(stock_data):
    #      #this code changes the stock data into a nested list with each row being a list [[row0,..],[row1,..]...]
    #      #the stock data needs to be a string with the prevalent stock information
    #      # the data comes in with stocks on a line above all info, so it must be changed

    #Changes the stock data to have the stocks and stock data on same line
    stocks = stock_data.splitlines()
    length = int(len(stocks))
    index = 1
    FINAL = stocks[0]
    while index < length:
        if index % 2 == 1:
            FINAL = FINAL + stocks[index] + '\n'
        else:
            FINAL = FINAL + stocks[index]
        index = index + 1

    nlines = FINAL.count('\n')
    stocks = FINAL.split()

    #modify ist so each individual object is its own item in the list ie. last traded date and time and B/A Size
    i = 0
    while i < len(stocks):
        if stocks[i] == 'ET':
            #stocks[i-1] = stocks[i-1]+ stocks[i+1]
            #del stocks[i+1]
            del stocks[i]
        if stocks[i] == 'X':
            stocks[i-1] = stocks[i-1]+stocks[i]+stocks[i+1]
            del stocks[i+1]
            del stocks[i]
        if stocks[i] == '<':
            stocks[i] = stocks[i] + stocks[i+1]
            del stocks[i+1]
        i = i+1

    #PUTS EACH ROW INTO A NESTED LIST
    j = 0
    i = 0
    elements = 24
    big = []
    while j <nlines:
        temp = []
        while i < elements*j:
            temp.append(stocks[i])
            i = i+1
        big.append(temp)
        j = j+1
    del big[0]
    return big

def write_stocks2csv(csv_file,stock_list):
    #this function writes a given list to a csv file
    # it is assumed that all neccessary stock info is in a nested list fashion ie. [[some, stock, info],[more, stock, info]...]

    #put the stock data into a csv file
    print(stock_list)
    with open(csv_file, newline='',mode='a') as stock_file:
        stock_writer = csv.writer(stock_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        #USE THE CODE BELOW IF IT IS THE FIRST TIME WRITING TO THE FILE: I.E TO MAKE THE CORRECT HEADLINES
        #fieldnames = ['Stock', 'Bid', 'Ask','Price', 'Chg($)', 'Chg(%)', 'Last', 'Last Chg($)','Last Chg(%)','Volume','Close', 'Open', 'High', 'Low', 'Last Traded Size', 'Last Traded Time', 'B/A size', '52-week high', '52-week low','stock exchange','P/E','Ex-div date','Div yield','Div amount']
        #writer = csv.DictWriter(stock_file, fieldnames=fieldnames)
        #writer.writeheader()
        print("made it 1")
        index = 0
        while index < len(stock_list):
            stock_writer.writerow(stock_list[index])
            index = index+1
        df = pandas.read_csv(csv_file)
        pandas.set_option('display.max_columns', None)
        print(df)



def repeat(driver):
    stock_data = find_stock_data(driver)
    csv_file = 'stocks.csv'
    stock_list = write_stocks2list(stock_data)
    write_stocks2csv(csv_file, stock_list)

def start():
    #enter username data
    username = 'Enter username Here';
    #enter password data
    password = 'Enter Password here';
    driver = ameritrade_login(username, password)
    go_to_watchlist_page(driver)
    return driver

# main function
driver = start()
while 1:
    try:
        repeat(driver)
    except:
        print("an exception was thrown")
        time.sleep(30)
        repeat(driver)
    time.sleep(10)



