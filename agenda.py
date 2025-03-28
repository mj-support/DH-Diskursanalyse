import os
import re
import json
import locale
from datetime import datetime

"""
Diese Skript führt eine Normalisierung durch.
Dafür werden Absätze, Leerzeichen, Bindestriche, Sonderzeichen und Abkürzungen vereinheitlicht.
Zudem wird die Agenda extrahiert und in einer JSON-Datei gespeichert. 
"""

reden_count = 0

def add_bookmarks(text):
    first_split = text.split("Berlin, ", 1)
    second_split = first_split[1].split("\n", 1)
    text = first_split[0] + second_split[0] + "\n\n----------TAGESORDNUNGSPUNKTE!!--------------\n\n" + second_split[1]

    try:
        third_split = text.split("\n(A)\n", 1)
        forth_split = third_split[1].split("\nBegin", 1)
    except:
        third_split = text.split("\n203. S\n", 1)
        forth_split = third_split[1].split("\nBegin", 1)

    content = remove_drucksachen(third_split[0])
    text = content + "\n\n----------BEGINN DER SITZUNG!!-----------\n\n" + forth_split[1].split("\n", 1)[1]

    try:
        fifth_split = text.split("\n(C)\n", 1)
        sixth_split = fifth_split[1].split(" Uhr\n", 1)
        text = fifth_split[0] + "\n" + sixth_split[1]
    except:
        try:
            fifth_split = text.split("\n(C)\n", 1)
            sixth_split = fifth_split[1].split(":00\n", 1)
        except:
            fifth_split = text.split("\ntzung\n", 1)
            sixth_split = fifth_split[1].split(".00 Uhr\n", 1)
        text = fifth_split[0] + "\n" + sixth_split[1]
    return text


def remove_drucksachen(text):
    content_list = text.split("\nDrucksache")
    content = content_list[0]
    for c in content_list[1:]:
        content_split = c.split("\n", 1)
        if content_split[0].startswith("n "):
            content += "\n" + content_split[1]
        else:
            if any(char.isalpha() for char in content_split[0]):
                content += "\n" + content_split[0] + "\n" + content_split[1]
            else:
                try:
                    content += "\n" + content_split[1]
                except:
                    continue

    content_list = content.split("(Drucksache")
    content = content_list[0]
    for c in content_list[1:]:
        content_split = c.split(")", 1)
        content += content_split[1]
        x = 2

    return content


def replace_unicode(text):
    """Ersetzt (cid:xxx) Muster durch entsprechende Unicode-Zeichen."""
    text = re.sub(r"\(cid:(\d+)\)", lambda m: chr(int(m.group(1))), text)
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = text.replace("DIE GRÜ-\nNEN", "DIE GRÜNEN")
    text = text.replace("BÜND-\nNIS 90", "BÜNDNIS 90")
    text = text.replace("DIE LIN-\nKE", "DIE LINKE")

    text = text.replace("(A)", "").replace("(B)", "").replace("(C)", "").replace("(D)", "")
    text = text.replace(".", ". ")
    text = text.replace("  ", " ")
    text = text.replace(" \n", "\n")
    return text


def get_metadata(text, regierung):
    datum = get_datum(text)
    tagesordnungspunkte = get_agenda(text, regierung)

    json_data = {
            "Datum": datum,
            "Agenda": tagesordnungspunkte,
    }
    return json_data


def get_datum(text):
    headline = text.split('\n\n------', 1)[0]
    datum_list = headline.split(" ")[-3:]

    jahr = datum_list[2]
    monat = datum_list[1]
    tag = datum_list[0][:-1]
    datum = tag + " " + monat + " " + jahr
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
    datum = datetime.strptime(datum, "%d %B %Y").strftime("%d-%m-%Y")
    return datum


