import pandas as pd
from collections import defaultdict
from collections import OrderedDict
import matplotlib.pyplot as plt
import random
import re
import ast
from nltk.corpus import wordnet as wn
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm



nlp = spacy.load("en")
print(nlp)

df_histories=pd.read_excel("sample_history.xlsx")
histories=df_histories["text"].tolist()
histrs=df_histories["problem"].tolist()
onset_list=[]
status_list=[]
severity_list=[]

for i in range(len(histories)):
    u=histories[i].strip()
    doc = nlp(u)
    #print(doc)
    #print([(X.text, X.label_) for X in doc.ents])
    '''
    print("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(
            "text",
            "idx",
            "lemma_",
            "is_punct",
            "is_space",
            "shape_",
            "pos_",
            "tag_"
        ))
    for token in doc:
        print("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(
            token.text,
            token.idx,
            token.lemma_,
            token.is_punct,
            token.is_space,
            token.shape_,
            token.pos_,
            token.tag_
        ))
    for ent in doc.ents:
        print(ent.text, ent.label_)
    for chunk in doc.noun_chunks:
        print(chunk.text, chunk.label_, chunk.root.text)
    '''
    #syms=[]
    statuses=[]
    onsets=[]
    severities=[]

    severity_indicators=set()
    for tem in ['mild', 'moderate', 'severe', 'strong', 'major', 'substantial', 'bad', 'high', 'painful', 'annoying']:
        for ss in wn.synsets(tem):
            for lemma_name in ss.lemma_names():
                severity_indicators.add(lemma_name)
    severity_indicators=list(severity_indicators)
    
    for token in doc:
        lem=token.lemma_.lower()
        #print(lem, token.pos_)
        if token.pos_=="ADJ" and lem in severity_indicators: severities.append(lem)
    
    freq_indicators=["every", "each", "per", "once", "twice", "thrice", "times"]
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            tex=ent.text.lower()
            if any(sub in tex for sub in freq_indicators): continue
            else: onsets.append(tex)

    for chunk in doc.noun_chunks:
        #print("text: " + chunk.text)
        #print("label: " + chunk.label_)
        #print("root: " + chunk.root.text)
        if chunk.root.text == 'DATE':
            tex=chunk.text.lower()
            if any(sub in tex for sub in freq_indicators): continue
            else: onsets.append(tex)
    
    u=u.lower()
    statuses="resolved"
    
    m = re.findall('(not)(.+?)(yet)', u)
    if len(m)>0:
        statuses="active"
    
    m = re.findall('(still)(.+?)(\\.)', u)
    if len(m)>0:
        statuses="active"
    
    m = re.findall('(not)(.+?)(anymore)', u)
    if len(m)>0:
        statuses="resolved"
    
    m = re.findall('(completely|fully)(.+?)(\\.)', u)
    if len(m)>0:
        statuses="resolved"

    m = re.findall('(not completely|not fully)(.+?)(\\.)', u)
    if len(m)>0:
        statuses="active"

    print(doc)
    print(severities)
    print(onsets)
    print(statuses)

    #symptoms=df_symptoms["text"].tolist()
    #syms=df_symptoms["symptom"].tolist()
    onset_list.append(onsets)
    status_list.append(statuses)
    severity_list.append(severities)

df_parsed={
    "text": histories,
    "histories": histrs,
    "severity": severity_list,
    "onset": onset_list,
    "status": status_list 
}

df_res=pd.DataFrame(df_parsed)
df_res.to_csv("parsed_history.csv")

        
            

