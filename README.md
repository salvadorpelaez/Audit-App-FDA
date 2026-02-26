# Audit Comparison App

A simple web application for comparing digital health applications against regulatory requirements.

## Features

- **Regulatory Framework Analysis**: Compare applications against HIPAA, FDA Software as Medical Device, and GDPR Health regulations
- **JSON Input**: Support for structured application data input
- **Compliance Scoring**: Automated compliance analysis with scoring system
- **Visual Results**: Color-coded compliance status with detailed findings
- **Sample Data**: Pre-loaded sample application for testing

## Regulations Supported

### HIPAA (Health Insurance Portability and Accountability Act)
- Privacy Rule compliance
- Security Rule requirements
- Breach notification procedures
- Access controls

### FDA Software as a Medical Device (SaMD)
- Clinical validation requirements
- Risk management procedures
- Documentation and labeling

### GDPR Health Data Protection
- Data minimization principles
- Consent management
- Data subject rights

## Installation

1. Clone or download the project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open browser to: http://127.0.0.1:5001

## Usage

1. **Enter Application Data**: Provide application details in JSON format
2. **Select Regulation**: Choose the regulatory framework to compare against
3. **Analyze**: Click "Analyze Compliance" to run the comparison
4. **Review Results**: View detailed compliance analysis with scores and findings

## Application Data Format

```json
{
  "product_name": "Application Name",
  "intended_use": "Description of intended use",
  "features": ["Feature 1", "Feature 2"],
  "technical_infrastructure": {
    "hosting": "Hosting details",
    "database": "Database information"
  }
}
```

## Compliance Scoring

- **70-100%**: COMPLIANT (Green)
- **40-69%**: PARTIALLY_COMPLIANT (Yellow)
- **0-39%**: NON_COMPLIANT (Red)

## API Endpoints

- `GET /api/regulations` - List available regulations
- `POST /api/analyze` - Analyze application compliance

## Technical Details

- **Backend**: Flask web framework
- **Frontend**: HTML5, CSS3, JavaScript
- **Analysis**: Keyword-based compliance scoring
- **Port**: 5001 (to avoid conflicts with other applications)

## Limitations

This is a simplified compliance tool for demonstration purposes. For production use, consider:
- More sophisticated NLP for requirement analysis
- Integration with official regulatory databases
- Detailed risk assessment methodologies
- Legal review of compliance determinations
