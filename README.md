# FIELDOPS SENTINEL AI

**Plataforma agentic de inteligÃªncia operacional para operaÃ§Ãµes de campo em ambiente real.**

Este projeto foi construÃ­do para demonstrar um produto de IA aplicado a operaÃ§Ãµes crÃ­ticas, com arquitetura robusta, governanÃ§a humana, explicabilidade e visÃ£o executiva.

## Posicionamento
O FIELDOPS Sentinel AI apoia operaÃ§Ãµes de:
- telecomunicaÃ§Ãµes;
- utilities;
- manutenÃ§Ã£o tÃ©cnica;
- centros de despacho;
- gestores operacionais.

## Problemas Reais que o Sistema Resolve
- ordens mal priorizadas;
- risco elevado de atraso, no-show e reagendamento;
- quebra de SLA por decisÃ£o tardia;
- desequilÃ­brio de carga entre tÃ©cnicos e regiÃµes;
- falta de explicabilidade da recomendaÃ§Ã£o da IA;
- ausÃªncia de auditoria em decisÃµes crÃ­ticas.

## Diferenciais de NÃ­vel Enterprise
- pipeline multiagente funcional (nÃ£o chatbot);
- recomendaÃ§Ã£o operacional com policy guard;
- fluxo Humano no Loop obrigatÃ³rio para aÃ§Ãµes crÃ­ticas;
- trilha auditÃ¡vel por `request_id` e `decision_id`;
- dashboard executivo premium para operaÃ§Ã£o e lideranÃ§a;
- seed automÃ¡tico com dados realistas para prova de valor imediata.

## Arquitetura Geral

```mermaid
flowchart LR
  UI[Next.js Frontend] --> API[FastAPI Backend]
  API --> IA[Agente de Intake]
  IA --> RS[Agente de Risco]
  RS --> DR[Agente de Recomendacao Operacional]
  DR --> PG[Agente de Politica e Guardrails]
  PG --> EX[Agente de Explicabilidade]
  EX --> DB[(PostgreSQL)]
  DB --> ER[Agente de Relatorio Executivo]
  API --> MON[APIs de Monitoramento e Auditoria]
  ML[Pipeline de Treino] --> ART[Artefatos de Modelo]
  ART --> RS
```

## Fluxo Multiagente
1. **Agente de Intake**
   - normaliza dados de ordem;
   - valida campos obrigatÃ³rios;
   - classifica contexto da ordem.

2. **Agente de Risco**
   - calcula risco de atraso;
   - calcula risco de no-show;
   - calcula risco de reagendamento;
   - devolve score consolidado e fatores.

3. **Agente de Recomendacao Operacional**
   - sugere prioridade e janela operacional;
   - propÃµe redistribuiÃ§Ã£o tÃ©cnico/regiÃ£o;
   - combina heurÃ­stica operacional com score de risco.

4. **Agente de Politica e Guardrails**
   - bloqueia sugestÃµes sem skill compatÃ­vel;
   - sinaliza risco de SLA crÃ­tico;
   - impÃµe aprovaÃ§Ã£o humana para alto impacto.

5. **Agente de Explicabilidade**
   - gera explicaÃ§Ã£o executiva;
   - gera explicaÃ§Ã£o operacional;
   - facilita auditoria e confianÃ§a.

6. **Agente de Relatorio Executivo**
   - consolida gargalos;
   - identifica regiÃµes de maior risco;
   - aponta pressÃ£o de backlog.

## Humano no Loop
- recomendaÃ§Ãµes crÃ­ticas ficam em `pending_human_approval`;
- operador decide aprovar/rejeitar;
- justificativa humana Ã© registrada;
- decisÃ£o final Ã© rastreada e auditada.

## Stack TÃ©cnica
### Frontend
- Next.js 15
- TypeScript
- Tailwind CSS
- estrutura `shadcn/ui`
- Recharts
- Framer Motion

### Backend
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- JWT

