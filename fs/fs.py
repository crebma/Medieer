import os
from os.path import join as fjoin
from urllib2 import urlopen

from sqlobject import SQLObjectNotFound

from data import Settings

def make_list(basepath):
    allowed_extensions = ['m4v', 'mp4', 'mov', 'wmv']
    videos = []
    for root, dirs, files in os.walk(basepath):
        for name in files:
            if name.split('.')[-1] in allowed_extensions:
                videos.append(fjoin(root,name))
                
    return videos

def download_file(URL, dest):
    if "http" not in URL[:4]:
        raise ValueError('%s is not valid URLs must start with http')
        return False
    try:
        with open(dest, 'wb') as f:
            f.write(urlopen(URL).read())
            return True
    except OSError:
        return False

def generate_filename(movie_path, movie_name, extn):
    return fjoin(movie_path, "%s.%s" % (movie_name, extn))  
        
def fn_to_parts(fn):
    (path, full_filename) = fn.rsplit('/', 1)
    (base_filename, file_ext) = full_filename.rsplit('.', 1)
    return (path, base_filename, file_ext)
    
def get_basepath(default_path):
    try:
        os.stat(default_path)
        basepath = default_path
    except SQLObjectNotFound:
        basepath = os.getcwd()
    
    return basepath