from flask import Flask, render_template, request, redirect, url_for, flash
import threading
import time
import datetime
import os
import csv
from pylogix import PLC

app = Flask(__name__)
app.secret_key = 'some_secret_key'

# Global variable to control the script
script_running = False
script_thread = None

def run_trend_collection(device_number, trend_desc, cycles, cycle_time, buffer_size, plc_ip, tags):
    global script_running
    script_running = True
    
    col_tags = tags.copy()
    col_tags.insert(0, 'DateTime')
    col_tags.insert(0, 'Index')

    trend_start_time = time.time()
    todays_date = datetime.datetime.today().strftime('%Y-%m-%d')
    full_path = f'{todays_date}/{device_number}/'

    if not os.path.exists(full_path):
        os.makedirs(full_path)

    rel_path = f"{todays_date}/{device_number}/{device_number}__{trend_desc}__{trend_start_time}.csv"
    with open(rel_path, 'w') as csv_file:
        csv_file = csv.writer(csv_file, delimiter=',', lineterminator='\n', quotechar='/', quoting=csv.QUOTE_MINIMAL)
        csv_file.writerow(col_tags)

    data_buffer = []

    with PLC() as comm:
        comm.IPAddress = plc_ip

        for cycle in range(cycles):
            if not script_running:
                break

            ret = comm.Read(tags)
            row = [x.Value for x in ret]
            row.insert(0, str(datetime.datetime.now()))
            row.insert(0, cycle)
            data_buffer.append(row)

            if len(data_buffer) >= buffer_size:
                with open(rel_path, 'a') as csv_file:
                    csv_file = csv.writer(csv_file, delimiter=',', lineterminator='\n', quotechar='/', quoting=csv.QUOTE_MINIMAL)
                    for row_in_buffer in data_buffer:
                        csv_file.writerow(row_in_buffer)

                    data_buffer = []

            time.sleep(cycle_time)

    script_running = False

@app.route('/')
def index():
    return render_template('index.html', script_running=script_running)

@app.route('/start', methods=['POST'])
def start_script():
    global script_thread
    if not script_running:
        device_number = request.form['device_number']
        trend_desc = request.form['trend_desc']
        cycles = int(request.form['cycles'])
        cycle_time = int(request.form['cycle_time'])
        buffer_size = int(request.form['buffer_size'])
        plc_ip = request.form['plc_ip']

        tags = ["BLD01_PIT01_00.SMTH", "BLD01_PIT04_00.SMTH", "BLD01_PIT05_00.SMTH", "BLD01_PT21_00.SMTH", "BLD01_PT21_02.SMTH",
                "BLD01_PT22_00.SMTH", "BLD01_PT22_02.SMTH", "BLD01_PIT00_00.SMTH", "BLD01_P21_00_PV.SMTH", "BLD01_P22_00_PV.SMTH",
                "BLD01_TT21_00.SMTH", "BLD01_TT21_01.SMTH", "BLD01_TT22_00.SMTH", "BLD01_TT22_01.SMTH", "BLD01_TT40_00.SMTH",
                "BLD01_TT41_00.SMTH", "BLD01_TT42_00.SMTH", "BLD01_TT43_00.SMTH", "BLD01_TT44_00.SMTH", "BLD01_PT80_00.SMTH",
                "BLD01_PT80_01.SMTH", "BLD01_FT80_00.SMTH", "BLD01_FT80_01.SMTH", "BLD01_PT40_00.SMTH", "BLD01_PT40_01.SMTH",
                "BLD01_FT40_00.SMTH", "BLD01_FT40_01.SMTH", "BLD01_PT41_00.SMTH", "BLD01_PT41_01.SMTH", "BLD01_FT41_00.SMTH",
                "BLD01_FT41_01.SMTH", "BLD01_PT42_00.SMTH", "BLD01_PT42_01.SMTH", "BLD01_FT42_00.SMTH", "BLD01_FT42_01.SMTH",
                "BLD01_PT43_00.SMTH", "BLD01_PT43_01.SMTH", "BLD01_FT43_00.SMTH", "BLD01_FT43_01.SMTH", "BLD01_PT44_00.SMTH",
                "BLD01_PT44_01.SMTH", "BLD01_FT44_00.SMTH", "BLD01_FT44_01.SMTH", "BLD01_AT21_01.SMTH", "BLD01_AT22_01.SMTH",
                "BLD01_AT62_00.SMTH", "BLD01_AT63_00.SMTH", "BLD01_AT62_01.SMTH", "BLD01_AT63_01.SMTH", "BLD01_WT21_00.SMTH",
                "BLD01_WT22_00.SMTH", "BLD01_AT21_00.SMTH", "BLD01_AT22_00.SMTH", "BLD01_AT40_00.SMTH", "BLD01_AT41_00.SMTH",
                "BLD01_AT42_00.SMTH", "BLD01_AT43_00.SMTH", "BLD01_AT44_00.SMTH"]

        script_thread = threading.Thread(target=run_trend_collection, args=(device_number, trend_desc, cycles, cycle_time, buffer_size, plc_ip, tags))
        script_thread.start()
        flash('Script started successfully!')
    else:
        flash('Script is already running!')

    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop_script():
    global script_running
    if script_running:
        script_running = False
        flash('Script stopped successfully!')
    else:
        flash('No script is running!')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
