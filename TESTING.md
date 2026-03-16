# Error Handling Test Suite

Comprehensive test suite for validating error handling in the Document Template Processing Service.

## Overview

This test suite validates the robust error handling implementation across all stages of document processing:

- **File Processing Errors**: Invalid files, missing files, corruption detection
- **Template Processing Errors**: Jinja2 syntax errors, undefined variables, runtime errors  
- **PDF Conversion Errors**: Gotenberg service failures, timeouts, invalid responses
- **Service Integration**: Health checks, large data processing, edge cases

## Architecture

### Test Components

1. **`test_error_handling.py`** - Main test suite with comprehensive error scenarios
2. **`run_tests.sh`** - Automated test runner with service management
3. **`requirements-test.txt`** - Testing dependencies
4. **`test_files/`** - Generated test documents with various error conditions

### Test File Generation

The test suite uses **Gotenberg's HTML to DOCX conversion** to generate test templates with specific Jinja2 syntax errors:

```python
# Example: Generate template with syntax error
html_content = """
<html><body>
    <p>Customer: {{customer.name}}</p>
    {% if items %}
        <ul>
        {% for item in items %}
            <li>{{item.description}}</li>
        <!-- Missing {% endfor %} -->
        </ul>
    {% endif %}
</body></html>
"""

# Convert to .docx using Gotenberg
create_docx_from_html(html_content, "syntax_error_unclosed_tag.docx")
```

## Test Categories

### 1. File Processing Error Tests

| Test Case | Error Type | Description |
|-----------|------------|-------------|
| `test_missing_file` | `missing_file` | No file uploaded |
| `test_invalid_file_type` | `invalid_file_type` | Non-.docx file upload |
| `test_corrupted_docx_file` | `invalid_docx_format` | Corrupted .docx content |
| `test_missing_template_data` | `missing_template_data` | No JSON data provided |
| `test_invalid_json_data` | `invalid_json` | Malformed JSON payload |

### 2. Template Processing Error Tests

| Test Case | Error Type | Template Issue |
|-----------|------------|----------------|
| `test_template_syntax_error_unclosed_tag` | `template_syntax_error` | Missing `{% endfor %}` |
| `test_template_syntax_error_invalid_tag` | `template_syntax_error` | Invalid Jinja2 tag |
| `test_template_syntax_error_malformed_variable` | `template_syntax_error` | Malformed `{{variable` |
| `test_undefined_variable_error` | `undefined_variable` | Missing template variable |
| `test_undefined_nested_variable_error` | `undefined_variable` | Missing nested field |
| `test_runtime_error_type_mismatch` | `template_runtime_error` | String * String operation |
| `test_runtime_error_division_by_zero` | `template_runtime_error` | Division by zero |

### 3. Successful Processing Tests

| Test Case | Description |
|-----------|-------------|
| `test_valid_template_processing` | Basic valid template with data injection |
| `test_complex_template_processing` | Complex template with loops, conditions, calculations |
| `test_template_with_optional_fields` | Template handling missing optional data |

### 4. Service Integration Tests

| Test Case | Description |
|-----------|-------------|
| `test_health_endpoint` | Service health check validation |
| `test_large_data_processing` | Processing with large data payloads |

## Generated Test Templates

The suite automatically generates these test `.docx` files:

### Valid Templates
- **`valid_template.docx`** - Basic invoice template for baseline testing
- **`complex_template.docx`** - Advanced template with tables, calculations, conditionals

### Syntax Error Templates
- **`syntax_error_unclosed_tag.docx`** - Missing `{% endfor %}` tag
- **`syntax_error_invalid_tag.docx`** - Invalid `{% invalidtag %}` usage
- **`syntax_error_malformed_variable.docx`** - Malformed `{{variable` syntax

### Variable Error Templates  
- **`undefined_variable.docx`** - References non-existent variable
- **`undefined_nested_variable.docx`** - References missing nested field

### Runtime Error Templates
- **`runtime_error_type_mismatch.docx`** - Type incompatible operations
- **`runtime_error_division_by_zero.docx`** - Division by zero scenario

## Running Tests

### Quick Start

```bash
# Run complete test suite (starts services automatically)
./run_tests.sh

# Run tests with existing services
./run_tests.sh --skip-services

# Cleanup test environment
./run_tests.sh --cleanup
```

