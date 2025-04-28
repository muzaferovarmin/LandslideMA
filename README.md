This repository was created for my Masters Thesis in which an automated Data-Pipeline was to be written. 
It is possible to select an area on a map, select the time-frame as well as the maximum cloud cover. Locations can be searched for using Well-Known-Names.
The selected locaion is then called for using the Copernicus API and will be formatted to an .h5 file.
The .h5 file can then be scanned for land-slides using the baseline model of the 2022 landslide4sense competition, see https://github.com/iarai/Landslide4Sense-2022

GUI was done using CustomTKinter (https://github.com/TomSchimansky/CustomTkinter) as well as TkinterMap(https://github.com/TomSchimansky/TkinterMapView)

## Usage
Simply Download the Executable for your operating system from the dist folder and run it!
You will be asked for your Copernicus Dataspace Credentials which can be retrieved here https://shapps.dataspace.copernicus.eu/dashboard/#/account/settings after registering for a dataspace account!
