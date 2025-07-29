#!/bin/env python
# -*- coding: utf-8 -*-


# ----------------------------------------------------------------#
# Plotting Utilities                                              #
# ----------------------------------------------------------------#
# These functions help in generating data visualizations.         #
# ----------------------------------------------------------------#


def stratified_barplot(data, var, strata, case_id, fill_color, xlab=None):
  """
  Creates a stratified bar plot showing the frequency distribution of a categorical
  variable across different strata, including an 'All cases' comparison group.

  Parameters:
  -----------
  data : pandas.DataFrame
    The DataFrame containing the variables of interest.
  var : str
    The name of the categorical variable in `data` to be plotted on the y-axis as
    frequencies.
  strata : str
    The name of the categorical variable in `data` to stratify by, displayed on the
    x-axis.
  case_id : str
    The name of the column in `data` used as the case identifier for counting
    observations.
  fill_color : dict or list
    Color specification for the bars. Can be a dictionary mapping variable categories
    to colors, or a list of colors.
  xlab : str, optional
    The label for the x-axis. If not provided, it defaults to the name of the `strata`
    variable with underscores replaced by spaces.

  Returns:
  --------
  plotnine.ggplot
    A ggplot object containing the stratified bar plot with:
      - Bars showing frequency distribution of `var` across `strata` categories.
      - An 'All cases' group for comparison.
      - Frequency percentages displayed above bars.
      - Sample counts (N=x) displayed below x-axis.
      - Dodged bar positioning for multiple categories.

  Notes:
  ------
  - Missing values in `var` are automatically filtered out before plotting and an error
  arises if no data is left after filtering.
  """
  import pandas as pd
  import numpy as np
  from plotnine import (
    ggplot,
    aes,
    geom_bar,
    geom_text,
    scale_y_continuous,
    scale_fill_manual,
    coord_cartesian,
    labs,
    theme_bw,
    theme,
    element_text,
    position_dodge,
    guides,
    guide_legend,
  )

  # Check `var` is categorical
  if not (data[var].dtype.name == 'category'):
    print(
      'The variable supplied to `var` was not a pandas Categorical variable. \
      Converting this variable to pandas Categorical with no specific ordering of \
      categories.'
    )
    data[var] = pd.Categorical(data[var])

  # Check `strata` is categorical
  if not (data[strata].dtype.name == 'category'):
    print(
      'The variable supplied to `strata` was not a pandas Categorical variable. \
      Converting this variable to pandas Categorical with no specific ordering of \
      categories.'
    )
    data[strata] = pd.Categorical(data[strata])

  # Filter out missing values for `var`
  plot_data = data[data[var].notna()]
  if plot_data.empty:
    raise ValueError(
      'No data available for `var` and `strata` after filtering out missing \
      values of `var`.'
    )

  # Get counts for each combination of `var` and `strata`
  strat_data = (
    plot_data.groupby([strata, var], observed=True)[case_id].count().reset_index()
  )

  # Ensure all combinations of categories are accounted for to avoid errors
  complete_combinations = pd.MultiIndex.from_product(
    [plot_data[strata].cat.categories, plot_data[var].cat.categories],
    names=[strata, var],
  )
  strat_data = (
    strat_data.set_index([strata, var]).reindex(complete_combinations).reset_index()
  )

  # Calculate frequencies
  total_counts = plot_data.groupby(strata, observed=True)[case_id].count().reset_index()
  total_counts = dict(zip(total_counts[strata], total_counts[case_id]))

  strat_data['freq'] = strat_data.apply(
    lambda row: row[case_id] / total_counts[row[strata]]
    if pd.notna(row[case_id])
    else pd.NA,
    axis=1,
  )

  # Aggregate data for all cases
  full_data = plot_data.groupby(var, observed=True)[case_id].count().reset_index()
  full_data[strata] = 'All cases'
  full_data['freq'] = full_data[case_id] / len(plot_data)

  # Combine full and stratified data and remove any missing frequencies
  summ_stats = pd.concat([full_data, strat_data], ignore_index=True)
  summ_stats = summ_stats[summ_stats['freq'].notna()]

  # Make labels for counts and frequencies
  summ_stats['count_lab'] = summ_stats[case_id].apply(lambda x: f'N={x}')
  summ_stats['freq_lab'] = summ_stats['freq'].apply(lambda x: f'{round(x * 100, 1)}%')

  # Ensure `strata` categories has initial ordering
  summ_stats[strata] = pd.Categorical(
    summ_stats[strata],
    categories=['All cases'] + list(plot_data[strata].cat.categories),
    ordered=True,
  )

  # Generate stratified bar plot
  if xlab is None:
    xlab = strata.replace('_', ' ')
  g = (
    ggplot(data=summ_stats)
    + aes(x=strata, y='freq', fill=var)
    + geom_bar(position='dodge', stat='identity', color='black')
    + geom_text(
      aes(y='freq + 0.1', label='freq_lab'),
      position=position_dodge(0.9),
      angle=90,
      size=12,
    )
    + geom_text(aes(y=-0.03, label='count_lab'), position=position_dodge(0.9), size=8)
    + scale_y_continuous(
      breaks=np.linspace(0, 1, 6), labels=lambda x: [f'{v:.0%}' for v in x]
    )
    + scale_fill_manual(name=var.replace('_', ' '), values=fill_color)
    + coord_cartesian(ylim=(0, 1))
    + labs(x=xlab, y='Frequency (%)')
    + guides(fill=guide_legend(position='top', ncol=2))
    + theme_bw()
    + theme(text=element_text(size=10), axis_text_x=element_text(angle=20, hjust=1))
  )

  return g


