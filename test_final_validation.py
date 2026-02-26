#!/usr/bin/env python3
"""
Final validation test matching exactly the issue requirements
"""
import pandas as pd
import numpy as np
import json
from unittest.mock import patch
from mpf_scrape_json import format_dataframe_for_json, combine_all_languages, build_fund_type_maps, LANGUAGE_LABELS

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
    
def test_indexed_table_data_structure():
    """
    Test that combine_all_languages produces table_data keyed by row index
    with language as sub-keys, matching the format required by the issue.
    """
    print("\n" + "=" * 70)
    print("TEST - Indexed table_data structure")
    print("=" * 70)

    # Build two minimal DataFrames (one per language) to avoid real HTTP calls
    def make_df(scheme_name, lang_label):
        df = pd.DataFrame({
            'Scheme': [scheme_name, scheme_name + ' B'],
            'Constituent Fund': ['Fund A', 'Fund B'],
            'MPF Trustee': ['Trustee X', 'Trustee X'],
            'Fund Type': ['Equity', 'Bond'],
            'Launch Date': ['01-01-2020', '01-01-2021'],
            "Fund size (HKD' m)": ['100.00', '200.00'],
            'Risk Class': ['5', '3'],
            'Latest FER (%)': ['1.00', '0.50'],
            '_language': [lang_label, lang_label],
        })
        return df, None  # (dataframe, date_str)

    side_effects = [
        make_df('Scheme EN', 'english'),
        make_df('Scheme ZH', 'traditional_chinese'),
        make_df('Scheme CN', 'simplified_chinese'),
    ]

    with patch('mpf_scrape_json.scrape_language', side_effect=side_effects):
        result = combine_all_languages()

    table_data = result['table_data']

    # table_data must be a dict, not a list
    assert isinstance(table_data, dict), \
        f"table_data should be a dict, got {type(table_data)}"
    print("✓ table_data is a dict")

    # Keys must be string row indices
    assert set(table_data.keys()) == {'0', '1'}, \
        f"Expected keys {{'0','1'}}, got {set(table_data.keys())}"
    print("✓ Keys are string row indices '0' and '1'")

    # Each entry must have all three language sub-keys
    for row_key in ['0', '1']:
        entry = table_data[row_key]
        assert set(entry.keys()) == {'english', 'traditional_chinese', 'simplified_chinese'}, \
            f"Entry {row_key} missing language keys: {set(entry.keys())}"
    print("✓ Each entry contains all three language sub-keys")

    # _language field must NOT appear in the fund records
    for row_key, entry in table_data.items():
        for lang, record in entry.items():
            assert '_language' not in record, \
                f"_language should be removed from record at index {row_key}/{lang}"
    print("✓ _language field removed from all fund records")

    # Spot-check a value
    assert table_data['0']['english']['Scheme'] == 'Scheme EN'
    assert table_data['0']['traditional_chinese']['Scheme'] == 'Scheme ZH'
    assert table_data['0']['simplified_chinese']['Scheme'] == 'Scheme CN'
    print("✓ Fund data correctly stored under each language sub-key")

    # columns key must not be present in the output
    assert 'columns' not in result, "'columns' key should not be present in output"
    print("✓ Obsolete 'columns' key not present in output")

    print("\n✅ ALL INDEXED STRUCTURE TESTS PASSED!")
    print("=" * 70)


