"""
Main GUI module
Houses all Page Classes as well as the App Class
"""
import json
import os
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter
from tkintermapview import TkinterMapView
from tkcalendar import DateEntry

import h5py
import numpy as np
from customtkinter import DrawEngine
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import Predict
from data_processing import save_hdf5_from_nparray, visualize_result
from utils import get_bbox_for_city, call_for_data
import credentials



polygonList = []
DISPLAYCORDS = []
FIGURE = None
CURRENT_FILE_PATH = ""

class App(customtkinter.CTk):
    """
    Main Application class
    """
    APP_NAME = "Satellite Data Pipeline"
    WIDTH = 800
    HEIGHT = 400
    file_path = ""
    shape = ""
    data = None
    CONFIG_PATH = os.path.expanduser("~/.myguiapp_config.json")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        DrawEngine.preferred_drawing_method = "polygon_shapes"

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.marker_list = []
        container = customtkinter.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.pages = {}
        self.create_pages(container)

        self.show_page("PageOne")

    def open_update_dialog(self):
        """
        Command for the Credential Update
        """
        update_win = tk.Toplevel()
        update_win.title("Update Credentials")

        tk.Label(update_win, text="Client ID:").grid(row=0, column=0)
        cid_entry = tk.Entry(update_win)
        cid_entry.grid(row=0, column=1)

        tk.Label(update_win, text="Client Secret:").grid(row=1, column=0)
        cs_entry = tk.Entry(update_win, show="*")
        cs_entry.grid(row=1, column=1)

        # Prefill with existing values
        stored_id, stored_secret = credentials.get_credentials()
        if stored_id:
            cid_entry.insert(0, stored_id)
        if stored_secret:
            cs_entry.insert(0, stored_secret)

        def update_and_close():
            new_id = cid_entry.get()
            new_secret = cs_entry.get()
            if new_id and new_secret:
                credentials.save_credentials(new_id, new_secret)
                messagebox.showinfo("Success", "Credentials updated.")
                update_win.destroy()
            else:
                messagebox.showerror("Error", "Both fields are required.")

        tk.Button(update_win, text="Save", command=update_and_close).grid(row=2, column=0,
                                                                          columnspan=2, pady=10)

    def set_data(self, data):
        """
        Setter for data
        """
        self.data = data

    def get_data(self):
        """
        Getter for data
        """
        return self.data

    def set_shape(self, shapeStr):
        """
        Setter for shape
        """
        self.shape = shapeStr

    def get_shape(self):
        """
        Getter for shape
        """
        return self.shape

    def set_file_path(self, file_path):
        """
        Setter for file_path
        """
        self.file_path = file_path

    def get_file_path(self):
        """
        Getter for file_path
        """
        return self.file_path

    def create_pages(self, container):
        """
        Init the pages and add them to pages-dict.
        """
        # Add pages to the dictionary
        self.pages["PageOne"] = PageOne(container, self)
        self.pages["PageTwo"] = PageTwo(container, self)
        self.pages["PageThree"] = PageThree(container, self)
        # Grid all the pages (but only one will be visible at a time)
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def show_page(self, page_name, option=False):
        """
        Navigation method, that raises and requested pages and hands over needed parameters
        """
        # Show the selected page
        page = self.pages[page_name]
        if page_name == "PageTwo":
            filepath = ''
            # Use the existing PageOne instance to get parameters
            page_one = self.pages["PageOne"]
            if option:
                filepath = page_one.pick_existing_inputfile()
                page.set_file_path(filepath)
                page.buttonUse.pack()
                page.buttonSave.pack_forget()
            else:
                page.buttonUse.pack_forget()
                page.buttonSave.pack()
            self.figure, data_selected = self.use_polygon(page_one, filepath)
            page.controller.set_data(data_selected)
            # Pass the FIGURE to PageTwo
            page.set_figure(self.figure)
        if page_name == "PageThree":
            if option:
                page.view_file_only()
            else:
                page.run_detection()
        page.tkraise()

    def on_closing(self, event=0):
        """
        Closes the application
        """
        self.destroy()

    def start(self):
        """
        Init the app
        """

        menu_bar = tk.Menu(self)
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Update Credentials", command=self.open_update_dialog)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        self.config(menu=menu_bar)


        self.mainloop()

    def use_polygon(self, pageOne, path=''):
        """
        Calls for Satellitedata using the selected polygon
        """
        if path == '':
            lat1, long1 = polygonList[0]
            lat2, long2 = polygonList[2]
            print((long1, lat1, long2, lat2))
            start_date = pageOne.startDate.get_date()
            end_date = pageOne.endDate.get_date()
            cloudcover = pageOne.cloudSlider.get()
            print((start_date, end_date, cloudcover))
            return call_for_data((long1, lat1, long2, lat2),
                                 start_date, end_date, cloudcover)
        else:
            return call_for_data(None, None, None, None, path)


