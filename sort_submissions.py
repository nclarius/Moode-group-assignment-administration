#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Collection of scripts for administration of group-wise assignment submissions via the Moodle system - Sort submissions
Natalie Clarius <clarius@informatik.uni-tuebingen.de>
University of Tübingen, Department of Computer Science, 2020
"""


import os
from os import path
from os.path import join
import csv
import json
import shutil
import zipfile
import subprocess


# helper functions

def print_success(msg):
    """Print a message in green."""
    print('\033[92m' + msg + '\033[0m')

def print_warning(msg):
    """Print a message in yellow."""
    print('\033[93m' + msg + '\033[0m')

def ascii(entry):
    """Transliterate eszett and umlaute into ASCII characters."""
    return entry.replace("ß", "ss"). \
        replace("Ä", "Ae").replace("Ö", "Oe").replace("Ü", "Ue"). \
        replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")

def noblank(members):
    """Remove blanks from Moodle directory name."""
    return "_".join(["-".join([name for name in member.split(" ")]) for member in members])

def infix(string, prefix, suffix):
    """Extract a substring between a prefix and a suffix."""
    start = string.index(prefix)+len(prefix) if prefix and prefix in string else 0
    end = string.index(suffix) if suffix and suffix in string else -1
    return string[start:end]

def und(strlist):
    """Concatenate a list of strings with ',' and 'und'."""
    return " und ".join([", ".join(strlist[:-1])] + [strlist[-1]]) \
        if len(strlist) > 1 else (strlist[0] if len(strlist) > 0 else "")

if __name__ == "__main__":
    # set initial variables from config file
    tutor, nr_ex, sort, feedback, table, printout_sheet, printout_subms, subms_all, redistribute, tutors, tutorials = \
        "", 0, True, True, True, False, False, True, True, list(), dict()
    with open("config.txt") as f:
        for line in f.readlines():
            setting = line.strip().split("#")[0]
            if setting:
                key, val = tuple(setting.split(" = "))
                globals()[key] = eval(val)
    for tut_nr in range(6):
        var = "tut_" + str(tut_nr)
        val = globals()[var]
        tutor_name = val[0]
        if not tutor_name:
            tutor_name = "verwaist"
        if tutor_name not in tutors:
            tutors.append(tutor_name)
        tutorials[str(tut_nr)] = tutor_name
    tutors_ = tutors[1:]
    to_extract = tutors if subms_all else [tutor]
    nr_ex = str(nr_ex).zfill(2)

    # print settings
    print("Ababen sortieren\n")
    settings = [
        ("Tutor", tutor),
        ("Übungsblatt-Nr.", nr_ex),
        ("Abgaben in Tutorenordner sortieren",          sort),
        ("Ordner für die Feedbackdateien generieren",   feedback),
        ("Tabelle für die Punkteeintragung generieren", table),
        ("Aufgabenblatt ausdrucken",                    printout_sheet),
        ("Aufgaben ausdrucken",                         printout_subms),
        ("Abgaben von allen Tutoren extrahieren", subms_all),
        ("Abgaben gleichmäßig auf Tutoren verteilen",   redistribute)
    ]
    max_len_label = max([len(tpl[0]) for tpl in settings])
    frmt = "{0:" + str(max_len_label) + "}   {1}"
    print("Gesetzte Einstellungen:")
    print(frmt.format(settings[0][0], settings[0][1]))
    for label, var in settings[1:]:
        print(frmt.format(label, ("✓" if var else "🗙") if type(var) == bool else var))
    print()

    # constant paths
    dir_exs = join(path.relpath(".."), "Übungsblätter")
    json_partis = "Teilnehmer.json"
    json_teams = "Teams.json"
    json_tutorials = "Tutorials.json"

    # exercise-wise paths
    dir_ex = join(dir_exs, "Blatt_" + nr_ex)
    dir_handins = join(dir_ex, "Einreichungen")
    zip_handins = join(dir_ex, "Einreichungen.zip")
    file_correctors = join(dir_ex, "Einreichungen.csv")
    dir_sorted = join(dir_ex, "Abgaben")
    zip_sorted = join(dir_ex, "Abgaben.zip")
    file_grades_ = join(dir_ex, "Bewertung.csv")

    # tutor-wise paths
    dir_subm = {tutor: join(dir_ex, "Abgaben" + "_" + tutor) for tutor in tutors}
    dir_corr = {tutor: join(dir_ex, "Korrekturen" + "_" + tutor) for tutor in tutors}
    dir_feedb = {tutor: join(dir_ex, "Feedbacks" + "_" + tutor) for tutor in tutors}
    file_points = {tutor: join(dir_ex, "Punkte" + "_" + tutor + ".tsv") for tutor in tutors}

    # import student data
    with open(json_teams) as fin:
        teams = json.load(fin)

    if sort:
        # unzip handins into handins folder
        print("Abgaben werden entzippt...")
        with zipfile.ZipFile(zip_handins, "r") as zip:
            zip.extractall(dir_handins)

        # create submission folders
        print("Abgabeordner" + (" wird " if not subms_all else " werden ") + "erstellt...")
        for tutor in to_extract:
            if not path.exists(dir_subm[tutor]):
                os.mkdir(dir_subm[tutor])

    if feedback:
        # create correction feedback folders
        print("Korrekturordner" + (" wird " if not subms_all else " werden ") + "erstellt...")
        for tutor in to_extract:
            if not path.exists(dir_corr[tutor]):
                os.mkdir(dir_corr[tutor])
            if not path.exists(dir_feedb[tutor]):
                os.mkdir(dir_feedb[tutor])

    if sort:
        # assign submissions to tutors
        print("Abgaben werden zugeordnet...")
        processed = []  # teams already processed
        skipped = []  # submissions skipped
        subms = {tut: [] for tut in tutors}  # submissions as originally assinged to each tutor
        # traverse Moodle submission folders
        for subm in sorted([dirname for dirname in os.listdir(dir_handins) if not dirname.startswith("_")]):
            if not subm.startswith("Team"):
                skipped.append(subm)
                continue
            team_nr_ = infix(subm, "Team ", "-")
            team_nr = team_nr_.zfill(3)
            team_name = "Team " + team_nr + " (" + "/".join(teams[team_nr][1]) + ")"
            tutorial_nr = teams[team_nr][0][6] if team_nr in teams and teams[team_nr][0] else "0"  # look up group for team
            team_tutor = tutorials[tutorial_nr]  # look up tutor for team
            if team_name not in processed:
                subms[team_tutor].append(team_name)
                processed.append(team_name)
        if skipped:
            print("Warnung: " + str(len(skipped)) + " Abgabeordner sind keine Teams und wurden übesprungen")

        if redistribute:
            # redistribute submissions evenly among tutors
            print("Abgaben werden umverteilt...")
            # (It may look inefficient to traverse the submissions twice, once for the initial tutor assignment and once
            # for the actual copying after the redistribution process. But in terms of runtime, this solution is in fact
            # faster than the alternative of first unpacking all submissions into the original tutor folder, then
            # moving them to a different folder when there are too many elements in one, because performing a check on
            # a number of files is ligther than a harddrive writing process. And redistributing afterwards rather than
            # equally distributing on the fly is necessary in order to ensure that a maximum amount of submissions gets
            # assigned its initial tutor.)
            subms_ = {tutor: [] for tutor in tutors}  # submission distribution equalled out between tutors to be filled
            # compute differences in number of submissions between tutors
            cnt_subms = sum([len(val) for val in subms.values()])
            avg_subms = round(cnt_subms/len(tutors))
            num_subms = {tutor: len(subms[tutor]) for tutor in tutors_[::-1]}
            diff_subms = {tutor: num_subms[tutor]-avg_subms for tutor in tutors_[::-1]}
            # diff_subms["Natalie"] = round((num_subms["Natalie"]/2-avg_subms)*2)  # Natalie has 2 tutorials
            redistr = []  # temporary stack to store submissions to be moved
            for tutor, diff in diff_subms.items():
                if diff > 0:  # tutor has too many submissions -- remove some to the redistr pile
                    breakpoint = num_subms[tutor]-diff
                    subms_[tutor] += subms[tutor][:breakpoint]  # keep up-to-average submissions
                    redistr += subms[tutor][breakpoint:]        # put protuding submissions on redistr pile
            for tutor, diff in diff_subms.items():
                if diff <= 0:  # tutor has too few submissions -- add some from the redistr pile
                    breakpoint = -diff
                    subms_[tutor] += subms[tutor]               # keep original submissions
                    subms_[tutor] += redistr[:breakpoint]       # add protuding submssions from redistr pile
                    redistr = redistr[breakpoint:]              # decimate redistr pile
            if redistr:  # there are still subms left on the redistr pile -- reassign them to original tutor
                for team_name in redistr:
                    team_tutor = [tutor for tutor in tutors_ if team_name in subms[tutor]][0]
                    subms_[team_tutor].append(team_name)
                redistr = []
        else:  # no redistribution: distribution is same as original tutor assignment
            subms_ = subms
        correctors = {team_name: tutor for tutor in tutors_ for team_name in subms_[tutor]}  # inverse subms_ map

        # sort submissions into tutor folders
        print("Abgaben werden einsortiert...")
        processed = []  # teams already processed
        # traverse Moodle submission folders
        for subm in sorted([dirname for dirname in os.listdir(dir_handins)]):
            if not subm.startswith("Team"):
                continue
            team_nr_ = infix(subm, "Team ", "-")
            team_nr = team_nr_.zfill(3)
            team_name = "Team " + team_nr + " (" + "/".join(teams[team_nr][1]) + ")"
            members = teams[team_nr][1]
            tutorial_nr = teams[team_nr][0][6] if team_nr in teams and teams[team_nr][0] else "0"
            corrector = correctors[team_name]  # look up correcting tutor in inverted redistribution map
            if corrector in to_extract:  # submission is relevant
                if team_name not in processed:
                    file_src = os.listdir(join(dir_handins, subm))[0]  # subm. = first file in student's folder
                    file_dest = "T" + team_nr + "_" + "Ü" + tutorial_nr + "_" + noblank(members) + ".pdf"
                    src = join(dir_handins, subm, file_src)
                    dest = join(dir_subm[corrector], file_dest)
                    shutil.copy(src, dest)  # copy submission into submissions folder for tutor
                if feedback:  # create empty folder in feedbacks folder for tutor
                    if not path.exists(join(dir_feedb[corrector], subm)):
                        os.mkdir(join(dir_feedb[corrector], subm))
                if team_name not in processed:
                    subms[corrector].append(team_name)
                    processed.append(team_name)

        if subms_all:
            # save submissions and correctors into file
            with open(file_correctors, "w", encoding="utf-8") as fout:
                fout.write(",".join(["Team", "Übungsgruppe", "Korrektor"]) + "\n")
                for team_name in sorted(correctors):
                    team_nr = team_name[5:8]
                    group = teams[team_nr][0]
                    corrector = correctors[team_name]
                    fout.write(",".join([team_name, group, corrector]) + "\n")

    if table:
        # generate Punkte.tsv
        print("Bewertungstabelle" + (" wird " if not subms_all else "n werden ") + "erstellt...")

        for tutor in to_extract:
            # load existing teams from points and comments
            if path.exists(file_points[tutor]):
                with open(file_points[tutor]) as fin:
                    reader = csv.DictReader(fin, delimiter="\t")
                    points = {row["Team"]: float(row["Punkte"].replace(",", ".")) if row["Punkte"] else None
                              for row in reader}
                with open(file_points[tutor]) as fin:
                    reader = csv.DictReader(fin, delimiter="\t")
                    comments = {row["Team"]: row["Kommentar"] for row in reader}
                # add new teams to points and comments
                entries = [{"Team": team, "Punkte": str(points[team]).replace(".", ",") if points[team] is not None else "",
                                          "Kommentar": comments[team]}
                           for team in points]
                entries += [{"Team": team, "Punkte": "", "Kommentar": ""}
                            for team in set(subms_[tutor]) if team not in points]
            # collect teams for points and comments from submissions
            else:
                entries = [{"Team": team, "Punkte": "", "Kommentar": ""} for team in set(subms_[tutor])]

            # re-generate points table
            with open(file_points[tutor], "w", encoding="utf8") as fout:
                fieldnames = ["Team", "Punkte", "Kommentar"]
                writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter="\t")
                writer.writeheader()
                for entry in sorted(entries, key=lambda e: e["Team"]):
                    writer.writerow(entry)

    if sort:
        # delete redundant files and folders
        print("Obsolte Dateien werden entfernt...")
        if subms_all and not os.listdir(dir_subm["verwaist"]):
            shutil.rmtree(dir_subm["verwaist"])
            shutil.rmtree(dir_corr["verwaist"])
            shutil.rmtree(dir_feedb["verwaist"])
            os.remove(file_points["verwaist"])
            del dir_subm["verwaist"]
        shutil.rmtree(dir_handins)

    if subms_all:
        # zip sorted files
        print("Dateien werden gezippt...")
        if os.path.exists(zip_sorted):
            os.remove(zip_sorted)
        if os.path.exists(dir_sorted):
            shutil.rmtree(dir_sorted)
        else:
            os.mkdir(dir_sorted)
        for dir in dir_subm.values():
            shutil.copytree(dir, os.path.join(dir_sorted, os.path.basename(dir)))
            shutil.rmtree(dir)
        shutil.make_archive(dir_sorted, "zip", dir_sorted)
        shutil.rmtree(dir_sorted)

    if printout_sheet:
        # print exercise sheet
        print("Aufagebenblatt wird gedruckt...")
        file_exsh = join(dir_ex, "logik-blatt" + nr_ex + ".pdf")
        if tutor == "Natalie":
            print_command = "~/Dropbox/Code/Shell/duplex_print.sh " + file_exsh
        else:
            print_command = "lp " + file_exsh
        subprocess.run(print_command, shell=True)

    if printout_subms:
        # print submissions
        print("Abgaben werden gedruckt...")
        subms = [join(dir_subm[tutor], subm) for subm in os.listdir(dir_subm[tutor])]
        if tutor == "Natalie":
            print_command = "~/Dropbox/Code/Shell/duplex_print_serial.sh " + " ".join(subms)
        else:
            print_command = "lp " + " ".join(subms)
        subprocess.run(print_command, shell=True)

    print_success("Fertig")
