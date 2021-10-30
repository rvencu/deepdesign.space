# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import base64
import os
import requests
import time
from datetime import datetime
import cvlib
import cv2
import numpy as np
import csv

from io import BytesIO
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

scraped =['Abstract','African','American Colonial','Amish', 'Arabian', 'Art Deco', 'Art Moderne', 'Art Nouveau', 'Artisan', 'Arts and Crafts', 'Asian', 'Baroque', 'Bauhaus', 'Beach House', 'Bohemian', 'Brazilian', 'British Colonial', 'Carolean', 'Chinese', 'Chippendale', 'Coastal', 'Coastal', 'Commonwealth', 'Contemporary', 'Cottage', 'Country', 'Danish', 'Directoire', 'Dutch Renaissance', 'Eclectic', 'Egyptian', 'Empire', 'English', 'English Country', 'European', 'Exploration', 'Finnish', 'Flemish', 'French', 'French Provincial', 'Georgian', 'Gothic', 'Greek', 'Indian', 'Industrial', 'Italian', 'Jacobean', 'Japanese', 'Lake House', 'Machine Age', 'Medieval', 'Mediterranean', 'Memphis', 'Mexican', 'Mid-Century Modern', 'Minimalist', 'Mission', 'Modern', 'Moroccan', 'Nautical', 'Neoclassic', 'Northwestern', 'Old World', 'Organic', 'Palladian', 'Parisian', 'Pennsylvania Dutch', 'Plantation', 'Post-modern', 'Puritan', 'Queen Anne', 'Regal', 'Regence', 'Regency', 'Renaissance', 'Retro', 'Revival', 'Rietveld', 'Rococo', 'Romantic', 'Russian', 'Rustic', 'Scandinavian', 'Shabby chic', 'Shaker', 'Southwestern', 'Space age', 'Spanish Renaissance', 'Steampunk', 'Swedish', 'Modernist', 'Traditional', 'Transitional', 'Tropical', 'Tudor', 'Tuscan', ]
error = []

CHROME_DRIVER_LOCATION = r'chromedriver.exe'
THEME = 'interior design'
SEARCH_TERMS = ['Urban', 'Venetian', 'Victorian', 'Vintage', 'Western', 'William and Mary', 'Zen']
SEARCH_TERMS.sort()

EXCLUDED_SOURCES = ['123rf.com','shutterstock.com','airfrance.com','dreamstime.com']
INCLUDED_SOURCES = []


# %%
def check_if_result_b64(source):
    possible_header = source.split(',')[0]
    if possible_header.startswith('data') and ';base64' in possible_header:
        image_type = possible_header.replace('data:image/', '').replace(';base64', '')
        return image_type
    return False

def get_driver(TERM, THEME, INCLUDED_SOURCES, EXCLUDED_SOURCES):

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--allow-cross-origin-auth-prompt")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    modifier = ''
    if INCLUDED_SOURCES:
        modifier = ' site:'+' site:'.join(INCLUDED_SOURCES)
    elif EXCLUDED_SOURCES:
        modifier = ' -site:'+' -site:'.join(EXCLUDED_SOURCES)

    new_driver = webdriver.Chrome(executable_path=CHROME_DRIVER_LOCATION, options=options)
    new_driver.get(f"https://www.google.com/search?q={TERM + ' interior design' + modifier}&source=lnms&tbm=isch&sa=X&tbs=isz:lt,islt:2mp")
    return new_driver, TERM + ' ' + THEME + modifier

def unique(list1):
    # insert the list to the set
    list_set = set(list1)
    # convert the set to the list
    unique_list = (list(list_set))
    return unique_list


# %%

