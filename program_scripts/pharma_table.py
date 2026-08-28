# -*- coding: utf-8 -*-
"""

Func for table of pharma product pick up

"""

import pandas as pd
import numpy as np



def pharma_table_func(func_dats, common_ids, cond, filtered, incl_filter):
    pdat = func_dats["pdat"]
    qdat = func_dats ["qdat"]
    
    # groupby object for group in grouped func
    grouped = pdat[pdat["StudieID"].isin(common_ids)].groupby(["StudieID","subnamn"])
    
    # Inclusion year dictionary
    incl_map = qdat.set_index("StudieID")["Inclusion_Year"].to_dict() # Get incl year (item) for each ID (key) in dic
    
    # Collect pick up cases info
    substance_info_rows = []
    for (stu_id, prod), group in grouped:
        incl_year = incl_map.get(stu_id)
        atc = group["ATC"].iloc[0]
        # upto+1 incl_year filter
        if incl_filter == "upto":
            group = group[pd.to_datetime(group["EDATUM"]) <= pd.to_datetime(f"{incl_year+1}-12-31")] # exclude all dates out of range
        # at+-1 incl_year filter
        elif incl_filter == "at":
            group = group[(pd.to_datetime(group["EDATUM"]) >= pd.to_datetime(f"{incl_year-1}-01-01")) &
                          (pd.to_datetime(group["EDATUM"]) <= pd.to_datetime(f"{incl_year+1}-12-31"))]
        # after incl_year filter
        elif incl_filter == "after": 
            group = group[pd.to_datetime(group["EDATUM"]) > pd.to_datetime(f"{incl_year}-12-31")] 
        dates = sorted(group["EDATUM"].tolist())   # all pickup dates for this ID+substance in order
        count = len(dates)               # number of pickups
        substance_info_rows.append([stu_id, prod, atc, count] + dates)  
    
    # Collect diagnosis cases info
    pharma_summary = pd.DataFrame(substance_info_rows)
    # Col headers
    pharma_summary.columns = ["StudieID", "subnamn", "ATC", "number_of_pickups"] + list(pharma_summary.columns[4:])
    pharma_summary = pharma_summary[pharma_summary["number_of_pickups"] != 0]
    
    # Time frame column
    # Get date col names
    pharma_cols = pharma_summary.columns.tolist()
    for i in range(3, len(pharma_summary.columns)):
        pharma_cols[i] = f'Date_{i-2}'
    # Add to table
    pharma_summary.columns = pharma_cols
    date_cols = pharma_summary.columns[5:]
    pharma_summary[date_cols] = pharma_summary[date_cols].apply(pd.to_datetime, errors='coerce')
    pharma_summary["min_date"] = pharma_summary[date_cols].min(axis=1)
    pharma_summary["max_date"] = pharma_summary[date_cols].max(axis=1)
    # Find min max and add
    for col in list(date_cols) + ["min_date", "max_date"]:
        pharma_summary[col] = pharma_summary[col].dt.strftime("%Y-%m-%d")
    pharma_summary.insert(3, "span", np.nan)
    # Add col for span and rm min max cols
    pharma_summary["span"] = pharma_summary["min_date"] + " - " + pharma_summary["max_date"]
    pharma_summary = pharma_summary.drop(columns=["min_date", "max_date"])
    
    # Replace NA with blanks
    pharma_summary = pharma_summary.fillna('')
    
    # Filter option for displayed subnamn entries
    if filtered == True:
        pharma_summary = pharma_summary[
            pharma_summary["subnamn"].str.contains("|".join(cond["pdat"]["subnamn"]["values"]), regex=True, na=False) |
            pharma_summary["ATC"].str.contains("|".join(cond["pdat"]["ATC"]["values"]), regex=True, na=False)
        ]
            
    if incl_filter is not None:
        # Add incl year col
        pharma_summary = pharma_summary.merge(qdat[["StudieID", "Inclusion_Year"]], on="StudieID", how="left")
        pharma_summary.insert(1, "Inclusion_Year", pharma_summary.pop("Inclusion_Year"))      
    
    return pharma_summary


