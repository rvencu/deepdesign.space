# Import necessary libraries
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.support import ui
from EnglishScraper import ScrapingEssentials
import threading
import csv
import os

t = ScrapingEssentials("Pinterest")

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


# Finds the detailed product page of each "pin" for pinterest
def download_pages(driver,category):
    list_counter = 0
    beginning = time.time()
    end = time.time()
    # Pinterest happens to change its HTML every once in a while to prevent botting.

    # This should account for all the differences
    # soup = BeautifulSoup(driver.page_source, "lxml")
    # for pinWrapper in soup.find_all("div", {"class": "pinWrapper"}):
    #     class_name = pinWrapper.get("class")
    #     print(class_name)
    #     if "_o" in class_name[0]:
    #         print(class_name)
    #         break
    #
    # #Finds the tags of the HTML and adjusts it
    # name = " ".join(class_name)
    # print(name)

    # Does this until you have 10000 items or the program has gone on for long enough, meaning that it reached the end of results
    valid_urls = []
    csv_path = os.path.join("/Users/user/PinterestScraper/Crawler/Pinterest/", category + '.csv')
    while list_counter < 1200 and beginning - end < 30:
        beginning = time.time()
        # ----------------------------------EDIT THE CODE BELOW------------------------------#
        # Locate all the urls of the detailed pins
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # for c in soup.find_all("div", {"class": name}):
        for pinLink in soup.find_all("div", {"data-test-id": "pinWrapper"}):
            for a in pinLink.find_all("a"):
                #print(pinLink)
                url = ("https://pinterest.com" + str(a.get("href")))
                #print(url)
                # Checks and makes sure that the pin isn't there already and that random urls are not invited
                if len(url) < 100 and url not in valid_urls and "A" not in url:
                    # ---------------------------------EDIT THE CODE ABOVE-------------------------------#
                    #print(url)
                    valid_urls.append(url)
                    with open (csv_path,'a+',newline='',encoding="utf-8") as labels:
                        writer = csv.writer(labels)
                        writer.writerow([url])
                    if list_counter % 100 ==0:
                        print(category + ": found the detailed page of: " + str(list_counter))
                    list_counter += 1
                    end = time.time()
                time.sleep(.15)
                # Scroll down now
        driver.execute_script("window.scrollBy(0,1000)")
    return


def main():
    global t
    list = t.english_pickle()
    print(list)
    driver1 = webdriver.Chrome()
    driver1.get("https://www.pinterest.com/login/?referrer=home_page")

    login(driver1, "", "")

    loaded = False
    while loaded == False:
        if driver1.current_url != "https://www.pinterest.com/login/?referrer=home_page":
            loaded = True

    for item in list:
        print("start")
        keyword = item
        print(keyword)
        driver1.get("https://pinterest.com/search/pins/?q=" + str(keyword) + "&rs=typed&term_meta[]=" + str(keyword) + "%7Ctyped")
        download_pages(driver1,keyword)
        print("done " + item)


if __name__ == "__main__":
    main()

else:
    main()
# while loaded:
#     driver.execute_script("window.scrollBy(0,250)")
