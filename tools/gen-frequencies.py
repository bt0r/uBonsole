#!/usr/bin/env python3
"""Generates the SDR frequency cheat sheets: config/i3/frequencies/<region>/<lang>.txt

Each file is Pango markup shown by the radio block (rofi -e -markup) in two columns.
Regions differ in band plans (ITU Region 1 vs Region 2), licence-free radio, ACARS/APRS
frequencies and in what the law lets you listen to. Edit the tables below, then run:

    python3 tools/gen-frequencies.py

"Do not listen" ranges are indicative blocks, not an official channel list.
"""
from html import escape
from pathlib import Path

LANGS = ("en", "fr", "de", "es")
OUT = Path(__file__).resolve().parent.parent / "config/i3/frequencies"
MAX_LINES = 36          # what fits on the 720 px uConsole screen
LCOLS = (24, 32, 15)    # frequency, description, mode
RCOLS = (24, 42)        # frequency, description
GAP = "    "
H, NOTE = "header", "note"
ERRORS = []             # layout problems, reported all at once


def check(ok, msg):
    if not ok:
        ERRORS.append(msg)


def tr(en, fr, de, es):
    return {"en": en, "fr": fr, "de": de, "es": es}


# ----------------------------------------------------------------- headers / shared text
HEAD = {
    "broadcast": tr("BROADCAST", "RADIODIFFUSION", "RUNDFUNK", "RADIODIFUSIÓN"),
    "ham": tr("AMATEUR RADIO", "RADIOAMATEUR", "AMATEURFUNK", "RADIOAFICIONADOS"),
    "misc": tr("HOBBY / MISC", "LOISIRS / DIVERS", "HOBBY / SONSTIGES", "OCIO / VARIOS"),
    "tolerated": tr("TOLERATED LISTENING — DISCLOSE NOTHING", "ÉCOUTE TOLÉRÉE — NE RIEN DIVULGUER",
                    "GEDULDETES MITHÖREN — NICHTS WEITERGEBEN", "ESCUCHA TOLERADA — NO DIVULGAR NADA"),
    "grey": tr("LEGAL GREY AREA — DISCLOSE NOTHING", "ZONE GRISE LÉGALE — NE RIEN DIVULGUER",
               "RECHTLICHE GRAUZONE — NICHTS WEITERGEBEN", "ZONA GRIS LEGAL — NO DIVULGAR NADA"),
    "monitor_us": tr("LEGAL TO MONITOR — NEVER DECRYPT", "ÉCOUTE LÉGALE — NE JAMAIS DÉCHIFFRER",
                     "MITHÖREN ERLAUBT — NIE ENTSCHLÜSSELN", "ESCUCHA LEGAL — NUNCA DESCIFRAR"),
    "monitor_ca": tr("MONITORING OK — NEVER DIVULGE OR USE", "ÉCOUTE OK — NE RIEN DIVULGUER NI UTILISER",
                     "MITHÖREN OK — NIE WEITERGEBEN/NUTZEN", "ESCUCHA OK — NO DIVULGAR NI USAR"),
    "forbidden": tr("DO NOT LISTEN (approximate ranges)", "À NE PAS ÉCOUTER (plages indicatives)",
                    "NICHT ABHÖREN (Richtwerte)", "NO ESCUCHAR (rangos orientativos)"),
    "protected": tr("DO NOT LISTEN — PROTECTED BY LAW", "INTERDIT — PROTÉGÉ PAR LA LOI",
                    "NICHT ABHÖREN — GESETZLICH GESCHÜTZT", "NO ESCUCHAR — PROTEGIDO POR LEY"),
}
PRIVATE = tr("Any private or encrypted communication", "Toute correspondance privée ou chiffrée",
             "Jede private oder verschlüsselte Kommunikation", "Toda comunicación privada o cifrada")
DIGITAL = tr("digital", "numérique", "digital", "digital")

TITLE = {
    "fr": tr("FRANCE", "FRANCE", "FRANKREICH", "FRANCIA"),
    "uk": tr("UNITED KINGDOM", "ROYAUME-UNI", "VEREINIGTES KÖNIGREICH", "REINO UNIDO"),
    "de": tr("GERMANY", "ALLEMAGNE", "DEUTSCHLAND", "ALEMANIA"),
    "es": tr("SPAIN", "ESPAGNE", "SPANIEN", "ESPAÑA"),
    "us": tr("USA", "ÉTATS-UNIS", "USA", "EE. UU."),
    "ca": tr("CANADA", "CANADA", "KANADA", "CANADÁ"),
    "eu": tr("EUROPE (ITU REGION 1)", "EUROPE (RÉGION UIT 1)", "EUROPA (ITU-REGION 1)", "EUROPA (REGIÓN UIT 1)"),
}
SDR_FREQ = tr("SDR FREQUENCIES", "FRÉQUENCIES SDR", "SDR-FREQUENZEN", "FRECUENCIAS SDR")
SDR_FREQ["fr"] = "FRÉQUENCES SDR"

