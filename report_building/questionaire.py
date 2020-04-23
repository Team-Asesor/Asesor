import pandas as pd
from collections import defaultdict
from collections import OrderedDict
import matplotlib.pyplot as plt
import random
import re
import ast


df_family=pd.read_excel("p_0_family.xlsx")
df_medication=pd.read_excel("p_0_medication.xlsx")
df_history=pd.read_excel("p_0_history.xlsx")
df_allergy=pd.read_excel("p_0_allergy.xlsx")
df_ques=pd.read_excel("questions.xlsx")
df_ques=df_ques[["id", "text"]]

ques_list=[]
ques_list.append("Greetings!!")
for i, row in df_ques.iterrows():
    ques_list.append(row["text"])

past_medications=df_medication["medication"].tolist()
past_history=df_history["problem"].tolist()
past_allergy=df_allergy["allergy"].tolist()

print(past_medications)
medic=" "
if len(past_medications)==1:
    medic=past_medications[-1]
elif len(past_medications)==2:
    medic+=past_medications[0]+" and "+past_medications[-1]
else:
    part1=past_medications[:-1]
    medic=", ".join(part1)
    medic+=", and "+past_medications[-1]

print(past_history)
history=" "
if len(past_history)==1:
    history=past_history[-1]
elif len(past_history)==2:
    history+=past_history[0]+" and "+past_history[-1]
else:
    part1=past_history[:-1]
    history=", ".join(part1)
    history+=", and "+past_history[-1]

print(past_allergy)
allergy=" "
if len(past_allergy)==1:
    allergy=past_allergy[-1]
elif len(past_allergy)==2:
    allergy+=past_allergy[0]+" and "+past_allergy[-1]
else:
    part1=past_allergy[:-1]
    allergy=", ".join(part1)
    allergy+=", and "+past_allergy[-1]

last_ques=18
current_ques=1

while(current_ques!=last_ques):
    next_ques=current_ques
    if current_ques==1:
        ans=input(ques_list[current_ques])
        if "new" in ans: next_ques=2
        elif "follow" in ans: next_ques=4
    elif current_ques==3:
        ans=input(ques_list[current_ques])
        next_ques=8
    elif current_ques==7:
        prompt=ques_list[current_ques].replace("placeholder", medic)
        ans=input(prompt)
        next_ques=8
    elif current_ques==8:
        prompt=ques_list[current_ques].replace("placeholder", history)
        ans=input(prompt)
        if "yes" in ans: next_ques=9
        elif "no" in ans: next_ques=10
    elif current_ques==10:
        prompt=ques_list[current_ques].replace("placeholder", allergy)
        ans=input(prompt)
        if "yes" in ans: next_ques=11
        elif "no" in ans: next_ques=16
    elif current_ques==11:
        ans=input(ques_list[current_ques])
        next_ques=16
    else:
        ans=input(ques_list[current_ques])
        next_ques=current_ques+1
    current_ques=next_ques
