import os
import requests


"""
Die Plenarprotokolle des Deutschen Bundestages werden unter folgender Struktur gespeichert:
https://dserver.bundestag.de/btp/<WAHLPERIODE>/<WAHLPERIODE><PROTOKOLLNUMMER>.pdf

Dieses Skript lädt alle Protokolle seit der 17. Wahlperiode (ab 2009) runter.
Die Protokolle werden dabei unverändert als PDF unter "/Plenarprotokolle" gespeichert.
Sie bilden die Grundlage für die Extraktion relevanter Passagen. 

Aufgrund von Formatierungsproblemen wird das Protokoll "17_250" nicht gescraped.

Protokolle: 950
Laufzeit: 20 Min
Größe: 1.67 GB
"""


def main():
    # Wahlperioden und maximale Protokollnummer
    wahlperioden = [17, 18, 19, 20]
    max_protokolle = 500

    # Speicherpfad
    download_folder = "Plenarprotokolle"
    os.makedirs(download_folder, exist_ok=True)

    for wp in wahlperioden:
        for nr in range(1, max_protokolle + 1):
            protokoll_nummer = f"{nr:03d}"
            url = f"https://dserver.bundestag.de/btp/{wp}/{wp}{protokoll_nummer}.pdf"
            file_path = os.path.join(download_folder, f"{wp}_{protokoll_nummer}.pdf")
            if wp == 17 and protokoll_nummer == 250:
                continue

            # Überprüfen ob Datei existiert
            response = requests.head(url)
            if response.status_code == 200:
                print(f"Downloading {url}")
                pdf_data = requests.get(url).content
                with open(file_path, "wb") as pdf_file:
                    pdf_file.write(pdf_data)
            else:
                print(f"Protokoll {wp}-{protokoll_nummer} existiert nicht. Breche ab.")
                break  # Wenn eine Nummer nicht existiert, nächste Wahlperiode


if __name__ == "__main__":
    main()
