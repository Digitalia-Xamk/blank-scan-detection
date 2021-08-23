#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 09:21:50 2017

Cleaner module, moves files, renames, deletes folders etc.

@author: digitalia-aj
"""
import shutil
import os

"""
def stripFileName(beginfilename):
    beginfilenamestriped = beginfilename.replace(" ","_")
    if beginfilename != beginfilenamestriped:
        os.rename(beginfilename, beginfilenamestriped)
    return beginfilenamestriped
"""

def removeDir(dirname): #actual method that removes the folder
    try:
        print ("Trying to delete folder "+dirname)
        shutil.rmtree(dirname)
    except OSError:
        pass
    return

def createDir(dirname:str):
    """Creates a directory dirname if it does not exist """
    try:
        os.makedirs(dirname)
    except OSError as e:                
        pass
    return

def removeFile(root, filename): #actual method that remove files
    try:
        delfile = os.path.join(root, filename)
        print ("Trying to delete file -->%s "%delfile)
        os.remove(delfile)

    except OSError:
        pass
    return

def removeFileFullPath(path): #actual method that remove files
    try:        
        print ("Trying to delete file --> {}".format(path))
        os.remove(path)

    except OSError:
        pass
    return


def moveFileToUpperFolder(orgfile, fname, root):
    # move file to upper folder    
    destPath = root.rsplit('/', 1)[0]
    #print("POLUT "+str(destPath)+" "+str(orgfile))
    os.rename(orgfile, destPath+"/"+fname)
    return

def copyFile (toBeCopiedFile: str, newLocation: str):
    """toBeCopiedFile = full path of the file to be copied, newLocation is just the folder"""
    try:
        shutil.copy(toBeCopiedFile, newLocation)
    except OSError:
        pass

def moveFile (toBeMovedFile: str, newLocation: str):
    """toBeMovedFile = full path of the file to be moved, newLocation is just the folder"""
    try:
        shutil.move(toBeMovedFile, newLocation)        
    except OSError:
        pass

def renameFile(origfile, renamedFile):
    print("Renaming:"+str(origfile)+" into "+str(renamedFile))
    os.replace(origfile, renamedFile)
    if os.path.isfile(renamedFile):
        return
   
