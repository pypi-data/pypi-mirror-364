import matplotlib.pyplot as plt
import pandas as pd

# Read the CSV file
csv_file = "path_length_history.csv"
data = pd.read_csv(csv_file)

# Plot the history of average path lengths
plt.figure(figsize=(10, 6))
plt.plot(data["Sample"], data["AveragePathLength"], marker='o', linestyle='-', color='b')
plt.xlabel("Sample")
plt.ylabel("Average Path Length")
plt.title("History of Average Path Length Between Nodes 0 and 1")
plt.grid(True)
plt.savefig("path_length_history.png")
