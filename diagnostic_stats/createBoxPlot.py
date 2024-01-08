import matplotlib.pyplot as plt
import numpy as np

with open('refCount.txt', 'r') as file:
    lines = file.readlines()
    t = ""
    for line in lines:
        t = t + line.strip()
d = []


# Sample data
t = t.replace("[","").replace("]","")

x = [int(x) for x in t.split(", ")]
print(x)


# Creating a figure and axes
fig, ax = plt.subplots()

# Creating a horizontal boxplot
bp = ax.boxplot(x, vert=False, patch_artist=True)

# Customizing the boxplot colors
box_color = 'lightblue'
whisker_color = 'gray'
flier_color = 'orange'
median_color = 'black'

for element in ['boxes', 'whiskers', 'fliers', 'medians', 'caps']:
    plt.setp(bp[element], color=whisker_color)

plt.setp(bp['medians'], color=median_color)
plt.setp(bp['boxes'], facecolor=box_color)
plt.setp(bp['fliers'], markeredgecolor=flier_color,markersize=2)

# Finding and highlighting the outliers
outliers = bp['fliers'][0].get_xdata()
ax.plot(outliers, [1] * len(outliers), marker='o', markersize=2, color=flier_color, linestyle='none')

# Setting a logarithmic scale for the x-axis
ax.set_xscale('log')
ax.xaxis.set_major_formatter(plt.ScalarFormatter())

# Adding labels and title
ax.set_xlabel('Data (log scale)')
ax.set_title('Horizontal Boxplot with Outliers')

# Removing Y-axis ticks and labels
ax.yaxis.set_ticklabels([])
plt.savefig("boxplotREF.png")
# Display the plot
plt.show()