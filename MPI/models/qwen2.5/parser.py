import re
import pickle
import numpy as np
import sys

#Load results will load all 16 pickle files and store the results in one array.
#RESULT_FILE will take the argument while we run the file as all 16 files 
#then the final parsing will essentially run the parser on an aggregate of all 16 files


def load_results(pickle_files):
    all_results = []  # Initialize a list to hold results from all files
    for file in pickle_files:
        with open(file, 'rb+') as f:
            results = pickle.load(f)  # Load the results from the pickle file
            all_results.extend(results)  # Add the results to the combined list
    return all_results  # Return the combined results


RESULT_FILE = sys.argv[1:]

# with open(RESULT_FILE, 'rb+') as f:
#     all_results = pickle.load(f)


count = {'A' : 0, 'B' : 0, 'C' : 0, 'D' : 0, 'E': 0,'UNK' : 0} #the count of each option chosen
#codes for all the persoanlities
traits = {
    "A": [],
    "B": [],
    "C": [],
    "E": [],
    "F": [],
    "G": [],
    "H": [],
    "I": [],
    "L": [],
    "M": [],
    "N": [],
    "O": [],
    "Q1": [],
    "Q2": [],
    "Q3": [],
    "Q4": []
}

SCORES = {
    "A" : 5 , 
    "B" : 4 ,
    "C" : 3 ,
    "D" : 2 ,
    "E" : 1 ,
}

def extract_option(text):
    """
    Extract option letter (A-E) from text.
    Tries multiple patterns in order of specificity.
    """
    # print(text[:100]) # Print the first 100 characters of the text for debugging
    # Pattern 1: "option (X)" or "option X" format
    match = re.search(r'option\s*\(?([A-E])\)?', text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    # Pattern 2: "(X)" where X is A-E
    match = re.search(r'\(([A-E])\)', text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    # Pattern 3: Standalone letter followed by non-letter or end of string
    match = re.search(r'\b([A-E])(?:[^a-zA-Z]|$)', text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    # Pattern 4: Letter at start of line followed by non-letter
    match = re.search(r'^([A-E])[^a-zA-Z]', text, re.IGNORECASE | re.MULTILINE)
    if match:
        return match.group(1).upper()
    
    return None

def calc_mean_and_var(result):
    mean  = {}
    std  = {}
    for key, item in result.items():
        mean[key] = np.mean(np.array(item))
        std[key] = np.std(np.array(item))

    return f'''mean:\n {sorted(mean.items(), key=lambda item:item[0])}\n std:\n {sorted(std.items(), key=lambda item:item[0])}'''

all_results = load_results(RESULT_FILE)

for question in all_results:
    res = question[2] + ')'
    # choice = re.search(r'[abcdeABCDE][^a-zA-Z]', res, flags = 0).group()[0].upper()
    choice = extract_option(res)
    print(choice)
    if choice is None:
        choice = 'UNK'
        print(f"Warning: Could not extract choice from: {res[:100]}...")

    count[choice] += 1
    label = question[0]['label_16_pf']
    label_raw = question[0]['label_raw']
    key = question[0]['key']
    score = SCORES[choice]

    if key == 1:
        traits[label].append(score)
    else:
        traits[label].append(6 - score)

print(calc_mean_and_var(traits))

print(count)
