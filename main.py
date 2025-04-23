import tkinter as tk
from tkinter import messagebox
import keyring
import os
import json

import gui

APP_NAME = "Satellite Data Pipeline"
CONFIG_PATH = os.path.expanduser("~/.LandslidePipeline_config.json")

def save_client_id(client_id):
    with open(CONFIG_PATH, "w") as f:
        json.dump({"client_id": client_id}, f)

def load_client_id():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f).get("client_id")
    return None

def save_credentials(client_id, client_secret):
    save_client_id(client_id)
    keyring.set_password(APP_NAME, client_id, client_secret)

def get_stored_credentials():
    client_id = load_client_id()
    if client_id:
        client_secret = keyring.get_password(APP_NAME, client_id)
        return client_id, client_secret
    return None, None

def on_save():
    client_id = client_id_entry.get()
    client_secret = client_secret_entry.get()

    if client_id and client_secret:
        save_credentials(client_id, client_secret)
        messagebox.showinfo("Saved", "Client ID and Secret saved!")
        root.destroy()
        run_main_app(client_id)
    else:
        messagebox.showerror("Error", "Both fields are required.")

def run_main_app(client_id):
    print(f"Running app with client_id: {client_id}")
    # Your main app logic starts here

# Try auto-login
stored_id, stored_secret = get_stored_credentials()

if stored_id and stored_secret:
    run_main_app(stored_id)
    App = gui.App()
    App.start()
else:
    root = tk.Tk()
    root.title("Enter API Credentials")

    tk.Label(root, text="Client ID:").grid(row=0, column=0)
    client_id_entry = tk.Entry(root)
    client_id_entry.grid(row=0, column=1)

    tk.Label(root, text="Client Secret:").grid(row=1, column=0)
    client_secret_entry = tk.Entry(root, show="*")
    client_secret_entry.grid(row=1, column=1)

    tk.Button(root, text="Save", command=on_save).grid(row=2, column=0, columnspan=2)
    root.mainloop()
