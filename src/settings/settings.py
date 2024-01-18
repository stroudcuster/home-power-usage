from pathlib import Path

from yaml import load, dump, YAMLObject, add_path_resolver
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

TEMP_DATA_SOURCES = ['Visual Crossing', 'SC ACIS']
class Settings:
    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data

    @property
    def data_store_folder(self):
        return self._data['data_store_folder']

    @data_store_folder.setter
    def data_store_folder(self, data_store_folder):
        self._data['data_store_folder'] = data_store_folder

    @property
    def input_data_folder(self):
        return self._data['input_data_folder']

    @input_data_folder.setter
    def input_data_folder(self, input_data_folder):
        self._data['input_data_folder'] = input_data_folder

    @property
    def daily_dataframe_filter(self):
        return self._data['daily_dataframe_filter']

    @daily_dataframe_filter.setter
    def daily_dataframe_filter(self, daily_dataframe_filter):
        self._data['daily_dataframe_filter'] = daily_dataframe_filter

    @property
    def hourly_dataframe_filter(self):
        return self._data['hourly_dataframe_filter']

    @hourly_dataframe_filter.setter
    def hourly_dataframe_filter(self, hourly_dataframe_filter):
        self._data['hourly_data_filter'] = hourly_dataframe_filter

    @property
    def temp_data_source(self):
        return self._data['temp_data_source']

    @temp_data_source.setter
    def temp_data_source(self, temp_data_source):
        self._data['temp_data_source'] = temp_data_source

    @property
    def temp_data_source_settings(self):
        return self._data['temp_data_source_settings']

    @temp_data_source_settings.setter
    def temp_data_source_settings(self, temp_data_source_settings):
        self._data['temp_data_source_settings'] = temp_data_source_settings

    @property
    def power_usage_url(self):
        return self._data['power_usage_url']

    @power_usage_url.setter
    def power_usage_url(self, power_usage_url):
        self._data['power_usage_url'] = power_usage_url

    def __repr__(self):
        return f'{self.__class__.__name__}(data={self._data})'


class VisualCrossingSettings:
    def __init__(self, data):
        self._data = data

    @property
    def url(self):
        return self._data['url']

    @url.setter
    def url(self, url):
        self._data['url'] = url

    @property
    def latitude(self):
        return self._data['latitude']

    @latitude.setter
    def latitude(self, latitude):
        self._data['latitude'] = latitude

    @property
    def longitude(self):
        return self._data['longitude']

    @longitude.setter
    def longitude(self, longitude):
        self._data['longitude'] = longitude

    @property
    def api_key(self):
        return self._data['api_key']

    @api_key.setter
    def api_key(self, api_key):
        self._data['api_key'] = api_key


def load_settings(yaml_file: Path) -> Settings:
    if yaml_file is not None and yaml_file.exists():
        with yaml_file.open(mode='r') as f:
            data = load(stream=f, Loader=Loader)
            return Settings(data)

    else:
        raise FileNotFoundError


def save_settings(settings: Settings, yaml_file: Path) -> None:
    with yaml_file.open(mode='w') as f:
        dump(data=settings.data, stream=f, Dumper=Dumper)


