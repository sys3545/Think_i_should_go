#!/usr/bin/python
from py.WordBackEndProgram import WordProgram
from flask import Flask, render_template
from flask import url_for, request

import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('MainPage.html')

if __name__ == "__main__":
    app.run(debug = True)

# wp = WordProgram(URL) 
# time.sleep(3)
# # print(wp.URL, wp.getTime, wp.getBoWLength)
# #top10 words는 tuple들을 감싸는 list 반환, cosine은 tuple 하나 반환, 데이터 넣는데 조금의 시간이 걸린다.
# print(wp.getAllData(URL,1))  #0 == tf-idf, 1 == cosine-similarity 
#flask pip 필요????


# elastic on => Elastic/elasticsearch-7.7.1/bin/elasticsearch -d