import numpy as np
import pandas as pd
from pycodebox import (
  stratified_barplot,
  stratified_violin_boxplot,
  stratified_coef_w_ci,
)


def test_stratified_barplot_required_params():
  df = pd.DataFrame(
    {
      'gender': pd.Categorical(
        np.random.choice(['Male', 'Female'], size=100, replace=True)
      ),
      'treatment': pd.Categorical(
        np.random.choice(['Treatment', 'Control'], size=100, replace=True)
      ),
      'case_id': np.arange(1, 100 + 1),
    }
  )
  p = stratified_barplot(df, 'gender', 'treatment', 'case_id')
  assert p is not None


def test_stratified_barplot_full_params():
  df = pd.DataFrame(
    {
      'gender': pd.Categorical(
        np.random.choice(['Male', 'Female'], size=100, replace=True)
      ),
      'treatment': pd.Categorical(
        np.random.choice(['Treatment', 'Control'], size=100, replace=True)
      ),
      'case_id': np.arange(1, 100 + 1),
    }
  )
  p = stratified_barplot(
    df,
    'gender',
    'treatment',
    'case_id',
    fill_color=['grey', 'black'],
    xlab='Treatment group',
  )
  assert p is not None


def test_stratified_violin_boxplot_required_params():
  df = pd.DataFrame(
    {
      'survival': pd.concat(
        [
          pd.Series(np.random.uniform(50, 100, size=50)),
          pd.Series(np.random.uniform(0, 50, size=50)),
        ]
      ),
      'treatment': pd.Categorical(['Treatment'] * 50 + ['Control'] * 50),
    }
  )
  p = stratified_violin_boxplot(df, 'survival', 'treatment')
  assert p is not None


def test_stratified_violin_boxplot_full_params():
  df = pd.DataFrame(
    {
      'survival': pd.concat(
        [
          pd.Series(np.random.uniform(50, 100, size=50)),
          pd.Series(np.random.uniform(0, 50, size=50)),
        ]
      ),
      'treatment': pd.Categorical(['Treatment'] * 50 + ['Control'] * 50),
    }
  )
  p = stratified_violin_boxplot(
    df,
    'survival',
    'treatment',
    ylab='Survival (months)',
    xlab='Treatment group',
  )
  assert p is not None


def test_stratified_coef_w_ci_required_params():
  df = pd.DataFrame(
    {
      'genes': pd.Categorical(
        ['Gene1'] * 2 + ['Gene2'] * 2 + ['Gene3'] * 2 + ['Gene4'] * 2 + ['Gene5'] * 2
      ),
      'treatment': pd.Categorical(['Treatment', 'Control'] * 5),
      'coef': [0.5, -0.3, 0.2, -0.1, 0.4, -0.2, 0.3, -0.4, 0.1, -0.5],
      'lower': [0.2, -0.5, 0.1, -0.3, 0.1, -0.4, 0.2, -0.6, 0.05, -0.7],
      'upper': [0.8, -0.1, 0.3, 0.1, 0.7, 0.0, 0.4, -0.2, 0.15, -0.3],
      'pvalue': [0.01, 0.05, 0.03, 0.07, 0.02, 0.04, 0.0012, 0.08, 0.09, 0.10],
    }
  )
  p = stratified_coef_w_ci(df, 'genes', 'treatment', 'coef', 'lower', 'upper')
  assert p is not None


def test_stratified_coef_w_ci_full_params():
  df = pd.DataFrame(
    {
      'genes': pd.Categorical(
        ['Gene1'] * 2 + ['Gene2'] * 2 + ['Gene3'] * 2 + ['Gene4'] * 2 + ['Gene5'] * 2
      ),
      'treatment': pd.Categorical(['Treatment', 'Control'] * 5),
      'coef': [0.5, -0.3, 0.2, -0.1, 0.4, -0.2, 0.3, -0.4, 0.1, -0.5],
      'lower': [0.2, -0.5, 0.1, -0.3, 0.1, -0.4, 0.2, -0.6, 0.05, -0.7],
      'upper': [0.8, -0.1, 0.3, 0.1, 0.7, 0.0, 0.4, -0.2, 0.15, -0.3],
      'pvalue': [0.01, 0.05, 0.03, 0.07, 0.02, 0.04, 0.0012, 0.08, 0.09, 0.10],
    }
  )
  p = stratified_coef_w_ci(
    df,
    'genes',
    'treatment',
    'coef',
    'lower',
    'upper',
    pvalue='pvalue',
    fill_color=['grey', 'black'],
    xlab='Effect Size',
  )
  assert p is not None
