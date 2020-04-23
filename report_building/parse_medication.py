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

df_medications=pd.read_excel("sample_medication.xlsx")
medication_list=df_medications["text"].tolist()
medication_list_med=df_medications["medication"].tolist()
dosage_list=[]
timing_list=[]
purpose_list=[]
for i in range(len(medication_list)):
    u=medication_list[i].strip()
    doc = nlp(u)
    dosages=[]
    timings=[]
    medications=[]
    purposes=[]

    dosage_indicators=["every", "each", "per", "once", "twice", "thrice", "times"]
    for ent in doc.ents:
        #print(ent.text, ent.label_)
        if ent.label_ == 'DATE':
            tex=ent.text.lower()
            if any(sub in tex for sub in dosage_indicators): dosages.append(tex)
            else: timings.append(tex)

    for chunk in doc.noun_chunks:
        #print("text: " + chunk.text)
        #print("label: " + chunk.label_)
        #print("root: " + chunk.root.text)
        if chunk.root.text == 'DATE':
            tex=chunk.text.lower()
            if any(sub in tex for sub in dosage_indicators): dosages.append(tex)
            else: timings.append(tex)
        else:
            word_a=chunk.root.text
            for token in doc:
                word_b=token.text.lower()
                if word_a!=word_b:
                    continue
                lem=token.lemma_.lower()
                #print(lem, token.pos_)
                if token.pos_=="NOUN" and token.tag_=="NN":
                    s_lower= chunk.text.strip().lower()
                    if 'purpose' not in s_lower and 'medication' not in s_lower and 'dosage' not in s_lower and 'timing' not in s_lower:medications.append(chunk.text)
                    s_lower= chunk.text.strip().lower()
                    if 'purpose' not in s_lower and 'medication' not in s_lower and 'dosage' not in s_lower and 'timing' not in s_lower:purposes.append(chunk.text) 

    
    
    parts=u.split()
    possible=["every", "once", "twice", "thrice"]
    for index, part in enumerate(parts):
        if (part=="times" or part=="time") and index>0:
            new_dosage=parts[index-1]+" "+parts[index]
            possible.append(new_dosage)

    u=u.lower() 
    possible_prefix="|".join(possible)
    possible_prefix="("+possible_prefix+")"
    m = re.findall(possible_prefix+'(.*?)(\\.|day|week|month|year)', u)
    
    if m!=None:
        for m_elem in m:
            t=m_elem[0]+m_elem[1]+m_elem[2]
            dosages.append(t)
    dosages=list(set(dosages))
    '''
    m = re.findall('(take|taking|took|taken|takes|taken)(.*?)(\\.|for|since)', u)
    
    if m!=None:
        for m_elem in m:
            t=m_elem[1]
            medications.append(t)
    '''
    medications=list(set(medications))
    
    
    m = re.findall('(take|taking|took|taken|takes|taken|use|using|used|uses)(.+?)(for)(.+?)(\\.)', u)
    

    if m!=None:
        for m_elem in m:
            #print(m_elem)
            t=m_elem[3]
            s=m_elem[1]
            t_parts=t.split()
            s_parts=s.split()
            if len(t_parts)<=2: 
                purposes.append(t.strip().lower())
            if len(s_parts)<=2: 
                medications.append(s.strip().lower())
    
    purposes=list(set(purposes))
    medications=list(set(medications))

    m = re.findall('(medication |medication:|medications |medications:)(.+?)(,|\\.|and)', u)
    if m!=None:
        for m_elem in m:
            s=m_elem[1]
            if len(s_parts)<=2:
                s_lower= s.strip().lower()
                medications.append(s_lower)
    medications=list(set(medications))
    
    m = re.findall('(purpose |problem |purpose:|purposes |purposes:)(.+?)(,|\\.|and)', u)
    if m!=None:
        for m_elem in m:
            s=m_elem[1]
            if len(s_parts)<=2: 
                s_lower= s.strip().lower()
                purposes.append(s_lower)
    purposes=list(set(purposes))

    m = re.findall('(timing |timing:|timings |timings:)(.+?)', u)
    if m!=None:
        for m_elem in m:
            s=m_elem[1]
            if len(s_parts)<=2: 
                s_lower=s.strip().lower()
                if s_lower!="":
                    timings.append(s_lower)
    timings=list(set(timings))

    m = re.findall('(dosage |dosage:|dosages |dosages:)(.+?)', u)
    if m!=None:
        for m_elem in m:
            s=m_elem[1]
            if len(s_parts)<=2: 
                s_lower=s.strip().lower()
                if s_lower!="":
                    dosages.append(s_lower)
    dosages=list(set(dosages))

    print("response: ")
    print(doc)
    print("medications: ")
    print(medications)
    print("purpose: ")
    print(purposes)
    print("timing: ")
    print(timings)
    print("dosages: ")
    print(dosages)

    #df_medications=pd.read_excel("sample_medication.xlsx")
    #medication_list=df_medications["text"].tolist()
    #medication_list_med=df_medications["medication"].tolist()
    dosage_list.append(dosages)
    timing_list.append(timings)
    purpose_list.append(purposes)

dic_res={
    "text":medication_list,
    "medications": medication_list_med,
    "purposes": purpose_list,
    "dosages": dosage_list,
    "timings": timing_list
}

df_res=pd.DataFrame(dic_res)
df_res.to_csv('parsed_medication.csv')
    
    
        
            