def stratified_violin_boxplot(data, var, strata, ylab, xlab=None):
  """
  Creates a violin box plot showing the distribution of a numerical variable across
  different strata, including an 'All cases' comparison group.

  Parameters:
  -----------
  data : pandas.DataFrame
    The DataFrame containing the variables of interest.
  var : str
    The name of the numerical variable in `data` to be plotted on the y-axis.
  strata : str
    The name of the categorical variable in `data` to stratify by, displayed on the
    x-axis.
  ylab : str
    The title for the y-axis, describing the numerical variable.
  xlab : str, optional
    The title for the x-axis. If not provided, it defaults to the name of the `strata`
    variable with underscores replaced by spaces.

  Returns:
  --------
  plotnine.ggplot
    A ggplot object containing the stratified violin box plot with:
      - Violin box plot showing distribution of `var` across `strata` categories as
      data densities (violin plot) and the median + interquartile range (box plot).
      - The mean and 95% confidence interval for each stratum displayed as a red point
      range.
      - An 'All cases' group for comparison.
      - Median values displayed as text labels on the plot.

  Notes:
  ------
  - Missing values in `var` are automatically filtered out before plotting and an error
  arises if no data is left after filtering.
  """
  import pandas as pd
  import numpy as np
  from plotnine import (
    ggplot,
    aes,
    geom_violin,
    geom_boxplot,
    geom_text,
    geom_jitter,
    stat_summary,
    coord_cartesian,
    labs,
    theme_bw,
    theme,
    element_text,
  )

  # Check `var` is numerical
  if data[var].dtype.kind not in ['i', 'f']:
    raise ValueError('The variable supplied to `var` must be numeric.')

  # Check `strata` is categorical
  if not (data[strata].dtype.name == 'category'):
    print(
      'The variable supplied to `strata` was not a pandas Categorical variable. \
      Converting this variable to pandas Categorical with no specific ordering of \
      categories.'
    )
    data[strata] = pd.Categorical(data[strata])

  # Filter out missing values for `var`
  plot_data = data[data[var].notna()]
  if plot_data.empty:
    raise ValueError(
      'No data available for `var` and `strata` after filtering out missing values of \
      `var`.'
    )

  # Add data for an all cases group
  plot_data = pd.concat([plot_data, plot_data])
  plot_data[strata] = pd.Categorical(
    plot_data[strata],
    categories=['All cases'] + plot_data[strata].cat.categories.tolist(),
    ordered=True,
  )
  plot_data.loc[
    plot_data.reset_index().index.to_numpy() >= (plot_data.shape[0] // 2),
    strata,
  ] = 'All cases'

  # Calculate median for each stratum of `strata`
  summ_stats = plot_data.groupby(strata, observed=True)[var].median().reset_index()
  summ_stats['median_lab'] = summ_stats[var].apply(
    lambda x: f'Median={int(round(x, 0))}'
  )

  # Generate violin boxplot
  if xlab is None:
    xlab = strata.replace('_', ' ')
  np.random.seed(1234)
  g = (
    ggplot(data=plot_data)
    + aes(y=var, x=strata)
    + geom_violin(scale='width', fill='lightgrey', color='black')
    + geom_boxplot(width=0.5, fill='white', color='black', outlier_size=0)
    + geom_jitter(width=0.05, color='black', size=3)
    + geom_text(aes(y=-0.03, label='median_lab'), size=10, data=summ_stats)
    + stat_summary(fun_data='mean_cl_normal', geom='pointrange', color='red', size=1)
    + coord_cartesian(ylim=(0, max(plot_data[var].dropna()) + 2))
    + labs(x=xlab, y=ylab)
    + theme_bw()
    + theme(text=element_text(size=10), axis_text_x=element_text(angle=20, hjust=1))
  )

  return g


def stratified_coef_w_ci(
  data, var, strata, coef, lower, upper, fill_color, xlab, pvalue=None
):
  """
  Creates a coefficient plot showing the estimated coefficients and confidence
  intervals of a numerical variable across different strata.

  Parameters:
  -----------
  data : pandas.DataFrame
    The DataFrame in "long" format that contains columns denoting the names of the
    tested variables (`var`), groups tested (`strata`), coefficients (`coef`), and the
    lower (`lower`) and upper (`upper`) limits of the coefficient confidence interval.
    Optionally, it can also contain p-values (`pvalue`) for each coefficient.
  var : str
    The column in `data` denoting names of tested variables to be plotted on the y-axis.
    The plot will be faceted by this variable.
  strata : str
    The name of the categorical variable in `data` to stratify by, displayed as
    different color points and ranges.
  coef : float
    The column in `data` denoting the estimated coefficients for each stratum of
    `strata` and variable of `var`.
  lower : float
    The column in `data` denoting the lower limit of the confidence interval for each
    coefficient.
  upper : float
    The column in `data` denoting the upper limit of the confidence interval for each
    coefficient
  fill_color : dict or list
    Color specification for the points and ranges. Can be a dictionary mapping variable
    categories to colors, or a list of colors.
  xlab : str
    The title for the x-axis describing the coefficients being plotted.
  pvalue : float, optional
    The column in `data` denoting the p-values for each coefficient. If provided,
    p-values will be displayed as text labels on the plot. If not provided, no p-values
    will be displayed.

  Returns:
  --------
  plotnine.ggplot
    A ggplot object containing the coefficient plot with:
      - Coefficients displayed as points with error bars representing confidence
      intervals.
      - An 'All cases' group for comparison.
      - P-values displayed as text labels on the plot if provided.
  """
  import pandas as pd
  from plotnine import (
    ggplot,
    aes,
    geom_vline,
    geom_errorbarh,
    geom_point,
    geom_text,
    position_dodge,
    scale_fill_manual,
    scale_color_manual,
    facet_grid,
    coord_cartesian,
    theme_bw,
    theme,
    element_text,
    element_blank,
    element_rect,
    labs,
  )

  # Check `var` is numerical
  if not (data[var].dtype.name == 'category'):
    print(
      'The variable supplied to `var` was not a pandas Categorical variable. \
      Converting this variable to pandas Categorical with no specific ordering of \
      categories.'
    )
    data[var] = pd.Categorical(data[var])

  # Check `strata` is categorical
  if not (data[strata].dtype.name == 'category'):
    print(
      'The variable supplied to `strata` was not a pandas Categorical variable. \
      Converting this variable to pandas Categorical with no specific ordering of \
      categories.'
    )
    data[strata] = pd.Categorical(data[strata])

  # Check `coef`, `lower`, and `upper` are numerical
  if data[coef].dtype.kind not in ['i', 'f']:
    raise ValueError('The variable supplied to `coef` must be numeric.')
  if data[lower].dtype.kind not in ['i', 'f']:
    raise ValueError('The variable supplied to `lower` must be numeric.')
  if data[upper].dtype.kind not in ['i', 'f']:
    raise ValueError('The variable supplied to `upper` must be numeric.')
  if pvalue and data[pvalue].dtype.kind not in ['i', 'f']:
    raise ValueError('The variable supplied to `pvalue` must be numeric.')

  # If `pvalue` provided, create p-value labels
  if pvalue:
    data['pvalue_labs'] = data[pvalue].apply(
      lambda x: f'P={x:.1e}' if x < 0.005 else f'P={x:.2f}' if x >= 0.005 else ''
    )

  # Generate coefficient plot
  g = (
    ggplot(data=data)
    + aes(x=coef, y=strata, color=strata)
    + geom_vline(xintercept=0, linetype='dashed')
    + geom_errorbarh(
      aes(xmin=lower, xmax=upper),
      position=position_dodge(0.3),
      height=0.01,
      size=1,
      show_legend=False,
    )
    + geom_point(position=position_dodge(0.3), size=3)
    + scale_fill_manual(values=fill_color)
    + scale_color_manual(values=fill_color)
    + facet_grid(f'{var} ~ .')
    + theme_bw()
    + theme(
      text=element_text(size=10),
      axis_text_y=element_blank(),
      axis_ticks_major_y=element_blank(),
      axis_title_y=element_blank(),
      axis_title_x=element_text(margin={'t': 20}),
      legend_text=element_text(size=10),
      legend_title=element_text(size=10),
      strip_text_y=element_text(angle=0),
      strip_background=element_rect(fill='lightgrey'),
    )
    + labs(x=xlab)
  )

  # Add p-value labels if provided
  if pvalue:
    g = (
      g
      + geom_text(
        aes(label='pvalue_labs'),
        x=data[upper].max() + 0.1,
        ha='left',
        size=8,
        show_legend=False,
        nudge_x=0.1,
      )
      + coord_cartesian(xlim=(data[lower].min(), data[upper].max() + 1.1))
    )

  return g
