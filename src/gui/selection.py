from pathlib import Path

import pandas as pd
import PySimpleGUIQt as sg

DATA_STORE_FN = 'Data Store File Name'
DATA_FRAME_LIST = 'Data Frame List'
CANCEL = 'Cancel'
SELECT_DS = 'Select DS'
SELECT_DF = 'Select DF'


class SelectionGUI:
    def __init__(self, title: str, data_store_dir: Path, data_store_file: Path = None):
        self.data_frame_names: list[str] = []
        self.data_store: [pd.HDFStore, None] = None
        self.data_frame: [pd.DataFrame, None] = None
        data_store_fn = ' '
        if data_store_file is not None and data_store_file.exists():
            data_store_fn = data_store_file.__str__()
            self.data_store = pd.HDFStore(data_store_file.__str__())
            self.data_frame_names = self.data_store.keys()
            self.data_store.close()
        layout = [
            [sg.Text(text='Data Store:'),
             sg.InputText(default_text=data_store_fn, key=DATA_STORE_FN, size_px=(600, 30)),
             sg.FileBrowse(button_text='Browse',
                           target=DATA_STORE_FN,
                           initial_folder=data_store_dir.__str__(),
                           file_types=(('HD5', '*.hd5'),)),
             sg.Button(button_text='Select', key=SELECT_DS)],
            [sg.Text(text='Data Frames')],
            [sg.Listbox(values=self.data_frame_names, size_px=(600, 600), key=DATA_FRAME_LIST)],
            [sg.Cancel(key=CANCEL), sg.OK(button_text='Select Data Frame', key=SELECT_DF)],
        ]
        self.window = sg.Window(title, layout, default_element_size=(12, 1), auto_size_text=False,
                                auto_size_buttons=False,
                                default_button_element_size=(12, 1))

    def read(self) -> tuple[pd.HDFStore | None, pd.DataFrame | None]:
        while True:
            event, values = self.window.read()
            if event == CANCEL:
                return None, None
            elif event == SELECT_DS:
                data_store_fn = values[DATA_STORE_FN]
                self.data_store = pd.HDFStore(data_store_fn)
                self.data_frame_names = self.data_store.keys()
                self.window.Element(DATA_FRAME_LIST).Update(self.data_frame_names)
            elif event == SELECT_DF:
                if self.data_store is not None:
                    if values[DATA_FRAME_LIST][0] in self.data_store.keys():
                        self.data_frame = self.data_store[values[DATA_FRAME_LIST][0]]
                        self.data_store.close()
                        return self.data_store, self.data_frame


if __name__ == '__main__':
    gui = SelectionGUI(title='Select a Data Store',
                       data_store_dir=Path('/home/stroud/PycharmProjects/home-power-usage/data'))
    data_store, data_frame = gui.read()
    pass

