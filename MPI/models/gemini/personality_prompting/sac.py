import google.generativeai as genai
import os
import pandas as pd
import numpy as np
from consts import personality_intensity_dict, p2_descriptions

# Set up API keys
gemini_api_key = os.environ["GEMINI_API_KEY"]
#this file adds the adjectives from intensity and then calculates you would first run sac_scoring then sac 


# Load the CSV files
traits_df = pd.read_csv("../inventories/MPI_Modified - 16_Intensity_Questions.csv")  # Load 16 intensity questions
intensity_df = pd.read_csv("../inventories/MPI_Modified - 16_Intensity_Questions.csv")  # Load intensity template

# Function to build the prompt with dynamic intensity
#might have to make new templates for each model - handle during testing
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

def get_response_gemini(prompt):
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text.strip()

# Process responses for each model
def process_results_for_model(model_name, response_function):
    results = {}
    trait_const = "EMOTIONALITY"
    intensity = 5
    
    for index, row in traits_df.iterrows():
        trait = row['Personality']
        question_1 = row['Question1']
        question_2 = row['Question2']
        question_3 = row['Question3']
        
        for i, intensity_row in intensity_df.iterrows():
            intensity_question = intensity_row['Question']
            intensity_answers = intensity_row[['1', '2', '3', '4', '5']].tolist()
            
            prompt_1 = build_prompt(trait_const, trait, question_1, intensity_question, intensity_answers, intensity_scale=intensity)
            prompt_2 = build_prompt(trait_const, trait, question_2, intensity_question, intensity_answers, intensity_scale=intensity)
            prompt_3 = build_prompt(trait_const, trait, question_3, intensity_question, intensity_answers, intensity_scale=intensity)
                
            try:
                response_1 = response_function(prompt_1)
                response_2 = response_function(prompt_2)
                response_3 = response_function(prompt_3)
                
                score_1 = float(response_1)
                score_2 = float(response_2)
                score_3 = float(response_3)
                
                if trait not in results:
                    results[trait] = []
                results[trait].extend([score_1, score_2, score_3])
            except Exception as e:
                print(f"Error processing {model_name} response for trait {trait}: {e}")
    
    # Calculate statistics
    summary_stats = {}
    for trait, scores in results.items():
        mean_score = np.mean(scores)
        variance_score = np.var(scores)
        summary_stats[trait] = {'mean': mean_score, 'variance': variance_score}
    
    return summary_stats

# Run the process for each model - comment out whatever is not necessary
gemini_stats = process_results_for_model("Gemini", get_response_gemini) 

# Output results for OpenAI
# Output results for Gemini
print("\nGemini Results:")
for trait, stats in gemini_stats.items():
    print(f"Trait: {trait}, Mean: {stats['mean']}, Variance: {stats['variance']}")

# # Print comparison of results across models
# for trait in traits_df['Personality'].unique():
#     print(f"\nTrait: {trait}")
#     if trait in openai_stats:
#         print(f"OpenAI - Mean: {openai_stats[trait]['mean']}, Variance: {openai_stats[trait]['variance']}")
#     if trait in claude_stats:
#         print(f"Claude - Mean: {claude_stats[trait]['mean']}, Variance: {claude_stats[trait]['variance']}")
#     if trait in gemini_stats:
#         print(f"Gemini - Mean: {gemini_stats[trait]['mean']}, Variance: {gemini_stats[trait]['variance']}")
#     if trait in deepseek_stats:
#         print(f"DeepSeek - Mean: {deepseek_stats[trait]['mean']}, Variance: {deepseek_stats[trait]['variance']}")


# # Output the results
# for trait, stats in summary_stats.items():
#     print(f"Trait: {trait}, Mean: {stats['mean']}, Variance: {stats['variance']}")