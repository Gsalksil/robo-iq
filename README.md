# robo-iq

Sistema completo de robô para operar ordens via API com:
- conexão/autenticação via Gmail + senha;
- análise de mercado com candles e médias móveis;
- envio e monitoramento de ordens;
- execução automática por sinal de mercado;
- cancelamento manual e cancelamento por expiração;
- frontend web integrado para operar tudo pelo navegador (evita 404 na raiz `/`).

## Requisitos
- Python 3.10+

## Instalação
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Executar API + Front
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Abra no navegador:
- Frontend: `http://localhost:8000/`
- Docs da API: `http://localhost:8000/docs`

## Fluxo recomendado
1. Conectar na plataforma
```bash
curl -X POST http://localhost:8000/connect \
  -H 'content-type: application/json' \
  -d '{"gmail":"seuusuario@gmail.com", "senha":"senhaforte123"}'
```

2. Consultar mercado/candles
```bash
curl http://localhost:8000/market/EURUSD
```

3. Criar ordem
```bash
curl -X POST http://localhost:8000/orders \
  -H 'content-type: application/json' \
  -d '{"symbol":"EURUSD","side":"buy","amount":50,"expiration_seconds":60}'
```

4. Monitorar ordem
```bash
curl -X POST http://localhost:8000/orders/<ORDER_ID>/monitor
```

5. Cancelar ordem
```bash
curl -X POST http://localhost:8000/orders/<ORDER_ID>/cancel
```

## Principais endpoints
- `GET /` — carrega o frontend web do robô.
- `POST /connect` — valida Gmail + senha e estabelece sessão.
- `POST /disconnect` — encerra sessão do robô.
- `GET /market/{symbol}` — retorna candles e análise de tendência/sinal.
- `POST /orders` — cria ordem e tenta execução conforme sinal.
- `POST /orders/{id}/monitor` — reavalia ordem pendente com novo cenário.
- `POST /orders/{id}/cancel` — cancela ordem aberta.
- `GET /orders` — lista ordens.
- `GET /orders/{id}` — detalha ordem.

## Testes
```bash
pytest -q
```


## Enviar para o repositório remoto
Depois de validar localmente, publique assim:
```bash
git add .
git commit -m "feat: sua mensagem"
git push origin <sua-branch>
```
