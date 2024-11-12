import openai
import os
from consts import personality_intensity_dict, p2_descriptions
import pandas as pd
import numpy as np

openai.api_key = os.environ["OPENAI_API_KEY"]


# Load the CSV files
traits_df = pd.read_csv("../inventories/MPI_Modified - 16_Intensity_Questions.csv")  # Load 16 intensity questions
intensity_df = pd.read_csv("../inventories/MPI_Modified - 16_Intensity_Questions.csv")  # Load intensity template

# Function to build the prompt with dynamic intensity
def build_prompt(trait_const, trait, question, intensity_question, intensity_answers, intensity_scale):
    trait_const = trait_const.upper()
    trait = trait.upper()
    adjectives = personality_intensity_dict.get(trait_const, {})
    definition = p2_descriptions.get(trait_const)

    # Dynamically fill in the template and add it to the end of the question batch
    template = f"""
    Personality intensity is defined as a combination of 5 factors including frequency, depth, threshold, effort, and willingness, rated on a scale of 1 to 5.
    
    The trait {trait_const} would be described as: {definition}

    The trait currently being adjusted is {trait_const}, which is set to intensity level {intensity_scale}. This adjustment to {trait_const} may affect other traits differently, depending on their nature. 
    Traits which are not {trait_const}, such as {trait}, should maintain or adapt to the given context but not necessarily follow the same intensity.
    It is important to note that while {trait_const} is set to {intensity_scale}, the intensity of other traits like {trait} may vary and should be independently assessed.

    Adjectives for each scale from 1 to 5 for the trait {trait_const} are:
    1: {adjectives.get(1, 'N/A')}, 
    2: {adjectives.get(2, 'N/A')}, 
    3: {adjectives.get(3, 'N/A')}, 
    4: {adjectives.get(4, 'N/A')}, 
    5: {adjectives.get(5, 'N/A')}
    
    The intensity for the trait {trait} should reflect how it behaves independently or in contrast with the modified intensity of {trait_const}.

    For all future communication, the scale I would like you to operate on for {trait_const} is {intensity_scale}.
    
    Task:
    {intensity_question} {question}?

    The possible intensity scale is 1 to 5, with corresponding descriptions as follows:
    1: {intensity_answers[0]}, 
    2: {intensity_answers[1]}, 
    3: {intensity_answers[2]}, 
    4: {intensity_answers[3]}, 
    5: {intensity_answers[4]}
    
    For each question, please provide an answer that best represents the trait {trait} at the intensity 
    of {trait_const} and exclusively give me the answer in the format - <number> 
    ensure there is no other text in the answer
    """
    # the format would be how often do you cheer someone up followed by the 5 options that it needs to pick from
    return template

# Function to call the OpenAI API for a given prompt

def get_response(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o",  # Use a relevant model
        messages=[
            {"role": "system", "content": "You are an assistant that helps answer questions about personality traits."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,  # Adjust based on expected length of batch response
        temperature=0.7  # Adjust the temperature if needed
    )
    return response.choices[0].message.content.strip()


# Initialize a dictionary to store the results
results = {}
trait_const = "EMOTIONALITY"
intensity = 5
# Loop over each trait and its questions
for index, row in traits_df.iterrows():
    trait = row['Personality']
    question_1 = row['Question1']
    question_2 = row['Question2']
    question_3 = row['Question3']
    
    # Filter the intensity_df to get the matching intensity factor and answers for the trait
    for i, intensity_row in intensity_df.iterrows():
        intensity_question = intensity_row['Question'] #the question row from the questionnaire csv
        intensity_answers = intensity_row[['1', '2', '3', '4', '5']].tolist() #the corresponding scale and options
        
        # Generate prompts for both questions with dynamic intensity and appended template
        prompt_1 = build_prompt(trait_const, trait, question_1, intensity_question, intensity_answers, intensity_scale=intensity)
        prompt_2 = build_prompt(trait_const, trait, question_2, intensity_question, intensity_answers, intensity_scale=intensity)
        prompt_3 = build_prompt(trait_const, trait, question_3, intensity_question, intensity_answers, intensity_scale=intensity)
            
        # Get responses from the OpenAI API
        response_1 = get_response(prompt_1)
       
        response_2 = get_response(prompt_2)
        
        response_3 = get_response(prompt_3)

            
        # Convert the responses to numeric intensity scores
        score_1 = float(response_1)
        score_2 = float(response_2)
        score_3 = float(response_3)
            
        # Store the scores for the trait and intensity scale
        if trait not in results:
            results[trait] = []
        # if intensity not in results[trait]:
        #     results[trait][intensity] = []
                
        # results[trait][intensity].extend([score_1, score_2])
        results[trait].extend([score_1, score_2, score_3])

# Calculate the mean and variance for each trait at different intensity scales
summary_stats = {}
for trait, scores in results.items():
    mean_score = np.mean(scores)
    variance_score = np.var(scores)
    summary_stats[trait] = {'mean': mean_score, 'variance': variance_score}

# Output the results
for trait, stats in summary_stats.items():
    print(f"Trait: {trait}, Mean: {stats['mean']}, Variance: {stats['variance']}")