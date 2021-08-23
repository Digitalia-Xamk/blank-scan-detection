#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 12:07:09 2019

@author: digitalia-aj
"""

#import os
#import sys #For getting cli parameters during startup
import argparse
import cv2
import multiprocessing
import os
import sys
from multiprocessing import Pool
import numpy as np
#import re

from pythonHelperClasses import dirStructureCalculator
from pythonHelperClasses import timeManager
from pythonHelperClasses import fileOperations
from pythonHelperClasses import edgeCropper
from pythonHelperClasses import imageProcessor

#try with pyvips / cv2 was lot slower than PIL
try:        
    import PIL
    print("Pillow version {}".format(PIL.__version__))
    from PIL import Image    
except ImportError:
    import Image


import pytesseract


# Params
maxArea = 15000
minArea = 2


analyseContent = True
cropBorders = True
removeLines = True
deSkew = False
deleteTemps = False
doClahe = True

empties = ['',' ','  ']

def doCommandWithTime(cmd): #Not yet in use
    startTime = timeManager.getTimeNs()
    endTime = timeManager.getTimeNs()
    runtime = endTime-startTime
    times = timeManager.convertNStoHuman(runtime)

def removeTempFiles(tempFiles):
    for path in tempFiles:
        fileOperations.removeFileFullPath(path)


def doTesseract(image, path, round=1):
    try:
        oneImageTimeStart = timeManager.getTimeNs() 
        if round==1:        
            print("Round {} {}".format(round, path))
            fileOSD = pytesseract.image_to_osd(image, output_type='dict') #can output bytes, string, dict    
            #fileOSD = pytesseract.image_to_string(image, output_type='dict', timeout=30) #can output bytes, string, dict                
            fileOSD['tesseract'] = "not empty"
            print("{} osd = {}".format(path, fileOSD))
        else:
            tes_config = r'--oem 3 --psm 12' ##all possible text is found
            #fileOSD = pytesseract.image_to_string(image, output_type='dict', config=tes_config) #can output bytes, string, dict                        
            fileOSD = pytesseract.image_to_data(image, output_type='dict', config=tes_config) #can output bytes, string, dict   
            #allTexts = fileOSD['text']
            #print("Before reducing -->{}".format(allTexts))
            
    except Exception:        
        fileOSD = {}
        fileOSD['tesseract'] = "no result"
        pass
    
    oneImageTimeEnd = timeManager.getTimeNs()
    runtime = oneImageTimeEnd-oneImageTimeStart
    times = timeManager.convertNStoHuman(runtime)
    print("{} Image to osd: {}ms = {}s".format(path, times[0], times[1]))
    
    return fileOSD

"""
osd vs string vs box --> osd paljon nopeampi, tyhjillä ei tulosta, käsi --> japani
string ja box melkein samat ajat, kummallakaan ei tulosta tyhjästä
data vs string --> data nopeampi tyhjillä, muuten kuin string eli hidas
"""

def findPossibleEmpties(image, path, round=1):
    print("Finding empties round {}".format(round))
    """Takes cv2 img as first parameter and full path to the original file as second
    returns OSD info and the thresholded image in returnData list"""
    
    
    #Image to osd (orientation and script detection (latin, japanese, etc.))
    oneImageTimeStart = timeManager.getTimeNs()            
    try:
        #tes_config = r'--oem 3 --psm 12' ##all possible text is found
        #fileOSD = pytesseract.image_to_string(image, output_type='dict', config=tes_config) #can output bytes, string, dict                        
        fileOSD = pytesseract.image_to_data(image, output_type='dict') #can output bytes, string, dict                        
    except Exception:        
        fileOSD = {}
        pass
    fileOSD["path"] = path    
    #print("{}{}".format(len(fileOSD), fileOSD))   
    oneImageTimeEnd = timeManager.getTimeNs()
    runtime = oneImageTimeEnd-oneImageTimeStart
    times = timeManager.convertNStoHuman(runtime)
    print("{} Image to osd: {}ms = {}s".format(path, times[0], times[1]))
    allTexts = fileOSD['text']
    #print("Before reducing -->{}".format(allTexts))
    allTexts = list(filter(None, allTexts)) #filters out None/empty ones from the list       
    print("After blanks removal -->{}".format(allTexts))
    
    oneString = ""
    for onetext in allTexts:
        oneString+=onetext
    oneString = oneString.strip()

    if (len(oneString)==0): #Text is empty
        print("File {} probably empty".format(path)) 
        fileOSD['tesseract']="empty" 
        return fileOSD             
        
    else:            
        if(round>1):
            fileOSD['tesseract']="digEvenDeeper" 
            print("Second round completed and still content {}".format(path)) 
        else:
            print("First round recognized something in: {}".format(path))    
            #print("{}-->{}".format(path, fileOSD))
            #Is there text in image
            #fileOSD = pytesseract.image_to_string(image, output_type='dict') #can output bytes, string, dict          
            fileOSD['tesseract']="possibledata"
        return fileOSD
    #returnData.append(fileOSD)
    #returnData.append(image)
    

def handleOneImageFile(fileName: str, fullpath: str):    
    """Actual multiprocessing module, takes in the filename and it's path
    Called from from handleJPEGdirs"""    
    tempFiles = []
    fullJPEGpath = os.path.join(fullpath, fileName)    
    baseDir = os.path.dirname(fullJPEGpath)
    #emptyDir = str(baseDir)+"/lajiteltu/tyhjat/"
    nonemptyDir = str(baseDir)+"/lajiteltu/ei-tyhjat/"
    #oddDir = str(baseDir)+"/lajiteltu/oudot/"    
    
    #Image loading
    imageLoadStart = timeManager.getTimeNs()   
    org= cv2.imread(fullJPEGpath)
    #original = original.astype('uint8')
    if np.shape(org) == ():
        print("Image {} not good".format(fullJPEGpath))    

    imageLoadStop  = timeManager.getTimeNs()    
    runtime = imageLoadStop-imageLoadStart
    times = timeManager.convertNStoHuman(runtime)
    print("{} Image loading {}ms = {}s".format(fileName, times[0], times[1]))     
    
    #Cropping borders happens always first, get rid of disturbing borders
    imageCropStart = timeManager.getTimeNs()   
    imageCrop = edgeCropper.cropBorderSize(org, 45)
    #croppedOriginal = image.copy()
    cv2.imwrite(fullJPEGpath.split(".")[0]+"-1-cropped.jpg", imageCrop)    
    tempFiles.append(fullJPEGpath.split(".")[0]+"-1-cropped.jpg")
    imageCropStop  = timeManager.getTimeNs()    
    runtime = imageCropStop-imageCropStart
    times = timeManager.convertNStoHuman(runtime)
    print("{} - cropping: {}ms = {}s".format(fileName, times[0], times[1]))
    
    #fast denoising
    print("fast denoising")
    imageNR = imageProcessor.fastMeansDenoisingCray(imageCrop)
    cv2.imwrite(fullJPEGpath.split(".")[0]+"-2-fastdenoised.jpg", imageNR)
    tempFiles.append(fullJPEGpath.split(".")[0]+"-2-fastdenoised.jpg")
    
    #Threshholding - for finding more text data           
    imageThreshStart = timeManager.getTimeNs()
    #image = imageProcessor.Otsuthresholding(image) 
    image = imageProcessor.adaptiveThreshold(imageNR) #Otsu is faster 
    imageThreshStop  = timeManager.getTimeNs()    
    runtime = imageThreshStop-imageThreshStart
    cv2.imwrite(fullJPEGpath.split(".")[0]+"-3-thresholding.jpg", image)
    tempFiles.append(fullJPEGpath.split(".")[0]+"-3-thresholding.jpg")
    
    """
    #Lineremoval - for finding more text data, no help therefore commented    
    imageLineStart = timeManager.getTimeNs()
    image=imageProcessor.get_grayscale(image)
    image = imageProcessor.removeLines(image)    
    imageLineStop  = timeManager.getTimeNs()    
    runtime = imageLineStop-imageLineStart
    times = timeManager.convertNStoHuman(runtime)
    print("{} Image Line removal: {}ms = {}s".format(fullJPEGpath, times[0], times[1]))
    cv2.imwrite(fullJPEGpath.split(".")[0]+"-3-removedlines.jpg", image)
    """
    if doClahe: #Not used in processing but to show differences an image is produced
        #Clahe equalization
        imageHistogramStart = timeManager.getTimeNs()   
        clahe = imageProcessor.claheHistogramEqualization(imageNR)
        #croppedOriginal = image.copy()
        cv2.imwrite(fullJPEGpath.split(".")[0]+"-4-clahe-equalized.jpg", clahe)    
        #tempFiles.append(fullJPEGpath.split(".")[0]+"-1-cropped.jpg")
        imageHistogramStop  = timeManager.getTimeNs()    
        runtime = imageHistogramStop-imageHistogramStart
        times = timeManager.convertNStoHuman(runtime)
        print("{} - Clahe histogram: {}ms = {}s".format(fileName, times[0], times[1]))
        
    
    
    results = doTesseract(image, fullJPEGpath, round=1)
    if results['tesseract']=="not empty":
        print("Not empty {}".format(fileName))
        fileOperations.createDir(nonemptyDir)
        fileOperations.moveFile(fullJPEGpath, nonemptyDir)
        if deleteTemps:
            removeTempFiles(tempFiles)
    elif results['tesseract'] == "no result":
        print("No results from OSD {} --> Check deeper thresholded version of ".format(fileName))
        results = doTesseract(image, fullJPEGpath, 2)
        #allTexts = list(filter(None, results['text'])) #filters out None/empty ones from the list       
        #With the best detection settings all files "have" text, analyze the text lenght and confidences
        texts = results['text']
        conf = results['conf']
        i=0
        totalConf = 0
        highestConf = 0
        wordCounter = 0 #Words with confidence more than 0
        
        totalWordLenght = 0
        while i < len(texts):
            if int(conf[i])>0:
                print("{}-{}%".format(texts[i], conf[i]))
                totalConf+=int(conf[i])
                wordCounter+=1
                totalWordLenght+=len(texts[i])
                
                if len(texts[i])>4 and int(conf[i])>70: #If even one text lenght is 5 or more and it's confidence is more than 70 it's something else than noise
                    print("{}-{}".format(texts[i], conf[i]))        
                    print("Definitely not empty {}".format(fileName))
                    fileOperations.createDir(nonemptyDir)
                    fileOperations.moveFile(fullJPEGpath, nonemptyDir)
                    if deleteTemps:
                        removeTempFiles(tempFiles)
                if(highestConf<conf[i]):
                    highestConf=conf[i]
            i+=1
        
        print(fileName)
        print("Words : {}".format(wordCounter))
        try:
            print("Word confidence : {}".format(totalConf/wordCounter))
            print("Word avg lenght : {}".format(totalWordLenght/wordCounter)) 
        except ZeroDivisionError:
            print("Zero division, so file {} is most likely empty".format(fileName))            
            if deleteTemps:
                removeTempFiles(tempFiles)
            pass
        
        #case
        """
        Words : 20
        Word confidence : 39.6
        Word avg lenght : 2.35

        Words : 27
        Word confidence : 31.925925925925927
        Word avg lenght : 2.3333333333333335

        Words : 9
        Word confidence : 42.666666666666664
        Word avg lenght : 2.111111111111111

        """
        """
        if (wordCounter > 5):
            print("Probably not empty {}".format(fileName))
            fileOperations.createDir(nonemptyDir)
            fileOperations.moveFile(fullJPEGpath, nonemptyDir)
        elif(wordCounter>0 and highestConf>10):
            print("Probably not empty {}, highest conf {}".format(fileName, highestConf))
            fileOperations.createDir(nonemptyDir)
            fileOperations.moveFile(fullJPEGpath, nonemptyDir)
                
          """ 
        
        #OLD rules kept here, used if required later on
        if(wordCounter>35): #if this many words the conf must be over 2
            if (totalWordLenght/wordCounter>2):
                print("Probably not empty {}".format(fileName))
                fileOperations.createDir(nonemptyDir)
                fileOperations.moveFile(fullJPEGpath, nonemptyDir)
        
        elif (wordCounter>20 and wordCounter<=35):
            if (totalConf/wordCounter>20 and totalWordLenght/wordCounter>1.4):
                print("Probably not empty {}".format(fileName))
                fileOperations.createDir(nonemptyDir)
                fileOperations.moveFile(fullJPEGpath, nonemptyDir)
        
        elif (wordCounter>10 and wordCounter<=20):
            if (totalConf/wordCounter>30 and totalWordLenght/wordCounter>1.4):
                print("Probably not empty {}".format(fileName))
                fileOperations.createDir(nonemptyDir)
                fileOperations.moveFile(fullJPEGpath, nonemptyDir)
            elif (totalConf/wordCounter>25 and totalWordLenght/wordCounter>2.5):
                print("Probably not empty {}".format(fileName))
                fileOperations.createDir(nonemptyDir)
                fileOperations.moveFile(fullJPEGpath, nonemptyDir)
            
                
        elif(wordCounter>4 and wordCounter<=10):
            if (totalConf/wordCounter>30 and totalWordLenght/wordCounter>3):
                print("Probably not empty {}".format(fileName))
                fileOperations.createDir(nonemptyDir)
                fileOperations.moveFile(fullJPEGpath, nonemptyDir)
                
        elif(wordCounter>1 and wordCounter<=4):
            if (totalConf/wordCounter>40 and totalWordLenght/wordCounter>3):
                print("Probably not empty {}".format(fileName))
                fileOperations.createDir(nonemptyDir)
                fileOperations.moveFile(fullJPEGpath, nonemptyDir)
            
        elif (wordCounter == 1):
            if (totalConf/wordCounter>50 and totalWordLenght/wordCounter>4):
                print("Probably not empty {}".format(fileName))
                fileOperations.createDir(nonemptyDir)
                fileOperations.moveFile(fullJPEGpath, nonemptyDir)
                      
            
        if deleteTemps:
            removeTempFiles(tempFiles)
        
    
    return
    """
    #fast denoising
    print("fast denoising")
    image = imageProcessor.fastMeansDenoisingCray(image)
    doTesseract(image,fullJPEGpath)
    cv2.imwrite(fullJPEGpath.split(".")[0]+"-fastdenoised.jpg", image)   
    
        
    #Reduce noice from image        
    #Blur the image
    image = imageProcessor.BasicBlurring(image)
    imageDenoiseStart = timeManager.getTimeNs()
    image = imageProcessor.reduceCrayNoise(image)
    cv2.imwrite(fullJPEGpath.split(".")[0]+"-1_denoised.jpg", image)
    imageDenoiseStop = timeManager.getTimeNs()
    runtime = imageDenoiseStop-imageDenoiseStart
    times = timeManager.convertNStoHuman(runtime)
    print("{} Image denoising: {}ms = {}s".format(fileName, times[0], times[1])) 
    doTesseract(image,fullJPEGpath)
    """
    
    """
    #Histogram equalization
    imageHistogramStart = timeManager.getTimeNs()   
    image = imageProcessor.histogramEqualization(org)
    #croppedOriginal = image.copy()
    cv2.imwrite(fullJPEGpath.split(".")[0]+"-equalized.jpg", image)    
    #tempFiles.append(fullJPEGpath.split(".")[0]+"-1-cropped.jpg")
    imageHistogramStop  = timeManager.getTimeNs()    
    runtime = imageHistogramStop-imageHistogramStart
    times = timeManager.convertNStoHuman(runtime)
    print("{} Image Histogram: {}ms = {}s".format(fileName, times[0], times[1]))
    """
    
    
    """
    #Threshholding - for finding more text data           
    imageThreshStart = timeManager.getTimeNs()
    #image = imageProcessor.Otsuthresholding(image) 
    image = imageProcessor.adaptiveThreshold(image) #Otsu works better and faster
    imageThreshStop  = timeManager.getTimeNs()    
    runtime = imageThreshStop-imageThreshStart
    
    times = timeManager.convertNStoHuman(runtime)
    print("{} - thresholding: {}ms = {}s".format(fileName, times[0], times[1]))
    cv2.imwrite(fullJPEGpath.split(".")[0]+"-threshold.jpg", image)
    """
    #fileOSD={}

    
    """
    
    fileOSD = findPossibleEmpties(image, fullJPEGpath) #FileOSD is the first and image the second return value
        #print("Return from empty detection round 1")
    
    if (fileOSD['tesseract']=='empty'):
        print("Going empty {}".format(fileName))
        fileOperations.createDir(emptyDir)
        fileOperations.moveFile(fullJPEGpath, emptyDir)
     
    elif (fileOSD['tesseract']=="digEvenDeeper" ):
        print("Continue..{}".format(fileName))
    
    elif (fileOSD['tesseract']=="possibledata"):
        print("Tesseract found some 'text' {}".format(fileOSD['text']))
        
    """
    """
    confidences = fileOSD['conf']
    texts = fileOSD['text']
    minusConfsCount = 0;
    actualConfsCount = 0;
    totalConf = 0;
    for x in range(len(confidences)):            
        if (confidences[x]=="-1"):
            minusConfsCount+=1
        else:
            actualConfsCount+=1
            totalConf+=confidences[x]
    
    print(fileName)
    print("Words ; minusconfs ; percentage")
    print("{} ; {} ; {}%".format(len(confidences), minusConfsCount, round(minusConfsCount/len(confidences)*100)))
    print("wordconfs ; Average")
    print("{} ; {}%".format(actualConfsCount, totalConf/actualConfsCount))
    """
    #image=dataList[1] #No need to do things again since thresholding already done.
    #cv2.imwrite(fullJPEGpath.split(".")[0]+"-2_thresh.jpg", image)
    #tempFiles.append(fullJPEGpath.split(".")[0]+"-2_thresh.jpg")
    """
    #Threshholding - for finding more text data           
    imageThreshStart = timeManager.getTimeNs()
    image = imageProcessor.adaptiveThreshold(image) 
    imageThreshStop  = timeManager.getTimeNs()    
    runtime = imageThreshStop-imageThreshStart
    times = timeManager.convertNStoHuman(runtime)
    print("{} Image thresholding: {}ms = {}s".format(path, times[0], times[1]))
    cv2.imwrite(path.split(".")[0]+"-2-threshold.jpg", image)
    
    #Lineremoval - for finding more text data    
    imageLineStart = timeManager.getTimeNs()
    image=imageProcessor.get_grayscale(image)
    image = imageProcessor.removeLines(image)    
    imageLineStop  = timeManager.getTimeNs()    
    runtime = imageLineStop-imageLineStart
    times = timeManager.convertNStoHuman(runtime)
    print("{} Image Line removal: {}ms = {}s".format(path, times[0], times[1]))
    cv2.imwrite(path.split(".")[0]+"-3-removedlines.jpg", image)
    """
    
    
    """
    #Fast means denoising
    imageStart = timeManager.getTimeNs()   
    image = imageProcessor.fastMeansDenoising(image)
    #croppedOriginal = image.copy()
    cv2.imwrite(fullJPEGpath.split(".")[0]+"-_fastdenoised.jpg", image)    
    tempFiles.append(fullJPEGpath.split(".")[0]+"-_fastdenoised.jpg")
    imageStop  = timeManager.getTimeNs()    
    runtime = imageStop-imageStart
    times = timeManager.convertNStoHuman(runtime)
    print("{} Image fast denoising: {}ms = {}s".format(fileName, times[0], times[1]))  
    """
    
    
    
    
    """
    dataContent = pytesseract.image_to_data(image, output_type='dict')
    confidences = dataContent['conf']
    texts = dataContent['text']
    minusConfsCount = 0;
    actualConfsCount = 0;
    totalConf = 0;
    for x in range(len(confidences)):            
        if (confidences[x]=="-1"):
            minusConfsCount+=1
        else:
            actualConfsCount+=1
            totalConf+=confidences[x]
            
    print(fileName)
    print("Words ; minusconfs ; percentage")
    print("{} ; {} ; {}%".format(len(confidences), minusConfsCount, round(minusConfsCount/len(confidences)*100)))
    print("wordconfs ; Average")
    print("{} ; {}%".format(actualConfsCount, totalConf/actualConfsCount))
    print(confidences)
    print(texts)
    """
    """
    if fileOSD['tesseract'=="digEvenDeeper"]:
    
        print("DeepChecking {}".format(fileName))
        #Possible text found, dig deeper and modify image
        
        #imfile = Image.open(fullJPEGpath)       
        """
    
    """
        #Sharpening the image
        imageSharpeningStart = timeManager.getTimeNs()
        imageProcessor.sharpen(cropped_color)
        cv2.imwrite(os.path.join(fullpath,fileName+"-2_sharpened.jpg"), sharpened)
        imageSharpeningStop = timeManager.getTimeNs()
        runtime = imageSharpeningStop-imageSharpeningStart
        times = timeManager.convertNStoHuman(runtime)
        print("{} Image sharpening: {}ms = {}s".format(fileName, times[0], times[1]))
        """
    """    
        #Reduce noice from image        
        imageDenoiseStart = timeManager.getTimeNs()
        image = imageProcessor.reduceColorNoise(image)
        cv2.imwrite(os.path.join(fullpath,fileName+"-1-5_denoised.jpg"), image)
        imageDenoiseStop = timeManager.getTimeNs()
        runtime = imageDenoiseStop-imageDenoiseStart
        times = timeManager.convertNStoHuman(runtime)
        print("{} Image denoising: {}ms = {}s".format(fileName, times[0], times[1]))
        """
        
       
    """       
        if removeLines: 
            image = imageProcessor.removeLines(image)        
            cv2.imwrite(fullJPEGpath.split(".")[0]+"-3_linesremoved.jpg", image)
        
        if deSkew:
            image = imageProcessor.deskew(image)
            cv2.imwrite(fullJPEGpath.split(".")[0]+"-4_deskewed.jpg", image)
        print("before test")
        
        altered = cv2.imread(fullJPEGpath.split(".")[0]+"-3_linesremoved.jpg")
        print("test {}".format(altered.size))
        try:            
            #print(pytesseract.image_to_data(Image.open(fullJPEGpath.split(".")[0]+"-3_linesremoved.jpg")))
            afterlinesRemoval = pytesseract.image_to_string(altered)
            print(len(afterlinesRemoval))
            if(len(afterlinesRemoval)<3):
               print("After checking {} seems to be empty".format(fullJPEGpath))
               fileOSD['tesseract']=="empty"
               #fileOperations.createDir(emptyDir)
               #fileOperations.moveFile(fullJPEGpath, emptyDir) 
               #fileOperations.removeFileFullPath(fullJPEGpath.split(".")[0]+"-3_linesremoved.jpg")
            
        except Exception:        
            print("exception occured {}".format(fullJPEGpath))            
            pass
        """
          
        
    """  
    
    if fileOSD['tesseract']=="possibledataXXX":
        #Image to data
        oneImageTimeStart = timeManager.getTimeNs()            
        #dataContent = pytesseract.image_to_data(original, output_type='dict')
        oneImageTimeEnd = timeManager.getTimeNs()
        runtime = oneImageTimeEnd-oneImageTimeStart
        times = timeManager.convertNStoHuman(runtime)
        #print("{} Image to data: {}ms = {}s".format(fileName, times[0], times[1]))
        #print(dataContent)
    """      
    
    
    """
    #image to string
    oneImageTimeStart = timeManager.getTimeNs()            
    pytesseract.image_to_string(imfile)
    oneImageTimeEnd = timeManager.getTimeNs()
    runtime = oneImageTimeEnd-oneImageTimeStart
    times = timeManager.convertNStoHuman(runtime)
    print("{} Image to string: {}ms = {}s".format(fileName, times[0], times[1]))
    
    #Image to data
    oneImageTimeStart = timeManager.getTimeNs()            
    pytesseract.image_to_data(imfile)
    oneImageTimeEnd = timeManager.getTimeNs()
    runtime = oneImageTimeEnd-oneImageTimeStart
    times = timeManager.convertNStoHuman(runtime)
    print("{} Image to data: {}ms = {}s".format(fileName, times[0], times[1]))
        
    # Get bounding box estimates
    oneImageTimeStart = timeManager.getTimeNs() 
    pytesseract.image_to_boxes(imfile)
    oneImageTimeEnd = timeManager.getTimeNs()
    runtime = oneImageTimeEnd-oneImageTimeStart
    times = timeManager.convertNStoHuman(runtime)
    print("{} Image to Box: {}ms = {}s".format(fileName, times[0], times[1]))
    """
    
    #print(pytesseract.image_to_data(Image.open(fullJPEGpath)))
    
    #timeout=2.5 lang='fra'
    #pytesseract.image_to_data #gets boxes, confidences, line and page numbers
    #hocr = pytesseract.image_to_pdf_or_hocr('test.png', extension='hocr')
    """
    # Example of adding any additional options.
    custom_oem_psm_config = r'--oem 3 --psm 6'
    pytesseract.image_to_string(image, config=custom_oem_psm_config)
    """

def handleJPEGdirs(path: str, fileCount: int):
    """Gets a path and filecount inside the given path, handless multiprocessing.
    This method should be called from the main app"""        
    allFiles = os.listdir(path)
    for onefile in allFiles:        
        pool.apply_async(handleOneImageFile, args=(onefile, path),)
        #handleOneImageFile(onefile, path)
        
    


if __name__ == "__main__":                   
    cpucount = multiprocessing.cpu_count()
    pool = Pool(cpucount)
    print("Usable CPUs: {}".format(cpucount))
    print ("PYTHON VERSION: {}".format(sys.version_info))    
    
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--dir", required=True, help="Path to browse")
    args = vars(ap.parse_args())
    pathName  = args["dir"]
    
    csvstartTime = timeManager.getTimeNs()
    print(pathName);
    content = dirStructureCalculator.generateStructureCSV(pathName);
    print("Content {}".format(content))
    jpegdirs = {} #This will be used later on to browse jpegs
    
    f = open("sample.csv", "w")
    csvContent = ""
    for key in content:
        print(key)
        csvContent+="{},{}\n".format(key, content[key])
        if(content[key])>0:
        #if key.endswith("jpeg"):
            jpegdirs[os.path.join(pathName, key)] = content[key] #Write found jpegs dirs to dictionary
            #print("Originals in {}".format(key))
    f.write(csvContent)
    f.close()
    
    csvendTime = timeManager.getTimeNs()
    runtime = csvendTime-csvstartTime    
    times = timeManager.convertNStoHuman(runtime)
    print("CSV creation: {}ms = {}s".format(times[0], times[1]))
   
    #Browse jpegdirs dictionary content and pass items to multiprocessing unit
    analyseStart = timeManager.getTimeNs()
    if analyseContent:
        for key in jpegdirs:                
            handleJPEGdirs(key, jpegdirs[key])
            
        
    pool.close()
    pool.join()
    analyseStop = timeManager.getTimeNs()    
    runtime = analyseStop-analyseStart    
    times = timeManager.convertNStoHuman(runtime)
    print("Analysis & sorting took: {}ms = {}s".format(times[0], times[1]))
    print("Move rest of the files to empty dirs")
    for key in jpegdirs:                
        print("Handling empties in dir {}".format(key))
        emptyDir = str(key)+"/lajiteltu/tyhjat/"
        remainingFiles = os.listdir(key)
        for onefile in remainingFiles:
            print(os.path.join(key,onefile))
            if os.path.isfile(os.path.join(key, onefile)):
                fileOperations.createDir(emptyDir)
                fileOperations.moveFile(os.path.join(key, onefile), emptyDir)
        #handleJPEGdirs(key, jpegdirs[key])
    """
    #Moves the remaining files to empty dir
    
    if deleteTemps:
        removeTempFiles(tempFiles)
    """
    
    
    