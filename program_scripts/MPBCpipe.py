#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
MPBCpipe.py

Description:
    dias before/at/after inclusion year in qdat currently refer to hdia!
    For details on any diagnosis refer to the additionally generated diagnosis table

Additional info/columns provided:
    qdat:
        Doctoral_diagnoses_at_inclusion_+-1year
        Doctoral_diagnoses_recorded_till_inclusion_+1year
        Doctoral_diagnoses_received_after_inclusion_year
    hvdat:
        all_diagnoses

Hard-code conditions:
- Header entries / short codes have to be named the same in any new data collection files

User-defined functions: None
Non-standard modules: None

Procedure:
    !Files have to be converted to tsv using the provided script csv_to_tsv to be applicable to this pipeline!

    
Input: 
Output: 

Usage: python MPBCpipe.py -q qdat_anonymised.tsv -p pdat_anonymised.tsv -hd hdat_anonymised.tsv -v vdat_anonymised.tsv -cat cats_4.json -cond conds_4.json

Version: 1.00
Date: 2026-02-28
Author: Lea Rachel Rieskamp

"""


# Imports:

from pathlib import Path
import argparse
import sys
import json
import pandas as pd
import numpy as np
import warnings

from all_dias_col import  all_diagnoses_func
from dia_vs_incl import diagnosis_vs_inclusion_time_func
from id_selec import id_selection_func
from pharma_table import pharma_table_func
from diagnosis_table import diagnosis_table_func
from thetable import thetable_func


# Storing Paths of arguments in variables:
    
warnings.simplefilter("ignore", category=pd.errors.PerformanceWarning)

# Set up argument parser
parser = argparse.ArgumentParser(description="Specify input files and optionally: Columns to sort by and other summary tables")
parser.add_argument("-q", "--qdat")
parser.add_argument("-p", "--pdat")
parser.add_argument("-hd", "--hdat") # -h is reserved by argparse for help
parser.add_argument("-v", "--vdat")
parser.add_argument("-cat", "--categories", required=True)
parser.add_argument("-cond", "--conditions", required=True)
parser.add_argument("-o", "--output")
parser.add_argument("-s", "--sort", type=str, nargs="+", help="Column to sort by")
parser.add_argument("-pt", "--pharma", nargs="*", default=None, help="Pharma pick ups summary table (optional: upto/at/after)")
parser.add_argument("-ptf", "--pharmafiltered", nargs="*", default=None, help="Filtered pharma pick ups summary table (optional: upto/at/after)")
parser.add_argument("-dt", "--diagnosis", nargs="*", default=None, help="Diagnosis cases summary table")
args = parser.parse_args()


# Reading in and assigning files
qdat = pd.read_csv(Path(args.qdat), sep="\t") if args.qdat else None
pdat = pd.read_table(Path(args.pdat), encoding='unicode_escape') if args.pdat else None
hdat = pd.read_table(Path(args.hdat), encoding='unicode_escape', low_memory=False) if args.hdat else None
vdat = pd.read_table(Path(args.vdat), encoding='unicode_escape', low_memory=False) if args.vdat else None
cats_file = Path(args.categories)
conds_file = Path(args.conditions)


# Sort flag set up
if args.sort is not None:
    sort_cols = list(args.sort)
else:
    sort_cols = []
    
    
# pharma flags set up

if "-pt" in sys.argv and "-ptf" in sys.argv:
    print("Please choose either -pt or -ptf")
    exit()

if args.pharma is not None:
    incl_filter = args.pharma[0] if args.pharma else None
elif args.pharmafiltered is not None:
    incl_filter = args.pharmafiltered [0] if args.pharma else None
else:
    incl_filter = None
    


# Error catches

# Missing qdat
if qdat is None:
    print("Please provide questionnaire data.")
    exit()

# Requesting Diagnosis table with no diagnosis data
if hdat is None and vdat is None:
    if args.diagnosis:
        print("Please provide diagnosis data for the diagnosis summary table generation.\nIf no diagnosis data is available, please remove the -dt flag in the command line.")
        exit()

# Requesting Pharma table with no pharma data
if pdat is None:
    if args.pharma:
        print("Please provide pharmacy data for the pharmacy summary table generation.\nIf no pharmacy data is available, please remove the -pt flag in the command line.")
        exit()

  

# More checks, formatting, and additional coloumns prep

qdat = qdat.rename(columns={"Id": "StudieID"})

if hdat is not None or vdat is not None:
    hvdat = pd.concat([hdat, vdat], ignore_index=True, join="outer") # hdat or vdat automatically ignored when one of them is None
    if hdat is not None:
        hvdat["UTDATUMA"] = hvdat["UTDATUMA"].astype("Int64")
else:
    hvdat = None



# Get json file contents

# chosen cats/headers
with open(cats_file, "r") as json_file:
    cat = json.load(json_file)
# chosen conditions
with open(conds_file) as json_file:
    cond = json.load(json_file)

# Error catches

# Requesting filtered meds in pharma table without subnamn or ATC condition
if "-ptf" in sys.argv and ("subnamn" not in cond["pdat"] and "ATC" not in cond["pdat"]):
    print("You have no subnamn or ATC condition in your conditions JSON file. Include a subnamn and/or ATC condition or change -ptf to -pt in the command line")
    exit()

# Requesting columns based on data that is not provided
if hdat is None and vdat is None:
    if "hvdat" in cat or "hvdat" in cond:
        print("Please provide diagnosis data for columns generated based on such data.\nIf no diagnosis data is available, please remove hvdat from your conditions and categories json files.")
        exit()
if pdat is None:
    if "pdat" in cat or "pdat" in cond:
        print("Please provide pharmacy data for columns generated based on such data.\nIf no pharmacy data is available, please remove pdat from your conditions and categories json files.")
        exit()


# List of cols containing diagnosis info
dia_cols = ["hdia"] + [f"DIA{i}" for i in range(1, 31)]

# Turning all Dia entries to simple strings cause the entry formats ARE A MESS
if hvdat is not None:
    hvdat[dia_cols] = hvdat[dia_cols].apply(lambda col: col.map(str))


# Variable and data dics for functions and other

func_dats = {
    "qdat": qdat,
    "hvdat": hvdat,
    "hdat": hdat,
    "vdat": vdat,
    "pdat": pdat,
    "categories": cat,
    "cond": cond
}


#------------------------------------------------------------------------------
# Additional info coloumns generation
#------------------------------------------------------------------------------


if hvdat is not None:
    # All Diagnoses listed in 1 col (All listed diagnoses at that visit)
    hvdat = all_diagnoses_func(func_dats, dia_cols)
    hvdat[dia_cols] = hvdat[dia_cols].replace("nan", np.nan)
    # Update func dats entry
    func_dats["hvdat"] = hvdat

    # Diagnosis time vs inclusion time
    qdat = diagnosis_vs_inclusion_time_func(func_dats)
    # Update func dats entry
    func_dats["qdat"] = qdat


# More variable and data dics for functions and other

# cat tables dic
cat_tables = {key: val for key, val in {
    "qdat": qdat,
    "pdat": pdat,
    "hvdat": hvdat
}.items() if val is not None}

# tables dic
tables = {key: val for key, val in {
    "qdat": qdat,
    "pdat": pdat,
    "hvdat": hvdat
}.items() if val is not None}


# -----------------------------------------------------------------------------
# Filtering for user-defined conditions
#------------------------------------------------------------------------------

# filter IDs by condition based on json file

common_ids = id_selection_func(tables, cond)

if not common_ids:
    print("There are no patients meeting all your conditions.")
    exit()


# -----------------------------------------------------------------------------
# Output table generation and formatting
#------------------------------------------------------------------------------

thetable = thetable_func(func_dats, cat_tables, common_ids)


#------------------------------------------------------------------------------
# Optional table transformations
#------------------------------------------------------------------------------

# sort format thetable

#sort_cols = ["Age_Diagnosis", "StudieID"] # Spyder version

if len(sort_cols) > 0:
    thetable = thetable.sort_values(by=sort_cols)


#------------------------------------------------------------------------------
# Output table saving
#------------------------------------------------------------------------------

thetable.to_csv(f"{(args.output + '_') if args.output else ''}filtered_table.tsv",
                sep='\t', index=False, index_label=None, na_rep='NA')

thetable.to_excel(f"{(args.output + '_') if args.output else ''}filtered_table.xlsx",
                  index=False, na_rep='NA')


#------------------------------------------------------------------------------
# ID list generation and saving
#------------------------------------------------------------------------------

thetable[["StudieID"]].to_csv(f"{(args.output + '_') if args.output else ''}ids_list.tsv", index=False, header=False)
thetable[["StudieID"]].to_excel(f"{(args.output + '_') if args.output else ''}ids_list.xlsx", index=False, header=False)


#------------------------------------------------------------------------------
# Pharma table generation
#------------------------------------------------------------------------------

# by pharma product pick up

if args.pharma is not None:
    pharma_summary = pharma_table_func(func_dats, common_ids, cond, False, incl_filter)
    pharma_summary.to_csv(f"{(args.output + '_') if args.output else ''}pharma_summary_table.tsv",
                          sep='\t', index=False, index_label=None, na_rep='NA')
    pharma_summary.to_excel(f"{(args.output + '_') if args.output else ''}pharma_summary_table.xlsx",
                            index=False, na_rep='NA')

# filter for only those subnamn requested in conditions

if args.pharmafiltered is not None:
    pharma_summary = pharma_table_func(func_dats, common_ids, cond, True, incl_filter)
    pharma_summary.to_csv(f"{(args.output + '_') if args.output else ''}pharma_summary_table.tsv",
                          sep='\t', index=False, index_label=None, na_rep='NA')
    pharma_summary.to_excel(f"{(args.output + '_') if args.output else ''}pharma_summary_table.xlsx",
                            index=False, na_rep='NA')
    

#------------------------------------------------------------------------------
# Diagnosis table generation
#------------------------------------------------------------------------------

if args.diagnosis is not None:
    if args.diagnosis != True:
        if isinstance(args.diagnosis, str):
            qdat_dias = [args.diagnosis]
        else:
            qdat_dias = args.diagnosis
    else:
        qdat_dias = None

    diagnosis_summary = diagnosis_table_func(func_dats, common_ids, dia_cols, qdat_dias)
    diagnosis_summary.to_csv(f"{(args.output + '_') if args.output else ''}diagnosis_summary_table.tsv",
                             sep='\t', index=False, index_label=None, na_rep='NA')
    diagnosis_summary.to_excel(f"{(args.output + '_') if args.output else ''}diagnosis_summary_table.xlsx",
                               index=False, na_rep='NA')





