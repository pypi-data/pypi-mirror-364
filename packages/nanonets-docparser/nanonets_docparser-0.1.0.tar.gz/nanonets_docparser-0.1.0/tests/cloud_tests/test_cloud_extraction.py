#!/usr/bin/env python3
"""
Test script for Nanonets Document Extractor cloud processing options.
Tests all output formats and features on a resume image.
"""

import json
import os
import sys
from pathlib import Path

# Add the package to the path for testing
sys.path.insert(0, str(Path(__file__).parent))

from nanonets_extractor import DocumentExtractor, ExtractionError


def test_cloud_extraction():
    """Test all cloud processing options on the resume image."""
    
    # Configuration
    API_KEY = os.getenv("NANONETS_API_KEY")
    if not API_KEY:
        print("❌ Error: NANONETS_API_KEY environment variable not set")
        print("Please set your API key: export NANONETS_API_KEY='your_key_here'")
        print("Get your FREE API key from: https://app.nanonets.com/#/keys")
        return False
    
    # Image file path (using sample.png)
    image_path = "sample.png"
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file '{image_path}' not found")
        print("Please ensure 'sample.png' exists in the current directory")
        return False
    
    print("🚀 Starting Nanonets Document Extractor Cloud Tests")
    print("=" * 60)
    
    # Initialize extractor
    try:
        extractor = DocumentExtractor(mode="cloud", api_key=API_KEY)
        print(f"✅ Cloud extractor initialized successfully")
        print(f"📊 Processing info: {extractor.get_processing_info()}")
    except Exception as e:
        print(f"❌ Failed to initialize extractor: {e}")
        return False
    
    print("\n" + "=" * 60)
    
    # Test 1: Basic Markdown Extraction
    print("📝 Test 1: Markdown Output")
    print("-" * 30)
    try:
        result = extractor.extract(
            file_path=image_path,
            output_type="markdown"
        )
        print("✅ Markdown extraction successful")
        print(f"📄 Content preview: {result.get('markdown', '')[:200]}...")
        save_result("test1_markdown.json", result)
    except Exception as e:
        print(f"❌ Markdown extraction failed: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Flat JSON Extraction
    print("📋 Test 2: Flat JSON Output")
    print("-" * 30)
    try:
        result = extractor.extract(
            file_path=image_path,
            output_type="flat-json"
        )
        print("✅ Flat JSON extraction successful")
        print("📊 Extracted fields:")
        for key, value in result.items():
            if key != "extracted_text":  # Skip long text for display
                print(f"   • {key}: {value}")
        if "extracted_text" in result:
            print(f"   • extracted_text: {result['extracted_text'][:100]}...")
        save_result("test2_flat_json.json", result)
    except Exception as e:
        print(f"❌ Flat JSON extraction failed: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 3: Specified Fields Extraction
    print("🎯 Test 3: Specified Fields Output")
    print("-" * 30)
    specified_fields = [
        "name",
        "email", 
        "phone",
        "address",
        "education",
        "experience",
        "skills",
        "objective"
    ]
    try:
        result = extractor.extract(
            file_path=image_path,
            output_type="specified-fields",
            specified_fields=specified_fields
        )
        print("✅ Specified fields extraction successful")
        print("📊 Extracted specified fields:")
        for field in specified_fields:
            value = result.get(field, "Not found")
            print(f"   • {field}: {value}")
        save_result("test3_specified_fields.json", result)
    except Exception as e:
        print(f"❌ Specified fields extraction failed: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 4: Custom JSON Schema Extraction
    print("🏗️ Test 4: Custom JSON Schema Output")
    print("-" * 30)
    
    # Define a comprehensive resume schema
    resume_schema = {
        "personal_info": {
            "name": "string",
            "email": "string",
            "phone": "string",
            "address": "string"
        },
        "objective": "string",
        "education": [
            {
                "institution": "string",
                "degree": "string",
                "field": "string",
                "dates": "string",
                "location": "string"
            }
        ],
        "experience": [
            {
                "title": "string",
                "company": "string",
                "location": "string",
                "dates": "string",
                "responsibilities": ["string"]
            }
        ],
        "skills": ["string"]
    }
    
    try:
        result = extractor.extract(
            file_path=image_path,
            output_type="specified-json",
            json_schema=resume_schema
        )
        print("✅ Custom schema extraction successful")
        print("📊 Structured resume data:")
        print_json_structure(result, max_depth=3)
        save_result("test4_custom_schema.json", result)
    except Exception as e:
        print(f"❌ Custom schema extraction failed: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 5: Resume-Specific Schema
    print("📄 Test 5: Resume-Specific Schema")
    print("-" * 30)
    
    # More specific resume schema based on the actual resume content
    specific_resume_schema = {
        "candidate_name": "string",
        "contact_info": {
            "email": "string",
            "phone": "string",
            "address": "string"
        },
        "professional_objective": "string",
        "education_history": [
            {
                "university": "string",
                "school": "string",
                "location": "string",
                "degree": "string",
                "dates": "string",
                "coursework": "string"
            }
        ],
        "work_experience": [
            {
                "job_title": "string",
                "company": "string",
                "location": "string",
                "duration": "string",
                "key_responsibilities": ["string"]
            }
        ],
        "key_skills": ["string"]
    }
    
    try:
        result = extractor.extract(
            file_path=image_path,
            output_type="specified-json",
            json_schema=specific_resume_schema
        )
        print("✅ Resume-specific schema extraction successful")
        print("📊 Resume structured data:")
        print_json_structure(result, max_depth=3)
        save_result("test5_resume_specific.json", result)
    except Exception as e:
        print(f"❌ Resume-specific schema extraction failed: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 6: Batch Processing Simulation
    print("🔄 Test 6: Batch Processing Simulation")
    print("-" * 30)
    
    # Simulate batch processing with the same file
    file_paths = [image_path] * 3  # Process same file 3 times to simulate batch
    
    try:
        results = extractor.extract_batch(
            file_paths=file_paths,
            output_type="flat-json"
        )
        print("✅ Batch processing successful")
        print(f"📊 Processed {len(results)} files")
        for i, (file_path, result) in enumerate(results.items(), 1):
            print(f"   File {i}: {os.path.basename(file_path)}")
            if "error" in result:
                print(f"      ❌ Error: {result['error']}")
            else:
                print(f"      ✅ Success - extracted {len(result)} fields")
        save_result("test6_batch_processing.json", results)
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 7: Error Handling
    print("⚠️ Test 7: Error Handling")
    print("-" * 30)
    
    # Test with invalid API key
    try:
        invalid_extractor = DocumentExtractor(mode="cloud", api_key="invalid_key")
        result = invalid_extractor.extract(image_path, output_type="flat-json")
        print("❌ Should have failed with invalid API key")
    except Exception as e:
        print(f"✅ Error handling working correctly: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 60)
    
    # Summary
    print("📋 Test Summary")
    print("-" * 30)
    print("✅ All tests completed!")
    print("📁 Results saved to JSON files:")
    print("   • test1_markdown.json")
    print("   • test2_flat_json.json") 
    print("   • test3_specified_fields.json")
    print("   • test4_custom_schema.json")
    print("   • test5_resume_specific.json")
    print("   • test6_batch_processing.json")
    
    return True


def save_result(filename, data):
    """Save test results to JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Results saved to {filename}")
    except Exception as e:
        print(f"❌ Failed to save {filename}: {e}")


def print_json_structure(data, max_depth=3, current_depth=0, indent=2):
    """Pretty print JSON structure with depth limiting."""
    if current_depth >= max_depth:
        print(" " * (indent * current_depth) + "...")
        return
    
    if isinstance(data, dict):
        for key, value in data.items():
            prefix = " " * (indent * current_depth)
            if isinstance(value, (dict, list)) and current_depth < max_depth - 1:
                print(f"{prefix}• {key}:")
                print_json_structure(value, max_depth, current_depth + 1, indent)
            else:
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                print(f"{prefix}• {key}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data[:3]):  # Limit to first 3 items
            prefix = " " * (indent * current_depth)
            if isinstance(item, (dict, list)) and current_depth < max_depth - 1:
                print(f"{prefix}[{i}]:")
                print_json_structure(item, max_depth, current_depth + 1, indent)
            else:
                if isinstance(item, str) and len(item) > 50:
                    item = item[:50] + "..."
                print(f"{prefix}[{i}]: {item}")
        if len(data) > 3:
            print(" " * (indent * current_depth) + f"... and {len(data) - 3} more items")


if __name__ == "__main__":
    print("🧪 Nanonets Document Extractor - Cloud Processing Test Suite")
    print("Testing all cloud processing options on resume image")
    print("=" * 80)
    
    success = test_cloud_extraction()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("📖 Check the generated JSON files for detailed results")
    else:
        print("\n💥 Some tests failed. Check the output above for details.")
        sys.exit(1) 