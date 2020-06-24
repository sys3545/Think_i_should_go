import requests, re, json, nltk, ssl, time, os
from bs4 import BeautifulSoup
from nltk.corpus import stopwords 
from elasticsearch import Elasticsearch 
from elasticsearch import helpers 
from math import log # IDF 계산을 위해
from numpy import dot
from numpy.linalg import norm
import numpy as np
#need pip elasticsearch, numpy, nltk, bs4, requests, ssl

#변수 = class() 를 통해서 생성. 
#exp = WordProgram()
class WordProgram:

    word_bag={}
    index_name = "crawl_data"        
    docType="bow_data"
    number=0

    es_host="127.0.0.1" #elasticsearch 연결.
    es_port="9200"
    es = Elasticsearch([{"host":es_host,"port":es_port}],timeout=30)

    def __init__(self,URL):
        self.URL = URL
        word_bag = self.word_bag
        self.number +=1
        
        try: #ssl 관련 오류 해결
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        nltk.download('stopwords')
        nltk.download('punkt')

        req = requests.get(URL) #----crawling 시작-----
        start_time= time.time()
        html = req.text
        soup= BeautifulSoup(html,"html.parser")

        tags = soup.select('p')
        sentence_list=[t.get_text() for t in tags]
        swlist = []

        for sw in stopwords.words("english"):
            swlist.append(sw) #stop words list

        for s in sentence_list:  #정제 작업 + BOW 생성 + running time 생성
            word_list = re.findall("[A-Za-z']+",s.strip())
            for w in word_list:
                if w not in swlist: #단어가 stopword 인 경우
                    if w in word_bag.keys():
                        word_bag[w] += 1
                    elif w not in word_bag.keys():
                        word_bag[w] =1

        self.word_config_time="{:.3f}".format(time.time() - start_time) #get time
        
        #저장 데이터 형식 지정.

        self.insertData(self.es,self.index_name,self.docType,URL)

    def getBoWLength(self):
        return len(self.word_bag)

    def getTime(self):
        return self.word_config_time
    
    def insertData(self,es,index_name,docType,URL):
        word_bag=self.word_bag
        if not es.indices.exists(index=index_name): 
            es.indices.create(index=index_name)
        doc={
            "BOW_time":self.word_config_time
        }
        for word in word_bag:
            doc[word]=word_bag[word]
        es.index(index=index_name, doc_type =docType, id=URL,body=doc) #id에는 고유 URL을 넣음. index는 하나의 type
        # es.update(index=index_name,doc_type=docType, id =URL,body=doc)

    # def deleteData():
    
    def getAllData(self,URL,status):
        es=self.es
        index_name = self.index_name

        res = es.search(index=index_name, body={'from':0,'size':10000,'query':{'match_all':{}}})
        URL_BOW_list=[]
        for r in res['hits']['hits']:
            temp_dict={}
            # print('URL:',r['_id'],'\ncount: ')
            for rs in r['_source']:
                # print(rs,r['_source'][rs])
                if rs=="BOW_time": continue
                temp_dict[rs] = r['_source'][rs]
            URL_BOW_list.append({"URL":r['_id'],"BOW":temp_dict})

        if status==0: #top10 word button clicked
            topWords=self.makeTopWords(es,URL_BOW_list,URL)  
            return topWords
        else:
            similarWebPage=self.findSimilarSite(es,URL_BOW_list,URL)
            return similarWebPage

    def makeTopWords(self,es,URL_BOW_list,URL):
        vocab=list(set(word for BOW_list in URL_BOW_list for word in BOW_list["BOW"]))
        docs={}
        for BOW_list in URL_BOW_list:
            temp_dict={}
            for v in vocab:
                if v in BOW_list["BOW"].keys():
                    temp_dict[v] = BOW_list["BOW"][v]
                else:
                    temp_dict[v]=0
            docs[BOW_list["URL"]] =temp_dict.copy() #docs key = URL, vla = tf dict
        
        idf={}
        for i in range(len(vocab)):
            df=0
            t = vocab[i]
            for BOW_list in URL_BOW_list:
                if t in BOW_list["BOW"].keys(): #df = 각 단어가 등장하는 문서 수
                    df += 1
            idf[t]=log(len(docs)/(df+1))
            # print(t,df,idf[t])
            
        for doc in docs:
            for i in idf:
                if i in docs[doc].keys():
                    docs[doc][i] = float(docs[doc][i])*idf[i]
        # print(docs)
        #현재 URL 기준 정렬 후 top10 단어 추출
        docs_res = sorted(docs[URL].items(), key=(lambda x:x[1]),reverse=True)
        top10Words=[] ; count=0
        for doc in docs_res: 
            if count == 10: break
            top10Words.append(doc)
            count+=1
        # print(top10Words)
        return top10Words
    
    def cos_sim(self,A, B):
        return dot(A, B)/(norm(A)*norm(B))

    def findSimilarSite(self,es,URL_BOW_list,URL):
        cocs=[]
        vocab=list(set(word for BOW_list in URL_BOW_list for word in BOW_list["BOW"]))
        cos_dict={}

        for BOW_list in URL_BOW_list:
            if URL == BOW_list["URL"]:
                temp_list=[]
                for v in vocab:
                    if v in BOW_list["BOW"].keys():
                        temp_list.append(BOW_list["BOW"][v])
                    else:
                        temp_list.append(0)
                cocs=temp_list.copy()
                break

        for BOW_list in URL_BOW_list:
            if URL != BOW_list["URL"]:
                temp_list=[]
                for v in vocab:
                    if v in BOW_list["BOW"].keys():
                        temp_list.append(BOW_list["BOW"][v])
                    else:
                        temp_list.append(0)
                cos_dict[BOW_list["URL"]] = self.cos_sim(np.array(cocs),np.array(temp_list.copy()))
        
        docs_res = sorted(cos_dict.items(), key=(lambda x:x[1]),reverse=True)
        # print(docs_res)
        return docs_res[0] #tuple 을 반환


