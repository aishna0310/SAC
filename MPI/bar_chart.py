import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load your CSV file
file_path = "ECAI-Results - sac_deltas.csv"  # Replace with your local path
df = pd.read_csv(file_path)
# Define traits and intensity labels
traits = df.columns[1:].tolist()
intensity_labels = ['Delta 1', 'Delta 3', 'Delta 5']
models = ['Claude', 'GPT4o', 'Gemini']

# Prepare the data structure
data = {
    'Trait': [],
    'Model': [],
    'Delta Intensity': [],
    'Value': []
}

# Append model data helper
def append_model_data_fixed(start_row, model_name):
    for i, intensity in enumerate(intensity_labels):
        row = df.iloc[start_row + i, 1:].astype(float)
        data['Trait'].extend(traits)
        data['Model'].extend([model_name] * len(traits))
        data['Delta Intensity'].extend([intensity] * len(traits))
        data['Value'].extend(row.tolist())

# Extract rows: Claude 0–2, GPT4o 5–7, Gemini 10–12
append_model_data_fixed(0, 'Claude')
append_model_data_fixed(5, 'GPT4o')
append_model_data_fixed(10, 'Gemini')

# Create long-form DataFrame
long_df = pd.DataFrame(data)

# Create a separate PDF for each intensity level
# Set Seaborn style and font scale
sns.set(style="whitegrid", font_scale=1.2)  # Increase font scale globally

for intensity in intensity_labels:
    plt.figure(figsize=(16, 5))
    subset = long_df[long_df['Delta Intensity'] == intensity]
    sns.barplot(data=subset, x='Trait', y='Value', hue='Model')

    # Add title and label formatting
    plt.title(f'Trait Intensities Compared Across LLMs - {intensity}', fontsize=16)
    plt.xlabel("Trait", fontsize=14)
    plt.ylabel("Δ Score", fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    # plt.legend(title='Model', fontsize=12, title_fontsize=13)
    plt.legend(
    title='Model',
    fontsize=12,
    title_fontsize=13,
    loc='upper left',              # position legend inside top-left
    bbox_to_anchor=(1.02, 1),      # offset to the right of the plot
    borderaxespad=0                # reduce padding
)

    plt.tight_layout()
    filename = f"LLM_Trait_Intensity_{intensity.replace(' ', '_')}.pdf"
    plt.savefig(filename)
    plt.close()
    print(f"Saved: {filename}")