class PageOne(customtkinter.CTkFrame):
    """
    PageOne shows a tile-server map and the search parameters can be selected.
    Also acts as main menu, to jump to other screens if data already exists
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150,
                                                 corner_radius=15, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1,
                              pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(2, weight=1)
        self.button_existingSet = customtkinter.CTkButton(
            master=self.frame_left,
            text="Analyse existing set",
            command=lambda: controller.show_page("PageTwo", True))
        self.button_existingSet.grid(pady=(20, 0), padx=(20, 20), row=0, column=1)

        self.button_viewResults = (customtkinter.CTkButton(
            master=self.frame_left,
            text="View Results",
            command=lambda: controller.show_page("PageThree", True)))

        self.button_viewResults.grid(pady=(20, 0), padx=(20, 20), row=0, column=2)

        self.button_GatherData = customtkinter.CTkButton(master=self.frame_left,
                                                text="Use for AI!",
                                                command=lambda: controller.show_page("PageTwo"))
        self.button_GatherData.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)

        self.startDateText = customtkinter.CTkLabel(master=self.frame_left,
                                                    text="Select a Start-Date!")
        self.startDateText.grid(pady=(20, 0), row=1, column=0)
        self.startDate = DateEntry(master=self.frame_left,
                                   selectmode='day',
                                   cursor="hand1",
                                   year=2021, month=1, day=1)
        self.startDate.grid(pady=(20, 0), padx=(20, 20), row=1, column=1)

        self.endDateText = customtkinter.CTkLabel(master=self.frame_left,
                                                  text="Select an End-Date!")
        self.endDateText.grid(pady=(20, 0), row=2, column=0)
        self.endDate = DateEntry(master=self.frame_left,
                                 selectmode='day',
                                 cursor="hand1",
                                 year=2025, month=1, day=1)
        self.endDate.grid(pady=(20, 0), padx=(20, 20), row=2, column=1)

        self.endDateText = customtkinter.CTkLabel(master=self.frame_left,
                                                  text="Maximum Cloud-Cover:")
        self.endDateText.grid(pady=(20, 0), row=3, column=0)

        self.cloudSlider = customtkinter.CTkSlider(master=self.frame_left,
                                                   orientation='horizontal',
                                                   from_=0, to=100, number_of_steps=10, width=150,
                                                   command=self.update_slider_percentage)
        self.cloudSlider.set(20)
        self.cloudSlider.grid(pady=(20, 0), row=3, column=1)

        self.cloudCoverDisplay = customtkinter.CTkLabel(master=self.frame_left,
                                                        text=str(int(self.cloudSlider.get())) + "%")
        self.cloudCoverDisplay.grid(
            pady=(20, 0), padx=(0, 20), row=3, column=2)

        self.map_label = customtkinter.CTkLabel(
            self.frame_left, text="Tile Server:", anchor="w")
        self.map_label.grid(row=4, column=0, padx=(20, 20), pady=(20, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left,
                                                           values=["OpenStreetMap",
                                                                   "Google normal",
                                                                   "Google satellite"],
                                                           command=self.change_map, width=180)
        self.map_option_menu.grid(row=4, column=1, padx=(20, 20), pady=(10, 0))

        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=1, rowspan=1,
                             column=0, columnspan=3,
                             sticky="nswe", padx=(0, 0), pady=(0, 0))

        self.entry = customtkinter.CTkEntry(master=self.frame_right,
                                            placeholder_text="type address")
        self.entry.grid(row =0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", self.search_event)

        self.button_Search = customtkinter.CTkButton(master=self.frame_right,
                                                text="Search",
                                                width=90,
                                                command=self.search_event)
        self.button_Search.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)

        # Set default values

        self.map_option_menu.set("Google satellite")
        self.map_widget.set_tile_server(
            "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        lat, long = get_bbox_for_city("Innsbruck")
        self.map_widget.set_position(lat, long)

        def add_marker_event(coords):
            """
            Adds selected coordinates to buffer after user selected them via right-click
            """
            print(coords)
            polygonList.append(coords)
            if len(polygonList) == 2:
                lat1, lon1 = polygonList[0]
                lat2, lon2 = polygonList[1]
                minlat = min(lat1, lat2)
                minlon = min(lon1, lon2)
                maxlat = max(lat1, lat2)
                maxlon = max(lon1, lon2)
                polygonList.insert(1, (minlat, minlon))
                polygonList.insert(3, (maxlat, maxlon))

                DISPLAYCORDS.append((minlat, minlon))
                DISPLAYCORDS.append((maxlat, minlon))
                DISPLAYCORDS.append((maxlat, maxlon))
                DISPLAYCORDS.append((minlat, maxlon))

                self.map_widget.set_polygon(DISPLAYCORDS)
            elif len(polygonList) > 2:
                self.map_widget.delete_all_polygon()
                polygonList.clear()
                DISPLAYCORDS.clear()

        self.map_widget.add_right_click_menu_command(label="Add polygon corner",
                                                     command=add_marker_event,
                                                     pass_coords=True)

    def pick_existing_inputfile(self):
        """
        Asks user for existing base_data file and returns the path including filename.
        """
        return filedialog.askopenfilename(filetypes=[("H5 Files", "*.h5")], initialdir=os.getcwd(),
                                          title="Select an existing file!")

    def search_event(self, event=None):
        """
        Handles user requests to searching WKN
        """
        lat, long = get_bbox_for_city(self.entry.get())
        self.map_widget.set_position(lat, long)

    def update_slider_percentage(self, value):
        """
        Handles the user changing the slider for cloud percentage
        """
        self.cloudCoverDisplay.configure(text=str(int(value)) + "%")

    def clear_marker_event(self):
        """
        Deletes all markers from the map
        """
        for marker in self.marker_list:
            marker.delete()

    def change_appearance_mode(self, new_appearance_mode: str):
        """
        Changes appearance mode (dark or light)
        """
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_map(self, new_map: str):
        """
        Changes the tile-server map
        """
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server(
                "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server(
                "c&x={x}&y={y}&z={z}&s=Ga",
                max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server(
                "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
                max_zoom=22)


class PageTwo(customtkinter.CTkFrame):
    """
    PageTwo is used to display pre-processed data and to confirm its usage
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.figure = None
        self.scatter = None
        label = customtkinter.CTkLabel(
            self,
            text="These are your results, you can either save them or select another region!")
        label.pack(pady=10, padx=10)
        self.file_path = ""
        # Button to go back
        self.button = customtkinter.CTkButton(
            self,
            text="Go Back",
            command=lambda: controller.show_page("PageOne"))
        self.button.pack(pady=10)
        self.buttonSave = customtkinter.CTkButton(
            self, text="Save", command=self.save)
        self.buttonSave.pack(pady=10)

        self.buttonUse = customtkinter.CTkButton(
            self, text="Use set!", command=self.use)
        self.buttonUse.pack(pady=10)

    def save(self):
        """
        Asks user where to save the data from the API and saves it there
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".h5",
            filetypes=[("HDF5", "*.h5"), ("All Files", "*.*")],
            title="Save File")
        if not file_path:
            return
        try:
            save_hdf5_from_nparray(self.controller.get_data(), file_path)
            self.controller.set_file_path(file_path)
            self.controller.set_shape(str(self.controller.get_data().shape[1]) + "," + str(
                self.controller.get_data().shape[0]))
            self.controller.show_page("PageThree")
        except Exception as e:
            print(e)

    def set_file_path(self, file_path):
        """
        Setter method file_path
        """
        self.file_path = file_path

    def use(self):
        """
        Used by the 'Use' button. Instead of asking where to save the file, since it's already
        saved, the function simply hands over the data from the file to the model and page three.
        """
        self.controller.set_file_path(self.file_path)
        self.controller.set_shape(str(self.controller.get_data().shape[1]) + "," + str(
            self.controller.get_data().shape[0]))
        self.controller.show_page("PageThree")

    def set_figure(self, figure):
        """
        Used to visualize the gathered data from either the API or an existing file
        """
        # Destroy previous scatter widget if exists
        if self.scatter is not None:
            self.scatter.get_tk_widget().destroy()
        # Create new scatter plot with the updated FIGURE
        self.figure = figure
        self.scatter = FigureCanvasTkAgg(self.figure, self)
        self.scatter.get_tk_widget().pack(pady=10, padx=10)
        self.scatter.draw()


class PageThree(customtkinter.CTkFrame):
    """
    PageThree is used to display results
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.figure = None
        self.scatter = None
        self.controller = controller
        self.file_path = ""
        label = customtkinter.CTkLabel(self, text="That worked!")
        label.pack(pady=10, padx=10)
        button = customtkinter.CTkButton(self, text="Go back main menu",
                                         command=lambda: controller.show_page("PageOne"))
        button.pack(pady=10)

        self.text_display = customtkinter.CTkLabel(
            self, height=20, width=500, text="")
        self.text_display.pack(pady=10, padx=10)

    def run_detection(self):
        """
        Asks for End-Folder where to save _mask.h5 and _result.h5 files
        Finds previously selected or created base_data .h5 file and runs detection
        also displays detection results
        """
        outputdir = filedialog.askdirectory(
            title="Select an End-Folder!", initialdir=os.getcwd())

        print("rundetection" + self.controller.get_file_path())
        Predict.main(self.controller.get_file_path(),
                                        self.controller.get_shape(), outputdir)

        path_to_result = os.path.join(outputdir, Path(
            self.controller.get_file_path()).stem + "_mask.h5")
        print("path_to_result" + path_to_result)
        with h5py.File(path_to_result, "r") as f:
            mask_array = np.array(f["mask"])
        base_data = self.controller.get_data()
        save_data_base = base_data
        mask_array = np.reshape(
            mask_array, (mask_array.shape[0], mask_array.shape[1], 1))
        # mask_array = np.rot90(mask_array)
        base_data = np.concatenate((base_data, mask_array), 2)
        count_pixels, percentage = self.view_result_file(base_data)
        path_to_result_set = os.path.join(
            outputdir,
            Path(self.controller.get_file_path()).stem + "_results.h5")
        self.save_result_file(save_data_base, mask_array,
                              count_pixels, percentage, path_to_result_set)

    def view_file_only(self):
        """
        Opens a .h5 File specified by user which has to be formatted as described in
        save_result_file and then presents the data
        """
        path_to_file = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            filetypes=[("HDF5", "*.h5")],
            title="Select results to view!")
        with h5py.File(path_to_file, "r") as f:
            mask_array = np.array(f["mask"])
            base_data = np.array(f["img"])
            mask_array = np.reshape(mask_array,
                                    (mask_array.shape[0],
                                     mask_array.shape[1], 1))
            base_data = np.concatenate((base_data, mask_array), 2)
            self.view_result_file(base_data)

    def view_result_file(self, base_data):
        """
        Visualizes AxBx15 nparray with :,:,15 being the result mask
        Returns Percentage and Count of Pixels
        """
        self.figure, count_pixels, percentage = visualize_result(base_data)

        text_content = (f"Number of Landslide Pixels: {count_pixels}\n"
                        f"Percentage of Landslide Pixels: {percentage:.2%}")
        self.text_display.configure(text=text_content)

        if self.scatter is not None:
            self.scatter.get_tk_widget().destroy()
        self.scatter = FigureCanvasTkAgg(self.figure, self)
        self.scatter.get_tk_widget().pack(pady=10, padx=10)
        self.scatter.draw()
        return count_pixels, percentage

    def save_result_file(self, base_data, mask_data, count, percentage, path):
        """
        Saves results to a .h5 file
        Includes used processing data as well as mask data
        Saves Count of Pixels and Percentage of Landslide Pixels
        """
        with h5py.File(path, "w") as f:
            f.create_dataset("mask", data=mask_data)
            f.create_dataset("img", data=base_data)

            f.attrs["Count of Landslide Pixels"] = count
            f.attrs["Percentage of Landslide Pixels"] = percentage


if __name__ == "__main__":
    app = App()
    app.start()
