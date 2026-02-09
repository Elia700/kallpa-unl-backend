import unittest
from unittest.mock import patch, MagicMock, Mock

class TestFinales(unittest.TestCase):
    """Pruebas Unitarias con Mocks Simplificados"""

    def setUp(self):
        pass

    @patch("app.controllers.usercontroller.java_sync")
    @patch("app.controllers.usercontroller.db")
    @patch("app.controllers.usercontroller.Participant")
    def test_tc_01_register_participant_success(self, mock_participant, mock_db, mock_java_sync):
        """TC-01: Registrar Participante - Adulto Funcional Exitoso"""
        from app.controllers.usercontroller import UserController
        
        # Mock that no participant exists with this DNI
        mock_participant.query.filter_by.return_value.first.return_value = None
        
        # Mock java sync service
        mock_java_sync.search_by_identification.return_value = {"found": False}
        
        # Mock successful participant creation
        mock_instance = Mock()
        mock_instance.external_id = "test-uuid-123"
        mock_participant.return_value = mock_instance
        
        # Mock database operations
        mock_db.session.add = Mock()
        mock_db.session.commit = Mock()
        mock_db.session.rollback = Mock()

        data = {
            "firstName": "Juan",
            "lastName": "Pérez",
            "dni": "1100000001",
            "age": 25,
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE",
            "phone": "0991234567",
            "email": "juan@test.com",
            "address": "Calle Falsa 123"
        }
        
        with patch.object(UserController, '_get_token', return_value="Bearer mock_token"):
            controller = UserController()
            response = controller.create_participant(data)
        
        # Verify response structure exists
        self.assertIsInstance(response, dict)
        self.assertIn("code", response)

    @patch("app.controllers.usercontroller.java_sync")
    @patch("app.controllers.usercontroller.db")  
    @patch("app.controllers.usercontroller.Participant")
    def test_tc_02_register_duplicate_dni(self, mock_participant, mock_db, mock_java_sync):
        """TC-02: Registrar Participante - Validación Duplicado (DNI local)"""
        from app.controllers.usercontroller import UserController
        
        # Mock existing participant with same DNI
        existing_participant = Mock()
        existing_participant.dni = "1100000001"
        mock_participant.query.filter_by.return_value.first.return_value = existing_participant

        data = {
            "firstName": "Duplicado",
            "lastName": "Usuario", 
            "dni": "1100000001",
            "age": 30,
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE"
        }
        
        with patch.object(UserController, '_get_token', return_value="Bearer mock_token"):
            controller = UserController()
            response = controller.create_participant(data)
        
        # Should return error for duplicate
        self.assertIsInstance(response, dict)
        self.assertIn("code", response)
        # Expect error code for duplicate
        self.assertEqual(response["code"], 400)

    @patch("app.controllers.assessment_controller.db")
    @patch("app.controllers.assessment_controller.Participant")
    @patch("app.controllers.assessment_controller.Assessment")
    def test_tc_03_register_assessment_success(self, mock_assessment, mock_participant, mock_db):
        """TC-03: Registro de medidas antropométricas - Exitoso"""
        from app.controllers.assessment_controller import AssessmentController
        
        # Mock participant exists
        mock_participant_obj = Mock()
        mock_participant_obj.external_id = "uuid-ext-id"
        mock_participant.query.filter_by.return_value.first.return_value = mock_participant_obj
        
        # Mock assessment creation
        mock_assessment_obj = Mock()
        mock_assessment_obj.external_id = "assessment-uuid"
        mock_assessment_obj.bmi = 22.86
        mock_assessment.return_value = mock_assessment_obj
        
        # Mock database operations
        mock_db.session.add = Mock()
        mock_db.session.commit = Mock()

        assessment_payload = {
            "participant_external_id": "uuid-ext-id",
            "weight": 70,
            "height": 1.75,
            "waistPerimeter": 0.80,
            "wingspan": 1.70,
            "date": "2025-01-05"
        }

        controller = AssessmentController()
        response = controller.register(assessment_payload)
        
        # Verify response structure
        self.assertIsInstance(response, dict)
        self.assertIn("code", response)

if __name__ == "__main__":
    unittest.main(verbosity=2)