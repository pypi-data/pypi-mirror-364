import pandas as pd
from pycodebox import (
  stratified_barplot,
  stratified_violin_boxplot,
  stratified_coef_w_ci,
)


def test_stratified_barplot():
  df = pd.DataFrame(
    {
      'var': pd.Categorical(['cat1', 'cat2', 'cat1', 'cat2']),
      'strata': pd.Categorical(['A', 'A', 'B', 'B']),
      'case_id': [1, 2, 3, 4],
    }
  )
  p = stratified_barplot(
    df, 'var', 'strata', 'case_id', fill_color=['red', 'blue']
  )
  assert p is not None


def test_stratified_violin_boxplot():
  df = pd.DataFrame(
    {
      'var': [1.0, 2.5, 3.1, 4.8],
      'strata': pd.Categorical(['A', 'A', 'B', 'B']),
    }
  )
  p = stratified_violin_boxplot(df, 'var', 'strata', ylab='Value')
  assert p is not None


def test_stratified_coef_w_ci():
  df = pd.DataFrame(
    {
      'var': pd.Categorical(['V1', 'V1']),
      'strata': pd.Categorical(['A', 'B']),
      'coef': [0.5, -0.5],
      'lower': [0.2, -0.8],
      'upper': [0.8, -0.2],
      'pvalue': [0.04, 0.02],
    }
  )
  p = stratified_coef_w_ci(
    df,
    'var',
    'strata',
    'coef',
    'lower',
    'upper',
    fill_color=['red', 'blue'],
    xlab='Effect Size',
    pvalue='pvalue',
  )
  assert p is not None
