## About The Project

`unimi_crop_sensing` nasce con l’obiettivo di offrire un insieme di **operazioni semplici e intuitive** per interagire con la **camera ZED**. Consiste in un toolkit per l'elaborazione e segmentazione di immagini e point cloud acquisiti tramite la **camera stereo ZED**. Il progetto è pensato per applicazioni di agricoltura di precisione, consentendo di identificare piante in 2D e 3D, generare bounding box e comunicare con un cobot attraverso WebSocket in ambiente ROS.

### Funzionalità principali
* Segmentazione del verde con Excess Green Index
* Clustering delle piante tramite KMeans
* Calcolo bounding box 2D e 3D su point cloud
* Salvataggio `.ply`, immagini, normal map
* Integrazione WebSocket ROS (`rosbridge`) per invio/lettura pose

### Built With

* [OpenCV](https://opencv.org/)
* [NumPy](https://numpy.org/)
* [scikit-image](https://scikit-image.org/)
* [scikit-learn](https://scikit-learn.org/)
* [websocket-client](https://github.com/websocket-client/websocket-client)
* [Stereolabs ZED SDK](https://www.stereolabs.com/zed-sdk/) 

## Getting Started

### Prerequisites

Assicurati di avere:
- Python 3.9
- ZED SDK installato correttamente e funzionante
- ROS + rosbridge in esecuzione se si usa WebSocket
- Le librerie listate in `requirements.txt`

⚠️ Pyzed 5.0 richiede numpy 2.x, ciò va in conflitto con altre funzioni del progetto, perciò se riscontri errori relativi a `numpy`, assicurati di installare una versione compatibile:
```bash
pip install "numpy<2"
```

### Installation

Puoi usare `unimi_crop_sensing` come **pacchetto Python installabile via PyPI**. Installa tutto con:
```bash
pip install unimi_crop_sensing
```

## Usage

Questo è un esempio di main che sfrutta ogni funzione per ottenere coordinate spaziali e point cloud di ogni piantina nel proprio raggio d'azione

```python
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
``` 

<!-- CONTACT -->
## Contact

francescobassam.morgigno@studenti.unimi.it

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Stereolabs](https://www.stereolabs.com/en-it)

