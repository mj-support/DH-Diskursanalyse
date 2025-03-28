import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

"""
Dieses Skript visualisiert die Ergebnisse der Sentimentanalyse
"""

def vergleich_regierung_opposition():
    # CSV-Datei einlesen
    df = pd.read_csv('sentimente_all.csv', sep=';')
    # Sentiment-Werte in numerische Werte umwandeln
    sentiment_map = {'Positiv': 1, 'Neutral': 0, 'Negativ': -1}
    df['Sentiment_Num'] = df['Sentiment'].map(sentiment_map)

    # Gruppieren nach Jahr, Rolle und Sentiment
    grouped = round(df.groupby(['Jahr', 'Rolle', 'Sentiment']).size().unstack(fill_value=0), 2)

    # Durchschnittliches Sentiment pro Jahr und Rolle
    avg_sentiment = round(df.groupby(['Jahr', 'Rolle'])['Sentiment_Num'].mean().unstack(), 2)

    # Ergebnisse ausgeben
    print("Sentiment-Verteilung pro Jahr und Rolle:")
    print(grouped)
    print("\nDurchschnittliches Sentiment pro Jahr und Rolle:")
    print(avg_sentiment)

    # Zusätzliche Statistiken
    print("\nGesamtdurchschnitt des Sentiments:")
    print(round(df.groupby('Rolle')['Sentiment_Num'].mean(), 2))

    print("\nJahr mit dem positivsten Sentiment für Regierung:")
    print(avg_sentiment['Regierung'].idxmax(), "mit Wert:", avg_sentiment['Regierung'].max())

    print("\nJahr mit dem negativsten Sentiment für Opposition:")
    print(avg_sentiment['Opposition'].idxmin(), "mit Wert:", avg_sentiment['Opposition'].min())

    print("\nJahr mit dem größten Unterschied im Sentiment zwischen Regierung und Opposition:")
    diff = avg_sentiment['Regierung'] - avg_sentiment['Opposition']
    max_diff_year = diff.abs().idxmax()
    print(max_diff_year, "mit Unterschied:", round(diff[max_diff_year], 2))

    # Visualisierung 2: Liniendiagramm für durchschnittliches Sentiment über die Jahre
    plt.figure(figsize=(12, 6))
    avg_sentiment.plot(kind='line')
    plt.xlabel('Jahr')
    plt.ylabel('Durchschnittliches Sentiment')
    plt.legend()
    plt.tight_layout()
    plt.savefig('Sentiment_nach_Rolle.png', dpi=300)
    plt.show()


    # Visualisierung 3: Heatmap des durchschnittlichen Sentiments
    plt.figure(figsize=(12, 6))
    sns.heatmap(avg_sentiment.T, annot=True, cmap='RdYlGn', center=0, vmin=-1, vmax=1)
    plt.title('Heatmap: Durchschnittliches Sentiment pro Jahr und Rolle')
    plt.tight_layout()
    plt.show()


def entwicklung_sentiment():
    # Daten einlesen & Sentiment in Zahlen umwandeln
    df = pd.read_csv('sentimente_all.csv', sep=';')
    df['Sentiment Score'] = df['Sentiment'].map({'Positiv': 1, 'Neutral': 0, 'Negativ': -1})

    # Durchschnittliches Sentiment und Anzahl der Reden pro Jahr berechnen
    avg_sentiment = df.groupby('Jahr')['Sentiment Score'].mean().round(2)
    speech_counts = df.groupby('Jahr').size()  # Anzahl der Reden pro Jahr

    # Farben für positive und negative Balken
    colors = ['#e74c3c' if x < 0 else '#2ecc71' for x in avg_sentiment]

    # Balkendiagramm mit zentralem Ausgangspunkt
    plt.figure(figsize=(10, 5))
    bars = plt.bar(avg_sentiment.index, avg_sentiment, color=colors, label='Durchschn. Sentiment')

    plt.axhline(0, color='black', linewidth=1)  # Mittellinie

    # X-Achse anpassen: Alle Jahre oder alle 2 Jahre anzeigen
    plt.xticks(avg_sentiment.index, rotation=45, fontsize=16)
    plt.yticks(fontsize=16)

    plt.xlabel('Jahr', fontsize=20)
    plt.ylabel('Sentiment Score', fontsize=20)

    # Anzahl der Reden in die Mitte der Balken schreiben
    for bar, count in zip(bars, speech_counts):
        height = bar.get_height()
        position = height / 2 if height != 0 else 0  # Mitte des Balkens berechnen
        plt.text(bar.get_x() + bar.get_width() / 2, position, str(count),
                 ha='center', va='center', fontsize=14, color='black')

    # Legende hinzufügen
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2ecc71', label='Positiver Score'),
        Patch(facecolor='#e74c3c', label='Negativer Score'),
        Patch(facecolor='black', label='Anzahl Reden')
    ]
    plt.legend(handles=legend_elements, loc='upper left', title='Legende', fontsize=13)

    plt.tight_layout()
    plt.savefig('Sentiment_nach_Jahr.png', dpi=300)
    plt.show()


