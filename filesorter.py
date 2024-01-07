import faulthandler

faulthandler.enable()
from os import listdir
from os.path import isfile, join, isdir
from datetime import datetime
import sys
import PIL.Image
from PIL.Image import Exif
from PIL import ExifTags
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPS
import os
import shutil

import filetype

import pathlib

import magic
from geopy.geocoders import Nominatim
from geopy import Location

geolocator = Nominatim(user_agent="filesorter")
def debugFile(file_path):
    fileinfo = magic.from_file(file_path)
    file_name = os.path.basename(file_path)
    if (filetype.is_video(file_path) or "MPEG" in fileinfo):
        year = file_name[0:4]
        if (year.isnumeric() is False):
            file_stat = pathlib.Path(file_path).stat()
            year = str(datetime.fromtimestamp(
                file_stat.st_mtime).year)
        print("Video file {0} is from year {1}".format(file_name, year))
    elif (filetype.is_image(file_path)):
        img = PIL.Image.open(file_path)
        exif = img.getexif().get_ifd(ExifTags.IFD.Exif)
        gps = img.getexif().get_ifd(ExifTags.IFD.GPSInfo)
        img.close()
        datetime_original = get_field(exif, "DateTimeOriginal")
        year = None
        if (datetime_original is None):
            create_time = os.path.getmtime(file_path)
            create_date = datetime.fromtimestamp(create_time)
            year = str(create_date.year)
            print("Could not determine year of image file {0} from EXIF. Using creation date of file".format(file_name))
        else:
            year = datetime_original.split(":")[0]
        print("Image file {0} is from year {1}".format(file_name, year))
        adress = getImagelocation(gps)
        print("Image GPS data {0} {1}".format(adress.point, adress.address))
    else:
        print("File {0} is not image or video".format(file_path))
    return False

def getImagelocation(gps) -> Location:
    longitude = get_field(gps, GPS.GPSLongitude)
    latitude = get_field(gps, GPS.GPSLatitude)
    print(longitude, latitude)
    if (longitude is None or latitude is None):
        obj = type('obj', (object,), {'address' : None, 'point' : None})
        return obj
    latnumber = float(latitude[0]) + float(latitude[1])/60 + float(latitude[2])/3600
    longnumber = float(longitude[0]) + float(longitude[1])/60 + float(longitude[2])/3600
    adress = geolocator.reverse((latnumber, longnumber))
    return adress
def listFiles(source_path):
    folders = [f for f in listdir(source_path) if isdir(
        join(source_path, f))] + [""]
    for folder in folders:
        sub_folders = [f for f in listdir(join(source_path, folder)) if isdir(
            join(source_path, folder, f))]

        for subfolder in sub_folders:
            sub_folder_path = join(source_path, folder, subfolder)
            listFiles(sub_folder_path)

        files = [f for f in listdir(join(source_path, folder)) if isfile(
            join(source_path, folder, f))]
        print("> Listing contents of folder {0} in path {1}. Number of files {2}".format(
            folder, source_path, files.__len__()))
        for file_name in files[0:10]:
            file_path = join(source_path, folder, file_name)
            file_stat = pathlib.Path(file_path).stat()
            creation_time = datetime.fromtimestamp(file_stat.st_mtime)
            print("File {0} in folder {1} with type {2} and date {3} {4}".format(
                file_name, file_path, filetype.guess_mime(file_path), creation_time, magic.from_file(file_path)))
            # move_file_by_year(file_path, file_name, "", move_file=False)


def sortByYear(source_path, dest_path, simulation):
    folders = [f for f in listdir(source_path) if isdir(
        join(source_path, f))]+[""]
    for folder in folders:
        print("Sorting folder {0}".format(folder))
        sub_folders = [f for f in listdir(join(source_path, folder)) if isdir(
            join(source_path, folder, f))]
        for subfolder in sub_folders:
            sub_folder_path = join(source_path, folder, subfolder)
            sortByYear(sub_folder_path, dest_path, simulation)

        files = [f for f in listdir(join(source_path, folder)) if isfile(
            join(source_path, folder, f))]
        for file_name in files:
            file_path = join(source_path, folder, file_name)
            move_file_by_year(file_path, file_name, dest_path, simulation)


def move_file_by_year(file_path, file_name: str, dest_path, simulation=False):
    try:
        if (file_name.endswith(".json")):
            return
        dest_year_folder = get_destination_folder(
            file_path, file_name, dest_path)
        if (dest_year_folder is False):
            print(
                "Could not determine destination path for file {0}".format(file_name))
            return

        dest_path_file = join(dest_year_folder, file_name)
        if (simulation is True):
            print("Simulating move of file {0} to {1}".format(
                file_path, dest_path_file))
            return
        create_folder(dest_year_folder)
        move_file(file_path, dest_path_file)
        print("Moved file {0} to {1}".format(
            file_path, dest_path_file))
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        e = sys.exc_info()
        print("Det skjedde en feil med filen {0} {1}".format(file_path, e))
        pass

def get_field(exif: Exif, field):
    for (k, v) in exif.items():
        if TAGS.get(k) == field:
            return v
        elif field == k:
            return v

def get_destination_folder(file_path, file_name, dest_path):
    fileinfo = magic.from_file(file_path)
    if (filetype.is_video(file_path) or "MPEG" in fileinfo):
        year = file_name[0:4]
        if (year.isnumeric() is False):
            file_stat = pathlib.Path(file_path).stat()
            year = str(datetime.fromtimestamp(
                file_stat.st_mtime).year)
            # print(
            #    "Could not determine year of videofile {0}".format(file_name))
            # return False
        print("Video file {0} is from year {1}".format(file_name, year))
        return join(dest_path, year, "video")
    elif (filetype.is_image(file_path)):
        img = PIL.Image.open(file_path)
        exif = img.getexif().get_ifd(ExifTags.IFD.Exif)
        gps = img.getexif().get_ifd(ExifTags.IFD.GPSInfo)
        img.close()
        datetime_original = get_field(exif, "DateTimeOriginal")
        year = None
        if (datetime_original is None):
            create_time = os.path.getmtime(file_path)
            create_date = datetime.fromtimestamp(create_time)
            year = str(create_date.year)
            raise RuntimeError("Could not determine year of image file {0}".format(file_name))
        else:
            year = datetime_original.split(":")[0]
        print("Image file {0} is from year {1}".format(file_name, year))
        #printLocation(gps, file_path)
        return join(dest_path, year)
    else:
        print("File {0} is not image or video".format(file_path))
    return False
def printLocation(gps, filepath):
    try:
        adress = getImagelocation(gps)
        print("Image GPS data {0}: {1} {2}".format(filepath, adress.point, adress.address))
    except:
        e = sys.exc_info()
        print("Could not get location for file {0} {1}".format(filepath, e))
        pass
def create_folder(path):
    if os.path.exists(path) is False:
        os.makedirs(path)
    pass


def move_file(file_path, dest_path):
    if os.path.exists(dest_path):
        print(
            "Could not move file {0} because it already exists in path {1}".format(file_path, dest_path))
        return False

    shutil.move(file_path, dest_path)
    return True

# print(TAGS)