def get_agenda(text, regierung):
    text = text.split('\n\n------', 2)[1]
    text = text.split('------\n\n', 1)[1]

    tagesordnungspunkte_list = text.split('\nTagesordnungspunkt ')
    if text.startswith('Tagesordnungspunkt'):
        tagesordnungspunkte_list[0] = tagesordnungspunkte_list[0].split("Tagesordnungspunkt ", 1)[1]
    else:
        zusatz_split = tagesordnungspunkte_list[0].split("Zusatztagesordnungspunkt ", 1)
        if len(zusatz_split) > 1:
            tagesordnungspunkte_list[0] = "Zusatztagesordnungspunkt " + zusatz_split[1]
        else:
            tagesordnungspunkte_list.pop(0)
    tagesordnungspunkte_list = ["Tagesordnungspunkt " + punkt for punkt in tagesordnungspunkte_list]

    tagesordnungspunkte_list_mit_zusatz = []
    for punkt in tagesordnungspunkte_list:
        punkte_split = punkt.split('\nZusatztagesordnungspunkt ')
        tagesordnungspunkte_list_mit_zusatz.append(punkte_split[0])
        for punkt in punkte_split[1:]:
            tagesordnungspunkte_list_mit_zusatz.append("Zusatztagesordnungspunkt " + punkt)

    agenda = []
    for punkt in tagesordnungspunkte_list_mit_zusatz:
        punkte_split = punkt.split('\nFragestunde', 1)
        if len(punkte_split) > 1:
            tagesordnungspunkt = punkte_split[0] + " Fragestunde - "

            fragen_list_temp = []
            dringliche_fragen_split = punkte_split[1].split("\nDringliche Frage")
            if len(dringliche_fragen_split) > 1:
                for dringliche_frage in dringliche_fragen_split[1:]:
                    fragen_list_temp.append(tagesordnungspunkt + "Dringliche Frage" + dringliche_frage)

            for frage in fragen_list_temp:
                mündliche_fragen_split = frage.split("\nMündliche Frage")
                if mündliche_fragen_split[0].startswith(tagesordnungspunkt + "Dringliche Frage"):
                    agenda.append(mündliche_fragen_split[0])
                if len(mündliche_fragen_split) > 1:
                    for mündliche_frage in mündliche_fragen_split[1:]:
                        agenda.append(tagesordnungspunkt + " Mündliche Frage" + mündliche_frage)
        else:
            agenda.append(punkt)

    tagesordnungspunkte_dict = {}
    for tagesordnungspunkt in agenda:
        punkt = tagesordnungspunkt.split("\n", 1)[0]
        if punkt.endswith(":"):
            punkt = punkt[:-1]
        try:
            inhalte = tagesordnungspunkt.split("\n", 1)[1]
        except:
            continue
        inhalte_list_temp = re.split(r"\d+ [A-Z]\n", inhalte)
        inhalte_list_temp2 = []
        for inhalt in inhalte_list_temp:
            if inhalt.startswith("Anlage 1\nListe der"):
                break
            elif inhalt.startswith("Anlage 1\nEntschuldigte Abgeordnete"):
                break
            inhalt_split = re.split(r"\nDr\.", inhalt)
            if len(inhalt_split) > 1:
                inhalt_split[1] = "Dr." + inhalt_split[1]
            inhalte_list_temp2.extend(inhalt_split)
        inhalte_list = []
        for inhalt in inhalte_list_temp2:
            inhalt_split = inhalt.split("\nAntwort\n")
            inhalte_list.extend(inhalt_split)

        last = any(i.startswith("Nächste Sitzung .") for i in inhalte_list)
        if not last:
            last = any(i.startswith("Nächste Sitzung  .") for i in inhalte_list)
            if not last:
                last = any(i.startswith("Nächste Sitzung.") for i in inhalte_list)
                if not last:
                    last = any(i.startswith("Liste der entschuldigten Abgeordneten") for i in inhalte_list)
        if last:
            tagesordnungspunkte_dict[punkt] = []
            for inhalt in inhalte_list:
                if inhalt.startswith("Nächste Sitzung .") or inhalt.startswith("Nächste Sitzung  .") or inhalt.startswith("Nächste Sitzung.") or inhalt.startswith("Liste der entschuldigten Abgeordneten"):
                    break
                else:
                    tagesordnungspunkte_dict[punkt].append(inhalt)
            break


        tagesordnungspunkte_dict[punkt] = inhalte_list

    tagesordnungspunkte_dict = process_tagesordnungspunkte(tagesordnungspunkte_dict, regierung)
    return tagesordnungspunkte_dict


