# CV PDF Generator

This Python script generates a high-quality PDF from your ATS-friendly CV template using your personal data.

## Features

- 🚀 **Automated PDF Generation**: Converts HTML template to PDF programmatically
- 📄 **Data Integration**: Uses your `personal_info.json` data automatically
- 🎨 **Print-Optimized**: Preserves all styling, colors, and layout from the template
- 📊 **Professional Quality**: Generates publication-ready PDF with proper fonts and spacing
- 🔧 **Customizable**: Supports custom output filenames and file paths

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements_pdf.txt
   ```

2. **Install Playwright browser:**
   ```bash
   playwright install chromium
   ```

## Usage

### Basic Usage
Generate PDF with auto-generated filename:
```bash
python generate_cv_pdf.py
```

### Custom Options
```bash
# Custom data file
python generate_cv_pdf.py --data path/to/your/data.json

# Custom template file
python generate_cv_pdf.py --template path/to/template.html

# Custom output filename
python generate_cv_pdf.py --output "John_Doe_CV_2025.pdf"

# All options combined
python generate_cv_pdf.py --data data/personal_info.json --template ats_cv_template.html --output "My_CV.pdf"
```

## Output

- 📁 **Location**: PDFs are saved in the `output/` directory
- 📋 **Format**: A4 size with 0.5" margins
- 🎨 **Quality**: Includes all colors, backgrounds, and styling
- 📱 **Filename**: Auto-generated based on your name and timestamp (e.g., `Jacob_Christian_P_Guanzing_CV_20250815_143022.pdf`)

## How It Works

1. **Loads Data**: Reads your `personal_info.json` file
2. **Processes Template**: Embeds JSON data directly into HTML template
3. **Renders HTML**: Uses Playwright to render the complete CV in a browser
4. **Generates PDF**: Converts the rendered HTML to high-quality PDF
5. **Saves File**: Outputs the PDF to the `output/` directory

## Requirements

- Python 3.7+
- Playwright (for HTML to PDF conversion)
- Jinja2 (for template processing)
- Chromium browser (installed automatically by Playwright)

## Advantages Over Browser Printing

- ✅ **Consistent Output**: Same result every time, regardless of browser
- ✅ **Automated Process**: No manual clicking or print dialog
- ✅ **Batch Processing**: Can generate multiple PDFs programmatically
- ✅ **Perfect Styling**: All CSS styles and print media queries applied correctly
- ✅ **Professional Quality**: Publication-ready PDF output

## Troubleshooting

### Common Issues

1. **"Data file not found"**
   - Ensure `data/personal_info.json` exists
   - Check file path with `--data` option

2. **"Template file not found"**
   - Ensure `ats_cv_template.html` exists in the same directory
   - Use `--template` to specify different path

3. **Browser installation issues**
   - Run `playwright install chromium` again
   - Check internet connection during installation

### Tips

- Run from the same directory as your HTML template
- Ensure your `personal_info.json` has valid JSON syntax
- Check that all required fields are present in your data file

## Example Output

```
🚀 Starting CV PDF generation...
📄 Loading personal data...
🔧 Processing HTML template...
📋 Generating PDF...
✅ PDF generated successfully!
📁 Output location: /path/to/output/Jacob_Christian_P_Guanzing_CV_20250815_143022.pdf
📊 File size: 156,789 bytes

🎉 Success! Your CV PDF has been generated:
   /path/to/output/Jacob_Christian_P_Guanzing_CV_20250815_143022.pdf
```