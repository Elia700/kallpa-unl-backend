import unittest
from unittest.mock import patch, Mock
from tests.test_integration.base_test import BaseTestCase
from app.controllers.evaluation_controller import EvaluationController


class TestEvaluationController(BaseTestCase):
    """Tests unitarios para controlador de evaluaciones - Cristian"""

    def setUp(self):
        super().setUp()
        self.controller = EvaluationController()

    @patch('app.controllers.evaluation_controller.db.session')
    @patch('app.utils.validations.evaluation_validation.Test')  # Patch the validation module too
    @patch('app.controllers.evaluation_controller.Test')
    def test_tc_02_registro_test_exitoso(self, mock_test, mock_validation_test, mock_session):
        """TC-02: Registro de Test - Test creado correctamente"""
        # Mock Test.query for duplicate check in both locations
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_test.query = mock_query
        mock_validation_test.query = mock_query
        
        mock_session.add = Mock()
        mock_session.flush = Mock()
        mock_session.commit = Mock()
        
        # Mock the created test
        fake_test = Mock()
        fake_test.id = 1
        fake_test.external_id = "test-123"
        fake_test.name = "test de hipertrofia"  
        fake_test.frequency_months = 3
        fake_test.description = "Primer test de hipertrofia"
        
        mock_test.return_value = fake_test

        data = {
            "name": "Test de hipertrofia",
            "description": "Primer test de hipertrofia",
            "frequency_months": 3,
            "exercises": [
                {"name": "Press Banca", "unit": "repeticiones"},
            ],
        }

        result = self.controller.register(data)

        self.assertEqual(result["code"], 200)
        self.assertEqual(result["status"], "ok") 
        self.assertIn("test_external_id", result["data"])

    @patch('app.controllers.evaluation_controller.db.session')
    def test_tc_03_registro_test_sin_ejercicios(self, mock_session):
        """TC-03: Registro de Test - Falla por ejercicios vacíos"""
        data = {
            "name": "Test sin ejercicios", 
            "description": "Test inválido",
            "frequency_months": 3,
            "exercises": []  # Empty exercises array
        }

        result = self.controller.register(data)

        self.assertEqual(result["code"], 400)
        self.assertEqual(result["status"], "error")
        # Check that the error is related to exercises validation
        self.assertTrue(
            "exercises" in str(result["data"]) or 
            "ejercicio" in str(result["data"])
        )

    @patch('app.controllers.evaluation_controller.db.session')  
    def test_tc_04_registro_test_ejercicios_invalidos(self, mock_session):
        """TC-04: Registro de Test - Falla por ejercicios con campos vacíos"""
        data = {
            "name": "Test con ejercicios inválidos",
            "description": "Test con ejercicios mal formados", 
            "frequency_months": 3,
            "exercises": [
                {"name": "", "unit": ""},  # Invalid empty fields
                {"name": "Valid Exercise", "unit": ""}  # Partially invalid
            ]
        }

        result = self.controller.register(data)

        self.assertEqual(result["code"], 400)
        self.assertEqual(result["status"], "error")
        # Verify that validation catches the empty fields
        self.assertIn("validation_errors", result["data"])


if __name__ == '__main__':
    unittest.main()
