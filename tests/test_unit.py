import hashlib
import os
from datetime import date, time
from database import Medico, Agendamento, session


def gerar_hash(senha, salt_hex):
    salt = bytes.fromhex(salt_hex)
    return hashlib.sha256(salt + senha.encode()).hexdigest()


def test_hash_senha_igual():
    senha = "abc123"
    salt = os.urandom(16).hex()

    h1 = gerar_hash(senha, salt)
    h2 = gerar_hash(senha, salt)

    assert h1 == h2


def test_hash_senha_diferente():
    senha = "abc123"
    salt1 = os.urandom(16).hex()
    salt2 = os.urandom(16).hex()

    h1 = gerar_hash(senha, salt1)
    h2 = gerar_hash(senha, salt2)

    assert h1 != h2


def test_criar_agendamento():
    ag = Agendamento(
        nome="Otávio",
        idade=21,
        convenio="UNIMED",
        especialidade="Cardiologia",
        data=date(2025, 1, 1),
        hora=time(8, 30),
        email="teste@gmail.com"
    )

    session.add(ag)
    session.commit()

    assert ag.id is not None
    assert ag.nome == "Otávio"
    assert ag.email == "teste@gmail.com"


def test_conflito_horario():
    ag1 = Agendamento(
        nome="A",
        idade=20,
        convenio="X",
        especialidade="Cardiologia",
        data=date(2030, 1, 1),
        hora=time(8, 0),
        email="a@a.com",
        medico_id=1
    )

    session.add(ag1)
    session.commit()

    conflito = session.query(Agendamento).filter_by(
        medico_id=1,
        data=date(2030, 1, 1),
        hora=time(8, 0)
    ).first()

    assert conflito is not None
