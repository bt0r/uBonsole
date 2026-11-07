#!/usr/bin/env python3
"""Generates the SDR frequency cheat sheets (config/i3/frequencies/<lang>.txt).

Each file is Pango markup shown by the radio block (rofi -e -markup) in two columns.
Edit the tables below, then run:  python3 tools/gen-frequencies.py
Ranges follow the ITU/IARU Region 1 band plans and French allocations; "do not listen"
ranges are indicative blocks, not an official channel list.
"""
from html import escape
from pathlib import Path

LANGS = ("en", "fr", "de", "es")
OUT = Path(__file__).resolve().parent.parent / "config/i3/frequencies"

# Text in the user's language: {lang: text}
T = {
    "title": {"en": "SDR FREQUENCIES — FRANCE / EUROPE", "fr": "FRÉQUENCES SDR — FRANCE / EUROPE",
              "de": "SDR-FREQUENZEN — FRANKREICH / EUROPA", "es": "FRECUENCIAS SDR — FRANCIA / EUROPA"},
    "broadcast": {"en": "BROADCAST", "fr": "RADIODIFFUSION", "de": "RUNDFUNK", "es": "RADIODIFUSIÓN"},
    "ham": {"en": "AMATEUR RADIO", "fr": "RADIOAMATEUR", "de": "AMATEURFUNK", "es": "RADIOAFICIONADOS"},
    "misc": {"en": "HOBBY / MISC", "fr": "LOISIRS / DIVERS", "de": "HOBBY / SONSTIGES", "es": "OCIO / VARIOS"},
    "tolerated": {"en": "TOLERATED LISTENING — DISCLOSE NOTHING", "fr": "ÉCOUTE TOLÉRÉE — NE RIEN DIVULGUER",
                  "de": "GEDULDETES MITHÖREN — NICHTS WEITERGEBEN", "es": "ESCUCHA TOLERADA — NO DIVULGAR NADA"},
    "forbidden": {"en": "DO NOT LISTEN (approximate ranges)", "fr": "À NE PAS ÉCOUTER (plages indicatives)",
                  "de": "NICHT ABHÖREN (Richtwerte)", "es": "NO ESCUCHAR (rangos orientativos)"},
    "private": {"en": "Any private or encrypted communication", "fr": "Toute correspondance privée ou chiffrée",
                "de": "Jede private oder verschlüsselte Kommunikation", "es": "Toda comunicación privada o cifrada"},
    "digital": {"en": "digital", "fr": "numérique", "de": "digital", "es": "digital"},
}


def tr(en, fr, de, es):
    return {"en": en, "fr": fr, "de": de, "es": es}


