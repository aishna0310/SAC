import openai
import pandas as pd
import pickle
import os

from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]


ITEMPATH = r"..\..\inventories\MPI_Modified - 16PF_Inventory.csv"  # Load the 16 PF inventory
TEST_TYPE = None
LABEL_TYPE = None

def getItems(filename=ITEMPATH, item_type=None, label_type=LABEL_TYPE):
    data = pd.read_csv(filename)
    if label_type is not None:
        items = data[data["label_16_pf"] == label_type]
    else:
        items = data
    return items


template = """Question:
Given a statement of you: "You {}."
Please choose from the following options to identify how accurately this statement describes you.
Options:
A. Very Accurate
B. Moderately Accurate
C. Neither Accurate Nor Inaccurate
D. Moderately Inaccurate
E. Very Inaccurate

IMPORTANT: only answer using the Letter of the option, do not include any other text. Limit yourself to only letters A,B,C,D,E corresponding to the options given
Answer:"""

import time

dataset = getItems(ITEMPATH, TEST_TYPE)

for temperature in [0]:
    # batchify request
    batch_size = 1
    result = []
    for i in range(0, len(dataset), batch_size):
        batch = dataset[i : i + batch_size]
        questions = [
            template.format(item["text"].lower()) for _, item in batch.iterrows()
        ]
        messages=[
        {"role": "system", "content": "You are an assistant that answers questions about your own personality traits."}]

        for question in questions:
            messages.append({"role": "user", "content": question})

        responses = openai.chat.completions.create(
            model="gpt-4o", #change model here
            # prompt=questions,
            messages=messages,
            temperature=temperature,
            max_tokens=400,
            top_p=0.95,
        )
        for j, response in enumerate(responses.choices):
            result.append((batch.iloc[j], questions[j], response))
            print(response.message.content)

    with open(f"openai-neutral-path-to-save.pickle", "wb+") as f:
        pickle.dump(result, f)


