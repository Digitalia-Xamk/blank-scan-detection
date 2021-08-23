#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 10:49:59 2020

@author: digitalia-aj
"""

import cv2
import numpy as np


# get grayscale image
def get_grayscale(image):
    if len(image.shape)==3: #If exported is a color image, convert to gray            
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image
    

# noise removal
def BasicBlurring(image):
    return cv2.medianBlur(image,5)


def fastMeansDenoisingColored(image):
    denoised = cv2.fastNlMeansDenoisingColored(image)
    return denoised

def fastMeansDenoisingCray(image):
    image=get_grayscale(image)
    denoised = cv2.fastNlMeansDenoising(image)
    return denoised

def reduceColorNoise(image):
    """Reduces noise from color images
    Return denoised image
    """
    denoised = cv2.GaussianBlur(image, (3, 3), 0) 
    denoised = cv2.bilateralFilter(denoised, 9, 25, 25)
    
    return denoised

def reduceCrayNoise(image):
    """Reduces noise from grayscale images
    Return denoised image
    """
    denoised = cv2.fastNlMeansDenoising(image)        
    #Filtering unwanted noise
    denoised = cv2.GaussianBlur(denoised, (3, 3), 0) 
    denoised = cv2.bilateralFilter(denoised, 9, 25, 25)
    return denoised

#Lines removal
def removeLines(image):
    """Removes horizontal and vertical lines but also reduces text quality"""       
    # Remove horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25,1))
    remove_horizontal = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv2.findContours(remove_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(image, [c], -1, (255,255,255), 9)
    
    # Repair image
    repair_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,6))
    image = 255 - cv2.morphologyEx(255 - image, cv2.MORPH_CLOSE, repair_kernel, iterations=2)
    
    # Remove vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,25))
    remove_vertical = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(image, [c], -1, (255,255,255), 9)

    return image
 
#Contrast limiting histogram
def histogramEqualization(image):
    image = get_grayscale(image)
    return cv2.equalizeHist(image)

#clahe histogram, more accurate than the above
def claheHistogramEqualization(image):
    image = get_grayscale(image)
    clahe = cv2.createCLAHE(clipLimit=8, tileGridSize=(2,2))
    return clahe.apply(image)

#filtering mexican hat
def mexicanHat(image):
    # Creating maxican hat filter
    filter = np.array([[0,0,-1,0,0],[0,-1,-2,-1,0],[-1,-2,16,-2,-1],[0,-1,-2,-1,0],[0,0,-1,0,0]])
    # Applying cv2.filter2D function on our Cybertruck image
    return cv2.filter2D(image,-1,filter)

#thresholding
def binaryThreshold (image):
    image = get_grayscale(image)
    return cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)[1]

def Otsuthresholding(image):
    image = get_grayscale(image)    
    return cv2.threshold(image, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def adaptiveThreshold(image, x=19, y=19):
    print("start thresholding with {}-{}".format(x,y))
    image = get_grayscale(image)
    #return cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,x,y)
    return cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,x,y)

#dilation
def dilate(image):
    kernel = np.ones((3,3),np.uint8)
    return cv2.dilate(image, kernel, iterations = 2)

#Sharpening
def sharpen(image):
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    return cv2.filter2D(image, -1, kernel)    

#erosion
def erode(image):
    kernel = np.ones((3,3),np.uint8)
    return cv2.erode(image, kernel, iterations = 1)

#opening - erosion followed by dilation
def opening(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

#canny edge detection
def canny(image):
    return cv2.Canny(image, 100, 200)

#skew correction
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

#template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED) 