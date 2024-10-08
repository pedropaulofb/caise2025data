import os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from loguru import logger


# Function to load data and plot the lines for each stereotype with optional smoothing and filtering
def plot_stereotypes_over_time(in_dir_path, out_dir_path, file_name, selected_stereotypes='all', window_size=1):
    # Load the CSV file
    csv_file = os.path.join(in_dir_path, file_name)
    df = pd.read_csv(csv_file, index_col='year')

    # Multiply all values by 100 to convert to percentages
    df = df * 100

    # Calculate the top and bottom 50% based on the maximum value of each stereotype
    stereotype_max = df.max().sort_values(ascending=False)
    num_stereotypes = len(stereotype_max)

    # Filter stereotypes based on 'selected_stereotypes' argument
    if selected_stereotypes == 'top':
        # Select top 50% stereotypes
        top_stereotypes = stereotype_max.index[:num_stereotypes // 2]
        df = df[top_stereotypes]
    elif selected_stereotypes == 'bottom':
        # Select bottom 50% stereotypes
        bottom_stereotypes = stereotype_max.index[num_stereotypes // 2:]
        df = df[bottom_stereotypes]
    # If 'all' is passed or no valid option, all stereotypes are used (default behavior)

    # Apply rolling mean if window_size is greater than 1
    if window_size > 1:
        df = df.rolling(window=window_size, min_periods=1).mean()

    # Reset index to have 'year' as a column for Seaborn plotting
    df_reset = df.reset_index()

    # Reshape the DataFrame from wide to long format
    df_melted = df_reset.melt(id_vars='year', var_name='Stereotype', value_name='Value')

    # Set plot style
    sns.set(style="whitegrid")

    # Line plot for the selected stereotypes
    fig, ax = plt.subplots(figsize=(16, 9))

    # Define 12 distinct colors using Seaborn's color palette
    colors = sns.color_palette("tab20", 12)  # 12 distinct colors from 'tab20' palette

    # Define line styles: solid for the first 12, dashed for the next 12
    line_styles = ['-' for _ in range(12)] + ['--' for _ in range(12)]

    # Plot each stereotype's line individually with the corresponding color and line style
    for idx, stereotype in enumerate(df.columns):
        sns.lineplot(data=df_melted[df_melted['Stereotype'] == stereotype], x='year', y='Value',
                     color=colors[idx % 12], linestyle=line_styles[idx], label=stereotype, ax=ax)

    # Determine if the file is "yearly" or "overall" based on the file name
    if "yearly" in file_name:
        normalization_type = "Yearly Normalized"
    elif "overall" in file_name:
        normalization_type = "Overall Normalized"
    else:
        normalization_type = "Unknown Normalization"

    # Customize plot title based on filtering, smoothing, and normalization type
    if window_size > 1:
        if selected_stereotypes == 'top':
            title = f'Top 50% Stereotype Proportions (Percentage) Over Time ({normalization_type}, Smoothed, Window: {window_size})'
        elif selected_stereotypes == 'bottom':
            title = f'Bottom 50% Stereotype Proportions (Percentage) Over Time ({normalization_type}, Smoothed, Window: {window_size})'
        else:
            title = f'Stereotype Proportions (Percentage) Over Time ({normalization_type}, Smoothed, Window: {window_size})'
    else:
        if selected_stereotypes == 'top':
            title = f'Top 50% Stereotype Proportions (Percentage) Over Time ({normalization_type})'
        elif selected_stereotypes == 'bottom':
            title = f'Bottom 50% Stereotype Proportions (Percentage) Over Time ({normalization_type})'
        else:
            title = f'Stereotype Proportions (Percentage) Over Time ({normalization_type})'

    ax.set_title(title)
    ax.set_xlabel('Year')
    ax.set_ylabel('Percentage (%)')

    # Add legend and layout adjustment
    plt.legend(title='Stereotypes', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    # Save the figure instead of showing it
    fig_name = f"{file_name.replace('.csv', '')}_stereotypes_{selected_stereotypes}_window{window_size}.png"
    fig.savefig(os.path.join(out_dir_path, fig_name), dpi=300)
    logger.success(f"Figure {fig_name} successfully saved in {out_dir_path}.")
    plt.close(fig)


# Function to load data and plot stereotypes divided into quartiles (25% each)
def plot_stereotypes_in_quartiles(in_dir_path, out_dir_path, file_name, window_size=1):
    # Load the CSV file
    csv_file = os.path.join(in_dir_path, file_name)
    df = pd.read_csv(csv_file, index_col='year')

    # Multiply all values by 100 to convert to percentages
    df = df * 100

    # Calculate the max value of each stereotype to determine the quartiles
    stereotype_max = df.max().sort_values(ascending=False)
    num_stereotypes = len(stereotype_max)

    # Divide the stereotypes into four groups (quartiles)
    top_25 = stereotype_max.index[:num_stereotypes // 4]
    second_25 = stereotype_max.index[num_stereotypes // 4:num_stereotypes // 2]
    third_25 = stereotype_max.index[num_stereotypes // 2:num_stereotypes * 3 // 4]
    bottom_25 = stereotype_max.index[num_stereotypes * 3 // 4:]

    quartile_groups = [
        ('Top 25%', top_25),
        ('Second Quartile (26-50%)', second_25),
        ('Third Quartile (51-75%)', third_25),
        ('Bottom 25%', bottom_25)
    ]

    # Set plot style
    sns.set(style="whitegrid")

    # Plot each quartile group
    for title, stereotypes in quartile_groups:
        # Filter the data to the selected stereotypes
        df_quartile = df[stereotypes]

        # Apply rolling mean if window_size is greater than 1
        if window_size > 1:
            df_quartile = df_quartile.rolling(window=window_size, min_periods=1).mean()

        # Reset index for plotting
        df_reset = df_quartile.reset_index()

        # Reshape the DataFrame for Seaborn plotting
        df_melted = df_reset.melt(id_vars='year', var_name='Stereotype', value_name='Value')

        # Plot each quartile
        fig, ax = plt.subplots(figsize=(16, 9))

        # Define 12 distinct colors using Seaborn's color palette
        colors = sns.color_palette("tab20", 12)

        # Define line styles: solid for the first 12, dashed for the next 12
        line_styles = ['-' for _ in range(12)] + ['--' for _ in range(12)]

        # Plot each stereotype's line individually with the corresponding color and line style
        for idx, stereotype in enumerate(df_quartile.columns):
            sns.lineplot(data=df_melted[df_melted['Stereotype'] == stereotype], x='year', y='Value',
                         color=colors[idx % 12], linestyle=line_styles[idx], label=stereotype, ax=ax)

        # Determine if the file is "yearly" or "overall" based on the file name
        if "yearly" in file_name:
            normalization_type = "Yearly Normalized"
        elif "overall" in file_name:
            normalization_type = "Overall Normalized"
        else:
            normalization_type = "Unknown Normalization"

        # Customize plot title based on quartile, smoothing, and normalization type
        if window_size > 1:
            plot_title = f'{title} Stereotype Proportions (Percentage) Over Time ({normalization_type}, Smoothed, Window: {window_size})'
        else:
            plot_title = f'{title} Stereotype Proportions (Percentage) Over Time ({normalization_type})'

        ax.set_title(plot_title)
        ax.set_xlabel('Year')
        ax.set_ylabel('Percentage (%)')

        # Add legend and layout adjustment
        plt.legend(title='Stereotypes', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        # Save the figure instead of showing it
        fig_name = f"{file_name.replace('.csv', '')}_quartile_{title.replace(' ', '_')}_window{window_size}.png"
        fig.savefig(os.path.join(out_dir_path, fig_name), dpi=300)
        logger.success(f"Figure {fig_name} successfully saved in {out_dir_path}.")
        plt.close(fig)


# Function to plot stacked bar chart
def plot_stacked_bar(in_dir_path, out_dir_path, file_name):
    # Load the CSV file
    csv_file = os.path.join(in_dir_path, file_name)
    df = pd.read_csv(csv_file, index_col='year')

    # Multiply all values by 100 to convert to percentages
    df = df * 100

    # Set up color palettes: 12 solid colors and 12 colors with texture ('.')
    solid_colors = sns.color_palette("tab20", 12)  # Use a seaborn palette for 12 solid colors
    textured_colors = sns.color_palette("tab20", 12)  # Another set of colors for textured

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(16, 9))

    # Initialize a list to keep track of the bottom for the stacked bar plot
    bottom = [0] * len(df)

    # Create a list to store custom legend patches
    custom_legend_patches = []

    # Loop through each stereotype and plot the bar chart
    for idx, stereotype in enumerate(df.columns):
        if idx < 12:
            # Plot the first 12 stereotypes with solid colors
            bars = ax.bar(df.index, df[stereotype], bottom=bottom, color=solid_colors[idx], label=stereotype)
            custom_legend_patches.append(mpatches.Patch(color=solid_colors[idx], label=stereotype))  # Solid color patch
        else:
            # Plot the next stereotypes with dots texture (hatch pattern) and the second color palette
            texture = '.'
            bars = ax.bar(df.index, df[stereotype], bottom=bottom, color=textured_colors[idx - 12], hatch=texture,
                          label=stereotype)
            # Create a custom legend patch with both color and hatch pattern
            custom_legend_patches.append(mpatches.Patch(facecolor=textured_colors[idx - 12], edgecolor='black',
                                                        hatch=texture, label=stereotype))

        # Update the bottom for the next stereotype
        bottom = [i + j for i, j in zip(bottom, df[stereotype])]

    # Add custom legend to the plot with patches including hatches
    ax.legend(handles=custom_legend_patches, bbox_to_anchor=(1.05, 1), loc='upper left')

    # Determine if the file is "yearly" or "overall" based on the file name
    if "yearly" in file_name:
        normalization_type = "Yearly Normalized"
    elif "overall" in file_name:
        normalization_type = "Overall Normalized"
    else:
        normalization_type = "Unknown Normalization"

    # Set labels and title
    ax.set_xlabel('Year')
    ax.set_ylabel('Percentage (%)')
    ax.set_title(f'Stereotype Proportions (Percentage) Over Time (Stacked Bar, {normalization_type})')

    # Ensure only integer years (no fractions) are shown on the x-axis
    ax.set_xticks(df.index)  # Set the x-axis ticks to the index (years)
    ax.set_xticklabels(df.index.astype(int), rotation=45, ha="right")  # Rotate the year labels for better readability

    # Adjust the layout
    plt.tight_layout()

    # Save the figure
    fig_name = f"{file_name.replace('.csv', '')}_stacked_bar.png"
    fig.savefig(os.path.join(out_dir_path, fig_name), dpi=300)
    logger.success(f"Figure {fig_name} successfully saved in {out_dir_path}.")
    plt.close(fig)


def plot_heatmap(in_dir_path, out_dir_path, file_name):
    # Load CSV file
    csv_file = os.path.join(in_dir_path, file_name)
    df = pd.read_csv(csv_file, index_col='year')

    # Multiply all values by 100 to convert to percentages
    df = df * 100

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(16, 9))
    sns.heatmap(df.T, cmap='coolwarm', ax=ax, annot=True, fmt=".1f", cbar_kws={'label': 'Proportion (%)'})

    ax.set_xlabel('Year')
    ax.set_ylabel('Stereotype')
    # Determine if the file is "yearly" or "overall" based on the file name
    if "yearly" in file_name:
        normalization_type = "Yearly Normalized"
    elif "overall" in file_name:
        normalization_type = "Overall Normalized"
    else:
        normalization_type = "Unknown Normalization"

    # Set plot title with normalization type
    ax.set_title(f'Stereotype Proportions (Percentage) Over Time (Heatmap, {normalization_type})')

    plt.tight_layout()

    # Save figure
    fig_name = f"{file_name.replace('.csv', '')}_heatmap.png"
    fig.savefig(os.path.join(out_dir_path, fig_name), dpi=300)
    logger.success(f"Figure {fig_name} successfully saved in {out_dir_path}.")
    plt.close(fig)


# Function to load data and plot the bump chart for each stereotype
def plot_stereotypes_over_time_bump(in_dir_path, out_dir_path, file_name, selected_stereotypes='all', window_size=1):
    # Load the CSV file
    csv_file = os.path.join(in_dir_path, file_name)
    df = pd.read_csv(csv_file, index_col='year')

    # Calculate the top and bottom 50% based on the maximum value of each stereotype
    stereotype_max = df.max().sort_values(ascending=False)
    num_stereotypes = len(stereotype_max)

    # Filter stereotypes based on 'selected_stereotypes' argument
    if selected_stereotypes == 'top':
        # Select top 50% stereotypes
        top_stereotypes = stereotype_max.index[:num_stereotypes // 2]
        df = df[top_stereotypes]
    elif selected_stereotypes == 'bottom':
        # Select bottom 50% stereotypes
        bottom_stereotypes = stereotype_max.index[num_stereotypes // 2:]
        df = df[bottom_stereotypes]
    # If 'all' is passed or no valid option, all stereotypes are used (default behavior)

    # Apply rolling mean if window_size > 1
    if window_size > 1:
        df = df.rolling(window=window_size, min_periods=1).mean()

    # Rank the stereotypes for each year (1 = highest value, N = lowest value)
    df_ranks = df.rank(axis=1, method='dense', ascending=False)

    # Set plot style
    sns.set(style="whitegrid")

    # Plot bump chart
    fig, ax = plt.subplots(figsize=(16, 9))

    # Define 12 distinct colors using Seaborn's color palette
    colors = sns.color_palette("tab20", 12)

    # Define line styles: solid for the first 12, dashed for the next 12
    line_styles = ['-' for _ in range(12)] + ['--' for _ in range(12)]

    # Plot each stereotype's rank over time individually with corresponding color and line style
    for idx, stereotype in enumerate(df_ranks.columns):
        ax.plot(df_ranks.index, df_ranks[stereotype], color=colors[idx % 12],
                linestyle=line_styles[idx], label=stereotype, linewidth=2)

    # Set y-axis limits (from 0 to the number of stereotypes + 1)
    ax.set_ylim(0, len(df_ranks.columns) + 1)

    # Set y-ticks to integers only
    ax.set_yticks(range(1, len(df_ranks.columns) + 1))

    # Add horizontal grid lines at each integer y-tick
    ax.yaxis.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Invert y-axis so that Rank 1 is at the top
    ax.invert_yaxis()

    # Determine if the file is "yearly" or "overall" based on the file name
    if "yearly" in file_name:
        normalization_type = "Yearly Normalized"
    elif "overall" in file_name:
        normalization_type = "Overall Normalized"
    else:
        normalization_type = "Unknown Normalization"

    # Customize plot title based on filtering, smoothing, and normalization type
    if window_size > 1:
        if selected_stereotypes == 'top':
            title = f'Top 50% Stereotype Rankings Over Time ({normalization_type}, Smoothed, Window: {window_size})'
        elif selected_stereotypes == 'bottom':
            title = f'Bottom 50% Stereotype Rankings Over Time ({normalization_type}, Smoothed, Window: {window_size})'
        else:
            title = f'Stereotype Rankings Over Time ({normalization_type}, Smoothed, Window: {window_size})'
    else:
        if selected_stereotypes == 'top':
            title = f'Top 50% Stereotype Rankings Over Time ({normalization_type})'
        elif selected_stereotypes == 'bottom':
            title = f'Bottom 50% Stereotype Rankings Over Time ({normalization_type})'
        else:
            title = f'Stereotype Rankings Over Time ({normalization_type})'

    ax.set_title(title)
    ax.set_xlabel('Year')
    ax.set_ylabel('Rank')
    ax.legend(title='Stereotypes', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Adjust layout
    plt.tight_layout()

    # Save the figure instead of showing it
    fig_name = f"{file_name.replace('.csv', '')}_bump_chart_{selected_stereotypes}_window{window_size}.png"
    fig.savefig(os.path.join(out_dir_path, fig_name), dpi=300)
    logger.success(f"Figure {fig_name} successfully saved in {out_dir_path}.")
    plt.close(fig)
