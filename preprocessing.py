import pandas as pd
import nltk
from nltk.corpus import stopwords
import string
import spacy

# functions
def prep(doc):
    rem_stop = " ".join([i for i in doc.lower().split() if i not in stopwords_ger])
    rem_punct = "".join(char for char in rem_stop if char not in punct)
    #rem_punct = "".join(char if char not in punct else " " for char in rem_stop) --> replaces punctuation with space
    print("done1")
    print("done2")
    return rem_punct

def lemmatize(text):
    doc = nlp(text)
    print("done 1")
    lem_doc = " ".join([token.lemma_ for token in doc])
    print("done 2")
    return lem_doc

# stopwords and punctuation
stopwords_ger = set(stopwords.words('german'))
punct = set(string.punctuation)
punct.discard("-") # remove '-' bc. e.g. CSU-Bundestagsfraktion -_> csubundestagsfraktion

# lemmatization
nlp = spacy.load("de_core_news_sm")

# import speeches to dataframe
all_speeches = pd.read_json("MethApp/project/reden.json")
all_speeches.head()
all_speeches.columns
all_speeches['Rede'] = all_speeches['Rede'].astype("string")
all_speeches.info()

# apply preprocessing functions
all_speeches['rede_prep'] = all_speeches['Rede'].apply(lemmatize)
all_speeches['rede_prep'] = all_speeches['rede_prep'].apply(prep)

# save to csv
all_speeches.to_csv('MethApp/project/speeches.csv')