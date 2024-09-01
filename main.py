from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'some_secret_key'

# Variable for the database name
DATABASE_NAME = 'database.db'

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

def execute_query(query, args=(), fetchone=False, fetchall=False):
    conn = get_db_connection()
    cursor = conn.execute(query, args)
    conn.commit()
    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    conn.close()
    return result

# Route to manage systems
@app.route('/manage_systems', methods=['GET', 'POST'])
def manage_systems():
    if request.method == 'POST':
        system_id = request.form.get('system_id')
        device_number = request.form['device_number']
        description = request.form['description']
        plc_ip = request.form['plc_ip']
        subnet = request.form['subnet']

        if system_id:  # If system_id exists, it's an edit operation
            execute_query('UPDATE Systems SET device_number = ?, description = ?, plc_ip = ?, subnet = ? WHERE id = ?',
                          (device_number, description, plc_ip, subnet, system_id))
            flash('System updated successfully!', 'success')
        else:  # Otherwise, it's an add operation
            execute_query('INSERT INTO Systems (device_number, description, plc_ip, subnet) VALUES (?, ?, ?, ?)',
                          (device_number, description, plc_ip, subnet))
            flash('System added successfully!', 'success')

        return redirect(url_for('manage_systems'))

    systems = execute_query('SELECT * FROM Systems', fetchall=True)
    return render_template('manage_systems.html', systems=systems)

@app.route('/edit_system/<int:id>', methods=['GET', 'POST'])
def edit_system(id):
    system = execute_query('SELECT * FROM Systems WHERE id = ?', (id,), fetchone=True)

    if request.method == 'POST':
        device_number = request.form['device_number']
        description = request.form['description']
        plc_ip = request.form['plc_ip']
        subnet = request.form['subnet']

        execute_query('UPDATE Systems SET device_number = ?, description = ?, plc_ip = ?, subnet = ? WHERE id = ?',
                      (device_number, description, plc_ip, subnet, id))
        flash('System updated successfully!', 'success')
        return redirect(url_for('manage_systems'))

    return render_template('edit_system.html', system=system)

@app.route('/delete_system/<int:id>', methods=['POST'])
def delete_system(id):
    execute_query('DELETE FROM Systems WHERE id = ?', (id,))
    flash('System deleted successfully!', 'success')
    return redirect(url_for('manage_systems'))

# Route to manage tag sets
@app.route('/manage_tags', methods=['GET', 'POST'])
def manage_tags():
    if request.method == 'POST':
        tag_set_id = request.form.get('tag_set_id')
        tag_set_name = request.form['tag_set_name']
        tags = request.form['tags']

        if tag_set_id:  # If tag_set_id exists, it's an edit operation
            execute_query('UPDATE Tags SET tag_set_name = ?, tags = ? WHERE id = ?',
                          (tag_set_name, tags, tag_set_id))
            flash('Tag set updated successfully!', 'success')
        else:  # Otherwise, it's an add operation
            execute_query('INSERT INTO Tags (tag_set_name, tags) VALUES (?, ?)',
                          (tag_set_name, tags))
            flash('Tag set added successfully!', 'success')

        return redirect(url_for('manage_tags'))

    tag_sets = execute_query('SELECT * FROM Tags', fetchall=True)
    return render_template('manage_tags.html', tag_sets=tag_sets)

@app.route('/edit_tag_set/<int:id>', methods=['GET', 'POST'])
def edit_tag_set(id):
    tag_set = execute_query('SELECT * FROM Tags WHERE id = ?', (id,), fetchone=True)

    if request.method == 'POST':
        tag_set_name = request.form['tag_set_name']
        tags = request.form['tags']

        execute_query('UPDATE Tags SET tag_set_name = ?, tags = ? WHERE id = ?',
                      (tag_set_name, tags, id))
        flash('Tag set updated successfully!', 'success')
        return redirect(url_for('manage_tags'))

    return render_template('edit_tag_set.html', tag_set=tag_set)

@app.route('/delete_tag_set/<int:id>', methods=['POST'])
def delete_tag_set(id):
    execute_query('DELETE FROM Tags WHERE id = ?', (id,))
    flash('Tag set deleted successfully!', 'success')
    return redirect(url_for('manage_tags'))

@app.route('/trend_control', methods=['GET', 'POST'])
def trend_control():
    if request.method == 'POST':
        trend_id = request.form.get('trend_id')
        device_number = request.form['device_number']
        tags = request.form['tags']
        cycles = request.form['cycles']
        cycle_time = request.form['cycle_time']
        buffer_size = request.form['buffer_size']
        description = request.form['description']

        if trend_id:  # If trend_id exists, it's an edit operation
            execute_query('''
                UPDATE Trends 
                SET device_number = ?, tags = ?, cycles = ?, cycle_time = ?, buffer_size = ?, description = ?
                WHERE id = ?''',
                (device_number, tags, cycles, cycle_time, buffer_size, description, trend_id))
            flash('Trend updated successfully!', 'success')
        else:  # Otherwise, it's an add operation
            execute_query('''
                INSERT INTO Trends (device_number, tags, cycles, cycle_time, buffer_size, description)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (device_number, tags, cycles, cycle_time, buffer_size, description))
            flash('Trend added successfully!', 'success')

        return redirect(url_for('trend_control'))

    trends = execute_query('SELECT * FROM Trends', fetchall=True)
    return render_template('trend_control.html', trends=trends)

@app.route('/edit_trend', methods=['GET', 'POST'])
def edit_trend():
    if request.method == 'POST':
        try:
            trend_id = request.form['trend_id']
            device_number = request.form['device_number']
            tags = request.form['tags']
            cycles = request.form['cycles']
            cycle_time = request.form['cycle_time']
            buffer_size = request.form['buffer_size']
            description = request.form['description']

            execute_query('''
                UPDATE Trends 
                SET device_number = ?, tags = ?, cycles = ?, cycle_time = ?, buffer_size = ?, description = ?
                WHERE id = ?''',
                (device_number, tags, cycles, cycle_time, buffer_size, description, trend_id))
            flash('Trend updated successfully!', 'success')
        except Exception as e:
            app.logger.error(f"Error occurred while updating the trend: {e}")
            flash('Error occurred while updating the trend!', 'error')
        return redirect(url_for('trend_control'))

    flash('Failed to edit; No POST!', 'fail')
    return redirect(url_for('trend_control'))

@app.route('/get_trend/<int:id>', methods=['GET'])
def get_trend(id):
    trend = execute_query('SELECT * FROM Trends WHERE id = ?', (id,), fetchone=True)

    if trend:
        trend_dict = dict(trend)
        return jsonify(trend=trend_dict)
    else:
        return jsonify({'message': 'Trend not found!'}), 404

@app.route('/delete_trend/<int:id>', methods=['POST'])
def delete_trend(id):
    try:
        execute_query('DELETE FROM Trends WHERE id = ?', (id,))
        flash('Trend deleted successfully!', 'success')
    except Exception as e:
        app.logger.error(f"Error occurred while deleting the trend: {e}")
        flash('Error occurred while deleting the trend!', 'error')
    return redirect(url_for('trend_control'))

if __name__ == '__main__':
    app.run(debug=True)
