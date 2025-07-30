import pyzed.sl as sl
import numpy as np
import cv2

### Questo file si occupa di interagire con la camera ###

# === Inizializza ZED ===
def zed_init(pose):
    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.depth_mode = sl.DEPTH_MODE.NEURAL_PLUS
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP 
    init_params.depth_maximum_distance = 2
    init_params.depth_minimum_distance = 0.2

    init_params.coordinate_units = sl.UNIT.METER
    if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
        print("Impossibile aprire la ZED")
        exit(1)
    
    translation = sl.Translation(pose.position.x, pose.position.y, pose.position.z)
    orientation = sl.Orientation()
    orientation.init_vector(pose.orientation.x,
                        pose.orientation.y,
                        pose.orientation.z,
                        pose.orientation.w)

    zed_tf = sl.Transform()
    zed_tf.init_orientation_translation(orientation, translation)
    
    return zed

def memorize_images(image, depth_map, normal_map):
    # Salva l'immagine e la mappa di profondità come PNG per utilizzo offline
    image_path = "data/saved_image.png"
    depth_map_path = "data/saved_depth_map.png"
    normal_map_path = "data/saved_normal_map.png"
    # Visualizza la normal map come immagine
    normal_map_data = normal_map.get_data()
    normal_map_image = ((normal_map_data[:, :, :3] + 1) / 2 * 255).astype(np.uint8)
    # Normalizza la depth map per visualizzazione e salvataggio
    depth_map_data = depth_map.get_data()
    depth_map_norm = cv2.normalize(depth_map_data[:, :, 2], None, 0, 255, cv2.NORM_MINMAX)
    depth_map_image = depth_map_norm.astype(np.uint8)
    # Salva le immagini
    cv2.imwrite(image_path, image)
    cv2.imwrite(depth_map_path, depth_map_image)
    cv2.imwrite(normal_map_path, normal_map_image)

# === Acquisizione immagine e mappa di profondità ===
def get_zed_image(zed, save=False):
    # Inizializza parametri e variabili
    runtime_parameters = sl.RuntimeParameters()
    image_zed = sl.Mat()
    depth_map = sl.Mat()
    point_cloud = sl.Mat()
    normal_map = sl.Mat()

    # Grab dell'immagine e della mappa di profondità
    print("Acquisizione misure dalla camera...")
    while zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
        # Acquisisci l'immagine e la mappa di profondità
        zed.retrieve_image(image_zed, sl.VIEW.LEFT)
        zed.retrieve_measure(depth_map, sl.MEASURE.XYZRGBA)
        zed.retrieve_measure(normal_map, sl.MEASURE.NORMALS)   
        zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA) 
        image = cv2.cvtColor(image_zed.get_data(), cv2.COLOR_RGBA2RGB)
        break

    # DEBUG: Salva l'immagine e la mappa di profondità per utilizzo offline
    if save:
        memorize_images(image, depth_map, normal_map)
        # Salva il point cloud in un file PLY
        point_cloud.write("data/point_cloud.ply")
        print(f"\"Salvato acquisizioni in \\data\"")
    
    # Ritorna le misure
    return image, depth_map, normal_map, point_cloud