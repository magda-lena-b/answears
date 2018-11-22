# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 21:19:53 2018

@author: Mag
"""

import bs4 as bs
import urllib.request
import re
import nltk
import pickle
from gensim.models import Word2Vec
from nltk.corpus import stopwords
import datetime
import wikipediaapi

wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI)

## druga opcja to HTML a nie jest ok



class Answer():
    
    def __init__(self):
        self.text_base = ''
                
    def create_model(self, subj: str):
        
        self.gather_data(subj)

        if len(self.text_base)==0:
            raise Exception('No text for model to learn')
         

        self.text_base = self.process_text(self.text_base)

        sentences = nltk.sent_tokenize(self.text_base)
        sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
        stop_list = stopwords.words('english')
        for i in range(len(sentences)):
            sentences[i] = [word for word in sentences[i] if word not in stop_list]

        return Word2Vec(sentences, min_count=3)
            
       
    def gather_data(self, subj: str):
        
        print('Gathering data')
        page_start = wiki_wiki.page(subj.lower())
            
        assert (page_start.exists()==1), 'Sorry, no information about this subject in wikipedia...'
        
        self.text_base = page_start.text
        links = page_start.links
        
        if len(links.keys())!=0:
            i, j =1, 0
            time_start = datetime.datetime.now()
            print('Pages to read: ', len(links.keys()))
            
            for link in links.keys(): 
                self.text_base += wiki_wiki.page(link).text
                if round(100*i/len(links.keys()),0)>=j+5:
                    j=round(100*i/len(links.keys()),0)
                    print('Current progress: {:.0f}% pages.'.format(j))
                i+=1
            time_stop = datetime.datetime.now()
            print('Total time: ', time_stop-time_start)
    
    
     
    def what_is_the_meaning_of(self, question: str = 'life', according_to: str = 'monthy python'):
        print('Checking existing models...')
        try:
            with open('models.pickle','rb') as f:
                models_dict = pickle.load(f)
        except Exception as e:
            print('No models stored yet.')
            models_dict={}
            
        if according_to in models_dict.keys():
            self.model = models_dict[according_to]
            print('Model loaded.')
        else:
            print('New model will be created.')
            self.model = self.create_model(according_to)
            models_dict[according_to] = self.model
            with open('models.pickle','wb') as f:
                pickle.dump(models_dict,f)
                
        print('The meaning of {} according to {} is : {}, {} or {}.'.format(question, according_to, self.model.wv.most_similar(question)[0][0],self.model.wv.most_similar(question)[1][0],self.model.wv.most_similar(question)[2][0]) )
    
    @staticmethod
    def process_text(text: str):
        
        text = re.sub(r"[\[\]=,.!?\-'()\"]", " ", text)
        text = re.sub(r"<[a-z/]+>", " ", text)
        text = text.lower()
        text = re.sub(r'\d', ' ', text)
        text = re.sub(r"\s+", " ", text)

        return text