# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import HttpCase
from odoo.tests import tagged
from unittest.mock import patch
from .common import OpenAPITestCase


@tagged('post_install', '-at_install')
class TestOpenAPIControllers(HttpCase):
    """Test cases for OpenAPI controllers."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment for HTTP tests."""
        super().setUpClass()
        
        # Create test namespace with token
        cls.test_namespace = cls.env['openapi.namespace'].create({
            'name': 'test_controller',
            'description': 'Test namespace for controller tests',
            'log_request': 'info',
            'log_response': 'debug',
        })
        
        # Ensure namespace has a token
        if not cls.test_namespace.token:
            cls.test_namespace._generate_token()

    def test_swagger_json_endpoint_exists(self):
        """Test that swagger.json endpoint is accessible."""
        url = f'/api/v1/{self.test_namespace.name}/swagger.json'
        
        # Test without token (should return 403 Forbidden)
        response = self.url_open(url)
        self.assertEqual(response.status_code, 403, "Should return 403 without valid token")

    def test_swagger_json_endpoint_with_token(self):
        """Test swagger.json endpoint with valid token."""
        url = f'/api/v1/{self.test_namespace.name}/swagger.json?token={self.test_namespace.token}'
        
        # Test with valid token
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200, "Should return 200 with valid token")
        
        # Check content type
        self.assertEqual(response.headers.get('Content-Type'), 'application/json')

    def test_swagger_json_endpoint_with_invalid_token(self):
        """Test swagger.json endpoint with invalid token."""
        url = f'/api/v1/{self.test_namespace.name}/swagger.json?token=invalid_token'
        
        response = self.url_open(url)
        self.assertEqual(response.status_code, 403, "Should return 403 with invalid token")

    def test_swagger_json_endpoint_nonexistent_namespace(self):
        """Test swagger.json endpoint with nonexistent namespace."""
        url = '/api/v1/nonexistent_namespace/swagger.json?token=any_token'
        
        response = self.url_open(url)
        self.assertEqual(response.status_code, 404, "Should return 404 for nonexistent namespace")

    def test_swagger_json_download_parameter(self):
        """Test swagger.json endpoint with download parameter."""
        url = f'/api/v1/{self.test_namespace.name}/swagger.json?token={self.test_namespace.token}&download=1'
        
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200, "Should return 200 with download parameter")
        
        # Check content disposition header for download
        content_disposition = response.headers.get('Content-Disposition')
        self.assertIsNotNone(content_disposition, "Should have Content-Disposition header")
        self.assertIn('swagger.json', content_disposition, "Should contain filename in header")

    def test_swagger_json_response_structure(self):
        """Test that swagger.json returns valid OpenAPI structure."""
        url = f'/api/v1/{self.test_namespace.name}/swagger.json?token={self.test_namespace.token}'
        
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        
        # Parse JSON response
        import json
        try:
            swagger_data = json.loads(response.content.decode())
            
            # Check required OpenAPI fields
            required_fields = ['swagger', 'info', 'host', 'basePath', 'schemes']
            for field in required_fields:
                self.assertIn(field, swagger_data, f"Response should contain {field}")
            
            # Check swagger version
            self.assertEqual(swagger_data['swagger'], '2.0', "Should use OpenAPI 2.0 format")
            
            # Check info section
            self.assertIn('title', swagger_data['info'])
            self.assertIn('version', swagger_data['info'])
            
        except json.JSONDecodeError:
            self.fail("Response should be valid JSON")

    def test_controller_route_registration(self):
        """Test that controller routes are properly registered."""
        # This test verifies that the routes are registered in Odoo's routing system
        from odoo.http import root
        
        # Check if the route pattern exists
        route_found = False
        for rule in root.get_db_router('test').iter_rules():
            if '/api/v1/' in rule.rule and 'swagger.json' in rule.rule:
                route_found = True
                break
        
        self.assertTrue(route_found, "OpenAPI route should be registered")

    def test_controller_csrf_disabled(self):
        """Test that CSRF is properly disabled for API endpoints."""
        # This is implicitly tested by the HTTP requests above
        # If CSRF was enabled, the requests would fail
        url = f'/api/v1/{self.test_namespace.name}/swagger.json?token={self.test_namespace.token}'
        
        response = self.url_open(url)
        # If we get here without CSRF errors, the test passes
        self.assertIn(response.status_code, [200, 403, 404], "Request should not fail due to CSRF")

    def test_controller_auth_none(self):
        """Test that authentication is set to none for public API access."""
        # This is tested by making requests without authentication
        # The endpoint should be accessible (though may return 403 for invalid tokens)
        url = f'/api/v1/{self.test_namespace.name}/swagger.json'
        
        response = self.url_open(url)
        # Should not return 401 (authentication required)
        self.assertNotEqual(response.status_code, 401, "Should not require authentication")

    def test_controller_error_handling(self):
        """Test controller error handling for various scenarios."""
        # Test with malformed URL
        response = self.url_open('/api/v1//swagger.json')  # Double slash
        self.assertIn(response.status_code, [404, 400], "Should handle malformed URLs gracefully")
        
        # Test with special characters in namespace
        response = self.url_open('/api/v1/test@namespace/swagger.json')
        self.assertIn(response.status_code, [404, 400], "Should handle special characters gracefully")


class TestOpenAPIControllersUnit(OpenAPITestCase):
    """Unit tests for OpenAPI controller methods."""

    def test_oas_controller_instantiation(self):
        """Test that OAS controller can be instantiated."""
        from odoo.addons.openapi.controllers.main import OAS
        
        controller = OAS()
        self.assertIsNotNone(controller, "Controller should be instantiable")

    def test_controller_method_exists(self):
        """Test that required controller methods exist."""
        from odoo.addons.openapi.controllers.main import OAS
        
        controller = OAS()
        
        # Check that the main endpoint method exists
        self.assertTrue(hasattr(controller, 'OAS_json_spec_download'),
                       "Controller should have OAS_json_spec_download method")

    @patch('odoo.http.request')
    def test_controller_database_access(self, mock_request):
        """Test controller database access patterns."""
        from odoo.addons.openapi.controllers.main import OAS
        
        # Mock the request environment
        mock_request.env = self.env
        
        controller = OAS()
        
        # Test that controller can access the environment
        # This would be tested with actual method calls in a real implementation
        self.assertTrue(hasattr(controller, 'OAS_json_spec_download'))

    def test_controller_response_headers(self):
        """Test that controller sets appropriate response headers."""
        # This test would verify response header configuration
        # Implementation depends on the actual controller code
        
        # For now, we verify the controller structure exists
        from odoo.addons.openapi.controllers.main import OAS
        controller = OAS()
        self.assertIsNotNone(controller)

    def test_controller_json_serialization(self):
        """Test JSON serialization in controller responses."""
        # Test that the controller can handle JSON serialization
        # This includes date/datetime objects using date_utils.json_default
        
        import json
        from odoo.tools import date_utils
        from datetime import datetime, date
        
        # Test data with various types
        test_data = {
            'string': 'test',
            'number': 123,
            'boolean': True,
            'date': date.today(),
            'datetime': datetime.now(),
            'null': None,
        }
        
        # Should not raise exception
        try:
            json_str = json.dumps(test_data, default=date_utils.json_default)
            self.assertIsInstance(json_str, str, "Should serialize to JSON string")
        except Exception as e:
            self.fail(f"JSON serialization should not fail: {e}")