# ----------------------------------------------------------------- reusable rows
LW = ("148,5 – 283,5 kHz", tr("Long wave (LW)", "Grandes ondes (GO)", "Langwelle (LW)", "Onda larga (OL)"), "AM")
MW_R1 = ("526,5 – 1606,5 kHz", tr("Medium wave (MW)", "Petites ondes (PO)", "Mittelwelle (MW)", "Onda media (OM)"), "AM")
SW_R1 = ("3,95 – 26,1 MHz", tr("Shortwave (scattered bands)", "Ondes courtes (bandes éparses)",
                              "Kurzwelle (verstreute Bänder)", "Onda corta (bandas dispersas)"), "AM")
FM_R1 = ("87,5 – 108 MHz", tr("FM radio", "Radio FM", "UKW-Radio", "Radio FM"), "WFM")
DAB = ("174 – 240 MHz", tr("DAB+ (digital)", "DAB+ (numérique)", "DAB+ (digital)", "DAB+ (digital)"), "welle.io")

MW_R2 = ("530 – 1700 kHz", tr("AM radio", "Radio AM", "AM-Radio", "Radio AM"), "AM")
SW_R2 = ("5,9 – 26,1 MHz", SW_R1[1], "AM")
FM_R2 = ("88,1 – 107,9 MHz", tr("FM radio (HD Radio)", "Radio FM (HD Radio)", "UKW-Radio (HD Radio)", "Radio FM (HD Radio)"), "WFM")
WX_US = ("162,400 – 162,550 MHz", tr("NOAA Weather Radio", "Météo NOAA Weather Radio", "NOAA-Wetterfunk", "Radio meteo NOAA"), "NFM")
WX_CA = ("162,400 – 162,550 MHz", tr("Weatheradio Canada", "Radiométéo Canada", "Weatheradio Kanada", "Radio meteo Canadá"), "NFM")


def band(f, name, mode):
    return (f, name, mode)


ISS = ("145,800 MHz", tr("ISS (voice, SSTV)", "ISS (phonie, SSTV)", "ISS (Sprache, SSTV)", "ISS (voz, SSTV)"), "NFM")
APRS_R1 = ("144,800 MHz", "APRS", "NFM → direwolf")
APRS_R2 = ("144,390 MHz", "APRS", "NFM → direwolf")
SSB2_R1 = ("144,05 – 144,4 MHz", tr("2 m CW / SSB (call 144.300)", "2 m CW / SSB (appel 144,300)",
                                  "2 m CW / SSB (Anruf 144,300)", "2 m CW / SSB (llamada 144,300)"), "USB / CW")
FM2_R1 = ("145,2 – 145,8 MHz", tr("2 m FM, repeaters (145.6+)", "2 m FM, relais (145,6+)",
                                "2 m FM, Relais (145,6+)", "2 m FM, repetidores (145,6+)"), "NFM")
UHF70_R1 = ("430 – 440 MHz", tr("70 cm (repeaters, satellites)", "70 cm (relais, satellites)",
                               "70 cm (Relais, Satelliten)", "70 cm (repetidores, satélites)"), "NFM / USB")
SHF23 = ("1240 – 1300 MHz", "23 cm", "NFM / USB")

CB_CEPT = ("26,965 – 27,405 MHz", tr("CB, 40 ch. (ch. 19: 27.185)", "CB, 40 can. (canal 19 : 27,185)",
                                   "CB, 40 Kan. (Kanal 19: 27,185)", "CB, 40 can. (canal 19: 27,185)"), "AM / FM")
METEOR = ("137,1 / 137,9 MHz", tr("Meteor-M weather satellites", "Satellites météo Meteor-M",
                                "Meteor-M Wettersatelliten", "Satélites meteo Meteor-M"), "→ SatDump")
SONDES = ("400 – 406 MHz", tr("Weather radiosondes", "Radiosondes météo", "Wetter-Radiosonden",
                              "Radiosondas meteorológicas"), "→ auto_rx")
