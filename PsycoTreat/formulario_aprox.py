import re
from collections import Counter
from flask_pymongo import pymongo
from unicodedata import normalize

CONNECTION_STRING_MY_DB = "mongodb+srv://adriansegura:adrianseguraortiz1999@psicotreatbd.e4kvw.mongodb.net/PsycoTreat?retryWrites=true&w=majority"
my_client = pymongo.MongoClient(CONNECTION_STRING_MY_DB)
my_db = my_client.get_database('PsycoTreat')
col_enfermedades = pymongo.collection.Collection(my_db, 'enfermedad')

def damePorcentajes(motivo, desencadenante, observaciones, diagnostico):
    res = {}
    lista_dict = col_enfermedades.find()
    for d in lista_dict:
        score = 0
        for w_motivo in motivo.replace(',', '').replace('(', '').replace(')', '').split(" "):
            if w_motivo in d['palabras_asociadas']:
                score = score + 1
        for w_des in desencadenante.replace(',', '').replace('(', '').replace(')', '').split(" "):
            if w_des in d['palabras_asociadas']:
                score = score + 2
        for w_obs in observaciones.replace(',', '').replace('(', '').replace(')', '').split(" "):
            if w_obs in d['palabras_asociadas']:
                score = score + 3
        for w_diag in diagnostico.replace(',', '').replace('(', '').replace(')', '').split(" "):
            if w_diag in d['palabras_asociadas']:
                score = score + 4
        if score != 0:
            res[d['enfermedad']] = score
    total = sum(res.values())
    for k,v in res.items():
        res[k] = str(round((v/total)*100,2)) + ' %'
    res = str(res).replace('{', '').replace('}', '').replace(', ', '\n').replace("'", '')
    return res