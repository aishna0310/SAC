import ollama
import requests
import pandas as pd
import pickle
from tqdm import tqdm
import os

from dotenv import load_dotenv

load_dotenv()


# Set up API keys
ITEMPATH = r"~/SAC-1/MPI/MPI_Modified - 16PF_Inventory.csv"  # Load the 16 PF inventory
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
# Function for gemini API call
def qwen_inventory(prompt, dim, aux):
    dataset = getItems(ITEMPATH, TEST_TYPE)
    batch_size = 1
    result = []
    
    for i in tqdm(range(0, len(dataset), batch_size), desc="qwen2.5 Progress"):
        batch = dataset[i : i + batch_size]
        questions = [
        template.format(prompt=prompt, item=item["text"].lower())
        for _, item in batch.iterrows()
    ]

        for j, q in enumerate(questions):
            messages = [
                {"role": "system", "content": "You are an assistant that helps answer questions about personality traits."},
                {"role": "user", "content": q},
            ]

            try:
                response = ollama.chat(
                    model="qwen2.5",
                    messages=messages
                )
                # Extract assistant reply
                answer = response["message"]["content"].strip()
                print(answer)
                result.append((batch.iloc[j], q, answer))
            except Exception as e:
                print(f"Error with qwen2.5 API: {e}")
                continue

    filename = f"qwen2.5_MPI_{dim}_{aux}.pickle"
    with open(filename, "wb+") as f:
        pickle.dump(result, f)