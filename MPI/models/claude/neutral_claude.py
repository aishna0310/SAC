import openai
import pandas as pd
import pickle
import os
import time

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

ITEMPATH = r"..\..\MPI_Modified - 16PF_Inventory.csv"  # Load the 16 PF inventory
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

dataset = getItems(ITEMPATH, TEST_TYPE)

for temperature in [0]:
    batch_size = 1
    result = []
    for i in range(0, len(dataset), batch_size):
        batch = dataset[i : i + batch_size]
        
        # Build all question prompts for this batch
        questions = [
            template.format(item["text"].lower()) for _, item in batch.iterrows()
        ]
        
        # Create your initial messages list (which can contain system or user instructions)
        messages = [
            {
                "role": "user",
                "content": "You are an assistant that answers questions about your own personality traits."
            }
        ]
        
        # Add each question to the `messages` list
        for question in questions:
            messages.append({"role": "user", "content": question})
        
        # Now call the chat completion with the messages
        completion = client.chat.completions.create(
            model="anthropic/claude-3.7-sonnet:beta",
            messages=messages
        )

        # If this call returns N=1 choice, you will typically have only `completion.choices[0]`.
        # If you need separate completions per question, you can either:
        #   (1) Make multiple calls (one per question), or
        #   (2) Use `completion.choices` if your call is returning multiple completions.
        
        # For now, just handle the single typical answer:
        for j, response in enumerate(completion.choices):
            # Save the result
            result.append((batch.iloc[j], questions[j], response))
            print(response.message.content)
            
    # Save the entire result list for all processed items
    with open("openai-neutral-path-to-save.pickle", "wb+") as f:
        pickle.dump(result, f)
