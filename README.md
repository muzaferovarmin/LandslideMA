This repository was created for my Masters Thesis in which an automated Data-Pipeline was to be written. 
It is possible to select an area on a map, select the time-frame as well as the maximum cloud cover. Locations can be searched for using Well-Known-Names.
The selected locaion is then called for using the Copernicus API and will be formatted to an .h5 file.
The .h5 file can then be scanned for land-slides using the baseline model of the 2022 landslide4sense competition, see https://github.com/iarai/Landslide4Sense-2022

Slope calculations were done using richdDEM (https://github.com/r-barnes/richdem), the GUI using CustomTKinter (https://github.com/TomSchimansky/CustomTkinter) as well as TkinterMap(https://github.com/TomSchimansky/TkinterMapView)

## Installation

Either run the gui.py directly, for which the requirements can be found in the requirements_base_app.txt, or simply run dist/gui. 
This will allow you to use the workflow until you need to run a detection. 
Either provide your own script and custom environment in the runSubProcess.py or. run the installEnvironment scripts for your OS from the dist folder. Importantly, the environment will be installed in the directory the script is run. The environment directory is expected to be in the same directory as the either gui.py or gui.

