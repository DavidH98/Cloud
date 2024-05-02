import mariadb
import sys

class DB:
    def __init__(self):
        try:
            self.conn = mariadb.connect(
                user="root",
                password="",
                host="localhost",
                port=3306,
                database="cloud"
            )
            self.cur = self.conn.cursor()
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

    def is_table_empty(self, table_name):
        self.cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = self.cur.fetchone()[0]

        if count == 0:
            return True
        else: 
            return False

    def get_last_id(self, table_name, data): # To set the user_id
        if(not self.is_table_empty(table_name)):
            self.cur.execute(f"SELECT * FROM {table_name} ORDER BY {data} DESC LIMIT 1;")
            last_id = self.cur.fetchone()[0]
            return last_id
        else:
            return 1

    def upload_file(self, file_name, file_size, user_id):
        try:
            file_id = 0
            try:
                file_id = self.get_last_id("files", "file_id")+1
            except Exception as e:
                file_id = 1
            self.cur.execute(
                "INSERT INTO files (file_id, user_id, file_name, file_size) VALUES (?, ?, ?, ?)",
                (file_id, user_id, file_name, file_size)
            )
        except Exception as e:
            print(f"Error upload file: {e}")
        finally:
            self.conn.commit()
            return file_id

    def upload_chunks(self, chunks, file_id):
        try:
            for chunk_num, chunk_data in enumerate(chunks, start=1):
                chunk_size = len(chunk_data)
                self.cur.execute(
                    "INSERT INTO chunks (chunk_id, file_id, chunk_size, chunk_data) VALUES (?, ?, ?, ?)",
                    (chunk_num, file_id, chunk_size, chunk_data)
                )
        except Exception as e:
            print(f"Error upload chunks: {e}")
        finally:
            self.conn.commit()

    def get_chunks(self, file_id):
        try:
            self.cur.execute("SELECT chunk_id, chunk_data FROM chunks WHERE file_id = %s", (file_id,))
            chunks = self.cur.fetchall() #[(num, data), (num, data)]
            return chunks
        except Exception as e:
            print(f"Error get chunks: {e}")

    def get_file_name(self, file_id):
        try:
            self.cur.execute("SELECT file_name FROM files WHERE file_id = %s", (file_id,))
            file_name = self.cur.fetchone()[0]
            return file_name
        except Exception as e:
            print(f"Error file name: {e}")

    def add_new_user(self, email, username, pass_hash):
        try:
        
            user_id = (self.get_last_id("users", "id"))+1
            self.cur.execute(
                "INSERT INTO users (id, username, email, password_hash) VALUES (?, ?, ?, ?)",
                (user_id, username, email, pass_hash)
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error adding user: {e}")

    def has_file(self, file_id, user_id):
        try:
            self.cur.execute("SELECT * FROM files WHERE file_id = %s AND user_id= %s", (file_id, user_id, ))
            is_file = self.cur.fetchone()
            self.conn.commit()
            return is_file
        except Exception as e:
            print(f"Error checking file: {e}")

    def delete_file(self, file_id):
        try:
            delete_query = "DELETE FROM chunks WHERE file_id = %s"
            self.cur.execute(delete_query, (file_id,))
            delete_query = "DELETE FROM files WHERE file_id = %s"
            self.cur.execute(delete_query, (file_id,))
            self.conn.commit()
        except Exception as e:
            print(f"Error deleting file: {e}")

    def is_user_in_db(self, email):
        query = "SELECT * FROM users WHERE email = %s"
        self.cur.execute(query, (email,))
        result = self.cur.fetchone()

        return bool(result)

    def get_user_pass_hash(self, email):
        query = "SELECT password_hash FROM users WHERE email = %s"
        self.cur.execute(query, (email,))
        result = self.cur.fetchone()[0]

        return result

    def get_username_by_email(self, email):
        query = "SELECT username FROM users WHERE email = %s"
        self.cur.execute(query, (email,))
        result = self.cur.fetchone()[0]

        return result
    
    def get_id_by_email(self, email):
        query = "SELECT id FROM users WHERE email = %s"
        self.cur.execute(query, (email,))
        result = self.cur.fetchone()[0]
        return result
    
    def get_files_by_user_id(self, user_id):
        query = "SELECT file_name, file_size, upload_date, file_id FROM files WHERE user_id = %d"
        self.cur.execute(query, (user_id,))
        results = self.cur.fetchall()
        self.conn.commit()
        return results

    def __del__(self):
        # Close the database connection when the object is deleted
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cur.close()
            self.conn.close()
            print("Database connection closed.")