import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read the CSV file into a DataFrame
df = pd.read_csv("../outputs/analyses/cs_analyses/frequency_analysis.csv")

# Convert the 'Construct' column to a categorical type to ensure proper ordering in the plots
df['Construct'] = pd.Categorical(df['Construct'], categories=df['Construct'].unique(), ordered=True)

# 1) Side-by-Side Bar Chart with Double Axis for Total Frequency and Ubiquity Index
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot Total Frequency on the primary y-axis
ax1.bar(df['Construct'], df['Total Frequency'], color='cornflowerblue', width=0.4, label='Total Frequency')
ax1.set_ylabel('Total Frequency', color='skyblue')
ax1.tick_params(axis='y', labelcolor='skyblue')
# Set tick positions and labels to fix the warning
ax1.set_xticks(range(len(df['Construct'])))
ax1.set_xticklabels(df['Construct'], rotation=45)

# Color specific x-axis labels
for label in ax1.get_xticklabels():
    if label.get_text() == 'none':
        label.set_color('blue')
    elif label.get_text() == 'other':
        label.set_color('red')

# Create a secondary y-axis for Ubiquity Index
ax2 = ax1.twinx()
ax2.bar([i + 0.4 for i in range(len(df))], df['Ubiquity Index (Group Frequency per Group)'],
        color='salmon', width=0.4, label='Ubiquity Index')
ax2.set_ylabel('Ubiquity Index (Group Frequency per Group)', color='salmon')
ax2.tick_params(axis='y', labelcolor='salmon')

plt.title('Double Axis Bar Chart for Total Frequency and Ubiquity Index')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
fig.tight_layout()
plt.show()

# 2) Side-by-Side Bar Chart with Double Axis for Total Frequency vs. Group Frequency
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot Total Frequency on the primary y-axis
x = range(len(df))
ax1.bar(x, df['Total Frequency'], color='cornflowerblue', width=0.4, label='Total Frequency')
ax1.set_ylabel('Total Frequency', color='green')
ax1.tick_params(axis='y', labelcolor='green')
ax1.set_xticks([i + 0.2 for i in x])
ax1.set_xticklabels(df['Construct'], rotation=45)

# Color specific x-axis labels
for label in ax1.get_xticklabels():
    if label.get_text() == 'none':
        label.set_color('blue')
    elif label.get_text() == 'other':
        label.set_color('red')

# Create a secondary y-axis for Group Frequency
ax2 = ax1.twinx()
ax2.bar([i + 0.4 for i in x], df['Group Frequency'], color='orange', width=0.4, label='Group Frequency')
ax2.set_ylabel('Group Frequency', color='orange')
ax2.tick_params(axis='y', labelcolor='orange')

plt.title('Side-by-Side Bar Chart with Double Axis for Total Frequency vs. Group Frequency')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
fig.tight_layout()
plt.show()


# 3) Scatter plot for Ubiquity Index vs. Total Frequency per Group

# Constructs in the top-right quadrant (high on both axes) are those that are not only frequently used in the models where they appear but are also used in many different models. These are likely the most "core" or "essential" constructs, which are both common and widely adopted by modelers.
# Constructs in the bottom-right quadrant (high "Total Frequency per Group" but low "Ubiquity Index") are used heavily when they do appear but only in a small number of models. This might suggest constructs with specialized or niche use cases.
# Constructs in the top-left quadrant (low "Total Frequency per Group" but high "Ubiquity Index") are used in many different models but not very frequently within each model. This could indicate constructs that are necessary for a broad range of models but are used sparingly.
# Constructs in the bottom-left quadrant (low on both axes) are used infrequently and in few models, potentially indicating constructs with limited relevance or applicability.

plt.figure(figsize=(10, 6))

# Define the base colors for the plot (12 distinct colors)
base_palette = sns.color_palette('tab10', n_colors=12)

# Extend the palette to handle all 23 categories by repeating colors
extended_palette = base_palette + base_palette[:11]  # 12 colors + 11 more to make 23 total

# Define marker types (12 circles 'o' and 11 squares 's')
markers = ['o'] * 12 + ['s'] * 11

