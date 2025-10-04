import cv2
import numpy as np
import math

debug = 10

def findContours(thresholded):
    # Find the largest contours in the thresholded image
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return max(contours, key=cv2.contourArea)

def findDefects(largest_contour):
    # Calculate convexity defects
    hull = cv2.convexHull(largest_contour, returnPoints=False)
    defects = cv2.convexityDefects(largest_contour, hull)

    # Sort defects based on depth
    return sorted(defects, key=lambda x: x[0, 3], reverse=True)

def calculateDistanceLength(pointA, pointB):
    x1, y1 = pointA
    x2, y2 = pointB
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance

def findFingers(largest_contour,defects):
    leftHand = True
    far_points = [tuple(largest_contour[defects[i][0][2]][0]) for i in range(4)]
    far_points = sorted(far_points, key=lambda point: point[1])  # Sort by y-coordinate

    lenthPoint_0_1 = calculateDistanceLength(far_points[0],far_points[1])       
    lenthPoint_2_3 = calculateDistanceLength(far_points[2],far_points[3])
    
    if lenthPoint_0_1 > lenthPoint_2_3:                                                         #right hand side
        far_points = far_points = sorted(far_points, reverse=True ,key=lambda point: point[1])
        leftHand = False

    return far_points, leftHand

def createSquere(far_Point):
    sizePic = 330
    
    # Punkte entpacken
    p0, p1, p2, p3 = far_Point
    
   # Richtung von p0 -> p2 (linke Kante)
    dx = p2[0] - p0[0]
    dy = p2[1] - p0[1]
    dir_vec = np.array([dx, dy], dtype=np.float32)
    dir_vec /= np.linalg.norm(dir_vec)

    offset_x = sizePic/2 - 30
    
    # Senkrechter Vektor (für obere Kante)
    if dy < 0: # linke hand
        dir_vec = -dir_vec  #horizontal spiegeln  
        offset_y = -(sizePic/2) +20
    else: 
        offset_y = -(sizePic/2) -20

    perp = np.array([dir_vec[1], -dir_vec[0]], dtype=np.float32)
    
       # Mittelpunkt von P0–P2
    p0 = np.array(p0, dtype=np.float32)
    p2 = np.array(p2, dtype=np.float32)
    mid = (p0 + p2) / 2.0
    
    # Offset in lokalen Achsen anwenden
    mid = mid + offset_x * perp + offset_y * dir_vec

    # Rechteck-Ecken (um den Mittelpunkt herum)
    top_left     = mid - (sizePic/2) * perp
    top_right    = mid + (sizePic/2) * perp
    bottom_right = top_right + sizePic * dir_vec
    bottom_left  = top_left + sizePic * dir_vec
    
    rect = np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.int32)
    return rect, sizePic

def main(image):
    # Load image
    image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # cropped_image = image[:, :image.shape[1] - 120]  # crop right side
    blurred = cv2.GaussianBlur(image, (5, 5), 0)  # gaussian blur
    _, thresholded = cv2.threshold(blurred, 75, 255, cv2.THRESH_BINARY)  # initial threshold
    # cv2.imwrite("roi.jpg",thresholded)
    largest_contour = findContours(thresholded)

    if debug >=1:
        # Create an image for drawing contours
        image_with_contours = np.copy(image)

        # Draw the largest contour on the image_with_contours
        cv2.drawContours(image_with_contours, [largest_contour], -1, (255, 255, 255), 1)
        cv2.imwrite("roi.jpg",image_with_contours)

    defects = findDefects(largest_contour)

    # Choose the far points with the lowest and third lowest y-coordinates
    if len(defects) >= 4:

        far_points, leftHand = findFingers(largest_contour,defects)

        if debug >= 2:
            #paint defekt
            image_with_contours_points = cv2.cvtColor(image_with_contours, cv2.COLOR_BAYER_GR2BGR)
            cv2.circle(image_with_contours_points, far_points[0], radius=5, color=(0, 255, 0), thickness=-1)  # Grüner Punkt
            cv2.circle(image_with_contours_points, far_points[1], radius=5, color=(255, 0, 0), thickness=-1)  # Blauer Punkt
            cv2.circle(image_with_contours_points, far_points[2], radius=5, color=(0, 255, 0), thickness=-1)  # Grüner Punkt
            cv2.circle(image_with_contours_points, far_points[3], radius=5, color=(255, 0, 0), thickness=-1)  # Blauer Punkt
            cv2.imwrite("roi.jpg",image_with_contours_points)

        if debug >= 3:
            cv2.line(image_with_contours_points, far_points[0], far_points[2], color=(0, 0, 255), thickness=2)            # Rote Linie
            cv2.imwrite("roi.jpg",image_with_contours_points)
          
        translated_along_perpendicular, length = createSquere(far_points)
        
        if debug >= 4:
            for i in range(len(translated_along_perpendicular)):
                nextp = (i + 1) % len(translated_along_perpendicular)                                                        # modulo für den letzten Punkt
                cv2.line(image_with_contours_points, translated_along_perpendicular[i], translated_along_perpendicular[nextp], color=(0, 255, 0), thickness=2)  

            cv2.imwrite("roi.jpg",image_with_contours_points)
        
        # Convert the lists to NumPy arrays
        translated_along_perpendicular = np.array(translated_along_perpendicular, dtype=np.float32)
        
        # Ensure a consistent order of points for perspective transformation
        rectified_order = np.array([[0, 0], [length, 0], [length, length], [0, length]], dtype=np.float32)

        # Perform a perspective transformation to rectify the rotated square to a rectangle
        transform_matrix = cv2.getPerspectiveTransform(translated_along_perpendicular, rectified_order)
        rectified_image = cv2.warpPerspective(image, transform_matrix, (length, length))
 
        if leftHand:
            rectified_image = cv2.rotate(rectified_image, cv2.ROTATE_180)

        return rectified_image
        # return image_with_contours_points


if __name__ == "__main__":
    import os

    folder = "samples"
    for file in os.listdir(folder):
        destPath    = os.path.join(folder,file)
        targetPath  = os.path.join(folder,"roi",file)
        if os.path.isfile(destPath):
            cv2.imwrite(targetPath,main(cv2.imread(destPath, cv2.IMREAD_GRAYSCALE)))