from app import db
from app.models.participant import Participant


class ParticipantDAO:
    """Data Access Object para la entidad Participant"""

    def get_all(self):
        """Obtiene todos los participantes"""
        return Participant.query.all()

    def get_by_id(self, participant_id):
        """Obtiene un participante por su ID"""
        return Participant.query.get(participant_id)

    def get_by_dni(self, dni):
        """Obtiene un participante por su DNI"""
        return Participant.query.filter_by(dni=dni).first()

    def get_by_correo(self, correo):
        """Obtiene un participante por su correo"""
        return Participant.query.filter_by(correo=correo).first()

    def create(self, nombre, apellido, edad, dni, telefono, correo, direccion, estado, tipo):
        """Crea un nuevo participante"""
        nuevo = Participant(
            nombre=nombre,
            apellido=apellido,
            edad=edad,
            dni=dni,
            telefono=telefono,
            correo=correo,
            direccion=direccion,
            estado=estado,
            tipo=tipo
        )
        db.session.add(nuevo)
        db.session.commit()
        return nuevo

    def update(self, participant_id, **kwargs):
        """Actualiza un participante existente"""
        participante = self.get_by_id(participant_id)
        if participante:
            for key, value in kwargs.items():
                if hasattr(participante, key) and value is not None:
                    setattr(participante, key, value)
            db.session.commit()
        return participante

    def delete(self, participant_id):
        """Elimina un participante"""
        participante = self.get_by_id(participant_id)
        if participante:
            db.session.delete(participante)
            db.session.commit()
            return True
        return False