def test_build_fund_type_maps():
    """
    Test that build_fund_type_maps correctly derives fund_type_map and
    fund_category_map from table_data using the example given in the issue.
    """
    print("\n" + "=" * 70)
    print("TEST - build_fund_type_maps")
    print("=" * 70)

    table_data = {
        "54": {
            "english": {
                "Scheme": "BCOM Joyful Retirement MPF Scheme",
                "Constituent Fund": "BCOM China Dynamic Equity (CF) Fund",
                "MPF Trustee": "BCOM",
                "Fund Type": "Equity Fund - China Equity Fund",
            },
            "traditional_chinese": {
                "Scheme": "交通銀行愉盈退休強積金計劃",
                "Constituent Fund": "交通銀行中國動力股票成分基金",
                "MPF Trustee": "交通",
                "Fund Type": "股票基金 - 中國股票基金",
            },
            "simplified_chinese": {
                "Scheme": "交通银行愉盈退休强积金计划",
                "Constituent Fund": "交通银行中国动力股票成分基金",
                "MPF Trustee": "交通",
                "Fund Type": "股票基金 - 中国股票基金",
            },
        },
        "55": {
            "english": {
                "Fund Type": "Mixed Assets Fund - Balanced Fund",
            },
            "traditional_chinese": {
                "Fund Type": "混合資產基金 - 平衡基金",
            },
            "simplified_chinese": {
                "Fund Type": "混合资产基金 - 平衡基金",
            },
        },
    }

    fund_type_map, fund_category_map = build_fund_type_maps(table_data)

    # fund_type_map checks
    assert "Equity Fund" in fund_type_map, "Expected 'Equity Fund' in fund_type_map"
    assert fund_type_map["Equity Fund"]["traditional_chinese"] == "股票基金"
    assert fund_type_map["Equity Fund"]["simplified_chinese"] == "股票基金"
    print("✓ 'Equity Fund' mapped correctly")

    assert "Mixed Assets Fund" in fund_type_map
    assert fund_type_map["Mixed Assets Fund"]["traditional_chinese"] == "混合資產基金"
    assert fund_type_map["Mixed Assets Fund"]["simplified_chinese"] == "混合资产基金"
    print("✓ 'Mixed Assets Fund' mapped correctly")

    # fund_category_map checks
    assert "China Equity Fund" in fund_category_map
    assert fund_category_map["China Equity Fund"]["traditional_chinese"] == "中國股票基金"
    assert fund_category_map["China Equity Fund"]["simplified_chinese"] == "中国股票基金"
    print("✓ 'China Equity Fund' category mapped correctly")

    assert "Balanced Fund" in fund_category_map
    assert fund_category_map["Balanced Fund"]["traditional_chinese"] == "平衡基金"
    assert fund_category_map["Balanced Fund"]["simplified_chinese"] == "平衡基金"
    print("✓ 'Balanced Fund' category mapped correctly")

    # Test em-dash separator in Chinese fund types
    table_data_emdash = {
        "100": {
            "english": {
                "Fund Type": "Money Market Fund - MPF Conservative Fund",
            },
            "traditional_chinese": {
                "Fund Type": "貨幣市場基金 — 強積金保守基金",
            },
            "simplified_chinese": {
                "Fund Type": "货币市场基金 — 强积金保守基金",
            },
        },
        "101": {
            "english": {
                "Fund Type": "Money Market Fund - Other than MPF Conservative Fund",
            },
            "traditional_chinese": {
                "Fund Type": "貨幣市場基金 — 不包括強積金保守基金",
            },
            "simplified_chinese": {
                "Fund Type": "货币市场基金 — 不包括强积金保守基金",
            },
        },
    }

    ft_map, fc_map = build_fund_type_maps(table_data_emdash)

    assert "Money Market Fund" in ft_map, "Expected 'Money Market Fund' in fund_type_map"
    assert ft_map["Money Market Fund"]["traditional_chinese"] == "貨幣市場基金"
    assert ft_map["Money Market Fund"]["simplified_chinese"] == "货币市场基金"
    print("✓ 'Money Market Fund' mapped correctly with em-dash separator")

    assert "MPF Conservative Fund" in fc_map
    assert fc_map["MPF Conservative Fund"]["traditional_chinese"] == "強積金保守基金"
    assert fc_map["MPF Conservative Fund"]["simplified_chinese"] == "强积金保守基金"
    print("✓ 'MPF Conservative Fund' category mapped correctly with em-dash separator")

    assert "Other than MPF Conservative Fund" in fc_map
    assert fc_map["Other than MPF Conservative Fund"]["traditional_chinese"] == "不包括強積金保守基金"
    assert fc_map["Other than MPF Conservative Fund"]["simplified_chinese"] == "不包括强积金保守基金"
    print("✓ 'Other than MPF Conservative Fund' category mapped correctly with em-dash separator")

    print("\n✅ ALL FUND TYPE MAP TESTS PASSED!")
    print("=" * 70)


def test_combine_all_languages_includes_fund_maps():
    """
    Test that combine_all_languages includes fund_type_map and fund_category_map
    in the returned dict.
    """
    print("\n" + "=" * 70)
    print("TEST - combine_all_languages includes fund maps")
    print("=" * 70)

    def make_df(scheme_name, lang_label, fund_type):
        df = pd.DataFrame({
            'Scheme': [scheme_name],
            'Constituent Fund': ['Fund A'],
            'MPF Trustee': ['Trustee X'],
            'Fund Type': [fund_type],
            'Launch Date': ['01-01-2020'],
            "Fund size (HKD' m)": ['100.00'],
            'Risk Class': ['5'],
            'Latest FER (%)': ['1.00'],
            '_language': [lang_label],
        })
        return df, None

    side_effects = [
        make_df('Scheme EN', 'english', 'Equity Fund - China Equity Fund'),
        make_df('Scheme ZH', 'traditional_chinese', '股票基金 - 中國股票基金'),
        make_df('Scheme CN', 'simplified_chinese', '股票基金 - 中国股票基金'),
    ]

    with patch('mpf_scrape_json.scrape_language', side_effect=side_effects):
        result = combine_all_languages()

    assert 'fund_type_map' in result, "fund_type_map must be present in output"
    assert 'fund_category_map' in result, "fund_category_map must be present in output"
    print("✓ fund_type_map and fund_category_map keys present in output")

    assert result['fund_type_map']['Equity Fund']['traditional_chinese'] == '股票基金'
    assert result['fund_category_map']['China Equity Fund']['simplified_chinese'] == '中国股票基金'
    print("✓ Maps contain correct translations")

    print("\n✅ ALL COMBINE TESTS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    test_exact_issue_requirements()
    test_indexed_table_data_structure()
    test_build_fund_type_maps()
    test_combine_all_languages_includes_fund_maps()
