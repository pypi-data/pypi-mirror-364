import customtkinter as ctk
from translation_helper.data.TranslationManager import TManager


class ValueFrame(ctk.CTkFrame):
    field = ""

    def __init__(self, manager: TManager, master, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.values_frame = ctk.CTkScrollableFrame(self, label_text="   Values",
                                                   fg_color="#2d2c2f",
                                                   label_anchor="w")
        self.values_frame.grid(
            row=0, column=0, padx=10, pady=5, sticky="nsew", columnspan=2)

        self.values_frame.grid_columnconfigure(0, weight=1)

        self.saveButton = ctk.CTkButton(self, text="Apply",
                                        command=self.save_values)
        self.saveButton.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

    def render_values(self, field: str):
        self.field = field

        for widget in self.values_frame.winfo_children():
            widget.destroy()

        row = 0

        for key, value in self.manager.data.items():
            font = ctk.CTkFont(family='Roboto', size=14)
            label = ctk.CTkLabel(self.values_frame, text=key.capitalize(),
                                 anchor="w", font=font)
            label.grid(row=row, column=0, padx=10, pady=5, sticky="ew")

            textbox = ctk.CTkTextbox(
                self.values_frame, height=50, border_width=1)

            langValue = value[field] if field in value else ""

            textbox.insert("0.0", langValue)
            textbox.grid(row=row+1, column=0, padx=10, pady=2, sticky="ew")

            row = row+2

    def save_values(self):

        keys = []
        fields = self.get_all_textboxes()
        for lang, value in self.manager.data.items():
            keys.append(lang)

        for index, key in enumerate(keys):
            self.manager.data[key][self.field] = fields[index].get(
                "0.0", "end").strip()

    def get_all_textboxes(self):
        return [widget for widget in self.values_frame.winfo_children() if
                isinstance(widget, ctk.CTkTextbox)]
