import time
import datetime
import os
import sys
import csv
from pylogix import PLC

class TrendLogger:
    def __init__(self, device_number, trend_desc, cycles, cycle_time, buffer_size, plc_ip, tags):
        self.device_number = device_number
        self.trend_desc = trend_desc
        self.cycles = cycles
        self.cycle_time = cycle_time
        self.buffer_size = buffer_size
        self.plc_ip = plc_ip
        self.tags = tags

        self.col_tags = ['Index', 'DateTime'] + tags
        self.trend_start_time = time.time()
        self.todays_date = datetime.datetime.today().strftime('%Y-%m-%d')
        self.full_path = f'{self.todays_date}/{self.device_number}/'
        self.rel_path = f"{self.full_path}{self.device_number}__{self.trend_desc}__{self.trend_start_time}.csv"
        self.data_buffer = []

        self._setup_logging_directory()
        self._create_csv_file()

    def _setup_logging_directory(self):
        if not os.path.exists(self.full_path):
            os.makedirs(self.full_path)
            print(f"'{self.full_path}' dir created.")

    def _create_csv_file(self):
        with open(self.rel_path, 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', lineterminator='\n', quotechar='/', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(self.col_tags)
            print(f"'{self.rel_path}' created.")
            print(f'\n{self.col_tags}')

    def log_trend(self):
        with PLC() as comm:
            comm.IPAddress = self.plc_ip
            for cycle in range(self.cycles):
                ret = comm.Read(self.tags)
                row = [x.Value for x in ret]
                row.insert(0, str(datetime.datetime.now()))
                row.insert(0, cycle)
                self.data_buffer.append(row)
                try:
                    if len(self.data_buffer) >= self.buffer_size:
                        self._write_to_csv()
                except KeyboardInterrupt:
                    sys.exit()
                except:
                    print("Failed to write to file...")
                    pass
                time.sleep(self.cycle_time)

    def _write_to_csv(self):
        with open(self.rel_path, 'a') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', lineterminator='\n', quotechar='/', quoting=csv.QUOTE_MINIMAL)
            for row_in_buffer in self.data_buffer:
                csv_writer.writerow(row_in_buffer)
                print(row_in_buffer)
            self.data_buffer = []

if __name__ == "__main__":
    device_number = "Blend B"
    trend_desc = "Phase 1"
    cycles = 99999
    cycle_time = 1
    buffer_size = 10
    plc_ip = '192.168.0.1'
    tags = ["BLD01_PIT01_00.SMTH", "BLD01_PIT04_00.SMTH", "BLD01_PIT05_00.SMTH", "BLD01_PT21_00.SMTH",
            "BLD01_PT21_02.SMTH", "BLD01_PT22_00.SMTH", "BLD01_PT22_02.SMTH", "BLD01_PIT00_00.SMTH",
            "BLD01_P21_00_PV.SMTH", "BLD01_P22_00_PV.SMTH", "BLD01_TT21_00.SMTH", "BLD01_TT21_01.SMTH",
            "BLD01_TT22_00.SMTH", "BLD01_TT22_01.SMTH", "BLD01_TT40_00.SMTH", "BLD01_TT41_00.SMTH",
            "BLD01_TT42_00.SMTH", "BLD01_TT43_00.SMTH", "BLD01_TT44_00.SMTH", "BLD01_PT80_00.SMTH",
            "BLD01_PT80_01.SMTH", "BLD01_FT80_00.SMTH", "BLD01_FT80_01.SMTH", "BLD01_PT40_00.SMTH",
            "BLD01_PT40_01.SMTH", "BLD01_FT40_00.SMTH", "BLD01_FT40_01.SMTH", "BLD01_PT41_00.SMTH",
            "BLD01_PT41_01.SMTH", "BLD01_FT41_00.SMTH", "BLD01_FT41_01.SMTH", "BLD01_PT42_00.SMTH",
            "BLD01_PT42_01.SMTH", "BLD01_FT42_00.SMTH", "BLD01_FT42_01.SMTH", "BLD01_PT43_00.SMTH",
            "BLD01_PT43_01.SMTH", "BLD01_FT43_00.SMTH", "BLD01_FT43_01.SMTH", "BLD01_PT44_00.SMTH",
            "BLD01_PT44_01.SMTH", "BLD01_FT44_00.SMTH", "BLD01_FT44_01.SMTH", "BLD01_AT21_01.SMTH",
            "BLD01_AT22_01.SMTH", "BLD01_AT62_00.SMTH", "BLD01_AT63_00.SMTH", "BLD01_AT62_01.SMTH",
            "BLD01_AT63_01.SMTH", "BLD01_WT21_00.SMTH", "BLD01_WT22_00.SMTH", "BLD01_AT21_00.SMTH",
            "BLD01_AT22_00.SMTH", "BLD01_AT40_00.SMTH", "BLD01_AT41_00.SMTH", "BLD01_AT42_00.SMTH",
            "BLD01_AT43_00.SMTH", "BLD01_AT44_00.SMTH"]

    trend_logger = TrendLogger(device_number, trend_desc, cycles, cycle_time, buffer_size, plc_ip, tags)
    trend_logger.log_trend()