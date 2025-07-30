"""
Data standardization functions for consistent RBA data format.

This module ensures that all data sources (CSV, Excel) return data in the same
standardized format with consistent column names and data types.
"""


import pandas as pd


def standardize_rba_dataframe(
    df: pd.DataFrame, source: str = "unknown"
) -> pd.DataFrame:
    """
    Standardize an RBA DataFrame to ensure consistent column names and format.

    This function takes a DataFrame from any RBA data source and converts it
    to the standard format used throughout rbadata.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame from any RBA source
    source : str, default "unknown"
        Source of the data ("csv", "excel", "api", etc.)

    Returns
    -------
    pd.DataFrame
        Standardized DataFrame with consistent columns

    Standard Columns
    ---------------
    The standardized format includes these columns:
    - date : datetime64[ns] - The observation date
    - series_id : object - RBA series identifier (e.g., 'FIRMMCRTD')
    - value : float64 - The numeric value
    - description : object - Human-readable series description
    - units : object - Units of measurement (e.g., 'Percent per annum')
    - table : object - RBA table number (e.g., 'F1')
    - frequency : object - Data frequency (e.g., 'Daily', 'Monthly')
    - series_type : object - Type of series (e.g., 'Original', 'Seasonally Adjusted')
    - source : object - Data source identifier
    """
    # Make a copy to avoid modifying the original
    df_std = df.copy()

    # Map common column variations to standard names
    column_mapping = {
        # Date columns
        "Date": "date",
        "DATE": "date",
        # Series ID variations
        "series": "series_id",
        "Series": "series_id",
        "SERIES_ID": "series_id",
        "SeriesID": "series_id",
        "series_code": "series_id",
        # Value columns
        "Value": "value",
        "VALUE": "value",
        "data": "value",
        "observation": "value",
        # Description variations
        "Description": "description",
        "DESCRIPTION": "description",
        "series_name": "description",
        "title": "description",
        # Table variations
        "table_no": "table",
        "Table": "table",
        "TABLE": "table",
        "table_number": "table",
        # Units variations
        "Units": "units",
        "UNITS": "units",
        "unit": "units",
        "measurement": "units",
        # Frequency variations
        "Frequency": "frequency",
        "FREQUENCY": "frequency",
        "freq": "frequency",
        # Series type variations
        "SeriesType": "series_type",
        "Series Type": "series_type",
        "type": "series_type",
    }

    # Rename columns using the mapping
    df_std = df_std.rename(columns=column_mapping)

    # Ensure required columns exist
    required_columns = ["date", "series_id", "value"]
    missing_required = [col for col in required_columns if col not in df_std.columns]

    if missing_required:
        raise ValueError(f"Missing required columns: {missing_required}")

    # Standardize data types
    try:
        # Convert date column to datetime
        if not pd.api.types.is_datetime64_any_dtype(df_std["date"]):
            df_std["date"] = pd.to_datetime(df_std["date"], errors="coerce")

        # Convert value to numeric
        if not pd.api.types.is_numeric_dtype(df_std["value"]):
            df_std["value"] = pd.to_numeric(df_std["value"], errors="coerce")
    except Exception as e:
        raise ValueError(f"Error standardizing data types: {e}")

    # Add missing optional columns with default values
    optional_defaults = {
        "description": df_std.get("series_id", ""),
        "units": "",
        "table": "",
        "frequency": "",
        "series_type": "Original",
        "source": source,
    }

    for col, default_value in optional_defaults.items():
        if col not in df_std.columns:
            if isinstance(default_value, pd.Series):
                df_std[col] = default_value
            else:
                df_std[col] = default_value

    # Ensure consistent column order
    standard_columns = [
        "date",
        "series_id",
        "value",
        "description",
        "units",
        "table",
        "frequency",
        "series_type",
        "source",
    ]

    # Add any extra columns that aren't in the standard set
    extra_columns = [col for col in df_std.columns if col not in standard_columns]
    all_columns = standard_columns + extra_columns

    # Select only existing columns in the desired order
    available_columns = [col for col in all_columns if col in df_std.columns]
    df_std = df_std[available_columns]

    # Remove rows with null dates or values
    df_std = df_std.dropna(subset=["date", "value"])

    # Sort by date and series_id for consistent output
    df_std = df_std.sort_values(["date", "series_id"]).reset_index(drop=True)

    return df_std


def validate_standard_format(df: pd.DataFrame) -> bool:
    """
    Validate that a DataFrame conforms to the standard RBA format.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate

    Returns
    -------
    bool
        True if DataFrame is in standard format

    Raises
    ------
    ValueError
        If DataFrame doesn't conform to standard format
    """
    # Check for empty DataFrame first
    if df.empty:
        raise ValueError("DataFrame is empty")

    # Check required columns
    required_columns = ["date", "series_id", "value"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Check data types
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        raise ValueError("'date' column must be datetime type")

    if not pd.api.types.is_numeric_dtype(df["value"]):
        raise ValueError("'value' column must be numeric type")

    if not pd.api.types.is_object_dtype(df["series_id"]):
        raise ValueError("'series_id' column must be string/object type")

    return True


def ensure_date_consistency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure date formats are consistent across all data sources.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with date column

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized dates
    """
    df = df.copy()

    if "date" in df.columns:
        # Convert to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df["date"]):
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # Normalize to start of day (remove time component for daily data)
        df["date"] = df["date"].dt.normalize()

        # Sort by date
        df = df.sort_values("date")

    return df


def merge_metadata_consistently(df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
    """
    Merge metadata into DataFrame in a consistent way.

    Parameters
    ----------
    df : pd.DataFrame
        Base DataFrame
    metadata : dict
        Metadata dictionary

    Returns
    -------
    pd.DataFrame
        DataFrame with merged metadata
    """
    df = df.copy()

    # Standard metadata fields
    metadata_mapping = {
        "table_name": "table",
        "frequency": "frequency",
        "units": "units",
        "series_type": "series_type",
        "source": "source",
    }

    for meta_key, df_column in metadata_mapping.items():
        if meta_key in metadata and df_column in df.columns:
            # Only update if the column is empty or has default values
            if df[df_column].fillna("").str.strip().eq("").all():
                df[df_column] = metadata[meta_key]

    return df
