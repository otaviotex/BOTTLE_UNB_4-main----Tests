from webtest import TestApp
import json
import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app
from database import session, Medico, Agendamento
from datetime import date, time
import os
import hashlib

@pytest.fixture(autouse=True)
def limpar_banco():
    session.query(Agendamento).delete()
    session.query(Medico).delete()
    session.commit()

test_app = TestApp(app)


def criar_medico_teste():
    """Garante médico existente no banco temporário."""
    med = session.query(Medico).filter_by(crm="0000").first()
    if med:
        return med

    salt = os.urandom(16)
    senha_hash = hashlib.sha256(salt + b"123").hexdigest()

    med = Medico(
        nome="Doutor X",
        idade=40,
        genero="M",
        crm="0000",
        especialidade="Ortopedia",
        senha=senha_hash,
        salt=salt.hex()
    )

    session.add(med)
    session.commit()
    return med


def test_rotas_basicas():
    r = test_app.get('/')
    assert r.status_code == 200

    r = test_app.get('/paciente')
    assert r.status_code == 200

    r = test_app.get('/medico')
    assert r.status_code == 200


def test_login_medico_sucesso():
    med = criar_medico_teste()

    response = test_app.post('/login_medico', {
        'crm': med.crm,
        'senha': '123'
    })

    assert response.status_code == 302
    assert "/area_medico" in response.location


def test_login_medico_falha():
    med = criar_medico_teste()

    r = test_app.post('/login_medico', {
        'crm': med.crm,
        'senha': 'errada'
    })

    assert "Senha incorreta" in r.text


def test_assumir_paciente():
    med = criar_medico_teste()

    pac = Agendamento(
        nome="Paciente Z",
        idade=30,
        convenio="UNIMED",
        especialidade=med.especialidade,
        data=date(2035, 1, 1),
        hora=time(10, 0),
        email="aaaa@aaa.com"
    )
    session.add(pac)
    session.commit()

    resposta = test_app.post('/assumir_paciente', {
        'medico_id': med.id,
        'paciente_id': pac.id
    })

    data = json.loads(resposta.text)
    assert data["status"] == "ok"
    assert data["medico_nome"] == med.nome


def test_api_pacientes_medico():
    med = criar_medico_teste()

    r = test_app.get(f'/api/pacientes_medico?medico_id={med.id}')

    assert r.status_code == 200
    data = r.json

    assert isinstance(data, list)
