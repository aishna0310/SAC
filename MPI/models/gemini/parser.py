# import re
# import pickle
# import numpy as np
# import sys

# #Load results will load all 16 pickle files and store the results in one array.
# #RESULT_FILE will take the argument while we run the file as all 16 files 
# #then the final parsing will essentially run the parser on an aggregate of all 16 files


# def load_results(pickle_files):
#     all_results = []  # Initialize a list to hold results from all files
#     for file in pickle_files:
#         with open(file, 'rb+') as f:
#             results = pickle.load(f)  # Load the results from the pickle file
#             all_results.extend(results)  # Add the results to the combined list
#     return all_results  # Return the combined results


# RESULT_FILE = sys.argv[1:]

# # with open(RESULT_FILE, 'rb+') as f:
# #     all_results = pickle.load(f)


# count = {'A' : 0, 'B' : 0, 'C' : 0, 'D' : 0, 'E': 0,'UNK' : 0} #the count of each option chosen
# #codes for all the persoanlities
# traits = {
#     "A": [],
#     "B": [],
#     "C": [],
#     "E": [],
#     "F": [],
#     "G": [],
#     "H": [],
#     "I": [],
#     "L": [],
#     "M": [],
#     "N": [],
#     "O": [],
#     "Q1": [],
#     "Q2": [],
#     "Q3": [],
#     "Q4": []
# }

# SCORES = {
#     "A" : 5 , 
#     "B" : 4 ,
#     "C" : 3 ,
#     "D" : 2 ,
#     "E" : 1 ,
# }

# def calc_mean_and_var(result):
#     mean  = {}
#     std  = {}
#     for key, item in result.items():
#         mean[key] = np.mean(np.array(item))
#         std[key] = np.std(np.array(item))

#     return f'''mean:\n {sorted(mean.items(), key=lambda item:item[0])}\n std:\n {sorted(std.items(), key=lambda item:item[0])}'''

# all_results = load_results(RESULT_FILE)

# for question in all_results:
#     res = question[2].message.content + ')'
#     match = re.search(r'[abcdeABCDE][^a-zA-Z]', res, flags = 0)
#     if match is None:
#         print(f"WARNING: Could not find a valid choice in response: {res[:50]}...")
#         choice = 'UNK'  # Default to 'C' (midpoint)
#     else:
#         choice = match.group()[0].upper()
#     count[choice] += 1
#     label = question[0]['label_16_pf']
#     label_raw = question[0]['label_raw']
#     key = question[0]['key']
#     score = SCORES[choice]

#     if key == 1:
#         traits[label].append(score)
#     else:
#         traits[label].append(6 - score)

# print(calc_mean_and_var(traits))



# # print(count)


#!/usr/bin/env python
"""
parser_v2.py  –  build 16×16 mean & variance matrices from 16 pickle files
Usage
-----
python parser_v2.py  file1.pickle file2.pickle … file16.pickle
"""

import sys, re, pickle, numpy as np, pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# 0.  16-PF code  →  full trait label  (and canonical order)
# ---------------------------------------------------------------------------
code_to_label = {
    "A":  "WARMTH",
    "B":  "INTELLECT",
    "C":  "EMOTIONAL STABILITY",
    "E":  "ASSERTIVENESS",
    "F":  "GREGARIOUSNESS",
    "G":  "DUTIFULNESS",
    "H":  "FRIENDLINESS",
    "I":  "SENSITIVITY",
    "L":  "DISTRUST",
    "M":  "IMAGINATION",
    "N":  "RESERVE",
    "O":  "ANXIETY",
    "Q1": "COMPLEXITY",
    "Q2": "INTROVERSION",
    "Q3": "ORDERLINESS",
    "Q4": "EMOTIONALITY",
}
traits_order = list(code_to_label.values())          # 16-item canonical order

# score key for A–E answers
SCORES = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}

# ---------------------------------------------------------------------------
# 1.  check input & create empty matrices
# ---------------------------------------------------------------------------
if len(sys.argv) < 2:
    sys.exit("Give me the 16 pickle files on the command line!")

cols = traits_order          # observed traits (columns)
rows = traits_order          # target traits   (rows)

mean_mat = pd.DataFrame(index=rows, columns=cols, dtype=float)
var_mat  = pd.DataFrame(index=rows, columns=cols, dtype=float)

# ---------------------------------------------------------------------------
# 2.  process ONE pickle file at a time (each = one target trait)
# ---------------------------------------------------------------------------
for fp in sys.argv[1:]:
    fp = Path(fp)
    # filename pattern “…_MPI_<TARGET>_…”
    try:
        target_code = fp.stem.split('_MPI_')[1].split('_')[0]
    except IndexError:
        sys.exit(f"Cannot parse target code from filename {fp}")
    
    raw_id = fp.stem.split('_MPI_')[1].split('_')[0]      # e.g. 'ANXIETY'  *or*  'Q3'
    raw_id = raw_id.replace('_', ' ')                     # handle EMOTIONAL_STABILITY

    # if it’s already a full name, keep it; otherwise map code→name
    target_label = code_to_label.get(raw_id, raw_id.upper())

    # holder for this row
    observed_scores = {code: [] for code in code_to_label}

    with fp.open('rb') as f:
        results = pickle.load(f)

    for q in results:
        meta, response = q[0], q[2].message.content + ')'

        m = re.search(r'[abcdeABCDE][^a-zA-Z]', response)
        choice = m.group()[0].upper() if m else 'C'   # midpoint if missing
        score  = SCORES.get(choice, 3)

        obs_code = meta['label_16_pf']          # observed trait code
        key_flag = meta['key']                  # 1 = forward, 0 = reversed
        score    = score if key_flag == 1 else 6 - score

        observed_scores[obs_code].append(score)

    # --- compute mean & variance for this target --------------------------
    means = {c: np.mean(v) for c, v in observed_scores.items()}
    vars_ = {c: np.var (v) for c, v in observed_scores.items()}

    mean_mat.loc[target_label] = [means[c] for c in code_to_label]
    var_mat.loc [target_label] = [vars_[c] for c in code_to_label]

    print(f"Processed {fp.name:45s} → row '{target_label}'")

# ---------------------------------------------------------------------------
# 3.  save CSVs
# ---------------------------------------------------------------------------
mean_mat.to_csv("Gemini_MPI_means.csv", sep='\t', index_label='')
var_mat .to_csv("Gemini_MPI_vars.csv",  sep='\t', index_label='')

print("\nSaved:")
print("  • Gemini_MPI_means.csv   (16×16 means)")
print("  • Gemini_MPI_vars.csv    (16×16 variances)")

