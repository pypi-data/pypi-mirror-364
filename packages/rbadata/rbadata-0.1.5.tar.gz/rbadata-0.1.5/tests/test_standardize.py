"""
Tests for data standardization functionality.
"""

import pytest
import pandas as pd
from datetime import datetime

from rbadata.standardize import (
    standardize_rba_dataframe,
    validate_standard_format,
    ensure_date_consistency,
    merge_metadata_consistently
)


class TestStandardizeRBADataFrame:
    """Test DataFrame standardization."""
    
    def test_basic_standardization(self):
        """Test basic DataFrame standardization."""
        # Create DataFrame with non-standard column names
        df = pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02'],
            'series': ['TEST1', 'TEST1'],
            'Value': [1.5, 1.6],
            'Description': ['Test Series', 'Test Series'],
            'Units': ['Percent', 'Percent']
        })
        
        result = standardize_rba_dataframe(df, source="test")
        
        # Check column names are standardized
        expected_columns = ['date', 'series_id', 'value', 'description', 'units', 'table', 'frequency', 'series_type', 'source']
        assert all(col in result.columns for col in expected_columns)
        
        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(result['date'])
        assert pd.api.types.is_numeric_dtype(result['value'])
        
        # Check values preserved
        assert len(result) == 2
        assert result['series_id'].iloc[0] == 'TEST1'
        assert result['value'].iloc[0] == 1.5
        
    def test_missing_required_columns(self):
        """Test error when required columns are missing."""
        df = pd.DataFrame({
            'Date': ['2023-01-01'],
            'series': ['TEST1']
            # Missing 'value' column
        })
        
        with pytest.raises(ValueError) as exc_info:
            standardize_rba_dataframe(df)
            
        assert "Missing required columns" in str(exc_info.value)
        assert "value" in str(exc_info.value)
        
    def test_column_mapping(self):
        """Test various column name mappings."""
        df = pd.DataFrame({
            'DATE': ['2023-01-01'],
            'series_code': ['TEST1'],
            'observation': [1.5],
            'series_name': ['Test Series'],
            'unit': ['Percent'],
            'table_no': ['F1'],
            'freq': ['Daily'],
            'type': ['Original']
        })
        
        result = standardize_rba_dataframe(df, source="test")
        
        # Check all mappings worked
        assert 'date' in result.columns
        assert 'series_id' in result.columns
        assert 'value' in result.columns
        assert 'description' in result.columns
        assert 'units' in result.columns
        assert 'table' in result.columns
        assert 'frequency' in result.columns
        assert 'series_type' in result.columns
        
        # Check values preserved
        assert result['series_id'].iloc[0] == 'TEST1'
        assert result['table'].iloc[0] == 'F1'
        assert result['frequency'].iloc[0] == 'Daily'
        
    def test_default_values(self):
        """Test default values for missing optional columns."""
        df = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01')],
            'series_id': ['TEST1'],
            'value': [1.5]
        })
        
        result = standardize_rba_dataframe(df, source="test")
        
        # Check default values
        assert result['description'].iloc[0] == 'TEST1'  # Defaults to series_id
        assert result['units'].iloc[0] == ''
        assert result['table'].iloc[0] == ''
        assert result['frequency'].iloc[0] == ''
        assert result['series_type'].iloc[0] == 'Original'
        assert result['source'].iloc[0] == 'test'
        
    def test_data_type_conversion(self):
        """Test data type conversions."""
        df = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],  # String dates
            'series_id': ['TEST1', 'TEST1'],
            'value': ['1.5', '1.6']  # String values
        })
        
        result = standardize_rba_dataframe(df)
        
        # Check conversions
        assert pd.api.types.is_datetime64_any_dtype(result['date'])
        assert pd.api.types.is_numeric_dtype(result['value'])
        assert result['value'].iloc[0] == 1.5
        assert result['value'].iloc[1] == 1.6
        
    def test_null_value_removal(self):
        """Test removal of rows with null dates or values."""
        df = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01'), None, pd.Timestamp('2023-01-03')],
            'series_id': ['TEST1', 'TEST1', 'TEST1'],
            'value': [1.5, 1.6, None]
        })
        
        result = standardize_rba_dataframe(df)
        
        # Should only have one valid row
        assert len(result) == 1
        assert result['date'].iloc[0] == pd.Timestamp('2023-01-01')
        assert result['value'].iloc[0] == 1.5
        
    def test_sorting(self):
        """Test sorting by date and series_id."""
        df = pd.DataFrame({
            'date': ['2023-01-02', '2023-01-01', '2023-01-01'],
            'series_id': ['TEST1', 'TEST2', 'TEST1'],
            'value': [1.6, 2.1, 1.5]
        })
        
        result = standardize_rba_dataframe(df)
        
        # Check sorting
        expected_order = [
            (pd.Timestamp('2023-01-01'), 'TEST1'),
            (pd.Timestamp('2023-01-01'), 'TEST2'),
            (pd.Timestamp('2023-01-02'), 'TEST1')
        ]
        
        actual_order = list(zip(result['date'], result['series_id']))
        assert actual_order == expected_order
        
    def test_extra_columns_preserved(self):
        """Test that extra columns are preserved."""
        df = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01')],
            'series_id': ['TEST1'],
            'value': [1.5],
            'custom_column': ['custom_value'],
            'another_extra': [42]
        })
        
        result = standardize_rba_dataframe(df)
        
        # Check extra columns preserved
        assert 'custom_column' in result.columns
        assert 'another_extra' in result.columns
        assert result['custom_column'].iloc[0] == 'custom_value'
        assert result['another_extra'].iloc[0] == 42


