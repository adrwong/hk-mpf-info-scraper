#!/usr/bin/env python3
"""
Additional edge case tests for data formatting
"""
import pandas as pd
import numpy as np
import json
from mpf_scrape_json import format_dataframe_for_json

def test_edge_cases():
    """Test edge cases in formatting"""
    
    print("Testing edge cases...")
    print("=" * 60)
    
    # Test 1: Fund size already as string
    test_data = {
        "Fund size (HKD' m)": ['123.45', 456.78, np.nan, '789.01'],
        'Calendar Year Return (%)\n-  2024': ['5.0', 6.0, np.nan, -3.14]
    }
    df = pd.DataFrame(test_data)
    df_formatted = format_dataframe_for_json(df)
    
    print("\nTest 1: Mixed string and numeric values")
    print(f"Input types: {df['Fund size (HKD\' m)'].apply(type).tolist()}")
    print(f"Output types: {df_formatted['Fund size (HKD\' m)'].apply(lambda x: type(x) if pd.notna(x) else 'NaN').tolist()}")
    print(f"Output values: {df_formatted['Fund size (HKD\' m)'].tolist()}")
    
    # Verify that string values are preserved and numeric values are formatted
    assert df_formatted["Fund size (HKD' m)"].iloc[0] == '123.45', "String value should be preserved"
    assert df_formatted["Fund size (HKD' m)"].iloc[1] == '456.78', "Numeric value should be formatted"
    assert pd.isna(df_formatted["Fund size (HKD' m)"].iloc[2]), "NaN should remain NaN"
    print("✓ Fund size edge cases handled correctly")
    
    # Test 2: Calendar Year Return with various formats
    print("\nTest 2: Calendar Year Return formatting")
    print(f"Input: {df['Calendar Year Return (%)\n-  2024'].tolist()}")
    print(f"Output: {df_formatted['Calendar Year Return (%)\n-  2024'].tolist()}")
    assert df_formatted['Calendar Year Return (%)\n-  2024'].iloc[0] == '5.0', "String should remain string"
    assert df_formatted['Calendar Year Return (%)\n-  2024'].iloc[1] == '6.0', "Float should be converted to string"
    print("✓ Calendar Year Return values formatted correctly")
    
    # Test 3: Record conversion with NaN removal
    print("\nTest 3: NaN removal from records")
    records = df_formatted.to_dict('records')
    cleaned_records = []
    for record in records:
        cleaned_record = {k: v for k, v in record.items() if pd.notna(v)}
        cleaned_records.append(cleaned_record)
    
    print(f"Original record count: {len(records)}")
    print(f"Cleaned record count: {len(cleaned_records)}")
    print(f"Keys in record 2 (has NaN): {list(cleaned_records[2].keys())}")
    
    # Record 2 should not have Fund size or Calendar Year Return keys (both were NaN)
    assert "Fund size (HKD' m)" not in cleaned_records[2], "NaN Fund size should be removed"
    assert "Calendar Year Return (%)\n-  2024" not in cleaned_records[2], "NaN Calendar Year Return should be removed"
    print("✓ NaN values correctly removed from records")
    
    # Test 4: Large numbers with comma formatting
    print("\nTest 4: Large number formatting")
    large_test = pd.DataFrame({
        "Fund size (HKD' m)": [1234567.89, 0.12, 999999999.99]
    })
    large_formatted = format_dataframe_for_json(large_test)
    
    print(f"Input: {large_test['Fund size (HKD\' m)'].tolist()}")
    print(f"Output: {large_formatted['Fund size (HKD\' m)'].tolist()}")
    
    assert large_formatted["Fund size (HKD' m)"].iloc[0] == "1,234,567.89", "Large number should have commas"
    assert large_formatted["Fund size (HKD' m)"].iloc[1] == "0.12", "Small number should format correctly"
    assert large_formatted["Fund size (HKD' m)"].iloc[2] == "999,999,999.99", "Very large number should have commas"
    print("✓ Large numbers formatted correctly with commas")
    
    print("\n" + "=" * 60)
    print("✓ All edge case tests passed!")

if __name__ == "__main__":
    test_edge_cases()