### Manual Setup

```bash
# 1. Start services
docker compose up -d

# 2. Install test dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-test.txt

# 3. Run tests
pytest test_error_handling.py -v

# 4. Run with coverage
pytest test_error_handling.py --cov=main --cov-report=html
```

### Test Output

The test runner generates:
- **`test_results/report.html`** - Detailed test execution report
- **`test_results/coverage/`** - Code coverage analysis
- **`test_files/`** - Generated test documents

## Expected Error Response Validation

Each test validates the structured error response format:

```python
def assert_error_response(self, response, expected_error_type, expected_status=400):
    assert response.status_code == expected_status
    
    error_data = response.json()
    assert error_data["status"] == "error"
    assert error_data["error_type"] == expected_error_type
    assert "message" in error_data
    assert "details" in error_data
```

### Example Validated Response

```json
{
  "status": "error",
  "error_type": "template_syntax_error",
  "message": "Template syntax error: unexpected 'end of template'",
  "details": {
    "file": "syntax_error_unclosed_tag.docx",
    "line": 5,
    "column": 12,
    "template_name": "template.docx",
    "syntax_error": "unexpected 'end of template'"
  }
}
```

## Test Data Scenarios

### Basic Template Data
```json
{
  "customer": {"name": "John Doe"},
  "amount": 150.00,
  "items": [
    {"description": "Web Development", "price": 100.00},
    {"description": "Consulting", "price": 50.00}
  ]
}
```

### Complex Template Data
```json
{
  "invoice_date": "2024-01-15",
  "customer": {
    "name": "Acme Corporation",
    "address": {
      "street": "123 Business St",
      "city": "Enterprise City"
    }
  },
  "items": [
    {"description": "Product A", "quantity": 2, "price": 25.00},
    {"description": "Product B", "quantity": 1, "price": 75.00}
  ],
  "subtotal": 175.00,
  "discount": 25.00
}
```

### Error-Inducing Data
```json
{
  "customer": {"name": "John Doe"},
  "quantity": "5",     // String instead of number
  "price": "invalid",  // Non-numeric string
  "zero_value": 0      // For division by zero tests
}
```

## Service Dependencies

The test suite requires:

1. **Document Template Processing Service** (`localhost:8000`)
   - Main application with error handling
   - Must be built with latest changes

2. **Gotenberg Service** (`localhost:3000`)
   - For HTML to DOCX conversion (test file generation)
   - For final PDF conversion testing

3. **Python Environment**
   - Python 3.12+ 
   - pytest, requests, coverage tools

## Debugging Test Failures

### Common Issues

1. **Services Not Ready**
   ```bash
   # Check service status
   curl http://localhost:8000/
   curl http://localhost:3000/
   
   # View service logs
   docker compose logs api
   docker compose logs gotenberg
   ```

2. **Test File Generation Failures**
   ```bash
   # Check Gotenberg conversion manually
   curl -X POST http://localhost:3000/forms/libreoffice/convert \
     -F "files=@test.html" \
     --output test.docx
   ```

3. **Permission Issues**
   ```bash
   # Ensure test runner is executable
   chmod +x run_tests.sh
   
   # Check test files directory
   ls -la test_files/
   ```

### Verbose Testing

```bash
# Run with maximum verbosity
pytest test_error_handling.py -vvv --tb=long --capture=no

# Run specific test class
pytest test_error_handling.py::TestTemplateProcessingErrors -v

# Run single test method
pytest test_error_handling.py::TestTemplateProcessingErrors::test_undefined_variable_error -v
```

## Continuous Integration

For CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Run Error Handling Tests
  run: |
    ./run_tests.sh --skip-services
  env:
    GOTENBERG_API_URL: http://gotenberg:3000
    DOCUMENT_SERVICE_URL: http://localhost:8000
```

## Coverage Goals

Target coverage metrics:
- **Error Handling Functions**: 100%
- **Template Processing**: 95%+
- **File Operations**: 90%+
- **Overall Application**: 85%+

## Contributing

When adding new error scenarios:

1. **Create test template** using HTML → DOCX conversion
2. **Add test method** following naming convention
3. **Validate error response** structure and content
4. **Update documentation** with new test case
5. **Verify coverage** includes new error paths