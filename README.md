# blank-scan-detection
This is a opensource based workflow created with Python which intends to recognize empty scans (no text) from those document pages that contains writing either by hand or by machine

Run with python ImageManipulationBasedRecognition.py -d /path-to/the-files/that-are-scanned/
Script seeks all image files inside the files and tries to identify the empty ones by utilizing openCV and Tesseract. These two applications needs to be installed before running the sciprt