ISM_R1 = ("433,92 / 868,3 MHz", tr("ISM sensors (weather, remotes)", "Capteurs ISM (météo, télécom.)",
                          "ISM-Sensoren (Wetter, Fernbed.)", "Sensores ISM (meteo, mandos)"), "→ rtl_433")
ISM_R2 = ("315 / 433,92 MHz", ISM_R1[1], "→ rtl_433")
# Wireless M-Bus modes C and T (EN 13757-4): water, heat and heat-cost meters
METERS_R1 = ("868,95 MHz", tr("Water / heat meters (M-Bus)", "Compteurs eau / chaleur (M-Bus)",
                             "Wasser-/Wärmezähler (M-Bus)", "Contadores agua / calor (M-Bus)"), "→ rtl_433")
PMR446 = ("446,0 – 446,2 MHz", tr("PMR446 (walkie-talkies, 16 ch.)", "PMR446 (talkies, 16 canaux)",
                                "PMR446 (Funkgeräte, 16 Kanäle)", "PMR446 (walkies, 16 canales)"), "NFM")
LORA_R1 = ("868 / 869,525 MHz", tr("LoRa / Meshtastic", "LoRa / Meshtastic", "LoRa / Meshtastic", "LoRa / Meshtastic"), DIGITAL)
LORA_R2 = ("902 – 928 MHz", tr("LoRa / Meshtastic (906.875)", "LoRa / Meshtastic (906,875)",
                              "LoRa / Meshtastic (906,875)", "LoRa / Meshtastic (906,875)"), DIGITAL)
ADSB = ("1090 MHz", tr("ADS-B (aircraft)", "ADS-B (avions)", "ADS-B (Flugzeuge)", "ADS-B (aviones)"), "→ tar1090")

VOR = ("108 – 118 MHz", tr("VOR / ILS beacons", "Balises VOR / ILS", "VOR- / ILS-Funkfeuer", "Radiobalizas VOR / ILS"))
AIR = ("118 – 137 MHz", tr("Civil aviation, AM (121.5 emergency)", "Aviation civile, AM (121,5 urgence)",
                         "Zivilluftfahrt, AM (121,5 Notfall)", "Aviación civil, AM (121,5 emergencia)"))
ACARS_R1 = ("131,525 – 131,825 MHz", tr("ACARS → acarsdec", "ACARS → acarsdec", "ACARS → acarsdec", "ACARS → acarsdec"))
VDL2_R1 = ("136,725 – 136,975 MHz", tr("VDL2 → dumpvdl2", "VDL2 → dumpvdl2", "VDL2 → dumpvdl2", "VDL2 → dumpvdl2"))
MARINE = ("156 – 162 MHz", tr("Marine VHF, NFM (ch. 16: 156.800)", "VHF marine, NFM (canal 16 : 156,800)",
                            "Seefunk UKW, NFM (Kanal 16: 156,800)", "VHF marina, NFM (canal 16: 156,800)"))
AIS = ("161,975 / 162,025 MHz", tr("AIS (ships) → AIS-catcher", "AIS (navires) → AIS-catcher",
                                  "AIS (Schiffe) → AIS-catcher", "AIS (barcos) → AIS-catcher"))

BABY = ("40,66 – 40,70 MHz", tr("Baby monitors, remote controls", "Babyphones, télécommandes",
                                "Babyphones, Fernbedienungen", "Vigilabebés, mandos a distancia"))
PRO_LOW = ("68 – 87,5 MHz", tr("Professional radio, defence (low VHF)", "Radiocom pro, défense (VHF basse)",
                               "Betriebsfunk, Militär (VHF-Low)", "Radio profesional, defensa (VHF baja)"))
PRO_VHF1 = ("146 – 156 MHz", tr("Professional VHF (transport, ambulances)", "Radiocom pro VHF (transports, ambulances)",
                                "Betriebsfunk VHF (Verkehr, Rettung)", "Radio prof. VHF (transporte, ambulancias)"))
PRO_VHF2 = ("162 – 174 MHz", tr("Professional VHF, smart meters", "Radiocom pro VHF, télérelevé compteurs",
                                "Betriebsfunk VHF, Zählerfernablesung", "Radio prof. VHF, telelectura contadores"))
MIL = ("225 – 380 MHz", tr("Military aviation UHF", "Aviation militaire UHF", "Militärluftfahrt UHF", "Aviación militar UHF"))
PRO_UHF1 = ("410 – 430 MHz", tr("Professional UHF, private TETRA", "Radiocom pro UHF, réseaux privés TETRA",
                                "Betriebsfunk UHF, private TETRA-Netze", "Radio prof. UHF, redes TETRA privadas"))
