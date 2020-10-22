from flask import Flask, render_template, render_template, request, jsonify, redirect, url_for
 
from flask import flash
import tensorflow as tf
import numpy as np
import re
import os
import base64
import uuid

from flask import send_from_directory
from werkzeug.utils import secure_filename

from PSGAN import demo
import pandas as pd


# print('Start')
# # demo.main("PSGAN/assets/images/non-makeup/xfsy_0478.png", "PSGAN/assets/images/makeup/Global_The_Vintage_Vamp_Jessi_Global_Model.jpeg") 
# demo.main("static/makeup/2.jpeg", "static/non-makeup/e7e0bd7ca6e93c5d61e0acd9846b5c1d.jpg") 
# print('Finish')
UPLOAD_FOLDER = 'static/non-makeup/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'} 
look_name = ["THE SUPER MODEL", "THE UPTOWN GIRL", "THE GOLDEN GODDESS", "THE SOPHISTICATE", "THE BOMBSHELL", "THE BELLA SOFIA", "THE VINTAGE VAMP", "THE QUEEN OF GLOW", "THE REBEL", "THE ROCK CHICK"]
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

item_data = pd.read_csv("static/products/products.csv", encoding= 'unicode_escape')
# @app.route('/')
# def index():
#     return render_template('home_page.html') 
# model = tf.keras.models.load_model("models/G.pth")

def parse_image(imgData):
    img_str = re.search(b"base64,(.*)", imgData).group(1)
    img_decode = base64.decodebytes(img_str)
    filename = "{}.jpg".format(uuid.uuid4().hex)
    with open('uploads/makeup/'+filename, "wb") as f:
        f.write(img_decode)
    return img_decode
 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route('/', methods=['GET'])
# def index():
#     return redirect(url_for('home', filename='load'))

@app.route('/', methods=['GET', 'POST'])
def index(filename=None):
    if request.method == 'POST':
        # check if the post request has the file part2
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('makeup_look.html', source_file = filename, look_name=look_name)
    return render_template('home_page.html') 

@app.route('/transfer/<filename>/<look>')
def transfer(filename,look):
    source_path = os.path.join('static/non-makeup', filename)
    print(source_path)
    look_path = os.path.join('static/makeup', str(look)+'.jpeg')
    print(look_path)
    filename = demo.main(source_path, look_path) 
    print(filename)
    item_name = look_name[int(look)-1]
    print(item_name)
    item_list = item_data[item_data['LOOK'] == item_name] 
    print(item_list) 
 
    item_list.reset_index(inplace=True)
    return render_template('style_transfer.html', filename = filename, look=str(look)+'.jpeg', item_list=item_list, source_path=source_path) 
    # return send_from_directory(app.config['UPLOAD_FOLDER'],
    #                            filename)

# from werkzeug.middleware.shared_data import SharedDataMiddleware
# app.add_url_rule('/uploads/<filename>', 'uploaded_file',
#                  build_only=True)
# app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
#     '/uploads':  app.config['UPLOAD_FOLDER']
# })

 
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)