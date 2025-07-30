import pytest
import pandas as pd
import numpy as np
from datacleaner.cleaner import DataCleaner
from datacleaner.test_data import generate_test_dataset

def test_data_cleaner_initialization():
    df = generate_test_dataset()
    cleaner = DataCleaner(df)
    assert isinstance(cleaner.df, pd.DataFrame)
    assert cleaner.df.shape == df.shape

def test_preprocess_mixed_types():
    df = generate_test_dataset()
    cleaner = DataCleaner(df)
    cleaner.preprocess_mixed_types()
    assert pd.api.types.is_numeric_dtype(cleaner.df['age'])
    assert pd.api.types.is_datetime64_any_dtype(cleaner.df['date_joined'])

def test_handle_missing_values():
    df = generate_test_dataset()
    cleaner = DataCleaner(df)
    cleaner.preprocess_mixed_types()
    cleaner.handle_missing_values(strategy='mean')
    assert cleaner.df.isnull().sum().sum() == 0

def test_remove_duplicates():
    df = generate_test_dataset()
    cleaner = DataCleaner(df)
    cleaner.standardize_text()
    cleaner.remove_duplicates(subset=['id', 'name'])
    assert cleaner.df.duplicated(subset=['id', 'name']).sum() == 0

def test_handle_outliers():
    df = generate_test_dataset()
    cleaner = DataCleaner(df)
    cleaner.preprocess_mixed_types()
    cleaner.handle_missing_values(strategy='mean')
    cleaner.handle_outliers(columns=['age', 'salary', 'score'], method='zscore')
    assert cleaner.df['age'].max() < 100  # Outlier 999 should be replaced
    assert cleaner.df['salary'].max() < 1e6  # Outlier 1e9 should be replaced

def test_standardize_text():
    df = generate_test_dataset()
    cleaner = DataCleaner(df)
    cleaner.standardize_text(columns=['name', 'email'], preserve_email=True)
    assert cleaner.df['name'].str.contains(r'[^\w\s]', regex=True, na=False).sum() == 0
    assert cleaner.df['email'].str.contains(r'@', na=False).sum() > 0

def test_convert_dtypes():
    df = generate_test_dataset()
    cleaner = DataCleaner(df)
    cleaner.preprocess_mixed_types()
    cleaner.convert_dtypes({'age': 'int32', 'salary': 'float64', 'date_joined': 'datetime64[ns]'})
    assert cleaner.df['age'].dtype == 'int32'
    assert cleaner.df['salary'].dtype == 'float64'
    assert pd.api.types.is_datetime64_any_dtype(cleaner.df['date_joined'])

def test_empty_dataframe():
    df = pd.DataFrame()
    cleaner = DataCleaner(df)
    cleaner.handle_missing_values()
    assert cleaner.df.empty