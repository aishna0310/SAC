import requests
import pandas as pd
import pickle
import os

# Set up DeepSeek API key
DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
API_URL = "https://api.deepseek.com/v1/chat/completions"

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

    # DeepSeek API request
    response = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "deepseek-chat",  # Change if using a different DeepSeek model
            "messages": messages,
            "temperature": 0,
            "max_tokens": 400
        }
    )

    response_data = response.json()

    if "choices" in response_data and len(response_data["choices"]) > 0:
        answer_text = response_data["choices"][0]["message"]["content"]
    else:
        answer_text = "Error: No response"

    for j, item in enumerate(batch.itertuples(index=False)):
        result.append((item, questions[j], answer_text))
        print(answer_text, item.label_16_pf)

# Save results
with open("deepseek-neutral-path-to-save.pickle", "wb+") as f:
    pickle.dump(result, f)
