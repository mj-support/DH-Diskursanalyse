import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report

df = pd.read_csv('sentiment_analyse_test.csv')

print("Datensatz-Informationen:")
print(f"Anzahl der Datensätze: {len(df)}")
print("\nVerteilung der manuellen Labels (sentiment_val):")
print(df['Sentiment_Manuell'].value_counts())
print("\nVerteilung der LLM-Labels (sentiment_test):")
print(df['Sentiment'].value_counts())

labels = ["positiv", "negativ", "neutral"]

# Accuracy
accuracy = accuracy_score(df['Sentiment_Manuell'], df['Sentiment'])

# Precision, Recall und F1-Score (mit average='macro' für Multi-Class-Klassifikation)
precision = precision_score(df['Sentiment'], df['Sentiment_Manuell'], 
                           labels=labels, average='macro', zero_division=0)
recall = recall_score(df['Sentiment'], df['Sentiment_Manuell'], 
                     labels=labels, average='macro', zero_division=0)
f1 = f1_score(df['Sentiment'], df['Sentiment_Manuell'], 
             labels=labels, average='macro', zero_division=0)

# Klassenspezifische Metriken
class_report = classification_report(df['Sentiment'], df['Sentiment_Manuell'], 
                                    labels=labels, output_dict=True)

# Confusion Matrix
conf_matrix = confusion_matrix(df['Sentiment'], df['Sentiment_Manuell'], labels=labels)

print("\n--- Allgemeine Metriken ---")
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision (macro): {precision:.4f}")
print(f"Recall (macro): {recall:.4f}")
print(f"F1-Score (macro): {f1:.4f}")

print("\n--- Klassenspezifische Metriken ---")
for label in labels:
    print(f"\nLabel: {label}")
    print(f"Precision: {class_report[label]['precision']:.4f}")
    print(f"Recall: {class_report[label]['recall']:.4f}")
    print(f"F1-Score: {class_report[label]['f1-score']:.4f}")
    print(f"Support: {class_report[label]['support']}")

# Visualisierungen

# Balkendiagramm der Metriken
plt.figure(figsize=(10, 6))
metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
values = [accuracy, precision, recall, f1]
bars = plt.bar(metrics, values, color=['skyblue', 'lightgreen', 'salmon', 'plum'])

# Werte über den Balken anzeigen
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
            f'{height:.4f}', ha='center', va='bottom', fontweight='bold')

plt.ylim(0, 1.1)  # y-Achse von 0 bis 1.1
plt.title('Leistungsmetriken der Sentiment-Klassifikation')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('sentiment_metriken.png', dpi=300, bbox_inches='tight')
plt.close()

# Confusion Matrix visualisieren
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
           xticklabels=labels, yticklabels=labels)
plt.xlabel('Vorhergesagte Labels')
plt.ylabel('Tatsächliche Labels')
plt.title('Confusion Matrix')
plt.tight_layout()
plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
plt.close()

# Klassenspezifische Metriken visualisieren
metrics_per_class = pd.DataFrame({
    'Precision': [class_report[label]['precision'] for label in labels],
    'Recall': [class_report[label]['recall'] for label in labels],
    'F1-Score': [class_report[label]['f1-score'] for label in labels]
}, index=labels)

metrics_per_class.plot(kind='bar', figsize=(10, 6), width=0.8)
plt.title('Klassenspezifische Metriken')
plt.xlabel('Klasse')
plt.ylabel('Wert')
plt.ylim(0, 1.1)
plt.legend(loc='lower right')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('klassenspezifische_metriken.png', dpi=300, bbox_inches='tight')
plt.close()

# Zusätzliche Analyse: Falsch klassifizierte Beispiele
misclassified = df[df['Sentiment'] != df['Sentiment_Manuell']]
print(f"\nAnzahl falsch klassifizierter Beispiele: {len(misclassified)}")

if len(misclassified) > 0:
    print("\nBeispiele für falsch klassifizierte Einträge:")
    if 'text' in misclassified.columns:
        for idx, row in misclassified.head(5).iterrows():
            print(f"Text: {row['text']}")
            print(f"Tatsächliches Label: {row['Sentiment_Manuell']}")
            print(f"Vorhergesagtes Label: {row['Sentiment']}")
            print("---")

print("\nAnalyse abgeschlossen. Visualisierungen wurden gespeichert.")

# DataFrame mit allen Ergebnissen speichern
df['korrekt'] = df['Sentiment_Manuell'] == df['Sentiment']
df.to_csv('sentiment_analyse_ergebnisse.csv', index=False)