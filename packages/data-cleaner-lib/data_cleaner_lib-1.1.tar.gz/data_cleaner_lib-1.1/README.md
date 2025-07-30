# data_cleaner_lib: A Comprehensive Python Data Cleaning Library

`data_cleaner_lib` is a robust and intuitive Python library designed to streamline the often complex and time-consuming process of data cleaning for pandas DataFrames. It provides a comprehensive suite of tools to identify and rectify common data quality issues, including missing values, duplicates, outliers, and inconsistent text formats, with careful consideration for various edge cases. This library aims to empower data professionals and analysts to prepare their datasets for analysis and machine learning models with greater efficiency and reliability.

## Features

`data_cleaner_lib` offers a versatile set of functionalities to tackle diverse data cleaning challenges:

- **Handle Missing Values**: Impute or remove missing data using a variety of strategies:
  - `'mean'`: Replace missing numerical values with the column's mean.
  - `'median'`: Replace missing numerical values with the column's median.
  - `'mode'`: Replace missing values (numerical or categorical) with the most frequent value.
  - `'drop'`: Remove rows containing missing values in specified columns.
  - `'custom'` (value): Fill with a user-specified constant value.
- **Remove Duplicates**: Identify and eliminate redundant rows based on all columns or a specified subset, ensuring data uniqueness with options to keep `'first'`, `'last'`, or no duplicates.
- **Handle Outliers**: Detect and mitigate the impact of extreme values using statistical methods:
  - `'iqr'` (Interquartile Range): Cap values outside 1.5×IQR from quartiles.
  - `'zscore'`: Replace outliers with the median based on a Z-score threshold (default 0.8), with additional clipping for `age` (≥100) and `salary` (≥1e6).
- **Standardize Text Data**: Clean and normalize string columns to ensure consistency:
  - Convert to lowercase.
  - Strip leading/trailing whitespace.
  - Remove extra internal whitespace.
  - Handle special characters and non-alphanumeric data.
  - Optionally preserve email formats (retaining `@` and `.`) during standardization.
- **Convert Data Types**: Safely cast columns to desired data types (e.g., int, float, datetime), with error handling and automatic NaN filling for integer conversions.
- **Preprocess Mixed-Type Columns**: Automatically detect and handle columns with mixed data types, converting empty strings to NaN and attempting numeric or datetime conversions where appropriate.
- **Generate Cleaning Reports**: Obtain a comprehensive summary of cleaning operations, including original and current DataFrame shapes, missing values, and data types.
- **Chaining Operations**: The API supports method chaining for fluid, sequential application of cleaning steps.

## Installation

You can install `data_cleaner_lib` using pip:

```bash
pip install data_cleaner_lib
```

### Requirements

- Python >= 3.8
- pandas >= 1.5.0
- numpy >= 1.21.0
- scipy >= 1.7.0

## Usage

Here's a quick example demonstrating how to use `data_cleaner_lib` to clean a DataFrame:

```python
from data_cleaner_lib.cleaner import DataCleaner
import pandas as pd

# 1. Load or create a DataFrame
# For demonstration, we'll create a sample dataset with various data quality issues.
df = pd.DataFrame({
    'id': [1, 2, 2, 3, 4],
    'name': ['John Doe', 'Jane  Smith', 'Jane Smith', 'Bob@123', None],
    'email': ['john@doe.com', ' jane.smith@email.com ', 'jane.smith@email.com', 'bob@123.com', 'invalid@'],
    'age': [25, '30', None, 150, -5],
    'salary': [50000, 60000, 60000, 1e9, None],
    'category': ['A', 'B', 'B', None, 'C'],
    'date_joined': ['2023-01-01', '2023-02-01', '2023-02-01', 'invalid', None]
})
print("Original DataFrame Head:")
print(df.head())
print("\nOriginal DataFrame Info:")
df.info()

# 2. Initialize the DataCleaner with your DataFrame
cleaner = DataCleaner(df)

# 3. Apply cleaning operations sequentially

# Preprocess columns that might have mixed data types
print("\nApplying preprocess_mixed_types...")
cleaner.preprocess_mixed_types()

# Standardize text columns (e.g., 'name', 'email', 'category')
# preserve_email=True ensures email addresses are not corrupted during standardization.
print("\nApplying standardize_text...")
cleaner.standardize_text(columns=['name', 'email', 'category'], preserve_email=True)

# Remove duplicate rows based on a subset of columns
print("\nApplying remove_duplicates...")
cleaner.remove_duplicates(subset=['id', 'name'])

# Handle missing values: fill numerical NaNs with the median, and categorical NaNs with the mode
print("\nApplying handle_missing_values...")
cleaner.handle_missing_values(strategy='median', columns=['age', 'salary'])
cleaner.handle_missing_values(strategy='mode', columns=['category'])

# Handle outliers in numerical columns using the Z-score method
# Values with a Z-score > 0.8 or < -0.8 will be replaced with the median.
print("\nApplying handle_outliers...")
cleaner.handle_outliers(columns=['age', 'salary'], method='zscore')

# Convert data types for specific columns
print("\nApplying convert_dtypes...")
cleaner.convert_dtypes({
    'age': 'int32',
    'salary': 'float64',
    'date_joined': 'datetime64[ns]'
})

# 4. View results and get the cleaned DataFrame
print("\n--- Cleaning Report ---")
print(cleaner.cleaning_report())

print("\n--- Cleaned DataFrame Head ---")
cleaned_df = cleaner.get_cleaned_data()
print(cleaned_df.head())

print("\n--- Cleaned DataFrame Info ---")
cleaned_df.info()
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

> **Note**: The example DataFrame above is for demonstration purposes. Replace it with your actual data loading mechanism (e.g., `pd.read_csv('your_data.csv')`).
