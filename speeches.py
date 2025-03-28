import os
import json
import re
import pandas as pd


"""
In diesem Skript werden die einzelnen Reden der Bundestagsabgeordneten basierend auf der Agenda extrahiert.
Im Anschluss werden die relevanten Reden über Geflüchtete gefiltert.
"""

präsidenten = ['Präsident Dr. Norbert Lammert',
               "Alterspräsident Dr. Heinz Riesenhuber",
               "Alterspräsident Dr. Hermann Otto Solms",
               "Präsidentin Bärbel Bas",
               "Präsident Dr. Wolfgang Schäuble",
               "Alterspräsident Dr. Wolfgang Schäuble",
               "Vizepräsident Dr. h. c. Wolfgang Thierse",
               "Vizepräsidentin Gerda Hasselfeldt",
               "Vizepräsidentin Petra Pau",
               "Vizepräsidentin Katrin Göring-Eckardt",
               "Vizepräsident Dr. Hermann Otto Solms",
               "Vizepräsident Eduard Oswald",
               "Vizepräsidentin Edelgard Bulmahn"
               "Vizepräsident Peter Hintze",
               "Vizepräsidentin Claudia Roth",
               "Vizepräsidentin Ulla Schmidt",
               "Vizepräsident Johannes Singhammer",
               "Vizepräsidentin Edelgard Bulmahn",
               "Vizepräsident Johannes Singhammer",
               "Vizepräsidentin Dr. h. c. Edelgard Bulmahn",
               "Vizepräsident Wolfgang Kubicki",
               "Vizepräsident Dr. Hans-Peter Friedrich",
               "Vizepräsident Thomas Oppermann",
               "Vizepräsidentin Dagmar Ziegler",
               "Vizepräsidentin Yvonne Magwas",
               "Vizepräsidentin Katrin Göring-Eckardt",
               "Vizepräsidentin Aydan Özoğuz"]


def remove_brackets(text):
    text_split = text.split("(")
    clean_text = text_split[0]
    for split in text_split[1:]:
        clean_text_split = split.split(")", 1)
        try:
            clean_text += clean_text_split[1]
        except:
            continue
    clean_text = clean_text.replace("\n\n", "")

    return clean_text


