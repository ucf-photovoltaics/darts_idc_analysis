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

st.title("IDC Analysis Plots")

if st.button("RGB Analysis 3D"):
    subprocess.Popen([sys.executable, "Analysis/rgb_3d.py"], cwd=repo_dir)

if st.button("RGB Analysis Box Plots"):
    subprocess.Popen([sys.executable, "Analysis/rgb_boxplots.py"], cwd=repo_dir)

if st.button("Grayscale Box Plots"):
    subprocess.Popen([sys.executable, "Analysis/grayscale_boxplots.py"], cwd=repo_dir)

if st.button("Correlation Heatmap"):
    subprocess.Popen([sys.executable, "Analysis/corr_heatmap.py"], cwd=repo_dir)

if st.button("Current Vs Time"):
    subprocess.Popen([sys.executable, "Analysis/current_time.py"], cwd=repo_dir)

if st.button("Failure Time Vs Solution"):
    subprocess.Popen([sys.executable, "Analysis/fail_time.py"], cwd=repo_dir)

if st.button("Failure Time Vs Ph"):
    subprocess.Popen([sys.executable, "Analysis/Ph_Plots.py"], cwd=repo_dir)

if st.button("Update Cached Data"):
    st.write("Updating...")
    subprocess.run([sys.executable, "Analysis/update_cache.py"], cwd=repo_dir)
    st.write("Done!")
