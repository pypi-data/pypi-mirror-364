import customtkinter
from translation_helper.components import KeysFrame, ValuesFrame
from translation_helper.data.TranslationManager import TManager
import pathlib
import os


class EditorFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame, for example:
        self.label = customtkinter.CTkLabel(self, text="Edit")
        self.label.grid(row=0, column=0, padx=20)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__(className="translation-manager")
        self.geometry("870x600")
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(0, weight=1)

        self.manager = TManager.get_instance()

        self.values_frame = ValuesFrame.ValueFrame(
            master=self, manager=self.manager)
        self.values_frame.grid(row=0, column=1, padx=10,
                               pady=10, sticky="nsew")

        self.my_frame = KeysFrame.KeysFrame(
            master=self, manager=TManager, values_frame=self.values_frame)
        self.my_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")


def run():
    current_dir = pathlib.Path(__file__).parent
    path = os.path.join(current_dir, "theme.json")

    customtkinter.set_default_color_theme(path)
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run()
