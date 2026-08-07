# MPBCpipe

Version: 1.00  
Date: 07.08.2026
Author: Lea Rachel Rieskamp
Supervision: Maria Swanberg, Translational Neurogenetics Lab, Lund University

------------------------------------------------------------------------------------------------------------------------------------------------------

# Table of contents

1.  Overview
2.  Supported input datasets
3.  Requirements
4.  Input pre-processing
5.  Usage
6.  Command line arguments
7.  Flag details & examples
8.  Output files
9.  JSON configuration files
10. Categories JSON file
11. Conditions JSON file
12. Additionally generated columns
13. Pharmacy summary table
14. Diagnosis summary table
15. Error handling
16. Important notes

------------------------------------------------------------------------------------------------------------------------------------------------------

# Overview

MPBCpipe.py is a flexible Python pipeline for filtering, combining, stratifying, and summarising clinical and registry data used in Parkinson's disease research.
The script integrates questionnaire, diagnosis, and pharmacy datasets and enables users to:

- Identify individuals matching user-defined conditions
- Generate filtered output tables with user-defined columns
- Combine information across datasets
- Generate additional columns with information derived from cross-table analysis
- Produce optional diagnosis summary tables
- Produce optional pharmacy summary tables
- Export all results as .tsv, .xlsx, and ID list files

The program is currently used in the Translational Neurogenetics Lab at Lund University for:
- General cohort inspection
- Phenotype stratification
- Longitudinal diagnosis analyses
- Cross-table validation and consistency checks
- Polygenic risk score analyses
- Medication analyses

------------------------------------------------------------------------------------------------------------------------------------------------------

# Supported input datasets

The pipeline currently supports the following datasets:

- QuestionnaireData_N1864_FINAL_CLEANED_210621	(Questionnaire / phenotype data, qdat)
- UT_R_LMED_14691_2021							(Medication collections registry, pdat)
- UT_R_PAR_SV_14691_2021						(Hospital diagnosis registry, hdat)
- UT_R_PAR_OV_14691_2021						(Outpatient/doctoral visit diagnosis registry, vdat)

For efficiency purposes these are referred to in my script and the following descriptions as qdat, pdat, hdat, and vdat, respectively.
hvdat refers to the combined vdat and hdat data.

------------------------------------------------------------------------------------------------------------------------------------------------------

# Requirements

## Python packages

- pandas
- numpy
- openpyxl

Install with:
pip install pandas numpy openpyxl

------------------------------------------------------------------------------------------------------------------------------------------------------

# Input pre-processing

All input files must first be converted to tsv format using the provided csv_to_tsv conversion script before running the pipeline:
python csv_to_tsv.py -q qdat -p pdat -hd hdat -v vdat

------------------------------------------------------------------------------------------------------------------------------------------------------

# Usage

## Basic command

python MPBCpipe.py -q qdat.tsv -cat categories.json -cond conditions.json

## Full example

python MPBCpipe.py \
-q qdat.tsv \
-p pdat.tsv \
-hd hdat.tsv \
-v vdat.tsv \
-cat categories.json \
-cond conditions.json

## Example with optional flags and example flag arguments

python MPBCpipe.py \
-q qdat.tsv \
-p pdat.tsv \
-hd hdat.tsv \
-v vdat.tsv \
-cat categories.json \
-cond conditions.json \
-o PD_patients \
-s Age_Diagnosis StudieID \
-pt after \
-dt Diabetes oneway_G20

------------------------------------------------------------------------------------------------------------------------------------------------------

# Command line arguments

## Required arguments

-cat, --categories		JSON file specifying output columns/categories
-cond, --conditions		JSON file specifying filtering conditions

## Input data files

-q, --qdat				Questionnaire dataset

Optional:

-p, --pdat				Pharmacy dataset
-hd, --hdat				Hospital diagnosis dataset
-v, --vdat				Doctoral/outpatient diagnosis dataset

## Optional output & processing flags

