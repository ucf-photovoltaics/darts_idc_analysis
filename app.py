import streamlit as st
import subprocess
import sys
import os

# Get important file paths, works when this script is run in any CWD
script_path = os.path.abspath(__file__)
repo_dir = os.path.dirname(script_path)

# Ensure script is run using Streamlit -----------------------------------------
# If script wasn't run with Streamlit
if "--as-streamlit" not in sys.argv:
    # Rerun using Streamlit. Pass a sentinal "--as-streamlit" param to script,
    # which will be checked in the if statement
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", script_path, "--", "--as-streamlit"],
        cwd=repo_dir
    )
    # Don't execute the Streamlit code if not being run with Streamlit
    exit()

# Run Streamlit app ------------------------------------------------------------
# Function to run a plot from the script name
def run_plot_script(script_name):
    # Run the script
    subprocess.Popen([sys.executable, os.path.join("Analysis", script_name)], cwd=repo_dir)

st.title("IDC Analysis Plots")

if st.button("RGB Analysis 3D"):
    run_plot_script("rgb_3d.py")

if st.button("RGB Analysis Box Plots"):
    run_plot_script("rgb_boxplots.py")

if st.button("Grayscale Box Plots"):
    run_plot_script("grayscale_boxplots.py")

if st.button("Correlation Heatmap"):
    run_plot_script("corr_heatmap.py")

if st.button("Current Vs Time"):
    run_plot_script("current_time.py")

if st.button("Failure Time Vs Solution"):
    run_plot_script("fail_time.py")

if st.button("Failure Time Vs Ph"):
    run_plot_script("Ph_Plots.py")