class TestValidateStandardFormat:
    """Test format validation."""
    
    def test_valid_format(self):
        """Test validation of valid format."""
        df = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01')],
            'series_id': ['TEST1'],
            'value': [1.5],
            'description': ['Test'],
            'units': ['Percent']
        })
        
        # Should not raise
        assert validate_standard_format(df) is True
        
    def test_missing_required_columns(self):
        """Test validation fails for missing columns."""
        df = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01')],
            'series_id': ['TEST1']
            # Missing 'value'
        })
        
        with pytest.raises(ValueError) as exc_info:
            validate_standard_format(df)
            
        assert "Missing required columns" in str(exc_info.value)
        
    def test_wrong_data_types(self):
        """Test validation fails for wrong data types."""
        # Wrong date type
        df1 = pd.DataFrame({
            'date': ['2023-01-01'],  # String instead of datetime
            'series_id': ['TEST1'],
            'value': [1.5]
        })
        
        with pytest.raises(ValueError) as exc_info:
            validate_standard_format(df1)
        assert "'date' column must be datetime type" in str(exc_info.value)
        
        # Wrong value type
        df2 = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01')],
            'series_id': ['TEST1'],
            'value': ['not_numeric']
        })
        
        with pytest.raises(ValueError) as exc_info:
            validate_standard_format(df2)
        assert "'value' column must be numeric type" in str(exc_info.value)
        
    def test_empty_dataframe(self):
        """Test validation fails for empty DataFrame."""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError) as exc_info:
            validate_standard_format(df)
        assert "DataFrame is empty" in str(exc_info.value)


