import customtkinter as ctk
from translation_helper.data.TranslationManager import TManager
from typing import Callable
import os


class ModuleSelectionWindow(ctk.CTkToplevel):
    def __init__(self, master, manager: TManager, callback: Callable):
        super().__init__(master=master)
        self.title("Select a module to manage")
        self.geometry("400x300")
        self.master = master
        self.manager = manager
        self.callback = callback
        self.resizable(False, False)

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
        self.grid_rowconfigure(1, weight=1)

        self.key_label = ctk.CTkLabel(
                self, text="Module to Manage", fg_color="#949cbb",
                text_color="#2b2b2b")

        self.key_label.grid(row=0, column=0, sticky="ew", pady=0, padx=0)

        self.frame = ctk.CTkScrollableFrame(self)
        self.frame.grid(row=1, column=0, sticky="nsew", pady=10, padx=10)
        self.frame.grid_columnconfigure(0, weight=1)
        self.draw_options()

    def draw_options(self):
        search_path = os.path.join(self.manager.path, self.manager.mainLang)
        print(search_path)

        row = 0
        for entry in os.listdir(search_path):
            print(entry)
            if os.path.isdir(os.path.join(search_path, entry)):
                continue

            def run_callback(e):
                self.manager.current_module = e
                self.callback(e)
                self.destroy()

            entry_button = ctk.CTkButton(
                    self.frame, text=f"{entry}",
                    command=lambda e=entry: run_callback(e))
            entry_button.grid(row=row, column=0, sticky="ew", padx=10, pady=10)
            row = row+1
