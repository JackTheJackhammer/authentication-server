import psycopg2

# DEBUG MODE! CHANGE ME TO THE HOST WHEN IN PROD


def createConnection():
    conn = psycopg2.connect(
        database="auth-hp-datavault",
        host="dev_auth_db",
        user="postgres",
        password="admin123",
        port="5432",
    )
    return conn


# make me co-current!
def queryDatabase(query: str, params=None):
    conn = createConnection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        closeConnection(conn)
        return results
    except Exception as e:
        closeConnection(conn)
        print(f"Error executing query: {e}")
        return None


def modifyDatabase(query: str, params=None):
    conn = createConnection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        closeConnection(conn)
        return True
    except Exception as e:
        closeConnection(conn)
        print(f"Error modifying database: {e}")
        return False


def closeConnection(conn: psycopg2.extensions.connection):
    try:
        if conn:
            conn.close()
            # print("Connection closed successfully.")
    except Exception as e:
        print(f"Error closing the connection: {e}")


def restartConnection(conn: psycopg2.extensions.connection):
    try:
        closeConnection(conn)
        return createConnection()
    except Exception as e:
        print(f"Error restarting the connection: {e}")
        return None
