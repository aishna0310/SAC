import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df1 = pd.read_csv("ECAI-Results - openai_intensity_1.csv")

df3 = pd.read_csv("ECAI-Results - openai_intensity_3.csv")

df5 = pd.read_csv("ECAI-Results - openai_intensity_5.csv")

# clean up labels once
for df in (df1, df3, df5):
    df.set_index(df.columns[0], inplace=True, drop=True)
    df.index   = df.index.str.strip().str.upper()
    df.columns = df.columns.str.strip().str.upper()


# Load the CSV file
# file_path = "ECAI-Results - openai_intensity_3.csv"
# df = pd.read_csv(file_path)

# # Set the index to the first column (trait names)
# df.set_index(df.columns[0], inplace=True)

# # Generate a heatmap
# plt.figure(figsize=(12, 10))
# sns.heatmap(df, annot=True, fmt=".2f", cmap="coolwarm", square=True, cbar_kws={'label': 'Score'})
# plt.title("Trait-to-Trait Relationship Heatmap")
# plt.xticks(rotation=45, ha='right')
# plt.yticks(rotation=0)

# # Add axis labels
# plt.xlabel("Traits (Columns)", fontsize=12)
# plt.ylabel("Target trait (Rows)", fontsize=12)

# plt.tight_layout()

# # Save as PDF
# plt.savefig("trait_heatmap.pdf", format='pdf')

# # Show the plot (optional if you're only saving)
# plt.show()

def plot_influence_profile(target, k=3,
                           df1=df1, df3=df3, df5=df5,
                           save=False, fname_prefix="profile"):
    """
    Plots the target trait’s Δ-score trajectory across the
    three intensity levels, together with its top-k co-moving traits.

    Parameters
    ----------
    target : str
        Row/column name of the trait you want as the focus.
    k : int, default 3
        Number of non-self traits with the largest absolute change
        (|Δ Int5 – Δ Int1|) to include.
    df1, df3, df5 : pandas.DataFrame
        Neutral-subtracted matrices at intensities 1, 3, 5.
    save : bool, default False
        If True, saves a vector PDF and a 300 dpi PNG.
    fname_prefix : str
        File name stem when save=True.
    """
    # --- pick allies ---------------------------------------------------------
    delta_end   = (df5.loc[target] - df1.loc[target]).abs()
    top_cols    = delta_end.nlargest(k).index.tolist()
    plot_cols   = [target] + top_cols

    # --- gather y-values -----------------------------------------------------
    data = {1: df1.loc[target, plot_cols],
            3: df3.loc[target, plot_cols],
            5: df5.loc[target, plot_cols]}

    # --- plotting ------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(5, 3.2))
    for col in plot_cols:
        y = [data[intensity][col] for intensity in [1, 3, 5]]
        ax.plot([1, 3, 5], y,
                marker='o',
                linewidth=2 if col == target else 1,
                label=col)

    ax.axhline(0, ls='--', lw=.8, color='grey')
    ax.set_xticks([1, 3, 5]);  ax.set_xlabel("Intensity level")
    ax.set_ylabel("Δ score vs. neutral")
    ax.set_title(f"{target}: trajectory + top-{k} co-movers")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()

    if save:
        pdf_path = f"{fname_prefix}_{target}.pdf"
        png_path = f"{fname_prefix}_{target}.png"
        fig.savefig(pdf_path, format="pdf")
        fig.savefig(png_path, dpi=300)
        print(f"saved to {pdf_path} | {png_path}")

    plt.show()

plot_influence_profile("DISTRUST",k=7,save=True)
