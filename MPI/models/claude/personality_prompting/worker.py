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


from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key = os.environ["OPENROUTER_API_KEY"],
)


# Set up API keys
ITEMPATH = r"..\..\..\MPI_Modified - 16PF_Inventory.csv"  # Load the 16 PF inventory
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
# Function for Claude API call
def claude_inventory(prompt, dim, aux):
    dataset = getItems(ITEMPATH, TEST_TYPE)
    batch_size = 1
    result = []
    
    for i in tqdm(range(0, len(dataset), batch_size), desc="Claude Progress"):
        batch = dataset[i : i + batch_size]
        questions = [
            template.format(prompt=prompt, item=item["text"].lower())
            for _, item in batch.iterrows()
        ]
        messages=[
            {"role": "system", "content": "You are an assistant that helps answer questions about personality traits."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            responses = client.chat.completions.create(
            model="anthropic/claude-3.7-sonnet:beta",
            messages=messages
        )
            for j, response in enumerate(responses.choices):
                result.append((batch.iloc[j], questions[j], response))
        except Exception as e:
            print(f"Error with Claude API: {e}")
            continue

    filename = f"Claude_MPI_{dim}_{aux}.pickle"
    with open(filename, "wb+") as f:
        pickle.dump(result, f)