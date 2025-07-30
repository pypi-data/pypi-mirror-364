import cv2
import numpy as np
from skimage import filters
from sklearn.cluster import KMeans



# === Trova piante filtrando il verde ===
def filter_plants(image, default_T=0, kernel_dimension=1, cut_iterations=1, save_mask=False):
    # Calcola l'EXG (Excess Green) per il rilevamento del verde (2G-B-R)
    r, g, b = cv2.split(image)
    exg = (2 * g.astype(np.int16) - r.astype(np.int16) - b.astype(np.int16)) 
    #gli = exg / (2 * g.astype(np.int16) + r.astype(np.int16) + b.astype(np.int16) + 0.001)

    # Filtra l'immagine per rimuovere il rumore
    T = filters.threshold_otsu(exg)
    if T < default_T:
        T = default_T

    print(f"Threshold: {T}") # DEBUG
    ColorSegmented = np.where(exg > T, 1, 0).astype(np.uint8)

    # Applica un filtro morfologico per rimuovere il rumore
    kernel = np.ones((kernel_dimension, kernel_dimension), np.uint8)
    erosion = cv2.erode(ColorSegmented, kernel, iterations=cut_iterations)
    dilation = cv2.dilate(erosion, kernel, iterations=cut_iterations)
    ColorSegmented = dilation

    # DEBUG: Applica la maschera all'immagine originale e la salva
    if save_mask:
        masked_image = cv2.bitwise_and(image, image, mask=ColorSegmented)
        cv2.imwrite("crop_sensing/data/excess_green.png", masked_image)

    # Ritorna la maschera del verde
    return ColorSegmented

def save_clustered_image(image, bounding_boxes):
    # Draw bounding boxes on the original image for visualization
    for (x_min, y_min, x_max, y_max) in bounding_boxes:
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    cv2.imwrite("crop_sensing/data/clusters.png", image)

def segment_plants(mask, n_plants):
    # Converti la maschera in coordinate 
    coords = np.column_stack(np.where(mask > 0))
    # KMeans clustering sulle coordinate
    kmeans = KMeans(n_clusters=n_plants, random_state=42)
    labels = kmeans.fit_predict(coords)
    # Crea maschere individuali
    masks = [np.zeros_like(mask, dtype=np.uint8) for _ in range(n_plants)]
    bounding_boxes = []

    for (y, x), label in zip(coords, labels):
        masks[label][y, x] = 1

    # Calculate 2D bounding boxes for each mask
    for i, plant_mask in enumerate(masks):
        ys, xs = np.where(plant_mask > 0)
        if len(xs) > 0 and len(ys) > 0:
            x_min, x_max = xs.min(), xs.max()
            y_min, y_max = ys.min(), ys.max()
            bounding_boxes.append((x_min, y_min, x_max, y_max))
        
    return masks, bounding_boxes

# === estrai la profondità dei punti del cluster ===
def extract_3d_points_from_mask(mask, point_cloud):
    ys, xs = np.where(mask > 0)
    points = []

    for x, y in zip(xs, ys):
        coords = point_cloud.get_data()[int(y), int(x)]
        if np.isfinite(coords).all():
            points.append(coords)

    return np.array(points)

# === Crea la bounding box 3D del cluster ===
def compute_bbox_3d(points):
    bbox_min = np.min(points, axis=0)
    bbox_max = np.max(points, axis=0)
    return bbox_min, bbox_max

# === Visualizza la bounding box 3D del cluster ===
def plot_3d_bbox(mask, point_cloud):
    
    # Estrai i punti 3D dalla maschera
    points = extract_3d_points_from_mask(mask, point_cloud)
    
    # Calcola la bounding box
    bbox_min, bbox_max = compute_bbox_3d(points)
    x0, y0, z0 = bbox_min[0], bbox_min[1], bbox_min[2]
    x1, y1, z1 = bbox_max[0], bbox_max[1], bbox_max[2]
    bbxpts = {
        "min": {"x": x0, "y": y0, "z": z0},
        "max": {"x": x1, "y": y1, "z": z1}
    }

    # DEBUG
    print(f"Bounding Box Min: {bbxpts['min']}, Bounding Box Max: {bbxpts['max']}")

    return bbxpts

