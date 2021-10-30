# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
# import the necessary packages
from imutils import paths
import numpy as np
import argparse
import cv2
import os
import csv

csv_columns = ['Hash','Paths']
csv_file = "Duplicates.csv"
# %%
def dhash(image, hashSize=8):
    # convert the image to grayscale and resize the grayscale image,
    # adding a single column (width) so we can compute the horizontal
    # gradient
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (hashSize + 1, hashSize))
    # compute the (relative) horizontal gradient between adjacent
    # column pixels
    diff = resized[:, 1:] > resized[:, :-1]
    # convert the difference image to a hash and return it
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])


# %%
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,
    help="path to input dataset")
ap.add_argument("-r", "--remove", type=int, default=-1,
    help="whether or not duplicates should be removed (i.e., dry run)")
args = vars(ap.parse_args())


# %%
# grab the paths to all images in our input dataset directory and
# then initialize our hashes dictionary
print("[INFO] computing image hashes...")
imagePaths = list(paths.list_images(args["dataset"]))
hashes = {}
# loop over our image paths
for imagePath in imagePaths:
    # load the input image and compute the hash
    image = cv2.imread(imagePath)
    h = dhash(image)
    # grab all image paths with that hash, add the current image
    # path to it, and store the list back in the hashes dictionary
    p = hashes.get(h, [])
    p.append(imagePath)
    hashes[h] = p


# %%

try:
    with open(csv_file, 'a+') as csvfile:
        for key in hashes.keys():
            csvfile.write("%s,%s\n"%(key,hashes[key]))
except IOError:
    print("I/O error")

# loop over the image hashes
for (h, hashedPaths) in hashes.items():
    # check to see if there is more than one image with the same hash
    if len(hashedPaths) > 1:
        # check to see if we got duplicates in a single class or in multiple classes
        kind = []
        killall = False
        for p in hashedPaths:
            k = '\\'.join(p.split('\\')[0:-1])
            if len(kind) == 0:
                kind.append(k)
            elif k not in kind:    
                #go for total kill as we have the same image in multiple classes
                killall = True
        if killall:
            flag = 'TRUE'
        else:
            flag = 'false'
        if args["remove"] <=0:
            print ("INFO: hash %s killall flag is %s" % (h,flag))
        else:
            print ("INFO: cleaning hash %s with killall flag set to %s" % (h,flag))
            if killall:
                for p in hashedPaths:
                    os.remove(p)
            else:
                #keep the first occurence of this image with duplicates only in the same class
                for p in hashedPaths[1:]:
                    os.remove(p)

