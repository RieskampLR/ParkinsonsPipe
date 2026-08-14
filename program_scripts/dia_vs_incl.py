# -*- coding: utf-8 -*-
"""

Func for column generation of diagnosis times in comparison to inclusion time in qdat
Diagnoses listed are from hdia AND any other DIA cols

"""


import pandas as pd
import numpy as np


def diagnosis_vs_inclusion_time_func(func_dats):
    # Assign data and variables from main script
    qdat = func_dats["qdat"]
    hvdat = func_dats["hvdat"]
    hdat = func_dats["hdat"]
    vdat = func_dats["vdat"]
    categories = func_dats["categories"]
    cond = func_dats["cond"]
    
    col_names = ["Doctoral_diagnoses_received_after_inclusion_year", "Doctoral_diagnoses_at_inclusion_+-1year", "Doctoral_diagnoses_recorded_till_inclusion_+1year"]
    
    # Calculate columns if needed in output table
    if any(col in categories["qdat"] or col in cond["qdat"] for col in col_names):

        # Participants with diagnosis at inclusion +-1
        
        year = qdat.set_index("StudieID")["Inclusion_Year"].astype(int)
        
        doc_combined = pd.concat([hdat, vdat], ignore_index=True)
        visit_year = doc_combined["INDATUMA"].astype(str).str[:4].astype(int)
        incl_year = doc_combined["StudieID"].map(year)
         
        masks = [
            visit_year > incl_year,
            (visit_year - incl_year).abs() <= 1,
            visit_year <= incl_year + 1,
        ]
        
        
        counter = 0
        
        
        for mask in masks: 
        
            # get diagnoses for these
            cols = ["StudieID"] + ["hdia"] + [c for c in hdat.columns if c.startswith("DIA") and c!= "DIA_ANT"]
            doc_combined = pd.concat([hdat, vdat], ignore_index=True)
            result = doc_combined.loc[mask, cols]

            
            # To 1 coloumn
            col_name = col_names[counter]
            counter = counter + 1
            result[col_name] = (
                result.drop(columns="StudieID").fillna("").astype(str).agg(",".join, axis=1)
                .str.replace(r"(,+)", ",", regex=True).str.strip(","))
            result = result[["StudieID", col_name]]
            
            
            # Each patient once (diagnoses fused)
            result = result.groupby("StudieID", as_index=False).agg({col_name: ",".join})
            
            for i, entry in enumerate(result [col_name]):
                diagnoses = entry.split(",")
                cut = set(diagnoses)
                result.at[i, col_name] = ",".join(sorted(cut)) # replace entry
            
            # Add to qdat table
            qdat = qdat.merge(result, on="StudieID", how="left")
            qdat.insert(5 + counter - 1, col_name, qdat.pop(col_name))
        
        
    qdat = qdat.copy() # removes saved memory of column movement
    
    # Turn str entries to lists by commas
    qdat[qdat.select_dtypes(include="object").columns] = qdat.select_dtypes(include="object").apply(lambda s: s.fillna("").apply(lambda x: x.split(",") if isinstance(x, str) else x))
        
    return qdat
        


