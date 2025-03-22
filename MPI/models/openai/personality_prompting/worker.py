import openai
import anthropic
import google.generativeai as genai
import requests
import pandas as pd
import pickle
from tqdm import tqdm
import os

from dotenv import load_dotenv

load_dotenv()

# Set up API keys
openai_api_key = os.environ["OPENAI_API_KEY"]

ITEMPATH = r"..\..\..\inventories\MPI_Modified - 16PF_Inventory.csv"  # Load the 16 PF inventory
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
# Function for OpenAI API call
def openai_inventory(prompt, dim, aux):
    dataset = getItems(ITEMPATH, TEST_TYPE)
    batch_size = 1
    result = []
    
    for i in tqdm(range(0, len(dataset), batch_size), desc="OpenAI Progress"):
        batch = dataset[i : i + batch_size]
        questions = [
            template.format(prompt=prompt, item=item["text"].lower())
            for _, item in batch.iterrows()
        ]
        messages=[
        {"role": "system", "content": "You are an assistant that helps answer questions about personality traits."}]

        for question in questions:
            messages.append({"role": "user", "content": question})
        
        try:
            responses = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.0,
                max_tokens=100,
                top_p=0.95,
            )
            for j, response in enumerate(responses.choices):
                result.append((batch.iloc[j], questions[j], response))
        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            continue

    filename = f"OpenAI_MPI_{dim}_{aux}.pickle"
    with open(filename, "wb+") as f:
        pickle.dump(result, f)