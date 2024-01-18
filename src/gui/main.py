import PySimpleGUIQt as sg

SETTINGS = "Settings"
EXIT = 'Exit'
CREATE_DS = 'Create Data Store'
DELETE_DS = 'Delete Data Stores'
SELECT_DS = 'Select Data Store'
CREATE_DF = 'Create Data Frames'
MERGE_DF = 'Merge Data Frames'
DELETE_DF = 'Delete Data Frames'
DAILY_USAGE = 'Daily Usage'
HOURLY_USAGE = 'Hourly Usage'

OUTPUT_KEY = 'Output'


class MainGUI:

    def __init__(self):
        menu_def = [['Misc', [SETTINGS, EXIT]],
                    ['Data Stores', [CREATE_DS, DELETE_DS, SELECT_DS]],
                    ['Data Frames', [CREATE_DF, MERGE_DF, DELETE_DF]],
                    ['Charts', [DAILY_USAGE, HOURLY_USAGE]]]
        layout = [[sg.Menu(menu_definition=menu_def)],
                  [sg.Output(size_px=(500, 500), key=OUTPUT_KEY)]]
        self.window = sg.Window("Home Power Usage", layout, default_element_size=(12, 1), auto_size_text=False,
                                auto_size_buttons=False,
                                default_button_element_size=(12, 1))

    def settings(self):
        self.window.Element(OUTPUT_KEY).update(f'{SETTINGS} selected.')

    def create_data_store(self):
        self.window.Element(OUTPUT_KEY).update(f'{CREATE_DS} selected.')

    def delete_data_store(self):
        self.window.Element(OUTPUT_KEY).update(f'{DELETE_DS} selected.')

    def select_data_store(self):
        self.window.Element(OUTPUT_KEY).update(f'{SELECT_DS} selected.')

    def create_data_frame(self):
        self.window.Element(OUTPUT_KEY).update(f'{CREATE_DF} selected.')

    def merge_data_frame(self):
        self.window.Element(OUTPUT_KEY).update(f'{MERGE_DF} selected.')

    def delete_data_frame(self):
        self.window.Element(OUTPUT_KEY).update(f'{DELETE_DF} selected.')

    def daily_usage_chart(self):
        self.window.Element(OUTPUT_KEY).update(f'{DAILY_USAGE} selected.')

    def hourly_usage_chart(self):
        self.window.Element(OUTPUT_KEY).update(f'{HOURLY_USAGE} selected.')

    def read(self) -> bool:
        event, values = self.window.read()
        if event == SETTINGS:
            self.settings()
        elif event in [sg.WIN_CLOSED, EXIT]:
            return True
        elif event == CREATE_DS:
            self.create_data_store()
        elif event == DELETE_DS:
            self.delete_data_store()
        elif event == SELECT_DS:
            self.select_data_store()
        elif event == CREATE_DF:
            self.create_data_frame()
        elif event == MERGE_DF:
            self.merge_data_frame()
        elif event == DELETE_DF:
            self.delete_data_frame()
        elif event == DAILY_USAGE:
            self.daily_usage_chart()
        elif event == HOURLY_USAGE:
            self.hourly_usage_chart()
        else:
            self.window.Element(OUTPUT_KEY).update(f'{event} is not a valid event')


if __name__ == '__main__':
    gui = MainGUI()
    while True:
        if gui.read():
            break

