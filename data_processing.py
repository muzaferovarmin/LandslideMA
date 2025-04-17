"""
Handles all visualizations, concatenations and normalizations.
A lot of tions.
"""
import rasterio
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.ndimage import median_filter
import richdem as rd


def save_hdf5_from_nparray(data, path):
    """
    Save normalized base_data to HDF5 file.
    This is the 'img' dataset
    """
    img_mean = np.array(
        [1111.81236406,
         824.63171476,
         663.41636217,
         445.17289745,
         645.8582926,
         1547.73508126,
         1960.44401001,
         1941.32229668,
         674.07572865,
         9.04787384,
         1113.98338755,
         519.90397929,
         20.29228266,
         772.83144788])
    reshaped_mean = img_mean[np.newaxis, np.newaxis, :]
    data = data / reshaped_mean
    print(data)
    with h5py.File(path, "w") as h5file:
        h5file.create_dataset("img", data.shape, dtype='float64', data=data)


def visualize_as_tiles_h5(h5_file, show=True):
    """
    Creates the plots for the 2x7 Subplot matrix of base_data
    Takes in H5 and handles data-extraction
    """
    # Open the HDF5 file
    with h5py.File(h5_file, 'r') as h5file:
        # Read the dataset (assuming the dataset name is 'img')
        data = h5file['img'][:]

        # Get the number of bands
        number_of_bands = data.shape[2]

        # Create subplots for each band
        fig, axes = plt.subplots(2, 7, figsize=(20, 10))
        axes = axes.flatten()
        for i in range(number_of_bands):
            b = data[:, :, i]
            ax = axes[i]
            ax.imshow(b, cmap='gray')
            ax.set_title(f"Band {i + 1}")
            ax.axis('off')

    plt.tight_layout()
    return fig, data


def visualize_as_tiles_np_array(numpy_array):
    """
    Creates the plots for the 2x7 Subplot matrix of base_data
    Takes in numpy-array
    """
    # Create 2 rows with 7 subplots each (for 14 bands)
    # Increased height for 2 rows
    fig, axes = plt.subplots(2, 7, figsize=(20, 10))

    # Flatten the axes array for easy iteration
    axes = axes.flatten()

    for i in range(numpy_array.shape[2]):
        b = numpy_array[:, :, i]
        ax = axes[i]
        ax.imshow(b, cmap='viridis')
        ax.set_title(f"Band {i + 1}")
        ax.axis('off')

    # Adjust layout to prevent overlapping
    plt.tight_layout()
    return fig


def visualize_result(numpy_array):
    """
    Creates the plots for the 2x7 + Result Subplot matrix of base_data
    Takes in numpy array and handles data-extraction
    """
    fig = plt.figure(figsize=(15, 8))
    gridSpecLayout = gridspec.GridSpec(
        3, 7, figure=fig, height_ratios=[1, 1, 2])

    # Plot first 14 layers
    for i in range(14):
        ax = fig.add_subplot(gridSpecLayout[i // 7, i % 7])
        ax.imshow(numpy_array[:, :, i], cmap='gray')
        ax.axis('off')

    # Extract and normalize RGB channels
    def normalize(channel):
        min_val, max_val = np.min(channel), np.max(channel)
        if max_val == min_val:
            return np.full_like(channel, 128, dtype='uint8')
        scaled = ((channel - min_val) / (max_val - min_val)
                  * 255).astype('uint8')

        return scaled
    red = normalize(numpy_array[:, :, 3])  # Channel 4 as Red
    green = normalize(numpy_array[:, :, 2])  # Channel 2 as Green
    blue = normalize(numpy_array[:, :, 1])  # Channel 3 as Blue

    rgb = np.dstack((red, green, blue))  # Correct order: R-G-B
    mask = numpy_array[:, :, 14]
    red_mask = np.zeros_like(rgb, dtype='uint8')
    red_mask[..., 0] = 255 * mask

    # Plot RGB
    ax_bottom = fig.add_subplot(gridSpecLayout[2, :])
    ax_bottom.imshow(rgb)

    ax_bottom.imshow(red_mask, alpha=0.5)
    ax_bottom.axis('off')
    countLandslidePixels = np.sum(mask)
    percentageLandslidePixels = (
        countLandslidePixels / float(numpy_array.shape[0] * numpy_array.shape[1]))

    return fig, countLandslidePixels, percentageLandslidePixels


def concatenate_dem_and_image(dem, image, metadata=None):
    """
    Takes in DEM and image-data. Reshapes and concatenates them to be AXBX14 numpy array.
    """
    print(dem.shape)
    dem_shape_dim1 = dem.shape[0]
    dem_shape_dim2 = dem.shape[1]
    dem_rd_array = rd.rdarray(dem, no_data=-9999, metadata=metadata)
    slope = rd.TerrainAttribute(
        dem_rd_array,
        attrib='slope_riserun',
        zscale=1.0)
    slope = np.array(slope).reshape((dem_shape_dim1, dem_shape_dim2, 1))
    dem = np.reshape(dem_rd_array, (dem_shape_dim1, dem_shape_dim2, 1))
    data = np.concatenate((image, slope), axis=2)
    data = np.concatenate((data, dem), axis=2)
    return data
