
import math
import itertools
import requests
from time import sleep
import json
import urllib.request
from os.path import exists
from os import system
import tqdm

import argparse
import getopt
import sys
import glob


# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]

short_options = "sp:"

# Long options
long_options = ["site", "path"]


PageToScrape = "imgur"  # Check siteInfo for what to write here.
imageSavePath = "./download"


LinksFile = "Links.json"
if not exists("./"+LinksFile):
    print("No LinkFile found. Please create one and edit LinksFile in script.")


siteInfo = {
    "imgur": {
        "name": "Imgur",
        "imageUrlPrefix": "https://i.imgur.com/",
        "imageUrlAppended": ".png",
        "urlLength": 5
    },
    "imgbb": {
        "imageUrlPrefix": "https://ibb.co/",
        "imageUrlAppended": "",
        "urlLength": 7
    }
}

siteInfo = siteInfo[PageToScrape]


try:
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help= "Path to save downloaded images")
    parser.add_argument("-s", "--site", help= "Wich page to scrape. Check siteInfo Dict inside script to se wich options are available.")

    args = parser.parse_args()

    if args.path:
        imageSavePath = args.path
    if args.site:
        PageToScrape = args.site


except Exception as e:
    print(e)
    exit()



imageSavePath = imageSavePath+PageToScrape


def _main_():
    
    lettersString = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    while True:
        pbar = tqdm.tqdm(enumerate(map(''.join, itertools.product(lettersString, repeat=siteInfo["urlLength"]))), total=math.comb(len(lettersString), siteInfo["urlLength"]))
        try:    
            for index, string in pbar:
                pbar.set_description("Current: "+str(string)+ " Index: "+ str(index))

                # TODO: Split files into subfolders with max limit number of files. Suggest 1000 per folder.
                ImgUrl = siteInfo["imageUrlPrefix"] + string + siteInfo["imageUrlAppended"]

                # print("Stats: Current combination: "+ImgUrl, end="\r")
                # If page exists,
                if CheckPageExists(ImgUrl, index):
                    imageDownloader(ImgUrl, index)
                # print("Stats: Current combination: "+ImgUrl+". Success: "+str(imageLinkSuccess)+" Fail: "+str(imageLinkFail), end="\r")
        except KeyboardInterrupt as e:
            input("\nPress CTRL+C again to exit. Press enter to coninue.")
            system("cls")

def imageDownloader(ImgUrl, index):

    newFileLocation = imageSavePath+"\\"+str(index)+" - "+ImgUrl.split('/')[-1]
    # newFileLocation = imageSavePath+"\\"+ ImgUrl.split('/')[-1]

    if glob.glob( r'%s' %(newFileLocation)):
        return
    

    try:
        if siteInfo["name"] == "Imgur":
            urllib.request.urlretrieve(ImgUrl, newFileLocation)
            return

        print("Something from Downloading image.")
    except WindowsError as e:
        if  e.winerror == 10055:
            print("\n")
            print("[WinError 10055] Too many connections at the same time. Trying again in 5 seconds.")
            sleep(3)
        if  e.winerror == 2:
            print("\n")
            print("[WinError 2] Can't find file. Delete last entry in LinksFile and try again.")
            sleep(3)
        else:
            print("Unknow error: " )
            print(e)
            exit()
    except TypeError as e:
        print(e)
        print("newFileLocation: "+newFileLocation)
        exit()


def getCheckedLinks():

    CheckedLinks = {}

    with open(LinksFile, "r+") as file:
        try:
            CheckedLinks = json.load(file)
        except:
            pass
    return CheckedLinks


def CheckPageExists(pageUrl, index):

    def writeJson(jsonData, LinksFile):
        with open(LinksFile, 'r+') as file:
            # First we load existing data into a dict.
            try:
                file_data = json.load(file)
            except ValueError:
                file_data = {}
            # Join new_data with file_data inside emp_details
            file_data[siteInfo["name"]].update(jsonData)
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent=4)

    while True and not pageUrl in CheckedLinks[siteInfo["name"]]:
        # if not pageUrl in emptyLinks:

        r = requests.head(pageUrl)
        try:

            if not r.status_code == 200:

                # print(str(index) + ", Fail: "+str(pageUrl)+" Status: " + str(r.status_code), end="\r")

                # emptyLinks.write(pageUrl)
                writeJson({pageUrl: r.status_code}, LinksFile)
                # return False
                break

            # print("Succsess! " + pageUrl, end="\n")

            writeJson({pageUrl: r.status_code}, LinksFile)
            return True
        except ConnectionError:
            print("\n")
            print("Connection Reset. Trying again in 5 seconds.")
            sleep(5)
    return False


system("cls")

CheckedLinks = getCheckedLinks()
_main_()
