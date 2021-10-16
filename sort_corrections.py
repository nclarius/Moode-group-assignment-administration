#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Collection of scripts for administration of group-wise assignment submissions via the Moodle system - Sort corrections
Natalie Clarius <clarius@informatik.uni-tuebingen.de>
University of Tübingen, Department of Computer Science, 2020
"""


import os
from os import path
from os.path import join
import csv
import json
import shutil
import PyPDF2
import zipfile


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

def average(lst):
    """Compute the average of a list of values.
    :param lst: the list of values to compute the averages for
    :return: the average of the values in lst
    """
    return sum([entry for entry in lst if entry is not None])/len([entry for entry in lst if entry is not None])


if __name__ == "__main__":
    # set initial variables from config file
    tutor, nr_ex, split_corrections, sort_corrections, generate_table, corrs_all, empty_backpages, tutors, tutorials = \
        "", 0, True, True, True, True, True, list(), dict()
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
    to_extract = tutors if corrs_all else [tutor]
    nr_ex = str(nr_ex).zfill(2)

    # print settings
    print("Korrekturen sortieren\n")
    settings = [
        ("Tutor", tutor),
        ("Übungsblatt-Nr.", nr_ex),
        ("Konkatenierte Korrekturdatei splitten", split_corrections),
        ("Korrekturdateien einsortieren",         sort_corrections),
        ("Bewertungstabelle erstellen",           generate_table),
        ("Korrekturen von allen Tutoren extrahieren", corrs_all),
        ("Leere letzte Rückseiten",               empty_backpages)
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

    # exercise-wise paths
    dir_ex = join(dir_exs, "Blatt_" + nr_ex)
    dir_handins = join(dir_ex, "Einreichungen")
    zip_handins = join(dir_ex, "Einreichungen.zip")

    # tutor-wise paths
    dir_subm = {tutor: join(dir_ex, "Abgaben" + "_" + tutor) for tutor in to_extract}
    if "verwaist" in to_extract and not path.exists(dir_subm["verwaist"]):
        to_extract.remove("verwaist")
    dir_corr = {tutor: join(dir_ex, "Korrekturen" + "_" + tutor) for tutor in to_extract}
    file_corr = {tutor: join(dir_ex, "Korrekturen" + "_" + tutor + ".pdf") for tutor in to_extract}
    dir_feedb = {tutor: join(dir_ex, "Feedbacks" + "_" + tutor) for tutor in to_extract}
    dir_zip_feedb = join(dir_ex, "Feedbacks" + "_" + (tutor if not corrs_all else "alle"))
    zip_feedb = join(dir_ex, "Feedbacks" + "_" + (tutor if not corrs_all else "alle") + ".zip")
    file_points = {tutor: join(dir_ex, "Punkte" + "_" + tutor + ".tsv") for tutor in to_extract}
    file_grades = join(dir_ex, "Bewertungen" + "_" + (tutor if not corrs_all else "alle") + ".csv")
    file_grades_ = join(dir_ex, "Bewertung.csv")

    # import student data
    with open(json_teams) as fin:
        teams = json.load(fin)

    if split_corrections:
        print("Korrekturen werden extrahiert...")
        for tutor in to_extract:
            if not path.exists(file_corr[tutor]):
                continue

            # single feedback file to be split
            # (re-)create folder
            if not path.exists(dir_corr[tutor]):
                os.mkdir(dir_corr[tutor])
            corrs = PyPDF2.PdfFileReader(open(file_corr[tutor], "rb"))
            len_corrs = corrs.getNumPages()
            curr_page = 0
            pages_exceeded = False
            pages_subceeded = False
            # traverse submissions
            for subm in [file for file in sorted(os.listdir(dir_subm[tutor])) if file.endswith(".pdf")]:
                # get submission file data
                file_subm = join(dir_subm[tutor], subm)  # original submission
                length = PyPDF2.PdfFileReader(open(file_subm, "rb"), strict=False).getNumPages()
                # split out feedback file
                corr = PyPDF2.PdfFileWriter()
                for p in range(curr_page, curr_page + length):
                    if p >= len_corrs:
                        pages_exceeded = True
                    if not pages_exceeded:
                        corr.addPage(corrs.getPage(p))
                # insert feedback file into corrections folder
                file_dest = join(dir_corr[tutor], subm)
                with open(file_dest, "wb") as fout:
                    corr.write(fout)
                # advance bookmark in feedbacks file
                curr_page += length
                if empty_backpages and length % 2 == 1:
                    curr_page += 1  # skip empty last back page for uneven page numbers
            if (curr_page+1) < len_corrs:
                pages_subceeded = True
            if pages_exceeded:
                print_warning("Warnung: Mehr Seiten in den Abgabe-PDFs als im Korrektur-PDF; "
                              "bitte Korrekturdateien überprüfen")
            if pages_subceeded:
                print_warning("Warnung: Weniger Seiten in den Abgabe-PDFs als im Korrektur-PDF; "
                              "bitte Korrekturdateien überprüfen")

    if sort_corrections:
        print("Korrekturen werden einsortiert...")
        for tutor in to_extract:
            if not path.exists(dir_corr[tutor]):
                continue

            # (re-)create feedbacks folder
            if not path.exists(dir_feedb[tutor]):
                # unzip handins
                with zipfile.ZipFile(zip_handins, "r") as zip:
                    zip.extractall(dir_handins)
                # go through each submission
                for dir in os.listdir(dir_handins):
                    team_nr_ = infix(dir, "Team ", "-")  # extract team number
                    team_nr = team_nr_.zfill(3)
                    # team is among submissions: remove submission and keep folder
                    if not path.exists(dir_subm[tutor]):
                        continue
                    if team_nr in [subm[1:4] for subm in os.listdir(dir_subm[tutor])]:
                        subm = join(dir_handins, dir, os.listdir(join(dir_handins, dir))[0])
                        os.remove(subm)
                    # team is not among submissions: remove folder
                    else:
                        shutil.rmtree(join(dir_handins, dir))
                os.rename(dir_handins, dir_feedb[tutor])  # rename handins to feedbacks

            # copy corrections from corrections folder into Moodle feedback folder
            no_corr = []
            # for each participant's feedback folder
            for dir in [dir for dir in os.listdir(dir_feedb[tutor])]:
                team_nr_ = infix(dir, "Team ", "-")  # extract team number
                team_nr = team_nr_.zfill(3)
                if len((dirlist := [dir for dir in os.listdir(dir_corr[tutor]) if team_nr in dir])) == 1:
                    file_src = dirlist[0]  # search for the correction file (the one that contains the team nr)
                    src = join(dir_corr[tutor], file_src)
                    file_dest = "Korrektur_" + "B" + nr_ex + "_" + file_src
                    dest = join(dir_feedb[tutor], dir, file_dest)
                    shutil.copy(src, dest)  # copy correction into folder
                else:
                    if team_nr not in no_corr:
                        no_corr.append(team_nr)
            if no_corr:
                print_warning("Warnung: Für Team" + ("s " if len(no_corr) > 1 else " ") + und(no_corr) +
                      " ist kein oder mehr als ein Korrektur-PDF vorhanden; überprungen")

        # zip corrections
        if os.path.exists(dir_zip_feedb) and corrs_all:
            shutil.rmtree(dir_zip_feedb)
        if os.path.exists(zip_feedb + ".zip"):
            os.remove(zip_feedb + ".zip")
        if corrs_all:
            for dir in dir_feedb.values():
                for dir_ in os.listdir(dir):
                    shutil.copytree(os.path.join(dir, dir_), os.path.join(dir_zip_feedb, dir_))
                shutil.rmtree(dir)

        shutil.make_archive(dir_zip_feedb, 'zip', dir_zip_feedb)
        shutil.rmtree(dir_zip_feedb)

    if generate_table:
        print("Bewertungstabelle wird geschrieben...")
        entries_all = list()
        points_all = dict()

        if corrs_all:
            shutil.copy(file_grades_, file_grades)
        
        for tutor in to_extract:
            if not path.exists(file_points[tutor]):
                continue

            # copy grade table into tutor folder
            if not corrs_all:
                shutil.copy(file_grades_, file_grades)
            
            # load points and comments
            with open(file_points[tutor]) as fin:
                reader = csv.DictReader(fin, delimiter="\t")
                points = {ascii(row["Team"]): float(row["Punkte"].replace(",", ".")) if row["Punkte"] else None
                          for row in reader}
                points_all |= points
                no_points = [row for row in reader if not row["Punkte"]]
            with open(file_points[tutor]) as fin:
                reader = csv.DictReader(fin, delimiter="\t")
                comments = {ascii(row["Team"]): row["Kommentar"] if row["Kommentar"] else None
                            for row in reader}
            if no_points:
                print_warning("Warnung: Für Team" + ("s " if len(no_points) > 1 else " ") + und(no_points) +
                      " sind keine Punkte eingetragen; übersprungen")

            # read existing table
            with open(file_grades, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f, delimiter=",")
                fieldnames = reader.fieldnames
                # go through each student
                entries = []
                for row_in in reader:
                    row_out = row_in  # by default, copy entry
                    team = row_out["Gruppe"]
                    # add results from previously loaded points file
                    if team in set({**points, **comments}.keys()):  # student graded: insert points and comment
                        row_out["Bewertung"] = (str(val).replace(".", ",").zfill(2)) \
                            if (val := points[team]) is not None else ""
                        row_out["Feedback als Kommentar"] = val \
                            if (val := comments[team]) is not None else ""
                    entries.append(row_out)  # save entry
                    entries_all.append(row_out)

            if not corrs_all:
                # overwrite table with results
                with open(file_grades, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=",")
                    writer.writeheader()
                    for entry in entries:
                        writer.writerow(entry)

                # display average
                avg = round(average(points.values()), 1) if any(points.values()) else "n.a."
                print("Durchschnitt: " + str(avg) + " Punkte")

        if corrs_all:
            # overwrite table with results
            with open(file_grades, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=",")
                writer.writeheader()
                for entry in entries_all:
                    writer.writerow(entry)

            # display average
            avg = round(average(points_all.values()), 1) if any(points_all.values()) else "n.a."
            print("Durchschnitt: " + str(avg) + " Punkte")

print_success("Fertig")
