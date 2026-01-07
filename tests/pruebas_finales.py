import unittest
import requests
import json
import uuid
import random
import string

BASE_URL = "http://127.0.0.1:5000/api"

class TestFinales(unittest.TestCase):
    def _generate_numeric_string(self, length):
        return ''.join(random.choices(string.digits, k=length))
    
    def setUp(self):
        self.headers = {"Content-Type": "application/json"}
        # Precondición: Usuario administrador debe existir
        self.admin_email = "admin@kallpa.com"
        self.admin_password = "123456" 
        self.token = None

    def _get_auth_headers(self):
        if not self.token:
             payload = {"email": self.admin_email, "password": self.admin_password}
             resp = requests.post(f"{BASE_URL}/auth/login", json=payload)
             if resp.status_code == 200:
                 self.token = resp.json()["token"]
        
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def test_tc_01_register_participant(self):
        """TC-01: Registrar Participante - Adulto Funcional Exitoso (Antes TC-05)"""
        # Precondiciones: Token válido, datos únicos
        
        # Generar DNI válido que inicie con 0 (no secuencial)
        unique_suffix = str(uuid.uuid4().int)[:9]
        unique_dni = f"0{unique_suffix}"
        
        payload = {
            "firstName": "Juan",
            "lastName": "Pérez",
            "dni": unique_dni,
            "age": 25,
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE",
            "phone": "0991234567",
            "email": f"juan.{unique_dni}@test.com",
            "address": "Calle Falsa 123"
        }
        
        headers = self._get_auth_headers()
        # Verificar que se obtuvo el token (Autenticación exitosa)
        self.assertTrue(headers.get("Authorization"), "No se pudo obtener el token de autorización")

        response = requests.post(f"{BASE_URL}/save-participants", json=payload, headers=headers)
        
        # Postcondición: Registro exitoso (200 o 201)
        self.assertIn(response.status_code, [200, 201], f"TC-01: Falló registro. Status: {response.status_code}, Resp: {response.text}")
        
        # Validar estructura de respuesta
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("participant_external_id", data["data"])
        
        print("TC-01: Registro Participante Exitoso - Correcto")

    def test_tc_02_register_duplicate(self):
        """TC-02: Registrar Participante - Validación Duplicado (Antes TC-06)"""
        headers = self._get_auth_headers()
        self.assertTrue(headers.get("Authorization"), "No se pudo obtener el token de autorización")
        
        # DNI válido con todos los campos requeridos
        unique_suffix = str(uuid.uuid4().int)[:9]
        dni = f"0{unique_suffix}"
        
        payload_1 = {
            "firstName": "Ana",
            "lastName": "Loja",
            "dni": dni,
            "age": 22,
            "address": "Calle Test",
            "phone": "0998877665",
            "email": f"ana{dni}@test.com",
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE"
        }
        
        # Paso 1: Primer registro (Precondición para el test de duplicado)
        resp1 = requests.post(f"{BASE_URL}/save-participants", json=payload_1, headers=headers)
        self.assertIn(resp1.status_code, [200, 201], "Fallo en la precondición: No se pudo crear el primer registro")

        # Paso 2: Intento de registro duplicado
        response = requests.post(f"{BASE_URL}/save-participants", json=payload_1, headers=headers)
        
        # Validar que rechace el duplicado
        if response.status_code == 200 or response.status_code == 201:
             print("TC-02 WARNING: El sistema permitió duplicado (puede ser actualización).")
             # Dependiendo de la lógica de negocio, esto podría ser un fallo
             self.fail("TC-02: El sistema permitió registrar un duplicado")
        else:
             self.assertEqual(response.status_code, 400, "TC-02: Debería reportar error de duplicado")
             resp_json = response.json()
             self.assertIn("data", resp_json)
             # Verificar que los errores sean específicos de duplicidad
             logging_err = resp_json.get("data", {})
             self.assertTrue("dni" in logging_err or "email" in logging_err, "Debe indicar error en DNI o Email")
             print(f"TC-02: Validación Duplicado - Error recibido: {response.text} - Correcto")

    def test_tc_03_registro_exitoso_medidas_antropometricas(self):
        """TC-03: Registro de medidas antropometricas - Registro Exitoso"""
        unique_id = str(uuid.uuid4())[:8]
        participant_payload = {
            "firstName": "Carlos",
            "lastName": "Lopez",
            "dni": f"10{self._generate_numeric_string(8)}",
            "age": 25,
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE",
            "phone": "0999999999",
            "email": f"carlos{unique_id}@test.com",
            "address": "Av. Siempre Viva"
        }

        response_participant = requests.post(
            f"{BASE_URL}/save-participants",
            json=participant_payload,
            headers=self._get_auth_headers()
        )

        self.assertIn(response_participant.status_code, [200, 201])

        participant_external_id = response_participant.json()["data"]["participant_external_id"]

        assessment_payload = {
            "participant_external_id": participant_external_id,
            "weight": 70,
            "height": 1.75,
            "waistPerimeter": 80,
            "wingspan": 170,
            "date": "2025-01-05"
        }

        response_assessment = requests.post(
            f"{BASE_URL}/save-assessment",
            json=assessment_payload,
            headers=self._get_auth_headers()
        )
        if response_assessment.status_code != 200:
            print("Error al registrar medidas (TC-03):", response_assessment.json())
        else:
            data = response_assessment.json()["data"]
            print("Registro de Medidas Exitoso (TC-03):", data)

    def test_tc_04_registro_medidas_altura_fuera_de_rango(self):
        """TC-04: Registro de medidas antropométricas - Altura fuera de rango"""

        unique_id = str(uuid.uuid4())[:8]
        participant_payload = {
            "firstName": "Luis",
            "lastName": "Gomez",
            "dni": f"12{self._generate_numeric_string(8)}",
            "age": 28,
            "program": "FUNCIONAL",
            "type": "ESTUDIANTE",
            "phone": "0997777777",
            "email": f"luis{unique_id}@test.com",
            "address": "Av Central"
        }

        response_participant = requests.post(
            f"{BASE_URL}/save-participants",
            json=participant_payload,
            headers=self._get_auth_headers()
        )

        self.assertIn(response_participant.status_code, [200, 201])

        participant_external_id = response_participant.json()["data"]["participant_external_id"]

        # Altura completamente inválida
        assessment_payload = {
            "participant_external_id": participant_external_id,
            "weight": 70,
            "height": 3000,  #Valor irreal
            "waistPerimeter": 80,
            "wingspan": 170,
            "date": "2025-01-05"
        }

        response_assessment = requests.post(
            f"{BASE_URL}/save-assessment",
            json=assessment_payload,
            headers=self._get_auth_headers()
        )
        if response_assessment.status_code != 200:
            print("Error al registrar medidas (TC-04):", response_assessment.json())
        else:
            data = response_assessment.json()["data"]
            print("Registro de Medidas Exitoso (TC-04):", data)

if __name__ == "__main__":
    unittest.main(verbosity=2)
