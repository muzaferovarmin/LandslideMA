"""
API Interface to Sentinel2 L1C and Sentinel30
"""
import io
import tifffile
from oauthlib.oauth2 import BackendApplicationClient
from pyproj import Transformer
from requests_oauthlib import OAuth2Session
from secrets_app import secret_client_id, secret_client_secret
def authenticate_with_copernicus():
    """
    Authenticate with Copernicus Dataspace using credentials from secrets_app.py
    """
    client_id = secret_client_id
    client_secret = secret_client_secret
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token_url = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'
    oauth.fetch_token(token_url=token_url, client_secret=client_secret, include_client_id=True)
    return oauth

def fetch_dem_data(oauth, bbox,evalscript, save_as_file = True):
    """
    Fetch DEM data from Sentinel-30
    First reprojects from long&lat degrees to meters (EPSG:4326 -> EPSG:32633) since the
    resolution is in meters and the input in degrees.
    POSTs request with bbox and requests upsampling
    """
    transformer = Transformer.from_crs("EPSG:4326","EPSG:32633", always_xy=True)
    minx, miny = transformer.transform(float(bbox[0]), float(bbox[1]))
    maxx, maxy = transformer.transform(float(bbox[2]), float(bbox[3]))
    request = {
    "input": {
        "bounds": {
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/32633"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [minx, miny],
                            [maxx, miny],
                            [maxx, maxy],
                            [minx, maxy],
                            [minx, miny]
                        ]
                    ]
                },
            },
        "data": [
            {
                "type": "dem",
                "dataFilter": {"demInstance": "COPERNICUS_30"},
                "processing": {
                    "upsampling": "BILINEAR",
                    "downsampling": "BILINEAR",
                },
            }
        ],
    },
    "output": {
        "resx": 10,
        "resy": 10,
        "responses": [
            {
                "identifier": "default",
                "format": {"type": "image/tiff"},
            }
        ],
    },
    "evalscript": evalscript,
}
    url = "https://sh.dataspace.copernicus.eu/api/v1/process"
    response = oauth.post(url, json=request)
    if response.status_code == 200:
        if save_as_file:
            with open("output/out_dem.tiff", "wb") as file:
                file.write(response.content)
            return "output/out_dem.tiff"
        image_data = io.BytesIO(response.content)
        image = tifffile.imread(image_data)
        return image
    print(f"Error: {response.status_code}")
    print(response.text)
    return None

def fetch_sentinel_data_image(oauth, bbox, evalscript,start_time,end_time,cloudcoverpercentage):
    """
    Fetch Image data from Sentinel2-L1C
    First reprojects from long&lat degrees to meters (EPSG:4326 -> EPSG:32633) since the
    resolution is in meters and the input in degrees.
    POSTs request with bbox and requests upsampling for lower RES bands.
    Also applies filter for date & CC
    """
    start_time = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    transformer = Transformer.from_crs("EPSG:4326","EPSG:32633", always_xy=True)
    minx, miny = transformer.transform(float(bbox[0]), float(bbox[1]))
    maxx, maxy = transformer.transform(float(bbox[2]), float(bbox[3]))
    request = {
        "input": {
            "bounds": {
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/32633"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [minx, miny],
                            [maxx, miny],
                            [maxx, maxy],
                            [minx, maxy],
                            [minx, miny]
                        ]
                    ]
                },
            },
            "data": [
                {
                    "type": "sentinel-2-l1c",
                    "dataFilter": {
                        "timeRange": {
                            "from": start_time,
                            "to": end_time,
                        }
                    },
                    "maxCloudCover": cloudcoverpercentage,
                }
            ],
        },
        "output": {
            "resx":10,
            "resy":10,
            "responses": [
                {
                    "identifier": "default",
                    "format": {"type": "image/tiff"},
                }
            ],
        },
        "evalscript": evalscript,
    }

    url = "https://sh.dataspace.copernicus.eu/api/v1/process"
    response = oauth.post(url, json=request)

    if response.status_code == 200:
        image_data = io.BytesIO(response.content)
        image = tifffile.imread(image_data)
        return image
    print(f"Error: {response.status_code}")
    print(response.text)
    return None
