from django.core.files.storage import FileSystemStorage
from fsplit.filesplit import FileSplit
from django.shortcuts import render
from django.http import request
from .encrypt import *
from .decrypt import *
from secry.settings import *
import os
readsize = 1024


def split(file):
    fs = FileSystemStorage()
    filename = fs.save(file.name, file)
    source = os.path.join(MEDIA_ROOT,filename)
    dest = os.path.join(MEDIA_ROOT, 'temp/')
    chunks = (int)((file.size)/2)
    fs = FileSplit(source, chunks, dest)
    fs.split()
    os.remove(source)


def join(fromdir, tofile):
    output = open(tofile, 'wb')
    parts = os.listdir(fromdir)
    parts.sort()
    for filename in parts:
        filepath = os.path.join(fromdir, filename)
        fileobj = open(filepath, 'rb')
        while 1:
            filebytes = fileobj.read(readsize)
            if not filebytes:
                break
            output.write(filebytes)
        fileobj.close()
        os.remove(filepath)
    output.close()

def encypt(alnum, key, file_path, iv):
    if(alnum == 0):
        AES(key, file_path, iv)
    elif(alnum == 1):
        DES(key, file_path, iv)
    elif(alnum == 2):
        RC4(key, file_path, iv)

def decrypt(alnum, key, file_path, iv):
    if(alnum == 0):
        DAES(key, file_path, iv)
    elif(alnum == 1):
        DDES(key, file_path, iv)
    elif(alnum == 2):
        DRC4(key, file_path, iv)
