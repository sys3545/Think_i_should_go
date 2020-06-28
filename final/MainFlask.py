#!/usr/bin/python
from py.WordBackEndProgram import WordProgram 
from py.WordBackEndProgram import ActTextFile 
from flask import Flask, render_template, redirect, url_for, request
import requests  #requests 와 request는 다르다!!!
from werkzeug.utils import secure_filename #download werkzeug
from bs4 import BeautifulSoup
import os


URL_list=[]
count=0
urlList=[]
timeList=[]
bowList=[]
app = Flask(__name__)
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/',methods=['GET','POST'])
def index(URL=None):
    global URL_list
    global count
    global urlList
    global timeList
    global bowList

    URL_list=[]
    count=0
    urlList=[]
    timeList=[]
    bowList=[]

    if count==0:
        WordProgram.downloadNLTK()
    elif count==2:
        os.system("""curl -X PUT localhost:9200/crawl_data/_settings -H 'Content-Type: application/json' -d'{ "index.mapping.total_fields.limit": 20000 } '""") 
    count+=1
    
    if request.method=='GET':
        return render_template('MainPage.html')

    else: #post
        if "URL" in request.form :
            url = request.form["URL"]
            urlObject = WordProgram(url)
            URL_list.append(urlObject)

            for l in URL_list:
                urlList.append(l.getURL())
                timeList.append(l.getTime())
                bowList.append(l.getBoWLength())

            return render_template('MainPage.html',URL_list = urlList, time_list=timeList,bowLength_list=bowList)    
        
        elif "FILE" in request.files:
            file = request.files["FILE"]
            if file and allowed_file(file.filename):
                filename = "./txtFolder/" + secure_filename(file.filename)
                program = ActTextFile(filename)
                URL_list += program.getList()

                for l in URL_list:
                    urlList.append(l.getURL())
                    timeList.append(l.getTime())
                    bowList.append(l.getBoWLength())
                return render_template('MainPage.html',URL_list = urlList, time_list=timeList,bowLength_list=bowList)    
                
        elif "similar" in request.form:
            number = request.form["similar"]
            return pop(number,1)

        elif "topWords" in request.form :
            number = request.form["topWords"]

            return pop(number,0)
        else:
            return render_template('MainPage.html')


@app.route('/developer',methods=['GET',"POST"])
def develope():
    return render_template('developer.html')

@app.route('/pop',methods=['GET'])
def pop(count,status):   
    url= URL_list[int(count)].getURL()
    sim = WordProgram.getAllData(url,status)
    return render_template('pop.html',sim=sim,url=url)
    

if __name__ == "__main__":
    app.run(debug = True)
    


#flask pip 필요????

# elastic on => Elastic/elasticsearch-7.7.1/bin/elasticsearch -d
# elasticsearch 프로그램이 깔려있는 환경에서 진행될 예정.