for TERM in SEARCH_TERMS:
    print(TERM)
    driver, query = get_driver(TERM, THEME, INCLUDED_SOURCES, EXCLUDED_SOURCES)
    CSV_SAVE_LOCATION = os.path.join(r'./images-raw/','labels.csv')
    with open (CSV_SAVE_LOCATION,'a+',newline='',encoding="utf-8") as labels:
        writer = csv.writer(labels)
        writer.writerow(['file','width','height','style','name','description','objects'])
    TARGET_SAVE_LOCATION = os.path.join(r'./images-raw/', TERM,  r'{}.{}')
    if not os.path.isdir(os.path.dirname(TARGET_SAVE_LOCATION)):
        os.makedirs(os.path.dirname(TARGET_SAVE_LOCATION))

    first_search_result = driver.find_elements_by_xpath('//a/div/img')[0]
    first_search_result.click()
    
    right_panel_base = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'''//*[@data-query="{query}"]''')))
    first_image = right_panel_base.find_elements_by_xpath('//*[@data-noaft="1"]')[0]
    magic_class = first_image.get_attribute('class')        
    image_finder_xp = f'//*[@class="{magic_class}"]'

    # initial wait for the first image to be loaded
    # this part could be improved but I couldn't find a proper way of doing it
    time.sleep(5)

    # initial thumbnail for "to_be_loaded image"
    thumbnail_src = driver.find_elements_by_xpath(image_finder_xp)[-1].get_attribute("src")

    for i in range(1000):

        try:
            # issue 4: All image elements share the same class. Assuming that you always click "next":
            # The last element is the base64 encoded thumbnail version is of the "next image"
            # [-2] element is the element currently displayed
            target = driver.find_elements_by_xpath(image_finder_xp)[-2]

            # you need to wait until image is completely loaded:
            # first the base64 encoded thumbnail will be displayed
            # so we check if the displayed element src match the cached thumbnail src.
            # However sometimes the final result is the base64 content, so wait is capped
            # at 5 seconds.
            wait_time_start = time.time()
            while (target.get_attribute("src") == thumbnail_src) and time.time() < wait_time_start + 10:
                time.sleep(0.2)
            thumbnail_src = driver.find_elements_by_xpath(image_finder_xp)[-1].get_attribute("src")
            attribute_value = target.get_attribute("src")
            attribute_label = target.get_attribute("alt")
        
            # issue 1: if the image is base64, requests get won't work because the src is not an url
            is_b64 = check_if_result_b64(attribute_value)
            if is_b64:
                print ('skipping base64 image')
            else:
                resp = requests.get(attribute_value, stream=True, timeout=30)
                temp_for_image_extension = BytesIO(resp.content)
                image = Image.open(temp_for_image_extension)
                image_format = image.format
                content = resp.content
                width, height = image.size
                temp_for_image_extension.seek(0)
                cv_image = cv2.imdecode(np.frombuffer(temp_for_image_extension.read(), np.uint8), 1)
                bbox, objects, conf = cvlib.detect_common_objects(cv_image, model='yolov4', confidence=0.7, enable_gpu=False)
                objects.sort()
                firstpos=attribute_value.rfind("/")
                lastpos=attribute_value.rfind(".")
                name = attribute_value[firstpos+1:lastpos]

                if min(width,height)>299:
                    print(attribute_value)
                    target = TARGET_SAVE_LOCATION.format(TERM.split(' ')[0]+'-'+datetime.now().strftime('%Y%m%d%H%M%S%f'), image_format)
                    with open(target, 'wb') as f:
                        with open (CSV_SAVE_LOCATION,'a+',newline='',encoding="utf-8") as labels:
                            f.write(content)
                            writer = csv.writer(labels)
                            writer.writerow([target,width,height,TERM,name,attribute_label,'|'.join(unique(objects))]) 

        except:
            print ('%s could not be opened' % temp_for_image_extension)
        finally:
            svg_arrows_xpath = '//div[@jscontroller]//a[contains(@jsaction, "click:trigger")]//*[@viewBox="0 0 24 24"]'
            next_arrow = driver.find_elements_by_xpath(svg_arrows_xpath)[-3]
            try:
                next_arrow.click()
            except:
                print()
                print ("Continuing with next query")
                print()
                break


# %%



