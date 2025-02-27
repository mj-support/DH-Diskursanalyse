import pdfplumber
import re
import json
import os
from datetime import datetime
import locale

"""
Dieses Skript extrahiert auf Basis der gescrapeten Plenarprotokolle werden zu jedem einzelnen Protokoll 
die Tagesordnungspunkte inkl. der Rednerinnen mitsamt der Partei. 

Auf dieser Basis kann vorab bereits gefiltert werden, welche Reden relevant sein könnten.
Zudem lässt sich mithilfe dieser Metadaten das jeweilige Protokoll gliedern, 
sodass darauf aufbauend Anfang und Ende einer Rede gefiltert und analysiert werden kann.

Resultat: metadaten.json
Laufzeit: 10 Min
Größe: 9 MB
"""

def extract_toc_and_entries(pdf_path):
    """Extrahiert Tagesordnungspunkte und alle zugehörigen Einträge aus einem zweispaltigen PDF-Dokument."""

    with pdfplumber.open(pdf_path) as pdf:
        content_text = ""
        titles = []
        for page in pdf.pages:  # Nur die ersten Seiten durchsuchen
            # Text der linken und rechten Spalte extrahieren
            full_page = page.extract_text()
            if full_page == "":
                continue
            if page.page_number == 1:
                title_split = full_page.split("I n h a l t :", 1)
                if len(title_split) == 1:
                    title_split = full_page.split("Inhalt:", 1)
                    if len(title_split) == 1:
                        title = full_page.split("Inhalt\n", 1)[0]
                    else:
                        title = title_split[0]
                else:
                    title = title_split[0]
                titles.append(title)
                jahr = title.split(" ")[-1][:-1]
                try:
                    int(jahr)
                    monat = re.sub(r"\(cid:(\d+)\)", lambda m: chr(int(m.group(1))), title.split(" ")[-2])
                    tag = title.split(" ")[-3]
                except:
                    jahrmonat = jahr.split(".")[-1]
                    tag = jahr.split(".")[-2].split("den")[-1] + "."
                    jahr = jahrmonat[-4:]
                    monat = jahrmonat.split(".")[-1][:-4]
                datum = tag + " " + monat + " "+ jahr
                locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
                datum = datetime.strptime(datum, "%d. %B %Y").strftime("%d-%m-%Y")
            else:
                title = full_page.split("\n", 1)[0]
                titles.append(title)
            left_column = page.within_bbox((0, 0, page.width / 2, page.height)).extract_text() or ""
            right_column = page.within_bbox((page.width / 2, 0, page.width, page.height)).extract_text() or ""
            content_text += left_column + "\n" + right_column + "\n"
            if full_page.split(title, 1)[1].startswith("\n(A) (C)\n"):
                break

    # Tagesordnungspunkte mit Nummern suchen (z. B. "Tagesordnungspunkt 4:")
    toc_pattern = r"(Tagesordnungspunkt ?\d+(?: \(Fortsetzung\))?:.*?)(?=(Tagesordnungspunkt ?\d+(?: \(Fortsetzung\))?:)|\Z)"
    toc_matches = re.findall(toc_pattern, content_text, re.DOTALL)
    if len(toc_matches) == 0:
        toc_pattern = r"\n(Tagesordnungspunkt"
        toc_matches_temp = content_text.split(toc_pattern, re.DOTALL)
        toc_matches = []
        for match in toc_matches_temp:
            toc_matches.append((match, ""))

    results = []
    for toc, _ in toc_matches:
        # Regulärer Ausdruck für Zeilen, die mit "... ZAHL BUCHSTABE" enden
        end_pattern = r"\.+ \d+ ?[A-Z]"

        # Text in Zeilen aufteilen
        lines = re.split(end_pattern, toc)
        #lines = toc.split('\n')

        # Liste für die Ergebnisse
        rednerin = []

        # Temporärer Speicher für den aktuellen Eintrag
        current_entry = []

        for line in lines:
            # Entferne Punkte und Leerzeichen am Ende der Zeile
            clean_line = ""
            if line.count("\n") > 2:
                line = line.split("\n")[-1]
                if ")  . ." in line or "Bundesminister" in line or line.startswith("Dr . "):
                   pass
                else:
                    continue

            for split in line.split("\n"):
                if not any(split in title for title in titles):
                    if bool(re.search(r"\d+ [A-Z]$", split)):
                        split = re.sub(r' \d+ [A-Z]$', '', split.strip())
                        split = re.sub(r"\(cid:(\d+)\)", lambda m: chr(int(m.group(1))), split)
                        rednerin.append(split)
                        continue

                    if split != "" and split[-1] == "-":
                        clean_line = split[:-1]
                    else:
                        clean_line += split + " "

            clean_line = re.sub(r'\.+ \d+ [A-Z]$', '', clean_line.strip())
            clean_line = clean_line.rstrip('. ').strip() # Punkte und Leerzeichen am Ende entfernen
            if clean_line.startswith("(") and clean_line.endswith(")"):
                continue

            if "," in clean_line or "(" in clean_line:
                clean_line = clean_line.replace("&shy", '-').replace(";\xad", "-").replace("\xad", "-")
                clean_line = re.sub(r"\(cid:(\d+)\)", lambda m: chr(int(m.group(1))), clean_line)
                current_entry.append(clean_line)
                # Den kompletten Eintrag zur Ergebnisliste hinzufügen
                rednerin.append(" ".join(current_entry).strip())  # Whitespace am Anfang/Ende entfernen

            # Den Eintragsspeicher zurücksetzen
            current_entry = []

        if len(rednerin) == 0:
            continue
        else:
            try:
                metainfos = lines[0]
                metainfos = re.sub(r'\.+ \d+ [A-Z]$', '', metainfos.strip())
                tagesordnungspunkt, thema = metainfos.split(":", 1)
            except:
                for i in range(10):
                    try:
                        metainfos = lines[i]
                        metainfos = re.sub(r'\.+ \d+ [A-Z]$', '', metainfos.strip())
                        tagesordnungspunkt, thema = metainfos.split(":", 1)
                        break
                    except:
                        pass

            if len(tagesordnungspunkt) > 50:
                tagesordnungspunkt = " " + tagesordnungspunkt.split(" ")[-1]
            thema = thema.replace("&shy", '-').replace(";\xad", "-").replace("\xad", "-")
            thema = thema.replace("-\n", "")
            thema = thema.replace("\n", " ")
            thema = re.sub(r"[ \.]+$", "", thema)
            thema = thema.replace("Drucksache", "").strip()
            thema = re.sub(r"\(cid:(\d+)\)", lambda m: chr(int(m.group(1))), thema)

            if len(tagesordnungspunkt.split(" ")) == 1:
                tagesordnungspunkt = tagesordnungspunkt.replace("punkt", "punkt ")
            tagesordnungspunkt_dict = {
                tagesordnungspunkt.split(" ")[1]: {
                    "Thema": thema,
                    "Rednerin": rednerin,
                }
            }
            results.append(tagesordnungspunkt_dict)

    json_data = {
            "Datum": datum,
            "Tagesordnungspunkte": results
    }

    return json_data


def main():
    # Ordner mit den PDF-Dateien
    pdf_folder = "Plenarprotokolle"

    # Liste für die gesammelten Ergebnisse
    all_extracted_data = {}

    # Durch alle PDFs im Ordner iterieren
    for filename in sorted(os.listdir(pdf_folder)):
        if filename.endswith(".pdf"):  # Nur PDF-Dateien verarbeiten
            pdf_path = os.path.join(pdf_folder, filename)
            print(f"Verarbeite {pdf_path}...")

            # Extrahiere die Tagesordnungspunkte mit allen Einträgen
            extracted_data = extract_toc_and_entries(pdf_path) #"Plenarprotokolle/" + "18_108.pdf"

            # Speichere die Ergebnisse unter dem Dateinamen (ohne ".pdf") als Schlüssel
            all_extracted_data[filename[:-4]] = extracted_data

    # Speichere alle extrahierten Daten in eine JSON-Datei
    output_path = "metadaten.json"
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(all_extracted_data, json_file, ensure_ascii=False, indent=4)

    print(f"Die Daten wurden erfolgreich in '{output_path}' gespeichert.")

if __name__ == "__main__":
    main()
