from app.utils.responses import success_response, error_response
from app import db
from app.models.test import Test
from app.models.testExercise import TestExercise
from app.models.evaluation import Evaluation
from app.models.participant import Participant
from app.models.evaluationResult import EvaluationResult

from datetime import date


class EvaluationServiceDB:

    def register_test(self, data):
        try:
            # ---------- validacion general ----------
            if not data or not isinstance(data, dict):
                return error_response("Datos inválidos")

            # ---------- validacion del nombre del test ----------
            if "name" not in data or not data["name"].strip():
                return error_response("Por favor ingrese el nombre del test")

            # evitar duplicar tests en la base de datos
            if Test.query.filter_by(name=data["name"].strip()).first():
                return error_response("El test con ese nombre ya existe")

            # ---------- validacion de frecuencia osea de cada que tiempo se ahcen los test ----------
            if "frequency_months" not in data:
                return error_response("Se requiere la frecuencia en meses")

            if not isinstance(data["frequency_months"], int) or data["frequency_months"] <= 0:
                return error_response("Los meses de frecuencia deben ser un número entero positivo")

            # ---------- validacion de ejercicios ----------
            if "exercises" not in data or not isinstance(data["exercises"], list):
                return error_response("Los ejercicios deben ser una lista")

            if len(data["exercises"]) == 0:
                return error_response("At least one exercise is required")

            # evitar ejercicios duplicados dentro del mismo test
            exercise_names = set()

            for ex in data["exercises"]:
                if "name" not in ex or not ex["name"].strip():
                    return error_response("Asignar un nombre a cada ejercicio")

                if "unit" not in ex or not ex["unit"].strip():
                    return error_response("Asignar un nombre a cada ejercicio")

                name_key = ex["name"].strip().lower()
                if name_key in exercise_names:
                    return error_response("Ejercicio repetido")

                exercise_names.add(name_key)

            # ---------- creacion del test ----------
            test = Test(
                name=data["name"].strip(),
                description=data.get("description"),
                frequency_months=data["frequency_months"],
            )

            db.session.add(test)
            db.session.flush()  # Obtiene el ID del test

            # ---------- creacion de ejercicios ----------
            for ex in data["exercises"]:
                exercise = TestExercise(
                    test_id=test.id,
                    name=ex["name"].strip(),
                    unit=ex["unit"].strip()
                )
                db.session.add(exercise)

            db.session.commit()

            return success_response(
                msg="Test creado correctamente",
                data={"test_external_id": test.external_id},
            )

        except Exception as e:
            db.session.rollback()
            return error_response(f"Internal error: {str(e)}")

    def apply_test(self, data):
        try:
            # ---------- validacion general ----------
            if not data or not isinstance(data, dict):
                return error_response("Datos ingresados inválidos")

            # ---------- validacion de participante ----------
            if "participant_external_id" not in data:
                return error_response("Se requiere identificación externa del participante")

            participant = Participant.query.filter_by(
                external_id=data["participant_external_id"]
            ).first()

            if not participant:
                return error_response("Participante no encontrado")

            # ---------- validacion de test ----------
            if "test_external_id" not in data:
                return error_response("Se requiere identificación externa del test")

            test = Test.query.filter_by(
                external_id=data["test_external_id"]
            ).first()

            if not test:
                return error_response("Test no encontrado")

            # ---------- validacion de resusltados ----------
            if "results" not in data or not isinstance(data["results"], list):
                return error_response("Los resultados deben ser una lista")

            if len(data["results"]) == 0:
                return error_response("Se requieren resultados para aplicar el test")

            # ---------- creacion de la evaluacion ----------
            evaluation = Evaluation(
                participant_id=participant.id,
                test_id=test.id,
                date=date.today(),
                general_observations=data.get("general_observations"),
            )

            db.session.add(evaluation)
            db.session.flush()  # Obtiene el ID de la evaluación

            # ejercicios válidos del test
            valid_exercises = {
                ex.external_id: ex.id
                for ex in TestExercise.query.filter_by(test_id=test.id).all()
            }

            used_exercises = set()

            # ---------- validacion y creacion de resultados ----------
            for res in data["results"]:
                if "test_exercise_external_id" not in res:
                    return error_response("Se requiere identificación externa del ejercicio")

                if "value" not in res:
                    return error_response("Se requiere valor del resultado")

                exercise_id = valid_exercises.get(res["test_exercise_external_id"])

                # verifcar que el ejercicio pertenezca al test
                if not exercise_id:
                    return error_response("Ejercicio no pertenece al test aplicado")

                # evitar resultados duplicados
                if exercise_id in used_exercises:
                    return error_response("Resultado repetido para el mismo ejercicio")

                used_exercises.add(exercise_id)

                result = EvaluationResult(
                    evaluation_id=evaluation.id,
                    test_exercise_id=exercise_id,
                    value=res["value"],
                    observation=res.get("observation"),
                )
                db.session.add(result)

            db.session.commit()

            return success_response(
                msg="Test aplicado correctamente",
                data={"evaluation_external_id": evaluation.external_id},
            )

        except Exception as e:
            db.session.rollback()
            return error_response(f"Internal error: {str(e)}")