def replace_multiple(inhalt):
    inhalt = re.sub(r"-\n(?=[a-z])", "", inhalt)
    inhalt = inhalt.replace("­ ", "").replace("­", "-").replace(" ,", ",")
    inhalt = inhalt.replace(" .", ".")
    inhalt = inhalt.replace("DIE GRÜ-\nNEN", "DIE GRÜNEN").replace("BÜND-\nNIS 90", "BÜNDNIS 90")
    inhalt = inhalt.replace("DIE LIN-\nKE", "DIE LINKE").replace("BÜNDNIS90", "BÜNDNIS 90")
    inhalt = inhalt.replace("\n", " ").replace("/ ", "/").replace("  ", " ").replace("- ", "-")
    inhalt = inhalt.replace("GRÜ-NEN", "GRÜNEN").replace("(CSU)", "(CDU/CSU)").replace("CSU/CSU", "CDU/CSU")
    inhalt = inhalt.replace("beim Bundesminister ", "beim Bundesministerium " )
    inhalt = inhalt.replace("bei der Bundesministerin ", "beim Bundesministerium ")
    inhalt = inhalt.replace("Staatsminister ", "Staatsministerium ")
    inhalt = inhalt.replace("Staatsministerin ", "Staatsministerium ")
    inhalt = inhalt.replace("Dr. Kirsten Tackmann (DIE LINKE)", "Dr. Kirsten Tackmann (DIE LINKE):")
    inhalt = inhalt.replace("::", ":").replace("Fami-lie", "Familie")
    inhalt = inhalt.replace("Bundesministerin ", "Bundesministerium ")
    inhalt = inhalt.replace("Bundesminister ", "Bundesministerium ")
    inhalt = inhalt.replace("beim Bundeskanzler:", "im Bundeskanzleramt:")
    inhalt = inhalt.replace("bei der Bundeskanzlerin:", "im Bundeskanzleramt:")
    inhalt = inhalt.replace("Bundeskanzlerin:", "Bundeskanzleramt:")
    inhalt = inhalt.replace("Bundeskanzler:", "Bundeskanzleramt:")
    inhalt = inhalt.replace('Dr. Angela Merkel (CDU/CSU)', 'Dr. Angela Merkel, Bundeskanzleramt')
    inhalt = inhalt.replace("BK ", "im Bundeskanzleramt")
    inhalt = inhalt.replace("bei der Bundes-kanzlerin", "im Bundeskanzleramt")
    inhalt = inhalt.replace("Bundesmi-nisterin ", "Bundesministerium ")
    inhalt = inhalt.replace("Bundesmi-nister ", "Bundesministerium ")
    inhalt = inhalt.replace("Finan-zen", "Finanzen")
    inhalt = inhalt.replace("Petra Hinz (Herborn)", "Priska Hinz (Herborn)")
    inhalt = inhalt.replace("Bundes-ministerin ", "Bundesministerium ")
    inhalt = inhalt.replace("Bundes-minister ", "Bundesministerium ")
    inhalt = inhalt.replace("In-nern", "Innern")
    inhalt = inhalt.replace("Bun-desminister ", "Bundesministerium ")
    inhalt = inhalt.replace(")(", ") (")
    inhalt = inhalt.replace("Aus-wärtigen", "Auswärtigen")
    inhalt = inhalt.replace("Ver-teidigung", "Verteidigung")
    inhalt = inhalt.replace("Dr. Christen Happach-Kasan (FDP)", 'Dr. Christel Happach-Kasan (FDP)')
    inhalt = inhalt.replace("Natur-schutz", "Naturschutz")
    inhalt = inhalt.replace("Omid Nouripour (BÜNDNIS 90/DIE GRÜNEN) ", "Omid Nouripour (BÜNDNIS 90/DIE GRÜNEN):")
    inhalt = inhalt.replace("/ ", "/")
    inhalt = inhalt.replace("Dr. Thomas de Maizière (CDU/CSU)", "Dr. Thomas de Maizière, Bundesministerium des Innern")
    inhalt = inhalt.replace("Christian Lange, Parl. Staatssekretär beim Bundesministerium der Justiz und Verbraucherschutz", "Christian Lange, Parl. Staatssekretär beim Bundesministerium der Justiz und für Verbraucherschutz")
    inhalt = inhalt.replace("Dr. Alexander S Neu (DIE LINKE)", "Dr. Alexander S. Neu (DIE LINKE)")
    inhalt = inhalt.replace(" G ", ' G. ')
    inhalt = inhalt.replace(' E ', ' E. ')
    inhalt = inhalt.replace(' Parl ', ' Parl. ')
    inhalt = inhalt.replace("Parl. Staatssekretär der", 'Parl. Staatssekretär beim Bundesministerium der')
    inhalt = inhalt.replace('Nadine Schön (St Wendel) (CDU/CSU)', 'Nadine Schön (St. Wendel) (CDU/CSU)')
    inhalt = inhalt.replace("bei der Bundeskanzlerin", "im Bundeskanleramt")
    inhalt = inhalt.replace(' M ', ' M. ')
    inhalt = inhalt.replace(' h c ', ' h. c. ')
    inhalt = inhalt.replace('Um-welt', 'Umwelt')
    inhalt = inhalt.replace('bei der Bundesministerium ', 'beim Bundesministerium ')
    inhalt = inhalt.replace("Na-turschutz", "Naturschutz")
    inhalt = inhalt.replace("(Bündnis 90/Die Grünen)", '(BÜNDNIS 90/DIE GRÜNEN)')
    inhalt = inhalt.replace("Auswärti-gen", 'Auswärtigen')
    inhalt = inhalt.replace("Se-nioren", 'Senioren')
    inhalt = inhalt.replace("beim Bundes-kanzler", "im Bundeskanzleramt")
    inhalt = inhalt.replace("Hubertus Heil (Peine) (SPD)", "Hubertus Heil, Bundesministerium für Arbeit und Soziales")
    inhalt = inhalt.replace("Sozia-les", "Soziales")
    inhalt = inhalt.replace("Vertei-digung", "Verteidigung")
    inhalt = inhalt.replace("Stadt-entwicklung", "Stadtentwicklung")
    inhalt = inhalt.replace("wirtschaftli-che", "wirtschaftliche")
    inhalt = inhalt.replace("Bil-dung", "Bildung")
    inhalt = inhalt.replace("Auswär-tigen", "Auswärtigen")
    inhalt = inhalt.replace("Parl. Staatssekretär bei der Bun-desministerin des Innern und für Heimat", 'Johann Saathoff, Parl. Staatssekretär beim Bundesministerium des Innern')
    return inhalt