def vergleich_herkunft():
    # CSV-Datei einlesen
    df = pd.read_csv('sentiment_gruppen.csv', sep=';')

    # Sentiment-Werte in numerische Werte umwandeln
    sentiment_map = {'Positiv': 1, 'Neutral': 0, 'Negativ': -1}
    df['Sentiment_Num'] = df['Sentiment'].map(sentiment_map)

    # --- NEU: Filter für mind. 5 Einträge pro Jahr/Rolle ---
    # Anzahl Einträge pro Jahr-Rolle-Kombination zählen
    count_filter = df.groupby(['Jahr', 'Gruppe'])['Sentiment'].transform('size') >= 5
    filtered_df = df[count_filter]

    # Gruppieren nach Jahr, Rolle und Sentiment
    grouped = round(filtered_df.groupby(['Jahr', 'Gruppe', 'Sentiment']).size().unstack(fill_value=0), 2)
    grouped_unfiltered = round(df.groupby(['Jahr', 'Gruppe', 'Sentiment']).size().unstack(fill_value=0), 2)

    # Durchschnittliches Sentiment pro Jahr und Rolle
    avg_sentiment = round(filtered_df.groupby(['Jahr', 'Gruppe'])['Sentiment_Num'].mean().unstack(), 2)
    avg_sentiment_unfiltered = round(df.groupby(['Jahr', 'Gruppe'])['Sentiment_Num'].mean().unstack(), 2)


    # Ergebnisse ausgeben
    print("Sentiment-Verteilung pro Jahr und Herkunft:")
    print(grouped_unfiltered)
    print("\nDurchschnittliches Sentiment pro Jahr und Herkunft:")
    print(avg_sentiment_unfiltered)

    # Zusätzliche Statistiken
    print("\nGesamtdurchschnitt des Sentiments:")
    print(round(df.groupby('Gruppe')['Sentiment_Num'].mean(), 2))

    print("\nJahr mit dem positivsten Sentiment für Ukraine:")
    print(avg_sentiment['Ukraine'].idxmax(), "mit Wert:", avg_sentiment['Ukraine'].max())

    print("\nJahr mit dem negativsten Sentiment für andere Länder:")
    print(avg_sentiment['Andere Länder'].idxmin(), "mit Wert:", avg_sentiment['Andere Länder'].min())

    print("\nJahr mit dem größten Unterschied im Sentiment zwischen Ukraine und Anderen Länder:")
    diff = avg_sentiment['Ukraine'] - avg_sentiment['Andere Länder']
    max_diff_year = diff.abs().idxmax()
    print(max_diff_year, "mit Unterschied:", round(diff[max_diff_year], 2))

    # Visualisierung 2: Liniendiagramm für durchschnittliches Sentiment über die Jahre
    plt.figure(figsize=(12, 6))
    avg_sentiment.plot(kind='line')
    plt.xlabel('Jahr')
    plt.ylabel('Durchschnittliches Sentiment')
    plt.legend()
    plt.tight_layout()
    plt.savefig('Sentiment_nach_Herkunft.png', dpi=300)
    plt.show()


    # Visualisierung 3: Heatmap des durchschnittlichen Sentiments
    plt.figure(figsize=(12, 6))
    sns.heatmap(avg_sentiment.T, annot=True, cmap='RdYlGn', center=0, vmin=-1, vmax=1)
    plt.title('Heatmap: Durchschnittliches Sentiment pro Jahr und Herkunft')
    plt.tight_layout()
    plt.show()


