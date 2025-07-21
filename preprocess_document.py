
import cv2
import numpy as np

def grayscale_and_sharpen(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 3)

    kernel = np.array([[0, -1, 0],
                      [-1, 5,-1],
                      [0, -1, 0]])
    sharpened = cv2.filter2D(blurred, -1, kernel)

    return sharpened

def preprocess_document(image):
    processed = grayscale_and_sharpen(image)
    binary = cv2.adaptiveThreshold(
      processed, 
      255,
      cv2.ADAPTIVE_THRESH_MEAN_C,
      cv2.THRESH_BINARY, 
      13, 
      14
    )
    return binary