import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime

import subprocess
import os
import json

class ExifTool(object):
    sentinel = "{ready}\n"

    def __init__(self, executable="exiftool"):
        self.executable = executable

    def __enter__(self):
        self.process = subprocess.Popen(
            [self.executable, "-stay_open", "True", "-@", "-"],
            universal_newlines=True,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return self

    def  __exit__(self, exc_type, exc_value, traceback):
        self.process.stdin.write("-stay_open\nFalse\n")
        self.process.stdin.flush()

    def execute(self, *args):
        args = args + ("-execute\n",)
        self.process.stdin.write(str.join("\n", args))
        self.process.stdin.flush()
        output = ""
        fd = self.process.stdout.fileno()
        while not output.endswith(self.sentinel):
            output += os.read(fd, 4096).decode('utf-8')
        return output[:-len(self.sentinel)]

    def get_metadata(self, *filenames):
        return json.loads(self.execute("-G", "-j", "-n", *filenames))


def get_create_date_and_camera_from_exif(image_file):
    image = Image.open(image_file)
    info = image._getexif()
    if info is None:
        return None, 'no info'

    try:
        date = datetime.strptime(info[0x9004], "%Y:%m:%d %H:%M:%S")
    except KeyError as e:
        print("Exception:")
        print(e)
        print(image_file, info)
        date = None
    #print(date)
    try:
        camera = info[0x0110]
    except KeyError:
        camera = 'no info'
    return date, camera


def get_create_date_for_video(video_file):
    with ExifTool() as e:
        metadata = e.get_metadata(video_file)
        try:
            return datetime.strptime(metadata[0]["QuickTime:MediaCreateDate"], "%Y:%m:%d %H:%M:%S")
        except KeyError:
            print("No creation_date for ", video_file)
            return None


def get_filenames(path):
    return [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


def get_extensions(filenames):
    ext = []
    for f in filenames:
        current_ext = os.path.basename(f).split(os.path.extsep)[-1]
        if current_ext not in ext:
            ext.append(current_ext)
    return ext

def get_list_of_images(files, extensions=['jpg', 'png', 'jpeg']):
    return [f for f in files if os.path.basename(f).split(os.path.extsep)[-1].lower() in extensions]

def get_list_of_videos(files, extensions=['m4v', 'mov', 'mp4']):
    return [f for f in files if os.path.basename(f).split(os.path.extsep)[-1].lower() in extensions]

if __name__ == '__main__':
    # TODO: implement args:
    path = "/Users/<username>/Desktop/photo_backup_2"
    files = get_filenames(path)
    #print(TAGS.keys(), TAGS.items())
    #print(TAGS.items())
    #exit()

    img_output_dir = os.path.join(path, "img_output")
    vid_output_dir = os.path.join(path, "vid_output")
    if not os.path.exists(img_output_dir):
        os.mkdir(img_output_dir)
    if not os.path.exists(vid_output_dir):
        os.mkdir(vid_output_dir)

    # Check wich extensions are used:
    print(get_extensions(files))
    images = get_list_of_images(files)
    videos = get_list_of_videos(files)

    images.sort()
    print(get_extensions(images))
    print(images)

    for i in images:
        try:
            date, camera = get_create_date_and_camera_from_exif(i)
        except AttributeError:
            continue
        if date is None:
            continue
        ext = os.path.basename(i).split(os.path.extsep)[-1]
        new_image_name = date.strftime("%Y-%m-%d-%H-%M-%S") + "_" + camera.replace(" ", "-") + "." + ext
        counter = 0
        print(i)

        try:
            while os.path.exists(os.path.join(img_output_dir, new_image_name)):
                counter += 1
                new_image_name = date.strftime("%Y-%m-%d-%H-%M-%S") + "_" + camera.replace(" ", "-") + "_" + str(counter) + "." + ext
            #print(new_image_name)
            shutil.move(i, os.path.join(img_output_dir, new_image_name))
        except ValueError:
            continue

    for i in videos:
        date = get_create_date_for_video(i)
        if date is None:
            continue

        ext = os.path.basename(i).split(os.path.extsep)[-1]

        new_image_name = date.strftime("%Y-%m-%d-%H-%M-%S") + "." + ext
        counter = 0
        while os.path.exists(os.path.join(vid_output_dir, new_image_name)):
            counter += 1
            new_image_name = date.strftime("%Y-%m-%d-%H-%M-%S") + "_" + str(counter) + "." + ext
        shutil.move(i, os.path.join(vid_output_dir, new_image_name))


