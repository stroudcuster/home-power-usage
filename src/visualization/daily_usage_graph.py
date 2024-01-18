from datetime import datetime, timedelta
from pathlib import Path

from data_cruncher.usage_data import qtr_hr_times, qtr_hr_fields, DailyUsageData, DailyUsageDataFactory
from data_type import DataType

import matplotlib.pyplot as plt
import pandas as pd


class DailyUsageGraph:
    def __init__(self, usage_data: DailyUsageData,
                 usage_axes: plt.Axes, temp_axes: plt.Axes):
        self.usage_data: DailyUsageData = usage_data
        self.usage_axes: plt.Axes = usage_axes
        self.usage_axes.set_title(label='Actual Daily Usage with Temperature from '
                                  f'{self.usage_data.from_date.strftime("%m/%d/%Y")} to '
                                  f'{self.usage_data.to_date.strftime("%m/%d/%Y")}')
        dates: list[datetime] = []
        date_labels: list[str] = []
        date = self.usage_data.from_date
        dateinc: timedelta = timedelta(days=1)
        while date <= self.usage_data.to_date:
            dates.append(date)
            date_labels.append(date.strftime('%m/%d'))
            date = date + dateinc
        self.usage_axes.set_xticks(dates, labels=date_labels, rotation='vertical')
        self.usage_axes.set_ylabel('Usage in Kilowatt Hours')
        self.usage_axes.plot('Date', 'Total', data=self.usage_data.data_frame, label='Actual Usage')
        self.usage_axes.legend()
        self.temp_axes: plt.Axes = temp_axes
        self.temp_axes.set_xticks(dates, labels=date_labels, rotation='vertical')
        self.temp_axes.set_ylabel('Temperature')
        self.temp_axes.plot('Date', 'Average', data=self.usage_data.data_frame, label='Average Temp')
        self.temp_axes.legend()


if __name__ == '__main__':
    usage_path = Path('data/power-usage.xlsx')
    temp_path = Path('data/temp-data.xlsx')
    daily_usage_data = DailyUsageDataFactory.from_spreadsheet(hourly_usage_path=usage_path,
                                                              daily_temp_path=temp_path,
                                                              from_date=datetime(year=2023, month=12, day=31),
                                                              to_date=datetime(year=2024, month=1, day=12))
    fig, ax_dict = plt.subplot_mosaic([['usage_graph'], ['temp_graph']])
    dug = DailyUsageGraph(usage_data=daily_usage_data,
                          usage_axes=ax_dict['usage_graph'],
                          temp_axes=ax_dict['temp_graph'])
    plt.show()
    pass
