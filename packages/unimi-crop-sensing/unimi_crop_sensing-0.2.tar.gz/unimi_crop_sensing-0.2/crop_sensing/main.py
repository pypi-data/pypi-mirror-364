import cv2
import zed_manager
import find_plant
import cobot_manager

def save_clustered_image(image, bounding_boxes):
    # Draw bounding boxes on the original image for visualization
    for (x_min, y_min, x_max, y_max) in bounding_boxes:
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    cv2.imwrite("crop_sensing/data/clusters.png", image)

def main():
    # init magic numbers
    linux_ip = "192.168.5.6"
    plants_number = 3
    
    # Ottieni translazione e orientamento del cobot
    pose = cobot_manager.get_cobot_pose(linux_ip)

    # Inizializza la ZED
    zed = zed_manager.zed_init(pose)
    
    # Acquisisci i dati dalla ZED
    image, depth_map, normal_map, point_cloud = zed_manager.get_zed_image(zed)
    #image, depth_map, normal_map, point_cloud = mock.get_image()
    
    # Trova le piantine nell'immagine
    mask = find_plant.filter_plants(image)
    
    # Dividi la maschera di ogni piantina
    masks, bounding_boxes = find_plant.segment_plants(mask, plants_number)
    save_clustered_image(image, bounding_boxes)

    # Estrai le bounding box 3D dei cluster
    for m in masks:
        bbxpts = find_plant.plot_3d_bbox(m, point_cloud)
        
    # Comunicala al Cobot e acquisci ply
    #cobot_manager.send_cobot_map(linux_ip, bbxpts)
    
    # Analizza ply
    


if __name__ == "__main__":
    main()
    

