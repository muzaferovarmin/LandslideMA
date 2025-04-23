"""
Utils Module:
This module provides utility functions for the app
"""
import os
import sys

import numpy as np
import requests

from copernicus_api import authenticate_with_copernicus, fetch_dem_data, fetch_sentinel_data_image
from data_processing import (concatenate_dem_and_image,
                             visualize_as_tiles_np_array, visualize_as_tiles_h5)
from requestDefinitions import EVALSCRIPT_DEM, EVALSCRIPT_RGB_IMAGE



def get_bbox_for_city(city_name, guiuse=False):
    """
    This function gets the bounding box of a WKN
    by calling the calling the nominatim API using secrets_app.
    """
    geocode_url = (f"https://nominatim.openstreetmap.org/search?q={city_name}"
                   f"&format=json&polygon_geojson=1")
    headers = {'User-Agent':'Landslide-Thesis|ma3608@mci4me.at'}
    response = requests.get(geocode_url, headers=headers, timeout=100)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            bbox = data[0]['boundingbox']

            print(bbox)
            if not guiuse:
                return float(bbox[2]), float(
                    bbox[0]), float(bbox[3]), float(bbox[1])
            return float(data[0]['lat']), float(data[0]['lon'])
        raise ValueError("City not found in geocoding service.")
    raise requests.exceptions.HTTPError(
        f"Error fetching bbox: {response.status_code}")


def call_for_data(bbox, starttime, enddtime, cloudpercentage, path=''):
    """
    uses a provided bounding box to call the Sentinel-API

    """
    if path == '':
        try:
            print("Authenticating with Copernicus API...")
            oauth = authenticate_with_copernicus()
            print("Fetching Sentinel-2 DEM Image")

            dem = np.array(fetch_dem_data(oauth, bbox, EVALSCRIPT_DEM, False))
            print("Fetching Sentinel-2 RGB Image")
            image_data = np.array(
                fetch_sentinel_data_image(oauth, bbox, EVALSCRIPT_RGB_IMAGE, starttime, enddtime,
                                          cloudpercentage))
            data = concatenate_dem_and_image(dem, image_data)
            figure = visualize_as_tiles_np_array(data)
            return figure, data
        except PermissionError as e:
            print(f"Error: {e}")
            return None, None
    else:
        figure, data = visualize_as_tiles_h5(path)
        return figure, data


def resource_path(relative_path):
    """ Get absolute path to resource"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
