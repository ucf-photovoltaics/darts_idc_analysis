import streamlit as st
import os
import plots
import adds

# Get important file paths, works when this script is run in any CWD
script_path = os.path.abspath(__file__)
repo_dir = os.path.dirname(script_path)

# Streamlit App
st.title("IDC Analysis Plotting Hub")

st.header("Plots")
with st.container(border=True):
    if st.button("RGB Analysis 3D"):
        st.plotly_chart(plots.rgb_3d())
    st.text("Maps RGB values to XYZ coordinates to view the average color of all boards, separated by board type and pristine/exposed")

with st.container(border=True):
    if st.button("RGB Analysis Box Plots"):
        st.pyplot(plots.rgb_boxplots())
    st.text("Plots the differences in average RGB channels from pristine to exposed boards")

with st.container(border=True):
    if st.button("Grayscale Box Plots"):
        st.pyplot(plots.grayscale_boxplots())
    st.text("Plots the average brightness of each board")

with st.container(border=True):
    if st.button("Scatterplot Matrix"):
        st.pyplot(plots.scatterplot_matrix())
    st.text("Plots a scatterplot matrix for all combinations of two variables")

with st.container(border=True):
    if st.button("Correlation Heatmap"):
        st.pyplot(plots.corr_heatmap())
    st.text("Plots the correlations between all combinations of two variables")

with st.container(border=True):
    if st.button("Current Vs Time"):
        for fig in plots.current_time():
            st.pyplot(fig)
    st.text("Plot current as a function of time for each tested sensor, separated by solution, board type, and sensor")

with st.container(border=True):
    if st.button("Failure Time Vs Solution"):
        for fig in plots.fail_time_solution():
            st.pyplot(fig)
    st.text("Plot failure time as function of solution, separated by board type and sensor")

with st.container(border=True):
    if st.button("Failure Time Vs Ph"):
        st.pyplot(plots.fail_time_ph())
    st.text("Plot failure time as a function of pH")

st.header("Settings")
if st.button("Update Cached Data"):
    st.write("Updating...")
    adds.get_master(from_cache=False).to_csv("master_cached.csv", index=False)
    st.write("Done!")