def get_reden_start(inhalt, rednerin, letzte_rede):
    try:
        reden_start = inhalt.split(rednerin + ":", 1)[1]
    except:
        try:
            rednerin = remove_abbreviations(rednerin)
            reden_start = inhalt.split(rednerin + ":", 1)[1]
        except:
            try:
                reden_start = inhalt.split(rednerin, 1)[1]
            except:
                if rednerin == 'Petra Hinz (Essen) (SPD)':
                    rednerin = "Priska Hinz (Herborn) (BÜNDNIS 90/DIE GRÜNEN)"
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Michael Schlecht (DIE LINKE)':
                    rednerin_temp = "Dr. Ilja Seifert :"
                    reden_start = letzte_rede.split(rednerin_temp, 1)[1]
                elif rednerin == 'Kerstin Andreae (BÜNDNIS 90/DIE GRÜNEN)':
                    rednerin_temp = "Kerstin Andreae :"
                    reden_start = letzte_rede.split(rednerin_temp, 1)[1]
                elif rednerin == 'Marcus Weinberg (Hamburg) (CDU/CSU)':
                    rednerin = "Harald Weinberg (DIE LINKE)"
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Arfst Wagner (Schleswig) (BÜNDNIS 90/DIE GRÜNEN)':
                    rednerin_temp = "Daniela Wagner :"
                    reden_start = letzte_rede.split(rednerin_temp, 1)[1]
                    rednerin = "Daniela Wagner (BÜNDNIS 90/DIE GRÜNEN)"
                elif rednerin == 'Siegfried Kauder (Villingen-Schwenningen) (CDU/CSU)':
                    rednerin = "Volker Kauder (CDU/CSU)"
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Bernd Neumann, Staatsministerium im Bundeskanzleramt':
                    rednerin = "Eckart von Klaeden, Staatsministerium im Bundeskanzleramt"
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == "Paul Schäfer (Köln) (CDU/CSU)":
                    rednerin = "Paul Schäfer (Köln) (DIE LINKE)"
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == "Dr. Martin Pätzold (CDU/CSU)":
                    rednerin = "Harald Petzold (Havelland) (DIE LINKE)"
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Caren Marks (SPD)':
                    rednerin = "Caren Marks, Parl. Staatssekretärin beim Bundesministerium für Familie, Senioren, Frauen und Jugend"
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == "Dr. Maria Flachsbarth, Parl. Staatssekretärin beim Bundesministerium für Umwelt, Naturschutz, Bau und Reaktorsicherheit":
                    rednerin = "Dr. Maria Flachsbarth, Parl. Staatssekretärin beim Bundesministerium für Ernährung und Landwirtschaft"
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Hans-Joachim Fuchtel (CDU/CSU)':
                    rednerin = "Hans-Joachim Fuchtel, Parl. Staatssekretär beim Bundesministerium für wirtschaftliche Zusammenarbeit und Entwicklung"
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Sigmar Gabriel, Bundesministerium für Wirtschaft und Energie':
                    rednerin_temp = "Sigmar Gabriel (SPD)"
                    reden_start = inhalt.split(rednerin_temp, 1)[1]
                elif rednerin == 'Katharina Dröge (BÜNDNIS 90/DIE GRÜNEN)':
                    reden_start = letzte_rede
                elif rednerin == "Norbert Barthle (CDU/CSU)":
                    rednerin = "Norbert Barthle, Parl. Staatssekretär beim Bundesministerium für Verkehr und digitale Infrastruktur"
                    reden_start = letzte_rede.split(rednerin, 1)[1]
                elif rednerin == "Dr. Thomas de Maizière (CDU/CSU)":
                    rednerin = "Dr. Thomas de Maizière, Bundesministerium des Innern"
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Dr. DanyalBayaz (BÜNDNIS 90/DIE GRÜNEN)':
                    rednerin = 'Dr. Danyal Bayaz (BÜNDNIS 90/DIE GRÜNEN)'
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Dr. h. c. (UnivKyiv) Hans Michelbach (CDU/CSU)':
                    rednerin = 'Dr. h. c. (Univ Kyiv) Hans Michelbach (CDU/CSU)'
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'TimonGremmels (SPD)':
                    rednerin = 'Timon Gremmels (SPD)'
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Sevim Dagğdelen (DIE LINKE)':
                    rednerin = 'Sevim Dağdelen (DIE LINKE)'
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Dr. Christian Jung (FDP)':
                    rednerin = 'Ingmar Jung (CDU/CSU)'
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Michael Georg Link (Heilbronn) (FDP)':
                    rednerin = 'Michael Georg Link (FDP)'
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Ana-Maria Trӑsnea (SPD)':
                    rednerin = 'Ana-Maria Trăsnea (SPD)'
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Lisa Paus (BÜNDNIS 90/DIE GRÜNEN)':
                    rednerin = "Lisa Paus, Bundesministerium für Familie, Senioren, Frauen und Jugend"
                    reden_start = letzte_rede.split(rednerin, 1)[1]
                elif rednerin == 'Benjamin Strasser (FDP)':
                    rednerin = 'Benjamin Strasser, Parl. Staatssekretär beim Bundesministerium der Justiz'
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Sevim Dagdelen (BSW)':
                    rednerin = 'Sevim Dağdelen (BSW)'
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Dr. Angela Merkel (CDU/CSU)':
                    rednerin = 'Dr. Angela Merkel, Bundeskanzleramt'
                    reden_start = inhalt.split(rednerin, 1)[1]
                elif rednerin == 'Hubertus Heil (Peine) (SPD)':
                    rednerin = 'Hubertus Heil, Bundesministerium für Arbeit und Soziales'
                    reden_start = inhalt.split(rednerin, 1)[1]



    return reden_start, rednerin


