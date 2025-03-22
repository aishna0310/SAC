import anthropic
import pandas as pd
import pickle
from tqdm import tqdm
import os


# Set up API keys
anthropic_api_key = os.environ["ANTHROPIC_API_KEY"]


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

# Function for Claude API call
def claude_inventory(prompt, dim, aux):
    dataset = getItems(ITEMPATH, TEST_TYPE)
    batch_size = 1
    result = []
    client = anthropic.Anthropic(api_key=anthropic_api_key)
    
    for i in tqdm(range(0, len(dataset), batch_size), desc="Claude Progress"):
        batch = dataset[i : i + batch_size]
        questions = [
            template.format(prompt=prompt, item=item["text"].lower())
            for _, item in batch.iterrows()
        ]
        
        for j, question in enumerate(questions):
            try:
                response = client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=100,
                    temperature=0.0,
                    messages=[
                        {"role": "user", "content": question}
                    ]
                )
                result.append((batch.iloc[j], question, response))
            except Exception as e:
                print(f"Error with Claude API: {e}")
                continue

    filename = f"Claude_MPI_{dim}_{aux}.pickle"
    with open(filename, "wb+") as f:
        pickle.dump(result, f)