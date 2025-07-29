import os
import customtkinter as ctk
import tkinter.filedialog as fd
from translation_helper.components.ValuesFrame import ValueFrame
from translation_helper.components.CreateKeyWindow import CreateKeyWindow
from translation_helper.data.TranslationManager import TManager


class KeysFrame(ctk.CTkFrame):
    def __init__(self, manager: TManager, values_frame: ValueFrame,
                 master, **kwargs):

        self.manager = manager
        self.values_frame = values_frame

        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(3, weight=1)

        self.loadButton = ctk.CTkButton(
            self, text="Load Folder", command=self._load_folder)
        self.loadButton.grid(row=0, column=0, padx=10,
                             pady=10, sticky="ew", columnspan=2)

        self.label = ctk.CTkLabel(self, text="Keys", anchor="w")
        self.label.grid(row=1, column=0, padx=10, sticky="we")

        self.addButton = ctk.CTkButton(
            self, text="Add Key",
            command=self.create_key)
        self.addButton.grid(row=1, column=1, padx=10, sticky="e")

        self.searchButton = ctk.CTkButton(self, text="Search", width=50,
                                          command=self.render_keys
                                          )
        self.searchButton.grid(row=2, column=0, padx=10, sticky="ew")

        self.filterField = ctk.CTkEntry(
            self, placeholder_text="Filter Keys")
        self.filterField.grid(row=2, column=1, padx=10, pady=10,
                              sticky="ew", columnspan=1)

        self.keysFields = ctk.CTkScrollableFrame(self)
        self.keysFields.grid(
            row=3, column=0, padx=10, pady=5, sticky="nsew", columnspan=2)

        self.saveButton = ctk.CTkButton(
            self, text="Save Changes",
            command=lambda: self.manager.saveData(self.manager)
        )
        self.saveButton.grid(row=4, column=0, padx=10,
                             pady=10, sticky="ew", columnspan=2)

    def _load_folder(self):
        folder_path = fd.askdirectory()
        if not folder_path:
            return

        self.manager.path = folder_path

        subfolders = []

        for entry in os.scandir(folder_path):
            if entry.is_dir():
                subfolders.append(entry.name)
        self._ask_select_subfolder(subfolders)

    def render_keys(self):
        if not self.manager.mainLang:
            return

        for widget in self.keysFields.winfo_children():
            widget.destroy()

        keys = self.manager.getKeys(self.manager)

        self.keysFields.grid_columnconfigure(0, weight=6)
        self.keysFields.grid_columnconfigure(1, weight=1)
        self.keysFields.grid_columnconfigure(2, weight=1)

        buttons = {}

        row = 0
        button = 0
        for entry in keys:

            filter = self.filterField.get().strip()
            if entry and filter not in entry:
                continue
            label = ctk.CTkLabel(self.keysFields, text=entry,
                                 justify="left", anchor="w", width=100)
            label.grid(row=row, column=0, padx=10, pady=5, sticky="nsew")

            buttons[button] = ctk.CTkButton(
                self.keysFields, text="Edit", width=30, fg_color="#e5c890",
                text_color="#2b2b2b"
            )
            buttons[button].configure(
                command=lambda e=entry:
                self.values_frame.render_values(e))

            buttons[button].grid(row=row, column=1, padx=5,
                                 pady=5, sticky="nsew")

            def delete_key(key: str):
                self.manager.removeKey(self.manager, key)
                self.render_keys()

            deleteButton = ctk.CTkButton(
                self.keysFields, text="Delete", width=30, fg_color="#e78284",
                text_color="#2b2b2b",
                command=lambda e=entry: delete_key(key=e)
            )

            deleteButton.grid(row=row, column=2, padx=5, pady=5, sticky="nsew")
            row = row+1
            button = button + 1

    def _ask_select_subfolder(self, subfolders):
        if not subfolders:
            return

        dlg = ctk.CTkToplevel(self)
        dlg.title("i18n Manager Main Language")
        dlg.geometry("400x200")
        dlg.grab_set()  # make modal
        parent_x = self.master.winfo_rootx()
        parent_y = self.master.winfo_rooty()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()

        # Get dialog dimensions
        dlg_width = dlg.winfo_width()
        dlg_height = dlg.winfo_height()

        # Calculate centered position
        x = parent_x + (parent_width // 2) - (dlg_width // 2)
        y = parent_y + (parent_height // 2) - (dlg_height // 2)

        dlg.geometry(f"+{x}+{y}")

        ctk.CTkLabel(dlg, text="Primary Language").pack(pady=10)

        def on_select(name):
            self.manager.mainLang = name
            # mb.showinfo("Subfolder Selected", f"You selected: {name}")
            dlg.destroy()
            self.manager.loadData(self.manager)
            self.render_keys()

        for name in subfolders:
            btn = ctk.CTkButton(
                dlg, text=name, command=lambda n=name: on_select(n))
            btn.pack(fill="x", padx=20, pady=3)

    def create_key(self):
        if not self.manager.path:
            return

        dlg = CreateKeyWindow(master=self.master,
                              manager=self.manager, callback=self.render_keys)
        dlg.grab_set()
