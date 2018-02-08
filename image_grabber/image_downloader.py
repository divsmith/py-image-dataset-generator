import json
import os
import urllib2

from bs4 import BeautifulSoup

from grab_source import GrabSourceType
from settings import *
from utils.string_utils import StringUtil


# TODO: split this into 3 classes: abstract grab class, google grab class and imageDownloader calling sub grab classes
class ImageDownloader:
    """Download images from a keyword and website sources"""

    keyword = None
    destination = 'images'
    limit = 50

    sources = [GrabSourceType.GOOGLE]
    file_prefix = None

    def __init__(self, destination='images', limit=50):
        """Constructor for ImageGrabber"""
        self.destination = destination
        self.limit = limit

    def download_images(self, keyword):
        self.keyword = keyword
        self.__set_default_file_prefix()
        self.__grab_from_google()

    def __grab_from_google(self):
        query = self.keyword.split()
        query = '+'.join(query)
        url = GOOGLE_URL % query

        print '> searching image on Google : ' + url

        soup = self.__get_soup(url)

        sub_folder_name = self.__create_destination_folder()

        images_urls = []
        for a in soup.find_all("div", {"class": "rg_meta"}):
            link, Type = json.loads(a.text)["ou"], json.loads(a.text)["ity"]
            # links for Large original images, type of  image
            images_urls.append((link, Type))

        print "total of %s images found (limit to download set to %s)" % (len(images_urls), self.limit)

        self.__download_files(images_urls, sub_folder_name)

    def __set_default_file_prefix(self):
        """if no specified file prefix, build one from keyword"""
        if self.file_prefix is None:
            self.file_prefix = StringUtil.underscore_and_lowercase(self.keyword)

    def __create_destination_folder(self):
        """ set default destination to 'images', create and return sub_folder based on keyword name """
        if self.destination is None:
            self.destination = 'images'

        if not os.path.exists(self.destination):
            os.mkdir(self.destination)
        sub_folder = os.path.join(self.destination, StringUtil.underscore_and_lowercase(self.keyword))

        if not os.path.exists(sub_folder):
            os.mkdir(sub_folder)
        return sub_folder

    def __download_files(self, urls, folder_name):
        """ save images in file system from list of urls """
        for i, (img, Type) in enumerate(urls):
            if i == self.limit:
                break
            try:
                req = urllib2.Request(img, headers={'User-Agent': USER_AGENT_HEADER})
                raw_img = urllib2.urlopen(req).read()

                counter = len([i for i in os.listdir(folder_name) if self.file_prefix in i]) + 1
                extension = ".jpg" if len(Type) == 0 else "." + Type
                file_name = self.file_prefix + "_" + str(counter) + extension
                f = open(os.path.join(folder_name, file_name), 'wb')

                print "> grabbing %s \n >> saving file %s" % (img, file_name)

                f.write(raw_img)
                f.close()

            except Exception as e:
                print "could not load : " + img
                print e

    def __get_soup(self, url):
        return BeautifulSoup(urllib2.urlopen(urllib2.Request(url, headers=USER_AGENT_HEADER)), 'html.parser')