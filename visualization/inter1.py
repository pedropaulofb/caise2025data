import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

# Load the data from the CSV files
diversity_measures = pd.read_csv('../outputs/analyses/cs_analyses/diversity_measures.csv')
frequency_analysis = pd.read_csv('../outputs/analyses/cs_analyses/frequency_analysis.csv')

# Merge the dataframes on the 'Construct' column
merged_data = pd.merge(diversity_measures[['Construct', 'Shannon Entropy']],
                       frequency_analysis[['Construct', 'Global Relative Frequency (Occurrence-wise)']],
                       on='Construct')


# Calculate thresholds
entropy_threshold = merged_data['Shannon Entropy'].median()  # Using median as a threshold
frequency_threshold = merged_data['Global Relative Frequency (Occurrence-wise)'].median()  # Using median as a threshold

# Plot with Seaborn scatter plot
plt.figure(figsize=(10, 6))
sns.scatterplot(data=merged_data,
                x='Shannon Entropy',
                y='Global Relative Frequency (Occurrence-wise)',
                hue='Construct',
                palette='viridis',
                size='Global Relative Frequency (Occurrence-wise)',
                legend=False,
                sizes=(20, 200))

# Customize the plot
plt.yscale('log')
plt.title('Scatter Plot of Shannon Entropy vs. Global Relative Frequency (Occurrence-wise)')
plt.xlabel('Shannon Entropy')
plt.ylabel('Global Relative Frequency (Occurrence-wise)')
plt.grid(True)

# Draw lines to create quadrants
plt.axhline(y=frequency_threshold, color='grey', linestyle='--', linewidth=1)  # Horizontal line
plt.axvline(x=entropy_threshold, color='grey', linestyle='--', linewidth=1)  # Vertical line

# Annotate each point with the construct name and color for 'none' and 'other'
for i in range(len(merged_data)):
    construct_name = merged_data['Construct'][i]

    # Set the color based on the construct name
    if construct_name == 'none':
        color = 'blue'
    elif construct_name == 'other':
        color = 'red'
    else:
        color = 'black'  # Default color for other constructs

    # Annotate the plot with the construct name and its color
    plt.text(x=merged_data['Shannon Entropy'][i],
             y=merged_data['Global Relative Frequency (Occurrence-wise)'][i],
             s=construct_name,
             fontsize=8,
             ha='right',
             color=color)  # Use the color variable here

# Add annotations for the median lines
plt.text(x=0, y=frequency_threshold, s=f'Median Frequency: {frequency_threshold:.2e}', color='grey', fontsize=10, va='bottom', ha='left')
plt.text(x=entropy_threshold, y=min(merged_data['Global Relative Frequency (Occurrence-wise)']), s=f'Median Entropy: {entropy_threshold:.2f}', color='grey', fontsize=10, va='bottom', ha='right', rotation=90)


# Show the plot
plt.show()