class TestEnsureDateConsistency:
    """Test date consistency functions."""
    
    def test_date_normalization(self):
        """Test date normalization."""
        df = pd.DataFrame({
            'date': [
                pd.Timestamp('2023-01-01 15:30:00'),
                pd.Timestamp('2023-01-02 09:15:00')
            ],
            'value': [1.5, 1.6]
        })
        
        result = ensure_date_consistency(df)
        
        # Check dates are normalized to start of day
        assert result['date'].iloc[0] == pd.Timestamp('2023-01-01')
        assert result['date'].iloc[1] == pd.Timestamp('2023-01-02')
        
    def test_date_conversion(self):
        """Test conversion of string dates."""
        df = pd.DataFrame({
            'date': ['2023-01-02', '2023-01-01'],
            'value': [1.6, 1.5]
        })
        
        result = ensure_date_consistency(df)
        
        # Check conversion and sorting
        assert pd.api.types.is_datetime64_any_dtype(result['date'])
        assert result['date'].iloc[0] == pd.Timestamp('2023-01-01')
        assert result['date'].iloc[1] == pd.Timestamp('2023-01-02')
        
    def test_no_date_column(self):
        """Test handling when no date column exists."""
        df = pd.DataFrame({
            'series_id': ['TEST1'],
            'value': [1.5]
        })
        
        result = ensure_date_consistency(df)
        
        # Should return unchanged
        pd.testing.assert_frame_equal(result, df)


class TestMergeMetadataConsistently:
    """Test metadata merging."""
    
    def test_metadata_merge(self):
        """Test merging metadata into DataFrame."""
        df = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01')],
            'series_id': ['TEST1'],
            'value': [1.5],
            'table': [''],  # Empty, should be filled
            'frequency': [''],  # Empty, should be filled
            'units': ['Existing Units'],  # Not empty, should not be overwritten
            'series_type': [''],
            'source': ['']
        })
        
        metadata = {
            'table_name': 'F1',
            'frequency': 'Daily',
            'units': 'Percent',  # Should not overwrite existing
            'series_type': 'Original',
            'source': 'RBA'
        }
        
        result = merge_metadata_consistently(df, metadata)
        
        # Check metadata merged correctly
        assert result['table'].iloc[0] == 'F1'
        assert result['frequency'].iloc[0] == 'Daily'
        assert result['units'].iloc[0] == 'Existing Units'  # Not overwritten
        assert result['series_type'].iloc[0] == 'Original'
        assert result['source'].iloc[0] == 'RBA'
        
    def test_missing_metadata_fields(self):
        """Test handling of missing metadata fields."""
        df = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01')],
            'series_id': ['TEST1'],
            'value': [1.5],
            'table': ['']
        })
        
        metadata = {
            'frequency': 'Daily'
            # Missing other fields
        }
        
        result = merge_metadata_consistently(df, metadata)
        
        # Should not error, just not update missing fields
        assert result['table'].iloc[0] == ''  # Unchanged
        
    def test_missing_dataframe_columns(self):
        """Test handling when DataFrame is missing columns."""
        df = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01')],
            'series_id': ['TEST1'],
            'value': [1.5]
            # Missing metadata columns
        })
        
        metadata = {
            'table_name': 'F1',
            'frequency': 'Daily'
        }
        
        result = merge_metadata_consistently(df, metadata)
        
        # Should not error, just skip missing columns
        pd.testing.assert_frame_equal(result, df)


class TestStandardizationIntegration:
    """Integration tests for standardization."""
    
    def test_csv_to_excel_consistency(self):
        """Test that CSV and Excel data produce consistent format."""
        # Simulate CSV-style data
        csv_df = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01')],
            'series_id': ['TEST1'],
            'value': [1.5],
            'table': ['F1'],
            'description': ['Test Series'],
            'units': ['Percent'],
            'series_type': ['Original']
        })
        
        # Simulate Excel-style data
        excel_df = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01')],
            'series': ['TEST1'],  # Different column name
            'value': [1.5],
            'table_no': ['F1'],  # Different column name
            'description': ['Test Series'],
            'units': ['Percent'],
            'series_type': ['Original']
        })
        
        # Standardize both
        csv_std = standardize_rba_dataframe(csv_df, source="csv")
        excel_std = standardize_rba_dataframe(excel_df, source="excel")
        
        # Should have same columns
        assert set(csv_std.columns) == set(excel_std.columns)
        
        # Core data should be the same
        assert csv_std['series_id'].iloc[0] == excel_std['series_id'].iloc[0]
        assert csv_std['value'].iloc[0] == excel_std['value'].iloc[0]
        assert csv_std['table'].iloc[0] == excel_std['table'].iloc[0]