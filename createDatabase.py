import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Create the Systems table with a subnet field
    c.execute('''CREATE TABLE IF NOT EXISTS Systems (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_number TEXT NOT NULL,
                    description TEXT,
                    plc_ip TEXT NOT NULL,
                    subnet TEXT  -- Added subnet field
                )''')

    # Create the Tags table
    c.execute('''CREATE TABLE IF NOT EXISTS Tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_set_name TEXT NOT NULL,
                    tags TEXT NOT NULL
                )''')

    conn.commit()
    conn.close()

init_db()
