import adds
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

def rgb_3d():
    master = adds.get_master()

    master.dropna(subset="Pattern", inplace=True)
    master["Pattern"] = master["Pattern"].apply(int).apply(str)

    # Melt the RGB columns
    master = master.melt(
        id_vars=["Pattern", "Board ID", "Sensor"],
        value_vars=["R_PRISTINE", "G_PRISTINE", "B_PRISTINE", "R_EXPOSED", "G_EXPOSED", "B_EXPOSED"],
        var_name="Channel_Age",
        value_name="Value"
    )

    # Split "Channel_Age" into "Channel" and "Age"
    master[["Channel", "Age"]] = master["Channel_Age"].str.extract(r"([RGB])_(PRISTINE|EXPOSED)")

    # Pivot to get R, G, B in separate columns, with "Age" as one of the columns
    master = master.pivot_table(
        index=["Pattern", "Board ID", "Sensor", "Age"],
        columns="Channel",
        values="Value"
    ).reset_index()

    fig = px.scatter_3d(
        master,
        x="R",
        y="G",
        z="B",
        color="Pattern",
        symbol="Age",
        symbol_map={"PRISTINE": "circle-open", "EXPOSED": "circle"},
        opacity=0.6,
        hover_data=["Pattern", "Board ID", "Sensor"]
    )

    return fig

def rgb_boxplots():
    master = adds.get_master()

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

    return g.figure

# Boxplots that show brightness difference between pristine/exposed images for each board pattern
def grayscale_boxplots():
    master=adds.get_master()

    # Add column for brightness difference
    master["Brightness Difference"]=master["Brightness Exposed"]-master["Brightness Pristine"]

    # make pattern categorical and ordered to make sure it is plotted correctly
    master["Pattern"]=pd.Categorical(master["Pattern"], categories=[1, 4, 7, 10], ordered=True)

    # plot
    return sns.boxplot(data=master, x="Pattern", y="Brightness Difference").get_figure()

# plots a scatterplot matrix of all variables to see how they are correlated
def scatterplot_matrix():
    # Get master data
    master=adds.get_master()

    # Rename Ph column to be correct
    master.rename(columns={'Ph': 'pH'}, inplace=True)

    # Drop NA values
    master.dropna(axis=1, how="all", inplace=True)

    # Drop non-numeric columns
    master=master.select_dtypes(include=["number"])

    # Plot
    axes=pd.plotting.scatter_matrix(master, figsize=(10, 10), alpha=1)

    # Rotate x and y labels so that they are more readable
    [ax.xaxis.label.set(rotation=45, ha="right") for ax in axes.flatten()]
    [ax.yaxis.label.set(rotation=45, ha="right") for ax in axes.flatten()]

    return axes[0, 0].get_figure()

def corr_heatmap():
    # Get master
    master = adds.get_master()
    # Drop columns that are entirely NaN
    master.dropna(axis=1, how="all", inplace=True)
    # Drop columns that are non-numeric
    master = master.select_dtypes(include=["number"])

    # Create a heatmap of the correlation matrix
    return sns.heatmap(master.corr(), annot=True, cmap="coolwarm").get_figure()

# Plot current vs time from all the CurrentTime files. The plots are grouped by
# solution, pattern, sensor, and voltage. This plot uses the master_current_time
# joined data.
def current_time():
    # Get joined data
    master_current_time = adds.get_master_current_time()

    # Add a unique sensor identifier
    master_current_time["Sensor ID"] = master_current_time["Board ID"] + "_" + master_current_time["Sensor"]

    figs = []

    # Plot Data --------------------------------------------------------------------
    # Plot for each unique voltage
    for voltage in master_current_time["Voltage"].unique():
        # Create a FacetGrid
        g = sns.FacetGrid(
            data=master_current_time[master_current_time["Voltage"] == voltage],
            row="Pattern", row_order=[1, 4, 7, 10],
            col="Solution", col_order=["DI Water", "Adipic Acid - 0.388mM", "Adipic Acid - 0.712mM", "Adipic Acid - 1.24mM", "Succinic 0.388mM", "Succinic 0.712 mM", "Succinic 1.425mM", "Succinic 3.6mM"],
            hue="Sensor", palette={"U1":"#FF0000", "U2":"#B6FF00", "U3":"#00FFFF", "U4":"#7F00FF"},
            margin_titles=True,
            sharex=False, sharey=False
        )

        # Create a lineplot on the FacetGrid
        g.map_dataframe(
            sns.lineplot,
            x="Time (ms)", y="Current (mA)",
            units="Sensor ID", estimator=None
        )

        # Set the text of the titles, which are already positioned properly
        g.set_titles(
            row_template="Pattern {row_name}",
            col_template="{col_name}"
        )

        # Remove all ticks and tick labels
        g.set(xticks=[], yticks=[], xticklabels=[], yticklabels=[])

        # Instead of an axis being L-shaped, make it a box
        for ax in g.axes.flat:
            ax.spines["top"].set_visible(True)
            ax.spines["right"].set_visible(True)

        # Adjust spacing
        g.figure.subplots_adjust(
            wspace=0,
            hspace=0,
            left=0.03,
            bottom=0.05,
            right=0.97,
            top=0.92
        )

        # Add legend
        g.add_legend(title="Sensor", edgecolor="#000000", frameon=True)

        # Add main title
        g.figure.suptitle(f"Current Vs Time, by Solution, Pattern, and Sensor ({int(voltage)}V)")

        figs.append(g.figure)
    
    return figs

