import sys
sys.path.append("/home/pop533611/thesis")

import numpy as np
from pymongo import MongoClient
import mongoConnect as mc

import matplotlib.pyplot as plt
from scipy.stats import norm

db = mc.connect()



# data = mc.retrieveWithCondition(db, "citedData","tokenLen")

with open('tokenLen.txt', 'r') as file:
    lines = file.readlines()
    t = ""
    for line in lines:
        t = t + line.strip()
d = []


# Sample data
t = t.replace("[","").replace("]","")

x = [int(x) for x in t.split(", ")]

data = np.array(x)

# Calculate z-scores for each data point
z_scores = (data - np.mean(data)) / np.std(data)

# Set threshold z-score value
z_threshold = 3

# Find outliers and remove them
outliers = np.abs(z_scores) > z_threshold
clean_data = data[~outliers]

# Calculate mean and standard deviation of remaining data
mean = np.mean(clean_data)
std = np.std(clean_data)

# d = np.arange(clean_data)

# plt.plot(d, norm.pdf(d, mean, std))

x = np.linspace(mean - 3*std, mean + 3*std, 100)

# Calculate the probability density function (PDF) for the normal distribution
y = (1 / (std * np.sqrt(2*np.pi))) * np.exp(-0.5*((x-mean)/std)**2)

# Plot the histogram of the numbers
plt.hist(clean_data, bins=10, density=True, alpha=0.5, label='Histogram')

# Plot the normal distribution curve
plt.plot(x, y, color='red', label='Normal Distribution')


# Define the boundaries for the three sections
lower_bound = mean - std
upper_bound = mean + std



# Divide the list into three sections
section1 = [x for x in clean_data if x < lower_bound]
section2 = [x for x in clean_data if lower_bound <= x <= upper_bound]
section3 = [x for x in clean_data if x > upper_bound]

print("section1 ",min(section1) , max(section1))
print("section2 ",min(section2) , max(section2))
print("section3 ",min(section3) , max(section3))

# mc.filterTokenLen(db, "citedData", section1, section2, section3)

# mean:  26.1882666800535
# std:  10.842992242228311
# lower_bound:  15.345274437825188
# upper_bound:  37.03125892228181

# Print the divided sections





# x = np.linspace(-4, 4, 100)
# plt.plot(clean_data, norm.pdf(clean_data), linewidth=2, color='r')
# plt.fill_between(clean_data, norm.pdf(clean_data), alpha=0.2, color='r')

# Show the plot
plt.show()
plt.savefig("normalDist.png")
