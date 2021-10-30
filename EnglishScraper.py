#Import necessary libraries
from urllib.request import urlretrieve
import os.path
import os
import cvlib
import cv2
import numpy as np
import csv
from io import BytesIO
from PIL import Image
import requests
from datetime import datetime

def unique(list1):
    # insert the list to the set
    list_set = set(list1)
    # convert the set to the list
    unique_list = (list(list_set))
    return unique_list

#Creates a class that contains the scraping essentials
class ScrapingEssentials(object):

    #Necessaary Class Variables
    currentItem = 0
    number = 0
    categories = []
    #Initializing a directory for the pictures to come in
    def __init__(self, source):
        ScrapingEssentials.number = 0
        self.source = source
        file_path_string = "/Users/user/PinterestScraper/Crawler/" + source
        if not os.path.exists(file_path_string):
            os.makedirs(file_path_string)
    # Needed to make a class to have a static way of counting
    def reset(self):
        ScrapingEssentials.number = 0
        ScrapingEssentials.currentItem += 1
    #Convert the file from a url to an actual image file and store it on the commputer
    def download_image(self, link, title, category):
        try:
            done = False
            #print("processing file: " + str(ScrapingEssentials.number))
            #Make a requests object
            #Make a folder name
            lett = category[0]

            file_name = datetime.now().strftime('%Y%m%d%H%M%S%f')
            #Make the directory of the folder
            file_path_string = "/Users/user/PinterestScraper/Crawler/" + self.source + "/" + category
            file_path = os.path.join(file_path_string, (file_name + ".jpg"))
            csv_path = os.path.join("/Users/user/PinterestScraper/Crawler/" + self.source + "/", 'labels' + str(lett) + '.csv')

            if not os.path.exists(file_path_string):
                os.makedirs(file_path_string)
            #Download it on the computer
            #print(file_path + "  " + link)
            ScrapingEssentials.number += 1

            #urlretrieve(link, file_path)
            resp = requests.get(link, stream=True, timeout=10)
            if resp.status_code != 200:
                resp = requests.get(link.replace(".jpg",".png"), stream=True, timeout=10)

            temp_for_image_extension = BytesIO(resp.content)
            image = Image.open(temp_for_image_extension)
            image_format = image.format
            content = resp.content
            width, height = image.size
            temp_for_image_extension.seek(0)
            cv_image = cv2.imdecode(np.frombuffer(temp_for_image_extension.read(), np.uint8), 1)
            bbox, objects, conf = cvlib.detect_common_objects(cv_image, model='yolov4', confidence=0.7, enable_gpu=False)
            objects.sort()
            #firstpos=link.rfind("/")
            #lastpos=link.rfind(".")
            #name = link[firstpos+1:lastpos]
            if min(width, height)>300:
                print(str(ScrapingEssentials.number) + ": " + link)
                with open(file_path, 'wb') as f:
                    with open (csv_path,'a+',newline='',encoding="utf-8") as labels:
                        f.write(content)
                        writer = csv.writer(labels)
                        writer.writerow([file_path,width,height,category,title,'|'.join(unique(objects))])
        except Exception:
            pass

    def english_pickle(self, letter):
        THEME = ' interior design'
        done = ['Abstract','African', 'American Colonial', 'Amish', 'Arabian', 'Art Deco']
        A = ['Art Moderne', 'Art Nouveau', 'Artisan', 'Arts and Crafts', 'Asian']
        B = ['Baroque', 'Bauhaus', 'Beach House', 'Bohemian', 'Brazilian', 'British Colonial']
        C = ['Carolean', 'Chinese', 'Chippendale', 'Coastal', 'Commonwealth', 'Contemporary', 'Cottage', 'Country']
        D = ['Danish', 'Directoire', 'Dutch Renaissance']
        E = ['Eclectic', 'Egyptian', 'Empire', 'English', 'English Country', 'European', 'Exploration']
        F = ['Finnish', 'Flemish', 'French', 'French Provincial']
        G = ['Georgian', 'Gothic', 'Greek']
        I = ['Indian', 'Industrial', 'Italian']
        J = ['Jacobean', 'Japanese']
        L = ['Lake House']
        M = ['Machine Age', 'Medieval', 'Mediterranean', 'Memphis', 'Mexican', 'Mid-Century Modern', 'Minimalist', 'Mission', 'Modern', 'Modernist', 'Moroccan']
        N = ['Nautical', 'Neoclassic', 'Northwestern']
        O = ['Old World', 'Organic']
        P = ['Palladian', 'Parisian', 'Pennsylvania Dutch', 'Plantation', 'Post-modern', 'Puritan']
        Q = ['Queen Anne']
        R = ['Regal', 'Regence', 'Regency', 'Renaissance', 'Retro', 'Revival', 'Rietveld', 'Rococo', 'Romantic', 'Russian', 'Rustic']
        S = ['Scandinavian', 'Shabby chic', 'Shaker', 'Southwestern', 'Space age', 'Spanish Renaissance', 'Steampunk', 'Swedish']
        T = ['Traditional', 'Transitional', 'Tropical', 'Tudor', 'Tuscan']
        U = ['Urban']
        V = ['Venetian', 'Victorian', 'Vintage']
        W = ['Western', 'William and Mary']
        Z = ['Zen']
        SEARCH_TERMS = []
        if letter:
            ScrapingEssentials.categories = [s + THEME for s in eval(letter)]
        else:
            ScrapingEssentials.categories = [s + THEME for s in SEARCH_TERMS]
        return ScrapingEssentials.categories