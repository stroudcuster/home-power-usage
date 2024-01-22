from collections import namedtuple
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from yaml import load, dump, YAMLObject, add_path_resolver
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

TEMP_DATA_SOURCE_VISUAL_CROSSING = 'Visual Crossing'
TEMP_DATA_SOURCE_SC_ACIS = 'SC ACIS'
TEMP_DATA_SOURCES = [TEMP_DATA_SOURCE_VISUAL_CROSSING, TEMP_DATA_SOURCE_SC_ACIS]


class Validator:
    @staticmethod
    def url_parse(url_str: str) -> namedtuple:
        url_parts: namedtuple = urlparse(url_str)
        if len(url_parts.scheme) == 0 or len(url_parts.netloc) == 0:
            raise ValueError(f'{url_str} is not a valid URL format.')
        else:
            return url_parts

    @staticmethod
    def url_open(url_str) -> None:
        try:
            urlopen(url_str)
        except ValueError:
            raise ValueError(f'{url_str} did not respond.')

    @staticmethod
    def vc_required(value: str) -> None:
        if len(value.strip()) == 0:
            raise ValueError('This is required to use Visual Crossing as a data source.')

    @staticmethod
    def latitude(value: str) -> None:
        try:
            float_value = float(value)
        except ValueError:
            raise ValueError('Latitude must be numeric.')
        if float_value < -90 or float_value > 90:
            raise ValueError('Latitude must be between -90 and 90.')

    @staticmethod
    def longitude(value: str) -> None:
        try:
            float_value = float(value)
            if float_value < -90 or float_value > 90:
                raise ValueError('Longitude must be between -90 and 90.')
        except ValueError:
            raise ValueError('Longitude must be numeric.')

    @staticmethod
    def required(value:str) -> None:
        if len(value.strip()) == 0:
            raise ValueError('This is a required field')

    @staticmethod
    def folder_required(value: str) -> None:
        path: Path = Path(value)
        if path.exists() and not path.is_dir():
            raise NotADirectoryError('This path must point to a folder.')

    @staticmethod
    def temp_data_source(value: str) -> None:
        if value not in TEMP_DATA_SOURCES:
            raise ValueError('Selection not valid.')


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

    def to_dict(self):
        return self._data


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


