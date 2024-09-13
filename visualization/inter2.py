import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the data from the CSV files
diversity_measures = pd.read_csv('../outputs/analyses/cs_analyses/diversity_measures.csv')
frequency_analysis = pd.read_csv('../outputs/analyses/cs_analyses/frequency_analysis.csv')

# Merge the dataframes on the 'Construct' column
merged_data = pd.merge(diversity_measures[['Construct', 'Gini Coefficient']],
                       frequency_analysis[['Construct', 'Ubiquity Index (Group Frequency per Group)']],
                       on='Construct')

# Calculate thresholds
gini_threshold = merged_data['Gini Coefficient'].median()  # Using median as a threshold
ubiquity_threshold = merged_data['Ubiquity Index (Group Frequency per Group)'].median()  # Using median as a threshold

# Plot with Seaborn scatter plot
plt.figure(figsize=(10, 6))
sns.scatterplot(data=merged_data,
                x='Gini Coefficient',
                y='Ubiquity Index (Group Frequency per Group)',
                hue='Construct',
                palette='viridis',
                size='Ubiquity Index (Group Frequency per Group)',
                legend=False,
                sizes=(20, 200))

# Customize the plot
plt.title('Scatter Plot of Ubiquity Index vs. Gini Coefficient')
plt.xlabel('Gini Coefficient')
plt.ylabel('Ubiquity Index (Group Frequency per Group)')
plt.grid(True)

# Draw lines to create quadrants
plt.axhline(y=ubiquity_threshold, color='grey', linestyle='--', linewidth=1)  # Horizontal line
plt.axvline(x=gini_threshold, color='grey', linestyle='--', linewidth=1)  # Vertical line

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
    plt.text(x=merged_data['Gini Coefficient'][i],
             y=merged_data['Ubiquity Index (Group Frequency per Group)'][i],
             s=construct_name,
             fontsize=8,
             ha='right',
             color=color)  # Use the color variable here

# Add annotations for the median lines
plt.text(x=0, y=ubiquity_threshold, s=f'Median Ubiquity Index: {ubiquity_threshold:.2f}', color='grey', fontsize=10, va='bottom', ha='left')
plt.text(x=gini_threshold, y=min(merged_data['Ubiquity Index (Group Frequency per Group)']), s=f'Median Gini Coefficient: {gini_threshold:.2f}', color='grey', fontsize=10, va='bottom', ha='right', rotation=90)

# Show the plot
plt.show()
