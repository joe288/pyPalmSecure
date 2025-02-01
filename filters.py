import numpy as np
import cv2
from skimage import filters

def main(image):

    # Frangi-Filter anwenden
    frangi_image = filters.frangi(image)

    # Skaliere das Bild auf den Bereich [0, 255] und konvertiere es in uint8
    frangi_image_uint8 = (frangi_image * 255).astype(np.uint8)
    
    # skimage.filters.frangi(image, sigmas=range(1, 10, 2), scale_range=None, scale_step=None, alpha=0.5, beta=0.5, gamma=None, black_ridges=True, mode='reflect', cval=0)

    # Speichere das Bild mit OpenCV
    return frangi_image_uint8

if __name__ == "__main__":
    cv2.imwrite('frangi_bild.jpg',main(cv2.imread('postProcess2.jpg'), cv2.IMREAD_GRAYSCALE))