import hashlib
import psycopg2
from psycopg2 import Error

#TODO create config file to fetch data for connection from it?
BUF_SIZE = 65536   # 64KB buffer to read images showed better results than 128 or 256
TABLE_NAME = 'imhashes'


def get_image_hash(imagename:str)-> str:
    sha1 = hashlib.sha1()

    with open(imagename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()

def search_for_duplicate(image_hash:str, cursor)-> int:
# CREATE TABLE imhashes (id SERIAL PRIMARY KEY , hash VARCHAR(40) UNIQUE NOT NULL); - table structure 
    try:
        cursor.execute(f"SELECT * FROM {TABLE_NAME} where hash like '{image_hash}';")
        record = cursor.fetchone()

        if record:  # Image hash in database means this image was already posted
            return None
        else:  # No image found - post it and add it's hash to the database
            print("No image found")
            cursor.execute(f"INSERT INTO {TABLE_NAME} (hash) VALUES ('{image_hash}');")
            return 1 

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)