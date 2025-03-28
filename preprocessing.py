import pandas as pd
import regex as re
from nltk.corpus import stopwords
import string
import spacy
import string

# stopwords, punctuation and lemmatization
punct = set(string.punctuation)
more_punct = ("–", "„","“")
punct.update(more_punct)

stopwords_ger = set(stopwords.words('german'))

nlp = spacy.load("de_core_news_sm")

# functions
def clean(doc):
    if isinstance(doc, list):
        doc = " ".join(doc)
    no_punct = "".join(char for char in doc if char not in punct).lower()
    no_stop = " ".join([i for i in no_punct.split() if i not in stopwords_ger])
    print("stopwords and punctuation removed")
    text = nlp(no_stop)
    lemmatized = " ".join([token.lemma_.lower() for token in text])
    print("lemmatized")
    return lemmatized

def remove_words(df, column, words_to_remove):
    pattern = r'\b('+'|'.join(map(re.escape, words_to_remove))+r')\b'
    df[column] = df[column].str.replace(pattern, '', regex=True).str.strip()
    return df

# import speeches to dataframe
speeches_a = pd.read_json("MethApp/project/reden_a.json")
speeches_a['Rede'] = speeches_a['Rede'].astype("string")

speeches_b = pd.read_json("MethApp/project/reden_b.json")
speeches_b['Rede'] = speeches_b['Rede'].astype("string")

all_speeches = pd.concat([speeches_a, speeches_b], ignore_index=True)
all_speeches['rede_prep'] = all_speeches['Rede'].apply(clean)

all_speeches["ID"] = all_speeches["Plenarprotokoll"].astype(str) + "_" + (all_speeches.groupby("Plenarprotokoll").cumcount() + 1).astype(str)
all_speeches = all_speeches.drop(columns = ["Unnamed: 0.4", "Unnamed: 0.3", "Unnamed: 0.2", "Unnamed: 0.1", "Unnamed: 0"])

#remove certain words
words_to_remove = [
    "--", "ja", "nein", "ganz", "schon", "thomas", "peter", "michael", "matthias",
    "frau", "herr", "dr", "kollege", "kollegen", "kollegin", "kolleginn", "kolleginne", "damen", "herren", "geehrt",
    "fraktion", "abgeordneter", "abgeordnete", "präsident", "präsidentin", "vizepräsident", "vizepräsidentin",
    "geben", "werden", "gehen","tun", "sein", "sagen", "müssen"
]
names = all_speeches['Rednerin'].apply(lambda x: 
    x.split()[-1] if ',' not in str(x) else x.split(',')[0].split()[-1]
).tolist()
set_names = set(names)

all_speeches = remove_words(all_speeches,'rede_prep', words_to_remove)
all_speeches = remove_words(all_speeches,'rede_prep', set_names)

# save to csv
all_speeches.to_csv('MethApp/project/speeches.csv')

# filter documents to only keep docs with certain words
searchwords = [
    "Geflüchtete", "Flüchtling", "Refugees", "Refugee", "Flüchtlinge", "Asyl", "Asylbewerber", "Flüchtling", "Asylant", "Asylantin", "Asylanten", "Asylantinnen"
]

pattern = '|'.join(searchwords)
mask = all_speeches['Rede'].str.contains(pattern, case=False, na=False)
filtered_df = all_speeches[mask]
filtered_df.to_csv('MethApp/project/filtered_speeches.csv')