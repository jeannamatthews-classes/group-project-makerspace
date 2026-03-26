import psycopg2

def log_event(event): #takes an instance of access_events class as argument
    #initialize variables
    conn = None
    cur = None

    #try to connect to the database with correct info
    try:
        conn = psycopg2.connect(
            host = 'localhost',
            dbname = 'postgres',
            user = 'postgres',
            password = 'makerspace26',
            port = '5432'
        )

        cur = conn.cursor()

        insert_script = 'INSERT INTO access_events (id, student_id, timestamp, decision, reason, device_id, export_status) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        insert_value = (0, event.student_id, event.timestamp, event.decision, event.reason, event.devic_id, event.export_status)
        cur.execute(insert_script, insert_value)

        conn.commit()

    #if it cannot connect
    except Exception as error:
        print("Could not connect to database.")

    #always close connections afterward
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

