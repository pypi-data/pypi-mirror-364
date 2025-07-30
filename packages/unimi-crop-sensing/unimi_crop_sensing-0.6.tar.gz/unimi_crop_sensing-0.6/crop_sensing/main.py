import zed_manager
import find_plant
import cobot_manager
import create_plc

# testing parameters
linux_ip = "192.168.5.6"
plants_number = 8

# This function is used to test the functionalities of the crop sensing module
def main():
    
    # Get the current pose of the cobot
    pose = cobot_manager.get_cobot_pose(linux_ip)

    # Initialize the ZED camera
    zed = zed_manager.zed_init(pose)
    
    # Capture the environment with the ZED camera
    image, depth_map, normal_map, point_cloud = zed_manager.get_zed_image(zed, save=True)

    # Filter the plants from the background
    mask = find_plant.filter_plants(image, save_mask=True)
    
    # Divide the plants into clusters
    masks, bounding_boxes = find_plant.segment_plants(mask, plants_number)
    find_plant.save_clustered_image(image, bounding_boxes)

    # Extract the 3D points from the clusters
    for m in masks:
        bbxpts = find_plant.plot_3d_bbox(m, point_cloud)
        
    # Communicate the bounding boxes to the cobot (only if the cobot is operated in another machine)
    cobot_manager.send_cobot_map(linux_ip, bbxpts)

    # Create point cloud (this will create a .ply file by taking a video of the environment)
    create_plc.record_and_save(plant_name='piantina1', frames=300)

    zed.close()


if __name__ == "__main__":
    main()
    

