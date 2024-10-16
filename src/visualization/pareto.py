import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from icecream import ic
from loguru import logger
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator
from matplotlib.lines import Line2D

from src.utils import create_visualizations_out_dirs, color_text, append_chars_to_labels, bold_left_labels


def plot_pareto(dataset, output_dir: str, plot_type: str) -> None:
    """
    Plot Pareto chart for stereotype frequencies (either occurrence-wise or group-wise) from class and relation data.
    The x-axis will be ordered by the ranking of stereotypes.

    :param dataset: Dataset object containing models and statistics.
    :param output_dir: Directory to save the generated Pareto charts.
    :param plot_type: Either "occurrence" or "group" to specify which type of data to plot.
    """
    # Create output directories
    class_raw_out, class_clean_out, relation_raw_out, relation_clean_out = create_visualizations_out_dirs(output_dir,
                                                                                                          dataset.name)

    # Define a helper function to create Pareto charts for the specified data type
    def create_pareto_chart(data, title, output_path, plot_type):
        if plot_type == 'occurrence':
            # Calculate percentage frequency and cumulative percentage for occurrence-wise data
            data['Percentage Frequency'] = (data['Frequency'] / data['Frequency'].sum()) * 100
            data['Cumulative Percentage'] = data['Percentage Frequency'].cumsum()
            bar_color = 'skyblue'
            line_color = 'blue'
            bar_label = 'Occurrence-wise Frequency'
            line_label = 'Occurrence-wise Cumulative'
        elif plot_type == 'group':
            # Calculate percentage frequency and cumulative percentage for group-wise data
            data['Percentage Frequency'] = (data['Group-wise Frequency'] / data['Group-wise Frequency'].sum()) * 100
            data['Cumulative Percentage'] = data['Percentage Frequency'].cumsum()
            bar_color = 'lightgreen'
            line_color = 'green'
            bar_label = 'Group-wise Frequency'
            line_label = 'Group-wise Cumulative'

        # Create the plot
        fig, ax1 = plt.subplots(figsize=(16, 9), tight_layout=True)

        # Bar plot for the selected frequency
        bar_width = 0.4
        ax1.bar(data['Stereotype'], data['Percentage Frequency'], width=bar_width, label=bar_label, color=bar_color,
                zorder=1)

        # Line plot for the cumulative percentage
        ax2 = ax1.twinx()  # Create a second y-axis
        ax2.plot(range(len(data)), data['Cumulative Percentage'], color=line_color, marker='o', label=line_label,
                 linestyle='-', linewidth=2, zorder=2)

        # Set the y-axis label and ticks for the cumulative percentage
        ax2.set_ylabel('Cumulative Percentage (%)', fontsize=12)

        # Ensure the ticks on the right y-axis (ax2) are every 10%
        ax2.set_yticks(range(int(data['Cumulative Percentage'].min()), 101, 10))
        ax2.yaxis.set_major_locator(MultipleLocator(10))  # Set major ticks every 10%

        ax1.tick_params(axis='x', rotation=45)  # Rotate by 45 degrees
        color_text(ax1.get_xticklabels())  # Color specific x-axis labels

        # Add legends
        legend1 = ax1.legend(loc='upper left')
        legend2 = ax2.legend(loc='upper right')

        # Apply color to legend original_labels
        color_text(legend1.get_texts())
        color_text(legend2.get_texts())

        ax1.grid(False)  # Disable gridlines for the left y-axis

        # Ensure gridlines are below other plot elements
        ax2.set_axisbelow(True)
        ax2.grid(True, axis='y', which='major')

        # Save the plot
        fig_name = f"pareto_{plot_type}.png"
        fig.savefig(os.path.join(output_path, fig_name), dpi=300)
        logger.success(f"Figure {fig_name} successfully saved in {output_path}.")
        plt.close(fig)

    # Now generate Pareto charts based on the plot_type for class raw, class clean, relation raw, and relation clean datasets
    if plot_type == 'occurrence':
        create_pareto_chart(pd.DataFrame(dataset.class_statistics_raw['rank_frequency_distribution']),
                            'Pareto Chart: Class Raw (Occurrence-wise)', class_raw_out, plot_type)

        create_pareto_chart(pd.DataFrame(dataset.class_statistics_clean['rank_frequency_distribution']),
                            'Pareto Chart: Class Clean (Occurrence-wise)', class_clean_out, plot_type)

        create_pareto_chart(pd.DataFrame(dataset.relation_statistics_raw['rank_frequency_distribution']),
                            'Pareto Chart: Relation Raw (Occurrence-wise)', relation_raw_out, plot_type)

        create_pareto_chart(pd.DataFrame(dataset.relation_statistics_clean['rank_frequency_distribution']),
                            'Pareto Chart: Relation Clean (Occurrence-wise)', relation_clean_out, plot_type)

    elif plot_type == 'group':
        create_pareto_chart(pd.DataFrame(dataset.class_statistics_raw['rank_groupwise_frequency_distribution']),
                            'Pareto Chart: Class Raw (Group-wise)', class_raw_out, plot_type)

        create_pareto_chart(pd.DataFrame(dataset.class_statistics_clean['rank_groupwise_frequency_distribution']),
                            'Pareto Chart: Class Clean (Group-wise)', class_clean_out, plot_type)

        create_pareto_chart(pd.DataFrame(dataset.relation_statistics_raw['rank_groupwise_frequency_distribution']),
                            'Pareto Chart: Relation Raw (Group-wise)', relation_raw_out, plot_type)

        create_pareto_chart(pd.DataFrame(dataset.relation_statistics_clean['rank_groupwise_frequency_distribution']),
                            'Pareto Chart: Relation Clean (Group-wise)', relation_clean_out, plot_type)


