import google.generativeai as genai
import pandas as pd
import pickle
from tqdm import tqdm
import os

from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key = os.getenv("GEMINI_API_KEY"))


ITEMPATH = r"..\..\..\inventories\MPI_Modified - 16PF_Inventory.csv" #load new dataset
TEST_TYPE = None
LABEL_TYPE = None


def getItems(filename=ITEMPATH, item_type=None, label_type=LABEL_TYPE):
    data = pd.read_csv(filename)
    if label_type is not None:
        items = data[data["label_16_pf"] == label_type]
    else:
        items = data
    return items


template = """Truth:
{prompt}

Question:
Given a statement of you: "You {item}."
Please choose from the following options to identify how accurately this statement describes you.
Options:
(A). Very Accurate
(B). Moderately Accurate
(C). Neither Accurate Nor Inaccurate
(D). Moderately Inaccurate
(E). Very Inaccurate

Answer:"""

#generates a pickle file for each trait in P2 prompting
# Function for Gemini API call
def gemini_inventory(prompt, dim, aux):
    dataset = getItems(ITEMPATH, TEST_TYPE)
    batch_size = 4
    result = []
    #genai.configure(api_key=gemini_api_key)
    genai.configure(api_key = os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    
    for i in tqdm(range(0, len(dataset), batch_size), desc="Gemini Progress"):
        batch = dataset[i : i + batch_size]
        questions = [
            template.format(prompt=prompt, item=item["text"].lower())
            for _, item in batch.iterrows()
        ]
        
        for j, question in enumerate(questions):
            try:
                response = model.generate_content(
                    question,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.0,
                        max_output_tokens=100,
                        top_p=0.95,
                    )
                )
                result.append((batch.iloc[j], question, response))
            except Exception as e:
                print(f"Error with Gemini API: {e}")
                continue

    filename = f"Gemini_MPI_{dim}_{aux}.pickle"
    with open(filename, "wb+") as f:
        pickle.dump(result, f)

