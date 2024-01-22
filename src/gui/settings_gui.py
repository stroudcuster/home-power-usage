from os import chdir
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

import PySimpleGUIQt as sg

from settings.settings import (Settings,
                               TEMP_DATA_SOURCES,
                               TEMP_DATA_SOURCE_VISUAL_CROSSING,
                               TEMP_DATA_SOURCE_SC_ACIS,
                               Validator,
                               VisualCrossingSettings)

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
VC_API_KEY = 'API Key:'
EDIT_TEMP_SETTINGS = 'Edit Temp Settings'
CANCEL = 'Cancel'
SAVE = 'Save Settings'
ERROR_MSG = 'Error Messages'


class BaseGUI:
    def __init__(self):
        self.window = None

    def post_error_msg(self, msg: str):
        self.window.Element(ERROR_MSG).update(f'{msg}\n', append=True)

    def clear_error_msg(self):
        self.window.Element(ERROR_MSG).update('')

    def url_bad(self, key: str, url_str: str) -> bool:
        try:
            url_parts = Validator.url_parse(url_str)
            try:
                Validator.url_open(f'{url_parts.scheme}://{url_parts.netloc}')
                return False
            except ValueError as excep:
                self.post_error_msg(f'{key} {excep.args[0]}')
                return True
        except ValueError as excep:
            self.post_error_msg(f'{key} {excep.args[0]}')
            return True


class VisualCrossingSettingsGUI(BaseGUI):
    def __init__(self, vc_settings: VisualCrossingSettings, app_folder: Path):
        BaseGUI.__init__(self)
        self.vc_settings: VisualCrossingSettings = vc_settings
        self.app_folder:Path = app_folder
        self.focus_element_key:str = VC_URL
        layout = [
            [sg.Text(text=VC_URL),
             sg.InputText(default_text=vc_settings.url,
                          size_px=(1000, 30), enable_events=True, key=VC_URL)],
            [sg.Text(text=VC_LATITUDE),
             sg.InputText(default_text=f'{vc_settings.latitude:.5f}',
                          size_px=(100, 30), enable_events=True, key=VC_LATITUDE)],
            [sg.Text(text=VC_LONGITUDE),
             sg.InputText(default_text=f'{vc_settings.longitude:.5f}',
                          size_px=(100, 30), enable_events=True, key=VC_LONGITUDE)],
            [sg.Text(text=VC_API_KEY),
             sg.InputText(default_text=vc_settings.api_key,
                          size_px=(600, 30), enable_events=True, key=VC_API_KEY)],
            [sg.MultilineOutput(default_text='', key=ERROR_MSG, size_px=(600, 120))],
            [sg.Cancel(button_text=CANCEL, key=CANCEL), sg.OK(button_text=SAVE, key=SAVE)],
        ]
        self.window = sg.Window('Visual Crossing Temperature Data Settings', layout,
                                default_element_size=(12, 1), auto_size_text=False,
                                auto_size_buttons=False,
                                default_button_element_size=(12, 1))

    def check_lat_long(self, label: str, value: str) -> bool:
        error = False
        try:
            if label == VC_LATITUDE:
                Validator.latitude(value)
            elif label == VC_LONGITUDE:
                Validator.longitude(value)
        except ValueError as excep:
            self.post_error_msg(f'{label} {excep.args[0]}')
            error = True
        return error

    def on_change_validations(self, values) -> bool:
        self.clear_error_msg()
        errors: list[bool] = []
        try:
            Validator.vc_required(values[VC_URL])
        except ValueError as excep:
            self.post_error_msg(f'{VC_URL} {excep.args[0]}')
            errors.append(True)
        errors.append(self.check_lat_long(VC_LATITUDE, values[VC_LATITUDE]))
        errors.append(self.check_lat_long(VC_LONGITUDE, values[VC_LONGITUDE]))
        try:
            Validator.vc_required(values[VC_API_KEY])
        except ValueError as excep:
            self.post_error_msg(f'{VC_API_KEY} {excep.args[0]}')
            errors.append(True)
        return any(errors)

    def on_save_validations(self, values) -> bool:
        errors: list[bool] = [self.on_change_validations(values)]
        if len(values[VC_URL]) > 0:
            url_parts = urlparse(values[VC_URL])
            url = f'{url_parts.scheme}://{url_parts.netloc}'
            errors.append(self.url_bad(VC_URL, url))
        return any(errors)

    def read(self) -> VisualCrossingSettings | None:
        self.focus_element_key = VC_URL
        error = False
        while True:
            event, values = self.window.read()
            if event == CANCEL or event == sg.WIN_CLOSED:
                self.vc_settings = None
                break
            elif event == SAVE:
                if not error:
                    error = self.on_save_validations(values)
                    if not error:
                        self.vc_settings.url = values[VC_URL]
                        self.vc_settings.latitude = float(values[VC_LATITUDE])
                        self.vc_settings.longitude = float(values[VC_LONGITUDE])
                        self.vc_settings.api_key = values[VC_API_KEY]
                        break
            else:
                if self.focus_element_key != self.window.FocusElement.Key:
                    error = self.on_change_validations(values)
                    self.focus_element_key = self.window.FocusElement.Key
                else:
                    error = False
        self.window.close()
        return self.vc_settings


