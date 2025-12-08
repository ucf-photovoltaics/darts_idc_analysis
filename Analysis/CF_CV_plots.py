import pandas as pd
import adds
import matplotlib
import matplotlib.pyplot as plt

# required to show plt plots in Streamlit
matplotlib.use("TkAgg")

# get CF and CV data
CF=adds.get_master_cf_or_cv(cf_or_cv="CF")
CV=adds.get_master_cf_or_cv(cf_or_cv="CV")

# filter out files with bad data
CF=CF[(CF["Capacitance (F)"]>0)&(CF["Capacitance (F)"]<100)]
CV=CV[(CV["Capacitance (F)"]>0)&(CV["Capacitance (F)"]<100)]

# list of sensor names and colors for plotting
sensors=["U1", "U2", "U3", "U4"]
colors=["c", "m", "y", "#47E183"]

# take the average across all data for each sensor and frequency for CF data
if CF is not None and not CF.empty:
    CF_average=CF.groupby(["Sensor","Frequency (Hz)"]).agg({"Capacitance (F)":"mean","Impedance (O)":"mean",
        "Phase Angle (D)":"mean"}).reset_index()
    print(CF_average)

# take the average across all data for each sensor and voltage for CV data
if CV is not None and not CV.empty:
    CV_average=CV.groupby(["Sensor","Voltage (V)"]).agg({"Capacitance (F)":"mean","Impedance (O)":"mean",
        "Phase Angle (D)":"mean"}).reset_index()
    print(CV_average)

# create figure and subplots
fig, axes=plt.subplots(2, 3, figsize=(15, 8))

# flatten array
ax1, ax2, ax3, ax4, ax5, ax6=axes.flatten()

# plot CF data - one line per sensor
for i, sensor in enumerate(sensors):
    sensor_data=CF_average[CF_average["Sensor"]==sensor]

    # plot Capacitance (F) vs. Frequency (Hz)
    ax1.plot(sensor_data["Frequency (Hz)"], sensor_data["Capacitance (F)"], c=colors[i], label=sensor)

    # plot Impedance (O) vs. Frequency (Hz)
    ax2.plot(sensor_data["Frequency (Hz)"], sensor_data["Impedance (O)"], c=colors[i], label=sensor)

    # plot Phase Angle (D) vs. Frequency (Hz)
    ax3.plot(sensor_data["Frequency (Hz)"], sensor_data["Phase Angle (D)"], c=colors[i], label=sensor)

ax1.set_title("Capacitance (F) vs. Frequency (Hz)")
ax1.set_ylabel("Capacitance (F)")
ax1.set_xlabel("Frequency (Hz)")
ax1.set_ylim(0,25)
ax1.legend()


ax2.set_title("Impedance (O) vs. Frequency (Hz)")
ax2.set_ylabel("Impedance (O)")
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylim(0,10e6)
ax2.legend()


ax3.set_title("Phase Angle (D) vs. Frequency (Hz)")
ax3.set_ylabel("Phase Angle (D)")
ax3.set_xlabel("Frequency (Hz)")
ax3.set_ylim(0,-100)
ax3.legend()


# plot CV data - one line per sensor
for i, sensor in enumerate(sensors):
    sensor_data=CV_average[CV_average["Sensor"]==sensor]

    # plot "Capacitance (F) vs. Voltage (V)
    ax4.plot(sensor_data["Voltage (V)"], sensor_data["Capacitance (F)"], c=colors[i], label=sensor)

    # plot Impedance (O) vs. Voltage (V)
    ax5.plot(sensor_data["Voltage (V)"], sensor_data["Impedance (O)"], c=colors[i], label=sensor)

    # plot Phase Angle (D) vs. Voltage (V)
    ax6.plot(sensor_data["Voltage (V)"], sensor_data["Phase Angle (D)"], c=colors[i], label=sensor)

ax4.set_title("Capacitance (F) vs. Voltage (V)")
ax4.set_ylabel("Capacitance (F)")
ax4.set_xlabel("Voltage (V)")
ax4.set_ylim(0,25)
ax4.legend()

ax5.set_title("Impedance (O) vs. Voltage (V)")
ax5.set_ylabel("Impedance (O)")
ax5.set_xlabel("Voltage (V)")
ax5.set_ylim(0,10e6)
ax5.legend()

ax6.set_title("Phase Angle (D) vs. Voltage (V)")
ax6.set_ylabel("Phase Angle (D)")
ax6.set_xlabel("Voltage (V)")
ax6.set_ylim(0,-100)
ax6.legend()

plt.tight_layout()
plt.show()