PRO_UHF2 = ("440 – 446 MHz", tr("Professional UHF (security, construction)", "Radiocom pro UHF (sécurité, BTP)",
                                "Betriebsfunk UHF (Sicherheit, Bau)", "Radio prof. UHF (seguridad, obras)"))
PRO_UHF3 = ("446,2 – 470 MHz", tr("Professional UHF, public transport", "Radiocom pro UHF, transports urbains",
                                  "Betriebsfunk UHF, Nahverkehr", "Radio prof. UHF, transporte urbano"))
MOB700 = ("703 – 862 MHz", tr("Mobile network 4G / 5G (700, 800)", "Téléphonie mobile 4G / 5G (700, 800)",
                              "Mobilfunk 4G / 5G (700, 800)", "Telefonía móvil 4G / 5G (700, 800)"))
MOB900 = ("876 – 960 MHz", tr("Mobile network 900, GSM-R (railways)", "Téléphonie mobile 900, GSM-R (rail)",
                              "Mobilfunk 900, GSM-R (Bahn)", "Telefonía móvil 900, GSM-R (ferrocarril)"))
MOB1800 = ("1710 – 1880 MHz", tr("Mobile network 4G (1800)", "Téléphonie mobile 4G (1800)",
                                 "Mobilfunk 4G (1800)", "Telefonía móvil 4G (1800)"))
DECT = ("1880 – 1900 MHz", tr("DECT cordless phones", "Téléphones sans fil DECT",
                              "DECT-Schnurlostelefone", "Teléfonos inalámbricos DECT"))
EMERG_TETRA = ("380 – 400 MHz", tr("Police, fire, ambulance (TETRA)", "Police, pompiers, secours (TETRA)",
                                   "Polizei, Feuerwehr, Rettung (TETRA)", "Policía, bomberos, emergencias (TETRA)"))


def r1_ham(top=band("1,81 – 2,0 MHz", "160 m", "LSB / CW"), six="50 – 52 MHz",
           sixty=("5,3515 – 5,3665 MHz", "60 m", "USB / CW"), extra=()):
    return [(H, "ham"),
            top,
            band("3,5 – 3,8 MHz", "80 m", "LSB / CW"),
            sixty,
            band("7,0 – 7,2 MHz", "40 m", "LSB / CW"),
            band("14,0 – 14,35 MHz", "20 m", "USB / CW"),
            band("21,0 – 21,45 MHz", "15 m", "USB / CW"),
            band("28,0 – 29,7 MHz", "10 m", "USB / FM"),
            band(six, "6 m", "USB / NFM"),
            *extra,
            SSB2_R1, APRS_R1, FM2_R1, ISS, UHF70_R1, SHF23]


R1_BROADCAST = [(H, "broadcast"), LW, MW_R1, SW_R1, FM_R1, DAB]
R1_MISC = [(H, "misc"), CB_CEPT, METEOR, SONDES, ISM_R1, PMR446, LORA_R1, METERS_R1, ADSB]
R1_MONITOR = [VOR, AIR, ACARS_R1, VDL2_R1, MARINE, AIS]


def note(t):
    return (NOTE, t)


REGIONS = {}

# ----------------------------------------------------------------- France
REGIONS["fr"] = dict(
    left=R1_BROADCAST + [None] + r1_ham(top=band("1,81 – 1,85 MHz", "160 m", "LSB / CW")) + [None] + R1_MISC,
    right=[(H, "tolerated"), *R1_MONITOR, None, (H, "forbidden"),
           BABY, PRO_LOW, PRO_VHF1, PRO_VHF2, MIL,
           ("380 – 400 MHz", tr("Police, fire, EMS (INPT network)", "Police, gendarmerie, pompiers, SAMU (INPT)",
                                "Polizei, Feuerwehr, Rettung (INPT)", "Policía, bomberos, emergencias (INPT)")),
           PRO_UHF1, PRO_UHF2, PRO_UHF3,
           ("466,0 – 466,25 MHz", tr("e*Message pagers (POCSAG)", "Pagers e*Message (POCSAG)",
                                     "e*Message-Pager (POCSAG)", "Buscas e*Message (POCSAG)")),
           MOB700, MOB900, MOB1800, DECT, None, ("", PRIVATE)],
)

