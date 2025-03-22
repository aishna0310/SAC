import anthropic
import pandas as pd
import pickle
import os

# Set up Claude API key
client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])

ITEMPATH = r"..\inventories\MPI_Modified - 16PF_Inventory.csv"  # Load the 16 PF inventory
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
(A). Very Accurate
(B). Moderately Accurate
(C). Neither Accurate Nor Inaccurate
(D). Moderately Inaccurate
(E). Very Inaccurate

Answer:"""

dataset = getItems(ITEMPATH, TEST_TYPE)

batch_size = 1
result = []

for i in range(0, len(dataset), batch_size):
    batch = dataset[i : i + batch_size]
    questions = [template.format(item["text"].lower()) for _, item in batch.iterrows()]

    messages = [
        {"role": "system", "content": "You are an assistant that helps answer questions about personality traits."}
    ]

    for question in questions:
        messages.append({"role": "user", "content": question})

    response = client.messages.create(
        model="claude-3-opus-20240229",  # Change model if needed (opus, sonnet, haiku)
        max_tokens=400,
        temperature=0,
        messages=messages
    )

    for j, item in enumerate(batch.itertuples(index=False)):
        result.append((item, questions[j], response.content[0].text))  # Extract response text
        print(response.content[0].text, item.label_16_pf)

# Save results
with open("anthropic-neutral-path-to-save.pickle", "wb+") as f:
    pickle.dump(result, f)
