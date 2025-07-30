import pandas as pd
import numpy as np
from typing import Union, List, Dict, Optional
import logging
from scipy import stats

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataCleaner:
    """A class for comprehensive data cleaning with edge case handling.

    Args:
        dataframe (pd.DataFrame): Input pandas DataFrame to clean.
    """

    def __init__(self, dataframe: pd.DataFrame):
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        self.df = dataframe.copy()
        self.original_shape = self.df.shape

    def preprocess_mixed_types(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Preprocess columns with mixed types to ensure consistent data types.

        Args:
            columns: List of columns to preprocess (None for all object-type columns).

        Returns:
            pd.DataFrame: DataFrame with preprocessed columns.
        """
        try:
            columns = columns if columns else self.df.select_dtypes(include=['object']).columns
            for col in columns:
                if col not in self.df.columns:
                    logger.warning(f"Column {col} not found in DataFrame")
                    continue
                # Replace empty strings with NaN
                self.df[col] = self.df[col].replace('', np.nan)
                # Try datetime conversion for date-like columns
                if 'date' in col.lower():
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                # Try numeric conversion for other columns, but skip text-heavy columns
                elif col not in ['name', 'email', 'category']:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            logger.info(f"Preprocessed mixed types: {columns}")
            return self.df
        except Exception as e:
            logger.error(f"Error preprocessing mixed types: {str(e)}")
            raise

    def handle_missing_values(self,
                              columns: Optional[List[str]] = None,
                              strategy: str = 'median',
                              custom_value: Union[int, float, str] = None) -> pd.DataFrame:
        """Handle missing values with various strategies.

        Args:
            columns: List of columns to process (None for all).
            strategy: 'mean', 'median', 'mode', 'drop', or 'custom'.
            custom_value: Value to use when strategy='custom'.

        Returns:
            pd.DataFrame: DataFrame with handled missing values.
        """
        try:
            columns = columns if columns else self.df.columns

            for col in columns:
                if col not in self.df.columns:
                    logger.warning(f"Column {col} not found in DataFrame")
                    continue

                if self.df[col].isnull().sum() == 0:
                    logger.info(f"No missing values in column {col}")
                    continue

                if strategy == 'drop':
                    self.df = self.df.dropna(subset=[col])
                elif strategy == 'custom' and custom_value is not None:
                    self.df[col] = self.df[col].fillna(custom_value)
                elif strategy in ['mean', 'median', 'mode']:
                    if pd.api.types.is_numeric_dtype(self.df[col]):
                        if strategy == 'mean':
                            fill_value = self.df[col].mean()
                        elif strategy == 'median':
                            fill_value = self.df[col].median()
                        else:  # mode
                            mode_series = self.df[col].mode()
                            fill_value = mode_series.iloc[0] if not mode_series.empty else 0
                        self.df[col] = self.df[col].fillna(fill_value)
                    else:
                        # Handle non-numeric columns
                        if self.df[col].dropna().empty:
                            fill_value = 'unknown'
                        else:
                            mode_series = self.df[col].mode()
                            fill_value = mode_series.iloc[0] if not mode_series.empty else 'unknown'
                        self.df[col] = self.df[col].fillna(fill_value)
                else:
                    raise ValueError(f"Invalid strategy: {strategy}")

            logger.info(f"Missing values handled. New shape: {self.df.shape}")
            return self.df
        except Exception as e:
            logger.error(f"Error handling missing values: {str(e)}")
            raise

    def remove_duplicates(self,
                          subset: Optional[List[str]] = None,
                          keep: str = 'first') -> pd.DataFrame:
        """Remove duplicate rows from the DataFrame.

        Args:
            subset: Columns to consider for duplicates (None for all).
            keep: 'first', 'last', or False.

        Returns:
            pd.DataFrame: DataFrame with duplicates removed.
        """
        try:
            initial_rows = self.df.shape[0]
            self.df = self.df.drop_duplicates(subset=subset, keep=keep)
            removed = initial_rows - self.df.shape[0]
            logger.info(f"Removed {removed} duplicate rows")
            return self.df
        except Exception as e:
            logger.error(f"Error removing duplicates: {str(e)}")
            raise

    def handle_outliers(self,
                        columns: Optional[List[str]] = None,
                        method: str = 'zscore',
                        threshold: float = 0.8) -> pd.DataFrame:  # Stricter threshold
        """Handle outliers using IQR or Z-score method.

        Args:
            columns: List of columns to process (None for numeric columns).
            method: 'iqr' or 'zscore'.
            threshold: Threshold for outlier detection (default 0.8 for zscore).

        Returns:
            pd.DataFrame: DataFrame with outliers handled.
        """
        try:
            columns = columns if columns else self.df.select_dtypes(include=[np.number]).columns

            for col in columns:
                if col not in self.df.columns:
                    logger.warning(f"Column {col} not found in DataFrame")
                    continue

                if not pd.api.types.is_numeric_dtype(self.df[col]):
                    logger.warning(f"Column {col} is not numeric, skipping")
                    continue

                if method == 'iqr':
                    Q1 = self.df[col].quantile(0.25)
                    Q3 = self.df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    self.df[col] = self.df[col].clip(lower=lower_bound, upper=upper_bound)
                elif method == 'zscore':
                    # Compute Z-scores only on non-NaN values
                    valid_data = self.df[col].dropna()
                    if valid_data.empty:
                        logger.warning(f"Column {col} has no valid data for outlier detection")
                        continue
                    logger.debug(f"Before outlier handling - {col} values: {valid_data.to_dict()}")
                    z_scores = np.abs(stats.zscore(valid_data))
                    logger.debug(f"Z-scores for {col}: {dict(zip(valid_data.index, z_scores))}")
                    # Use median of non-outlier values
                    non_outlier_data = valid_data[z_scores < threshold]
                    median = non_outlier_data.median() if not non_outlier_data.empty else valid_data.median()
                    # Create mask for outliers in original DataFrame
                    outlier_indices = valid_data[z_scores >= threshold].index
                    if not outlier_indices.empty:
                        logger.info(f"Replacing outliers in {col} at indices {outlier_indices} with median {median}")
                        self.df.loc[outlier_indices, col] = median
                    # Column-specific clipping
                    if col == 'age' and self.df[col].max() >= 100:
                        logger.warning(f"Age values exceed 100 (max={self.df[col].max()}); clipping to median {median}")
                        self.df.loc[self.df[col] >= 100, col] = median
                    if col == 'salary' and self.df[col].max() >= 1e6:
                        logger.warning(
                            f"Salary values exceed 1e6 (max={self.df[col].max()}); clipping to median {median}")
                        self.df.loc[self.df[col] >= 1e6, col] = median
                    logger.debug(f"After outlier handling - {col} values: {self.df[col].to_dict()}")
                else:
                    raise ValueError(f"Invalid method: {method}")

            logger.info(f"Outliers handled for columns: {columns}")
            return self.df
        except Exception as e:
            logger.error(f"Error handling outliers: {str(e)}")
            raise

    def standardize_text(self,
                         columns: Optional[List[str]] = None,
                         lowercase: bool = True,
                         remove_special: bool = True,
                         preserve_email: bool = False) -> pd.DataFrame:
        """Standardize text columns by cleaning and normalizing.

        Args:
            columns: List of columns to process (None for string columns).
            lowercase: Convert to lowercase.
            remove_special: Remove special characters (except for emails if preserve_email=True).
            preserve_email: Preserve '@' and '.' in email columns.

        Returns:
            pd.DataFrame: DataFrame with standardized text.
        """
        try:
            columns = columns if columns else self.df.select_dtypes(include=['object']).columns

            for col in columns:
                if col not in self.df.columns:
                    logger.warning(f"Column {col} not found in DataFrame")
                    continue

                if lowercase:
                    self.df[col] = self.df[col].str.lower()

                if remove_special:
                    if preserve_email and 'email' in col.lower():
                        self.df[col] = self.df[col].str.replace(r'[^\w\s@.]', '', regex=True)
                    else:
                        self.df[col] = self.df[col].str.replace(r'[^\w\s]', '', regex=True)

                self.df[col] = self.df[col].str.strip().str.replace(r'\s+', ' ', regex=True)

            logger.info(f"Text standardized for columns: {columns}")
            return self.df
        except Exception as e:
            logger.error(f"Error standardizing text: {str(e)}")
            raise

    def convert_dtypes(self,
                       column_types: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """Convert column data types with error handling.

        Args:
            column_types: Dictionary of column names and target types.

        Returns:
            pd.DataFrame: DataFrame with converted data types.
        """
        try:
            if not column_types:
                for col in self.df.columns:
                    try:
                        self.df[col] = pd.to_numeric(self.df[col], errors='ignore')
                    except:
                        pass
            else:
                for col, dtype in column_types.items():
                    if col not in self.df.columns:
                        logger.warning(f"Column {col} not found in DataFrame")
                        continue
                    try:
                        if dtype.startswith('int') and self.df[col].isnull().any():
                            # Fill NaN with median for integer conversion
                            fill_value = self.df[col].median() if pd.api.types.is_numeric_dtype(self.df[col]) else 0
                            logger.warning(f"Filling NaN in {col} with {fill_value} for {dtype} conversion")
                            self.df[col] = self.df[col].fillna(fill_value)
                        self.df[col] = self.df[col].astype(dtype)
                    except Exception as e:
                        logger.warning(f"Could not convert {col} to {dtype}: {str(e)}")

            logger.info("Data types converted")
            return self.df
        except Exception as e:
            logger.error(f"Error converting data types: {str(e)}")
            raise

    def get_cleaned_data(self) -> pd.DataFrame:
        """Return the cleaned DataFrame."""
        return self.df

    def cleaning_report(self) -> str:
        """Generate a report of cleaning operations performed.

        Returns:
            str: Cleaning summary.
        """
        try:
            report = f"""
Data Cleaning Report
===================
Original Shape: {self.original_shape}
Current Shape: {self.df.shape}
Missing Values: {self.df.isnull().sum().sum()}
Columns: {list(self.df.columns)}
Data Types:
{self.df.dtypes}
===================
"""
            return report
        except Exception as e:
            logger.error(f"Error generating cleaning report: {str(e)}")
            raise