def stacked_bar_chart():

    # CSV-Datei einlesen
    df = pd.read_csv('sentimente_all.csv', sep=';')

    # Gruppieren nach Jahr und Sentiment
    grouped = df.groupby(['Jahr', 'Sentiment']).size().unstack(fill_value=0)

    # Prozentuale Verteilung berechnen
    grouped_percent = grouped.div(grouped.sum(axis=1), axis=0) * 100

    # Farbschema festlegen
    colors = {'Positiv': '#2ecc71', 'Neutral': '#f1c40f', 'Negativ': '#e74c3c'}

    # Visualisierung mit einem gestapelten Balkendiagramm
    ax = grouped_percent.plot(kind='bar', stacked=True, figsize=(12, 6), color=[colors[col] for col in grouped_percent.columns])

    plt.title('Sentiment-Verteilung pro Jahr', fontsize=16)
    plt.xlabel('Jahr', fontsize=12)
    plt.ylabel('Prozent', fontsize=12)
    plt.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()

    # Ergebnisse ausgeben
    print("Sentiment-Verteilung in Prozent:")
    print(grouped_percent)

    # Gruppieren nach Jahr und Sentiment
    grouped = df.groupby(['Jahr', 'Sentiment']).size().unstack(fill_value=0)

    # Prozentuale Verteilung berechnen
    grouped_percent = grouped.div(grouped.sum(axis=1), axis=0) * 100

    # Farbschema festlegen
    colors = {'Positiv': '#2ecc71', 'Neutral': '#f1c40f', 'Negativ': '#e74c3c'}

    # Visualisierung mit einem gestapelten Balkendiagramm
    fig, ax = plt.subplots(figsize=(15, 8))

    bottom = np.zeros(len(grouped))

    for sentiment in grouped.columns:
        values = grouped[sentiment]
        percentages = grouped_percent[sentiment]
        bars = ax.bar(grouped.index.astype(str), values, bottom=bottom, label=sentiment, color=colors[sentiment])
        bottom += values

        # Prozentzahlen in die Balken einfügen (außer für Neutral)
        for bar, percentage in zip(bars, percentages):
            height = bar.get_height()
            if height > 0 and sentiment != 'Neutral':
                ax.text(bar.get_x() + bar.get_width() / 2., bar.get_y() + height / 2.,
                        f'{percentage:.0f}%', ha='center', va='center', rotation=0,
                        color='black', fontsize=10)

    plt.xlabel('Jahr', fontsize=12)
    plt.ylabel('Anzahl der Reden', fontsize=12)
    plt.legend(title='Sentiment')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('Sentiment_BarChart.png', dpi=300)
    plt.show()

    # Ergebnisse ausgeben
    print("Sentiment-Verteilung (absolut und prozentual):")
    output = pd.DataFrame()
    for sentiment in ['Negativ', 'Neutral', 'Positiv']:
        output[f'{sentiment} absolut'] = grouped[sentiment]
        output[f'{sentiment} %'] = grouped_percent[sentiment].round(0).astype(int).astype(str) + '%'

    print(output.to_string())


