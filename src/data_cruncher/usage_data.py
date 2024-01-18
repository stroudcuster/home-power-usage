from cmath import isnan
from datetime import datetime, timedelta
from pathlib import Path
import re

import pandas as pd
import matplotlib.pyplot as plt

from temperature_data import TemperatureData

#
# build a list of time interval column headings
#
qtr_hr_fields: list[str] = []
qtr_hr_times: list[datetime] = []
today = datetime.today()
dt = datetime(year=today.year, month=today.month, day=today.day, hour=0, minute=0, second=0)
delta = timedelta(hours=0, minutes=15, seconds=0)
for i in range(0, 96):
    fmt_time = dt.strftime('%I:%M %p')
    if fmt_time[0:1] == '0':
        fmt_time = fmt_time[1:]
    qtr_hr_fields.append(fmt_time)
    qtr_hr_times.append(dt)
    dt = dt + delta


class HourlyUsageData:
    def __init__(self, from_date: datetime, to_date: datetime, data_frame: pd.DataFrame):
        self.name = f'Hourly-{from_date.strftime("%m/%d/%Y")}-{to_date.strftime("%m/%d/%Y")}'
        self.from_date = from_date
        self.to_date = to_date
        self.data_frame = data_frame

    def min(self) -> pd.DataFrame:
        return self.data_frame[(self.data_frame['type'] == 'min')]

    def mean(self) -> pd.DataFrame:
        return self.data_frame[self.data_frame['type'] == 'mean']

    def max(self) -> pd.DataFrame:
        return self.data_frame[self.data_frame['type'] == 'max']

    def actual(self) -> pd.DataFrame:
        return self.data_frame[self.data_frame['type'] == 'actual']

    def save(self, datastore_path: Path):
        ds = pd.HDFStore(datastore_path.__str__())
        ds[self.name] = self.data_frame
        ds.close()

    def merge(self, other):
        self.data_frame.merg(other.data_frame)


class DailyUsageData:
    def __init__(self, from_date: datetime, to_date: datetime, data_frame: pd.DataFrame):
        self.name = f'Daily-{from_date.strftime("%m/%d/%Y")}-{to_date.strftime("%m/%d/%Y")}'
        self.from_date = from_date
        self.to_date = to_date
        self.data_frame = data_frame[(data_frame['Date'] >= from_date) & (data_frame['Date'] <= to_date)]

    def save(self, datastore_path: Path):
        ds = pd.HDFStore(datastore_path.__str__())
        ds[self.name] = self.data_frame
        ds.close()

    def merge(self, other):
        self.data_frame.merge(other.data_frame)


class HourlyUsageDataFactory:
    @classmethod
    def from_spreadsheet(cls, hourly_usage_path: Path, from_date: datetime, to_date: datetime):
        # Load hourly usage spreadsheet and drop unneeded columns
        hourly_usage_df: pd.DataFrame = pd.read_excel(hourly_usage_path)
        hourly_usage_df.drop(columns=['Account Number', 'Meter Number'], inplace=True)
        # Get from and to dates from the hourly usage data
        date_range = hourly_usage_df['Date'].agg(['min', 'max'])
        source_from_date: datetime = datetime(year=date_range['min'].year,
                                              month=date_range['min'].month,
                                              day=date_range['min'].day)
        source_to_date: datetime = datetime(year=date_range['max'].year,
                                            month=date_range['max'].month,
                                            day=date_range['max'].day)
        #
        # assemble a pivot table with a row for each usage time interval
        #
        # create a Series containing the average usage for each time interval
        agg_df = hourly_usage_df[
            (hourly_usage_df['Date'] >= from_date) & (hourly_usage_df['Date'] <= to_date)][qtr_hr_fields].agg(['min', 'mean', 'max'])
        # build lists for actual usage, date and entry type ('mean' or 'actual')
        usage_data: list[float]= []
        usage_index: list[datetime] = []
        usage_type: list[str] = []
        for idx, field in enumerate(qtr_hr_fields):
            for usage in hourly_usage_df[field].values:
                if not isnan(usage):
                    usage_data.append(usage)
                    usage_index.append(qtr_hr_times[idx])
                    usage_type.append('actual')
            usage_data.append(agg_df[field]['min'])
            usage_index.append(qtr_hr_times[idx])
            usage_type.append('min')
            usage_data.append(agg_df[field]['mean'])
            usage_index.append(qtr_hr_times[idx])
            usage_type.append('mean')
            usage_data.append(agg_df[field]['max'])
            usage_index.append(qtr_hr_times[idx])
            usage_type.append('max')
        # create Series objects for actual usage, date and entry type
        time_series: pd.Series = pd.Series(data=usage_index, dtype='datetime64[ns]')
        usage_series: pd.Series = pd.Series(data=usage_data, dtype='float64')
        type_series: pd.Series = pd.Series(data=usage_type, dtype='object')
        # create a DataFrame using the Series created above
        usage_df = pd.DataFrame({'time': time_series, 'usage': usage_series, 'type': type_series})
        return HourlyUsageData(from_date=from_date, to_date=to_date, data_frame=usage_df)

    @classmethod
    def from_datastore(cls, datastore_path: Path, name: str) -> HourlyUsageData:
        # extract from and to dates from data store entry name
        regex = re.compile('Hourly-(\d{2}/\d{2}/\d{4})-(\d{2}/\d{2}/\d{4})')
        match = regex.match(name)
        from_date_str = match.groups()[0]
        to_date_str = match.groups()[1]
        from_date: datetime = datetime(year=from_date_str[6:],
                                       month=from_date_str[0:2],
                                       day=from_date_str[3:5])
        to_date: datetime = datetime(year=to_date_str[6:],
                                     month=to_date_str[0:2],
                                     day=to_date_str[3:5])
        with pd.HDFStore(datastore_path.__str__()) as ds:
            usage_df = ds[name]
        return HourlyUsageData(from_date=from_date, to_date=to_date, data_frame=usage_df)


