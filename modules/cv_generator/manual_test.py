#!/usr/bin/env python3
"""
Manual Test Script for CV Generator Module
Tests CV generation from personal_info.json to PDF
"""

import os
import sys
import asyncio
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_personal_info_file():
    """Test if personal_info.json exists and is valid."""
    print("📁 Testing Personal Info File")
    print("-" * 40)
    
    personal_info_path = "modules/shared/data/personal_info.json"
    
    if os.path.exists(personal_info_path):
        print(f"✅ Found: {personal_info_path}")
        try:
            import json
            with open(personal_info_path, 'r') as f:
                data = json.load(f)
            
            # Check key sections for CV generation
            required_sections = ['personal_info', 'work_info', 'education']
            optional_sections = ['certifications', 'other']
            
            for section in required_sections:
                if section in data:
                    print(f"✅ Required section '{section}' found")
                else:
                    print(f"❌ Required section '{section}' missing")
                    return False
            
            for section in optional_sections:
                if section in data:
                    print(f"✅ Optional section '{section}' found")
            
            # Check personal info details
            personal = data.get('personal_info', {})
            if personal.get('name'):
                print(f"✅ Name: {personal['name']}")
            if personal.get('job_title'):
                print(f"✅ Job Title: {personal['job_title']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
    else:
        print(f"❌ File not found: {personal_info_path}")
        print("   Make sure you're running from the project root")
        return False


def test_template_file():
    """Test if HTML template exists."""
    print("\n📄 Testing HTML Template")
    print("-" * 40)
    
    template_path = "modules/cv_generator/ats_cv_template.html"
    
    if os.path.exists(template_path):
        print(f"✅ Found template: {template_path}")
        
        try:
            with open(template_path, 'r') as f:
                content = f.read()
            
            # Check for key template placeholders
            placeholders = [
                '{{name}}', '{{job_title}}', '{{email}}',
                '{{summary}}', '{{experience}}', '{{skills}}'
            ]
            
            found_placeholders = []
            for placeholder in placeholders:
                if placeholder in content:
                    found_placeholders.append(placeholder)
            
            print(f"✅ Template size: {len(content)} characters")
            print(f"✅ Placeholders found: {len(found_placeholders)}/{len(placeholders)}")
            print(f"   Sample placeholders: {found_placeholders[:3]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error reading template: {e}")
            return False
    else:
        print(f"❌ Template not found: {template_path}")
        return False


def test_output_directory():
    """Test output directory setup."""
    print("\n📂 Testing Output Directory")
    print("-" * 40)
    
    output_dir = "modules/cv_generator/output"
    
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        print(f"✅ Output directory ready: {output_dir}")
        
        # Check write permissions
        test_file = os.path.join(output_dir, "test_write.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        if os.path.exists(test_file):
            os.remove(test_file)
            print("✅ Write permissions confirmed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with output directory: {e}")
        return False


def test_cv_generator_import():
    """Test CV generator import."""
    print("\n📦 Testing CV Generator Import")
    print("-" * 40)
    
    try:
        from modules.cv_generator.generate_pdf import CVPDFGenerator
        print("✅ CVPDFGenerator imported successfully")
        
        # Test initialization
        generator = CVPDFGenerator()
        print("✅ CVPDFGenerator initialized")
        
        # Check if it has required methods
        required_methods = ['load_data', 'render_template', 'generate_pdf', 'run']
        for method in required_methods:
            if hasattr(generator, method):
                print(f"✅ Method '{method}' available")
            else:
                print(f"⚠️  Method '{method}' not found")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False


def test_data_loading():
    """Test data loading functionality."""
    print("\n📊 Testing Data Loading")
    print("-" * 40)
    
    try:
        from modules.cv_generator.generate_pdf import CVPDFGenerator
        
        generator = CVPDFGenerator(
            data_file="modules/shared/data/personal_info.json",
            template_file="modules/cv_generator/ats_cv_template.html"
        )
        
        # Test data loading
        data = generator.load_data()
        
        if data:
            print("✅ Data loaded successfully")
            print(f"   Data keys: {list(data.keys())}")
            
            # Check specific data points
            if 'personal_info' in data:
                personal = data['personal_info']
                if personal.get('name'):
                    print(f"   Name: {personal['name']}")
            
            if 'work_info' in data:
                work = data['work_info']
                if work.get('summary'):
                    print(f"   Summary length: {len(work['summary'])} chars")
                if work.get('experience'):
                    print(f"   Experience entries: {len(work['experience'])}")
            
            return True
        else:
            print("❌ No data loaded")
            return False
            
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False


def test_template_rendering():
    """Test template rendering."""
    print("\n🎨 Testing Template Rendering")
    print("-" * 40)
    
    try:
        from modules.cv_generator.generate_pdf import CVPDFGenerator
        
        generator = CVPDFGenerator(
            data_file="modules/shared/data/personal_info.json",
            template_file="modules/cv_generator/ats_cv_template.html"
        )
        
        # Load data and render template
        data = generator.load_data()
        rendered_html = generator.render_template(data)
        
        if rendered_html:
            print("✅ Template rendered successfully")
            print(f"   HTML length: {len(rendered_html)} characters")
            
            # Check if placeholders were replaced
            placeholders_found = rendered_html.count('{{')
            if placeholders_found == 0:
                print("✅ All placeholders replaced")
            else:
                print(f"⚠️  {placeholders_found} placeholders remaining")
            
            # Check for key content
            if '<html' in rendered_html:
                print("✅ Valid HTML structure")
            
            return True
        else:
            print("❌ Template rendering failed")
            return False
            
    except Exception as e:
        print(f"❌ Error rendering template: {e}")
        return False


async def test_pdf_generation():
    """Test PDF generation."""
    print("\n📄 Testing PDF Generation")
    print("-" * 40)
    
    try:
        from modules.cv_generator.generate_pdf import CVPDFGenerator
        
        generator = CVPDFGenerator(
            data_file="modules/shared/data/personal_info.json",
            template_file="modules/cv_generator/ats_cv_template.html"
        )
        
        # Generate CV with test name
        output_path = await generator.run("test_cv_manual.pdf")
        
        if output_path and os.path.exists(output_path):
            print(f"✅ PDF generated successfully: {output_path}")
            
            # Check file size
            file_size = os.path.getsize(output_path)
            print(f"   File size: {file_size:,} bytes")
            
            if file_size > 1000:  # Reasonable PDF size
                print("✅ PDF size looks good")
            else:
                print("⚠️  PDF might be too small")
            
            # Check if it's a PDF file
            with open(output_path, 'rb') as f:
                header = f.read(4)
                if header == b'%PDF':
                    print("✅ Valid PDF format")
                else:
                    print("⚠️  File might not be a valid PDF")
            
            return True
        else:
            print("❌ PDF generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return False


async def test_custom_filename():
    """Test PDF generation with custom filename."""
    print("\n📝 Testing Custom Filename")
    print("-" * 40)
    
    try:
        from modules.cv_generator.generate_pdf import CVPDFGenerator
        
        generator = CVPDFGenerator()
        
        # Generate with custom name
        custom_name = "Jacob_SoftwareEngineer_CV.pdf"
        output_path = await generator.run(custom_name)
        
        if output_path and os.path.exists(output_path):
            print(f"✅ Custom filename PDF generated: {Path(output_path).name}")
            
            # Verify the name matches
            if custom_name in output_path:
                print("✅ Filename matches request")
            
            return True
        else:
            print("❌ Custom filename generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error with custom filename: {e}")
        return False


def test_playwright_availability():
    """Test if Playwright is available and configured."""
    print("\n🎭 Testing Playwright Availability")
    print("-" * 40)
    
    try:
        from playwright.async_api import async_playwright
        print("✅ Playwright library imported")
        
        # Note: We don't test browser launch here as it might be slow
        # The actual PDF generation test will verify this
        print("✅ Playwright appears to be configured")
        print("   (Browser availability tested during PDF generation)")
        
        return True
        
    except ImportError:
        print("❌ Playwright not installed")
        print("   Install with: pip install playwright")
        print("   Then run: playwright install")
        return False
    except Exception as e:
        print(f"❌ Playwright error: {e}")
        return False


async def run_all_tests():
    """Run all CV generator tests."""
    print("=" * 60)
    print("🧪 CV GENERATOR MODULE MANUAL TESTS")
    print("=" * 60)
    
    # Synchronous tests
    sync_tests = [
        test_personal_info_file,
        test_template_file,
        test_output_directory,
        test_cv_generator_import,
        test_data_loading,
        test_template_rendering,
        test_playwright_availability
    ]
    
    results = []
    
    for test in sync_tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            results.append(False)
    
    # Async tests
    async_tests = [
        test_pdf_generation,
        test_custom_filename
    ]
    
    for test in async_tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Async test {test.__name__} failed: {e}")
            results.append(False)
    
    # Clean up test files
    cleanup_files = [
        "modules/cv_generator/output/test_cv_manual.pdf",
        "modules/cv_generator/output/Jacob_SoftwareEngineer_CV.pdf"
    ]
    
    for file_path in cleanup_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🧹 Cleaned up: {file_path}")
            except:
                pass
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check dependencies and file paths.")
    
    print("\n💡 Next steps:")
    print("- For full workflow: python ats_workflow.py job_description.txt")
    print("- For standalone generation: python modules/cv_generator/generate_cv_pdf.py")
    print("- If Playwright fails: pip install playwright && playwright install")
    
    print("\n📋 Quick usage:")
    print("from modules.cv_generator import CVPDFGenerator")
    print("generator = CVPDFGenerator()")
    print("output = await generator.run('My_CV.pdf')")


if __name__ == "__main__":
    asyncio.run(run_all_tests())