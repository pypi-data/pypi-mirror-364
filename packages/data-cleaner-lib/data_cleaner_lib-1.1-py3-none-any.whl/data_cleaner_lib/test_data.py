import pandas as pd
import numpy as np


def generate_test_dataset() -> pd.DataFrame:
    """Generate a test dataset for DataCleaner with various edge cases.

    Returns:
        pd.DataFrame: A DataFrame containing test cases for data cleaning.
    """
    data = {
        'id': [1, 2, 2, 3, None, 4, 5, np.nan, 6, 7],
        'name': [
            'John Doe', 'jane doe  ', 'JOHN DOE', None, 'Mary Smith!@#',
            '  Bob Jones  ', '', 'Alice@Wonder', 'Tom_Hardy', np.nan
        ],
        'age': [
            25, None, 30, '28', 150, -5, 40, 'forty', np.nan, 999
        ],
        'salary': [
            50000, 60000, 60000, None, -1000, 75000, 0, 1e9, np.nan, 80000
        ],
        'email': [
            'john.doe@email.com', 'JANE@EMAIL.COM', 'invalid_email', None, 'mary.smith@',
            'bob.jones@email.com  ', '', 'alice@wonder.com', 'tom@hardy', np.nan
        ],
        'date_joined': [
            '2023-01-01', '2023-01-02', 'invalid', None, '2023-01-05',
            '2023/01/06', '2023-01-07', np.nan, '2023-01-09', '23-01-10'
        ],
        'category': [
            'A', 'B', 'B', 'a', None, 'C', ' ', 'A', 'B', np.nan
        ],
        'score': [
            95.5, 88.0, np.nan, 75.0, -10.0, 100.0, 0.0, 999.9, None, 85.5
        ]
    }

    df = pd.DataFrame(data)
    empty_row = pd.Series([np.nan] * len(df.columns), index=df.columns)
    df = pd.concat([df, empty_row.to_frame().T], ignore_index=True)

    return df