# ----------------------------------------------------------------- United Kingdom
REGIONS["uk"] = dict(
    left=[(H, "broadcast"),
          ("148,5 – 283,5 kHz", tr("Long wave (BBC R4 closed 2026)", "Grandes ondes (BBC R4 arrêtée)",
                                   "Langwelle (BBC R4 2026 aus)", "Onda larga (BBC R4 cerrada)"), "AM"),
          MW_R1, SW_R1, FM_R1, DAB, None]
    + r1_ham(sixty=("5,2585 – 5,4065 MHz", tr("60 m (segmented)", "60 m (segments)", "60 m (Segmente)", "60 m (segmentos)"), "USB / CW"),
             extra=[band("70,0 – 70,5 MHz", "4 m", "FM / USB")])
    + [None, (H, "misc"),
       ("27,60125 – 27,99125 MHz", tr("UK CB, 40 ch. (19: 27.78125)", "CB UK, 40 can. (19 : 27,78125)",
                                      "UK-CB, 40 Kan. (19: 27,78125)", "CB UK, 40 can. (19: 27,78125)"), "FM"),
       ("26,965 – 27,405 MHz", tr("CB, CEPT 40 ch.", "CB, CEPT 40 canaux", "CB, CEPT 40 Kanäle", "CB, CEPT 40 canales"), "FM / AM"),
       METEOR, SONDES, ISM_R1, PMR446, LORA_R1, METERS_R1, ADSB],
    right=[(H, "grey"), *R1_MONITOR, None, (H, "forbidden"),
           BABY, PRO_LOW, PRO_VHF1,
           PRO_VHF2, MIL,
           ("380 – 400 MHz", tr("Police, fire, ambulance (Airwave)", "Police, pompiers, ambulances (Airwave)",
                                "Polizei, Feuerwehr, Rettung (Airwave)", "Policía, bomberos, ambul. (Airwave)")),
           PRO_UHF1, PRO_UHF2, PRO_UHF3, MOB700, MOB900, MOB1800, DECT, None, ("", PRIVATE),
           note(tr("UK: intercepting messages not meant for you is an offence",
                   "R.-U. : intercepter un message non destiné est un délit",
                   "UK: Abhören fremder Nachrichten ist strafbar (WTA s.48)",
                   "R. Unido: interceptar mensajes ajenos es delito"))],
)

# ----------------------------------------------------------------- Germany
REGIONS["de"] = dict(
    left=R1_BROADCAST + [None] + r1_ham() + [None, (H, "misc"),
        ("26,565 – 27,405 MHz", tr("CB, 80 ch. (ch. 19: 27.185)", "CB, 80 canaux (19 : 27,185)",
                                   "CB, 80 Kanäle (19: 27,185)", "CB, 80 canales (19: 27,185)"), "FM / AM"),
        METEOR, SONDES, ISM_R1, PMR446, LORA_R1, METERS_R1, ADSB],
    right=[(H, "grey"), *R1_MONITOR, None, (H, "forbidden"),
           BABY,
           ("74,215 – 77,475 MHz", tr("BOS analogue 4 m, lower (emergency)", "BOS analogique 4 m bas (secours)",
                                      "BOS analog 4-m-Band (unten)", "BOS analógico 4 m bajo (emergencias)")),
           ("84,015 – 87,255 MHz", tr("BOS analogue 4 m, upper (emergency)", "BOS analogique 4 m haut (secours)",
                                      "BOS analog 4-m-Band (oben)", "BOS analógico 4 m alto (emergencias)")),
           PRO_VHF1,
           ("165,21 – 173,98 MHz", tr("BOS analogue 2 m, alarm pagers", "BOS analogique 2 m, bips d'alerte",
                                      "BOS analog 2-m-Band, Alarmierung", "BOS analógico 2 m, buscas de alarma")),
           MIL,
           ("380 – 400 MHz", tr("BOS digital radio (TETRA)", "Radio numérique BOS (TETRA)",
                                "BOS-Digitalfunk (TETRA)", "Radio digital BOS (TETRA)")),
           PRO_UHF1, PRO_UHF2, PRO_UHF3,
           ("465,97 – 466,23 MHz", tr("e*Message pagers (POCSAG)", "Pagers e*Message (POCSAG)",
                                      "e*Message-Pager (POCSAG)", "Buscas e*Message (POCSAG)")),
           MOB700, MOB900, MOB1800, DECT, None, ("", PRIVATE),
           note(tr("Germany: listening to messages not for you is banned",
                   "Allemagne : écouter ce qui ne vous est pas destiné est interdit",
                   "Abhören fremder Nachrichten verboten (§ 5 TDDDG)",
                   "Alemania: prohibido escuchar mensajes ajenos"))],
)