def process_tagesordnungspunkte(tagesordnungspunkte_dict, regierung):
    parteien = ["(CDU/CSU)", "(SPD)", "(FDP)", "(BÜNDNIS 90/DIE GRÜNEN)", "(DIE LINKE)", "(AFD)", "(AfD)", "(Die Linke)", "(BSW)", "(fraktionslos)"]
    ämter = [", Bundeskanzler", ", Bundesminister", ", Staatsminister", ", Parl. Staatssekretär", ", Minister", ", Parl Staatssekretär", "Staatsministerin"]
    new_tagesordnungspunkte_dict = {}
    global reden_count

    for punkt, inhalte in tagesordnungspunkte_dict.items():
        themen = []
        reden = []
        for inhalt in inhalte:
            inhalt = inhalt.replace("Dr .", "Dr.").replace("..", ". . ").replace("\uf020", "").replace(").", ") .").replace("  ", " ").replace(" .", "").replace("\n", " ").replace("/ ", "/").strip()
            if inhalt.endswith(" Antwort"):
                inhalt = inhalt[:-8]
            if inhalt == "":
                continue
            else:
                inhalt = re.split(r"\d+ [A-Z]", inhalt)[0].strip()
                if inhalt.startswith("Zusatzfrage"):
                    try:
                        reden = [reden[0]]
                        inhalt = inhalt.split(" ", 1)[1]
                    except:
                        continue
                if len(inhalt) > 100:
                    if inhalt.startswith("Vereinbarte Debatte"):
                        x = 2
                    themen.append(inhalt)
                elif any(inhalt.endswith(partei) for partei in parteien) or any(amt in inhalt for amt in ämter):
                    if inhalt.startswith("Zur Geschäftsordnung"):
                        inhalt = inhalt.split("Zur Geschäftsordnung")[1][1:].strip()
                    inhalt = replace_abbrevations(inhalt, regierung)
                    if inhalt.startswith("Befragung der Bundesregierung"):
                        themen.append("Befragung der Bundesregierung")
                        inhalt = inhalt.split("Befragung der Bundesregierung", 1)[1].strip()
                    if inhalt.startswith("Vereinbarte Debatte") or inhalt.startswith("Aktuelle ") or inhalt.startswith("Wahl ") or inhalt.startswith("Abgabe "):
                        themen.append(inhalt)
                    else:
                        if ' 11380A ' in inhalt:
                            inhalte = inhalt.split(' 11380A ', 1)
                            reden.append(inhalte[0])
                            reden.append(inhalte[1])
                        else:
                            if regierung == "19" and punkt == "Tagesordnungspunkt 1: (Fortsetzung)" and themen[0].startswith("a) Erste Beratung des von der Bundesregierung") and inhalt == "Dr. Alexander S. Neu (DIE LINKE)":
                                continue
                            elif regierung == "19" and punkt == "Tagesordnungspunkt 24" and themen[0].startswith("Zweite und dritte Beratung des von der Bundesregierung eingebrachten Entwurfs eines Gesetzes zur Änderung des Zensusvorbereitungsgesetzes"):
                                continue
                            elif regierung == "19" and punkt == "Zusatztagesordnungspunkt 13" and themen[0].startswith("Aktuelle Stunde auf Verlangen") and inhalt == "Olav Gutting (CDU/CSU)":
                                continue
                            elif regierung == "19" and punkt == "Tagesordnungspunkt 15" and themen[0].startswith("b) Beschlussempfehlung und Bericht des Ausschusses für Verkehr und digitale Infrastruktur zu dem Antrag der Abgeordneten Dietmar Friedhoff"):
                                continue
                            elif regierung == "19" and punkt == 'Tagesordnungspunkt 11' and themen[0].startswith("a) Wahlvorschlag der Fraktion der AfD: Wahl von Mitgliedern des Gremiums gemäß § 3 des Bundesschuldenwesengesetzes") and inhalt == "Dr. Eva Högl (SPD)":
                                continue
                            elif regierung == "19" and punkt == "Tagesordnungspunkt 35" and themen[0].startswith("d) Erste Beratung des von der Bundesregierung eingebrachten Entwurfs") and inhalt == 'Karsten Hilse (AfD)':
                                continue
                            elif regierung == "19" and punkt == "Tagesordnungspunkt 20" and themen[0].startswith("a) Antrag der Abgeordneten Margit Stumpp,"):
                                continue
                            elif regierung == "19" and punkt == "Tagesordnungspunkt 31" and inhalt == 'Detlev Spangenberg (AfD)':
                                continue
                            elif regierung == "19" and punkt == "Tagesordnungspunkt 7" and themen[0].startswith("r) Beschlussempfehlung und Bericht"):
                                continue
                            elif regierung == "19" and punkt == "Tagesordnungspunkt 4" and themen[0].startswith("a) Beschlussempfehlung und Bericht") and inhalt == 'Bernhard Loos (CDU/CSU)':
                                continue
                            elif regierung == "19" and punkt == "Tagesordnungspunkt 8" and themen[0].startswith('Wahlvorschlag der Fraktion der AfD: Wahl eines Stellvertreters') and inhalt == 'Dagmar Ziegler (SPD)':
                                continue
                            elif regierung == "19" and punkt == "Tagesordnungspunkt 37" and (themen[0].startswith('v) Antrag der Abgeordneten Mariana Iris') or themen[0].startswith('j) Erste Beratung des von der Bundesregi')):
                                continue
                            elif regierung == "19" and punkt == "Tagesordnungspunkt 27" and themen[0].startswith('a) Zweite und dritte Beratung des von der'):
                                continue
                            elif regierung == "19" and punkt == "Tagesordnungspunkt 51" and (themen[0].startswith('k) Beschlussempfehlung und Bericht des Ausschusses') or themen[0].startswith('dddd) Beschlussempfehlung')):
                                continue
                            elif regierung == "20" and punkt == "Tagesordnungspunkt 6" and themen[0].startswith('Wahlvorschlag der Fraktion BÜNDNIS 90/DIE GRÜNEN: Wahl einer Stellvertreterin der Präsidentin (1. Wahlgang)'):
                                continue
                            elif regierung == "20" and punkt == "Tagesordnungspunkt VI" and themen[0].startswith('– Zweite und dritte Beratung des von der Bundesregierung eingebrachten Entwurfs'):
                                continue
                            elif regierung == "20" and punkt == "Tagesordnungspunkt 2" and themen[0].startswith('a) – Zweite und dritte Beratung des von den Fraktionen SPD, BÜNDNIS 90/DIE GRÜNEN und FDP eingebrachten Entwurfs eines Gesetzes zur Stärkung'):
                                continue
                            elif regierung == "20" and punkt == "Tagesordnungspunkt 13" and themen[0].startswith('Wahlvorschlag der Fraktion der AfD: Wahl eines Mitglieds des Parlamentarischen') and (inhalt == 'Peter Boehringer (AfD)' or inhalt == 'Alexander Ulrich (DIE LINKE)'):
                                continue
                            elif regierung == "20" and punkt == "Tagesordnungspunkt 32" and themen[0].startswith('g) Antrag der Abgeordneten Stephan Brandner, Marc Bernhard, Roger Beckamp, weiterer Abgeordneter und der Fraktion der AfD: Erweiterungsba'):
                                continue
                            elif regierung == "20" and punkt == "Tagesordnungspunkt I (Fortsetzung)" and themen[0].startswith('I. 15 a) Einzelplan'):
                                continue
                            elif regierung == "20" and punkt == "Tagesordnungspunkt 37" and themen[0].startswith('i) Antrag der Abgeordneten Marc Bernhard, Roger Beckamp'):
                                continue
                            elif regierung == "20" and punkt == "Tagesordnungspunkt 26" and themen[0].startswith('c) Antrag der Abgeordneten Susanne Ferschl, Ina Latendorf, Gökay Akbulut, weiterer Abgeordneter'):
                                continue
                            elif regierung == "20" and punkt == "Tagesordnungspunkt 37" and themen[0].startswith('a) Antrag der Fraktion der CDU/CSU: Kontinuität'):
                                continue
                            elif regierung == "20" and punkt == "Tagesordnungspunkt 33" and themen[0].startswith('a) Erste Beratung des von den Abgeordneten Caren Lay, Dr. Gesine Lötzsch,'):
                                continue
                            elif regierung == "20" and punkt == "Tagesordnungspunkt I (Fortsetzung)" and themen[0].startswith('I.'):
                                continue
                            else:
                                reden.append(inhalt)
                else:
                    if inhalt.startswith("Präsident") or inhalt.startswith("Alterspräsident"):
                        continue
                    elif inhalt != "":
                        themen.append(inhalt)

        themen = "\n".join(themen)
        if len(themen) > 0 or len(reden) > 1:
            new_tagesordnungspunkte_dict[punkt] = {}
            new_tagesordnungspunkte_dict[punkt]["Thema"] = themen
            new_tagesordnungspunkte_dict[punkt]["Reden"] = reden
            reden_count += len(reden)

    return new_tagesordnungspunkte_dict


