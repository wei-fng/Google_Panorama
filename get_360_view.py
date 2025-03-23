import os
import time
import requests
from PIL import Image
from io import BytesIO
import pandas as pd

# helper functions in increase image down and right
def increase_right(img, pixels):
    width, height = img.size
    new_width = width + pixels
    result = Image.new(img.mode, (new_width, height), (250, 250, 250))
    result.paste(img, (0, 0))
    return result

def increase_down(img, pixels):
    width, height = img.size
    new_height = height + pixels
    result = Image.new(img.mode, (width, new_height), (250, 250, 250))
    result.paste(img, (0, 0))
    return result

class GMAP360:
    def __init__(self, sv_ids: list = None, download_path: str = None, zoom: int = 4, retry: int = 5, overwrite: bool = False):
        self.street_info = sv_ids
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        self.download_path = download_path
        self.retry = retry
        # only zoom levels from 1-5 are allowed
        if 5 < zoom < 0:
            raise Exception(f"Incorrect zoom size: {zoom}, only sizes 1-5 are allowed.")
        self.zoom = zoom
        self.overwrite = overwrite
        self.start()

    def download_street_view(self, location_id: str, lat: str, lng: str, id: str):
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}
        X = Y = 0
        end_column = 0
        block_size = 512 if self.zoom <= 4 else 256
        while True:
            while True:
                if Y == end_column and Y != 0:
                    break
                response = requests.get(f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={location_id}&x={X}&y={Y}&zoom={self.zoom}&nbt=1&fover=2", headers=headers)
                if response.status_code == 400:
                    end_column = Y
                    break
                image = Image.open(BytesIO(response.content))
                if X == 0 and Y == 0:
                    panorama = Image.new('RGB', (block_size, block_size), (250, 250, 250))
                elif end_column == 0 and Y != 0:
                    panorama = increase_down(panorama, block_size)
                panorama.paste(image, (X * block_size, Y * block_size))
                Y += 1
                time.sleep(0.01)
            Y = 0
            X += 1
            response = requests.get(f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={location_id}&x={X}&y={Y}&zoom={self.zoom}&nbt=1&fover=2", headers=headers)
            if response.status_code == 400:
                break
            image = Image.open(BytesIO(response.content))
            panorama = increase_right(panorama, block_size)
            panorama.paste(image, (X * block_size, Y * block_size))
        panorama.save(os.path.join(self.download_path, f"{id}_{lat}_{lng}.jpg"), format="JPEG")

    def download(self, location_id: str, retry: int, lat: str, lng: str, id: str):
        try:
            self.download_street_view(location_id, lat, lng, id)
        except Exception as e:
            print('Download Failed!')
            print(e)
            if retry > 0:
                print('Retrying...')
                self.download(location_id, retry - 1, lat, lng, id)

    def start(self):
        for index, street in enumerate(self.street_info):
            id, lat, lng, location_id = street
            if not self.overwrite and os.path.exists(os.path.join(self.download_path, f"{id}_{lat}_{lng}.jpg")):
                print(f"Skipping download | Image {id}_{lat}_{lng}.jpg already exists")
                continue
            print(f"Downloading image {id}_{lat}_{lng}.jpg {index}/{len(self.street_info)}")
            if location_id:
                self.download(location_id, self.retry, lat, lng, id)

def generate_ids(file_path):
    df = pd.read_csv(file_path, sep="\t")
    return [(f"pano_{index}", row['latitude'], row['longitude'], row['pano_id']) for index, row in df.iterrows()]

if __name__ == '__main__':
    csv_path = "coordinates_with_pano_id.txt" 
    street_info = generate_ids(csv_path)
    download_path = "./downloaded_images"
    zoom = 3
    retry = 3
    overwrite = False
    GMAP360(sv_ids=street_info, download_path=download_path, zoom=zoom, retry=retry, overwrite=overwrite)
