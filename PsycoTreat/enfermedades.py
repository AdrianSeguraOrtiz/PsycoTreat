import re
from collections import Counter
from flask_pymongo import pymongo
from unicodedata import normalize

CONNECTION_STRING_MY_DB = "mongodb+srv://adriansegura:adrianseguraortiz1999@psicotreatbd.e4kvw.mongodb.net/PsycoTreat?retryWrites=true&w=majority"
my_client = pymongo.MongoClient(CONNECTION_STRING_MY_DB)
my_db = my_client.get_database('PsycoTreat')
col_enfermedades = pymongo.collection.Collection(my_db, 'enfermedad')

def words(text): return re.findall(r'\w+', text.lower())

enfermedades = []
lista_dict = []
for doc in col_enfermedades.find():
    enfermedades.append(doc['enfermedad'])
    pals_enf = doc['enfermedad'].replace("(", "").replace(")", "").split(" ")
    doc['palabras'] = pals_enf
    lista_dict.append(doc)
ENFERMEDADES = Counter(enfermedades)

def P(word, N=sum(ENFERMEDADES.values())): 
    "Probability of `word`."
    return ENFERMEDADES[word] / N

def correction(word): 
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)

def candidates(word): 
    "Generate possible spelling corrections for word."
    e1 = edits1(word)
    e2 = edits2(word)
    return (known([word]) or codigo([word]) or known(e1) or known(e2) or inside([word]) or asociated([word]) or inside(e1) or [None])

def known(words): 
    "Enfermedades con el mismo nombre que las palabras de entrada"
    res = []
    for w in words:
        for d in lista_dict:
            if w == d['enfermedad'] or w == d['enfermedad'] + ' (' + d['cod_ICD-10'] + ')':
                 res.append(d['enfermedad'] + ' (' + d['cod_ICD-10'] + ')')
    return res

def codigo(words):
    res = []
    for w in words:
        for d in lista_dict:
            if w == d['cod_ICD-10']:
                 res.append(d['enfermedad'] + ' (' + d['cod_ICD-10'] + ')')
    return res

def inside(words):
    "Enfermedades que contienen a las palabras que se pasan como entrada"
    res = []
    for w in words:
        for d in lista_dict:
            if w in d['palabras']:
                res.append(d['enfermedad'] + ' (' + d['cod_ICD-10'] + ')')
    return res

def asociated(words):
    "Enfermedades que se encuentran asociadas a las palabras que se pasan como entrada"
    res = []
    for w in words:
        for d in lista_dict:
            if w in d['palabras_asociadas']:
                res.append(d['enfermedad'] + ' (' + d['cod_ICD-10'] + ')')
    return res

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnñopqrstuvwxyzáéíóú'
    mayuscula  = [word.upper()]
    minuscula  = [word.lower()]
    sin_tildes = [normalize("NFKD", word).encode("ascii","ignore").decode("ascii")]
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(mayuscula + minuscula + sin_tildes + deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))