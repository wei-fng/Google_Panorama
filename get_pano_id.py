import requests
import pandas as pd
import time


API_KEY = "Your_Google_API"  # Replace with your API key
API_URL = "https://maps.googleapis.com/maps/api/streetview/metadata"

df = pd.read_csv("test_converted_points.txt", sep="\t")
failed_requests = []  # List to store failed requests

def get_pano_id(latitude, longitude):
    params = {
        'location': f"{latitude},{longitude}",
        'key': API_KEY
    }
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            return data.get("pano_id", "")
        else:
            print(f"Location {latitude}, {longitude} does not have a pano_id.")
            failed_requests.append((latitude, longitude)) 
            return ""
    except Exception as e:
        print(f"Request failed for location {latitude}, {longitude}: {e}")
        failed_requests.append((latitude, longitude))
        return ""

df['pano_id'] = df.apply(lambda row: get_pano_id(row['latitude'], row['longitude']), axis=1)

time.sleep(0.1)

df.to_csv("coordinates_with_pano_id.txt", sep="\t", index=False)

if failed_requests:
    with open("failed_requests.txt", "w") as f:
        for latitude, longitude in failed_requests:
            f.write(f"{latitude}, {longitude}\n")

print("Pano_id retrieval and saving completed!")

if failed_requests:
    print(f"Failed to retrieve pano_id for {len(failed_requests)} locations. Check 'failed_requests.txt' for details.")