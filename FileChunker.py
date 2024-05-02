import os
from itertools import chain
import array
from db import DB
import time


class Chunker:
    def __init__(self, chunk_size=1024):
        self.chunk_size = chunk_size
        self.db = DB()

    def chunk_file(self, file_data, file_fullname, user_id):
        file_name = os.path.basename(file_fullname).split(".")[0]
        file_type = os.path.basename(file_fullname).split(".")[1]

        chunks = [file_data[i:i + self.chunk_size] for i in range(0, len(file_data), self.chunk_size)]  

        file_id = self.db.upload_file(f"{file_name}.{file_type}", len(file_data), user_id)
        time.sleep(0.5)
        self.db.upload_chunks(chunks, file_id)

    
    def rechunk_file(self, file_id):
        chunks = self.db.get_chunks(file_id)
        file_name = self.db.get_file_name(file_id)
        combined_chunks = chunks[0][1]
        
        try:
            print(len(chunks))
            for i in range(1, len(chunks)):
                combined_chunks += chunks[i][1]
                print(chunks[i][0])
        except Exception as e:
            print(f"Error during chunk concatenation: {e}")

        return [combined_chunks, file_name]