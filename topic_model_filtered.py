import pandas as pd
import numpy as np
import nltk
nltk.download('wordnet')
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
from sklearn.metrics import log_loss

n_top_words = 10

def display_topics(model, feature_names, n_top_words):
    for topic_index, topic in enumerate(model.components_):
        print("Topic: ", topic_index )
        print(" ".join([feature_names[i] for i in topic.argsort()[: -n_top_words -1:-1]]))

def plot_top_words(model, feature_names, n_top_words, title):
    fig, axes = plt.subplots(2, 3, figsize=(30, 15), sharex=True)
    axes = axes.flatten()
    for topic_idx, topic in enumerate(model.components_):
        top_features_ind = topic.argsort()[: -n_top_words - 1 : -1]
        top_features = [feature_names[i] for i in top_features_ind]
        weights = topic[top_features_ind]
        ax = axes[topic_idx]
        ax.barh(top_features, weights, height=0.7)
        ax.set_title(f"Topic {topic_idx +1}", fontdict={"fontsize": 20})
        ax.invert_yaxis()
        ax.tick_params(axis="both", which="major", labelsize=15)
        for i in "top right left".split():
            ax.spines[i].set_visible(False)
        fig.suptitle(title, fontsize=30)
    plt.subplots_adjust(top=0.90, bottom=0.05, wspace=0.90, hspace=0.3)
    plt.show()

#load dataset
df = pd.read_csv('MethApp/project/filtered_speeches.csv')

documents = df['rede_prep']
documents = documents.fillna("")

# create DTM to feed to LDA
tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2) # matrix of token counts
dtm = tf_vectorizer.fit_transform(documents) # document-term matrix
vocab = tf_vectorizer.get_feature_names_out() # list of top 1000 words that appear in the documents

# test different parameters
lda1 = LatentDirichletAllocation(n_components=10, max_iter=20, learning_method='online', learning_offset=50, random_state=0)
lda2 = LatentDirichletAllocation(n_components=9, max_iter=20, learning_method='online', learning_offset=50, random_state=0)
lda3 = LatentDirichletAllocation(n_components=8, max_iter=20, learning_method='online', learning_offset=50, random_state=0)
lda4 = LatentDirichletAllocation(n_components=7, max_iter=20, learning_method='online', learning_offset=50, random_state=0)
lda5 = LatentDirichletAllocation(n_components=6, max_iter=20, learning_method='online', learning_offset=50, random_state=0)
lda6 = LatentDirichletAllocation(n_components=5, max_iter=20, learning_method='online', learning_offset=50, random_state=0)

lda1.fit(dtm)
score1 = lda1.score(dtm)
perplexity1 = lda1.perplexity(dtm)

lda2.fit(dtm)
score2 = lda2.score(dtm)
perplexity2 = lda2.perplexity(dtm)

lda3.fit(dtm)
score3 = lda3.score(dtm)
perplexity3 = lda3.perplexity(dtm)

lda4.fit(dtm)
score4 = lda4.score(dtm)
perplexity4 = lda4.perplexity(dtm)

lda5.fit(dtm)
score5 = lda5.score(dtm)
perplexity5 = lda5.perplexity(dtm)

lda6.fit(dtm)
score6 = lda6.score(dtm)
perplexity6 = lda6.perplexity(dtm)

lda_models = [lda1,lda2,lda3,lda4,lda5,lda6]
scores = [score1, score2, score3, score4, score5, score6]
perplexities = [perplexity1, perplexity2, perplexity3, perplexity4, perplexity5, perplexity6]

# lowest perplexity: lda6
eval = {"models": lda_models, "scores": scores, "perplexities" : perplexities}
eval_df = pd.DataFrame(eval)
eval_df.to_csv('MethApp/project/evaluation_filtered_topic_models.csv')

# fit lda model with optimized parameters
lda = LatentDirichletAllocation(n_components=5, max_iter=20, learning_method='online', learning_offset=50, random_state=0)
lda.fit(dtm)
lda.perplexity(dtm)
lda.score(dtm)

# plot top words
display_topics(lda, vocab, n_top_words)
plot_top_words(lda, vocab, n_top_words, "")

# get topic distribution for each document
T=lda.fit_transform(dtm)
colnames = ["Topic "+str(i+1) for i in range(lda.n_components)]

df['Datum'] = pd.to_datetime(df['Datum'], format='%d-%m-%Y')
df['Jahr-Monat'] = df['Datum'].dt.to_period('M')
docnames = df['Jahr-Monat']

# probabilities for each topic in each protocol
df_T = pd.DataFrame(np.round(T, 2), columns=colnames, index=docnames)
piv_table = df_T.groupby('Jahr-Monat').mean()

# save piv_table
piv_table.to_excel("MethApp/project/filtered_topic distribution per month.xlsx")

#separate into 2 plots
middle = len(piv_table) // 2
first_half = piv_table.iloc[:middle]
second_half = piv_table.iloc[middle:]

fig, axes = plt.subplots(2, 1, figsize = (15, 8))

# Plot first half
first_half.plot(kind='line', colormap='tab20', ax=axes[0], marker='o')
axes[0].set_title('Themenentwicklung (Nov 2009 - Mai 2017)')
axes[0].set_xlabel('Monat')
axes[0].set_ylabel('Themenwahrscheinlichkeit')
axes[0].legend(title='Themen', bbox_to_anchor=(1.05, 1), loc='upper left')
axes[0].grid(axis='y', linestyle='--', alpha=0.7)
axes[0].set_xticks(first_half.index[::5])
axes[0].set_xticklabels(first_half.index[::5], rotation = -90)
# Plot second half
second_half.plot(kind='line', colormap='tab20', ax=axes[1], marker='o')
axes[1].set_title('Themenentwicklung (Juni 2017 - Feb 2025)')
axes[1].set_xlabel('Monat')
axes[1].set_ylabel('Themenwahrscheinlichkeit')
axes[1].legend(title='Themen', bbox_to_anchor=(1.05, 1), loc='upper left')
axes[1].grid(axis='y', linestyle='--', alpha=0.7)
axes[1].set_xticks(second_half.index[::5])
axes[1].set_xticklabels(second_half.index[::5], rotation = -90)

# adjust layout and plot
plt.tight_layout()
plt.show()