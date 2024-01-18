from datetime import datetime
from pathlib import Path

from data_cruncher.usage_data import qtr_hr_times, qtr_hr_fields, HourlyUsageData, HourlyUsageDataFactory
from data_type import DataType

import matplotlib.pyplot as plt


class HourlyUsageGraph:
    def __init__(self, usage_data: HourlyUsageData,
                 axes: plt.Axes,
                 show: tuple[DataType, ...]):
        self.usage_data: HourlyUsageData = usage_data
        self.axes: plt.Axes = axes
        self.show = show
        self.axes.set_title(label=f'Hourly Usage Summary: '
                                  f'{self.usage_data.from_date.strftime("%m/%d/%Y")} to '
                                  f'{self.usage_data.to_date.strftime("%m/%d/%Y")}')
        self.axes.set_xlabel('Time of Day')
        hr_times: list[datetime] = []
        hr_labels: list[str] = []
        for idx, time in enumerate(qtr_hr_times):
            if time.minute == 0:
                hr_times.append(time)
                hr_labels.append(qtr_hr_fields[idx])
        self.axes.set_xticks(hr_times, labels=hr_labels, rotation='vertical')
        self.axes.tick_params(axis='x', width=20)
        self.axes.set_ylabel('Usage in Kilowatt Hours')
        if DataType.MAX in self.show:
            self.axes.plot('time', 'usage', data=self.usage_data.max(), label='Max')
        if DataType.MIN in self.show:
            self.axes.plot('time', 'usage', data=self.usage_data.min(), label='Min')
        if DataType.AVERAGE in self.show:
            self.axes.plot('time', 'usage', data=self.usage_data.mean(), label='Average')
        if DataType.ACTUAL in self.show:
            self.axes.plot('time', 'usage', data=self.usage_data.actual(), label='Actual')
        self.axes.legend()
        self.axes.plot()


if __name__ == '__main__':
    usage_path = Path('data/power-usage.xlsx')
    hourly_usage_data = HourlyUsageDataFactory.from_spreadsheet(hourly_usage_path=usage_path,
                                                                from_date=datetime(year=2024, month=1, day=1),
                                                                to_date=datetime(year=2024, month=1, day=12))
    fig, ax = plt.subplots()
    hrg = HourlyUsageGraph(usage_data=hourly_usage_data, axes=ax, show=(DataType.AVERAGE, ))
    plt.show()
    pass
