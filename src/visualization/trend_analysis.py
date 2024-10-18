import os

from loguru import logger
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
import os

# Function to generate the regression visualization from two input CSV files
def generate_trend_visualization(df_occurrence, df_modelwise, output_dir, file_name):
    df_occurrence = df_occurrence.reset_index()
    df_modelwise = df_modelwise.reset_index()

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Extract the relevant columns ('year', 'none', 'other') from both DataFrames
    df_occurrence = df_occurrence[['year', 'none', 'other']].copy()
    df_modelwise = df_modelwise[['year', 'none', 'other']].copy()

    # Define the output file name based on the occurrence file name
    final_file_name = f'regression_plot_{file_name}.png'

    # Call the generate_regression_visualization function to generate the plot
    generate_regression_visualization(df_occurrence, df_modelwise, output_dir, final_file_name)



# Helper function to calculate and plot linear regression
def linear_regression_and_plot(df, column, period, ax, color, label, linestyle, marker=None):
    # Extract the relevant data for the period
    period_df = df[(df['year'].astype(int) >= period[0]) & (df['year'].astype(int) <= period[1])]
    X = np.array(period_df['year'].astype(int)).reshape(-1, 1)  # Years as independent variable
    y = np.array(period_df[column])  # Dependent variable (frequency)

    # Fit the linear regression model (1st degree)
    if len(X) > 1:  # Ensure there's enough data for regression
        model = LinearRegression().fit(X, y)
        y_pred = model.predict(X)

        # Plot the linear regression line (1st order)
        ax.plot(period_df['year'], y_pred, color=color, linestyle=linestyle, marker=marker,
                label=f'{label} ({period[0]}-{period[1]} Linear)', linewidth=2)


# Helper function to calculate and plot quadratic (2nd-degree) regression
def quadratic_regression_and_plot(df, column, period, ax, color, label, marker):
    # Extract the relevant data for the period (2015-2024)
    period_df = df[(df['year'].astype(int) >= period[0]) & (df['year'].astype(int) <= period[1])]
    X = np.array(period_df['year'].astype(int)).reshape(-1, 1)  # Years as independent variable
    y = np.array(period_df[column])  # Dependent variable (frequency)

    # Fit a quadratic regression model (2nd-degree polynomial)
    poly = PolynomialFeatures(degree=2)
    X_poly = poly.fit_transform(X)
    model = LinearRegression().fit(X_poly, y)
    y_pred = model.predict(X_poly)

    # Plot the quadratic regression curve (2nd order) with markers
    ax.plot(period_df['year'], y_pred, color=color, linestyle='-', marker=marker,
            label=f'{label} (2015-2024 Quadratic)', linewidth=2)