-o, --output			Prefix added to all generated output files
-s, --sort				Columns to sort the final output table by
-pt, --pharma			Generate pharmacy summary table
-ptf, --pharmafiltered	Generate filtered pharmacy summary table
-dt, --diagnosis		Generate diagnosis summary table

------------------------------------------------------------------------------------------------------------------------------------------------------

# Flag details & examples

## -o

Adds a prefix to all output files.
Example: -o Parkinsons_subset
Produces files such as:
Parkinsons_subset_filtered_table.tsv
Parkinsons_subset_ids_list.csv

## -s

Sorts the final output table vertically by one or more columns.
Syntax: -s column1 column2 column3
The first column is the primary sort variable, the second is the secondary sort variable, etc.
Example: -s Age_Diagnosis StudieID
Important: Sort columns must also be included in the categories JSON file.

## -pt

Generates a pharmacy summary table (described in further detail under Pharma summary table below).
Optional arguments:
upto
at
after
These define filtering relative to inclusion year.
Example: -pt after

## -ptf

Same as -pt, but restricts the displayed output to pharmacy entries matching the requested subnamn conditions.
Example: -ptf after
Important: -pt and -ptf cannot be used simultaneously.

## -dt

Generates a diagnosis summary table (described in further detail under Diagnosis summary table below).
Optional arguments can specify:
qdat diagnosis columns to be included
diagnosis conversion analysis modes
Example: -dt Diabetes
Example with conversion mode: -dt oneway_G20
Example with multiple arguments: -dt Diabetes Depression oneway_G20

------------------------------------------------------------------------------------------------------------------------------------------------------

# Output files

The pipeline generates the following output files as .tsv and excel files:

filtered_table.tsv/xlsx				Main filtered output table
ids_list.tsv/xlsx					Included patient IDs

Optional outputs:

pharma_summary_table.tsv/xlsx		Pharmacy summary table
diagnosis_summary_table.tsv/xlsx	Diagnosis summary table

------------------------------------------------------------------------------------------------------------------------------------------------------

# JSON configuration files

The pipeline requires two JSON files:

categories.json
conditions.json

Their structuring and use are described in the following below.
Example files are provided on GitHub and can be adjusted easily.

------------------------------------------------------------------------------------------------------------------------------------------------------

# Categories JSON file

The categories JSON defines which columns should appear in the final output table.
The file contains a simple dictionary with dataset names as keys and lists of column names as items:

## Basic structure

{
  "qdat": [],
  "pdat": [],
  "hvdat": []
}

qdat: Questionnaire data
pdat: Medication collections data
hvdat: In- and outpatient data

## Example:

{
  "qdat":
  ["StudieID",
  "Doctoral_diagnoses_at_inclusion_+-1year"],

  "pdat":
  ["ATC",
  "produkt"],

  "hvdat":
  ["hdia",
  "all_diagnoses"]
}

## Important Notes

qdat must always be included and contain "StudieID" (noted as "id" in the original file).
The file can contain additional column names (not present in the original data sets).
These are generated by the program based on data stratification within and across tables (described in detail under Additionally generated columns).

------------------------------------------------------------------------------------------------------------------------------------------------------

# Conditions JSON file

The conditions JSON defines which individuals are included in the final output table.
The file contains nested dictionaries with dataset names as top-level keys with dictionaries as items.
These nested dictionaries contain column names as keys and again dictionaries as items,
which contain "type" as a key with a string as the item followed by "values" as a key and a list as the item.
The nesting represents the structure:
dataset --> column/category --> condition imposed on it

## Basic structure

{
  "qdat": {},
  "pdat": {},
  "hvdat": {}
}

qdat: Questionnaire data
pdat: Medication collections data
hvdat: In- and outpatient data

! qdat must always be included. If no conditions are imposed on it leave the dictionary empty as seen in the basic structure above.

## Condition setting format

To set a condition the user needs to specify the "type" of condition under the key "type".
Supported types are:
string
range
values