H = "header"
# Left column: (frequency, description, mode). Frequencies use a decimal comma; English gets a dot.
LEFT = [
    (H, "broadcast"),
    ("148,5 – 283,5 kHz", tr("Long wave (LW)", "Grandes ondes (GO)", "Langwelle (LW)", "Onda larga (OL)"), "AM"),
    ("526,5 – 1606,5 kHz", tr("Medium wave (MW)", "Petites ondes (PO)", "Mittelwelle (MW)", "Onda media (OM)"), "AM"),
    ("3,95 – 26,1 MHz", tr("Shortwave (scattered bands)", "Ondes courtes (bandes éparses)",
                           "Kurzwelle (verstreute Bänder)", "Onda corta (bandas dispersas)"), "AM"),
    ("87,5 – 108 MHz", tr("FM radio", "Radio FM", "UKW-Radio", "Radio FM"), "WFM"),
    ("174 – 240 MHz", tr("DAB+ (digital)", "DAB+ (numérique)", "DAB+ (digital)", "DAB+ (digital)"), "welle.io"),
    None,
    (H, "ham"),
    ("1,81 – 2,0 MHz", "160 m", "LSB / CW"),
    ("3,5 – 3,8 MHz", "80 m", "LSB / CW"),
    ("7,0 – 7,2 MHz", "40 m", "LSB / CW"),
    ("14,0 – 14,35 MHz", "20 m", "USB / CW"),
    ("21,0 – 21,45 MHz", "15 m", "USB / CW"),
    ("28,0 – 29,7 MHz", "10 m", "USB / FM"),
    ("50 – 52 MHz", "6 m", "USB / NFM"),
    ("144,05 – 144,4 MHz", "2 m CW / SSB", "USB / CW"),
    ("144,800 MHz", "APRS", "NFM → direwolf"),
    ("145,2 – 145,8 MHz", tr("2 m FM, repeaters (145.6+)", "2 m FM, relais (145,6+)",
                             "2 m FM, Relais (145,6+)", "2 m FM, repetidores (145,6+)"), "NFM"),
    ("145,800 MHz", tr("ISS (voice, SSTV)", "ISS (phonie, SSTV)", "ISS (Sprache, SSTV)", "ISS (voz, SSTV)"), "NFM"),
    ("430 – 440 MHz", tr("70 cm (repeaters, satellites)", "70 cm (relais, satellites)",
                         "70 cm (Relais, Satelliten)", "70 cm (repetidores, satélites)"), "NFM / USB"),
    ("1240 – 1300 MHz", "23 cm", "NFM / USB"),
    None,
    (H, "misc"),
    ("26,965 – 27,405 MHz", tr("CB (ch. 19: 27.185)", "CB (canal 19 : 27,185)",
                               "CB (Kanal 19: 27,185)", "CB (canal 19: 27,185)"), "AM / FM"),
    ("137,1 / 137,9 MHz", tr("Meteor-M weather satellites", "Satellites météo Meteor-M",
                             "Meteor-M Wettersatelliten", "Satélites meteo Meteor-M"), "→ SatDump"),
    ("400 – 406 MHz", tr("Weather radiosondes", "Radiosondes météo", "Wetter-Radiosonden",
                         "Radiosondas meteorológicas"), "→ auto_rx"),
    ("433,92 MHz", tr("ISM sensors (weather, remotes)", "Capteurs ISM (météo, télécom.)",
                      "ISM-Sensoren (Wetter, Fernbed.)", "Sensores ISM (meteo, mandos)"), "→ rtl_433"),
    ("446,0 – 446,2 MHz", tr("PMR446 (walkie-talkies, 16 ch.)", "PMR446 (talkies, 16 canaux)",
                             "PMR446 (Funkgeräte, 16 Kanäle)", "PMR446 (walkies, 16 canales)"), "NFM"),
    ("868 / 869,525 MHz", "LoRa / Meshtastic", T["digital"]),
    ("1090 MHz", tr("ADS-B (aircraft)", "ADS-B (avions)", "ADS-B (Flugzeuge)", "ADS-B (aviones)"), "→ tar1090"),
]
# Right column: (frequency, description[, mode])
RIGHT = [
    (H, "tolerated"),
    ("108 – 118 MHz", tr("VOR / ILS beacons", "Balises VOR / ILS", "VOR- / ILS-Funkfeuer", "Radiobalizas VOR / ILS"), "AM"),
    ("118 – 137 MHz", tr("Civil aviation (121.5 emergency)", "Aviation civile (121,5 urgence)",
                         "Zivilluftfahrt (121,5 Notfall)", "Aviación civil (121,5 emergencia)"), "AM"),
    ("131,525 / 131,725", "ACARS", "→ acarsdec"),
    ("136,975 MHz", "VDL2", "→ dumpvdl2"),
    ("156 – 162 MHz", tr("Marine VHF (ch. 16: 156.800)", "VHF marine (canal 16 : 156,800)",
                         "Seefunk UKW (Kanal 16: 156,800)", "VHF marina (canal 16: 156,800)"), "NFM"),
    ("161,975 / 162,025", tr("AIS (ships)", "AIS (navires)", "AIS (Schiffe)", "AIS (barcos)"), "→ AIS-catcher"),
    None,
    (H, "forbidden"),
    ("40,66 – 40,70 MHz", tr("Baby monitors, remote controls", "Babyphones, télécommandes",
                             "Babyphones, Fernbedienungen", "Vigilabebés, mandos a distancia")),
    ("68 – 87,5 MHz", tr("Professional radio, defence (low VHF)", "Radiocom pro, défense (VHF basse)",
                         "Betriebsfunk, Militär (VHF-Low)", "Radio profesional, defensa (VHF baja)")),
    ("146 – 156 MHz", tr("Professional VHF (transport, ambulances)", "Radiocom pro VHF (transports, ambulances)",
                         "Betriebsfunk VHF (Verkehr, Rettung)", "Radio prof. VHF (transporte, ambulancias)")),
    ("162 – 174 MHz", tr("Professional VHF, smart meters", "Radiocom pro VHF, télérelevé compteurs",
                         "Betriebsfunk VHF, Zählerfernablesung", "Radio prof. VHF, telelectura contadores")),
    ("225 – 380 MHz", tr("Military aviation UHF", "Aviation militaire UHF", "Militärluftfahrt UHF", "Aviación militar UHF")),
    ("380 – 400 MHz", tr("Police, fire, ambulance (INPT / TETRA)", "Police, gendarmerie, pompiers, SAMU (INPT)",
                         "Polizei, Feuerwehr, Rettung (TETRA)", "Policía, bomberos, emergencias (TETRA)")),
    ("410 – 430 MHz", tr("Professional UHF, private TETRA", "Radiocom pro UHF, réseaux privés TETRA",
                         "Betriebsfunk UHF, private TETRA-Netze", "Radio prof. UHF, redes TETRA privadas")),
    ("440 – 446 MHz", tr("Professional UHF (security, construction)", "Radiocom pro UHF (sécurité, BTP)",
                         "Betriebsfunk UHF (Sicherheit, Bau)", "Radio prof. UHF (seguridad, obras)")),
    ("446,2 – 470 MHz", tr("Professional UHF, public transport", "Radiocom pro UHF, transports urbains",
                           "Betriebsfunk UHF, Nahverkehr", "Radio prof. UHF, transporte urbano")),
    ("466,0 – 466,25 MHz", tr("e*Message pagers (POCSAG)", "Pagers e*Message (POCSAG)",
                              "e*Message-Pager (POCSAG)", "Buscas e*Message (POCSAG)")),
    ("703 – 862 MHz", tr("Mobile network 4G / 5G (700, 800)", "Téléphonie mobile 4G / 5G (700, 800)",
                         "Mobilfunk 4G / 5G (700, 800)", "Telefonía móvil 4G / 5G (700, 800)")),
    ("876 – 960 MHz", tr("Mobile network 900, GSM-R (railways)", "Téléphonie mobile 900, GSM-R (SNCF)",
                         "Mobilfunk 900, GSM-R (Bahn)", "Telefonía móvil 900, GSM-R (ferrocarril)")),
    ("1710 – 1880 MHz", tr("Mobile network 4G (1800)", "Téléphonie mobile 4G (1800)",
                           "Mobilfunk 4G (1800)", "Telefonía móvil 4G (1800)")),
    ("1880 – 1900 MHz", tr("DECT cordless phones", "Téléphones sans fil DECT",
                           "DECT-Schnurlostelefone", "Teléfonos inalámbricos DECT")),
    None,
    ("", T["private"]),
]

