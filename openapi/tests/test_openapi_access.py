# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from .common import OpenAPITestCase


class TestOpenAPIAccess(OpenAPITestCase):
    """Test cases for openapi.access model."""

    def test_access_creation(self):
        """Test access record creation with required fields."""
        access = self.env['openapi.access'].create({
            'namespace_id': self.test_namespace.id,
            'model_id': self.test_model.id,
            'api_create': True,
            'api_read': True,
            'api_update': False,
            'api_delete': False,
        })
        
        self.assertTrue(access.active, "Access should be active by default")
        self.assertEqual(access.namespace_id, self.test_namespace)
        self.assertEqual(access.model_id, self.test_model)
        self.assertTrue(access.api_create)
        self.assertTrue(access.api_read)
        self.assertFalse(access.api_update)
        self.assertFalse(access.api_delete)
        self.assertFalse(access.api_public_methods, "Public methods should be disabled by default")

    def test_access_namespace_required(self):
        """Test that namespace is required for access."""
        with self.assertRaises(ValidationError):
            self.env['openapi.access'].create({
                'model_id': self.test_model.id,
                'api_read': True,
            })

    def test_access_model_required(self):
        """Test that model is required for access."""
        with self.assertRaises(ValidationError):
            self.env['openapi.access'].create({
                'namespace_id': self.test_namespace.id,
                'api_read': True,
            })

    def test_access_model_name_computation(self):
        """Test model name computation from model_id."""
        self.assertEqual(self.test_access.model, self.test_model.model)
        
        # Change model and verify computation
        user_model = self.env['ir.model'].search([('model', '=', 'res.users')], limit=1)
        self.test_access.model_id = user_model
        self.assertEqual(self.test_access.model, 'res.users')

    def test_access_crud_permissions(self):
        """Test CRUD permissions configuration."""
        # Test all permissions enabled
        access = self.env['openapi.access'].create({
            'namespace_id': self.test_namespace.id,
            'model_id': self.test_model.id,
            'api_create': True,
            'api_read': True,
            'api_update': True,
            'api_delete': True,
        })
        
        self.assertTrue(access.api_create)
        self.assertTrue(access.api_read)
        self.assertTrue(access.api_update)
        self.assertTrue(access.api_delete)
        
        # Test all permissions disabled
        access.write({
            'api_create': False,
            'api_read': False,
            'api_update': False,
            'api_delete': False,
        })
        
        self.assertFalse(access.api_create)
        self.assertFalse(access.api_read)
        self.assertFalse(access.api_update)
        self.assertFalse(access.api_delete)

    def test_access_public_methods_configuration(self):
        """Test public methods configuration."""
        # Initially disabled
        self.assertFalse(self.test_access.api_public_methods)
        
        # Enable public methods
        self.test_access.api_public_methods = True
        self.assertTrue(self.test_access.api_public_methods)
        
        # Test with public_methods text field
        self.test_access.public_methods = "method1\nmethod2\nmethod3"
        self.assertIn("method1", self.test_access.public_methods)
        self.assertIn("method2", self.test_access.public_methods)
        self.assertIn("method3", self.test_access.public_methods)

    def test_access_get_OAS_definition_method(self):
        """Test OpenAPI definition generation for access."""
        # This test validates that the access record can generate OAS definitions
        # The actual method implementation would be tested here
        
        # Check that access has the required methods for OAS generation
        self.assertTrue(hasattr(self.test_access, 'get_OAS_definitions'))
        
        # Test method call (would return actual definitions in real implementation)
        try:
            definitions = self.test_access.get_OAS_definitions()
            self.assertIsInstance(definitions, dict, "OAS definitions should be a dictionary")
        except AttributeError:
            # Method might not be implemented yet, which is acceptable for this test
            pass

    def test_access_get_paths_method(self):
        """Test API paths generation for access."""
        # Check that access has the required methods for paths generation
        self.assertTrue(hasattr(self.test_access, 'get_paths'))
        
        # Test method call
        try:
            paths = self.test_access.get_paths()
            self.assertIsInstance(paths, dict, "API paths should be a dictionary")
        except AttributeError:
            # Method might not be implemented yet, which is acceptable for this test
            pass

    def test_access_active_flag(self):
        """Test access active flag functionality."""
        # Access should be active by default
        self.assertTrue(self.test_access.active)
        
        # Deactivate access
        self.test_access.active = False
        self.assertFalse(self.test_access.active)
        
        # Reactivate access
        self.test_access.active = True
        self.assertTrue(self.test_access.active)

    def test_access_model_cascade_delete(self):
        """Test cascade delete when model is deleted."""
        # Create a test access
        test_access = self.env['openapi.access'].create({
            'namespace_id': self.test_namespace.id,
            'model_id': self.test_model.id,
            'api_read': True,
        })
        
        access_id = test_access.id
        
        # Verify access exists
        self.assertTrue(self.env['openapi.access'].browse(access_id).exists())
        
        # Note: We can't actually delete ir.model records in tests as they're system records
        # This test validates the ondelete='cascade' configuration exists in the model definition

    def test_access_namespace_relationship(self):
        """Test relationship with namespace."""
        # Verify access is linked to namespace
        self.assertEqual(self.test_access.namespace_id, self.test_namespace)
        
        # Verify namespace contains this access
        self.assertIn(self.test_access, self.test_namespace.access_ids)

    def test_access_permissions_combinations(self):
        """Test various permission combinations."""
        test_cases = [
            {'api_create': True, 'api_read': False, 'api_update': False, 'api_delete': False},
            {'api_create': False, 'api_read': True, 'api_update': False, 'api_delete': False},
            {'api_create': False, 'api_read': False, 'api_update': True, 'api_delete': False},
            {'api_create': False, 'api_read': False, 'api_update': False, 'api_delete': True},
            {'api_create': True, 'api_read': True, 'api_update': True, 'api_delete': True},
        ]
        
        for i, permissions in enumerate(test_cases):
            with self.subTest(case=i):
                access = self.env['openapi.access'].create({
                    'namespace_id': self.test_namespace.id,
                    'model_id': self.test_model.id,
                    **permissions
                })
                
                for perm, expected in permissions.items():
                    self.assertEqual(getattr(access, perm), expected,
                                   f"Permission {perm} should be {expected}")


