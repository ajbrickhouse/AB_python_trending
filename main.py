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

# Route to manage systems
@app.route('/manage_systems', methods=['GET', 'POST'])
def manage_systems():
    conn = get_db_connection()

    if request.method == 'POST':
        system_id = request.form.get('system_id')
        device_number = request.form['device_number']
        description = request.form['description']
        plc_ip = request.form['plc_ip']
        subnet = request.form['subnet']

        if system_id:  # If system_id exists, it's an edit operation
            conn.execute('UPDATE Systems SET device_number = ?, description = ?, plc_ip = ?, subnet = ? WHERE id = ?',
                         (device_number, description, plc_ip, subnet, system_id))
            flash('System updated successfully!', 'success')
        else:  # Otherwise, it's an add operation
            conn.execute('INSERT INTO Systems (device_number, description, plc_ip, subnet) VALUES (?, ?, ?, ?)',
                         (device_number, description, plc_ip, subnet))
            flash('System added successfully!', 'success')

        conn.commit()
        return redirect(url_for('manage_systems'))

    systems = conn.execute('SELECT * FROM Systems').fetchall()
    conn.close()
    return render_template('manage_systems.html', systems=systems)

@app.route('/edit_system/<int:id>', methods=['GET', 'POST'])
def edit_system(id):
    conn = get_db_connection()
    system = conn.execute('SELECT * FROM Systems WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        device_number = request.form['device_number']
        description = request.form['description']
        plc_ip = request.form['plc_ip']
        subnet = request.form['subnet']

        conn.execute('UPDATE Systems SET device_number = ?, description = ?, plc_ip = ?, subnet = ? WHERE id = ?',
                    (device_number, description, plc_ip, subnet, id))
        conn.commit()
        conn.close()
        flash('System updated successfully!', 'success')
        return redirect(url_for('manage_systems'))

    conn.close()
    return render_template('edit_system.html', system=system)

@app.route('/delete_system/<int:id>', methods=['POST'])
def delete_system(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Systems WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('System deleted successfully!', 'success')
    return redirect(url_for('manage_systems'))

# Route to manage tag sets
@app.route('/manage_tags', methods=['GET', 'POST'])
def manage_tags():
    conn = get_db_connection()

    if request.method == 'POST':
        tag_set_id = request.form.get('tag_set_id')
        tag_set_name = request.form['tag_set_name']
        tags = request.form['tags']

        if tag_set_id:  # If tag_set_id exists, it's an edit operation
            conn.execute('UPDATE Tags SET tag_set_name = ?, tags = ? WHERE id = ?',
                         (tag_set_name, tags, tag_set_id))
            flash('Tag set updated successfully!', 'success')
        else:  # Otherwise, it's an add operation
            conn.execute('INSERT INTO Tags (tag_set_name, tags) VALUES (?, ?)',
                         (tag_set_name, tags))
            flash('Tag set added successfully!', 'success')

        conn.commit()
        return redirect(url_for('manage_tags'))

    tag_sets = conn.execute('SELECT * FROM Tags').fetchall()
    conn.close()
    return render_template('manage_tags.html', tag_sets=tag_sets)

@app.route('/edit_tag_set/<int:id>', methods=['GET', 'POST'])
def edit_tag_set(id):
    conn = get_db_connection()
    tag_set = conn.execute('SELECT * FROM Tags WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        tag_set_name = request.form['tag_set_name']
        tags = request.form['tags']

        conn.execute('UPDATE Tags SET tag_set_name = ?, tags = ? WHERE id = ?',
                     (tag_set_name, tags, id))
        conn.commit()
        conn.close()
        flash('Tag set updated successfully!', 'success')
        return redirect(url_for('manage_tags'))

    conn.close()
    return render_template('edit_tag_set.html', tag_set=tag_set)

@app.route('/delete_tag_set/<int:id>', methods=['POST'])
def delete_tag_set(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Tags WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Tag set deleted successfully!', 'success')
    return redirect(url_for('manage_tags'))

@app.route('/trend_control', methods=['GET', 'POST'])
def trend_control():
    conn = get_db_connection()
    systems = conn.execute('SELECT * FROM Systems').fetchall()
    tag_sets = conn.execute('SELECT * FROM Tags').fetchall()
    trends = conn.execute('SELECT * FROM Trends').fetchall()
    
    try:
        if request.method == 'POST':
            system_id = request.form['system_id']
            tag_set_id = request.form['tag_set_id']
            description = request.form['description']
            cycles = request.form['cycles']
            cycle_time = request.form['cycle_time']
            buffer_size = request.form['buffer_size']

            # Fetch system and tag details for the trend
            system_data = conn.execute('SELECT device_number, plc_ip, subnet FROM Systems WHERE id = ?', (system_id,)).fetchone()
            tag_set = conn.execute('SELECT tags FROM Tags WHERE id = ?', (tag_set_id,)).fetchone()[0]

            conn.execute('''
                INSERT INTO Trends (device_number, plc_ip, subnet, tags, description, cycles, cycle_time, buffer_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (system_data['device_number'], system_data['plc_ip'], system_data['subnet'], tag_set, description, cycles, cycle_time, buffer_size))
            flash('Trend added successfully!', 'success')

            conn.commit()
            return redirect(url_for('trend_control'))
    except Exception as e:
        app.logger.error(f"Error occurred while saving the trend: {e}")
        flash('Error occurred while saving the trend!', 'error')
    finally:
        conn.close()

    return render_template('trend_control.html', systems=systems, tag_sets=tag_sets, trends=trends)

@app.route('/test_json')
def test_json():
    return jsonify({"message": "Hello, World!"})

@app.route('/edit_trend', methods=['GET', 'POST'])
def edit_trend():
    conn = get_db_connection()
    
    if request.method == 'POST':
        try:
            trend_id = request.form['trend_id']
            device_number = request.form['device_number']
            tags = request.form['tags']
            cycles = request.form['cycles']
            cycle_time = request.form['cycle_time']
            buffer_size = request.form['buffer_size']
            description = request.form['description']

            conn.execute('''
                UPDATE Trends 
                SET device_number = ?, tags = ?, cycles = ?, cycle_time = ?, buffer_size = ?, description = ?
                WHERE id = ?''',
                (device_number, tags, cycles, cycle_time, buffer_size, description, trend_id))
            conn.commit()
            flash('Trend updated successfully!', 'success')
        except Exception as e:
            app.logger.error(f"Error occurred while updating the trend: {e}")
            flash('Error occurred while updating the trend!', 'error')
        finally:
            conn.close()
        return redirect(url_for('trend_control'))

    conn.close()
    flash('Failed to edit; No POST!', 'fail')
    return redirect(url_for('trend_control'))

@app.route('/get_trend/<int:id>', methods=['GET'])
def get_trend(id):
    conn = get_db_connection()
    trend = conn.execute('SELECT * FROM Trends WHERE id = ?', (id,)).fetchone()
    conn.close()

    if trend:
        trend_dict = dict(trend)
        return jsonify(trend=trend_dict)
    else:
        return jsonify({'message': 'Trend not found!'}), 404

@app.route('/delete_trend/<int:id>', methods=['POST'])
def delete_trend(id):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM Trends WHERE id = ?', (id,))
        conn.commit()
        flash('Trend deleted successfully!', 'success')
    except Exception as e:
        app.logger.error(f"Error occurred while deleting the trend: {e}")
        flash('Error occurred while deleting the trend!', 'error')
    finally:
        conn.close()
    return redirect(url_for('trend_control'))

if __name__ == '__main__':
    app.run(debug=True)