### IA / Analytics
- pandas
- numpy
- scikit-learn
- XGBoost

### Infra e Qualidade
- Docker Compose
- Makefile
- `.env.example`
- GitHub Actions (lint + teste + build)

## Estrutura do RepositÃ³rio
```text
/frontend
/backend
/ml
/scripts
/docs
/docker
/.github/workflows
```

## ExecuÃ§Ã£o Local
1. Copie variÃ¡veis de ambiente:
   - `cp .env.example .env`
2. Suba os serviÃ§os:
   - `docker compose up -d --build`
3. Acesse:
   - Frontend: `http://localhost:3000/login`
   - Swagger: `http://localhost:8000/docs`

## Credenciais de DemonstraÃ§Ã£o
- `manager@fieldops.ai / manager123`
- `dispatcher@fieldops.ai / dispatcher123`
- `analyst@fieldops.ai / analyst123`

## Prova de Valor com Dados Reais
Quando o banco inicia vazio, o sistema realiza auto-seed com cenÃ¡rio operacional completo.

Exemplo real validado:
- `orders`: 180
- `recommendations`: 180
- `decisions`: 180
- com aprovaÃ§Ãµes e rejeiÃ§Ãµes humanas registradas

Endpoint para validaÃ§Ã£o:
- `GET /api/v1/dashboard/demo-status`

## Pipeline de Dados e Treino
### Gerar dataset sintÃ©tico
- `python ml/scripts/generate_synthetic_data.py --rows 5000`

### Treinar modelos
- `python ml/scripts/train_models.py`

### Alimentar ordens via API
- `python scripts/seed_demo_data.py --rows 120`

## MÃ³dulos do Produto
- **Login Operacional**
- **Centro de Comando**
- **Grade de Ordens**
- **Detalhe de Caso com IA**
- **Fila de RecomendaÃ§Ãµes CrÃ­ticas**
- **Insights Executivos**
- **Monitoramento de Modelo**

## MÃ©tricas de NegÃ³cio Expostas
- percentual de ordens em risco;
- risco mÃ©dio de SLA;
- taxa de aprovaÃ§Ã£o humana;
- taxa de override humano;
- latÃªncia mÃ©dia de resposta;
- atrasos evitados projetados;
- reduÃ§Ã£o de backlog projetada;
- impacto operacional estimado.

## Observabilidade e GovernanÃ§a
- logs estruturados;
- correlaÃ§Ã£o por `request_id`;
- rastreio por `decision_id`;
- auditoria em `audit_logs`;
- monitoramento de latÃªncia e drift;
- polÃ­tica de aprovaÃ§Ã£o humana para aÃ§Ãµes crÃ­ticas.

## SeguranÃ§a
- configuraÃ§Ã£o por ambiente;
- validaÃ§Ã£o forte de entrada;
- CORS;
- JWT;
- rate limiting bÃ¡sico;
- sem segredos de produÃ§Ã£o no cÃ³digo.

## DocumentaÃ§Ã£o Complementar
- Endpoints: `docs/endpoints.md`
- Arquitetura: `docs/architecture.md`

## ConsideraÃ§Ãµes de ProduÃ§Ã£o
- migraÃ§Ãµes com Alembic;
- rate limit distribuÃ­do com Redis;
- OpenTelemetry + Prometheus + Grafana;
- filas assÃ­ncronas para alta escala;
- versionamento e rollout controlado de modelos.

## Roadmap
- otimizaÃ§Ã£o geoespacial real de rotas;
- ingestÃ£o de eventos em tempo real;
- reasoning com LLM para incidentes complexos;
- modo multi-tenant SaaS;
- online learning;
- integraÃ§Ãµes ERP/CRM/WFM.

## Resumo
Este projeto representa um blueprint realista de IA aplicada a operaÃ§Ãµes: produto com apresentaÃ§Ã£o premium, arquitetura sÃ³lida e governanÃ§a adequada para contexto corporativo.