def generate_regression_visualization(df_occurrence, df_modelwise, out_dir_path, file_name, year_start=None,
                                      year_end=None):
    df_occurrence = df_occurrence.reset_index()
    df_modelwise = df_modelwise.reset_index()

    # Convert 'year' to int for filtering
    df_occurrence['year'] = df_occurrence['year'].astype(int)
    df_modelwise['year'] = df_modelwise['year'].astype(int)

    # Filter based on year_start and year_end
    if year_start is not None:
        df_occurrence = df_occurrence[df_occurrence['year'] >= year_start]
        df_modelwise = df_modelwise[df_modelwise['year'] >= year_start]
    if year_end is not None:
        df_occurrence = df_occurrence[df_occurrence['year'] <= year_end]
        df_modelwise = df_modelwise[df_modelwise['year'] <= year_end]

    # Ensure both DataFrames have the necessary columns ('year', 'none', 'other')
    if 'year' not in df_occurrence.columns or 'none' not in df_occurrence.columns or 'other' not in df_occurrence.columns:
        logger.error("Missing 'year', 'none', or 'other' columns in the occurrence-wise data.")
        return

    if 'year' not in df_modelwise.columns or 'none' not in df_modelwise.columns or 'other' not in df_modelwise.columns:
        logger.error("Missing 'year', 'none', or 'other' columns in the model-wise data.")
        return

    # Convert 'none' and 'other' to percentages for both occurrence-wise and model-wise data
    df_occurrence['none'] = df_occurrence['none'] * 100
    df_occurrence['other'] = df_occurrence['other'] * 100

    df_modelwise['none'] = df_modelwise['none'] * 100
    df_modelwise['other'] = df_modelwise['other'] * 100

    # Sort both DataFrames by year (just in case)
    df_occurrence = df_occurrence.sort_values('year')
    df_modelwise = df_modelwise.sort_values('year')

    # Convert 'year' to string in both DataFrames
    df_occurrence['year'] = df_occurrence['year'].astype(str)
    df_modelwise['year'] = df_modelwise['year'].astype(str)

    # Create the plot
    fig, ax1 = plt.subplots(figsize=(16, 9))  # Adjusted figure size for better layout

    # Define specific hex colors for 'none' and 'other'
    line_colors = {'none': '#d62728', 'other': '#1f77b4'}  # Red for 'none' and blue for 'other'

    ### Linear Regression (1st order) ###
    # Red lines (bars): continuous red lines for red bars (none occurrence)
    linear_regression_and_plot(df_occurrence, 'none', (2015, 2018), ax1, line_colors['none'], 'none (occurrence-wise)',
                               linestyle='-')
    linear_regression_and_plot(df_occurrence, 'none', (2019, 2024), ax1, line_colors['none'], 'none (occurrence-wise)',
                               linestyle='-')

    # Blue lines (bars): continuous blue lines for blue bars (other occurrence)
    linear_regression_and_plot(df_occurrence, 'other', (2015, 2018), ax1, line_colors['other'],
                               'other (occurrence-wise)', linestyle='-')
    linear_regression_and_plot(df_occurrence, 'other', (2019, 2024), ax1, line_colors['other'],
                               'other (occurrence-wise)', linestyle='-')

    # Red lines (curves): dashed red lines for red curves (none modelwise)
    linear_regression_and_plot(df_modelwise, 'none', (2015, 2018), ax1, line_colors['none'], 'none (model-wise)',
                               linestyle='--')
    linear_regression_and_plot(df_modelwise, 'none', (2019, 2024), ax1, line_colors['none'], 'none (model-wise)',
                               linestyle='--')

    # Blue lines (curves): dashed blue lines for blue curves (other modelwise)
    linear_regression_and_plot(df_modelwise, 'other', (2015, 2018), ax1, line_colors['other'], 'other (model-wise)',
                               linestyle='--')
    linear_regression_and_plot(df_modelwise, 'other', (2019, 2024), ax1, line_colors['other'], 'other (model-wise)',
                               linestyle='--')

    ### Quadratic Regression (2nd order) ###
    # Red marked curve using circles (none occurrence)
    quadratic_regression_and_plot(df_occurrence, 'none', (2015, 2024), ax1, line_colors['none'],
                                  'none (occurrence-wise)', marker='o')

    # Red marked curve using squares (none modelwise)
    quadratic_regression_and_plot(df_modelwise, 'none', (2015, 2024), ax1, line_colors['none'], 'none (model-wise)',
                                  marker='s')

    # Blue marked curve using circles (other occurrence)
    quadratic_regression_and_plot(df_occurrence, 'other', (2015, 2024), ax1, line_colors['other'],
                                  'other (occurrence-wise)', marker='o')

    # Blue marked curve using squares (other modelwise)
    quadratic_regression_and_plot(df_modelwise, 'other', (2015, 2024), ax1, line_colors['other'], 'other (model-wise)',
                                  marker='s')

    # Set labels for the axis
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Frequency (%)', color='black')
    ax1.tick_params(axis='y', labelcolor='black')

    # Add title
    title = f"Linear and Quadratic Regression for 'none' and 'other' (2015-2024)"
    plt.title(title, fontweight='bold')

    # Display the legend
    ax1.legend(loc='upper right')

    # Save the figure
    fig_name = f"regression_visualization_{file_name}"
    plt.savefig(os.path.join(out_dir_path, fig_name), dpi=300)
    logger.success(f"Figure {fig_name} successfully saved in {out_dir_path}.")
    # Close the plot to free memory
    plt.close()