Example:
{
  "type": "range",
  "values": [5, 10]
}

### Values conditions

Used for numerical values filtering, e.g., to include individuals at specific Hoehn&Yahr stages.

Basic example:
{
  "Hoehn_Yahr": {
    "type": "values",
	"values": [3, 5]
  }
}
Filters for all individuals that have Hoehn&Yahr stage of 3 OR 5.

### Range conditions

Used for numerical range filtering, e.g., to include any individuals within an age range.

Basic example:
{
  "type": "range",
  "values": [20, 40]
}
Where the outer limit values, 20 and 40, are included in the selected range.

#### Supported operators:

>=
<=
>
<

Example:
{
  "Age_Diagnosis": {
    "type": "range",
    "values": ["<=", 40]
  }
}
Filters for all individuals that received their diagnosis at 40 or younger.

### String conditions

Used for text matching, e.g., diagnosis or medication codes.
Capable of regex matching.

Basic example:
{
  "hvdat": {
    "all_diagnoses": {
      "type": "string",
      "values": ["G20"]
    }
  }
}
Filters for individuals having "G20" in "all_diagnoses" (an hvdat column).

#### Match to exclude:

Individuals can also be EXCLUDED from the final table by matching a condition.
To exclude if a string is matched, begin the string with: "!"
Example:	["!G20"]
Filters for individuals NOT having G20.

#### Multiple match conditions:

Match any - Example:	["G20", "E11"]
Filters for all individuals containing G20 AND/OR E11.

Match both - Example: 	["&", "G20", "E11"]
Filters for all individuals containing G20 AND E11.
If all entries must match, begin the list with: "&"

Complex combination - Example: ["&", "G20", "E.*", "!E11"]
Filters for all individuals that have G20 AND have any diagnosis starting with E, but NOT E11.

#### Special Conditions:

any
Includes only non-empty entries.
Example:
{
  "produkt": {
    "type": "string",
    "values": ["any"]
  }
}

none
Matches empty and na entries.
Example:
{
  "produkt": {
    "type": "string",
    "values": ["none"]
  }
}

## Example condition JSON
{
  "qdat": {
  },
  "pdat": {
    "ATC": {
      "type": "string",
      "values": ["^C05.*"]
    }
  },
  "hvdat": {
    "all_diagnoses": {
      "type": "string",
      "values": ["G20"]
    }
  }
}

------------------------------------------------------------------------------------------------------------------------------------------------------

# Additionally generated columns

The pipeline can generate additional derived columns when diagnosis data (hdat and/or vdat) is provided.
The columns can be requested by the user by simply adding their header in the categories JSON file as one of the output columns.

Columns, their content, and under which key to include in the JSON file:

all_diagnoses										All diagnoses an individual received combined into one column	hvdat
Doctoral_diagnoses_at_inclusion_+-1year				Diagnoses at inclusion year in qdat +-1 year					qdat
Doctoral_diagnoses_recorded_till_inclusion_+1year	Diagnoses recorded up to inclusion in qdat +1 year				qdat
Doctoral_diagnoses_received_after_inclusion_year	Diagnoses received after inclusion in qdat						qdat

Inclusion years vary by individual. The program automatically adjusts for this per individual.
The diagnoses are only based on hdat and vdat (diagnoses stated by an individual in qdat are not considered due to lack of reliability).

------------------------------------------------------------------------------------------------------------------------------------------------------

# Pharmacy summary table

The optionally generated pharmacy summary table:
- Gives a medication-focussed overview of the filtered data
- Displays each medication (based on substance name ("subnamn")) collected by an individual from the pharmacy in a separate row,
  together with information on the number of collections, each collection date, and the overall time span of these

## Filtering medications displayed

The user can request the table to list all or list only the medications that the cohort was filtered by via the JSON file subnamn conditions.
This is done by adjustment of the command line flag:

-pt for a table displaying all medications the filtered individuals collected at the pharmacy
-ptf for a filtered table displaying only the medications the individuals were filtered by

