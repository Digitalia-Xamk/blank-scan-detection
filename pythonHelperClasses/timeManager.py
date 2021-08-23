#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 12:07:09 2019

@author: digitalia-aj
"""

#import subprocess #For calling cli methods
#import os
import time

def getTimeNs():
    return time.time_ns()
    
    
def convertNStoHuman(nanoseconds: int):
    """Converts nanoseconds (int) into milliseconds and seconds, returns and Array [millisecods, seconds]"""
    microseconds = nanoseconds/1000
    milliseconds = microseconds/1000
    seconds = milliseconds/1000
    times =[milliseconds, seconds]       
    return times

 