# Plotting the scatter plot with different colors and markers
for i, construct in enumerate(df['Construct'].unique()):
    subset = df[df['Construct'] == construct]
    plt.scatter(subset['Total Frequency per Group'], subset['Ubiquity Index (Group Frequency per Group)'],
                color=extended_palette[i], marker=markers[i], s=100, edgecolor='w', label=construct)

# Adding labels and title
plt.xlabel('Total Frequency per Group')
plt.ylabel('Ubiquity Index')
plt.title('Scatter Plot of Ubiquity Index vs. Total Frequency per Group')

# Adding a cross to separate the plot into four quadrants
plt.axhline(y=df['Ubiquity Index (Group Frequency per Group)'].mean(), color='black', linestyle='--', linewidth=1)
plt.axvline(x=df['Total Frequency per Group'].mean(), color='black', linestyle='--', linewidth=1)

# Customize the legend to color 'none' and 'other'
legend = plt.legend(title='Constructs', bbox_to_anchor=(1.05, 1), loc='upper left')
for text in legend.get_texts():
    if 'none' in text.get_text():
        text.set_color('blue')
    elif 'other' in text.get_text():
        text.set_color('red')

plt.tight_layout()
plt.show()

# 4) Side-by-Side Donut Charts for Occurrence-wise and Group-wise Relative Frequencies with Colors and Dots Texture

# Calculate the percentages
percent_occurrence = df['Global Relative Frequency (Occurrence-wise)'] * 100
percent_group = df['Global Relative Frequency (Group-wise)'] * 100

# Prepare labels with percentages
labels_occurrence = [f'{label}: {percentage:.1f}%' for label, percentage in zip(df['Construct'], percent_occurrence)]
labels_group = [f'{label}: {percentage:.1f}%' for label, percentage in zip(df['Construct'], percent_group)]

# Create a palette with 12 distinct colors
base_palette = sns.color_palette('tab10', n_colors=12)  # 'tab10' provides 10 colors; use 'tab12' or any suitable palette
extended_palette = base_palette + base_palette  # Repeat the 12 colors to handle 24 categories

# Define the hatch pattern (dots) for every other category
hatches = ['' if i < 12 else '...' for i in range(24)]  # Apply dots for the second set of 12 colors

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

# Donut chart for Occurrence-wise relative frequency
wedges, texts, autotexts = ax1.pie(df['Global Relative Frequency (Occurrence-wise)'],
                                   labels=['' for _ in df['Construct']],  # Empty labels to avoid clutter
                                   autopct='',
                                   startangle=140,
                                   colors=extended_palette,
                                   wedgeprops=dict(width=0.4))

# Apply dot texture to every other wedge
for i, wedge in enumerate(wedges):
    wedge.set_hatch(hatches[i % 24])  # Use the hatch pattern for every other wedge

# Add custom legend with colored text
legend_occurrence = ax1.legend(wedges, labels_occurrence, title="Constructs", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

# Color specific legend texts
for text in legend_occurrence.get_texts():
    if 'none' in text.get_text():
        text.set_color('blue')
    elif 'other' in text.get_text():
        text.set_color('red')

ax1.set_title('Occurrence-wise Relative Frequency')

# Donut chart for Group-wise relative frequency
wedges, texts, autotexts = ax2.pie(df['Global Relative Frequency (Group-wise)'],
                                   labels=['' for _ in df['Construct']],  # Empty labels to avoid clutter
                                   autopct='',
                                   startangle=140,
                                   colors=extended_palette,
                                   wedgeprops=dict(width=0.4))

# Apply dot texture to every other wedge
for i, wedge in enumerate(wedges):
    wedge.set_hatch(hatches[i % 24])  # Use the hatch pattern for every other wedge

# Add custom legend with colored text
legend_group = ax2.legend(wedges, labels_group, title="Constructs", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

# Color specific legend texts
for text in legend_group.get_texts():
    if 'none' in text.get_text():
        text.set_color('blue')
    elif 'other' in text.get_text():
        text.set_color('red')

ax2.set_title('Group-wise Relative Frequency')

plt.tight_layout()
plt.show()