import mysql.connector
import json

class ReadOnlyMySQL:
    def __init__(self, host, user, password, database):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }

    def get_schema(self):
        conn = mysql.connector.connect(**self.config)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        schema = {}
        for table in tables:
            cursor.execute(f"DESCRIBE {table}")
            schema[table] = [
                {"column": row[0], "type": row[1]}
                for row in cursor.fetchall()
            ]
        conn.close()
        return json.dumps(schema, indent=2)

    def run_query(self, query: str):
        clean_query = query.strip()
        if not clean_query.upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed!")
        conn = mysql.connector.connect(**self.config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(clean_query)
        results = cursor.fetchall()
        conn.close()
        return results
