import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from adjustText import adjust_text

# --- 0. read neutral table ------------------------------------------------
neutral = pd.read_csv("gemini_sac_neutral.csv", index_col="Trait")["Mean"]  # Series
# ---------------------------------------------------------------------------
# 1.  Load & clean the three intensity matrices
# ---------------------------------------------------------------------------
files = {
    1: "gemini_sac_intensity_1.csv",          # intensity 1   (neutral-subtracted)
    3: "gemini_sac_intensity_3.csv",  # intensity 3
    5: "gemini_sac_intensity_5.csv"   # intensity 5
}

dfs = {}                       # {intensity: DataFrame}
for intensity, fp in files.items():
    df = pd.read_csv(fp)
    df.set_index(df.columns[0], inplace=True, drop=True)        # first col → index
    df.index   = df.index.str.strip().str.upper()               # standardise labels
    df.columns = df.columns.str.strip().str.upper()
    dfs[intensity] = df

# --- 1. subtract ----------------------------------------------------------
dfs_delta = {}
for intensity, df in dfs.items():          # dfs came from your earlier loader
    dfs_delta[intensity] = df.sub(neutral, axis=1)   # column-wise subtract

df1, df3, df5 = dfs_delta[1], dfs_delta[3], dfs_delta[5]
traits        = df1.index.tolist() 

def plot_profile(ax, target, k=3):
    # ----- pick top-k co-movers -------------------------------------------
    delta_abs = (df5.loc[target] - df1.loc[target]).abs()
    top_cols  = delta_abs.nlargest(k).index.tolist()
    plot_cols = [target] + top_cols

    texts = []      # collect Text objects for adjustText later

    # ----- plot lines & cache labels ---------------------------------------
    for col in plot_cols:
        y = [df1.loc[target, col],
             df3.loc[target, col],
             df5.loc[target, col]]

        ax.plot([1, 3, 5], y,
                marker='o',
                linewidth=2 if col == target else 1,
                color='tab:green' if col == target else None)  # keeps target distinct

        if col != target: 
            if col == "EMOTIONAL STABILITY":
                texts.append(ax.text(5.15, y[-1] - 0.1, "EMOTIONAL", fontsize=9, va='center', ha='left'))  # Adjust y position
                texts.append(ax.text(5.15, y[-1] - 0.15, "STABILITY", fontsize=9, va='center', ha='center'))  # Adjust y position
            else:
                texts.append(ax.text(5.15, y[-1], col, fontsize=10, va='center', ha='left'))

    # ----- automatically nudge labels to avoid overlaps --------------------
    # (only in y-direction so they stay aligned to x=5.15)
    adjust_text(texts, only_move={'points': 'y', 'text': 'y'},
                ax=ax,  # limit optimisation to this subplot
                expand_points=(1.2, 1.4))        # small extra spacing

    # for t in texts:
    #     if t.get_text() == "EMOTIONALITY":          # ← the label that still overlaps
    #         t.set_y(t.get_position()[1] - 0.15)  # move it up (or −0.15 to drop)
    #         break     
    # ----- cosmetics -------------------------------------------------------
    ax.axhline(0, ls='--', lw=.7, color='grey')
    ax.set_xticks([1, 3, 5])
    ax.set_xlim(1, 5.5)
    ax.set_title(target.title(), fontsize=14, weight='bold')
    ax.tick_params(axis='both', labelsize=13)


# ---------------------------------------------------------------------------
# 3.  Build the 4 × 4 grid
# ---------------------------------------------------------------------------

fig, axes = plt.subplots(4, 4, figsize=(12, 12), sharex=True, sharey=True)
axes = axes.flatten()

for idx, (ax, trait) in enumerate(zip(axes, traits)):
    plot_profile(ax, trait, k=3)

    # # put a legend in the first subplot of every row (idx // 4 gives the row)
    # if idx % 4 == 0:
    #     ax.legend(frameon=False, fontsize=6, loc='upper left')

# Create a custom legend for the whole grid
handles = [
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='tab:green', markersize=10, label='Target Trait(title of the subplot)'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='tab:blue', markersize=10, label='Most Closely Related Trait'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='tab:orange', markersize=10, label='Second Most Closely Related Trait')
]

fig.legend(handles=handles, loc='upper center', fontsize=14, ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.95))


# hide any extra empty axes (if trait count < grid size)
for ax in axes[len(traits):]:
    ax.set_visible(False)

# global labels & layout
# fig.suptitle("Target-Trait Trajectories and Top-2 Co-movers (Δ vs. neutral)",
            #  y=0.92, fontsize=14)
fig.text(0.5, 0.04, "Intensity level", ha='center', fontsize=14)
fig.text(0.04, 0.5, "Δ score", va='center', rotation='vertical', fontsize=14)
fig.tight_layout(rect=[0.05, 0.06, 0.95, 0.9])

# Adjust subplot spacing
fig.subplots_adjust(hspace=0.25, wspace=0.25)

# ---------------------------------------------------------------------------
# 4.  Save to disk
# ---------------------------------------------------------------------------
out_pdf = Path("influence_profiles_grid.pdf")
out_png = Path("influence_profiles_grid.png")
fig.savefig(out_pdf)           # vector quality
fig.savefig(out_png, dpi=300)  # high-res raster

print(f"Saved: {out_pdf}  |  {out_png}")
plt.show()
