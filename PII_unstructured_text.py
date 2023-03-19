import boto3
import pandas as pd
import numpy as np
from faker import Faker

def getFakeData(tp):
    fake = Faker()
    if(tp=='NAME'):
        synth = fake.name()
    elif(tp=='PHONE'):
        synth = fake.phone_number()
    elif(tp=='EMAIL'):
        synth = fake.email()
    elif tp == "ADDRESS":
        synth = fake.address()
    elif tp == "USERNAME":
        synth = fake.user_name()
    elif tp == "PASSWORD":
        synth = fake.password()
    elif tp == "DATE_TIME":
        synth = fake.date_time()
    elif tp == "CREDIT_DEBIT_NUMBER":
        synth = fake.credit_card_number()
    else:
        synth="UNKNOWN_TYPE"
    return synth

def detectReplacePII(text):
    
    client = boto3.client('comprehend')
    request = client.detect_pii_entities(Text=text,LanguageCode='en')
    print("Detected PII")
    pii = {}
    for i in request['Entities']:
        tp = i['Type']
        if(tp!='AGE'):
            word = text[i['BeginOffset']:i['EndOffset']]
            if(tp in pii.keys()):
                if(word in pii[tp]):
                    pass
                else:
                    synth = getFakeData(tp)
                    pii[tp][word]=synth
            else:
                synth = getFakeData(tp)
                pii[tp] = {word:synth}
    print("Generated fake entities")
    for ent in pii.values():
        for key, val in ent.items():
            text = text.replace(key, str(val))
    print("Replacing PII")
    return [text,pii]