def plot_pareto_combined(dataset, output_dir: str, coverage_limit: float = None) -> None:
    """
    Plot combined Pareto chart for occurrence-wise and group-wise stereotype frequencies from class and relation data
    (both raw and clean).

    :param dataset: Dataset object containing models and statistics.
    :param output_dir: Directory to save the generated Pareto charts.
    :param coverage_limit: Optional coverage limit value (between 0 and 1) to draw a vertical line on the plot.
    """
    # Create output directories
    class_raw_out, class_clean_out, relation_raw_out, relation_clean_out = create_visualizations_out_dirs(output_dir,
                                                                                                          dataset.name)

    # Define a helper function to create Pareto charts for a given dataset
    def create_pareto_chart(data_occurrence, data_groupwise, title, output_path, coverage_limit=None):
        # Calculate the percentage frequency for occurrence-wise and group-wise data
        data_occurrence['Percentage Frequency'] = (data_occurrence['Frequency'] / data_occurrence[
            'Frequency'].sum()) * 100
        data_groupwise['Percentage Group-wise Frequency'] = (data_groupwise['Group-wise Frequency'] / data_groupwise[
            'Group-wise Frequency'].sum()) * 100

        # Ensure that group-wise data is ordered based on occurrence-wise data
        data_groupwise = data_groupwise.set_index('Stereotype').reindex(data_occurrence['Stereotype']).reset_index()

        # Calculate cumulative percentages for occurrence-wise and group-wise data
        data_occurrence['Cumulative Percentage'] = data_occurrence['Percentage Frequency'].cumsum()
        data_groupwise['Group-wise Cumulative Percentage'] = data_groupwise['Percentage Group-wise Frequency'].cumsum()

        # Reset index to ensure integer indexing
        data_occurrence = data_occurrence.reset_index(drop=True)
        data_groupwise = data_groupwise.reset_index(drop=True)

        # Create the plot
        fig, ax1 = plt.subplots(figsize=(16, 9), tight_layout=True)

        # Set solid white background for the figure
        fig.patch.set_alpha(1)  # Ensure complete figure background opacity
        fig.patch.set_facecolor('white')  # Set background color to white

        # Bar plot for occurrence-wise frequency
        bar_width = 0.4
        ax1.bar(data_occurrence['Stereotype'], data_occurrence['Percentage Frequency'], width=bar_width,
                label='Occurrence-wise Frequency', align='center', color='skyblue', zorder=1)

        # Bar plot for group-wise frequency (shifted to the right)
        ax1.bar(data_groupwise['Stereotype'], data_groupwise['Percentage Group-wise Frequency'], width=bar_width,
                label='Group-wise Frequency', align='edge', color='lightgreen', zorder=1)

        # Calculate medians
        median_occurrence = np.median(data_occurrence['Percentage Frequency'])
        median_groupwise = np.median(data_groupwise['Percentage Group-wise Frequency'])

        # Plot horizontal dashed lines for the medians (keep simple labels for the legend)
        ax1.axhline(median_occurrence, color='blue', linestyle='--', linewidth=1.5, label='Occurrence-wise Median')
        ax1.axhline(median_groupwise, color='green', linestyle='--', linewidth=1.5, label='Group-wise Median')

        # Annotate the medians at the rightmost end of the lines
        ax1.annotate(f'{median_occurrence:.2f}%', xy=(len(data_occurrence) - 1, median_occurrence), xytext=(5, 5),
                     textcoords='offset points', color='blue', fontsize=10, fontweight='bold')

        ax1.annotate(f'{median_groupwise:.2f}%', xy=(len(data_groupwise) - 1, median_groupwise), xytext=(5, 5),
                     textcoords='offset points', color='green', fontsize=10, fontweight='bold')

        # Set labels and title
        ax1.set_ylabel('Relative Frequency (%)', fontsize=12)
        ax1.set_title(title, fontweight='bold', fontsize=14)

        # Rotate the labels by 90 degrees for better readability
        ax1.tick_params(axis='x', rotation=90)

        # Line plot for occurrence-wise cumulative percentage
        ax2 = ax1.twinx()  # Create a second y-axis

        ax2.plot(range(len(data_occurrence)), data_occurrence['Cumulative Percentage'], color='blue', marker='o',
                 label='Occurrence-wise Cumulative', linestyle='-', linewidth=2, zorder=2)

        # Line plot for group-wise cumulative percentage
        ax2.plot(range(len(data_groupwise)), data_groupwise['Group-wise Cumulative Percentage'], color='green',
                 marker='o', label='Group-wise Cumulative', linestyle='-', linewidth=2, zorder=2)

        if coverage_limit is not None:
            coverage_limit_percent = coverage_limit * 100

            # Find the index where both cumulative percentages exceed the coverage limit
            for i in range(len(data_occurrence)):
                occurrence_cumulative = data_occurrence.loc[i, 'Cumulative Percentage']
                groupwise_cumulative = data_groupwise.loc[i, 'Group-wise Cumulative Percentage']
                if min(occurrence_cumulative, groupwise_cumulative) >= coverage_limit_percent:
                    # Plot the vertical dashed line at this index
                    ax1.axvline(x=i, color='red', linestyle='--', label=f'{coverage_limit_percent:.1f}% coverage')

                    # Annotate the occurrence-wise cumulative percentage, automatically adjusted
                    ax2.annotate(f'{occurrence_cumulative:.1f}%', xy=(i, occurrence_cumulative),
                                 textcoords='offset points', xytext=(5, -5), ha='left', va='top', fontsize=10,
                                 color='blue')

                    # Annotate the group-wise cumulative percentage, automatically adjusted
                    ax2.annotate(f'{groupwise_cumulative:.1f}%', xy=(i, groupwise_cumulative),
                                 textcoords='offset points', xytext=(5, -5), ha='left', va='top', fontsize=10,
                                 color='green')

                    red_line_index = i
                    break

        # Set the y-axis label and ticks for the cumulative percentage
        ax2.set_ylabel('Cumulative Percentage (%)', fontsize=12)
        ax2.set_yticks(range(0, 101, 10))

        ax1.tick_params(axis='x', rotation=45)  # Rotate by 45 degrees
        texts = ax1.get_xticklabels()  # Color specific x-axis labels
        # Modify the labels with symbols
        texts = append_chars_to_labels(texts, data_occurrence, data_groupwise,
                                                             median_occurrence, median_groupwise)

        bold_left_labels(texts, red_line_index)

        for label in texts:
            # Align labels to the right, so the last character is near the corresponding tick
            label.set_ha('right')
            # Adjust the label positioning slightly if needed (use pad for further fine-tuning)
            label.set_position(
                (label.get_position()[0] - 0.02, label.get_position()[1]))  # Adjust the x-position slightly

        # Set the new x-tick labels
        ax1.set_xticks(range(len(texts)))  # Make sure the number of ticks matches the number of labels
        ax1.set_xticklabels(texts)  # Apply the new labels

        color_text(ax1.get_xticklabels())

        # Get the current x-tick positions
        x_positions = range(len(texts))

        # Explicitly set the x-tick positions to match the number of labels
        ax1.set_xticks(x_positions)

        # Apply the updated labels back to the axis
        ax1.set_xticklabels(texts)

        ax2.set_axisbelow(True)  # Ensure gridlines are below other plot elements
        ax1.grid(False)
        ax2.grid(True, axis='y', which='major')

        # Extract handles and labels from both axes
        handles1, labels1 = ax1.get_legend_handles_labels()  # Bar plot legend info (ax1)
        handles2, labels2 = ax2.get_legend_handles_labels()  # Line plot legend info (ax2)

        # Combine the handles and labels from both legends
        combined_handles = handles1 + handles2
        combined_labels = labels1 + labels2

        combined_legend = ax2.legend(combined_handles, combined_labels, loc='center right', bbox_to_anchor=(1, 0.5),
                                     frameon=True, facecolor='white', edgecolor='black', framealpha=1, shadow=True,
                                     handletextpad=1.5, borderaxespad=2, borderpad=1.5)

        # Set the zorder of the combined legend higher than other elements
        combined_legend.set_zorder(10)
        plt.draw()  # Force re-rendering of the plot, ensuring legend is drawn last

        # Customize the title: left-align and make it bold
        combined_legend.get_title().set_fontweight('bold')  # Make the title bold

        # Create proxy artists for the symbols
        legend_elements = [
            Line2D([0], [0], marker='+', color='black', linestyle='None', markersize=7,
                   label='value >= median (Occurrence-wise)'),
            Line2D([0], [0], marker='*', color='black', linestyle='None', markersize=7, label='value >= median (Group-wise)')
        ]

        # Add these proxies to the existing legend
        ax2.legend(
            handles=combined_handles + legend_elements,  # Combine previous handles with new ones
            loc='center right', bbox_to_anchor=(1, 0.5),
            frameon=True, facecolor='white', edgecolor='black', framealpha=1, shadow=True,
            handletextpad=1.5, borderaxespad=2, borderpad=1.5
        )

        # Save the plot
        fig_name = f"pareto_combined_cov_{coverage_limit}.png"
        # Ensure tight layout for the figure before saving
        plt.tight_layout()
        fig.savefig(os.path.join(output_path, fig_name), dpi=300, bbox_inches='tight')

        logger.success(f"Figure {fig_name} successfully saved in {output_path}.")
        plt.close(fig)

    # Now generate Pareto charts for class raw, class clean, relation raw, and relation clean datasets
    create_pareto_chart(pd.DataFrame(dataset.class_statistics_raw['rank_frequency_distribution']),
                        pd.DataFrame(dataset.class_statistics_raw['rank_groupwise_frequency_distribution']),
                        'Class Stereotypes Occurrences and Coverages', class_raw_out, coverage_limit)

    create_pareto_chart(pd.DataFrame(dataset.class_statistics_clean['rank_frequency_distribution']),
                        pd.DataFrame(dataset.class_statistics_clean['rank_groupwise_frequency_distribution']),
                        'Class Stereotypes Occurrences and Coverages', class_clean_out, coverage_limit)

    create_pareto_chart(pd.DataFrame(dataset.relation_statistics_raw['rank_frequency_distribution']),
                        pd.DataFrame(dataset.relation_statistics_raw['rank_groupwise_frequency_distribution']),
                        'Relation Stereotypes Occurrences and Coverages', relation_raw_out, coverage_limit)

    create_pareto_chart(pd.DataFrame(dataset.relation_statistics_clean['rank_frequency_distribution']),
                        pd.DataFrame(dataset.relation_statistics_clean['rank_groupwise_frequency_distribution']),
                        'Relation Stereotypes Occurrences and Coverages', relation_clean_out, coverage_limit)