class DailyUsageDataFactory:
    @classmethod
    def from_spreadsheet(cls, hourly_usage_path: Path, daily_temp_data: TemperatureData, from_date: datetime, to_date: datetime):
        # Load hourly usage spreadsheet and drop unneeded columns
        daily_usage_df: pd.DataFrame = pd.read_excel(hourly_usage_path)
        drop_fields: list[str] = ['Account Number', 'Meter Number', 'Min', 'Max'] + qtr_hr_fields
        daily_usage_df.drop(columns=drop_fields, inplace=True)
        # Get from and to dates from the hourly usage data
        date_range = daily_usage_df['Date'].agg(['min', 'max'])
        source_from_date: datetime = datetime(year=date_range['min'].year,
                                              month=date_range['min'].month,
                                              day=date_range['min'].day)
        source_to_date: datetime = datetime(year=date_range['max'].year,
                                            month=date_range['max'].month,
                                            day=date_range['max'].day)
        # Merge daily temp data into the daily usage data
        usage_and_temp_df = daily_usage_df.merge(how='left',
                                                 on='Date',
                                                 right=daily_temp_data.data_frame)

        return DailyUsageData(from_date=from_date, to_date=to_date, data_frame=usage_and_temp_df)

    @classmethod
    def from_datastore(cls, datastore_path: Path, name: str) -> DailyUsageData:
        # extract from and to dates from data store entry name
        regex = re.compile('Daily-(\d{2}/\d{2}/\d{4})-(\d{2}/\d{2}/\d{4})')
        match = regex.match(name)
        from_date_str = match.groups()[0]
        to_date_str = match.groups()[1]
        from_date: datetime = datetime(year=from_date_str[6:],
                                       month=from_date_str[0:2],
                                       day=from_date_str[3:5])
        to_date: datetime = datetime(year=to_date_str[6:],
                                     month=to_date_str[0:2],
                                     day=to_date_str[3:5])
        with pd.HDFStore(datastore_path.__str__()) as ds:
            usage_df = ds[name]
        return DailyUsageData(from_date=from_date, to_date=to_date, data_frame=usage_df)


if __name__ == '__main__':
    usage_path = Path('data/power-usage.xlsx')
    hourly_usage_data = HourlyUsageDataFactory.from_spreadsheet(hourly_usage_path=usage_path)
    temp_path = Path('data/temp-data.xlsx')
    daily_usage_data = DailyUsageDataFactory.from_spreadsheet(hourly_usage_path=usage_path,
                                                              daily_temp_path=temp_path,
                                                              from_date=datetime(year=2023, month=11, day=1),
                                                              to_date=datetime(year=2023, month=11, day=30))
    daily_usage_data.data_frame.plot.line(x='Date', y='Total')
    plt.show()
    #datastore_path = Path('data/test_data.h5')
    #hourly_usage_data.save(datastore_path)
    #daily_usage_data.save(datastore_path)
