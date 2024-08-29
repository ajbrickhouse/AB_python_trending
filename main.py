from flask import Flask, render_template, request, redirect, url_for, flash
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
            flash('System updated successfully!')
        else:  # Otherwise, it's an add operation
            conn.execute('INSERT INTO Systems (device_number, description, plc_ip, subnet) VALUES (?, ?, ?, ?)',
                         (device_number, description, plc_ip, subnet))
            flash('System added successfully!')

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
        flash('System updated successfully!')
        return redirect(url_for('manage_systems'))

    conn.close()
    return render_template('edit_system.html', system=system)

@app.route('/delete_system/<int:id>', methods=['POST'])
def delete_system(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Systems WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('System deleted successfully!')
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
            flash('Tag set updated successfully!')
        else:  # Otherwise, it's an add operation
            conn.execute('INSERT INTO Tags (tag_set_name, tags) VALUES (?, ?)',
                         (tag_set_name, tags))
            flash('Tag set added successfully!')

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
        flash('Tag set updated successfully!')
        return redirect(url_for('manage_tags'))

    conn.close()
    return render_template('edit_tag_set.html', tag_set=tag_set)

@app.route('/delete_tag_set/<int:id>', methods=['POST'])
def delete_tag_set(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Tags WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Tag set deleted successfully!')
    return redirect(url_for('manage_tags'))

# Route for trend control (showing dropdowns for system and tag set selection)
@app.route('/trend_control', methods=['GET', 'POST'])
def trend_control():
    conn = get_db_connection()
    systems = conn.execute('SELECT * FROM Systems').fetchall()
    tag_sets = conn.execute('SELECT * FROM Tags').fetchall()

    try:
        if request.method == 'POST':
            trend_id = request.form.get('trend_id')
            system_id = request.form['system_id']
            tag_set_id = request.form['tag_set_id']
            description = request.form['description']
            cycles = request.form['cycles']
            cycle_time = request.form['cycle_time']
            buffer_size = request.form['buffer_size']

            # Fetch system and tag details for the trend
            system_device_number = conn.execute('SELECT device_number FROM Systems WHERE id = ?', (system_id,)).fetchone()[0]
            system_ip = conn.execute('SELECT plc_ip FROM Systems WHERE id = ?', (system_id,)).fetchone()[0]
            system_subnet = conn.execute('SELECT subnet FROM Systems WHERE id = ?', (system_id,)).fetchone()[0]
            tag_set = conn.execute('SELECT tags FROM Tags WHERE id = ?', (tag_set_id,)).fetchone()[0]

            if trend_id:  # If trend_id exists, it's an edit operation
                conn.execute('''
                    UPDATE Trends SET device_number = ?, plc_ip = ?, subnet = ?, tags = ?, description = ?, cycles = ?, cycle_time = ?, buffer_size = ?
                    WHERE id = ?''',
                            (system_device_number, system_ip, system_subnet, tag_set, description, cycles, cycle_time, buffer_size, trend_id))
                flash('Trend updated successfully!')
            else:  # Otherwise, it's an add operation
                conn.execute('''
                    INSERT INTO Trends (device_number, plc_ip, subnet, tags, description, cycles, cycle_time, buffer_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                            (system_device_number, system_ip, system_subnet, tag_set, description, cycles, cycle_time, buffer_size))
                flash('Trend added successfully!')

            conn.commit()
            return redirect(url_for('trend_control'))
    except Exception as e:
        print(e)
        flash('Error occurred while saving the trend!')

    trends = conn.execute('''SELECT * FROM Trends''').fetchall()

    conn.close()
    return render_template('trend_control.html', systems=systems, tag_sets=tag_sets, trends=trends)

@app.route('/edit_trend/<int:id>', methods=['GET', 'POST'])
def edit_trend(id):
    conn = get_db_connection()
    trend = conn.execute('SELECT * FROM Trends WHERE id = ?', (id,)).fetchone()
    systems = conn.execute('SELECT * FROM Systems').fetchall()
    tag_sets = conn.execute('SELECT * FROM Tags').fetchall()

    if request.method == 'POST':
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
            (device_number, tags, cycles, cycle_time, buffer_size, description, id))
        conn.commit()
        conn.close()
        flash('Trend updated successfully!')
        return redirect(url_for('trend_control'))

    trends = conn.execute('SELECT * FROM Trends').fetchall()
    conn.close()
    return render_template('edit_trend.html', trend=trend, systems=systems, tag_sets=tag_sets, trends=trends)

@app.route('/delete_trend/<int:id>', methods=['POST'])
def delete_trend(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Trends WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Trend deleted successfully!')
    return redirect(url_for('trend_control'))

if __name__ == '__main__':
    app.run(debug=True)