class SettingsGUI(BaseGUI):
    def __init__(self, settings: Settings, app_folder: Path ):
        BaseGUI.__init__(self)
        self.settings = settings
        self.app_folder = app_folder
        self.focus_element_key = DATA_STORE_FOLDER
        layout = [
                  [sg.Text(text=DATA_STORE_FOLDER),
                   sg.InputText(default_text=self.settings.data_store_folder,
                                size_px=(600, 30), enable_events=True, key=DATA_STORE_FOLDER),
                   sg.FolderBrowse(button_text='Browse', target=DATA_STORE_FOLDER,
                                   initial_folder=app_folder.__str__())],
                  [sg.Text(text=INPUT_DATA_FOLDER),
                   sg.InputText(default_text=self.settings.input_data_folder,
                                size_px=(600, 30), enable_events=True, key=INPUT_DATA_FOLDER),
                   sg.FolderBrowse(button_text='Browse', target=INPUT_DATA_FOLDER,
                                   initial_folder=app_folder.__str__())],
                  [sg.Text(text=DAILY_DATAFRAME_FILTER),
                   sg.InputText(default_text=self.settings.daily_dataframe_filter,
                                size=(600, 30), enable_events=True, key=DAILY_DATAFRAME_FILTER)],
                  [sg.Text(text=HOURLY_DATAFRAME_FILTER),
                   sg.InputText(default_text=self.settings.hourly_dataframe_filter,
                                size=(600, 30), enable_events=True, key=HOURLY_DATAFRAME_FILTER)],
                  [sg.Text(text=TEMP_DATA_SOURCE),
                   sg.Combo(values=TEMP_DATA_SOURCES, default_value=self.settings.temp_data_source,
                            key=TEMP_DATA_SOURCE),
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

    def on_change_validations(self, values: dict) -> bool:
        self.clear_error_msg()
        errors: list[bool] = []
        try:
            Validator.required(values[DATA_STORE_FOLDER])
        except ValueError as excep:
            self.post_error_msg(f'{DATA_STORE_FOLDER} {excep.args[0]}')
            errors.append(True)
        else:
            try:
                Validator.folder_required(values[DATA_STORE_FOLDER])
            except NotADirectoryError as excep:
                self.post_error_msg(f'{DATA_STORE_FOLDER} {excep.args[0]}')
                errors.append(True)
        try:
            Validator.required(values[INPUT_DATA_FOLDER])
        except ValueError as excep:
            self.post_error_msg(f'{INPUT_DATA_FOLDER} {excep.args[0]}')
            errors.append(True)
        else:
            try:
                Validator.folder_required(values[INPUT_DATA_FOLDER])
            except NotADirectoryError as excep:
                self.post_error_msg(f'{INPUT_DATA_FOLDER} {excep.args[0]}')
                errors.append(True)
        try:
            Validator.temp_data_source(values[TEMP_DATA_SOURCE])
        except ValueError as excep:
            self.post_error_msg(f'{TEMP_DATA_SOURCE} {excep.args[0]}.')
            errors.append(True)
        return any(errors)

    def on_save_validations(self,  values: dict) -> bool:
        errors: list[bool] = [self.on_change_validations(values)]
        if not any(errors):
            path: Path = Path(values[DATA_STORE_FOLDER])
            if not path.exists():
                create = sg.popup_ok_cancel(f"{values[DATA_STORE_FOLDER]} not found.  Create new folder?")
                if create == 'OK':
                    path.mkdir()
                else:
                    self.post_error_msg(f'{DATA_STORE_FOLDER} does not exist and creation was declined.')
                    errors.append(True)
        if not any(errors):
            path: Path = Path(values[INPUT_DATA_FOLDER])
            if not path.exists():
                create = sg.popup_ok_cancel(f"{values[INPUT_DATA_FOLDER]} not found.  Create new folder?")
                if create == 'OK':
                    path.mkdir()
                else:
                    self.post_error_msg(f'{INPUT_DATA_FOLDER} does not exist and creation was declined.')
                    errors.append(True)
        if len(values[POWER_USAGE_URL]) > 0:
            errors.append(self.url_bad(POWER_USAGE_URL, values[POWER_USAGE_URL]))
        return any(errors)

    def read(self) -> Settings | None:
        self.focus_element_key = DATA_STORE_FOLDER
        error = False
        while True:
            event, values = self.window.read()
            if event == CANCEL or event == sg.WIN_CLOSED:
                self.settings = None
                break
            elif event == EDIT_TEMP_SETTINGS:
                if values[TEMP_DATA_SOURCE] == TEMP_DATA_SOURCE_VISUAL_CROSSING:
                    vc_settings = VisualCrossingSettings(self.settings.temp_data_source_settings)
                    temp_window = VisualCrossingSettingsGUI(vc_settings, self.app_folder)
                    vc_settings = temp_window.read()
                    if vc_settings is not None:
                        self.settings.temp_data_source_settings = vc_settings.to_dict()
                elif values[TEMP_DATA_SOURCE] == TEMP_DATA_SOURCE_SC_ACIS:
                    ...
            elif event == SAVE:
                if not error:
                    error = self.on_save_validations(values)
                    if not error:
                        self.settings.data_store_folder = values[DATA_STORE_FOLDER]
                        self.settings.input_data_folder = values[INPUT_DATA_FOLDER]
                        self.settings.daily_dataframe_filter = values[DAILY_DATAFRAME_FILTER]
                        self.settings.hourly_dataframe_filter = values[HOURLY_DATAFRAME_FILTER]
                        self.settings.temp_data_source = values[TEMP_DATA_SOURCE]
                        self.settings.power_usage_url = values[POWER_USAGE_URL]
                        break
                else:
                    self.post_error_msg(f'You must correct errors before saving the settings.')
            else:
                if self.focus_element_key != self.window.FocusElement.Key:
                    error = self.on_change_validations(values)
                    self.focus_element_key = self.window.FocusElement.Key
        self.window.close()
        return self.settings


