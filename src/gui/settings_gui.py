from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

import PySimpleGUIQt as sg

from settings.settings import Settings, TEMP_DATA_SOURCES

DATA_STORE_FOLDER = 'Data Store Folder:'
INPUT_DATA_FOLDER = 'Input Data Folder:'
DAILY_DATAFRAME_FILTER = 'Daily Data Frame Filter:'
HOURLY_DATAFRAME_FILTER = 'Hourly Data Frame Filter:'
TEMP_DATA_SOURCE = 'Temperature Data Source:'
POWER_USAGE_URL = 'Power Usage URL:'
VISUAL_CROSSING_SETTINGS = 'Visual Crossing Settings'
VC_URL = 'Visual Crossing URL:'
VC_LATITUDE = 'Latitude:'
VC_LONGITUDE = 'Longitude:'
API_KEY = 'API Key:'
EDIT_TEMP_SETTINGS = 'Edit Temp Settings'
CANCEL = 'Cancel'
SAVE = 'Save Settings'
ERROR_MSG = 'Error Messages'


class SettingsGUI:
    def __init__(self, settings: Settings, app_folder: Path ):
        self.settings = settings
        self.focus_element_key = DATA_STORE_FOLDER
        layout = [
                  [sg.Text(text='Application Settings')],
                  [sg.Text(text=DATA_STORE_FOLDER),
                   sg.InputText(default_text=self.settings.data_store_folder,
                                size_px=(600, 30), enable_events=True, key=DATA_STORE_FOLDER),
                   sg.FolderBrowse(button_text='Browse', target=DATA_STORE_FOLDER, initial_folder=app_folder.__str__())],
                  [sg.Text(text=INPUT_DATA_FOLDER),
                   sg.InputText(default_text=self.settings.input_data_folder,
                                size_px=(600, 30), enable_events=True, key=INPUT_DATA_FOLDER),
                   sg.FolderBrowse(button_text='Browse', target=INPUT_DATA_FOLDER, initial_folder=app_folder.__str__())],
                  [sg.Text(text=DAILY_DATAFRAME_FILTER),
                   sg.InputText(default_text=self.settings.daily_dataframe_filter,
                                size=(600, 30), enable_events=True, key=DAILY_DATAFRAME_FILTER)],
                  [sg.Text(text=HOURLY_DATAFRAME_FILTER),
                   sg.InputText(default_text=self.settings.hourly_dataframe_filter,
                                size=(600, 30), enable_events=True, key=HOURLY_DATAFRAME_FILTER)],
                  [sg.Text(text=TEMP_DATA_SOURCE),
                   sg.Combo(values=TEMP_DATA_SOURCES, default_value=self.settings.temp_data_source),
                   sg.Button(button_text=EDIT_TEMP_SETTINGS, key=EDIT_TEMP_SETTINGS)],
                  [sg.Text(text=POWER_USAGE_URL),
                   sg.InputText(default_text=self.settings.power_usage_url,
                                size_px=(600, 30), enable_events=True, key=POWER_USAGE_URL)],
                  [sg.MultilineOutput(default_text='', key=ERROR_MSG, size_px=(600, 120))],
                  [sg.Cancel(button_text=CANCEL, key=CANCEL), sg.OK(button_text=SAVE, key=SAVE)],
                 ]
        self.window = sg.Window('Application Settings', layout, default_element_size=(12, 1), auto_size_text=False,
                                auto_size_buttons=False,
                                default_button_element_size=(12, 1))

    def post_error_msg(self, msg: str):
        self.window.Element(ERROR_MSG).update(f'{msg}\n', append=True)

    def clear_error_msg(self):
        self.window.Element(ERROR_MSG).update('')

    def url_bad(self, key: str, url_str: str) -> bool:
        url_parts = urlparse(url_str)
        if len(url_parts.scheme) == 0 or len(url_parts.netloc) == 0:
            self.post_error_msg(f'{key} is not a valid URL')
            return True
        try:
            urlopen(f'{url_parts.scheme}://{url_parts.netloc}')
            return False
        except ValueError:
            self.post_error_msg(f'{key} is not a valid URL')
            return True

    def on_change_validations(self, values: dict) -> bool:
        self.clear_error_msg()
        error = False
        if len(values[DATA_STORE_FOLDER]) == 0:
            self.post_error_msg(f'{DATA_STORE_FOLDER} must have a value.')
            error = True
        if len(values[INPUT_DATA_FOLDER]) == 0:
            self.post_error_msg(f'{INPUT_DATA_FOLDER} must have a value.')
        if not values[TEMP_DATA_SOURCE] in TEMP_DATA_SOURCES:
            self.post_error_msg(f'{TEMP_DATA_SOURCE} not valid.')
            error = True
        error = self.url_bad(POWER_USAGE_URL, values[POWER_USAGE_URL])
        return error

    def on_save_validations(self,  values: dict) -> bool:
        error: bool = self.on_change_validations(values)
        if not error:
            path: Path = Path(values[DATA_STORE_FOLDER])
            if not path.exists():
                ...
        if not error:
            path: Path = Path(values[INPUT_DATA_FOLDER])
            if not path.exists():
                ...
        return error

    def read(self) -> Settings | None:
        self.focus_element_key = DATA_STORE_FOLDER
        error = False
        while True:
            event, values = self.window.read()
            if event == CANCEL:
                self.settings = None
                break
            elif event == EDIT_TEMP_SETTINGS:
                ...
            elif event == SAVE:
                if not error:
                    error = self.on_save_validations(values)
                    if not error:
                        break
                else:
                    self.post_error_msg(f'You must correct errors before saving the settings.')
            else:
                if self.focus_element_key != self.window.FocusElement.Key:
                    error = self.on_change_validations(values)
                    self.focus_element_key = self.window.FocusElement.Key
        return self.settings


if __name__ == '__main__':
    from settings.settings import load_settings
    app_folder = Path('/home/stroud/PycharmProjects/home-power-usage')
    settings = load_settings(Path(app_folder, 'settings.yaml'))
    w = SettingsGUI(settings=settings, app_folder=app_folder)
    settings = w.read()
    pass