E.g., if the data was filtered for only individuals that received Levodopa and/or Metformin,
the -pt flag generates a table showing all medications these individuals received,
the -ptf flag generates a table with only the Levodopa and Metformin rows for these individuals

## Filtering relative to inclusion year in qdat

The pharmacy table can also be filtered to include only medications collected before, around, or after the year an individual was included in qdat.

Modes:

- all (default)
- upto mode
- at mode
- after mode

All (default)
All available pharmacy data is included

Upto mode
Only includes medication collections occurring up to inclusion +1 year
Use:
-pt upto
or
-ptf upto

At mode
Only includes medication collections occurring at inclusion +-1 year
Use:
-pt at
or
-ptf at

After mode
Only includes medication collections occurring after the inclusion year
Use:
-pt after
or
-ptf after

------------------------------------------------------------------------------------------------------------------------------------------------------

# Diagnosis summary table

The optionally generated diagnosis summary table:
- Gives a diagnosis-focussed overview of the filtered data
- Compares questionnaire diagnoses with diagnosis registry data
- Displays each diagnosis an individual received in a separate row, together with information on
  deviations from qdat, selected qdat columns, number of times diagnosed, each diagnosis date, the overall time span of these

## Additionally displayed qdat columns

The user can display specific additional diagnoses columns from qdat by adding the column header after the -dt flag in the command line.

Example:
-dt Depression Asthma
Will include the Depression and the Asthma columns from qdat in the final diagnosis summary table.

## Conversion analysis

The program can compare G20 (Parkinsons) and E11 (Diabetes) diagnoses for an individual in qdat to the doctoral diagnoses in hvdat.
For conversion analysis of E11, Diabetes has to be listed among the additional qdat columns (see paragraph above).
Deviations can occur for several reasons including:
- An individuals self-perception varies from doctorally "approved" diagnoses
- An individual is aware of a condition but has not been to a medical professional to receive an official diagnosis
- A diagnosis can be present before inclusion in the questionnaire (hence appearing among the hvdat diagnoses) but is no longer present at the time of inclusion (hence not stated by the individual as such)
- A diagnosis is only given after inclusion in qdat. The individual might have only noticed or developed the condition at a later state.
- An individual has received the diagnosis doctorally but not within the time span covered by the hvdat data set.

### Conversion analysis modes

- two-way mode (default)
- one-way mode
- reverse one-way mode

Two-Way (default)
A conversion is flagged if qdat diagnosis and hvdat diagnosis do not match.
This includes:
Diagnosis stated in qdat but absent in hvdat
Diagnosis absent in qdat but present in hvdat

One-Way
Only detects cases where:
hvdat diagnosis exists
qdat diagnosis does NOT exist
Useful for identifying likely post-inclusion diagnosis development.
Use:
-dt oneway_G20
or
-dt oneway_E11

Reverse one-Way
Only detects cases where:
qdat diagnosis exists
hvdat diagnosis does NOT exist
Useful for identifying self-reported diagnoses lacking registry confirmation.
Use:
-dt onewayother_G20
or
-dt onewayother_E11

Note: The conversion modes for G20 and E11 can be applied in parallel and do not have to match. The order of -dt arguments does not matter.
Example:
-dt Diabetes oneway_E11 onewayother_G20

------------------------------------------------------------------------------------------------------------------------------------------------------

# Error handling

The script checks for:

Missing required datasets
Invalid optional flag combinations
Conditions/categories referencing unavailable datasets
Empty filtered results (no individuals meet the user-defined requirements)

Examples:

Using -pt without pdat
Using diagnosis-derived columns without diagnosis data
Using both -pt and -ptf

------------------------------------------------------------------------------------------------------------------------------------------------------

# Important notes

If a dataset is not provided, corresponding entries must be removed from the categories and conditions JSON files.

hdat and vdat are automatically merged internally into hvdat.

------------------------------------------------------------------------------------------------------------------------------------------------------
