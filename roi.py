import cv2
import numpy as np
import math

debug = 0

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

def createSquere(first_defect_far,third_defect_far,midpoint):
    sizeOffset = 150
    posOffset = 7.5
    rotOffset = 0
    # Calculate the direction vector (dx, dy) of the line
    dx = third_defect_far[0] - first_defect_far[0]
    dy = third_defect_far[1] - first_defect_far[1]

    # Normalize the direction vector
    length = np.sqrt(dx**2 + dy**2)

    dx /= length
    dy /= length
    if dy < 0:
        dy = abs(dy)
        dx = abs(dx)
        rotOffset = 90
        posOffset = 4
    
    # Calculate the coordinates of the perpendicular line
    perpendicular = [int(midpoint[0] + 50 * dy),int(midpoint[1] - 50 * dx)]  # X,Y

    # Calculate the length of the side of the ROI square
    length = int(np.sqrt((third_defect_far[0] - first_defect_far[0])**2 + (third_defect_far[1] - first_defect_far[1])**2))
    length += sizeOffset

    # Calculate the coordinates of the square vertices
    square_vertices = [
        (perpendicular[0] , perpendicular[1]),
        (perpendicular[0] , perpendicular[1] - length),
        (perpendicular[0] + length , perpendicular[1] - length),
        (perpendicular[0] + length, perpendicular[1])
    ]

    # Ensure that midpoint contains integers
    midpoint = (int(midpoint[0]), int(midpoint[1]))

    # Calculate the angle of rotation
    angle = np.arctan2(-dy, dx) * 180 / np.pi
    angle = angle + rotOffset

    # Create a rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(midpoint, angle, scale=1)

    # Apply the rotation to the square vertices
    rotated_square_vertices = cv2.transform(np.array([square_vertices], dtype=np.float32), rotation_matrix).squeeze().astype(np.int32)

    # Calculate the new starting point for the square
    start_point = (first_defect_far[0] - rotated_square_vertices[0][0], first_defect_far[1] - rotated_square_vertices[0][1])
    # start_point = (int(start_point[0]- (sizeOffset/3)), int(start_point[1]- (sizeOffset/1.7)))

    # Translate the rotated square to the new starting point
    translated_square_vertices = rotated_square_vertices + start_point

    # Calculate the direction vector (dx_perpendicular, dy_perpendicular) of the perpendicular line
    d_perpendicular = [perpendicular[0] - midpoint[0], perpendicular[1] - midpoint[1]]  # X,Y

    # Normalize the direction vector
    length_perpendicular = np.sqrt(d_perpendicular[0]**2 + d_perpendicular[1]**2)
    d_perpendicular[0] /= length_perpendicular 
    d_perpendicular[1] /= length_perpendicular 

    # Calculate the translation vector along the perpendicular line
    translation_vector = (int((0)* d_perpendicular[0]), int((50 - (sizeOffset*posOffset)) * d_perpendicular[1]))

    # Translate the rotated and aligned square vertices
    return translated_square_vertices + translation_vector, perpendicular, length,


def main(image):
    # Load image
    image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # cropped_image = image[:, :image.shape[1] - 120]  # crop right side
    blurred = cv2.GaussianBlur(image, (5, 5), 0)  # gaussian blur
    _, thresholded = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)  # initial threshold

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

        first_defect_far, third_defect_far = far_points[0], far_points[2]

        # Calculate the midpoint of the line
        midpoint = ((first_defect_far[0] + third_defect_far[0]) // 2, (first_defect_far[1] + third_defect_far[1]) // 2)
        
        translated_along_perpendicular, perpendicular, length = createSquere(first_defect_far, third_defect_far, midpoint)
        
        if debug >= 3:
            cv2.line(image_with_contours_points, first_defect_far, third_defect_far, color=(0, 0, 255), thickness=2)            # Rote Linie
            # cv2.line(image_with_contours_points, midpoint, perpendicular, color=(0, 0, 255), thickness=2)                       # Rote Linie
            cv2.imwrite("roi.jpg",image_with_contours_points)
    
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
            rectified_image = cv2.rotate(rectified_image, cv2.ROTATE_90_CLOCKWISE)

        return rectified_image


if __name__ == "__main__":
    cv2.imwrite("roi.jpg",main(cv2.imread("capture_1.png", cv2.IMREAD_GRAYSCALE)))