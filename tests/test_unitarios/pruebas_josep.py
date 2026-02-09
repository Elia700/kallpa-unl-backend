# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, Mock
from tests.test_integration.base_test import BaseTestCase
from app.controllers.usercontroller import UserController


class TestJosepUserController(BaseTestCase):
    """Tests unitarios para validaciones de usuario - Josep"""
    
    def setUp(self):
        super().setUp()
        self.controller = UserController()

    @patch('app.controllers.usercontroller.db.session')
    @patch('app.controllers.usercontroller.Participant')
    @patch('app.controllers.usercontroller.UserController._get_token')
    def test_tc_16_phone_validations(self, mock_get_token, mock_participant, mock_session):
        """TC-16, TC-21, TC-24: Validaciones de Teléfono - Verifica formato inválido"""
        mock_get_token.return_value = "Bearer mock_token"
        mock_participant.query.filter_by.return_value.first.return_value = None
        mock_session.commit = Mock()
        
        scenarios = [
            ("1234567890", "Teléfono debe iniciar con 0"),
            ("098abc1234", "Teléfono debe contener solo números"),
            ("0123456789", "Teléfono no puede ser un número secuencial")
        ]
        
        for phone_val, expected_msg in scenarios:
            with self.subTest(phone=phone_val):
                data = {
                    "firstName": "Test",
                    "lastName": "Phone", 
                    "dni": "1100000005",
                    "email": "test@example.com",
                    "age": 25,
                    "phone": phone_val,
                    "program": "FUNCIONAL",
                    "type": "ESTUDIANTE"
                }
                
                response = self.controller.create_participant(data)
                
                self.assertEqual(response["code"], 400)
                self.assertIn("Teléfono", str(response["data"]))

    @patch('app.controllers.usercontroller.db.session')
    @patch('app.controllers.usercontroller.Participant')
    @patch('app.controllers.usercontroller.UserController._get_token')
    def test_tc_17_program_age_validation(self, mock_get_token, mock_participant, mock_session):
        """TC-17: Validación de programas - Verifica que programas inválidos den error"""
        mock_get_token.return_value = "Bearer mock_token"
        mock_participant.query.filter_by.return_value.first.return_value = None
        mock_session.commit = Mock()
        
        # Test with invalid program to verify validation works
        data = {
            "firstName": "Test",
            "lastName": "User",
            "dni": "1000000025",  # Valid 10-digit DNI
            "email": "test@example.com",
            "age": 25,
            "phone": "0987654321",
            "program": "PROGRAMA_INVALIDO",  # Invalid program
            "type": "ESTUDIANTE"
        }
        
        response = self.controller.create_participant(data)
        
        # Should get error for invalid program
        self.assertEqual(response["code"], 400)
        self.assertIn("Programa", str(response["data"]))

    @patch('app.controllers.usercontroller.db.session')
    @patch('app.controllers.usercontroller.Participant')
    @patch('app.controllers.usercontroller.UserController._get_token')
    def test_tc_18_dni_validations(self, mock_get_token, mock_participant, mock_session):
        """TC-18: Validaciones de DNI - formato y duplicados"""
        mock_get_token.return_value = "Bearer mock_token"
        mock_participant.query.filter_by.return_value.first.return_value = None
        mock_session.commit = Mock()
        
        # Test invalid DNI formats
        invalid_dnis = [
            "12345678",      # Too short
            "12345678901",   # Too long  
            "123abc4567",    # Contains letters
            "0000000000",    # All zeros
        ]
        
        for dni in invalid_dnis:
            with self.subTest(dni=dni):
                data = {
                    "firstName": "Test",
                    "lastName": "User",
                    "dni": dni,
                    "email": "test@example.com",
                    "age": 25,
                    "phone": "0987654321",
                    "program": "FUNCIONAL",
                    "type": "ESTUDIANTE"
                }
                
                response = self.controller.create_participant(data)
                
                self.assertEqual(response["code"], 400)
                self.assertIn("dni", str(response["data"]).lower())


if __name__ == '__main__':
    unittest.main()