LCOLS = (22, 32, 14)   # frequency, description, mode
RCOLS = (22, 42)       # frequency, description
GAP = "    "


def text(value, lang):
    return value[lang] if isinstance(value, dict) else value


def freq(value, lang):
    return value.replace(",", ".") if lang == "en" else value


def row(item, cols, lang):
    """Returns (plain text, markup) for one line."""
    if item is None:
        return "", ""
    if item[0] == H:
        label = T[item[1]][lang]
        return label, "<b>%s</b>" % escape(label)
    vals = [freq(item[0], lang)] + [text(v, lang) for v in item[1:]]
    vals += [""] * (len(cols) - len(vals))
    for v, w in zip(vals, cols):
        assert len(v) < w or v is vals[-1], "column too narrow for %r (%s)" % (v, lang)
    plain = "".join(v.ljust(w) for v, w in zip(vals, cols)).rstrip()
    return plain, escape(plain)


def build(lang):
    left = [row(i, LCOLS, lang) for i in LEFT]
    right = [row(i, RCOLS, lang) for i in RIGHT]
    n = max(len(left), len(right))
    left += [("", "")] * (n - len(left))
    right += [("", "")] * (n - len(right))
    width = sum(LCOLS)
    lines = ["<b>%s</b>" % escape(T["title"][lang]), ""]
    for (lt, lm), (_, rm) in zip(left, right):
        lines.append((lm + " " * (width - len(lt)) + GAP + rm).rstrip())
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in LANGS:
        (OUT / ("%s.txt" % lang)).write_text(build(lang))
        print("wrote", OUT / ("%s.txt" % lang))
