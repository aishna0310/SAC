import requests
import pandas as pd
import pickle
from tqdm import tqdm
import os


# Set up API keys
deepseek_api_key = os.environ["DEEPSEEK_API_KEY"]

ITEMPATH = r"..\inventories\MPI_Modified - 16PF_Inventory.csv" #load new dataset
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
# Function for DeepSeek API call
def deepseek_inventory(prompt, dim, aux):
    dataset = getItems(ITEMPATH, TEST_TYPE)
    batch_size = 1
    result = []
    
    for i in tqdm(range(0, len(dataset), batch_size), desc="DeepSeek Progress"):
        batch = dataset[i : i + batch_size]
        questions = [
            template.format(prompt=prompt, item=item["text"].lower())
            for _, item in batch.iterrows()
        ]
        
        for j, question in enumerate(questions):
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {deepseek_api_key}"
                }
                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You are an assistant that helps answer questions about personality traits."},
                        {"role": "user", "content": question}
                    ],
                    "temperature": 0.0,
                    "max_tokens": 100,
                    "top_p": 0.95
                }
                response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                response_data = response.json()
                result.append((batch.iloc[j], question, response_data["choices"][0]["message"]))
            except Exception as e:
                print(f"Error with DeepSeek API: {e}")
                continue

    filename = f"DeepSeek_MPI_{dim}_{aux}.pickle"
    with open(filename, "wb+") as f:
        pickle.dump(result, f)