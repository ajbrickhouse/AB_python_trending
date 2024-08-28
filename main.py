from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import threading
import time
import datetime
import os
import csv
from pylogix import PLC
import uuid  # To generate unique thread IDs

app = Flask(__name__)
app.secret_key = 'some_secret_key'

# Global variables to control the script
script_threads = {}  # Dictionary to keep track of active threads
data_buffer = []
tags = ["BLD01_PIT01_00.SMTH", "BLD01_PIT04_00.SMTH"]  # Default tags

def run_trend_collection(device_number, trend_desc, cycles, cycle_time, buffer_size, plc_ip, thread_id):
    global script_threads, data_buffer

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

    with PLC() as comm:
        comm.IPAddress = plc_ip

        for cycle in range(cycles):
            if thread_id not in script_threads:
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

    # Remove the thread from the dictionary after completion
    if thread_id in script_threads:
        del script_threads[thread_id]

@app.route('/')
def index():
    return render_template('index.html', tags=tags, script_threads=script_threads)

@app.route('/start', methods=['POST'])
def start_script():
    global script_threads
    device_number = request.form['device_number']
    trend_desc = request.form['trend_desc']
    cycles = int(request.form['cycles'])
    cycle_time = int(request.form['cycle_time'])
    buffer_size = int(request.form['buffer_size'])
    plc_ip = request.form['plc_ip']

    # Check for duplicate device number and description
    for thread_info in script_threads.values():
        if thread_info['device_number'] == device_number and thread_info['trend_desc'] == trend_desc:
            flash('A script with the same device number and description is already running!')
            return redirect(url_for('index'))
    
    # Generate a unique thread ID
    thread_id = str(uuid.uuid4())

    # Store the thread info
    script_threads[thread_id] = {
        'device_number': device_number,
        'trend_desc': trend_desc,
        'thread': threading.Thread(target=run_trend_collection, args=(device_number, trend_desc, cycles, cycle_time, buffer_size, plc_ip, thread_id))
    }

    # Start the thread
    script_threads[thread_id]['thread'].start()
    flash('Script started successfully!')

    return redirect(url_for('index'))

@app.route('/stop_thread/<string:thread_id>', methods=['POST'])
def stop_thread(thread_id):
    global script_threads
    if thread_id in script_threads:
        # Simply remove the thread from the dictionary to stop it
        del script_threads[thread_id]
        flash(f'Script stopped successfully!')
    else:
        flash('No script found with that ID!')

    return redirect(url_for('index'))

@app.route('/add_tag', methods=['POST'])
def add_tag():
    tags_input = request.form['tags']
    new_tags = tags_input.splitlines()  # Split input by new lines

    for tag in new_tags:
        tag = tag.strip()  # Remove any leading/trailing whitespace
        if tag and tag not in tags:
            tags.append(tag)

    return redirect(url_for('index'))

@app.route('/remove_tag/<string:tag>', methods=['POST'])
def remove_tag(tag):
    if tag in tags:
        tags.remove(tag)
    return redirect(url_for('index'))

@app.route('/data')
def get_data():
    global data_buffer
    sorted_data = sorted(data_buffer[-10:], key=lambda x: x[0])  # Use the appropriate index for sorting
    return jsonify(sorted_data)  # Return the last 10 rows of sorted data

if __name__ == '__main__':
    app.run(debug=True)
