#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 08:29:43 2020

@author: digitalia-aj
"""

import numpy as np

def autocropThreshold(image, threshold=0):
    """Crops any edges below or equal to threshold
    0 is black and 255 is white
    Crops blank image to 1x1.
    Returns cropped image.
    """
    print("Cropping..")
    try:        
        rows = np.where(np.max(image, 0) > threshold)[0]
        if rows.size:
            cols = np.where(np.max(image, 1) > threshold)[0]
            image = image[cols[0]: cols[-1] + 1, rows[0]: rows[-1] + 1]
        else:
            image = image[:1, :1]
    except Exception as e:
        print(e)
        
    
    return image
    

def cropBorderSize(image, borderSize=5):
    """Crops border size of definition, default = 5    
    Returns cropped image.
    """   
    image = image[borderSize:-borderSize, borderSize:-borderSize]    
    
    return image

def cropEdges(image, borderSize = 5, threshold = 10):    
    try:        
        rows = np.where(np.max(image, 0) > threshold)[0]
        if rows.size:
            cols = np.where(np.max(image, 1) > threshold)[0]
            image = image[cols[0]: cols[-1] + 1, rows[0]: rows[-1] + 1]
        else:
            image = image[:1, :1]
    except Exception as e:
        print(e)
        pass
    image = image[borderSize:-borderSize, borderSize:-borderSize]
    return image