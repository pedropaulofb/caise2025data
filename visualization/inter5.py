import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the data from the CSV files
diversity_measures = pd.read_csv('../outputs/analyses/cs_analyses/diversity_measures.csv')
frequency_analysis = pd.read_csv('../outputs/analyses/cs_analyses/frequency_analysis.csv')

# Merge the dataframes on the 'Construct' column
merged_data = pd.merge(diversity_measures[['Construct', 'Simpson Index']],
                       frequency_analysis[['Construct', 'Total Frequency']],
                       on='Construct')

# Calculate thresholds (medians)
frequency_threshold = merged_data['Total Frequency'].median()  # Median for Total Frequency
simpson_threshold = merged_data['Simpson Index'].median()  # Median for Simpson Index

# Create a scatter plot for Simpson's Index vs. Total Frequency
plt.figure(figsize=(10, 6))
sns.scatterplot(data=merged_data,
                x='Total Frequency',
                y='Simpson Index',
                hue='Construct',
                palette='viridis',
                s=100,
                legend=False)

# Customize the plot
plt.title("Scatter Plot of Simpson's Index vs. Total Frequency")
plt.xlabel('Total Frequency')
plt.ylabel("Simpson's Index")
plt.grid(True)

# Draw lines to create quadrants using medians
plt.axhline(y=simpson_threshold, color='grey', linestyle='--', linewidth=1)  # Horizontal line for Simpson Index
plt.axvline(x=frequency_threshold, color='grey', linestyle='--', linewidth=1)  # Vertical line for Total Frequency

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
    plt.text(x=merged_data['Total Frequency'][i],
             y=merged_data['Simpson Index'][i],
             s=construct_name,
             fontsize=8,
             ha='right',
             color=color)  # Use the color variable here

# Add annotations for the median lines
plt.text(x=0, y=simpson_threshold, s=f'Median Simpson Index: {simpson_threshold:.2f}', color='grey', fontsize=10, va='bottom', ha='left')
plt.text(x=frequency_threshold, y=min(merged_data['Simpson Index']), s=f'Median Total Frequency: {frequency_threshold:.2f}', color='grey', fontsize=10, va='bottom', ha='right', rotation=90)

# Show the plot
plt.show()
