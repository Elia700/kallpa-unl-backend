from app.dao.participant_dao import ParticipantDAO
from app.schemas.participant_schema import participant_schema, participants_schema


class UserServiceDB:
    def __init__(self):
        self.dao = ParticipantDAO()

    def get_all_users(self):
        result = self.dao.get_all()
        return participants_schema.dump(result)

    def create_user(self, data):
        try:
            nuevo_participante = self.dao.create(
                nombre=data.get('nombre'),
                apellido=data.get('apellido'),
                edad=data.get('edad'),
                dni=data.get('dni'),
                telefono=data.get('telefono'),
                correo=data.get('correo'),
                direccion=data.get('direccion'),
                estado="ACTIVO",
                tipo=data.get('tipo', 'EXTERNO')
            )
            return {
                "status": "ok",
                "msg": "Participante registrado exitosamente",
                "data": participant_schema.dump(nuevo_participante)
            }, 201
        except Exception as e:
            return {
                "status": "error",
                "msg": f"Error al registrar: {str(e)}"
            }, 400