def stacked_bar_chart_parteien():
    # CSV-Datei einlesen
    df = pd.read_csv('sentimente_all.csv', sep=';')

    # Gruppieren nach Partei und Sentiment
    grouped = df.groupby(['Partei', 'Sentiment']).size().unstack(fill_value=0)

    # Prozentuale Verteilung berechnen
    grouped_percent = grouped.div(grouped.sum(axis=1), axis=0) * 100

    # Farbschema festlegen
    colors = {'Positiv': '#2ecc71', 'Neutral': '#f1c40f', 'Negativ': '#e74c3c'}

    # Visualisierung mit einem gestapelten Balkendiagramm
    ax = grouped_percent.plot(kind='bar', stacked=True, figsize=(12, 6),
                              color=[colors[col] for col in grouped_percent.columns])

    # Werte in die Balken einfügen (außer für "Neutral")
    for i, bar_group in enumerate(ax.containers):
        sentiment = grouped_percent.columns[i]  # Aktuelle Sentiment-Kategorie
        if sentiment != "Neutral":  # Neutral nicht beschriften
            for bar in bar_group:
                height = bar.get_height()
                if height > 0:  # Nur beschriften, wenn größer als 0
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,  # X-Position (Mitte der Bar)
                        bar.get_y() + height / 2,  # Y-Position (Mitte der Bar)
                        f"{height:.1f}%",  # Prozentwert runden und als String formatieren
                        ha='center', va='center', fontsize=10, color='white', fontweight='bold'
                    )

    plt.xlabel('Partei', fontsize=12)
    plt.ylabel('Prozent', fontsize=12)
    plt.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()

    # Ergebnisse ausgeben
    print("Sentiment-Verteilung in Prozent:")
    print(grouped_percent)

    import textwrap

    # Gruppieren nach Jahr und Sentiment
    grouped = df.groupby(['Partei', 'Sentiment']).size().unstack(fill_value=0)

    # Prozentuale Verteilung berechnen
    grouped_percent = grouped.div(grouped.sum(axis=1), axis=0) * 100

    # Farbschema festlegen
    colors = {'Positiv': '#2ecc71', 'Neutral': '#f1c40f', 'Negativ': '#e74c3c'}

    # Visualisierung mit einem gestapelten Balkendiagramm
    fig, ax = plt.subplots(figsize=(15, 8))

    bottom = np.zeros(len(grouped))

    for sentiment in grouped.columns:
        values = grouped[sentiment]
        percentages = grouped_percent[sentiment]
        bars = ax.bar(grouped.index.astype(str), values, bottom=bottom, label=sentiment, color=colors[sentiment])
        bottom += values

        # Prozentzahlen in die Balken einfügen (außer für Neutral)
        for bar, percentage in zip(bars, percentages):
            height = bar.get_height()
            if height > 0 and percentage > 15:
                ax.text(bar.get_x() + bar.get_width() / 2., bar.get_y() + height / 2.,
                        f'{percentage:.0f}%', ha='center', va='center', rotation=0,
                        color='black', fontsize=18)

    # X-Achsen-Beschriftungen mehrzeilig umbrechen, wenn sie zu lang sind
    labels = grouped.index.astype(str)
    wrapped_labels = [textwrap.fill(label, width=12) for label in labels]  # Text umbrechen bei 10 Zeichen

    # X-Achsen-Beschriftungen setzen
    ax.set_xticks(np.arange(len(grouped)))  # Setze X-Ticks auf die Positionen der Balken
    ax.set_xticklabels(wrapped_labels, rotation=0, fontsize=18)  # Verwende die umgebrochenen Labels

    # Achsenbeschriftungen und Legende
    plt.xlabel('Partei', fontsize=18)
    plt.ylabel('Anzahl der Reden', fontsize=18)
    plt.legend(title='Sentiment', fontsize=18)
    plt.tight_layout()

    # Diagramm speichern und anzeigen
    plt.savefig('Sentiment_nach_Partei.png', dpi=300)
    plt.show()

    # Ergebnisse ausgeben
    print("Sentiment-Verteilung (absolut und prozentual):")
    output = pd.DataFrame()
    for sentiment in ['Negativ', 'Neutral', 'Positiv']:
        output[f'{sentiment} absolut'] = grouped[sentiment]
        output[f'{sentiment} %'] = grouped_percent[sentiment].round(0).astype(int).astype(str) + '%'

    print(output.to_string())


def anzahl_reden():
    # CSV-Datei einlesen
    df_with_group = pd.read_csv('sentiment_gruppen.csv', sep=';')
    df_without_group = pd.read_csv('sentimente_all.csv', sep=';')

    # Anzahl der Reden pro Jahr und Gruppe berechnen
    grouped_with_group = df_with_group.groupby(['Jahr', 'Gruppe']).size().unstack(fill_value=0)

    # Anzahl der Reden pro Jahr berechnen (ohne Gruppen)
    grouped_without_group = df_without_group.groupby(['Jahr']).size()

    # Visualisierung: Liniendiagramm für Anzahl der Reden pro Jahr und Gruppe + Gesamtanzahl ohne Gruppen
    plt.figure(figsize=(12, 6))

    # Linien für "mit Gruppen"
    grouped_with_group.plot(kind='line', ax=plt.gca())

    # Linie für "ohne Gruppen"
    grouped_without_group.plot(kind='line', color='black', label='Gesamtanzahl')

    plt.xlabel('Jahr', fontsize=14)
    plt.ylabel('Anzahl der Reden', fontsize=14)
    plt.legend(title='Gruppe', fontsize=14)
    plt.tight_layout()

    # Diagramm speichern und anzeigen
    plt.savefig('Reden_Anzahl.png', dpi=300)
    plt.show()


def main():
    vergleich_regierung_opposition()
    entwicklung_sentiment()
    vergleich_herkunft()
    stacked_bar_chart()
    stacked_bar_chart_parteien()
    anzahl_reden()


if __name__ == "__main__":
    main()
