import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_ph():
    # read file with the organized Ph data
    ph_df=pd.read_csv("IDCSubmersionMasterlist_PH.csv")

    # split data into 2 data frames based on sensor type
    ph_df1=ph_df[ph_df["Sensor"]=="U1"]
    ph_df4=ph_df[ph_df["Sensor"]=="U4"]

    # plot Time to Failure vs. Ph based on sensor type
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.scatterplot(x="Time to Failure (ms)", y="Ph", data=ph_df1, ax=axes[0], color="blue")
    axes[0].set_title('Time to Failure vs. Ph for U1')
    sns.scatterplot(x="Time to Failure (ms)", y="Ph", data=ph_df4, ax=axes[1], color="red")
    axes[1].set_title('Time to Failure vs. Ph for U4')
    axes[0].tick_params(axis='x', rotation=45)
    axes[1].tick_params(axis='x', rotation=45)
    plt.show()
plot_ph()
