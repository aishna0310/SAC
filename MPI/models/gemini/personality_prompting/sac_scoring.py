import pandas as pd
import os
import numpy as np
from consts import p2_descriptions


#this is the neutral version of the LLM - to understand what the LLM would say with no instructions prior

# Load the CSV files
traits_df = pd.read_csv("../inventories/MPI_Modified - 16_Intensity_Questions.csv")  # Load 16 intensity questions
intensity_df = pd.read_csv("../inventories/MPI_Modified - 16_Intensity_Questions.csv")  # Load intensity template

# Set up API keys
gemini_api_key = os.environ["GEMINI_API_KEY"]


# Function to generate batch prompt for multiple questions
def generate_batch_prompt(trait, questions, intensity_factor, intensity_answers):
    # Concatenate multiple questions into a single prompt
    definition = p2_descriptions.get(trait)
    questions_str = "\n\n".join([f"Q{i+1}: {q}" for i, q in enumerate(questions)])
    return f"""
    The trait {trait} is defined by {definition}
    For the trait '{trait}' with the intensity factor '{intensity_factor}', please answer the following questions: 
    
    {questions_str}
    
    The possible intensity scale is 1 to 5, with corresponding descriptions as follows:
    1: {intensity_answers[0]}, 
    2: {intensity_answers[1]}, 
    3: {intensity_answers[2]}, 
    4: {intensity_answers[3]}, 
    5: {intensity_answers[4]}
    
    For each question, please provide a number between 1 and 5 that best represents the intensity.
    Always give me the answer in a format - Answer: <number>
    """

import google.generativeai as genai

def get_batch_response_gemini(prompt):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text


# Initialize dictionaries to store results for each model
results_gemini = {}


# Loop over each trait and its questions
for index, row in traits_df.iterrows():
    trait = row['Personality']
    question_1 = row['Question1']
    question_2 = row['Question2']
    # question_3 = row['Question3']
    
    # List of questions to send in a single batch
    # questions = [question_1, question_2, question_3]
    questions = [question_1, question_2]
    
    # Filter the intensity_df to get the matching intensity factor and answers for the trait
    for i, intensity_row in intensity_df.iterrows():
        intensity_factor = intensity_row['Intensity factor']
        intensity_question = intensity_row['Question']
        intensity_answers = intensity_row[['1', '2', '3', '4', '5']].tolist()

        questions[0]=intensity_question + questions[0]
        questions[1]=intensity_question + questions[1]
        # questions[2]=intensity_question + questions[2]
        
        # Generate a single batch prompt for both questions - might need diff prompts for diff models
        batch_prompt = generate_batch_prompt(trait, questions, intensity_factor, intensity_answers)
        
        # Get response from the APIs for the batch prompt - comment out whats not needed
        gemini_response = get_batch_response_gemini(batch_prompt)
        
        # Try to extract numerical values from the responses for each question
        try:
            gemini_responses = gemini_response.split("\n")
            gemini_score_1 = float(gemini_responses[0].split(":")[-1].strip())
            gemini_score_2 = float(gemini_responses[1].split(":")[-1].strip())
            if trait not in results_gemini:
                results_gemini[trait] = []
            results_gemini[trait].extend([gemini_score_1, gemini_score_2])
        except (ValueError, IndexError) as e:
            print(f"Error processing Gemini response: {e}")
        

# Calculate stats for each model
def calculate_stats(results):
    summary_stats = {}
    for trait, scores in results.items():
        mean_score = np.mean(scores)
        variance_score = np.var(scores)
        summary_stats[trait] = {'mean': mean_score, 'variance': variance_score}
    return summary_stats

#comment out stats which are not needed
gemini_stats = calculate_stats(results_gemini)

# Print or save results for comparison
for trait in traits_df['Personality'].unique():
    print(f"\nTrait: {trait}")
    print(f"Gemini - Mean: {gemini_stats[trait]['mean']}, Variance: {gemini_stats[trait]['variance']}")

#["For the trait 'WARMTH' with the intensity factor 'Frequency':", '', 'Q1: Know how to comfort others.  ', '**Answer: 4 (Often)**', '', 'Q2: Cheer people up.  ', '**Answer: 4 (Often)**']