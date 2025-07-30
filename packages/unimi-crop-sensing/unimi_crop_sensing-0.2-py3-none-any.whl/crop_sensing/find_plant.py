import cv2
import numpy as np
from skimage import filters
from sklearn.cluster import KMeans
import pyzed.sl as sl



# === Trova piante filtrando il verde ===
def filter_plants(image, kernel_dimension=1, cut_iterations=1):
    # Calcola l'EXG (Excess Green) per il rilevamento del verde (2G-B-R)
    r, g, b = cv2.split(image)
    exg = (2 * g.astype(np.int16) - r.astype(np.int16) - b.astype(np.int16)) 
    #gli = exg / (2 * g.astype(np.int16) + r.astype(np.int16) + b.astype(np.int16) + 0.001)
    # Filtra l'immagine per rimuovere il rumore
    T = filters.threshold_otsu(exg)
    print(f"Threshold: {T}") # DEBUG
    ColorSegmented = np.where(exg > T, 1, 0).astype(np.uint8)
    # Applica un filtro morfologico per rimuovere il rumore
    kernel = np.ones((kernel_dimension, kernel_dimension), np.uint8)
    erosion = cv2.erode(ColorSegmented, kernel, iterations=cut_iterations)
    dilation = cv2.dilate(erosion, kernel, iterations=cut_iterations)
    ColorSegmented = dilation
    # DEBUG: Applica la maschera all'immagine originale e la salva
    masked_image = cv2.bitwise_and(image, image, mask=ColorSegmented)
    cv2.imwrite("crop_sensing/data/excess_green.png", masked_image)
    # Ritorna la maschera del verde
    return ColorSegmented

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

# === Crea una lista di punti lungo una linea tra due punti ===
def generate_line_points(p1, p2, num_points=50, color=(255, 0, 0)):
    p1 = np.array(p1)
    p2 = np.array(p2)
    return [(*(p1 + t * (p2 - p1)), *color) for t in np.linspace(0, 1, num_points)]


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
    corners = np.array([
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]
    ])    
    edges = [
        (0,1), (1,3), (3,2), (2,0), 
        (4,5), (5,7), (7,6), (6,4),  
        (0,4), (1,5), (2,6), (3,7)  
    ]
    
    # Crea punti rossi lungo le linee della bbox 
    red_lines = []
    for i, j in edges:
        red_lines.extend(generate_line_points(corners[i], corners[j], num_points=30))

    # Crea un oggetto PointCloud per salvare i dati 
    point_cloud_with_bbox = sl.Mat(point_cloud.get_width(), point_cloud.get_height(), sl.MAT_TYPE.F32_C4)
    point_cloud_with_bbox.set_from(point_cloud)

    # Aggiungi i punti rossi al point cloud DA FIXXARE  
    for x, y, z, r, g, b in red_lines:
        if 0 <= int(x) < point_cloud_with_bbox.get_width() and 0 <= int(y) < point_cloud_with_bbox.get_height():
            point_cloud_with_bbox.set_value(int(x), int(y), [x, y, z, r / 255.0, g / 255.0, b / 255.0])

    # Salva il point cloud con la bounding box come file PLY
    point_cloud_with_bbox.write("crop_sensing/data/point_cloud_with_bbox.ply")
    # FINE DEBUG

    return bbxpts