# ----------------------------------------------------------------- Spain
REGIONS["es"] = dict(
    left=R1_BROADCAST + [None]
    + r1_ham(top=("1,81 – 1,85 MHz", tr("160 m (1.85–2.0: temporary)", "160 m (1,85–2,0 : temporaire)",
                                        "160 m (1,85–2,0: befristet)", "160 m (1,85–2,0: temporal)"), "LSB / CW"))
    + [None] + R1_MISC,
    right=[(H, "tolerated"), *R1_MONITOR, None, (H, "forbidden"),
           BABY, PRO_LOW, PRO_VHF1, PRO_VHF2, MIL,
           ("380 – 400 MHz", tr("Police, Guardia Civil (SIRDEE)", "Police, Guardia Civil (SIRDEE)",
                                "Polizei, Guardia Civil (SIRDEE)", "Policía, Guardia Civil (SIRDEE)")),
           PRO_UHF1, PRO_UHF2, PRO_UHF3, MOB700, MOB900, MOB1800, DECT, None, ("", PRIVATE)],
)

# ----------------------------------------------------------------- Other Europe (generic Region 1)
REGIONS["eu"] = dict(
    left=R1_BROADCAST + [None] + r1_ham() + [None] + R1_MISC,
    right=[(H, "tolerated"), *R1_MONITOR, None, (H, "forbidden"),
           BABY, PRO_LOW, PRO_VHF1, PRO_VHF2, MIL, EMERG_TETRA,
           PRO_UHF1, PRO_UHF2, PRO_UHF3, MOB700, MOB900, MOB1800, DECT, None, ("", PRIVATE),
           note(tr("Rules differ by country: check your national law",
                   "Les règles varient selon le pays : vérifiez la loi",
                   "Regeln je nach Land verschieden: Gesetz prüfen",
                   "Las normas varían según el país: consulte la ley"))],
)

# ----------------------------------------------------------------- USA / Canada (ITU Region 2)
def r2_ham(sixty, onefive, seventy):
    return [(H, "ham"),
            band("1,8 – 2,0 MHz", "160 m", "LSB / CW"),
            band("3,5 – 4,0 MHz", "80 / 75 m", "LSB / CW"),
            sixty,
            band("7,0 – 7,3 MHz", "40 m", "LSB / CW"),
            band("14,0 – 14,35 MHz", "20 m", "USB / CW"),
            band("21,0 – 21,45 MHz", "15 m", "USB / CW"),
            band("28,0 – 29,7 MHz", "10 m", "USB / FM"),
            band("50 – 54 MHz", "6 m", "USB / NFM"),
            ("144,1 – 144,275 MHz", tr("2 m CW / SSB (call 144.200)", "2 m CW / SSB (appel 144,200)",
                                       "2 m CW / SSB (Anruf 144,200)", "2 m CW / SSB (llamada 144,200)"), "USB / CW"),
            APRS_R2,
            ("145,1 – 147,4 MHz", tr("2 m FM, repeaters (call 146.52)", "2 m FM, relais (appel 146,52)",
                                     "2 m FM, Relais (Anruf 146,52)", "2 m FM, repet. (llam. 146,52)"), "NFM"),
            ISS, onefive, seventy, SHF23]


CB_US = ("26,965 – 27,405 MHz", tr("CB (9 emergency, 19 truckers)", "CB (9 urgence, 19 routiers)",
                                   "CB (9 Notruf, 19 Trucker)", "CB (9 emergencia, 19 camiones)"), "AM / SSB")
FRS = ("462,55 – 467,72 MHz", tr("FRS / GMRS (walkie-talkies)", "FRS / GMRS (talkies)",
                                 "FRS / GMRS (Funkgeräte)", "FRS / GMRS (walkies)"), "NFM")
ADSB_US = ("1090 / 978 MHz", tr("ADS-B / UAT (aircraft)", "ADS-B / UAT (avions)", "ADS-B / UAT (Flugzeuge)",
                                "ADS-B / UAT (aviones)"), "→ tar1090")
ACARS_R2 = ("129,125 – 131,725 MHz", tr("ACARS, main 131.550 → acarsdec", "ACARS, principal 131,550 → acarsdec",
                                         "ACARS, Haupt 131,550 → acarsdec", "ACARS, principal 131,550 → acarsdec"))
VDL2_R2 = ("136,650 – 136,975 MHz", VDL2_R1[1])
CELL = ("824 – 849 / 869 – 894", tr("Cellular 850 (scanners blocked)", "Cellulaire 850 (bloqué sur scanners)",
                                    "Mobilfunk 850 (in Scannern gesperrt)", "Celular 850 (bloqueado en escáneres)"))
