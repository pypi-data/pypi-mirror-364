import zed_manager
import find_plant
import cobot_manager
import create_plc

# This function is used to test the functionalities of the crop sensing module
def main():
    # testing parameters
    linux_ip = "192.168.5.6"
    plants_number = 8
    
    # Ottieni translazione e orientamento del cobot
    pose = cobot_manager.get_cobot_pose(linux_ip)

    # Inizializza la ZED
    zed = zed_manager.zed_init(pose)
    
    # Acquisisci i dati dalla ZED
    image, depth_map, normal_map, point_cloud = zed_manager.get_zed_image(zed, save=True)

    # Trova le piantine nell'immagine
    mask = find_plant.filter_plants(image, save_mask=True)
    
    # Dividi la maschera di ogni piantina
    masks, bounding_boxes = find_plant.segment_plants(mask, plants_number)
    find_plant.save_clustered_image(image, bounding_boxes)

    # Estrai le bounding box 3D dei cluster
    for m in masks:
        bbxpts = find_plant.plot_3d_bbox(m, point_cloud)
        
    # Comunicala al Cobot [nel caso sia in una macchina differente]
    #cobot_manager.send_cobot_map(linux_ip, bbxpts)

    # Crea plc [da chiamare quando si intende memorizzare la plc di un video]
    #create_plc.record_and_save(plant_name='piantina1', frames=300)

    #zed.close()


if __name__ == "__main__":
    main()
    

