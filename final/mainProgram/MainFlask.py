#!/usr/bin/python
from WordBackEndProgram import WordProgram

import time


# URL = "https://cassandra.apache.org/" #URL 변수를 홈페이지에서 받아와여함.
# URL = "https://allura.apache.org/"
# URL = "https://airavata.apache.org/"
URL = "https://bloodhound.apache.org/"
# URL = "https://groovy.apache.org/"
# URL = "http://impala.apache.org/"
# URL = "http://santuario.apache.org/"
# URL = "http://climate.apache.org/"
# URL = "https://lucene.apache.org/"
# URL = "http://streams.apache.org/"
# URL = "http://incubator.apache.org/"
# URL = "http://thrift.apache.org/"
# URL = "http://poi.apache.org/"

wp = WordProgram(URL) 
time.sleep(3)
# print(wp.URL, wp.getTime, wp.getBoWLength)
#top10 words는 tuple들을 감싸는 list 반환, cosine은 tuple 하나 반환, 데이터 넣는데 조금의 시간이 걸린다.
print(wp.getAllData(URL,1))  #0 == tf-idf, 1 == cosine-similarity 



# elastic on => Elastic/elasticsearch-7.7.1/bin/elasticsearch -d