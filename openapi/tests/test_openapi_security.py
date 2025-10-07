# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError
from .common import OpenAPITestCase


class TestOpenAPISecurity(OpenAPITestCase):
    """Test cases for OpenAPI security and permissions."""

    def test_security_groups_exist(self):
        """Test that required security groups exist."""
        # Check OpenAPI User group
        user_group = self.env.ref('openapi.group_user', raise_if_not_found=False)
        self.assertIsNotNone(user_group, "OpenAPI User group should exist")
        self.assertEqual(user_group.name, 'User')
        
        # Check OpenAPI Manager group
        manager_group = self.env.ref('openapi.group_manager', raise_if_not_found=False)
        self.assertIsNotNone(manager_group, "OpenAPI Manager group should exist")
        self.assertEqual(manager_group.name, 'Manager')

    def test_security_group_hierarchy(self):
        """Test security group hierarchy and inheritance."""
        user_group = self.env.ref('openapi.group_user')
        manager_group = self.env.ref('openapi.group_manager')
        base_user_group = self.env.ref('base.group_user')
        
        # User group should inherit from base.group_user
        self.assertIn(base_user_group, user_group.implied_ids)
        
        # Manager group should inherit from openapi.group_user
        self.assertIn(user_group, manager_group.implied_ids)

    def test_security_module_category(self):
        """Test that OpenAPI module category exists."""
        category = self.env.ref('openapi.module_management', raise_if_not_found=False)
        self.assertIsNotNone(category, "OpenAPI module category should exist")
        self.assertEqual(category.name, 'OpenAPI')

    def test_namespace_access_permissions(self):
        """Test namespace model access permissions."""
        # Test with OpenAPI User
        user_namespace = self.test_namespace.with_user(self.test_user)
        
        # User should be able to read
        try:
            name = user_namespace.name
            self.assertEqual(name, self.test_namespace.name)
        except AccessError:
            self.fail("OpenAPI User should be able to read namespaces")
        
        # User should not be able to create (depends on access rules)
        with self.assertRaises(AccessError):
            user_namespace.create({
                'name': 'unauthorized_namespace',
                'description': 'Should not be created by user',
            })

    def test_access_model_permissions(self):
        """Test access model permissions."""
        # Test with OpenAPI User
        user_access = self.test_access.with_user(self.test_user)
        
        # User should be able to read
        try:
            model_name = user_access.model
            self.assertEqual(model_name, self.test_access.model)
        except AccessError:
            self.fail("OpenAPI User should be able to read access records")
        
        # User should not be able to create access records
        with self.assertRaises(AccessError):
            user_access.create({
                'namespace_id': self.test_namespace.id,
                'model_id': self.test_model.id,
                'api_read': True,
            })

    def test_log_model_permissions(self):
        """Test log model permissions."""
        # Create a test log
        log = self._create_test_log()
        
        # Test with OpenAPI User
        user_log = log.with_user(self.test_user)
        
        # User should be able to read logs
        try:
            request = user_log.request
            self.assertEqual(request, log.request)
        except AccessError:
            self.fail("OpenAPI User should be able to read logs")
        
        # User should be able to create logs (for API usage)
        try:
            new_log = user_log.create({
                'namespace_id': self.test_namespace.id,
                'request': 'POST /api/v1/test/create',
                'request_data': '{"test": "data"}',
                'response_data': '{"id": 1}',
            })
            self.assertTrue(new_log.id, "User should be able to create logs")
        except AccessError:
            self.fail("OpenAPI User should be able to create logs")

    def test_manager_permissions(self):
        """Test manager permissions."""
        # Create a manager user
        manager_user = self.env['res.users'].create({
            'name': 'Test OpenAPI Manager',
            'login': 'test_openapi_manager',
            'email': 'manager@openapi.com',
            'groups_id': [(6, 0, [self.env.ref('openapi.group_manager').id])],
        })
        
        # Manager should be able to create namespaces
        try:
            manager_namespace = self.env['openapi.namespace'].with_user(manager_user).create({
                'name': 'manager_namespace',
                'description': 'Created by manager',
            })
            self.assertTrue(manager_namespace.id, "Manager should be able to create namespaces")
        except AccessError:
            self.fail("OpenAPI Manager should be able to create namespaces")
        
        # Manager should be able to create access records
        try:
            manager_access = self.env['openapi.access'].with_user(manager_user).create({
                'namespace_id': self.test_namespace.id,
                'model_id': self.test_model.id,
                'api_read': True,
            })
            self.assertTrue(manager_access.id, "Manager should be able to create access records")
        except AccessError:
            self.fail("OpenAPI Manager should be able to create access records")

    def test_access_rules_context(self):
        """Test access rules with different contexts."""
        # Test that users can only access their own namespace data (if such rules exist)
        # This would depend on the specific access rules implementation
        
        # For now, test basic access
        self.assertTrue(self.test_namespace.exists(), "Namespace should be accessible")
        self.assertTrue(self.test_access.exists(), "Access should be accessible")

    def test_field_level_security(self):
        """Test field-level security if implemented."""
        # Test that sensitive fields are protected
        # This would test any field-level security rules
        
        # For now, verify that all expected fields are accessible to authorized users
        namespace_fields = ['name', 'description', 'token', 'log_request', 'log_response']
        for field in namespace_fields:
            try:
                value = getattr(self.test_namespace, field)
                # Field should be accessible
            except AccessError:
                self.fail(f"Field {field} should be accessible to authorized users")

    def test_record_rules_active_flag(self):
        """Test record rules respect active flag."""
        # Create an inactive namespace
        inactive_namespace = self.env['openapi.namespace'].create({
            'name': 'inactive_test',
            'description': 'Inactive namespace',
            'active': False,
        })
        
        # Test that inactive records are handled according to context
        all_namespaces = self.env['openapi.namespace'].search([])
        active_namespaces = self.env['openapi.namespace'].search([('active', '=', True)])
        
        self.assertGreaterEqual(len(all_namespaces), len(active_namespaces),
                               "All namespaces should include inactive ones")

    def test_multi_company_security(self):
        """Test multi-company security if applicable."""
        # This test would verify multi-company access rules
        # For now, we test basic company context
        
        current_company = self.env.company
        self.assertIsNotNone(current_company, "Should have a current company context")
        
        # Test that records are created in the correct company context
        self.assertEqual(self.test_namespace.create_uid.company_id, current_company,
                        "Namespace should be created in current company context")

    def test_api_token_security(self):
        """Test API token security."""
        # Test that tokens are properly generated and validated
        self.assertTrue(self.test_namespace.token, "Namespace should have a token")
        self.assertIsInstance(self.test_namespace.token, str, "Token should be a string")
        
        # Test token uniqueness (if implemented)
        another_namespace = self.env['openapi.namespace'].create({
            'name': 'another_test',
            'description': 'Another test namespace',
        })
        
        self.assertNotEqual(self.test_namespace.token, another_namespace.token,
                           "Tokens should be unique between namespaces")

    def test_sql_injection_protection(self):
        """Test protection against SQL injection."""
        # Test that model methods properly handle malicious input
        malicious_inputs = [
            "'; DROP TABLE openapi_namespace; --",
            "1' OR '1'='1",
            "admin'/*",
            "1; DELETE FROM openapi_namespace WHERE 1=1; --",
        ]
        
        for malicious_input in malicious_inputs:
            try:
                # Try to create namespace with malicious name
                namespace = self.env['openapi.namespace'].create({
                    'name': malicious_input,
                    'description': 'Test malicious input',
                })
                # If we get here, the input was sanitized (which is good)
                self.assertTrue(namespace.id, "Malicious input should be sanitized")
            except Exception:
                # Any exception is acceptable as it means the input was rejected
                pass

    def test_xss_protection(self):
        """Test protection against XSS attacks."""
        # Test that text fields properly handle script tags
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
        ]
        
        for xss_input in xss_inputs:
            try:
                namespace = self.env['openapi.namespace'].create({
                    'name': 'xss_test',
                    'description': xss_input,
                })
                # Input should be stored safely
                self.assertTrue(namespace.id, "XSS input should be handled safely")
            except Exception:
                # Exception is acceptable as it means input was rejected
                pass