def get_nächste_rede(reden_start, rednerin):
    if rednerin is not None:
        rednerin_pos = reden_start.find(rednerin + ":")
        if rednerin_pos == -1:
            try:
                rednerin = remove_abbreviations(rednerin)
                rednerin_pos = reden_start.find(rednerin + ":")
            except:
                rednerin_pos = reden_start.find(rednerin)
    else:
        rednerin_pos = -1
    return rednerin_pos


def get_nächste_rednerin(punkt_index, sitzung, step):
    if punkt_index != len(list(sitzung)) - step:
        try:
            nächste_rednerin = sitzung[list(sitzung)[punkt_index + step]]["Reden"][0]
        except:
            nächste_rednerin = get_nächste_rednerin(punkt_index, sitzung, step + 1)
    else:
        nächste_rednerin = None
    return nächste_rednerin


def get_partei(rednerin_split):
    parteizugehörigkeit = {
        "Dr. Angela Merkel": "CDU/CSU",
        "Dr. Guido Westerwelle": "FDP",
        "Dr. Thomas de Maizière": "CDU/CSU",
        "Sabine Leutheusser-Schnarrenberger": "FDP",
        "Dr. Wolfgang Schäuble": "CDU/CSU",
        "Rainer Brüderle": "FDP",
        "Dr. Franz Josef Jung": "CDU/CSU",
        "Ilse Aigner": "CDU/CSU",
        "Dr. Karl-Theodor Freiherr zu Guttenberg": "CDU/CSU",
        "Dr. Ursula von der Leyen": "CDU/CSU",
        "Dr. Philipp Rösler": "FDP",
        "Dr. Peter Ramsauer": "CDU/CSU",
        "Dr. Norbert Röttgen": "CDU/CSU",
        "Dr. Annette Schavan": "CDU/CSU",
        "Dirk Niebel": "FDP",
        "Ronald Pofalla": "CDU/CSU",
        "Bernd Neumann": "CDU/CSU",
        "Eckart von Klaeden": "CDU/CSU",
        "Dr. Ole Schröder": "CDU/CSU",
        "Cornelia Pieper": "FDP",
        "Dr. Max Stadler": "FDP",
        "Hartmut Koschyk": "CDU/CSU",
        "Hans-Joachim Fuchtel": "CDU/CSU",
        "Dr. Kristina Köhler": "CDU/CSU",
        "Dr. Werner Hoyer": "FDP",
        "Christian Schmidt": "CDU/CSU",
        "Dr. Hermann Kues": "CDU/CSU",
        "Daniel Bahr": "FDP",
        "Dr. Andreas Scheuer": "CDU/CSU",
        "Jan Mücke": "FDP",
        "Enak Ferlemann": "CDU/CSU",
        "Ursula Heinen-Esser": "CDU/CSU",
        "Hans-Joachim Otto": "FDP",
        "Dr. Helge Braun": "CDU/CSU",
        "Dr. Ralf Brauksiepe": "CDU/CSU",
        "Dr. Gerd Müller": "CDU/CSU",
        "Thomas Kossendey": "CDU/CSU",
        "Peter Hintze": "CDU/CSU",
        "Steffen Kampeter": "CDU/CSU",
        "Annette Widmann-Mauz": "CDU/CSU",
        "Katherina Reiche": "CDU/CSU",
        "Thomas Rachel": "CDU/CSU",
        "Maria Böhmer": "CDU/CSU",
        "Dr. Christoph Bergner": "CDU/CSU",
        "Dr. Kristina Schröder": "CDU/CSU",
        "Gudrun Kopp": "FDP",
        "Ernst Burgbacher": "FDP",
        "Julia Klöckner": "CDU/CSU",
        "Dr. Maria Böhmer": "CDU/CSU",
        "Karl-Theodor Freiherr zu Guttenberg": "CDU/CSU",
        "Dr. Hans-Peter Friedrich": "CDU/CSU",
        "Peter Bleser": "CDU/CSU",
        "Ulrike Flach": "FDP",
        "Michael Link": "FDP",
        "Peter Altmaier": "CDU/CSU",
        "Dr. Johanna Wanka": "CDU/CSU",
        "Sigmar Gabriel": "SPD",
        "Dr. Frank-Walter Steinmeier": "SPD",
        "Heiko Maas": "SPD",
        "Andrea Nahles": "SPD",
        "Manuela Schwesig": "SPD",
        "Hermann Gröhe": "CDU/CSU",
        "Alexander Dobrindt": "CDU/CSU",
        "Dr. Barbara Hendricks": "SPD",
        "Gabriele Lösekrug-Möller": "SPD",
        "Dr. Günter Krings": "CDU/CSU",
        "Michael Roth": "SPD",
        "Dr. Maria Flachsbarth": "CDU/CSU",
        "Uwe Beckmeyer": "SPD",
        "Christian Lange": "SPD",
        "Florian Pronold": "SPD",
        "Rita Schwarzelühr-Sutter": "SPD",
        "Brigitte Zypries": "SPD",
        "Caren Marks": "SPD",
        "Stefan Müller": "CDU/CSU",
        "Anette Kramme": "SPD",
        "Iris Gleicke": "SPD",
        "Aydan Özoğuz": "SPD",
        "Dorothee Bär": "CDU/CSU",
        "Monika Grütters": "CDU/CSU",
        "Thomas Silberhorn": "CDU/CSU",
        "Johanna Wanka": "CDU/CSU",
        "Elke Ferner": "SPD",
        "Dr. Michael Meister": "CDU/CSU",
        "Ingrid Fischbach": "CDU/CSU",
        "Ulrich Kelber": "SPD",
        "Thomas de Maizière": "CDU/CSU",
        "Norbert Barthle": "CDU/CSU",
        "Jens Spahn": "CDU/CSU",
        "Markus Grübel": "CDU/CSU",
        "Dr. Katarina Barley": "SPD",
        "Olaf Scholz": "SPD",
        "Horst Seehofer": "CDU/CSU",
        "Hubertus Heil": "SPD",
        "Dr. Franziska Giffey": "SPD",
        "Andreas Scheuer": "CDU/CSU",
        "Svenja Schulze": "SPD",
        "Anja Karliczek": "CDU/CSU",
        "Niels Annen": "SPD",
        "Dr. Peter Tauber": "CDU/CSU",
        "Steffen Bilger": "CDU/CSU",
        "Christine Lambrecht": "SPD",
        "Marco Wanderwitz": "CDU/CSU",
        "Stephan Mayer": "CDU/CSU",
        "Sabine Weiss": "CDU/CSU",
        "Dr. Hendrik Hoppenstedt": "CDU/CSU",
        "Dr. Thomas Gebhart": "CDU/CSU",
        "Kerstin Griese": "SPD",
        "Michael Stübgen": "CDU/CSU",
        "Thomas Bareiß": "CDU/CSU",
        "Rita Hagl-Kehl": "SPD",
        "Christian Hirte": "CDU/CSU",
        "Oliver Wittke": "CDU/CSU",
        "Stefan Zierke": "SPD",
        "Bettina Hagedorn": "SPD",
        "Michelle Müntefering": "SPD",
        "Annegret Kramp-Karrenbauer": "CDU/CSU",
        "Sarah Ryglewski": "SPD",
        "Volkmar Vogel": "CDU/CSU",
        "Elisabeth Winkelmeier-Becker": "CDU/CSU",
        "Franziska Giffey": "SPD",
        "Angela Merkel": "CDU/CSU",
        'Dr. Robert Habeck': "BÜNDNIS 90/DIE GRÜNEN",
        'Christian Lindner': "FDP",
        'Nancy Faeser': "SPD",
        "Annalena Baerbock": "BÜNDNIS 90/DIE GRÜNEN",
        "Dr. Marco Buschmann": "FDP",
        'Cem Özdemir': "BÜNDNIS 90/DIE GRÜNEN",
        'Anne Spiegel': "BÜNDNIS 90/DIE GRÜNEN",
        'Dr. Karl Lauterbach': "SPD",
        'Dr. Volker Wissing': "FDP",
        'Steffi Lemke': "BÜNDNIS 90/DIE GRÜNEN",
        'Bettina Stark-Watzinger': "FDP",
        "Klara Geywitz": "SPD",
        "Wolfgang Schmidt": "SPD",
        'Carsten Schneider': "SPD",
        "Reem Alabali-Radovan": "SPD",
        'Dr. Anna Lührmann': "BÜNDNIS 90/DIE GRÜNEN",
        "Michael Kellner": "BÜNDNIS 90/DIE GRÜNEN",
        'Oliver Luksic': "FDP",
        "Dr. Franziska Brantner": "BÜNDNIS 90/DIE GRÜNEN",
        'Claudia Roth': "BÜNDNIS 90/DIE GRÜNEN",
        'Ekin Deligöz': "BÜNDNIS 90/DIE GRÜNEN",
        'Sven Lehmann': "BÜNDNIS 90/DIE GRÜNEN",
        'Lisa Paus': "BÜNDNIS 90/DIE GRÜNEN",
        'Oliver Krischer': "BÜNDNIS 90/DIE GRÜNEN",
        'Katja Keul': "BÜNDNIS 90/DIE GRÜNEN",
        'Katja Hessel': "FDP",
        'Dr. Florian Toncar': "FDP",
        "Dr. Tobias Lindner": "BÜNDNIS 90/DIE GRÜNEN",
        'Thomas Hitschler': "SPD",
        "Mario Brandenburg": "FDP",
        "Cansel Kiziltepe": "SPD",
        "Dr. Bettina Hoffmann": "BÜNDNIS 90/DIE GRÜNEN",
        "Christian Kühn": "BÜNDNIS 90/DIE GRÜNEN",
        "Benjamin Strasser": "FDP",
        "Daniela Kluckert": "FDP",
        "Mahmut Özdemir": "SPD",
        "Dr. Jens Brandenburg": "FDP",
        "Boris Pistorius": "SPD",
        'Siemtje Möller': "SPD",
        'Dr. Ophelia Nick': "BÜNDNIS 90/DIE GRÜNEN",
        'Claudia Müller': "BÜNDNIS 90/DIE GRÜNEN",
        "Sören Bartol": "SPD",
        "Johann Saathoff": "SPD",
        "Michael Theurer": "FDP",
        "Sabine Dittmar": "SPD",
        'Dr. Bärbel Kofler': "SPD",
        'Dr. Edgar Franke': "SPD",
        "Elisabeth Kaiser": "SPD",
        "Dr. Jan-Niclas Gesenhues": "BÜNDNIS 90/DIE GRÜNEN",
        'Dr. Jörg Kukies': "SPD",
    }
    try:
        partei = rednerin_split[1][:-1]
        if "(" in partei:
            partei = partei.split("(")[1]
    except:
        name = rednerin_split[0].split(",", 1)[0]
        partei = parteizugehörigkeit[name]
    return partei


