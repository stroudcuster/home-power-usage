from cmath import isnan
from datetime import datetime
from http.client import HTTPResponse
import json
from pathlib import Path
import re
from urllib.request import urlopen
import pandas as pd

DATE_COL = 'Date'
MIN_TEMP_COL = 'Min'
MAX_TEMP_COL = 'Max'
AVE_TEMP_COL = 'Avg'


def to_float(x: str):
    return float(x.strip(','))


class TemperatureData:

    def __init__(self, source: str, data_frame: pd.DataFrame, from_date: datetime, to_date: datetime):
        self.source: str = source
        self.data_frame: pd.DataFrame = (
            data_frame)[(data_frame[DATE_COL] >= from_date) & (data_frame[DATE_COL] <= to_date)]
        self.from_date: datetime = from_date
        self.to_date: datetime = to_date


class TemperatureDataFactory:

    @classmethod
    def from_nws_spreadsheet(cls, data_path: Path, from_date: datetime, to_date: datetime):
        daily_temp_df: pd.DataFrame = pd.read_excel(data_path)
        daily_temp_df['Date'] = pd.to_datetime(daily_temp_df['Date'], format='%Y-%m-%d')
        return TemperatureData(source='NWS', data_frame=daily_temp_df, from_date=from_date, to_date=to_date)

    @classmethod
    def from_sc_acis_clipboard(self, source: str, from_date: datetime, to_date: datetime):
        daily_temp_df: pd.DataFrame = pd.read_clipboard()
        drop_list = ['AvgTemperatureDeparture,',
                     'HDD,',
                     'CDD,',
                     'Precipitation,',
                     'Snowfall,',
                     'SnowDepth',
                     ]
        daily_temp_df.drop(columns=drop_list, inplace=True)
        rename_map: dict[str, str] = {'Date,': DATE_COL,
                                      'MaxTemperature,': MAX_TEMP_COL,
                                      'MinTemperature,': MIN_TEMP_COL,
                                      'AvgTemperature,': AVE_TEMP_COL}

        daily_temp_df.rename(mapper=rename_map, axis=1, inplace=True)
        daily_temp_df[DATE_COL] = pd.to_datetime(daily_temp_df[DATE_COL], format='mixed')
        daily_temp_df[MIN_TEMP_COL] = daily_temp_df[MIN_TEMP_COL].apply(func=to_float)
        daily_temp_df[MAX_TEMP_COL] = daily_temp_df[MAX_TEMP_COL].apply(func=to_float)
        daily_temp_df[AVE_TEMP_COL] = daily_temp_df[AVE_TEMP_COL].apply(func=to_float)
        return TemperatureData(source=source, data_frame=daily_temp_df, from_date=from_date, to_date=to_date)

    @classmethod
    def from_visual_crossing(cls, latitude: int, longitude: int, from_date: datetime, to_date: datetime, passkey: str):
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/" \
            f"{latitude},{longitude}/{from_date.strftime('%Y-%m-%d')}/{to_date.strftime('%Y-%m-%d')}" \
            f"?key={passkey}&include=days&elements=datetime,tempmax,tempmin,temp"
        response: HTTPResponse = urlopen(url)
        payload = json.loads(response.read())
        daily_temps = payload['days']
        data: dict[str, list[datetime | float]] = {}
        data[DATE_COL]: list[datetime] = []
        data[MIN_TEMP_COL]: list[float] = []
        data[MAX_TEMP_COL]: list[float] = []
        data[AVE_TEMP_COL]: list[float] = []
        for daily_temp in daily_temps:
            data[DATE_COL].append(datetime.strptime(daily_temp['datetime'], '%Y-%m-%d'))
            data[MIN_TEMP_COL].append(daily_temp['tempmin'])
            data[MAX_TEMP_COL].append(daily_temp['tempmax'])
            data[AVE_TEMP_COL].append(daily_temp['temp'])
        daily_temp_df = pd.DataFrame(data)
        return TemperatureData(source="Visual Crossing", data_frame=daily_temp_df, from_date=from_date, to_date=to_date)

    def from_local(self, from_date: datetime, to_date: datetime):
        ...


