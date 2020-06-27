#!/usr/bin/python
from py.WordBackEndProgram import WordProgram 
from py.WordBackEndProgram import ActTextFile 
from flask import Flask, render_template, redirect, url_for, request
import requests  #requests 와 request는 다르다!!!
from werkzeug.utils import secure_filename #download werkzeug

import sys



app = Flask(__name__)
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/',methods=['GET','POST'])
def index(URL=None):
    URL_list=[]
    WordProgram.downloadNLTK()
    if request.method=='GET':
        return render_template('MainPage.html')

    else: #post
        if "URL" in request.form :
            url = request.form["URL"]
            urlObject = WordProgram(url)
            URL_list.append(urlObject)

            time=urlObject.getTime()
            bowLength = urlObject.getBoWLength()

            return render_template('MainPage.html',URL = url,time=time,bowLength=bowLength)
        elif "FILE" in request.files:
            file = request.files["FILE"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                program = ActTextFile(filename)
                URL_list += program.getList()
                # print(URL_list[0].getURL)
                # url = URL_list[0].getURL
                
                # URL =URL_list[0].getAllData(url,0)
                return render_template('MainPage.html',URL = URL_list[0].getURL(), time=URL_list[0].getTime(),bowLength=URL_list[0].getBoWLength())
                
        else:
            return render_template('MainPage.html')

    
if __name__ == "__main__":
    app.run(debug = True)


#flask pip 필요????

# elastic on => Elastic/elasticsearch-7.7.1/bin/elasticsearch -d
# elasticsearch 프로그램이 깔려있는 환경에서 진행될 예정.