def remove_abbreviations(rednerin):
    posten_dict = {
        "AA": "des Auswärtigen",
        "Enak Ferlemann (CDU/CSU)": "Enak Ferlemann, Parl. Staatssekretär beim Bundesministerium für Verkehr, Bau und Stadtentwicklung",
        "Erwin Josef Rüddel (CDU/CSU)": "Erwin Rüddel (CDU/CSU)",
        "Dr. Guido Westerwelle (FDP)": "Dr. Guido Westerwelle (FDP) (spricht von seinem Platz aus)",
        "Staatsministerium AA": "Staatsministerium im Auswärtigen Amt",
        "Dr. Wolfgang Schäuble (CDU/CSU)": "Dr. Wolfgang Schäuble, Bundesministerium der Finanzen",
        "Christian Lindner (FDP)": "Dr. Martin Lindner (Berlin) (FDP)",
        "Andreas G. Lämmel (CDU/CSU)": "Andreas Lämmel (CDU/CSU)",
        "Thomas Kossendey (CDU/CSU)": 'Thomas Kossendey, Parl. Staatssekretär beim Bundesministerium der Verteidigung',
        "im AA": "im Auswärtigen Amt"
    }
    posten_split = rednerin.split(", ")
    try:
        bereich = posten_split[1].split(" ")
    except:
        rednerin = posten_dict[posten_split[0]]
        return rednerin

    posten = posten_dict[bereich[1]]
    rednerin = posten_split[0] + ", " + bereich[0] + " " + posten
    return rednerin