# 769-775 / 799-805 MHz (700 MHz public safety) are left out on purpose
MOB_R2_LOW = ("617 – 768 / 776 – 798", tr("Mobile 600 / 700 (4G, 5G)", "Mobile 600 / 700 (4G, 5G)",
                                  "Mobilfunk 600 / 700 (4G, 5G)", "Móvil 600 / 700 (4G, 5G)"))
MOB_R2_HIGH = ("1710 – 2200 MHz", tr("Mobile AWS / PCS (4G, 5G)", "Mobile AWS / PCS (4G, 5G)",
                                     "Mobilfunk AWS / PCS (4G, 5G)", "Móvil AWS / PCS (4G, 5G)"))
DECT6 = ("1920 – 1930 MHz", tr("DECT 6.0 cordless phones", "Téléphones sans fil DECT 6.0",
                               "DECT-6.0-Schnurlostelefone", "Teléfonos inalámbricos DECT 6.0"))
PAGING = ("929 – 932 MHz", tr("Pagers (message content)", "Pagers (contenu des messages)",
                              "Pager (Nachrichteninhalt)", "Buscas (contenido de mensajes)"))
ENCRYPTED = ("", tr("Encrypted public safety (P25): never decrypt", "Secours chiffrés (P25) : ne pas déchiffrer",
                    "Verschlüsselter BOS-Funk (P25): nie entschlüsseln", "Emergencias cifradas (P25): no descifrar"))

REGIONS["us"] = dict(
    left=[(H, "broadcast"), MW_R2, SW_R2, FM_R2, WX_US, None]
    + r2_ham(sixty=("5,3305 – 5,4035 MHz", tr("60 m (band + 4 channels)", "60 m (bande + 4 canaux)",
                                              "60 m (Band + 4 Kanäle)", "60 m (banda + 4 canales)"), "USB / CW"),
             onefive=("222 – 225 MHz", tr("1.25 m", "1,25 m", "1,25 m", "1,25 m"), "NFM"),
             seventy=("420 – 450 MHz", tr("70 cm (call 446.000)", "70 cm (appel 446,000)", "70 cm (Anruf 446,000)",
                                          "70 cm (llamada 446,000)"), "NFM / USB"))
    + [None, (H, "misc"), CB_US, FRS,
       ("151,82 – 154,60 MHz", tr("MURS (5 channels)", "MURS (5 canaux)", "MURS (5 Kanäle)", "MURS (5 canales)"), "NFM"),
       METEOR, SONDES, ISM_R2, LORA_R2, ADSB_US],
    right=[(H, "monitor_us"), VOR, AIR, ACARS_R2, VDL2_R2, MARINE, AIS,
           ("160,11 – 161,565 MHz", tr("Railroads (AAR channels)", "Chemins de fer (canaux AAR)",
                                       "Eisenbahn (AAR-Kanäle)", "Ferrocarriles (canales AAR)")),
           ("150 – 174 / 450 – 470", tr("Public safety, business (analog, P25)", "Secours, entreprises (analogique, P25)",
                                        "BOS, Betriebsfunk (analog, P25)", "Emergencias, empresas (analóg., P25)")),
           ("769 – 775 / 851 – 869", tr("Public safety 700 / 800 (trunked)", "Secours 700 / 800 (trunking)",
                                        "BOS 700 / 800 (Bündelfunk)", "Emergencias 700 / 800 (trunking)")),
           None, (H, "protected"),
           ("43 – 50 MHz", tr("Old cordless phones, baby monitors", "Anciens téléphones sans fil, babyphones",
                              "Alte Schnurlostelefone, Babyphones", "Teléfonos inalámbricos viejos, vigilabeb.")),
           MOB_R2_LOW, CELL, PAGING, MOB_R2_HIGH, DECT6, None, ENCRYPTED,
           note(tr("Some states restrict scanners in vehicles",
                   "Certains États limitent les scanners en voiture",
                   "Manche Staaten beschränken Scanner im Auto",
                   "Algunos estados limitan escáneres en vehículos"))],
)

