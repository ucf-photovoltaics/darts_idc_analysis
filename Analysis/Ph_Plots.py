# plots Ph as a function of Time to Failure (ms), colored by solution type
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import adds

def plot_ph():
    
    df=adds.get_master()

    # remove solutions with no recorded Ph so they don't take up space in the legend
    df=df[(df["Solution"]=="Adipic Acid - 1.24mM")|(df["Solution"]=="Adipic Acid - 0.712mM")|(df["Solution"]=="Adipic Acid - 0.388mM")|(df["Solution"]=="Succinic 0.388mM")]

    # plot
    sns.scatterplot(x="Time to Failure (ms)", y="Ph", data=df, hue="Solution").set_title("Time to Failure (ms) vs. Ph by Solution Type")

    # move legend to the right of the plot
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0., title="Solution")

    plt.show()
    
plot_ph()
