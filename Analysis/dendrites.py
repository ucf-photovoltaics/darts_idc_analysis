import adds
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

master = adds.get_master(dendrite_score_col=True)

# Add columns for RGB difference
master["Red"] = master["R_EXPOSED"] - master["R_PRISTINE"]
master["Green"] = master["G_EXPOSED"] - master["G_PRISTINE"]
master["Blue"] = master["B_EXPOSED"] - master["B_PRISTINE"]

# Convert to long for easy plotting
master = pd.melt(
    master,
    id_vars=["Board ID", "Sensor", "Pattern"],
    value_vars=["Red", "Green", "Blue"], # Possible values stored in Channel column
    var_name="Channel", # A channel column will be added, storing "R_Diff"...
    value_name="Channel Difference" # This column will be added, storing a number
)

# Create a FacetGrid
g = sns.FacetGrid(
    data=master,
    col="Channel",
    margin_titles=True,
    hue="Channel",
    palette={"Red": "#FF0000", "Green": "#00FF00", "Blue": "#0000FF"}
)

# Create a lineplot on the FacetGrid
g.map_dataframe(
    sns.boxplot,
    x="Pattern", y="Channel Difference",
)

# Set the text of the titles
g.set_titles(col_template="{col_name}")

# Set ticks to ints, not floats
g.set_xticklabels([1, 4, 7, 10])

plt.show()
