# Endpoints da API

Base URL: `/api/v1`

## Autenticação
### `POST /auth/login`
**Descrição:** autentica usuário e retorna JWT.

**Body**
```json
{
  "email": "manager@fieldops.ai",
  "password": "manager123"
}
```

**Resposta**
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

### `GET /auth/me`
**Descrição:** retorna contexto do usuário autenticado.

**Headers**
- `Authorization: Bearer <token>`

---

## Ordens
### `POST /orders`
**Descrição:** cria/atualiza ordem de serviço e aciona pipeline multiagente completo.

### `GET /orders?city=&region=&priority=&q=`
**Descrição:** lista ordens com filtros para operação.

### `GET /orders/{order_id}`
**Descrição:** detalhamento completo da ordem para investigação.

---

## Recomendações e Governança Humana
### `GET /recommendations/queue`
**Descrição:** lista recomendações pendentes de aprovação humana.

### `GET /recommendations/{decision_id}`
**Descrição:** retorna recomendação pelo `decision_id`.

### `POST /recommendations/approve`
**Descrição:** aprova/rejeita recomendação crítica.

**Body**
```json
{
  "decision_id": "DEC-ABC123",
  "approve": true,
  "justification": "Revisado pelo dispatcher"
}
```

### `GET /recommendations/decision/{decision_id}`
**Descrição:** retorna trilha completa IA + decisão humana.

---

## Dashboard Executivo
### `GET /dashboard/kpis`
Métricas de negócio e performance operacional.

### `GET /dashboard/risk-by-region`
Distribuição de risco por região.

### `GET /dashboard/executive-insights`
Insights agregados para liderança.

### `GET /dashboard/demo-status`
Status do cenário real de demonstração (ordens, recomendações, decisões, aprovadas/rejeitadas).

---

## Monitoramento de Modelo
### `GET /monitoring/models`
Latência, volume, drift simulado e taxa de override humano.

---

## Saúde
### `GET /health`
Checagem de vida da API.

---

## Rastreabilidade
- Todas as respostas incluem `x-request-id`.
- Decisões críticas são vinculadas por `decision_id`.
- A trilha de auditoria é persistida na tabela `audit_logs`.