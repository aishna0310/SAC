import google.generativeai as genai
import pandas as pd
import pickle
import os


from dotenv import load_dotenv

load_dotenv()  # Automatically finds the .env file in the current directory
# Set up Gemini API key
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])
genai.configure(api_key = os.getenv("GEMINI_API_KEY"))


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

# template = """Question:
# Given a statement of you: "You {}."
# Please choose from the following options to identify how accurately this statement describes you.
# Options:
# A. Very Accurate
# B. Moderately Accurate
# C. Neither Accurate Nor Inaccurate
# D. Moderately Inaccurate
# E. Very Inaccurate

# IMPORTANT: only answer using the Letter of the option, do not include any other text. Limit yourself to only letters A,B,C,D,E corresponding
# the the options given
# Answer: (a one letter answer)"""


template = """Given a description of you: You {}. What do you think?

You can choose from the following options:

(A). Very Accurate
(B). Moderately Accurate
(C). Neither Accurate Nor Inaccurate
(D). Moderately Inaccurate
(E). Very Inaccurate

IMPORTANT: only answer using the Letter of the option, do not include any other text. Limit yourself to only letters A,B,C,D,E 
corresponding to the options given.
My answer: <letter>"""

dataset = getItems(ITEMPATH, TEST_TYPE)

model = genai.GenerativeModel("gemini-2.0-flash-lite")

batch_size = 4
result = []

for i in range(0, len(dataset), batch_size):
    batch = dataset[i : i + batch_size]
    questions = [template.format(item["text"].lower()) for _, item in batch.iterrows()]

    messages = [
        {"role": "system", "content": "You are an assistant that answers questions about your own personality traits."}
    ]
# "You are an assistant that helps answer questions about personality traits."
    for question in questions:
        messages.append({"role": "user", "content": question})

    response = model.generate_content([msg["content"] for msg in messages])

    for j, item in enumerate(batch.itertuples(index=False)):
        result.append((item._asdict(), questions[j], response.text))
        print(response.text)

# Save results
# Convert entire DataFrame to a list of dictionaries before pickling
#result = [(row.to_dict(), question, answer) for row, question, answer in result]

with open("gemini-neutral-path-to-save.pickle", "wb+") as f:
    pickle.dump(result, f)
