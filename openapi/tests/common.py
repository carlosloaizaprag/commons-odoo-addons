# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class OpenAPITestCase(TransactionCase):
    """Base test case for OpenAPI module tests."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        super().setUpClass()
        
        # Create test namespace
        cls.test_namespace = cls.env['openapi.namespace'].create({
            'name': 'test_namespace',
            'description': 'Test namespace for unit tests',
            'log_request': 'info',
            'log_response': 'debug',
        })
        
        # Create test model for access testing
        cls.test_model = cls.env['ir.model'].search([('model', '=', 'res.partner')], limit=1)
        
        # Create test access
        cls.test_access = cls.env['openapi.access'].create({
            'namespace_id': cls.test_namespace.id,
            'model_id': cls.test_model.id,
            'api_create': True,
            'api_read': True,
            'api_update': True,
            'api_delete': False,
            'api_public_methods': False,
        })
        
        # Create test user with OpenAPI permissions
        cls.test_user = cls.env['res.users'].create({
            'name': 'Test OpenAPI User',
            'login': 'test_openapi_user',
            'email': 'test@openapi.com',
            'groups_id': [(6, 0, [cls.env.ref('openapi.group_user').id])],
        })

    def _create_test_log(self, request_data=None, response_data=None):
        """Helper method to create test log entries."""
        return self.env['openapi.log'].create({
            'namespace_id': self.test_namespace.id,
            'request': 'GET /api/v1/test_namespace/test',
            'request_data': request_data or '{"test": "data"}',
            'response_data': response_data or '{"result": "success"}',
        })

    def _get_test_swagger_spec(self):
        """Helper method to get test swagger specification."""
        return {
            "swagger": "2.0",
            "info": {
                "title": "Test API",
                "version": "1.0"
            },
            "host": "localhost:8090",
            "basePath": f"/api/v1/{self.test_namespace.name}",
            "schemes": ["http"],
            "consumes": ["application/json"],
            "produces": ["application/json"],
            "paths": {},
            "definitions": {}
        }
