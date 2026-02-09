import unittest
import json
import uuid
import random
import string
from datetime import datetime
from unittest.mock import patch, MagicMock
from tests.test_integration.base_test import BaseTestCase

class TestAttendanceScenarios(BaseTestCase):
    
    def setUp(self):
        super().setUp()
        self.headers = {"Content-Type": "application/json", "Authorization": "Bearer mock_token"}
        self.admin_email = "admin@kallpa.com"
        self.admin_password = "123456" 
        self.token = "mock_token_123"
        self.created_participant_id = None
        self.created_schedule_id = None

    def _generate_numeric_string(self, length):
        return ''.join(random.choices(string.digits, k=length))

    @patch('app.utils.jwt_required.jwt_required')
    @patch('app.routes.attendance_routes.AttendanceController')
    def test_tc_01_create_schedule_success(self, mock_controller, mock_jwt):
        """TC-01: Crear Horario/Sesión - Caso exitoso"""
        # Mock JWT middleware
        mock_jwt.return_value = lambda f: f
        
        # Mock controller response
        mock_instance = mock_controller.return_value
        mock_instance.create_schedule_v2.return_value = {
            "code": 201,
            "msg": "Horario creado exitosamente",
            "data": {"external_id": "schedule-123", "name": "Sesión Test"}
        }
        
        unique_suffix = str(uuid.uuid4())[:4]
        payload = {
            "name": f"Sesión Test {unique_suffix}",
            "startTime": "08:00",
            "endTime": "10:00",
            "program": "FUNCIONAL",
            "maxSlots": 20,
            "description": "Sesión de prueba automatizada",
            "dayOfWeek": "MONDAY"
        }
        
        response = self.client.post(
            '/api/attendance/v2/public/schedules',
            data=json.dumps(payload),
            headers=self.headers
        )
        
        self.assertIn(response.status_code, [200, 201])
        # Verify controller was called
        mock_instance.create_schedule_v2.assert_called_once()

    @patch('app.utils.jwt_required.jwt_required')
    @patch('app.routes.attendance_routes.AttendanceController')
    def test_tc_06_create_schedule_invalid_time_format(self, mock_controller, mock_jwt):
        """TC-06: Crear Horario - Formato de hora inválido"""
        mock_jwt.return_value = lambda f: f
        
        mock_instance = mock_controller.return_value
        mock_instance.create_schedule_v2.return_value = {
            "code": 400,
            "msg": "Formato de hora inválido",
            "errors": {"startTime": "Formato inválido"}
        }
        
        payload = {
            "name": "Sesión con hora inválida",
            "startTime": "25:00",  # Hora inválida
            "endTime": "10:00",
            "program": "FUNCIONAL",
            "maxSlots": 20,
            "dayOfWeek": "MONDAY"
        }
        
        response = self.client.post(
            '/api/attendance/v2/public/schedules',
            data=json.dumps(payload),
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400)

    @patch('app.utils.jwt_required.jwt_required')
    @patch('app.routes.attendance_routes.AttendanceController')
    def test_tc_07_create_schedule_start_after_end(self, mock_controller, mock_jwt):
        """TC-07: Crear Horario - Inicio después de Fin (Negativo)"""
        mock_jwt.return_value = lambda f: f
        
        mock_instance = mock_controller.return_value
        mock_instance.create_schedule_v2.return_value = {
            "code": 400,
            "msg": "La hora de inicio no puede ser posterior a la hora de fin",
            "errors": {"time": "Rango de tiempo inválido"}
        }
        
        payload = {
            "name": "Sesión con tiempo inválido",
            "startTime": "15:00",  
            "endTime": "10:00",   # Fin antes que inicio
            "program": "FUNCIONAL",
            "maxSlots": 20,
            "dayOfWeek": "MONDAY"
        }
        
        response = self.client.post(
            '/api/attendance/v2/public/schedules',
            data=json.dumps(payload),
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400)

    @patch('app.utils.jwt_required.jwt_required')
    @patch('app.routes.attendance_routes.AttendanceController')
    def test_tc_08_create_schedule_invalid_day(self, mock_controller, mock_jwt):
        """TC-08: Crear Horario - Día Inválido (Negativo)"""
        mock_jwt.return_value = lambda f: f
        
        mock_instance = mock_controller.return_value
        mock_instance.create_schedule_v2.return_value = {
            "code": 400,
            "msg": "Día de la semana inválido",
            "errors": {"dayOfWeek": "Valor no permitido"}
        }
        
        payload = {
            "name": "Sesión día inválido",
            "startTime": "08:00",
            "endTime": "10:00",
            "program": "FUNCIONAL",
            "maxSlots": 20,
            "dayOfWeek": "INEXISTENTE"  # Día inválido
        }
        
        response = self.client.post(
            '/api/attendance/v2/public/schedules',
            data=json.dumps(payload),
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400)

    @patch('app.utils.jwt_required.jwt_required')
    @patch('app.routes.attendance_routes.AttendanceController')
    def test_tc_11_negative_max_slots(self, mock_controller, mock_jwt):
        """TC-11: Slots máximos negativos"""
        mock_jwt.return_value = lambda f: f
        
        mock_instance = mock_controller.return_value
        mock_instance.create_schedule_v2.return_value = {
            "code": 400,
            "msg": "El número de slots debe ser positivo",
            "errors": {"maxSlots": "Debe ser mayor a 0"}
        }
        
        payload = {
            "name": "Sesión slots negativos",
            "startTime": "08:00",
            "endTime": "10:00",
            "program": "FUNCIONAL",
            "maxSlots": -5,  # Slots negativos
            "dayOfWeek": "MONDAY"
        }
        
        response = self.client.post(
            '/api/attendance/v2/public/schedules',
            data=json.dumps(payload),
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400)

    def test_tc_21_expired_or_invalid_token(self):
        """TC-21: Token inválido o expirado"""
        headers = {"Content-Type": "application/json", "Authorization": "Bearer invalid_token"}
        
        payload = {
            "name": "Sesión token inválido",
            "startTime": "08:00",
            "endTime": "10:00",
            "program": "FUNCIONAL",
            "maxSlots": 20,
            "dayOfWeek": "MONDAY"
        }
        
        response = self.client.post(
            '/api/attendance/v2/public/schedules',
            data=json.dumps(payload),
            headers=headers
        )
        
        self.assertEqual(response.status_code, 401)

    @patch('app.utils.jwt_required.jwt_required')
    @patch('app.routes.user_routes.UserController')
    def test_tc_18_register_participant_success(self, mock_controller, mock_jwt):
        """TC-18: Registrar participante - Caso exitoso"""
        mock_jwt.return_value = lambda f: f
        
        mock_instance = mock_controller.return_value
        mock_instance.create_participant.return_value = {
            "code": 201,
            "msg": "Participante registrado correctamente",
            "data": {"participant_external_id": "part-123"}
        }
        
        payload = {
            "firstName": "Juan",
            "lastName": "Pérez", 
            "dni": f"10{self._generate_numeric_string(8)}",
            "age": 25,
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE",
            "phone": "0991234567",
            "email": f"test.{uuid.uuid4()}@example.com",
            "address": "Calle Test 123"
        }
        
        response = self.client.post(
            '/api/save-participants',
            data=json.dumps(payload),
            headers=self.headers
        )
        
        self.assertIn(response.status_code, [200, 201])

if __name__ == '__main__':
    unittest.main()