import sqlite3
import pandas as pd
import re
import os

from werkzeug.utils import secure_filename
from flask import Flask, jsonify,request, make_response, redirect, url_for, flash, render_template
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
from io import StringIO
from pathlib import Path

app = Flask(__name__)

# mengetahui path directory untuk penyimpanan file
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join('staticFiles', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# print("APP_ROOT", APP_ROOT)
# print("UPLOAD_FOLDER", UPLOAD_FOLDER)


class CustomFlaskAppWithEncoder(Flask):
    json_provider_class = LazyJSONEncoder

app = CustomFlaskAppWithEncoder(__name__)



swagger_template = dict(
    info = {
        'title': LazyString(lambda: "Muhammad Bayu Oktodwilavito Gold Chalange"),
        'version': LazyString(lambda: "1.0.0"),
        'description': LazyString(lambda: "Dokumentasi API data Processing dan Modeling Gold Chalange"),
    },
    host = LazyString(lambda: request.host)
)


swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "docs",
            "route": "/docs.json",
        }
    ],
    "static_url_path": "/flasgger_static",
    #"static_folder": "static", #must be set by user
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,config = swagger_config)

@app.route('/', methods=['GET'])
def hello_world():
    json_response = {
        'status_code': 200,
        'description': "BINAR ACADEMY GOLD CHALANGE",
        'description1': "SILAHKAN TAMBAHKAN /docs untuk masuk ke UI SWEGGER",
        'data': "MUHAMMAD BAYU OKTODWILAVITO - DATA SCIENCE - WAVE 21",
    }

    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():

    # Lakukan cleansing pada teks
    text = request.form.get("text")   
    text_clean = str(text).lower()
    text_clean1 = re.sub(r"((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))|([^a-zA-Z0-9])|(rt)|(user)"," ", text_clean)  
    # print(text_clean1)

    # Lakukan add ke database
    conn = sqlite3.connect('gold_chalange.db')
    print("open database successfully")

    conn.execute("INSERT INTO users (Text, clean_text) VALUES (?, ?)", (text, text_clean1))
    print("add database successfully")
    

    conn.commit()
    print("Records created successfully")
    conn.close()
    print(text_clean1)

    json_response = {
        'status_code': 200,
        'description' : "text yang sudah di proses",
        'data': text_clean1
    }

    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/File_processing.yml", methods=['POST'])
@app.route('/file-processing', methods=['POST'])

def upload_file():
    #memulai proses upload file, save and read file 
    if 'upload_file' not in request.files:
        return redirect(request.url)
    
    file = request.files['upload_file']

    if file.filename == '':
        return redirect(request.url)

    csv_filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, csv_filename))
    path = os.path.join(UPLOAD_FOLDER)
    print("data_film", csv_filename)


    file_path = Path(path) / csv_filename
    try:
        read = file_path.read_text(encoding='ANSI')


        # Pandas prosess
        df = pd.read_csv(StringIO(read), header=None)
        # print("df", df)
        
        # mengakses dari kolom pertama dan mengambil 10 baris pertama 
        read_csv = df[0].head(5)
        print("read_csv", read_csv)


        # Lakukan cleansing pada teks
        cleaned_text = []
        for text in read_csv:
            cleaned_text.append(re.sub(r"((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))|([^a-zA-Z0-9])"," ", text).upper())
        print("text_clean", cleaned_text)




        

        json_response = {
            'status_code': 200,
            'description': "Teks yang sudah diproses",
            'data': cleaned_text,
        }


        conn = sqlite3.connect('gold_chalange.db')
        print("open database successfully")
        for original_text, clean_text in zip(read_csv, cleaned_text):
            conn.execute("INSERT INTO users (Text, clean_text) VALUES (?, ?)", (original_text, clean_text))
        print("Data berhasil disimpan ke dalam tabel")
        conn.commit()
        conn.close()



        # conn.execute("INSERT INTO users(Text, clean_text) VALUES (?, ?)",(str(read_csv), str(cleaned_text)))
        # print("add database successfully")
        # conn.commit()
        # conn.close()

    except Exception as read:

        response_data = jsonify(json_response)
        return response_data
    return cleaned_text    


if __name__ == '__main__':
    app.run(debug=True)