def extract_relevant_speeches():
    # Lade die JSON-Datei
    with open("Plenarprotokolle/reden/merged.json", "r", encoding="utf-8") as f:
        daten = json.load(f)

    df = pd.DataFrame(daten)

    suchbegriffe = ["Geflüchtete", "Flüchtling", "Refugee", "Asyl"]

    suchbegriffe_ukraine = ["ukrainisch", "Ukraine"]
    suchbegriffe_other = [
        "syrisch", "Syrien", "Syrer", "afghanisch", "Afghanistan", "Afghane", "Afghanin", "Afghanen", "Iran", "Irak"
    ]


    pattern = '|'.join(suchbegriffe)
    mask = df['Rede'].str.contains(pattern, case=False, na=False)
    gefilterte_reden = df[mask]
    gefilterte_reden.to_json("Plenarprotokolle/reden/gefilterte_reden.json", orient="records", force_ascii=False, indent=4)
    print(f"Es wurden {len(gefilterte_reden)} relevante Reden gefunden.")

    pattern = '|'.join(suchbegriffe_ukraine)
    mask = gefilterte_reden['Rede'].str.contains(pattern, case=False, na=False)
    gefilterte_reden_ukraine = gefilterte_reden[mask]
    gefilterte_reden_ukraine.to_json("Plenarprotokolle/reden/gefilterte_reden_ukraine.json", orient="records", force_ascii=False, indent=4)
    print(f"Es wurden {len(gefilterte_reden_ukraine)} relevante Reden gefunden.")

    pattern = '|'.join(suchbegriffe_other)
    mask = gefilterte_reden['Rede'].str.contains(pattern, case=False, na=False)
    gefilterte_reden_other = gefilterte_reden[mask]
    gefilterte_reden_other.to_json("Plenarprotokolle/reden/gefilterte_reden_other.json", orient="records", force_ascii=False, indent=4)
    print(f"Es wurden {len(gefilterte_reden_other)} relevante Reden gefunden.")


