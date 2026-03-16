#!/usr/bin/env python3
"""
Comprehensive test suite for error handling in the Document Template Processing Service.

This test suite covers:
- Template syntax errors (Jinja2)
- Undefined variable errors  
- Runtime template errors
- File processing errors
- PDF conversion errors
- Input validation errors

Uses Gotenberg to generate test .docx files with various error conditions.
"""

import pytest
import requests
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Test configuration
BASE_URL = "http://localhost:8000"
GOTENBERG_API_URL = "http://localhost:3000"
TEST_FILES_DIR = Path("test_files")

# Ensure test files directory exists
TEST_FILES_DIR.mkdir(exist_ok=True)

class TestDocumentProcessor:
    """Test class for document processing error handling"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment and generate test files"""
        # Wait for services to be ready
        cls.wait_for_services()
        
        # Generate test .docx files with various error conditions
        cls.generate_test_files()
    
    @staticmethod
    def wait_for_services(timeout: int = 60):
        """Wait for both services to be ready"""
        services = [
            (BASE_URL, "Document service"),
            (GOTENBERG_API_URL, "Gotenberg service")
        ]
        
        for url, name in services:
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    response = requests.get(f"{url}/", timeout=5)
                    if response.status_code == 200:
                        print(f"✓ {name} is ready")
                        break
                except requests.exceptions.RequestException:
                    time.sleep(2)
            else:
                pytest.fail(f"{name} not ready after {timeout}s")
    
    @staticmethod
    def create_docx_with_python_docx(content_paragraphs: list, output_path: Path):
        """Create a proper DOCX file using python-docx library with Jinja2 content"""
        try:
            from docx import Document
            
            doc = Document()
            
            # Add paragraphs with Jinja2 content
            for paragraph_text in content_paragraphs:
                doc.add_paragraph(paragraph_text)
            
            doc.save(output_path)
            
        except Exception as e:
            print(f"Failed to create {output_path}: {e}")
            # Fallback to creating an empty docx file
            output_path.write_bytes(b'')
    
    @classmethod
    def generate_test_files(cls):
        """Generate test .docx files with proper Jinja2 syntax that work with docxtpl"""
        
        # Define templates with proper Jinja2 syntax for Word documents
        test_templates = {
            # Valid template for baseline testing
            "valid_template.docx": [
                "Invoice",
                "Customer: {{customer.name}}",
                "Amount: ${{amount}}",
                "{% if items %}",
                "Items:",
                "{% for item in items %}",
                "- {{item.description}}: ${{item.price}}",
                "{% endfor %}",
                "{% endif %}"
            ],
            
            # Template syntax errors
            "syntax_error_unclosed_tag.docx": [
                "Invoice",
                "Customer: {{customer.name}}",
                "{% if items %}",
                "Items:",
                "{% for item in items %}",
                "- {{item.description}}: ${{item.price}}",
                "{% endif %}"
                # Actually missing {% endfor %} - this should cause TemplateSyntaxError
            ],
            
            "syntax_error_invalid_tag.docx": [
                "Invoice", 
                "Customer: {{customer.name}}",
                "{% invalidtag items %}",
                "This is invalid",
                "{% endinvalidtag %}"
            ],
            
            "syntax_error_malformed_variable.docx": [
                "Invoice",
                "Customer: {{customer.name",  # Missing closing brace
                "Amount: {{amount}}"
            ],
            
            # Undefined variable errors
            "undefined_variable.docx": [
                "Invoice",
                "Customer: {{customer.name}}",
                "Missing: {{nonexistent_variable}}",
                "Amount: ${{amount}}"
            ],
            
            "undefined_nested_variable.docx": [
                "Invoice",
                "Customer: {{customer.missing_field.name}}",
                "Amount: ${{amount}}"
            ],
            
            # Runtime error templates - using operations that will fail
            "runtime_error_type_mismatch.docx": [
                "Invoice",
                "Customer: {{customer.name}}",
                "Total: ${{quantity * price}}",
                "Length calculation: {{quantity | length}}",  # This will fail if quantity is int
                "Note: this should cause type errors"
            ],
            
            "runtime_error_division_by_zero.docx": [
                "Invoice", 
                "Customer: {{customer.name}}",
                "Rate: {{total / zero_value}}",  # Division by zero
                "Another calculation: {{100 / zero_value}}"
            ],
            
            # Complex template for testing advanced features
            "complex_template.docx": [
                "Complex Invoice",
                "Date: {{invoice_date}}",
                "Customer: {{customer.name}}",
                "",
                "{% if customer.address %}",
                "Address: {{customer.address.street}}, {{customer.address.city}}",
                "{% endif %}",
                "",
                "Items:",
                "{% for item in items %}",
                "{{item.description}} - Qty: {{item.quantity}} - Price: ${{item.price}} - Total: ${{item.quantity * item.price}}",
                "{% endfor %}",
                "",
                "Subtotal: ${{subtotal}}",
                "{% if discount > 0 %}",
                "Discount: -${{discount}}",
                "{% endif %}",
                "Total: ${{subtotal - discount}}"
            ]
        }
        
        for filename, content_paragraphs in test_templates.items():
            filepath = TEST_FILES_DIR / filename
            if not filepath.exists():
                cls.create_docx_with_python_docx(content_paragraphs, filepath)
                print(f"Generated test file: {filename}")
    
    @staticmethod
    def create_docx_from_html(html_content: str, output_path: Path):
        """Convert HTML to DOCX using Gotenberg"""
        try:
            # Prepare the HTML file for Gotenberg
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_html:
                temp_html.write(html_content)
                temp_html.flush()
                
                # Convert HTML to DOCX using Gotenberg
                with open(temp_html.name, 'rb') as html_file:
                    files = {
                        'files': ('template.html', html_file, 'text/html')
                    }
                    
                    response = requests.post(
                        f"{GOTENBERG_API_URL}/forms/libreoffice/convert",
                        files=files,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        with open(output_path, 'wb') as docx_file:
                            docx_file.write(response.content)
                    else:
                        raise Exception(f"Gotenberg conversion failed: {response.status_code}")
                        
        finally:
            # Clean up temporary HTML file
            if 'temp_html' in locals():
                os.unlink(temp_html.name)
    
    @staticmethod
    def make_request(file_path: Optional[Path] = None, data: Optional[Dict] = None, 
                    filename: Optional[str] = None) -> requests.Response:
        """Make a request to the document processing endpoint"""
        url = f"{BASE_URL}/api/v1/process-template-document"
        
        files = {}
        form_data = {}
        
        if file_path and file_path.exists():
            files['file'] = (filename or file_path.name, open(file_path, 'rb'), 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        elif filename:
            # For testing missing file scenarios
            form_data['filename'] = filename
            
        if data is not None:
            form_data['data'] = json.dumps(data)
            
        try:
            response = requests.post(url, files=files, data=form_data, timeout=30)
            return response
        finally:
            # Close file handles
            for file_tuple in files.values():
                if hasattr(file_tuple[1], 'close'):
                    file_tuple[1].close()
    
    def assert_error_response(self, response: requests.Response, 
                            expected_error_type: str, 
                            expected_status: int = 400):
        """Assert that response contains expected error structure"""
        assert response.status_code == expected_status
        
        error_data = response.json()
        assert error_data["status"] == "error"
        assert error_data["error_type"] == expected_error_type
        assert "message" in error_data
        assert "details" in error_data
        
        return error_data

# =============================================================================
# FILE PROCESSING ERROR TESTS
# =============================================================================

class TestFileProcessingErrors(TestDocumentProcessor):
    """Test file-related error handling"""
    
    def test_missing_file(self):
        """Test error when no file is provided"""
        data = {"name": "Test"}
        response = self.make_request(data=data)
        
        # FastAPI validation error for missing file
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
    
    def test_invalid_file_type(self):
        """Test error when non-.docx file is uploaded"""
        # Create a text file
        text_file = TEST_FILES_DIR / "test.txt"
        text_file.write_text("This is not a docx file")
        
        data = {"name": "Test"}
        response = self.make_request(file_path=text_file, data=data)
        
        error_data = self.assert_error_response(response, "invalid_file_type", 400)
        assert "supported_types" in error_data["details"]
        assert ".docx" in error_data["details"]["supported_types"]
    
    def test_corrupted_docx_file(self):
        """Test error when corrupted .docx file is uploaded"""
        # Create a fake .docx file with invalid content
        fake_docx = TEST_FILES_DIR / "corrupted.docx"
        fake_docx.write_text("This is not a valid docx file content")
        
        data = {"name": "Test"}
        response = self.make_request(file_path=fake_docx, data=data)
        
        # The corrupted file triggers template_document_corruption during template loading  
        error_data = self.assert_error_response(response, "template_document_corruption", 400)
        assert "suggestion" in error_data["details"]
    
    def test_missing_template_data(self):
        """Test error when no template data is provided"""
        valid_template = TEST_FILES_DIR / "valid_template.docx"
        response = self.make_request(file_path=valid_template)
        
        # FastAPI validation error for missing data
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
    
    def test_invalid_json_data(self):
        """Test error when invalid JSON is provided"""
        valid_template = TEST_FILES_DIR / "valid_template.docx"
        
        # Test with malformed JSON string
        url = f"{BASE_URL}/api/v1/process-template-document"
        with open(valid_template, 'rb') as f:
            files = {'file': ('template.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            data = {'data': '{"name": "test", invalid json}'}  # Malformed JSON
            
            response = requests.post(url, files=files, data=data, timeout=30)
        
        # FastAPI returns 422 for validation errors, not 400
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data  # FastAPI validation error format

# =============================================================================
# TEMPLATE PROCESSING ERROR TESTS  
# =============================================================================

class TestTemplateProcessingErrors(TestDocumentProcessor):
    """Test Jinja2 template-related error handling"""
    
    def test_template_syntax_error_unclosed_tag(self):
        """Test template with unclosed Jinja2 tag"""
        template_file = TEST_FILES_DIR / "syntax_error_unclosed_tag.docx"
        data = {
            "customer": {"name": "John Doe"},
            "items": [{"description": "Item 1", "price": 10}]
        }
        
        response = self.make_request(file_path=template_file, data=data)
        error_data = self.assert_error_response(response, "template_syntax_error", 400)
        
        details = error_data["details"]
        assert "file" in details
        assert "syntax_error" in details
    
    def test_template_syntax_error_invalid_tag(self):
        """Test template with invalid Jinja2 tag"""
        template_file = TEST_FILES_DIR / "syntax_error_invalid_tag.docx"
        data = {
            "customer": {"name": "John Doe"},
            "items": [{"description": "Item 1", "price": 10}]
        }
        
        response = self.make_request(file_path=template_file, data=data)
        error_data = self.assert_error_response(response, "template_syntax_error", 400)
        
        details = error_data["details"]
        assert "file" in details
        assert "syntax_error" in details
    
    def test_template_syntax_error_malformed_variable(self):
        """Test template with malformed variable syntax"""
        template_file = TEST_FILES_DIR / "syntax_error_malformed_variable.docx"
        data = {
            "customer": {"name": "John Doe"},
            "amount": 100
        }
        
        response = self.make_request(file_path=template_file, data=data)
        error_data = self.assert_error_response(response, "template_syntax_error", 400)
        
        details = error_data["details"]
        assert "file" in details
        assert "syntax_error" in details
    
    def test_undefined_variable_error(self):
        """Test template with undefined variable - docxtpl handles gracefully by default"""
        template_file = TEST_FILES_DIR / "undefined_variable.docx"
        data = {
            "customer": {"name": "John Doe"},
            "amount": 100
            # Missing: nonexistent_variable - docxtpl will ignore this gracefully
        }
        
        response = self.make_request(file_path=template_file, data=data)
        
        # docxtpl handles undefined variables gracefully by default (doesn't raise errors)
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/pdf'
        assert len(response.content) > 0
        assert response.content.startswith(b'%PDF')  # Valid PDF header
    
    def test_undefined_nested_variable_error(self):
        """Test template with undefined nested variable"""
        template_file = TEST_FILES_DIR / "undefined_nested_variable.docx"
        data = {
            "customer": {"name": "John Doe"},  # Missing nested field
            "amount": 100
        }
        
        response = self.make_request(file_path=template_file, data=data)
        error_data = self.assert_error_response(response, "undefined_variable", 400)
        
        details = error_data["details"]
        assert "file" in details
        assert "undefined_variable" in details
    
    def test_runtime_error_type_mismatch(self):
        """Test template runtime error with type mismatch"""
        template_file = TEST_FILES_DIR / "runtime_error_type_mismatch.docx"
        data = {
            "customer": {"name": "John Doe"},
            "quantity": "5",  # String instead of number
            "price": "ten"    # String that can't be converted
        }
        
        response = self.make_request(file_path=template_file, data=data)
        error_data = self.assert_error_response(response, "template_runtime_error", 400)
        
        details = error_data["details"]
        assert "file" in details
        assert "runtime_error" in details
    
    def test_runtime_error_division_by_zero(self):
        """Test template runtime error with division by zero"""
        template_file = TEST_FILES_DIR / "runtime_error_division_by_zero.docx"
        data = {
            "customer": {"name": "John Doe"},
            "total": 100,
            "zero_value": 0
        }
        
        response = self.make_request(file_path=template_file, data=data)
        error_data = self.assert_error_response(response, "template_runtime_error", 400)
        
        details = error_data["details"]
        assert "file" in details
        assert "runtime_error" in details

# =============================================================================
# SUCCESSFUL PROCESSING TESTS
# =============================================================================

class TestSuccessfulProcessing(TestDocumentProcessor):
    """Test successful document processing scenarios"""
    
    def test_valid_template_processing(self):
        """Test successful processing of valid template"""
        template_file = TEST_FILES_DIR / "valid_template.docx"
        data = {
            "customer": {"name": "John Doe"},
            "amount": 150.00,
            "items": [
                {"description": "Web Development", "price": 100.00},
                {"description": "Consulting", "price": 50.00}
            ]
        }
        
        response = self.make_request(file_path=template_file, data=data)
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/pdf'
        assert len(response.content) > 0
        assert response.content.startswith(b'%PDF')  # Valid PDF header
    
    def test_complex_template_processing(self):
        """Test successful processing of complex template"""
        template_file = TEST_FILES_DIR / "complex_template.docx"
        data = {
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
                {"description": "Product B", "quantity": 1, "price": 75.00},
                {"description": "Service C", "quantity": 3, "price": 50.00}
            ],
            "subtotal": 275.00,
            "discount": 25.00
        }
        
        response = self.make_request(file_path=template_file, data=data)
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/pdf'
        assert len(response.content) > 0
        assert response.content.startswith(b'%PDF')
    
    def test_template_with_optional_fields(self):
        """Test template processing with optional fields"""
        template_file = TEST_FILES_DIR / "valid_template.docx"
        data = {
            "customer": {"name": "Jane Smith"},
            "amount": 75.00
            # items is optional and missing
        }
        
        response = self.make_request(file_path=template_file, data=data)
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/pdf'
        assert len(response.content) > 0

# =============================================================================
# SERVICE INTEGRATION TESTS
# =============================================================================

class TestServiceIntegration(TestDocumentProcessor):
    """Test service integration and edge cases"""
    
    def test_health_endpoint(self):
        """Test service health endpoint"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "Service is healthy !"
    
    def test_health_check_endpoint(self):
        """Test alternative health check endpoint"""
        response = requests.get(f"{BASE_URL}/health-check")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "Service is healthy !"
    
    def test_large_data_processing(self):
        """Test processing with large data payload"""
        template_file = TEST_FILES_DIR / "complex_template.docx"
        
        # Generate large items list
        items = []
        for i in range(100):
            items.append({
                "description": f"Item {i+1} with a very long description that should test data handling",
                "quantity": i + 1,
                "price": round((i + 1) * 1.5, 2)
            })
        
        data = {
            "invoice_date": "2024-01-15",
            "customer": {
                "name": "Large Corporation",
                "address": {
                    "street": "456 Enterprise Blvd",
                    "city": "Business City"
                }
            },
            "items": items,
            "subtotal": sum(item["quantity"] * item["price"] for item in items),
            "discount": 0
        }
        
        response = self.make_request(file_path=template_file, data=data)
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/pdf'
        assert len(response.content) > 0

# =============================================================================
# TEST RUNNER
# =============================================================================

if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])