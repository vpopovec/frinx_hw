import psycopg2
from psycopg2 import sql
from psycopg2.errors import DuplicateDatabase


def get_conn(user, initial_db_name):
    conn = psycopg2.connect(f"dbname={initial_db_name} user={user}")
    conn.autocommit = True
    cur = conn.cursor()

    # Create a database
    db_name = 'vpopovec_homework'
    try:
        cur.execute(sql.SQL('CREATE DATABASE {};').format(sql.Identifier(db_name)))
    except DuplicateDatabase:
        print(f"Database {db_name} already set up")

    conn = psycopg2.connect(f"dbname={db_name} user={user}")
    conn.autocommit = True
    return conn


def create_table(cur):
    db_model = {
        "id": "SERIAL PRIMARY KEY",
        "connection": "INTEGER",
        "name": "VARCHAR(255) NOT NULL",
        "description": "VARCHAR(255)",
        "config": "JSON",
        "type": "VARCHAR(50)",
        "infra_type": "VARCHAR(50)",
        "port_channel_id": "INTEGER",
        "max_frame_size": "INTEGER"
    }
    # query = sql.SQL("CREATE TABLE interfaces (" + ', '.join(['{}' for i in range(len(db_model))]) + ");").format(
    #     *[sql.Identifier(f"{k} {v}") for k, v in db_model.items()])

    cur.execute("DROP TABLE IF EXISTS interfaces")
    " This query could be improved to prevent SQL injection attacks... "
    query = f"CREATE TABLE interfaces (" + ", ".join([f"{k} {v}" for k, v in db_model.items()]) + ");"
    cur.execute(query)
