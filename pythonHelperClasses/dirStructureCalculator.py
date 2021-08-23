#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 12:07:09 2019

@author: digitalia-aj
"""

#import subprocess #For calling cli methods
import os


def generateStructureCSV(myPath: str):
    """"Reads the given full path and returns a dictionary containing 
        {directorypath: number of items} """
    content = {}
    print("start {}".format(myPath))
    for(root, dirs, files) in os.walk(myPath):            
        for onedir in dirs:            
            oneFullDir = os.path.join(root,onedir)
            print("full path {}".format(oneFullDir))
            fullDirContentCount = len(os.listdir(oneFullDir))
            print(fullDirContentCount)            
            print("Remove {} from {}, result {}".format(myPath, oneFullDir, oneFullDir.replace(str(myPath),"")))
            content[oneFullDir] = fullDirContentCount            
    return content;
            

 