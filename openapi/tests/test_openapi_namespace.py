# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from .common import OpenAPITestCase


class TestOpenAPINamespace(OpenAPITestCase):
    """Test cases for openapi.namespace model."""

    def test_namespace_creation(self):
        """Test namespace creation with required fields."""
        namespace = self.env['openapi.namespace'].create({
            'name': 'test_api_creation',
            'description': 'Test API for creation test',
        })
        
        self.assertTrue(namespace.active, "Namespace should be active by default")
        self.assertEqual(namespace.name, 'test_api_creation')
        self.assertEqual(namespace.description, 'Test API for creation test')
        self.assertEqual(namespace.log_request, 'disabled', "Default log_request should be disabled")
        self.assertEqual(namespace.log_response, 'error', "Default log_response should be error")

    def test_namespace_name_required(self):
        """Test that namespace name is required."""
        with self.assertRaises(ValidationError):
            self.env['openapi.namespace'].create({
                'description': 'Test without name',
            })

    def test_namespace_log_count_computation(self):
        """Test log count computation."""
        # Initially should have 0 logs
        self.assertEqual(self.test_namespace.log_count, 0)
        
        # Create a log entry
        self._create_test_log()
        
        # Recompute and check
        self.test_namespace._compute_log_count()
        self.assertEqual(self.test_namespace.log_count, 1)
        
        # Create another log entry
        self._create_test_log()
        
        # Recompute and check
        self.test_namespace._compute_log_count()
        self.assertEqual(self.test_namespace.log_count, 2)

    def test_namespace_last_log_date_computation(self):
        """Test last log date computation."""
        # Initially should have no last log date
        self.assertFalse(self.test_namespace.last_log_date)
        
        # Create a log entry
        log = self._create_test_log()
        
        # Recompute and check
        self.test_namespace._compute_last_used()
        self.assertEqual(self.test_namespace.last_log_date, log.create_date)

    def test_namespace_get_oas_method(self):
        """Test OpenAPI Specification generation."""
        # This test validates the get_OAS method exists and returns proper structure
        oas_spec = self.test_namespace.get_OAS()
        
        self.assertIsInstance(oas_spec, dict, "OAS spec should be a dictionary")
        
        # Check required OpenAPI fields
        required_fields = ['swagger', 'info', 'host', 'basePath', 'schemes', 'consumes', 'produces']
        for field in required_fields:
            self.assertIn(field, oas_spec, f"OAS spec should contain {field}")
        
        # Check info section
        self.assertIn('title', oas_spec['info'])
        self.assertIn('version', oas_spec['info'])
        
        # Check basePath contains namespace name
        self.assertIn(self.test_namespace.name, oas_spec['basePath'])

    def test_namespace_token_generation(self):
        """Test namespace token generation and validation."""
        # Check that namespace has a token
        self.assertTrue(self.test_namespace.token, "Namespace should have a token")
        
        # Token should be a string
        self.assertIsInstance(self.test_namespace.token, str)
        
        # Token should have reasonable length (UUID format)
        self.assertGreaterEqual(len(self.test_namespace.token), 32)

    def test_namespace_access_relationship(self):
        """Test relationship with openapi.access records."""
        # Check that test_access is linked to test_namespace
        self.assertIn(self.test_access, self.test_namespace.access_ids)
        
        # Create another access record
        test_model_2 = self.env['ir.model'].search([('model', '=', 'res.users')], limit=1)
        access_2 = self.env['openapi.access'].create({
            'namespace_id': self.test_namespace.id,
            'model_id': test_model_2.id,
            'api_read': True,
        })
        
        # Check both access records are linked
        self.assertEqual(len(self.test_namespace.access_ids), 2)
        self.assertIn(access_2, self.test_namespace.access_ids)

    def test_namespace_log_settings_validation(self):
        """Test log settings validation."""
        # Test valid log_request values
        valid_request_values = ['disabled', 'info', 'debug']
        for value in valid_request_values:
            self.test_namespace.log_request = value
            # Should not raise any exception
        
        # Test valid log_response values
        valid_response_values = ['disabled', 'error', 'debug']
        for value in valid_response_values:
            self.test_namespace.log_response = value
            # Should not raise any exception

    def test_namespace_active_flag(self):
        """Test namespace active flag functionality."""
        # Namespace should be active by default
        self.assertTrue(self.test_namespace.active)
        
        # Deactivate namespace
        self.test_namespace.active = False
        self.assertFalse(self.test_namespace.active)
        
        # Reactivate namespace
        self.test_namespace.active = True
        self.assertTrue(self.test_namespace.active)
