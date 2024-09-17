import os

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import seaborn as sns
from loguru import logger

from src.color_legend import color_text
from src.create_figure_subdir import create_figures_subdir


def execute_visualization_similarity_measures(file_path):
    # Read data from the CSV file
    df = pd.read_csv(file_path)
    save_dir = create_figures_subdir(file_path)

    # Extract constructs from the 'Construct Pair' column
    df['Construct 1'] = df['Construct Pair'].apply(lambda x: eval(x)[0])
    df['Construct 2'] = df['Construct Pair'].apply(lambda x: eval(x)[1])

    ### 1) Heatmap

    # 1.1) Heatmap for Jaccard Similarity

    # Create a pivot table for Jaccard Similarity
    jaccard_pivot = df.pivot_table(index='Construct 1', columns='Construct 2', values='Jaccard Similarity')

    # Mirror the matrix to ensure symmetry
    jaccard_pivot = jaccard_pivot.combine_first(jaccard_pivot.T)

    # Fill diagonal with 1s for Jaccard Similarity
    for construct in jaccard_pivot.index:
        jaccard_pivot.loc[construct, construct] = 1

    # Plot heatmap for Jaccard Similarity
    fig = plt.figure(figsize=(16, 9), tight_layout=True)
    ax = sns.heatmap(jaccard_pivot, annot=True, cmap='viridis', fmt='.2f', cbar_kws={'label': 'Jaccard Similarity'})

    # Customize the x and y axis labels
    plt.setp(ax.get_xticklabels(), color='black')  # Reset all labels to black first

    # Color specific labels
    color_text(ax.get_xticklabels())
    color_text(ax.get_yticklabels())

    plt.title('Jaccard Similarity Heatmap for Construct Pairs', fontweight='bold')
    fig_name = 'heatmap_jaccard_similarity_construct_pairs.png'
    fig.savefig(os.path.join(save_dir, fig_name), dpi=300)
    logger.success(f"Figure {fig_name} successfully saved in {save_dir}.")
    plt.close(fig)

    # 1.2) Heatmap for Dice Coefficient

    # Create a pivot table for Dice Coefficient
    dice_pivot = df.pivot_table(index='Construct 1', columns='Construct 2', values='Dice Coefficient')

    # Mirror the matrix to ensure symmetry
    dice_pivot = dice_pivot.combine_first(dice_pivot.T)

    # Fill diagonal with 1s for Dice Coefficient
    for construct in dice_pivot.index:
        dice_pivot.loc[construct, construct] = 1

    # Plot heatmap for Dice Coefficient
    fig = plt.figure(figsize=(16, 9), tight_layout=True)
    ax = sns.heatmap(dice_pivot, annot=True, cmap='viridis', fmt='.2f', cbar_kws={'label': 'Dice Coefficient'})

    # Customize the x and y axis labels
    plt.setp(ax.get_xticklabels(), color='black')  # Reset all labels to black first

    # Color specific labels
    color_text(ax.get_xticklabels())
    color_text(ax.get_yticklabels())

    plt.title('Dice Coefficient Heatmap for Construct Pairs', fontweight='bold')
    fig_name = 'heatmap_dice_coefficient_construct_pairs.png'
    fig.savefig(os.path.join(save_dir, fig_name), dpi=300)
    logger.success(f"Figure {fig_name} successfully saved in {save_dir}.")
    plt.close(fig)

    ### 2) Network Graph

    # Number of top pairs to visualize
    N = 15

    # Select top N pairs for Jaccard Similarity
    top_jaccard = df.nlargest(N, 'Jaccard Similarity')

    # Select top N pairs for Dice Coefficient
    top_dice = df.nlargest(N, 'Dice Coefficient')

    # Function to create a network graph with a legend
    def plot_network(data, title, metric_label, fig_name):
        # Create an empty graph
        G = nx.Graph()

        # Add edges to the graph
        for _, row in data.iterrows():
            G.add_edge(row['Construct 1'], row['Construct 2'], weight=row[metric_label])

        # Draw the graph
        pos = nx.circular_layout(G)
        weights = [G[u][v]['weight'] for u, v in G.edges()]

        # Create a figure and axis for the plot
        fig, ax = plt.subplots(figsize=(16, 9), tight_layout=True)

        # Draw nodes and edges
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, edge_color=weights,
                edge_cmap=plt.cm.viridis, width=3, edge_vmin=min(weights), edge_vmax=max(weights), ax=ax)

        # Add a color bar
        sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=plt.Normalize(vmin=min(weights), vmax=max(weights)))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)  # Associate the color bar with the current axis
        cbar.set_label(metric_label)

        plt.title(title, fontweight='bold')
        fig.savefig(os.path.join(save_dir, fig_name), dpi=300)
        logger.success(f"Figure {fig_name} successfully saved in {save_dir}.")
        plt.close(fig)

    # Plot network for Jaccard Similarity
    plot_network(top_jaccard, f'Top {N} Pairs Network by Jaccard Similarity', 'Jaccard Similarity',
                 fig_name='network_top_jaccard_similarity_pairs.png')

    # Plot network for Dice Coefficient
    plot_network(top_dice, f'Top {N} Pairs Network by Dice Coefficient', 'Dice Coefficient',
                 fig_name='network_top_dice_coefficient_pairs.png')

    # 3. Scatter plot
    fig = plt.figure(figsize=(16, 9), tight_layout=True)
    scatter_plot = sns.scatterplot(data=df, x='Jaccard Similarity', y='Dice Coefficient', hue='Construct Pair',
                                   # Different colors for different construct pairs
                                   palette='viridis',  # Color palette for the scatter plot
                                   s=100,  # Size of the markers
                                   legend=False  # Remove the legend for each point
                                   )

    # Customize the plot
    plt.title('Scatter Plot of Jaccard Similarity vs. Dice Coefficient', fontweight='bold')
    plt.xlabel('Jaccard Similarity')
    plt.ylabel('Dice Coefficient')
    plt.grid(True)

    # Show the plot
    plt.tight_layout()
    fig_name = 'scatter_jaccard_vs_dice_similarity.png'
    fig.savefig(os.path.join(save_dir, fig_name), dpi=300)
    logger.success(f"Figure {fig_name} successfully saved in {save_dir}.")
    plt.close(fig)

    # 4. Box Plot

    # Create a mirrored dataframe for the missing (y, x) pairs
    mirror_df = df.copy()
    mirror_df['Construct 1'], mirror_df['Construct 2'] = df['Construct 2'], df['Construct 1']

    # Concatenate the original and mirrored dataframes
    full_df = pd.concat([df, mirror_df], ignore_index=True)

    # Create box plots grouped by the first construct
    fig = plt.figure(figsize=(16, 9), tight_layout=True)
    ax = sns.boxplot(data=full_df, x='Construct 1', y='Jaccard Similarity', hue='Construct 1', palette='viridis',
                     legend=False)
    # Customize x-axis label colors
    color_text(ax.get_xticklabels())

    plt.title('Box Plot of Jaccard Similarity by Construct', fontweight='bold')
    plt.xlabel('Construct')
    plt.ylabel('Jaccard Similarity')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
    plt.grid(True)
    plt.tight_layout()
    fig_name = 'boxplot_jaccard_similarity_by_construct.png'
    fig.savefig(os.path.join(save_dir, fig_name), dpi=300)
    logger.success(f"Figure {fig_name} successfully saved in {save_dir}.")
    plt.close(fig)

    fig = plt.figure(figsize=(16, 9), tight_layout=True)
    ax = sns.boxplot(data=full_df, x='Construct 1', y='Dice Coefficient', hue='Construct 1', palette='viridis',
                     legend=False)
    # Customize x-axis label colors
    color_text(ax.get_xticklabels())

    plt.title('Box Plot of Dice Coefficient by Construct', fontweight='bold')
    plt.xlabel('Construct')
    plt.ylabel('Dice Coefficient')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
    plt.grid(True)
    plt.tight_layout()
    fig_name = 'boxplot_dice_coefficient_by_construct.png'
    fig.savefig(os.path.join(save_dir, fig_name), dpi=300)
    logger.success(f"Figure {fig_name} successfully saved in {save_dir}.")
    plt.close(fig)