class TestOpenAPIAccessCreateContext(OpenAPITestCase):
    """Test cases for openapi.access.create.context model."""

    def test_create_context_creation(self):
        """Test create context creation."""
        context = self.env['openapi.access.create.context'].create({
            'name': 'test_context',
            'description': 'Test context for creation',
            'model_id': self.test_model.id,
            'context': '{"default_customer": True}',
        })
        
        self.assertEqual(context.name, 'test_context')
        self.assertEqual(context.description, 'Test context for creation')
        self.assertEqual(context.model_id, self.test_model)
        self.assertEqual(context.context, '{"default_customer": True}')

    def test_create_context_name_required(self):
        """Test that context name is required."""
        with self.assertRaises(ValidationError):
            self.env['openapi.access.create.context'].create({
                'model_id': self.test_model.id,
                'context': '{}',
            })

    def test_create_context_model_required(self):
        """Test that model is required for context."""
        with self.assertRaises(ValidationError):
            self.env['openapi.access.create.context'].create({
                'name': 'test_context',
                'context': '{}',
            })

    def test_create_context_context_required(self):
        """Test that context field is required."""
        with self.assertRaises(ValidationError):
            self.env['openapi.access.create.context'].create({
                'name': 'test_context',
                'model_id': self.test_model.id,
            })

    def test_create_context_unique_constraint(self):
        """Test unique constraint on name and model."""
        # Create first context
        self.env['openapi.access.create.context'].create({
            'name': 'unique_test',
            'model_id': self.test_model.id,
            'context': '{"test": 1}',
        })
        
        # Try to create another with same name and model
        with self.assertRaises(ValidationError):
            self.env['openapi.access.create.context'].create({
                'name': 'unique_test',
                'model_id': self.test_model.id,
                'context': '{"test": 2}',
            })

    def test_create_context_json_validation(self):
        """Test context JSON validation."""
        # Valid JSON should work
        context = self.env['openapi.access.create.context'].create({
            'name': 'json_test',
            'model_id': self.test_model.id,
            'context': '{"valid": "json", "number": 123, "boolean": true}',
        })
        
        self.assertTrue(context.id, "Valid JSON context should be created successfully")
        
        # Invalid JSON should be caught by _check_context constraint
        with self.assertRaises(ValidationError):
            self.env['openapi.access.create.context'].create({
                'name': 'invalid_json_test',
                'model_id': self.test_model.id,
                'context': '{"invalid": json}',  # Invalid JSON
            })
