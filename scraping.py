import os
import requests
import pdfplumber


"""
Die Plenarprotokolle des Deutschen Bundestages werden unter folgender Struktur gespeichert:
https://dserver.bundestag.de/btp/<WAHLPERIODE>/<WAHLPERIODE><PROTOKOLLNUMMER>.pdf

Dieses Skript lädt alle Protokolle seit der 17. Wahlperiode (ab 2009) runter.
Die Protokolle werden dabei unverändert als PDF unter "/Plenarprotokolle" gespeichert.
Sie bilden die Grundlage für die Extraktion relevanter Passagen. 

Aufgrund von Formatierungsproblemen werden 17 Protokolle nicht gescraped.
Im Anschluss wird der Text aus den PDFs extrahiert und gespeichert. 
"""

def scrape_pdfs(pdf_folder):
    # Wahlperioden und maximale Protokollnummer
    wahlperioden = [17, 18, 19, 20]
    max_protokolle = 500

    # Speicherpfad

    os.makedirs(pdf_folder, exist_ok=True)

    for wp in wahlperioden:
        for nr in range(1, max_protokolle + 1):
            protokoll_nummer = f"{nr:03d}"
            url = f"https://dserver.bundestag.de/btp/{wp}/{wp}{protokoll_nummer}.pdf"
            file_path = os.path.join(pdf_folder, f"{wp}_{protokoll_nummer}.pdf")
            if (wp == 17 and protokoll_nummer == 250) or (wp == 19 and protokoll_nummer == 114) or (wp == 20 and protokoll_nummer == 17) or (wp == 17 and protokoll_nummer == 208) or (wp == 18 and protokoll_nummer == 24) or (wp == 18 and protokoll_nummer == 30) or (wp == 18 and protokoll_nummer == 42) or (wp == 18 and protokoll_nummer == 99) or (wp == 18 and protokoll_nummer == 175) or (wp == 18 and protokoll_nummer==240) or (wp == 18 and protokoll_nummer == 242) or (wp == 18 and protokoll_nummer == 29) or (wp == 18 and protokoll_nummer == 59) or (wp == 18 and protokoll_nummer == 175) or (wp == 19 and protokoll_nummer == 22) or (wp == 19 and protokoll_nummer == 65) or (wp == 19 and protokoll_nummer == 65):
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


def extract_text_from_pdf(pdf_folder, txt_folder):
    os.makedirs(txt_folder, exist_ok=True)

    for filename in sorted(os.listdir(pdf_folder)):
        if filename.endswith(".pdf"):  # Nur PDF-Dateien verarbeiten
            pdf_path = os.path.join(pdf_folder, filename)
            print(f"Extrahiere {pdf_path}...")

            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                inhalt_patterns = ["\nInhalt:\n", "\nI n h a l t :\n", "\nInhalt\n"]

                for page in pdf.pages:
                    left_box = (0, 0, page.width / 2, page.height)
                    right_box = (page.width / 2, 0, page.width, page.height)

                    if page.page_number == 1:
                        full_page = page.extract_text()
                        for inhalt in inhalt_patterns:
                            if inhalt in full_page:
                                full_page = full_page.split(inhalt, 1)[0]
                                left_split = inhalt.split("h", 1)[0] + "h\n"
                                right_split = inhalt.split("a", 1)[1].strip() + "\n"
                                break

                        try:
                            left_column = page.within_bbox(left_box).extract_text().split(left_split)[1] or ""
                        except:
                            left_split = left_split[:-2] + "\n"
                            left_column = page.within_bbox(left_box).extract_text().split(left_split)[1] or ""
                        right_column = page.within_bbox(right_box).extract_text().split(right_split)[1] or ""
                        text += full_page + "\n" + left_column + "\n" + right_column + "\n"
                    else:
                        try:
                            left_column = page.within_bbox(left_box).extract_text()
                            if left_column.startswith("Anlagen\nDeutscher Bundestag"):
                                break

                            left_column = left_column.split("\n", 1)[1] or ""
                            right_column = page.within_bbox(right_box).extract_text().split("\n", 1)[1] or ""

                            if left_column.startswith("(A)\nAnlage"):
                                break

                            text += left_column + "\n" + right_column + "\n"
                        except:
                            # Leere Seite
                            continue

            with open(f"{txt_folder}/{filename[:-4]}.txt", "w", encoding="utf-8") as file:
                file.write(text)


def main():
    pdf_folder = "Plenarprotokolle/pdf"
    txt_folder = "Plenarprotokolle/txt"

    scrape_pdfs(pdf_folder)
    extract_text_from_pdf(pdf_folder, txt_folder)


if __name__ == "__main__":
    main()