# Plot mean failure time vs solution, separated by pattern, sensor, and voltage.
def fail_time_solution():
    # Get master data
    master = adds.get_master()

    # Drop NaN rows
    master.dropna(subset="Voltage", inplace=True)

    # Add column to store failure time in seconds
    master["Failure Time (s)"] = master["Time to Failure (ms)"] / 1000

    figs = []

    # Plot Data --------------------------------------------------------------------
    # Plot for each unique voltage
    for voltage in master["Voltage"].unique():
        # Create a FacetGrid
        g = sns.FacetGrid(
            data=master[master["Voltage"] == voltage],
            row="Pattern", row_order=[1, 4, 7, 10],
            hue="Sensor", palette={"U1":"#FF0000", "U2":"#B6FF00", "U3":"#00FFFF", "U4":"#7F00FF"},
            margin_titles=True,
            sharex=False, sharey=False
        )

        # Create scatterplots on the FacetGrid
        g.map_dataframe(
            sns.pointplot,
            x="Solution", y="Failure Time (s)",
            order=["DI Water", "Adipic Acid - 0.388mM", "Adipic Acid - 0.712mM", "Adipic Acid - 1.24mM", "Succinic 0.388mM", "Succinic 0.712 mM", "Succinic 1.425mM", "Succinic 3.6mM"],
            errorbar=None
        )

        # Shrink font size
        g.tick_params(labelsize="small")

        # Set the text of the titles, which are already positioned properly
        g.set_titles(
            row_template="Pattern {row_name}",
            col_template="{col_name}"
        )

        # Instead of an axis being L-shaped, make it a box
        for ax in g.axes.flat:
            ax.spines["top"].set_visible(True)
            ax.spines["right"].set_visible(True)

        # Add legend
        g.add_legend(title="Sensor", edgecolor="#000000", frameon=True)

        # Add main title
        g.figure.suptitle(f"Mean Failure Time Vs Solution, by Pattern, and Sensor ({int(voltage)}V)")

        # Adjust spacing
        g.figure.subplots_adjust(
            hspace=1,
            left=0.06,
            bottom=0.08,
            right=0.91,
            top=0.94
        )

        g.set_xticklabels(rotation=90)

        figs.append(g.figure)
    
    return figs

# Plot pH as a function of Time to Failure (ms), colored by solution type
def fail_time_ph():
    df=adds.get_master()

    # Remove solutions with no recorded Ph so they don't take up space in the legend
    df=df[(df["Solution"]=="Adipic Acid - 1.24mM")|(df["Solution"]=="Adipic Acid - 0.712mM")|(df["Solution"]=="Adipic Acid - 0.388mM")|(df["Solution"]=="Succinic 0.388mM")]

    # Rename Ph column to be correct
    df.rename(columns={'Ph': 'pH'}, inplace=True)
    # Plot
    ax=sns.scatterplot(x="pH", y="Time to Failure (ms)", data=df, hue="Solution")
    
    ax.set_title("Time to Failure (ms) vs. pH by Solution Type")

    # Move legend to the right of the plot
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))

    # Tight layout so the legend doesn't get cut off
    plt.tight_layout()
    return ax.get_figure()
