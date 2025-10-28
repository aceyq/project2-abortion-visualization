import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load Excel
excel_path = "GuttmacherInstituteAbortionDataByState.xlsx"
df_raw = pd.read_excel(excel_path)

# Helper to find columns flexibly
def find_col(df, candidates, contains=None):
    cols = list(df.columns)
    for c in candidates:
        if c in cols:
            return c
    if contains:
        for col in cols:
            low = col.lower()
            if all(frag.lower() in low for frag in contains):
                return col
    return None

# Identify key columns
state_col = find_col(df_raw, ["U.S. State"], contains=["state"])
no_clinic_col = find_col(
    df_raw,
    ["% of counties without a known clinic, 2020"],
    contains=["counties", "clinic", "2020"]
)
travel_col = find_col(
    df_raw,
    ["% of residents obtaining abortions who traveled out of state for care, 2020"],
    contains=["traveled", "out", "state", "2020"]
)

# Rename for easier reference
rename_map = {}
if state_col:
    rename_map[state_col] = "state"
if no_clinic_col:
    rename_map[no_clinic_col] = "pct_counties_no_clinic_2020"
if travel_col:
    rename_map[travel_col] = "pct_traveled_outstate_2020"
df = df_raw.rename(columns=rename_map)

# Keep and clean
use = ["state", "pct_counties_no_clinic_2020", "pct_traveled_outstate_2020"]
missing = [c for c in use if c not in df.columns]  # CORRECTED THIS LINE
if missing:
    raise ValueError(f"Missing columns: {missing}")

for c in ["pct_counties_no_clinic_2020", "pct_traveled_outstate_2020"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

plot_df = df.dropna(subset=["pct_counties_no_clinic_2020", "pct_traveled_outstate_2020"])

# Data
x = plot_df["pct_counties_no_clinic_2020"].values
y = plot_df["pct_traveled_outstate_2020"].values

# Calculate correlation for annotation
correlation = np.corrcoef(x, y)[0, 1]
r_squared = correlation ** 2

# Trend line
m, b = np.polyfit(x, y, 1)
x_line = np.linspace(np.nanmin(x), np.nanmax(x), 100)
y_line = m * x_line + b

# Create figure with better styling
plt.figure(figsize=(10, 7))

# Create scatter plot with color intensity based on x values
scatter = plt.scatter(
    x, y,
    c=x, cmap='Reds',
    alpha=0.7, s=60,
    edgecolors='black', linewidth=0.5
)
plt.colorbar(scatter, label='% Counties Without Clinic →')

# Plot trend line
plt.plot(x_line, y_line, 'r--', linewidth=2, label=f'Trend (R² = {r_squared:.3f})')

# Annotate selected states - choose states that tell a story
highlight_states = [
    "Mississippi", "Louisiana", "Kentucky", "Missouri", "Wyoming",
    "Illinois", "Colorado", "California"
]
for s in highlight_states:
    row = plot_df[plot_df["state"] == s]
    if not row.empty:
        xv = float(row["pct_counties_no_clinic_2020"].iloc[0])
        yv = float(row["pct_traveled_outstate_2020"].iloc[0])
        plt.annotate(
            s, (xv, yv),
            xytext=(8, 8), textcoords="offset points",
            fontsize=9, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow', alpha=0.7)
        )

# Improved axis labels & title
plt.xlabel(
    "% of Counties Without an Abortion Clinic (2020)\n← More Accessible | More Restrictive →",
    fontsize=12
)
plt.ylabel(
    "% of Residents Traveling Out of State\nfor Abortion Care (2020)",
    fontsize=12
)
plt.title(
    "Limited Clinic Access Correlates with Higher Out-of-State Abortion Travel",
    fontsize=14, fontweight='bold', pad=20
)

# Add explanatory text box
textstr = (
    f"• Strong positive correlation (r = {correlation:.3f})\n"
    f"• As clinic access decreases, out-of-state travel increases\n"
    f"• Data supports argument that restrictions displace rather than prevent abortions"
)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
plt.text(
    0.02, 0.98, textstr, transform=plt.gca().transAxes,
    fontsize=10, verticalalignment='top', bbox=props
)

plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("prop1_against_scatter_improved.png", dpi=200, bbox_inches='tight')
plt.show()

print(f"Correlation coefficient: {correlation:.3f}")
print(f"R-squared: {r_squared:.3f}")
print("Saved: prop1_against_scatter_improved.png")