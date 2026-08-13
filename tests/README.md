# Test Suite — Permutare API

Suíte de testes automatizados para o `fastapi-start-project` (Permutare API).

## Como rodar

Na raiz do projeto (com a venv ativada):

```bash
pip install pytest httpx
pytest
```

ou com cobertura:

```bash
pip install pytest-cov
pytest --cov=app
```

## Estrutura

```
tests/
├── conftest.py                 # fixtures compartilhadas (client, usuários, headers)
│
├── auth/
│   ├── test_login.py           # login: sucesso, senha errada, email inexistente
│   ├── test_refresh.py         # refresh + rotação de token
│   ├── test_logout.py          # logout + invalidação de sessão
│   ├── test_forgot_password.py # forgot-password (sempre 204)
│   └── test_reset_password.py  # reset + token de uso único
│
└── users/
    ├── test_register.py        # cadastro público
    ├── test_profile.py         # GET/PATCH /users/me
    ├── test_password_change.py # troca de senha + regras
    ├── test_delete.py          # soft delete da própria conta
    └── test_admin.py           # rotas administrativas + autorização
```

## Como funciona o isolamento

O fixture `client` (em `conftest.py`) apaga e recria todas as tabelas
**antes de cada teste**, garantindo que um teste nunca interfira em outro.

Usa um banco SQLite dedicado (`test.db`), então o banco de desenvolvimento
(`permutare.db`) nunca é tocado.

## Fixtures principais

| Fixture          | O que faz                                                        |
|------------------|------------------------------------------------------------------|
| `client`         | TestClient com banco limpo por teste                             |
| `registered_user`| Registra o usuário padrão (user) e devolve suas credenciais    |
| `auth_headers`   | Faz login como user e devolve o header `Authorization`         |
| `admin_user`     | Cria um ADMIN direto pela camada de serviço                      |
| `admin_headers`  | Faz login como ADMIN e devolve o header `Authorization`          |

## Observações importantes

1. **Login usa form-data** (`data=`), não JSON, porque a rota usa
   `OAuth2PasswordRequestForm`. O campo `username` recebe o e-mail.

2. **Reset de senha**: como o token só é exposto via log (nunca na resposta
   da API), os testes geram o token chamando `auth_service.request_password_reset`
   diretamente e depois exercitam o endpoint público.

3. Se algum teste de admin retornar **404** ao buscar por `{user_id}`, verifique
   se `get_user_by_id` está comparando corretamente `UserModel.id == str(user_id)`
   (questão UUID x String que discutimos). Nesse caso, normalize o id para `str`.
