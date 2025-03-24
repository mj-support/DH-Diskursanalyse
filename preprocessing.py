import pandas as pd
import regex as re
#import nltk
from nltk.corpus import stopwords
import string
import spacy

# stopwords and punctuation
stopwords_ger = set(stopwords.words('german'))
len(stopwords_ger)
words_to_remove = ["--", "frau", "herr", "kollege", "kollegen", "kollegin", "kolleginn", "kolleginne" "damen", "herren", "geehrt", "sagen", "müssen", "ganz", "schon", "geben", "werden", "gehen","tun", "sein"]
stopwords_ger.update(words_to_remove)
punct = set(string.punctuation)
more_punct = ("–", "„","“")
punct.update(more_punct)

# lemmatization
nlp = spacy.load("de_core_news_sm")
# functions
def clean(doc):
    #no_punct = re.sub(r'\s([.,!?;:-])', ' ', doc)
    no_punct = "".join(char for char in doc if char not in punct).lower()
    #no_punct = punct_pattern
    no_stop = " ".join([i for i in no_punct.split() if i not in stopwords_ger])
    #rem_punct = "".join(char if char not in punct else " " for char in rem_stop) --> replaces punctuation with space
    print("stopwords and punctuation removed")
    text = nlp(no_stop)
    lemmatized = " ".join([token.lemma_.lower() for token in text])
    print("lemmatized")
    return lemmatized

# sample
sample = pd.read_json("MethApp/project/sample.json")
sample.columns
sample['Rede'].astype("string")
sample['rede_prep'] = sample['Rede'].apply(clean)
sample
sample["ID"] = sample["Plenarprotokoll"].astype(str) + "_" + (sample.groupby("Plenarprotokoll").cumcount() + 1).astype(str)

# import speeches to dataframe
speeches_a = pd.read_json("MethApp/project/reden_a.json")
speeches_a['Rede'] = speeches_a['Rede'].astype("string")

speeches_b = pd.read_json("MethApp/project/reden_b.json")
speeches_b['Rede'] = speeches_b['Rede'].astype("string")

all_speeches = pd.concat([speeches_a, speeches_b], ignore_index=True)
all_speeches['rede_prep'] = all_speeches['Rede'].apply(clean)

all_speeches = pd.read_csv('MethApp/project/speeches.csv')
all_speeches["ID"] = all_speeches["Plenarprotokoll"].astype(str) + "_" + (all_speeches.groupby("Plenarprotokoll").cumcount() + 1).astype(str)
all_speeches
all_speeches.to_csv('MethApp/project/speeches.csv')

##################
#remove certain words
def remove_words(df, column, words_to_remove):
    pattern = r'\b('+'|'.join(map(re.escape, words_to_remove))+r')\b'
    df[column] = df[column].str.replace(pattern, '', regex=True).str.strip()
    return df
words_to_remove = ["--", "frau", "herr", "kollege", "kollegen", "kollegin", "kolleginn", "kolleginne" "damen", "herren", "geehrt", "sagen", "müssen", "ganz", "schon", "geben", "werden", "gehen","tun", "sein"]
all_speeches = remove_words(all_speeches,'rede_prep', words_to_remove)
# save to csv
all_speeches.to_csv('MethApp/project/speeches.csv')
all_speeches = pd.read_csv('MethApp/project/speeches.csv')

all_speeches['rede_prep'].iloc[24]