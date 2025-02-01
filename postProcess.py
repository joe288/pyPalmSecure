import cv2
import numpy as np

# gray
ip_file = "preProcess.jpg"

def gray_scale(img):
    gray= cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray

# reduce noise in the image
def reduce_noise(img):
    # img = gray_scale(img)
    noise = cv2.fastNlMeansDenoising(img)
    return noise

# histogram equalization
def equalize_hist(img, kernel):
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
    return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

# invert a binary image
def invert(img):
    return cv2.bitwise_not(img)

# skeletonize the image
def skel(img):
    noise = reduce_noise(img)
    # noise = CLAHE(noise)
    noise = cv2.cvtColor(noise, cv2.COLOR_GRAY2BGR)
    
    kernel = np.ones((6,6),np.uint8)                            # kernel = np.ones((3,3),np.uint8)   
    img_output = equalize_hist(noise, kernel)                   # histogram equalization

    # cv2.imwrite("postProcess.jpg",img_output)

    inv = invert(img_output)                                    # invert a binary image
    
    img = gray_scale(inv)
    skel = img.copy()
    skel[:,:] = 0
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5,5))

    while True:
        eroded = cv2.morphologyEx(img, cv2.MORPH_ERODE, kernel)
        temp = cv2.morphologyEx(eroded, cv2.MORPH_DILATE, kernel)
        temp  = cv2.subtract(img, temp)
        skel = cv2.bitwise_or(skel, temp)
        img[:,:] = eroded[:,:]
        if cv2.countNonZero(img) == 0:
            break
    # draw_after_canvas(skel)
    
    skel = thresh(skel)
    # cv2.imwrite("postProcess1.jpg",skel)
    skel = invert(skel)
    # cv2.imwrite("postProcess2.jpg",skel)
    return skel
# threshold to make the veins more visible
def thresh(img):
    _, thr = cv2.threshold(img, 30,255, cv2.THRESH_BINARY)
    return thr

#CLAHE
def CLAHE(noise):
    clahe = cv2.createCLAHE(clipLimit=8.0, tileGridSize=(8,8))  #Define tile size and clip limit. 
    cl1 = clahe.apply(noise)
    return cl1

if __name__ == "__main__":
    cv2.imwrite("postProcess.jpg",skel(cv2.imread(ip_file, cv2.IMREAD_GRAYSCALE)))