# Import necessary libraries
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.support import ui
from EnglishScraper import ScrapingEssentials
import threading
import csv
import os
import argparse

t = ScrapingEssentials("Pinterest")
valid_urls = []

parser = argparse.ArgumentParser(description='Which chunk to process?')
parser.add_argument('letter', metavar='N', type=str, help='the letter to process')
args = parser.parse_args()

# Determines if the page is loaded yet.
def page_is_loaded(driver):
    return driver.find_element_by_tag_name("body") != None


# Logs in to Pinterest.com to access the content
def login(driver, username, password):
    if driver.current_url != "https://www.pinterest.com/login/?referrer=home_page":
        driver.get("https://www.pinterest.com/login/?referrer=home_page")
    wait = ui.WebDriverWait(driver, 10)
    wait.until(page_is_loaded)
    email = driver.find_element_by_xpath("//input[@type='email']")
    password = driver.find_element_by_xpath("//input[@type='password']")
    email.send_keys("john@yijinjing.ro")
    password.send_keys("MUWN2frok_wirk*blax")
    # driver.find_element_by_xpath("//div[@data-reactid='30']").click()
    password.submit()
    time.sleep(3)
    print("Teleport Successful!")


# Search for the product, this is the way to change pages later.
def search_for_product(driver, keyword):
    seeker = driver.find_element_by_xpath("//input[@name='searchBoxInput']")
    seeker.send_keys(keyword)
    seeker.submit()

# Downloads the image files from the img urls
def get_pic(driver, valid_urls, category):
    #print("hey")
    #print (valid_urls)
    get_pic_counter = 0
    time.sleep(5)
    for urls in valid_urls:
        driver.get(urls[0])

        # Wait until the page is loaded
        if driver.current_url == urls[0]:
            wait = ui.WebDriverWait(driver, 10)
            wait.until(page_is_loaded)
            loaded = True
        #print(1)
        # -----------------------------------EDIT THE CODE BELOW IF PINTEREST CHANGES---------------------------#
        # Extract the image url
        soup = BeautifulSoup(driver.page_source, "html.parser")
        #print(2)
        for mainContainer in soup.find_all("div", {"class": "mainContainer"}):
            #print(3)
            for closeupContainer in mainContainer.find_all("div", {"data-test-id": "closeup-image"}):
                #print(4)
                # for heightContainer in closeupContainer.find_all("div", {"class": "FlashlightEnabledImage Module"}):
                #print(5)
                for img in closeupContainer.find_all("img"):
                    #print(6)
                    #print("hello")
                    img_link = img.get("src")
                    if "/564x/" in img_link:
                        #print("found the img url of: " + str(get_pic_counter))
                        get_pic_counter += 1
                        try:
                            title = soup.select('h1')[0].text.strip()
                        except:
                            title = ''
                        t.download_image(img_link.replace("/564x/","/originals/"),title, category)
                        break

        # ---------------------------------EDIT THE CODE ABOVE IF PINTEREST CHANGES-----------------------------#


def main(): 
    global t
    global args
    search_list = t.english_pickle(args.letter)
    print(search_list)
    driver1 = webdriver.Chrome()
    #driver2 = webdriver.Chrome()
    driver1.get("https://www.pinterest.com/login/?referrer=home_page")
    #driver2.get("https://www.pinterest.com/login/?referrer=home_page")
    # Log in to Pinterest.com

    login(driver1, "", "")
    #login(driver2, "", "")
    # Make sure it's loaded before doing anything

    loaded = False
    while loaded == False:
        if driver1.current_url != "https://www.pinterest.com/login/?referrer=home_page":
            loaded = True

    for item in search_list:
        print("start")
        keyword = item
        csv_path = os.path.join("/Users/user/PinterestScraper/Crawler/Pinterest/", keyword + '.csv')
        with open(csv_path, newline='') as f:
            reader = csv.reader(f)
            valid_urls = [line for line in reader]
        print(keyword)

        get_pic(driver1,valid_urls,keyword)

        print("done " + item)


if __name__ == "__main__":
    main()

else:
    main()
# while loaded:
#     driver.execute_script("window.scrollBy(0,250)")