def main():
    agenda = "Plenarprotokolle/agenda.json"
    reden_folder = "Plenarprotokolle/reden/"
    os.makedirs(reden_folder, exist_ok=True)

    with open(agenda, "r", encoding="utf-8") as f:
        json_file = json.load(f)

    json_reden = []
    reden_count = 0
    for dateiname in list(json_file.keys())[:]:
        print(f"Verarbeite: {dateiname}")
        dateipfad = os.path.join("Plenarprotokolle", "preprocessed", dateiname + ".txt")
        sitzung = json_file[dateiname]["Agenda"]

        with open(dateipfad, "r", encoding="utf-8") as datei:
            inhalt = datei.read()
            inhalt = inhalt.split("---BEGINN DER SITZUNG", 1)[1].split("\n\n", 1)[1]
            inhalt = replace_multiple(inhalt)

            for punkt_index, punkt in enumerate(sitzung):
                if "Fragestunde" in punkt:
                    if len(sitzung[punkt]["Reden"]) > 0:
                        antwort = sitzung[punkt]["Reden"][0]
                else:
                    antwort = None

                reden = sitzung[punkt]["Reden"]
                for rede_index, rednerin in enumerate(reden):
                    if len(json_reden) == 0:
                        letzte_rede = ""
                    else:
                        letzte_rede = json_reden[-1]["Rede"]
                    reden_start, rednerin = get_reden_start(inhalt, rednerin, letzte_rede)

                    if rede_index != len(reden) - 1:
                        nächste_rednerin = reden[rede_index + 1]
                    else:
                        nächste_rednerin = get_nächste_rednerin(punkt_index, sitzung, 1)

                    nächste_rede = get_nächste_rede(reden_start, nächste_rednerin)
                    nächste_antwort = get_nächste_rede(reden_start, antwort)
                    nächste_präsidentin = min((reden_start.find(präsident) for präsident in präsidenten if präsident in reden_start), default=-1)
                    nächste_list = [v for v in [nächste_rede, nächste_antwort, nächste_präsidentin] if v != -1]
                    reden_end = min(nächste_list) if nächste_list else -1
                    if reden_end == nächste_antwort and nächste_antwort != nächste_rede:
                        reden.insert(rede_index + 1, antwort)


                    rede = reden_start[:reden_end] if reden_end != -1 else reden_start
                    try:
                        inhalt = inhalt.split(rede, 1)[1]
                    except:
                        x = 2
                    rede = remove_brackets(rede)
                    rednerin_split = rednerin.split("(", 1)
                    rednerin = rednerin_split[0].strip()
                    partei = get_partei(rednerin_split)
                    reden_dict = {
                        "Plenarprotokoll": dateiname,
                        "Datum": json_file[dateiname]["Datum"],
                        "Rednerin": rednerin,
                        "Partei": partei,
                        "Tagesordnungspunkt": punkt,
                        "Thema": sitzung[punkt]["Thema"],
                        "Rede": rede.strip(),
                    }

                    json_reden.append(reden_dict)
                    reden_count += 1

    with open(reden_folder + "reden.json", "w", encoding="utf-8") as f:
        json.dump(json_reden, f, indent=4, ensure_ascii=False)
    print(reden_count)

    extract_relevant_speeches()


if __name__ == "__main__":
    main()
