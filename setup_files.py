#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Collection of scripts for administration of group-wise assignment submissions via the Moodle system - Initial Setup
Natalie Clarius <clarius@informatik.uni-tuebingen.de>
University of Tübingen, Department of Computer Science, 2020
"""

import os, json, csv

def parse_config():
    global times, tutors
    with open("config.txt") as f:
        for line in f.readlines():
            setting = line.strip().split("#")[0]
            if setting:
                key, val = tuple(setting.split(" = "))
                globals()[key] = eval(val)
    for var, val in globals().items():
        if var.startswith("tut_"):
            nr = var[4]
            first_name, last_name, time = tuple(val)
            tut_name = ("Übung " + nr + ": " + time + " (" + first_name + " " + last_name + ")").replace(" ( )", "")
            times[nr] = tut_name
            if first_name and first_name not in tutors:
                tutors.append(first_name)

def load_files():
    global parts, teams, tuts
    print("Dateien werden geladen ...\n")
    if os.path.isfile("participants.json"):
        with open("participants.json", encoding="utf8") as fin:
            parts = json.load(fin)
    if os.path.isfile("teams.json"):
        with open("teams.json", encoding="utf8") as fin:
            teams = json.load(fin)
    if os.path.isfile("tutorials.json"):
        with open("tutorials.json", encoding="utf8") as fin:
            tuts = json.load(fin)

def save_files():
    global parts, teams, tuts
    # dump data into json files
    print("Dateien werden gespeichert ...\n")
    with open("teams.json", "w", encoding="utf8") as fout:
        json.dump(teams, fout, indent=2, sort_keys=True, ensure_ascii=False)
    with open("participants.json", "w", encoding="utf8") as fout:
        json.dump(parts, fout, indent=2, sort_keys=True, ensure_ascii=False)
    with open("tutorials.json", "w", encoding="utf8") as fout:
        json.dump(tuts, fout, indent=2, sort_keys=True, ensure_ascii=False)

def setup_participants():
    global parts
    print("Teilnehmerliste wird aufgesetzt ...\n")
    with open("participants.csv", encoding="utf-8-sig") as fin:
        reader = csv.DictReader(fin, delimiter=",")
        # add entries for participants
        for row in reader:
            first_name = row["Vorname"]
            last_name = row["Nachname"]
            matr = row["ID-Nummer"]
            email = row["E-Mail-Adresse"]
            full_name = first_name + " " + last_name
            if full_name not in parts:
                parts[full_name] = [first_name, last_name, matr, email, "", "", ""]

def setup_tutorials():
    global parts, tuts, teams
    print("Übungsterminliste wird aufgesetzt ...\n")

    with open("tutorial_choice.csv", encoding="utf-8-sig") as fin:
        reader = csv.DictReader(fin, delimiter="\t")
        # add tutorial field for participants
        for row in reader:
            name = row["Nachname"] + " " + row["Vorname"]
            tutorial = row["Gruppe"]
            if name not in parts:
                continue
            if not tutorial:
                tutorial = "Übung 0: zu keinem Übungstermin angemeldet"
            parts[name][4] = tutorial
    # initialize tutorial entries
    tuts = {tut: [] for tut in times.values()}

def setup_teams():
    global parts, tuts, teams
    print("Übungsteamliste wird aufgesetzt ...\n")
    with open("team_choice.csv", encoding="utf-8-sig") as fin:
        reader = csv.DictReader(fin, delimiter="\t")
        # add entries for teams
        for row in reader:
            name = row["Nachname"] + " " + row["Vorname"]
            team = row["Gruppe"]
            if name not in parts:
                continue
            if not team:
                team = "000"
            if not team[-2].isdigit():
                team = team[:-1] + "0" + team[-1:]
            if not team[-3].isdigit():
                team = team[:-2] + "0" + team[-2:]
            team_nr = team[-3:]
            parts[name][5] = team_nr
            if team_nr not in teams:
                teams[team_nr] = ["", []]
            if name not in teams[team_nr][1]:
                teams[team_nr][1].append(name)
        # update partcipant entry with full team name
        for name in parts:
            team_nr = parts[name][5]
            if not team_nr:
                continue
            if team_nr != "000":
                team_name = "Team " + team_nr + " " + "(" + "/".join(teams[team_nr][1]) + ")"
            else:
                team_name = "Team 000: zu keinem Übungsteam angemeldet"
            parts[name][5] = team_name
        # add full team names to tutorials
        for team_nr in teams:
            member_tutorials = [parts[member][4] for member in teams[team_nr][1]
                         if parts[member][4] and "Übung 0" not in parts[member][4]]
            if member_tutorials and len(set(member_tutorials)) == 1:
                team_tutorial = member_tutorials[0]
            else:
                team_tutorial = "Übung 0: zu keinem Übungstermin angemeldet"
            team_name = "Team " + team_nr + " " + "(" + "/".join(sorted(teams[team_nr][1])) + ")"
            teams[team_nr][0] = team_tutorial
            if team_name not in tuts[team_tutorial]:
                tuts[team_tutorial].append(team_name)

if __name__ == "__main__":
    parts, teams, tuts, times, tutors = dict(), dict(), dict(), dict(), list()
    parse_config()
    load_files()
    setup_participants()
    setup_tutorials()
    setup_teams()
    save_files()
    print("Fertig\n")