REGIONS["ca"] = dict(
    left=[(H, "broadcast"), MW_R2, SW_R2, FM_R2, WX_CA, None]
    + r2_ham(sixty=("5,3305 – 5,4035 MHz", tr("60 m (band + 4 channels)", "60 m (bande + 4 canaux)",
                                              "60 m (Band + 4 Kanäle)", "60 m (banda + 4 canales)"), "USB / CW"),
             onefive=("219 – 225 MHz", tr("1.25 m (219–220, 222–225)", "1,25 m (219–220, 222–225)",
                                          "1,25 m (219–220, 222–225)", "1,25 m (219–220, 222–225)"), "NFM"),
             seventy=("430 – 450 MHz", tr("70 cm (repeaters, satellites)", "70 cm (relais, satellites)",
                                          "70 cm (Relais, Satelliten)", "70 cm (repetidores, satélites)"), "NFM / USB"))
    + [None, (H, "misc"), CB_US,
       ("462,55 – 467,72 MHz", tr("FRS (licence-free walkies)", "FRS (talkies sans licence)",
                                  "FRS (lizenzfreie Funkgeräte)", "FRS (walkies sin licencia)"), "NFM"),
       METEOR, SONDES, ISM_R2, LORA_R2, ADSB],
    right=[(H, "monitor_ca"), VOR, AIR, ACARS_R2, VDL2_R2, MARINE, AIS,
           None, (H, "protected"),
           MOB_R2_LOW,
           ("824 – 849 / 869 – 894", tr("Cellular 850 (Criminal Code 184.5)", "Cellulaire 850 (Code criminel 184.5)",
                                        "Mobilfunk 850 (Strafgesetzbuch 184.5)", "Celular 850 (Código Penal 184.5)")),
           PAGING, MOB_R2_HIGH, DECT6, None, ENCRYPTED, ("", PRIVATE),
           note(tr("Canada: never divulge or use what you hear (s. 9)",
                   "Canada : ne rien divulguer ni utiliser (art. 9)",
                   "Kanada: nichts weitergeben oder nutzen (§ 9)",
                   "Canadá: no divulgar ni usar lo oído (art. 9)"))],
)


# ----------------------------------------------------------------- rendering
def text(value, lang):
    return value[lang] if isinstance(value, dict) else value


def freq(value, lang):
    return value.replace(",", ".") if lang == "en" else value


def row(item, cols, lang, where):
    """Returns (plain text, markup) for one line."""
    if item is None:
        return "", ""
    if item[0] == H:
        label = HEAD[item[1]][lang]
        check(len(label) <= sum(cols), "header too long: %r (%s)" % (label, where))
        return label, "<b>%s</b>" % escape(label)
    if item[0] == NOTE:
        label = text(item[1], lang)
        check(len(label) <= sum(cols), "note too long: %r (%s)" % (label, where))
        return label, "<i>%s</i>" % escape(label)
    if item[0] == "":
        label = text(item[1], lang)
        check(len(label) <= sum(cols), "line too long: %r (%s)" % (label, where))
        return label, escape(label)
    vals = [freq(item[0], lang)] + [text(v, lang) for v in item[1:]]
    vals += [""] * (len(cols) - len(vals))
    for i, (v, w) in enumerate(zip(vals, cols)):
        limit = w if i < len(cols) - 1 else w + 2
        check(len(v) < limit, "%d chars, max %d: %r (%s)" % (len(v), limit - 1, v, where))
    plain = "".join(v.ljust(w) for v, w in zip(vals, cols)).rstrip()
    return plain, escape(plain)


def build(region, lang):
    spec = REGIONS[region]
    where = "%s/%s" % (region, lang)
    left = [row(i, LCOLS, lang, where) for i in spec["left"]]
    right = [row(i, RCOLS, lang, where) for i in spec["right"]]
    n = max(len(left), len(right))
    check(n + 2 <= MAX_LINES, "%s: %d lines, max %d" % (where, n + 2, MAX_LINES))
    left += [("", "")] * (n - len(left))
    right += [("", "")] * (n - len(right))
    width = sum(LCOLS)
    title = "%s — %s" % (SDR_FREQ[lang], TITLE[region][lang])
    lines = ["<b>%s</b>" % escape(title), ""]
    for (lt, lm), (_, rm) in zip(left, right):
        lines.append((lm + " " * (width - len(lt)) + GAP + rm).rstrip())
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sheets = {(r, l): build(r, l) for r in REGIONS for l in LANGS}
    if ERRORS:
        raise SystemExit("\n".join(sorted(set(ERRORS))))
    for region in REGIONS:
        d = OUT / region
        d.mkdir(parents=True, exist_ok=True)
        for lang in LANGS:
            (d / ("%s.txt" % lang)).write_text(sheets[region, lang])
    print("wrote %d regions x %d languages to %s" % (len(REGIONS), len(LANGS), OUT))
