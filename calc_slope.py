import numpy as np
import h5py
import matplotlib.pyplot as plt
from scipy.ndimage import sobel
from skimage.measure import block_reduce

# Load the DEM data
with h5py.File('/home/armin/Masterarbeit/Landslide/image_13.h5', 'r') as f:
    data = f['img'][:]
dem = data[:,:,13]  # Get the DEM for the specific band
goal = data[:,:,12]
print(dem)
print(goal)
dem = dem*772.83144788
goal = goal*20.29228266


slope_dz_dx = sobel(dem, axis=1,mode='nearest' )/ (8*10)
slope_dz_dy = sobel(dem, axis=0,mode='nearest' ) / (8*10)


slope = np.arctan(np.sqrt(slope_dz_dy ** 2 + slope_dz_dx ** 2))
slope_deg = np.rad2deg(slope)

print("calculated:")
print(slope_deg.min(), slope_deg.max())

print("goaL:")
print(goal.min(), goal.max())

print("difference")
print(np.sqrt(np.mean((goal - slope_deg) ** 2)))