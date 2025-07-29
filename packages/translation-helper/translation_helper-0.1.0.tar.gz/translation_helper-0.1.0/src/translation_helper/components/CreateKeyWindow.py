import customtkinter as ctk
from translation_helper.data.TranslationManager import TManager
from typing import Callable


class CreateKeyWindow(ctk.CTkToplevel):
    def __init__(self, master, manager: TManager, callback: Callable):
        super().__init__(master=master)
        self.title("Create Key")
        self.geometry("400x280")
        self.master = master
        self.manager = manager
        self.callback = callback

        parent_x = self.master.winfo_rootx()
        parent_y = self.master.winfo_rooty()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        # Get dialog dimensions
        self_width = self.winfo_width()
        self_height = self.winfo_height()
        x = parent_x + (parent_width // 2) - (self_width // 2)
        y = parent_y + (parent_height // 2) - (self_height // 2)
        self.geometry(f"+{x}+{y}")

        self.grid_columnconfigure(0, weight=1)

        key_label = ctk.CTkLabel(self, text="Add new Key")
        key_label.grid(row=0, column=0, sticky="ew", pady=15, padx=10)

        key_label = ctk.CTkLabel(self, text="Key Name", anchor="w")
        key_label.grid(row=1, column=0, sticky="ew", pady=5, padx=10)

        key_name = ctk.CTkEntry(self, placeholder_text="Key Name")
        key_name.grid(row=2, column=0, sticky="ew", pady=5, padx=10)

        value_label = ctk.CTkLabel(self, text="Key Value", anchor="w")
        value_label.grid(row=3, column=0, sticky="ew", pady=5, padx=10)

        value_field = ctk.CTkEntry(self, placeholder_text="Key Value")
        value_field.grid(row=4, column=0, sticky="ew", pady=5, padx=10)

        def save_action():
            key = key_name.get().strip()
            val = value_field.get().strip()

            if not key or not val:
                return

            self.manager.addKey(self.manager, key=key, val=val)
            self.callback()
            self.destroy()

        save_button = ctk.CTkButton(self, text="Add Key", command=save_action)
        save_button.grid(row=5, column=0, sticky="sew", pady=15, padx=10)
