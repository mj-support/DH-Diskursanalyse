import time
import os
import torch
import json
import csv

from mistral_inference.transformer import Transformer
from mistral_inference.generate import generate

from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from mistral_common.protocol.instruct.messages import UserMessage
from mistral_common.protocol.instruct.request import ChatCompletionRequest

"""
Dieses Skript für eine Sentimentanalyse auf die gefilterten Reden (für alle Geflüchtete, für die Ukraine und für andere Länder) durch.
Das Ergebnis ist jeweils eine CSV-Datei mit dem jeweiligen Sentiment pro Rede und der Begründung.
Um die mistral_inference-Bibliothek benutzen zu können, muss eine GPU vorhanden sein.
Zudem muss vorher das Sprachmodelle runtergeladen und gespeichert werden -> https://models.mistralcdn.com/mistral-7b-v0-3/mistral-7B-Instruct-v0.3.tar
Die Benutzung eines Clusters wird empfohlen.
"""


def sentiment_analysis():
    start_time = time.time()
    # load model
    model = Transformer.from_folder(os.path.expanduser("~") + "/mistral_7b_instruct_v3", dtype=torch.float16)
    # load tokenizer
    mistral_tokenizer = MistralTokenizer.from_file(os.path.expanduser("~") + "/mistral_7b_instruct_v3/tokenizer.model.v3")

    with open("Plenarprotokolle/reden/gefilterte_reden.json", "r", encoding="utf-8") as f:
        gefilterte_reden = json.load(f)

    with open('Plenarprotokolle/reden/sentiment_all.csv', 'w', newline='', encoding='utf-8') as csvfile:
        # CSV-Writer erstellen
        csv_writer = csv.writer(csvfile, delimiter=';')

        # Header schreiben
        csv_writer.writerow(['Datum', 'Rednerin', 'Partei', 'Sentiment', 'Text'])

        for index, gefilterte_rede in enumerate(gefilterte_reden):
            start_time2 = time.time()

            datum = gefilterte_rede["Datum"]
            rednerin = gefilterte_rede["Rednerin"]
            rede = gefilterte_rede["Rede"]
            partei = gefilterte_rede["Partei"]

            prompt = f"""
            Du bist ein Experte für Sentimentanalysen von Bundestagsreden in Bezug auf Geflüchtete.
            Gegebene sei folgende Rede.
            Rede: <<<{rede}>>>
    
            Welcher spezifische Aspekt von Geflüchteten wird beschrieben?
            Welche implizite Meinung wird zu diesem Aspekt geäußert?
            Klassifiziere auf dieser Grundlage das implizite Sentiment der Rede in einem Wort (positiv, negativ, neutral).
    
            Das Ausgabformat soll im JSON-Format sein:
            {{
                "Sentiment": "Positiv/Negativ/Neutral",
                "Begründung": "Maximal 3 Sätze, keine Absätze",
            }}
            """

            # chat completion request
            completion_request = ChatCompletionRequest(messages=[UserMessage(content=prompt)])
            # encode message
            tokens = mistral_tokenizer.encode_chat_completion(completion_request).tokens
            # generate results
            out_tokens, _ = generate([tokens], model, max_tokens=500, temperature=0.1,
                                     eos_id=mistral_tokenizer.instruct_tokenizer.tokenizer.eos_id)
            # decode generated tokens
            sentiment = mistral_tokenizer.instruct_tokenizer.tokenizer.decode(out_tokens[0])
            print(f"--------{index}---------")
            print(partei)
            print(sentiment)
            csv_writer.writerow([datum, rednerin, partei, sentiment, rede])

    print("--- %s seconds ---" % (time.time() - start_time2))
    print("--- %s seconds ---" % (time.time() - start_time))
    
def postprocessing():
    # Input- und Output-Dateien
    input_file = "Plenarprotokolle/reden/sentiment_all.csv"
    output_file = "sentiment_all.csv"

    # Neue CSV-Datei erstellen
    with open(input_file, mode='r', encoding='utf-8') as infile, open(output_file, mode='w', encoding='utf-8',
                                                                      newline='') as outfile:
        reader = csv.DictReader(infile, delimiter=';')  # Annahme: Tab-separierte CSV
        fieldnames = ['Datum', 'Rednerin', 'Partei', 'Sentiment', 'Begründung', 'Rede']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()

        for row in reader:
            # JSON-String in Dictionary umwandeln
            sentiment_data = row['Sentiment']
            try:
                sentiment_data = json.loads(sentiment_data)
            except:
                sentiment_split = sentiment_data.replace('"', '').split("Begründung: ", 1)
                sentiment_data = {}
                sentiment_data['Sentiment'] = sentiment_split[0].split(": ")[1].replace(",", "").strip()
                sentiment_data['Begründung'] = sentiment_split[1]

            writer.writerow({
                'Datum': row['Datum'],
                'Rednerin': row['Rednerin'],
                'Partei': row['Partei'],
                'Sentiment': sentiment_data['Sentiment'].replace("Mischt", "Neutral"),
                'Begründung': sentiment_data['Begründung'].replace("}", "").strip(),
                'Rede': row['Text']
            })

    print(f"CSV wurde erfolgreich in {output_file} gespeichert.")


def main():
    sentiment_analysis()
    postprocessing()
    


if __name__ == "__main__":
    main()
