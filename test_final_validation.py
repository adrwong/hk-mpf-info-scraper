#!/usr/bin/env python3
"""
Final validation test matching exactly the issue requirements
"""
import pandas as pd
import numpy as np
import json
from mpf_scrape_json import format_dataframe_for_json

def test_exact_issue_requirements():
    """
    Test that exactly matches the before/after example in the issue
    """
    print("=" * 70)
    print("FINAL VALIDATION - Matching Issue Requirements")
    print("=" * 70)
    
    # Create data matching the "Now" state in the issue
    test_data = {
        'Scheme': ['AIA MPF - Prime Value Choice'],
        'Constituent Fund': ['Age 65 Plus Fund'],
        'MPF Trustee': ['AIAT'],
        'Fund Type': ['Mixed Assets Fund - Default Investment Strategy - Age 65 Plus Fund'],
        'Launch Date': ['01-04-2017'],
        "Fund size (HKD' m)": [2533.59],  # Numeric - issue shows 2533.59 in "Now"
        'Risk Class': ['4'],
        'Latest FER (%)': ['0.78633'],
        'Details': [np.nan],  # NaN in the "Now" state
        'Calendar Year Return (%)\n-  2024': [3.09],  # Should be in output
        'Calendar Year Return (%)\n-  2023': [7.10],  
        'Calendar Year Return (%)\n-  2022': [-14.78],
        'Calendar Year Return (%)\n-  2021': [0.89],
        'Calendar Year Return (%)\n-  2020': [8.12],
        '_language': ['english']
    }
    
    print("\n📋 BEFORE FORMATTING (Current/Now state):")
    print("-" * 70)
    df = pd.DataFrame(test_data)
    record_before = df.to_dict('records')[0]
    print(json.dumps(record_before, indent=2, ensure_ascii=False, default=str))
    
    # Apply formatting
    df_formatted = format_dataframe_for_json(df)
    
    # Convert to dict and remove NaN values
    records = df_formatted.to_dict('records')
    cleaned_records = []
    for record in records:
        cleaned_record = {k: v for k, v in record.items() if pd.notna(v)}
        cleaned_records.append(cleaned_record)
    
    actual_output = cleaned_records[0]
    
    print("\n✅ AFTER FORMATTING (Expected/Updated state):")
    print("-" * 70)
    print(json.dumps(actual_output, indent=2, ensure_ascii=False))
    
    # Define expected output from the issue
    expected_output = {
        "Scheme": "AIA MPF - Prime Value Choice",
        "Constituent Fund": "Age 65 Plus Fund",
        "MPF Trustee": "AIAT",
        "Fund Type": "Mixed Assets Fund - Default Investment Strategy - Age 65 Plus Fund",
        "Launch Date": "01-04-2017",
        "Fund size (HKD' m)": "2,533.59",  # Note: Using original value from issue
        "Risk Class": "4",
        "Latest FER (%)": "0.78633",
        "Calendar Year Return (%)\n-  2024": "3.09",
        "Calendar Year Return (%)\n-  2023": "7.1",  # Note: pandas may format differently
        "Calendar Year Return (%)\n-  2022": "-14.78",
        "Calendar Year Return (%)\n-  2021": "0.89",
        "Calendar Year Return (%)\n-  2020": "8.12",
        "_language": "english"
    }
    
    print("\n🔍 VALIDATION:")
    print("-" * 70)
    
    # 1. Check Fund size is string with comma
    fund_size = actual_output["Fund size (HKD' m)"]
    assert isinstance(fund_size, str), \
        "Fund size must be a string"
    assert "," in fund_size, \
        "Fund size must contain comma separator"
    assert fund_size == "2,533.59", \
        f"Fund size should be '2,533.59', got '{fund_size}'"
    print("✓ Fund size formatted correctly as string with comma: '2,533.59'")
    
    # 2. Check Details field is removed (was NaN)
    assert 'Details' not in actual_output, \
        "Details field should be removed when NaN"
    print("✓ Details field (NaN) successfully removed from output")
    
    # 3. Check Calendar Year Return fields
    calendar_years = ['2024', '2023', '2022', '2021', '2020']
    for year in calendar_years:
        key = f'Calendar Year Return (%)\n-  {year}'
        assert key in actual_output, f"Missing Calendar Year Return for {year}"
        assert isinstance(actual_output[key], str), \
            f"Calendar Year Return {year} must be string, got {type(actual_output[key])}"
    print("✓ All Calendar Year Return fields present and formatted as strings")
    
    # 4. Verify specific values
    assert actual_output['Calendar Year Return (%)\n-  2024'] == '3.09'
    assert actual_output['Calendar Year Return (%)\n-  2023'] == '7.1'
    assert actual_output['Calendar Year Return (%)\n-  2022'] == '-14.78'
    assert actual_output['Calendar Year Return (%)\n-  2021'] == '0.89'
    assert actual_output['Calendar Year Return (%)\n-  2020'] == '8.12'
    print("✓ All Calendar Year Return values match expected format")
    
    # 5. Check all required fields are present
    required_fields = [
        'Scheme', 'Constituent Fund', 'MPF Trustee', 'Fund Type', 
        'Launch Date', "Fund size (HKD' m)", 'Risk Class', 'Latest FER (%)', 
        '_language'
    ]
    for field in required_fields:
        assert field in actual_output, f"Missing required field: {field}"
    print("✓ All required fields present in output")
    
    print("\n" + "=" * 70)
    print("✅ ALL VALIDATIONS PASSED!")
    print("=" * 70)
    print("\n📊 Summary of Changes:")
    print("  • Fund size: numeric → string with comma separator")
    print("  • Details: NaN removed from output")
    print("  • Calendar Year Returns: all formatted as strings")
    print("\nThe output format now exactly matches the requirements in the issue.")
    
if __name__ == "__main__":
    test_exact_issue_requirements()
