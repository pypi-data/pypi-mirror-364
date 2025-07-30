# mock_zed_manager.py
import cv2
import numpy as np
import torch
import pyzed.sl as sl

# Usa MiDaS per stimare depth da RGB
def estimate_depth_midas(image_path):
    model_type = "DPT_Large"
    midas = torch.hub.load("intel-isl/MiDaS", model_type)
    midas.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    midas.to(device)

    transform = torch.hub.load("intel-isl/MiDaS", "transforms").dpt_transform

    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    input_batch = transform(img_rgb).to(device)

    with torch.no_grad():
        prediction = midas(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()

    depth_map = prediction.cpu().numpy()
    return img_rgb, depth_map

def create_fake_point_cloud(depth_map, scale=1.0):
    h, w = depth_map.shape
    fx = fy = 500.0
    cx = w / 2
    cy = h / 2

    # Crea point cloud numpy [H, W, 4]
    pointcloud_np = np.zeros((h, w, 4), dtype=np.float32)

    for y in range(h):
        for x in range(w):
            Z = depth_map[y, x] * scale
            if Z <= 0:
                pointcloud_np[y, x] = [np.nan, np.nan, np.nan, 0]
            else:
                X = (x - cx) * Z / fx
                Y = (y - cy) * Z / fy
                pointcloud_np[y, x] = [X, Y, Z, 1.0]

    # Ottieni il puntatore e lo step
    data =  pointcloud_np.ctypes.data
    step = pointcloud_np.strides[0]

    # Crea sl.Mat e inizializzalo
    pc_mat = sl.Mat()
    pc_mat.init_mat_type(w, h, sl.MAT_TYPE.F32_C4)

    return pc_mat

def get_image():
    image_path = "crop_sensing/data/test.png"
    image, depth = estimate_depth_midas(image_path)
    point_cloud = create_fake_point_cloud(depth)

    # Normal map finta (solo per forma)
    normal_map = np.zeros_like(image)

    return image, depth, normal_map, point_cloud