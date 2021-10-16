This repository is a collection of instructions and scripts to

- use the Moodle e-learning platform to create user groups for tutorials and teams, and let participants submit assignments using these groups (`setup_files.py`),

- automatically sort the submissions by tutor and teams (`sort_submissions.py`),
- easily enter points and corrections into the grading system (`sort_corrections.py`).

Natalie Clarius <clarius@informatik.uni-tuebingen.de>

University of Tübingen, Department of Computer Science, 2020



# Prerequisites

[Python](https://www.python.org/downloads/) (Version >= 3.9).



# Usage

Instructions and program output are currently only in German. If you are interested in an English translation, please contact me.



## Initiales Setup

- Diese Schritte sind einmalig zu Beginn der Veranstaltung durchzuführen.

- Gruppen aufsetzen:
  - Moodle > ‘Teilnehmer/innen’ > Einstellungsrad > ‘Gruppen’
  - Gruppen für Übungstermine anlegen: für jede Übungsgruppe: > ‘Gruppe anlegen’
    - ‘Gruppenname’: im Format “Übung 1: Montag 12-14 (Max Mustertutor)”
    - restliche Einstellungen lassen
  - Gruppen für Übungsteams anlegen: > ‘Gruppen automatisch anlegen’
    - ‘Namensschema’: Team @
    - ‘Kriterien für automatisches Erstellen’: ‘Anzahl von Gruppen’
    - ‘Anzahl von Gruppen oder Mitgliedern pro Gruppe’: ausreichende Anzahl an leeren Gruppen je nach Teilnehmerzahl und gewünschter Teamgröße plus etwas Puffer, z.B. bei 300 Teilnehmern und 3er-Teams etwa 110 Gruppen
    - ‘Grupenmitteilungen’: ‘Ja’
    - restliche Einstellungen lassen
  - Gruppierungen (Überkategorien von Gruppen) anlegen:
    - Reiter ‘Gruppierungen’ > zweimal ‘Gruppierung anlegen’ > eine Gruppierung namens “Übungstermine”, eine Gruppierung namens “Übungsteams”
    - Gruppierungsübersicht > Mitglieder-Icon in der ‘Bearbeiten’-Spalte für die jeweilige Gruppierung > zu Gruppierung “Übungstermine” die Gruppen “Übung x: …” hinzufügen, zu Gruppierung “Übungsteams” die Gruppen “Team xxx” hinzufügen
- Gruppenwahl anlegen:
  - Übungsterminwahl anlegen: Moodle > ‘Aktivität anlegen’ > ‘Gruppenwahl’
    - ‘Name der Gruppenwahl’: “Übungsterminwahl”
    - ‘Änderung der Wahl erlauben’: ‘Ja’
    - ‘Obergrenzen für Wahl erlauben’: ‘Aktivieren’
    - ‘Generelle Obergrenze’: gewünschte maximale Größe pro Übungstermin, z. B. 50
    - ‘Obergrenze für alle Gruppen anwenden’
    - ‘Gruppen’: Gruppierung ‘Übungstermine’ zu ‘Ausgewählte Gruppen’ hinzufügen, sodass die Gruppen “Übung x: …” zur Wahl stehen
    - ‘Wahl auf Zeitraum beschränken’: ggf. gewünschten Zeitraum setzen
    - restliche Einstellungen lassen
  - Übungsteamwahl anlegen: Moodle > ‘Aktivität anlegen’ > ‘Gruppenwahl’
    - ‘Name der Gruppenwahl’: “Übungsteamwahl”
    - ‘Änderung der Wahl erlauben’: ‘Ja’
    - ‘Obergrenzen für Wahl erlauben’: ‘Aktivieren’
    - ‘Generelle Obergrenze’: gewünschte maximale Größe pro Übungsteam, z. B. 3
    - ‘Obergrenze für alle Gruppen anwenden’
    - ‘Gruppen’: Gruppierung ‘Übungsteams’ zu ‘Ausgewählte Gruppen’ hinzufügen, sodass die Gruppen “Team xxx” zur Wahl stehen
    - ‘Wahl auf Zeitraum beschränken’: ggf. gewünschten Zeitraum setzen
    - ‘Voraussetzungen’ > ‘Voraussetzung hinzufügen’ > ‘Gruppierung’ > “Übungstermine”
    - restliche Einstellungen lassen
- Gruppenwahl durchführen, d.h. Teilnehmer sich in Übungstermine und Übungsteams eintragen lassen. Den Teilnehmern mitteilen, dass die Eintragung in einen Übungstermin zur Eintragung in ein Übungsteam zwingend notwendig ist, die Eintragung in ein Übungsteam zur Abgabe von Aufgaben zwingend notwendig ist, und alle Teilnehmer eines Teams zum selben Termin eingetragen sein sollen.
- Eintragungslisten runterladen:
  - Teilnehmerliste: Moodle > ‘Bewertungen’ > Reiter ‘Export’ > Reiter ‘Textdatei’ > ‘Herunterladen’, speichern als “Teilnehmer.csv”
  - Übungsterminwahl: Moodle > ‘Übungsterminwahl’ > ‘xxx Antworten anzeigen’ > ‘Im Text-Format herunterladen’, speichern als “Terminwahl.csv”
  - Übungsteamwahl: Moodle > ‘Übungsteamwahl’ > ‘xxx Antworten anzeigen’ > ‘Im Text-Format herunterladen’, speichern als “Teamwahl.csv”
  - Die Dateien müssen sich im selben Ordner wie diese Skriptsammlung befinden.
- Einstellungen setzen: ‘Verwaltung’ > ‘config.txt’:
  - Tutoriumstermine eintragen.
- ‘Verwaltung’ > ‘setup_files.py’ ausführen.
- Die erstellten Listen finden sich in den Dateien ‘Teilnehmer.json’, ‘Termine.json’ und ‘Teams.json’. Diese Dateien werden für die Sortierung der Abgaben und Korrekturen benötigt, sind aber menschenlesbar und lassen sich mit einem Texteditor öffnen.
- JSON-Dateien überprüfen und ggf. die Teilnehmer, die in keinem bzw. keinem Team-einheitlichen Übungstermin (“Übung 0”) oder in keinem Übungsteam (“Team 000”) eingetragen sind bitten, die Anmeldung nachzuholen bzw. zu korrigieren.
- Bei etwaigen Aktualisierungen Dateien neu runterladen und Skript neu ausführen.
- Alternativ können die JSON-Dateien auch manuell bearbeitet werden, um z.B. Übungsterminzuordnungen zu ändern. Es ist aber zu beachten, dass sämtliche Änderungen bei einer erneuten Ausführung des Skripts überschrieben werden.



## Wöchentliches Moodle-Aufgaben-Setup

- Diese Schritte sind für jedes Aufgabenblatt durchzuführen.

- Aufgabe anlegen:
  - Moodle > ‘Aktivität anlegen’ > ‘Aufgabe’
    - ‘Allgemeines’ > ‘Name der Aufgabe’ und ‘Zusätzliche Dateien’: wie gewünscht setzen
    - ‘Verfügbarkeit’ > ‘Abgabebeginn’, ‘Fälligkeitsdatum’, ‘Letzte Abgabemöglichkeit’ aktivieren und wie gewünscht setzen
    - ‘Abgabetypen’ > ‘Abgabetypen’: ‘Dateiabgabe’
    - ‘Abgabetypen’ > ‘Anzahl hochladbarer Dateien’, Maximale Dateigröße’, ‘Akzeptierte Dateitypen’ wie gewünscht setzen
    - ‘Feedback-Typen’ > ‘Feedback-Typen’: alle auswählen (wichtig!)
    - ‘Abgabeeinstellungen’ > ‘Versuche erneut bearbeitbar’: ‘Automatisch bis zum Bestehen’,
    - ‘Abgabeeinstellungen’ > ‘Maximal mögliche Versuche’: ‘Unbegrenzt
    - ‘Einstellungen für Gruppeneinreichungen’ > ‘Teilnehmer geben in Gruppen ab’: ‘Ja’ (wichtig!)
    - ‘Einstellungen für Gruppeneinreichungen’ > ’Gruppe notwendig, um etwas abgaben zu können’: ‘Ja’
    - ‘Einstellungen für Gruppeneinreichungen’ > ‘Berücksichtigte Gruppierung’: ‘’Übungsteams’ (wichtig!)
    - ‘Bewertung’ > ‘Bewertung’ wie gewünscht setzen
    - restliche Einstellungen lassen



## Wöchentliche Abgaben-Sortierung

- Diese Schritte sind für jedes Aufgabenblatt nach der Abgabe durchzuführen, wenn die Abgaben nach Tutoren und Gruppen sortiert werden sollen.

- 'sort_submissions.py' kann:

  - aus Moodle heruntergeladene Abgaben nach Tutoren sortieren, ausgeglichen verteilen, für einen Tutor filtern und mit systematischen Dateinamen speichern;
  - einen Ordner für die Feedbacks und eine einfache Punktetabelle generieren,
    die mit sort_corretions.py hinterher in Moodle-kompatible Formate umgewandelt werden können;
  - Aufgabenblatt und Abgaben ausdrucken.

- vorab von Moodle runterzuladen:
  - Moodle > Aufgabenblatt > ‘Alle Abgaben anzeigen’
  - \> unten Checkbox 'Abgaben in Verzeichnissen herunterladen' > oben Dropdown ‘Bewertungsvorgang’: ‘Alle Abgaben herunterladen’, speichern als Einreichungen.zip
  - (nur notwendig, wenn man später die Punkte über eine Tabelle auf Moodle hochladen will:) > oben Dropdown ‘Bewertungsvorgang’: ‘Bewertungstabelle herunterladen’, speichern als ‘Bewertung.zip’

- vorausgesetzte Dateistruktur:
  ```
  - Logik_SS20
    - Verwaltung
      - sort_submissions.py
      - Teilnehmer.json
      - Teams.json
      ...
    - Übungsblätter
      - Blatt_01
        - Einreichungen.zip         (von Moodle runtergeladenes ZIP mit allen Abgaben in einem Ordner pro Teilnehmer)
       (- Bewertung.csv             (von Moodle runtergeladene leere Bewertungstabelle)                              )
       (- logik-blatt01.pdf         (Aufgabenblatt)                                                                  )
      - Blatt_02
      ...
  ```

- Einstellungen setzen: ‘Verwaltung’ > ‘config.txt’ >
  - über ‘Vorname des Tutors’ und ‘Nummer des Übungsblatts’ setzen, was sortiert werden soll
  - über ‘Aktivierte Module für die Abgabensortierung’ setzen, welche Programmteile ausgeführt werden sollen
  - über ‘Einstellungen für die Abgabensortierung’ weitere Einstellungen setzen

- ‘sort_submissions.py’ ausführen.

- Danach können ggf. die Punkte und Feedbackkommentare in Punkte.tsv eingetragen und die Korrekturen erstellt werden, und im Anschluss sort_corrections.py ausgeführt werden.



## Wöchentliche Korrektur-Sortierung

- Diese Schritte sind für jedes Aufgabenblatt nach der Korrektur durchzuführen, wenn die Punkte und Korrekturen per Datei auf Moodle hochgeladen werden sollen.

- ‘sort_corrections.py’ kann:
  - Korrekturenscans aus einer konkatenierten PDF-Datei in die Korrekturen der einzelnen Teams aufsplitten;
  - Korrekturendateien in die Moodle-Feedback-Ordner aller Teammitglieder einsortieren und zippen, sodass dieser Ordner nur noch auf Moodle hochgeladen werden muss, um die Korrekturen für alle einzustellen;
  - Punkte und Feedback-Kommentare aus einem einfachen nach Teams aufgelösten und nach Übungsgruppen gefilterten TSV in die Moodle-Bewertungstabelle für alle Teammitglieder übertragen, sodass diese Tabelle nur noch auf Moodle hochgeladen werden muss, um die Punkte für alle einzutragen.
- vorausgesetzte Dateistruktur:
 ```
  - Logik_SS20
    - Verwaltung
       - sort_corrections.py
       -...
    - Übungsblätter
      - Blatt_01
        - Abgaben                     (mit sort_submissions.py generierter Abgabenordner)
        - Feedbacks                   (mit sort_submissions.py generierter Feedbackordner)
        - Bewertung.csv               (von Moodle runtergeladene leere Bewertungstabelle)
        - Punkte.tsv                  (mit sort_submissions.py generierte und dann ausgefüllte Punktetabelle)
        - Korrekturen                 (Ordner mit einzelnen Korrektur-PDFs aller Teams)
          - Team_001.pdf
          - Team_002.pdf
          - ...
        - Korrekturen.pdf             (PDF mit konkatenierten Korrekturen aller Teams)
        -...
      - Blatt_02
      ...

 ```
-
  - Bei Dateien im Blatt-Ordner zu beachten:
    - Dateien ‘Punkte.tsv ‘und ‘Bewertungen.csv’ nur notwendig, wenn die Punkte über Moodle als Bewertungstabelle hochgeladen werden anstatt von Hand auf Moodle eingetragen werden sollen.
    - Ordner ‘Feedbacks’ nur notwendig, wenn die Korrekturen über Moodle als ZIP hochgeladen werden anstatt von Hand auf Moodle eingestellt werden sollen. In diesem Fall ist entweder der Ordner Korrekturen oder die Datei ‘Korrekturen.pdf’ notwendig.
    - Dateien im Ordner ‘Korrekturen’ nur notwendig, wenn die Korrekturen in mehreren PDFs für jedes Teams einzeln liegen.
    - Datei ‘Korrekturen.pdf’ nur notwendig, wenn die Korrekturen in einem einzigen PDF für alle Teams konkateniert liegen.

  - Bei Dateien im Korrektur-Ordner zu beachten:
    - Alle Dateinamen müssen die dreistellige Teamnummer enthalten.

  - Bei Korrekturen.pdf zu beachten:
    - Die Datei muss die Scans aller Korrekturen in der Reihenfolge der Teammnummern enthalten. Es darf keine Korrektur fehlen, falsch (ein-)sortiert sein oder eine andere Seitenanzahl haben als die Abgabedatei.
    - Wenn bei ungerader Seitenzahl die leeren letzten Rückseiten mitgescannt wurden (üblicherweise bei Stapeleinzug), muss in ‘config.txt’ die Variable 'empty_backpages' auf 'True' gesetzt werden, andernfalls auf 'False'.

- Einstellungen setzen: ‘Verwaltung’ > ‘config.txt’ >
  - über ‘Vorname des Tutors’ und ‘Nummer des Übungsblatts’ setzen, was sortiert werden soll
  - über ‘Aktivierte Module für die Korrekturensortierung’ setzen, welche Programmteile ausgeführt werden sollen
  - über ‘Einstellungen für die Korrekturensortierung’ weitere Einstellungen setzen

- ‘sort_corrections.py’ ausführen.

- Nach Ausführung des Skripts müssen nur noch die generierten Dateien auf Moodle hochgeladen werden, um die Punkte und Korrekturen für alle Teilnehmer einzutragen:
  - Moodle > Aufgabenblatt > ‘Alle Abgaben anzeigen’ > ‘Bewertungsvorgang’
  - Punkte hochladen: \> 'Bewertungstabelle hochladen’ > ‘Bewertungen_Tutorname.csv' als Bewertungstabelle hochladen, Checkbox 'Update von Datensätzen zulassen...' auswählen, restliche Einstellungen lassen > bestätigen
  - Korrekturen hochladen: > ‘Mehrere Feedback-Dateien in einer ZIP-Datei hochladen’ > ‘Feedbacks.zip’ hochladen, bestätigen

