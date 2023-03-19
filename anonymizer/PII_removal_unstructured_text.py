import boto3
import pandas as pd
import numpy as np

def detectReplacePII(text):
    
    client = boto3.client('comprehend')
    request = client.detect_pii_entities(Text=text,LanguageCode='en')
    pii = {}
    for i in request['Entities']:
        tp = i['Type']
        if(tp!='AGE'):
            word = text[i['BeginOffset']:i['EndOffset']]
            if(tp in pii.keys()):
                if(word in pii[tp]):
                    pass
                else:
                    synth = "XXXXXX"
                    pii[tp][word]=synth
            else:
                synth = "XXXXXX"
                pii[tp] = {word:synth}
    for ent in pii.values():
        for key, val in ent.items():
            text = text.replace(key, str(val))
    return [text,pii]