def replace_abbrevations(inhalt, regierung):
    inhalt = inhalt.replace("  ", " ").replace("- ", "-").replace("BK.", "BK").replace("AA.", "AA")
    inhalt = inhalt + " "
    inhalt = inhalt.replace("Bundesminister ", "Bundesministerium ").replace("Bundesministerin ", "Bundesministerium ")
    inhalt = inhalt.replace("Parl. Staatssekretär ", "Parl. Staatssekretär beim Bundesministerium ")
    inhalt = inhalt.replace("Parl. Staatssekretärin ", "Parl. Staatssekretärin beim Bundesministerium ")
    inhalt = inhalt.replace("BMAS ", "für Arbeit und Soziales")
    inhalt = inhalt.replace("BMAS", "für Arbeit und Soziales")
    inhalt = inhalt.replace("BMI ", "des Innern")
    inhalt = inhalt.replace("BMJ ", "der Justiz")
    inhalt = inhalt.replace("BMF.", "der Finanzen")
    inhalt = inhalt.replace("BMF ", "der Finanzen")
    inhalt = inhalt.replace("BMVg.", "der Verteidigung")
    inhalt = inhalt.replace("BMVg ", "der Verteidigung")
    inhalt = inhalt.replace("BMFSFJ ", "für Familie, Senioren, Frauen und Jugend")
    inhalt = inhalt.replace("BMFSFJ.", "für Familie, Senioren, Frauen und Jugend")
    inhalt = inhalt.replace("BMG.", "für Gesundheit")
    inhalt = inhalt.replace("BMG ", "für Gesundheit")
    inhalt = inhalt.replace("BMVBS ", "für Verkehr, Bau und Stadtentwicklung")
    inhalt = inhalt.replace("BMDV ", "für Digitales und Verkehr")
    inhalt = inhalt.replace("BMDV.", "für Digitales und Verkehr")
    inhalt = inhalt.replace("BMWK.", "für Wirtschaft und Klimaschutz")
    inhalt = inhalt.replace("BMWK ", "für Wirtschaft und Klimaschutz")
    inhalt = inhalt.replace("BMWSB ", "für Wohnen, Stadtentwicklung und Bauwesen")
    inhalt = inhalt.replace("BMWSB.", "für Wohnen, Stadtentwicklung und Bauwesen")
    if regierung == "17" or regierung == "18":
        inhalt = inhalt.replace("BMU ", "für Umwelt, Naturschutz und Reaktorsicherheit")
    else:
        inhalt = inhalt.replace("BMU.", "für Umwelt, Naturschutz und nukleare Sicherheit")
        inhalt = inhalt.replace("BMU ", "für Umwelt, Naturschutz und nukleare Sicherheit")
    if regierung == "17":
        inhalt = inhalt.replace("BMWi ", "für Wirtschaft und Technologie")
    else:
        inhalt = inhalt.replace("BMWi.", "für Wirtschaft und Energie")
        inhalt = inhalt.replace("BMWi", "für Wirtschaft und Energie")
    inhalt = inhalt.replace("BMBF.", "für Bildung und Forschung")
    inhalt = inhalt.replace("BMBF ", "für Bildung und Forschung")
    inhalt = inhalt.replace("BMELV ", "für Ernährung, Landwirtschaft und Verbraucherschutz")
    inhalt = inhalt.replace("BMEL ", "für Ernährung und Landwirtschaft")
    inhalt = inhalt.replace("BMEL.", "für Ernährung und Landwirtschaft")
    inhalt = inhalt.replace("BMJV.", "der Justiz und für Verbraucherschutz")
    inhalt = inhalt.replace("BMJV", "der Justiz und für Verbraucherschutz")
    inhalt = inhalt.replace("BMVI ", "für Verkehr und digitale Infrastruktur")
    inhalt = inhalt.replace("BMUB", "für Umwelt, Naturschutz, Bau und Reaktorsicherheit")
    inhalt = inhalt.replace("BMZ.", "für wirtschaftliche Zusammenarbeit und Entwicklung")
    inhalt = inhalt.replace("BMZ ", "für wirtschaftliche Zusammenarbeit und Entwicklung")
    inhalt = inhalt.replace("BMUV." ,"für Umwelt, Naturschutz, nukleare Sicherheit und Verbraucherschutz")
    inhalt = inhalt.replace("BMUV ", "für Umwelt, Naturschutz, nukleare Sicherheit und Verbraucherschutz")
    inhalt = inhalt.replace("Staatsministerin AA", "Staatsministerium im Auswärtigen Amt")
    inhalt = inhalt.replace("Staatsminister AA", "Staatsministerium im Auswärtigen Amt")
    inhalt = inhalt.replace("Staatsminister ", "Staatsministerium ")
    inhalt = inhalt.replace("Staatsministerin ", "Staatsministerium ")
    inhalt = inhalt.replace("bei der Bundeskanzlerin ", "im Bundeskanzleramt")
    inhalt = inhalt.replace("beim Bundeskanzler ", "im Bundeskanzleramt")
    inhalt = inhalt.replace("Bundeskanzlerin ", "Bundeskanzleramt")
    inhalt = inhalt.replace("Bundeskanzlerin.", "Bundeskanzleramt")
    inhalt = inhalt.replace("Bundeskanzler ", "Bundeskanzleramt")
    inhalt = inhalt.replace("BK ", "im Bundeskanzleramt")
    inhalt = inhalt.replace("Antwort ", "")
    inhalt = inhalt.replace("Staatsministerium im AA", "Staatsministerium im Auswärtigen Amt")
    inhalt = inhalt.replace("Özoguz", "Özoğuz")
    inhalt = inhalt.replace(" (Erklärung nach §", "")
    inhalt = inhalt.replace("4038", "")
    inhalt = inhalt.replace("BMBU", "für Umwelt, Naturschutz, Bau und Reaktorsicherheit")
    inhalt = inhalt.replace("(§", "")
    inhalt = inhalt.replace("Dr. Alexander S Neu (DIE LINKE)", "Dr. Alexander S. Neu (DIE LINKE)")
    inhalt = inhalt.replace(" G ", ' G. ')
    inhalt = inhalt.replace(' E ', ' E. ')
    inhalt = inhalt.replace(' W ', ' W. ')
    inhalt = inhalt.replace(' M ', ' M. ').replace(" A ", " A. ").replace(" L ", " L. ").replace(" H ", " H. ")
    inhalt = inhalt.replace(' h c ', ' h. c. ')
    inhalt = inhalt.replace(' Parl ', ' Parl. ')
    inhalt = inhalt.replace('Nadine Schön (St Wendel) (CDU/CSU)', 'Nadine Schön (St. Wendel) (CDU/CSU)')
    inhalt = inhalt.replace("Parl. Staatssekretär der", 'Parl. Staatssekretär beim Bundesministerium der')
    inhalt = inhalt.replace("Parl. Staatssekretärin der", 'Parl. Staatssekretärin beim Bundesministerium der')
    inhalt = inhalt.replace("Parl. Staatssekretärin für", 'Parl. Staatssekretärin beim Bundesministerium für')
    inhalt = inhalt.replace("Parl. Staatssekretär für", 'Parl. Staatssekretär beim Bundesministerium für')
    inhalt = inhalt.replace("Parl. Staatssekretärin des", 'Parl. Staatssekretärin beim Bundesministerium des')
    inhalt = inhalt.replace("Parl. Staatssekretär des", 'Parl. Staatssekretär beim Bundesministerium des')
    inhalt = inhalt.replace("­ ", "").replace("­", "-")
    inhalt = inhalt.replace("Justizund", "Justiz und")
    inhalt = inhalt.replace('Memet Kilic (BÜNDNIS 90/DIE GRÜNEN) Konkretisierung der von Staatsministerium', 'Memet Kilic (BÜNDNIS 90/DIE GRÜNEN)')
    inhalt = inhalt.replace("Weitere Fragen: ", "")
    inhalt = inhalt.replace('Wirtschaftliche Zusammenarbeit und Entwicklung Dr.', 'Dr.')
    inhalt = inhalt.replace('Verkehr und digitale Infrastruktur Andreas', 'Andreas')
    inhalt = inhalt.replace('Bildung und Forschung Anja', "Anja")
    inhalt = inhalt.replace('Ernährung und Landwirtschaft Julia', 'Julia')
    inhalt = inhalt.replace('Umwelt, Naturschutz und nukleare Sicherheit Svenja', 'Svenja')
    inhalt = inhalt.replace('Gesundheit Jens', 'Jens')
    inhalt = inhalt.replace("Allgemeine Finanzdebatte (einschließlich Einzelpläne 08, 20, 32 und 60)", "")
    inhalt = inhalt.replace("Bundesministerium für besondere Aufgaben.", "Bundesministerium für besondere Aufgaben")
    inhalt = inhalt.replace('Dr. h. c. #Univ Kyiv) Hans Michelbach (CDU/CSU)', 'Dr. h. c. (Univ Kyiv) Hans Michelbach (CDU/CSU)')
    inhalt = inhalt.replace("Außen, Europa und Menschenrechte Annalena Baerbock", "Annalena Baerbock")
    inhalt = inhalt.replace("Umwelt, Naturschutz, nukleare Sicherheit und Verbraucherschutz Steffi Lemke", "Steffi Lemke")
    inhalt = inhalt.replace("Arbeit und Soziales Kerstin Griese", "Kerstin Griese")
    inhalt = inhalt.replace("Familie, Senioren, Frauen und Jugend Anne Spiegel", "Anne Spiegel")
    inhalt = inhalt.replace("Bundeskanzleramt (Ostdeutschland, Integration und Kultur) Carsten Schneider", "Carsten Schneider")
    inhalt = inhalt.replace("Wohnen, Stadtentwicklung und Bauwesen Klara Geywitz", "Klara Geywitz")
    inhalt = inhalt.replace("Ernährung und Landwirtschaft Cem Özdemir", "Cem Özdemir")
    inhalt = inhalt.replace('Verteidigung Christine Lambrecht', "Christine Lambrecht")
    inhalt = inhalt.replace('Wirtschaftliche Zusammenarbeit und Entwicklung Svenja Schulze', "Svenja Schulze")
    inhalt = inhalt.replace('Marja Liisa', 'Marja-Liisa')
    inhalt = inhalt.replace('Bundesministerium für Familie, Senioren, Frauen und Jugend Paul Lehrieder (CDU/CSU)', 'Paul Lehrieder (CDU/CSU)')
    inhalt = inhalt.replace('Bundesministerium für Wohnen, Stadtentwicklung und Bauwesen Markus Uhl (CDU/CSU)',
                            'Markus Uhl (CDU/CSU)')
    inhalt = inhalt.replace('Bundesministerium für Digitales und Verkehr Florian Oßner (CDU/CSU)',
                            'Florian Oßner (CDU/CSU)')
    inhalt = inhalt.replace('Bundesbeauftragter für den Datenschutz und die Informationsfreiheit Yannick Bury (CDU/CSU)',
                            'Yannick Bury (CDU/CSU)')
    inhalt = inhalt.replace('Bundesministerium für Bildung und Forschung Kerstin Radomski (CDU/CSU)',
                            'Kerstin Radomski (CDU/CSU)')
    inhalt = inhalt.replace('Unabhängiger Kontrollrat Friedrich Merz (CDU/CSU)', 'Friedrich Merz (CDU/CSU)')
    inhalt = inhalt.replace('Auswärtiges Amt Carsten Körber (CDU/CSU)', 'Carsten Körber (CDU/CSU)')
    inhalt = inhalt.replace('Bundesministerium der Verteidigung Ingo Gädechens (CDU/CSU)', 'Ingo Gädechens (CDU/CSU)')
    inhalt = inhalt.replace('Bundesministerium für wirtschaftliche Zusammenarbeit und Entwicklung Carsten Körber (CDU/CSU)', 'Carsten Körber (CDU/CSU)')
    inhalt = inhalt.replace('Bundesministerium für Ernährung und Landwirtschaft Josef Rief (CDU/CSU)', 'Josef Rief (CDU/CSU)')
    inhalt = inhalt.replace('Zusatzpunkte 3 und 4 (Fortsetzung): Jörg Cezanne (Die Linke)', 'Jörg Cezanne (Die Linke)')
    inhalt = inhalt.replace('Auswärtiges Amt Annalena Baerbock', 'Annalena Baerbock')
    inhalt = inhalt.replace('Verkehrsowie', 'Verkehr sowie')
    inhalt = inhalt.replace('Zu Zusatzpunkt 9 d: ', '')
    inhalt = inhalt.replace('Landwirtschaftsowie', 'Landwirtschaft sowie')
    inhalt = inhalt.replace('Bundesministerium für Bildung und Forschung Bettina Stark-Watzinger, Bundesministerium für Bildung und Forschung', 'Bettina Stark-Watzinger, Bundesministerium für Bildung und Forschung')
    inhalt = inhalt.replace('Bundesministerium für Familie, Senioren, Frauen und Jugend Lisa Paus, Bundesministerium für Familie, Senioren, Frauen und Jugend', 'Lisa Paus, Bundesministerium für Familie, Senioren, Frauen und Jugend')
    inhalt = inhalt.replace('Bundesministerium der Verteidigung Wolfgang Hellmich (SPD)', 'Wolfgang Hellmich (SPD)')
    inhalt = inhalt.replace('Bundeskanzleramtund Bundeskanzleramt sowie Unabhängiger Kontrollrat Alexander Dobrindt (CDU/CSU)', 'Alexander Dobrindt (CDU/CSU)')
    inhalt = inhalt.replace('Bundesministerium für Klara Geywitz, Bundesministerium für Wohnen, Stadtentwicklung und Bauwesen', 'Klara Geywitz, Bundesministerium für Wohnen, Stadtentwicklung und Bauwesen')
    inhalt = inhalt.replace('Bundesministerium für Cem Özdemir, Bundesministerium für Ernährung und Landwirtschaft', 'Cem Özdemir, Bundesministerium für Ernährung und Landwirtschaft')
    inhalt = inhalt.replace('Bundesministerium für Arbeit und Soziales Hubertus Heil, Bundesministerium für Arbeit und Soziales',
                            'Hubertus Heil, Bundesministerium für Arbeit und Soziales')
    if inhalt[-1] == ".":
        inhalt = inhalt[:-1]
    inhalt = inhalt.strip()

    return inhalt


def main():
    txt_folder = "Plenarprotokolle/txt"
    preprocessed_folder = "Plenarprotokolle/preprocessed/"
    os.makedirs(preprocessed_folder, exist_ok=True)
    tagesordnungspunkte_json = {}

    for filename in sorted(os.listdir(txt_folder)):
        print(f"Verarbeite: {filename}")
        if filename.endswith(".txt"):
            file_path = os.path.join(txt_folder, filename)

            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()

            text = add_bookmarks(text)
            text = replace_unicode(text)

            with open(preprocessed_folder + filename, "w", encoding="utf-8") as file:
                file.write(text)

            metadata = get_metadata(text, filename[:2])
            tagesordnungspunkte_json[filename[:-4]] = metadata

    with open("Plenarprotokolle/agenda.json", "w", encoding="utf-8") as json_file:
        json.dump(tagesordnungspunkte_json, json_file, ensure_ascii=False, indent=4)

    print("Reden:", reden_count)


if __name__ == "__main__":
    main()
