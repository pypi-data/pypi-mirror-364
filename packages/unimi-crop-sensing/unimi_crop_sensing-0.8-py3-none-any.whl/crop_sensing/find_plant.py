import cv2
import numpy as np
from skimage import filters
from sklearn.cluster import KMeans



# === Filter plants using the excess green filter ===
def filter_plants(image, default_T=0, kernel_dimension=1, cut_iterations=1, save_mask=False):
    """
    This function detects green areas (typically vegetation or plants) in an RGB image
    by calculating the ExG index (2G - R - B), applying a threshold, and performing
    morphological operations to clean up noise. Optionally, it saves a masked image

    Args:
        image (np.ndarray): Input RGB image as a NumPy array.
        default_T (int, optional): Minimum threshold to enforce if Otsu's method returns a lower value. Default is 0
        kernel_dimension (int, optional): Size of the square kernel used in morphological operations. Default is 1
        cut_iterations (int, optional): Number of erosion and dilation iterations to apply. Default is 1
        save_mask (bool, optional): If True, saves the masked RGB image to `crop_sensing/data/excess_green.png`. Default is False

    Returns:
        np.ndarray: A mask where only the green areas from the input image are retained
    """
    # Calculate the EXG (Excess Green) for green detection (2G-B-R)
    r, g, b = cv2.split(image)
    exg = (2 * g.astype(np.int16) - r.astype(np.int16) - b.astype(np.int16)) 
    #gli = exg / (2 * g.astype(np.int16) + r.astype(np.int16) + b.astype(np.int16) + 0.001)

    # Filters the image using a threshold
    T = filters.threshold_otsu(exg)
    if T < default_T:
        T = default_T
    print(f"Threshold: {T}") # DEBUG
    ColorSegmented = np.where(exg > T, 1, 0).astype(np.uint8)

    # Apply a morphological operation to clean the mask
    kernel = np.ones((kernel_dimension, kernel_dimension), np.uint8)
    erosion = cv2.erode(ColorSegmented, kernel, iterations=cut_iterations)
    dilation = cv2.dilate(erosion, kernel, iterations=cut_iterations)
    ColorSegmented = dilation

    # DEBUG: Apply the mask to the original image and save it
    if save_mask:
        masked_image = cv2.bitwise_and(image, image, mask=ColorSegmented)
        cv2.imwrite("crop_sensing/data/excess_green.png", masked_image)

    return ColorSegmented

# === Saves the clustered image with bounding boxes ===
def save_clustered_image(image, bounding_boxes):
    # Draw bounding boxes on the original image for visualization
    for (x_min, y_min, x_max, y_max) in bounding_boxes:
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    cv2.imwrite("crop_sensing/data/clusters.png", image)

# === Segment plants using KMeans clustering ===
def segment_plants(mask, n_plants):
    """
    Given a binary mask where plants are indicated by non-zero pixels, this function clusters
    the pixel coordinates into `n_plants` groups and returns separate masks and bounding boxes
    for each plant cluster

    Args:
        mask (np.ndarray): Binary mask where plant pixels have values > 0
        n_plants (int): Number of individual plants (clusters) to segment

    Returns:
        tuple: A tuple containing:
            - masks (list of np.ndarray): List of binary masks, one per plant cluster
            - bounding_boxes (list of tuples): List of 2D bounding boxes for each cluster,
              each as (x_min, y_min, x_max, y_max)
    """
    # Converts the mask to coordinates for clustering
    coords = np.column_stack(np.where(mask > 0))
    # KMeans clustering on the coordinates
    kmeans = KMeans(n_clusters=n_plants, random_state=42)
    labels = kmeans.fit_predict(coords)
    # Create masks for each cluster
    masks = [np.zeros_like(mask, dtype=np.uint8) for _ in range(n_plants)]
    bounding_boxes = []

    for (y, x), label in zip(coords, labels):
        masks[label][y, x] = 1

    # Calculate 2D bounding boxes for each mask
    for plant_mask in enumerate(masks):
        ys, xs = np.where(plant_mask > 0)
        if len(xs) > 0 and len(ys) > 0:
            x_min, x_max = xs.min(), xs.max()
            y_min, y_max = ys.min(), ys.max()
            bounding_boxes.append((x_min, y_min, x_max, y_max))
        
    return masks, bounding_boxes

# === extract 3D points from the mask using the point cloud ===
def extract_3d_points_from_mask(mask, point_cloud):
    ys, xs = np.where(mask > 0)
    points = []

    for x, y in zip(xs, ys):
        coords = point_cloud.get_data()[int(y), int(x)]
        if np.isfinite(coords).all():
            points.append(coords)

    return np.array(points)

# === Create a 3D bounding box from the mask and point cloud ===
def plot_3d_bbox(mask, point_cloud):
    """
    Computes the 3D bounding box coordinates for a segmented region defined by a binary mask
    using the corresponding point cloud data.

    Args:
        mask (np.ndarray): Binary mask (2D) indicating the region of interest.
        point_cloud (sl.Mat): 3D point cloud data aligned with the mask.

    Returns:
        dict: A dictionary containing the minimum and maximum coordinates of the bounding box:
            {
                "min": {"x": x_min, "y": y_min, "z": z_min},
                "max": {"x": x_max, "y": y_max, "z": z_max}
            }
    """
    # Extract 3D points from the mask using the point cloud
    points = extract_3d_points_from_mask(mask, point_cloud)
    
    # Find the edges of the 3D bounding box
    bbox_min = np.min(points, axis=0)
    bbox_max = np.max(points, axis=0)
    x0, y0, z0 = bbox_min[0], bbox_min[1], bbox_min[2]
    x1, y1, z1 = bbox_max[0], bbox_max[1], bbox_max[2]

    bbxpts = {
        "min": {"x": x0, "y": y0, "z": z0},
        "max": {"x": x1, "y": y1, "z": z1}
    }

    # DEBUG: Print the bounding box coordinates
    print(f"Bounding Box Min: {bbxpts['min']}, Bounding Box Max: {bbxpts['max']}")

    return bbxpts

