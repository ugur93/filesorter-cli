from os import listdir
from os.path import isfile, join, isdir
from datetime import datetime
import sys
import PIL.Image
from PIL.ExifTags import TAGS
import os
import shutil

import filetype

import pathlib

import magic


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
        print("> Listing contents of folder {0} in path {1}".format(
            folder, source_path))
        for file_name in files[0:10]:
            file_path = join(source_path, folder, file_name)
            file_stat = pathlib.Path(file_path).stat()
            creation_time = datetime.fromtimestamp(file_stat.st_mtime)
            print("File {0} in folder {1} with type {2} and date {3} {4}".format(
                file_name, file_path, filetype.guess_mime(file_path), creation_time, magic.from_file(file_path)))
            # move_file_by_year(file_path, file_name, "", move_file=False)


def sortByYear(source_path, dest_path):
    folders = [f for f in listdir(source_path) if isdir(
        join(source_path, f))]+[""]
    for folder in folders:
        print("Sorting folder {0}".format(folder))
        sub_folders = [f for f in listdir(join(source_path, folder)) if isdir(
            join(source_path, folder, f))]
        for subfolder in sub_folders:
            sub_folder_path = join(source_path, folder, subfolder)
            sortByYear(sub_folder_path, dest_path)

        files = [f for f in listdir(join(source_path, folder)) if isfile(
            join(source_path, folder, f))]
        for file_name in files:
            file_path = join(source_path, folder, file_name)
            move_file_by_year(file_path, file_name, dest_path)


def move_file_by_year(file_path, file_name, dest_path):
    try:
        dest_year_folder = get_destination_folder(
            file_path, file_name, dest_path)
        if (dest_year_folder is False):
            print(
                "Could not determine destination path for file {0}".format(file_name))
            return

        dest_path_file = join(dest_year_folder, file_name)
        create_folder(dest_year_folder)
        move_file(file_path, dest_path_file)
        print("Moved file {0} to {1}".format(
            file_path, dest_path_file))
    except:
        e = sys.exc_info()
        print(e)
        pass

def get_field(exif, field):
    for (k, v) in exif.items():
        if TAGS.get(k) == field:
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
        return join(dest_path, year, "video")
    elif (filetype.is_image(file_path)):
        img = PIL.Image.open(file_path)
        exif = img._getexif()
        img.close()
        datetime_original = get_field(exif, "DateTimeOriginal")
        year = datetime_original.split(":")[0]
        return join(dest_path, year)
    else:
        print("File {0} is not image or video".format(file_path))
    return False


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
