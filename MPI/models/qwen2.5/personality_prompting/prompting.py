from worker import qwen_inventory
from dotenv import load_dotenv
from consts import (
    vignettes, #dont need vignettes
    trait_words,
    p2_descriptions,
    p2_descriptions_reversed,
    trait_words_reversed,
    naive_prompt,
    trait_words_searched,
    trait_words_searched_reverse,
)
import os
import json

load_dotenv()

def get_p2_descriptions():
    words_template = """Given some key words of {trait} person: {d1}, {d2}, {d3}, {d4}, {d5}, and {d6}. A second-person view of {trait} person:"""
    t = 0.0

    descriptions = {}

    for trait, words in trait_words.items():
        d1, d2, d3, d4, d5, d6 = words
        result = words_template.format(
            trait=trait, d1=d1, d2=d2, d3=d3, d4=d4, d5=d5, d6=d6
        )
        response = openai.chat.completions.create(
            model="gpt-4o", #change model here
            messages=[
        {"role": "system", "content": "You are an assistant that helps answer questions about personality traits."},
        {"role": "user", "content": result}  # 'result' now becomes the user's message
    ],
            temperature=t,
            max_tokens=400,
            top_p=1.0,
        )
        descriptions[trait] = response["choices"][0].message.content.strip()

    return descriptions


def get_p2_descriptions_negative():
    words_template = """Given some key words of {trait} person: {d1}, {d2}, {d3}, {d4}, {d5}, and {d6}. A second-person view of {trait} person:"""
    t = 0.0

    descriptions = {}

    for trait, words in trait_words_reversed.items():
        d1, d2, d3, d4, d5, d6 = words
        result = words_template.format(
            trait=trait, d1=d1, d2=d2, d3=d3, d4=d4, d5=d5, d6=d6
        )
        response = openai.chat.completions.create(
            model="gpt-4o", #change model here
            messages=[
        {"role": "system", "content": "You are an assistant that helps answer questions about personality traits."},
        {"role": "user", "content": str(result)}  # 'result' now becomes the user's message
    ],
            temperature=t,
            max_tokens=400,
            top_p=1.0,
        )
        descriptions[trait] = response["choices"][0].message.content.strip()
    return descriptions


def get_inventory_result(prompts, aux=""):
    for trait, prompt in prompts.items():
        print(trait)
        qwen_inventory(prompt, trait, aux)
        #comment out the ones not in use



def get_opposite():
    for dim, words in trait_words.items():
        for word in words:
            result = f"Antonyms of {word} is:"
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
        {"role": "system", "content": "You are an assistant that helps answer questions about personality traits."},
        {"role": "user", "content": str(result)}  # 'result' now becomes the user's message
    ],
                temperature=0,
                max_tokens=400,
                top_p=1.0,
            )
            print(result, response["choices"][0]["text"])


def words_prompt(trait_words_searched):
    return dict(
        (k, f"You have the traits of {', '.join(v)}.")
        for k, v in trait_words_searched.items()
    )


if __name__ == "__main__":
    # get_inventory_result(naive_prompt, 'naive')  # naive prompting
    # get_inventory_result(words_prompt(trait_words_searched), 'auto') # words auto prompting
    get_inventory_result(p2_descriptions, 'p2')  # P^2 prompting
    #print(get_p2_descriptions()) # generate P^2 prompts from scratch



#48 different pickle files for 3 calls made to get_inventory result 
#we need to run parser 48 different times to get scores for each trait for each call

