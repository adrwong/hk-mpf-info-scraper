#!/usr/bin/env python3
"""
Test script to validate data formatting changes for processed_data.json
"""
import pandas as pd
import numpy as np
import json
from mpf_scrape_json import format_dataframe_for_json

def test_formatting():
    """Test that the formatting function works correctly"""
    
    # Create a mock DataFrame with the structure similar to what we'd get from scraping
    test_data = {
        'Scheme': ['AIA MPF - Prime Value Choice'],
        'Constituent Fund': ['Age 65 Plus Fund'],
        'MPF Trustee': ['AIAT'],
        'Fund Type': ['Mixed Assets Fund - Default Investment Strategy - Age 65 Plus Fund'],
        'Launch Date': ['01-04-2017'],
        "Fund size (HKD' m)": [2496.08],  # Numeric value
        'Risk Class': ['4'],
        'Latest FER (%)': ['0.78633'],
        'Calendar Year Return (%)\n-  2024': [3.09],  # Numeric value
        'Calendar Year Return (%)\n-  2023': [7.10],  # Numeric value
        'Calendar Year Return (%)\n-  2022': [-14.78],  # Numeric value
        'Calendar Year Return (%)\n-  2021': [0.89],  # Numeric value
        'Calendar Year Return (%)\n-  2020': [8.12],  # Numeric value
        'Details': [np.nan],  # NaN value
        '_language': ['english']
    }
    
    df = pd.DataFrame(test_data)
    
    print("Before formatting:")
    print(df.dtypes)
    print("\nSample values:")
    print(f"Fund size type: {type(df['Fund size (HKD\' m)'].iloc[0])}")
    print(f"Fund size value: {df['Fund size (HKD\' m)'].iloc[0]}")
    print(f"Calendar Year 2024 type: {type(df['Calendar Year Return (%)\n-  2024'].iloc[0])}")
    print(f"Calendar Year 2024 value: {df['Calendar Year Return (%)\n-  2024'].iloc[0]}")
    
    # Apply formatting
    df_formatted = format_dataframe_for_json(df)
    
    print("\n\nAfter formatting:")
    print(df_formatted.dtypes)
    print("\nSample values:")
    print(f"Fund size type: {type(df_formatted['Fund size (HKD\' m)'].iloc[0])}")
    print(f"Fund size value: {df_formatted['Fund size (HKD\' m)'].iloc[0]}")
    print(f"Calendar Year 2024 type: {type(df_formatted['Calendar Year Return (%)\n-  2024'].iloc[0])}")
    print(f"Calendar Year 2024 value: {df_formatted['Calendar Year Return (%)\n-  2024'].iloc[0]}")
    
    # Convert to dict and remove NaN values
    records = df_formatted.to_dict('records')
    cleaned_records = []
    for record in records:
        cleaned_record = {k: v for k, v in record.items() if pd.notna(v)}
        cleaned_records.append(cleaned_record)
    
    print("\n\nFinal JSON record:")
    print(json.dumps(cleaned_records[0], indent=2, ensure_ascii=False))
    
    # Validate expected output
    expected_record = {
        "Scheme": "AIA MPF - Prime Value Choice",
        "Constituent Fund": "Age 65 Plus Fund",
        "MPF Trustee": "AIAT",
        "Fund Type": "Mixed Assets Fund - Default Investment Strategy - Age 65 Plus Fund",
        "Launch Date": "01-04-2017",
        "Fund size (HKD' m)": "2,496.08",
        "Risk Class": "4",
        "Latest FER (%)": "0.78633",
        "Calendar Year Return (%)\n-  2024": "3.09",
        "Calendar Year Return (%)\n-  2023": "7.1",
        "Calendar Year Return (%)\n-  2022": "-14.78",
        "Calendar Year Return (%)\n-  2021": "0.89",
        "Calendar Year Return (%)\n-  2020": "8.12",
        "_language": "english"
    }
    
    actual_record = cleaned_records[0]
    
    print("\n\nValidation:")
    print("=" * 60)
    
    # Check Fund size formatting
    assert actual_record["Fund size (HKD' m)"] == "2,496.08", \
        f"Fund size not formatted correctly: {actual_record['Fund size (HKD\' m)']}"
    print("✓ Fund size formatted correctly as string with comma: '2,496.08'")
    
    # Check that Details field is removed (was NaN)
    assert 'Details' not in actual_record, "Details field should be removed (was NaN)"
    print("✓ Details field (NaN) removed from output")
    
    # Check Calendar Year Return fields are strings
    for year in ['2024', '2023', '2022', '2021', '2020']:
        key = f'Calendar Year Return (%)\n-  {year}'
        assert key in actual_record, f"Missing Calendar Year Return for {year}"
        assert isinstance(actual_record[key], str), \
            f"Calendar Year Return {year} should be string, got {type(actual_record[key])}"
    print("✓ All Calendar Year Return fields present and formatted as strings")
    
    print("\n✓ All validations passed!")
    print("\nExpected format matches the issue requirements:")
    print("- Fund size is a string with comma separator")
    print("- NaN values (Details) are removed")
    print("- Calendar Year Return fields are present and formatted as strings")

if __name__ == "__main__":
    test_formatting()
