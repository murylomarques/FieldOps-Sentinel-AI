# Arquitetura TÃ©cnica

## Fluxo Multiagente
1. **Agente de Intake**
Valida e normaliza dados da ordem de serviÃ§o.

2. **Agente de Risco**
Calcula risco de atraso, no-show e reagendamento com modelo tabular.

3. **Agente de Recomendacao Operacional**
Sugere prioridade operacional, janela e redistribuiÃ§Ã£o de execuÃ§Ã£o.

4. **Agente de Politica e Guardrails**
Impede aÃ§Ãµes que violem regras de skill, SLA crÃ­tico e impacto sem aprovaÃ§Ã£o.

5. **Agente de Explicabilidade**
Gera justificativa em linguagem operacional e executiva.

6. **Agente de Relatorio Executivo**
Consolida gargalos, hotspots regionais e pressÃ£o de backlog.

## Modelo de GovernanÃ§a
- Cada recomendaÃ§Ã£o recebe um `decision_id` Ãºnico.
- AÃ§Ãµes de alto impacto ficam em `pending_human_approval`.
- AprovaÃ§Ã£o/rejeiÃ§Ã£o humana exige justificativa.
- DecisÃ£o final, autor e timestamp sÃ£o auditados.

## Observabilidade
- logs estruturados em JSON;
- correlaÃ§Ã£o por `request_id`;
- trilha completa por `decision_id`;
- mÃ©tricas de latÃªncia, volume e override humano;
- endpoint dedicado de monitoramento de modelo.

## Camadas da SoluÃ§Ã£o
- **Frontend:** visual executivo premium com foco em operaÃ§Ã£o real.
- **Backend:** API FastAPI com domÃ­nio orientado a decisÃµes.
- **Dados:** PostgreSQL com histÃ³rico operacional e auditoria.
- **IA:** modelos tabulares + heurÃ­sticas de dispatch + guardrails.
- **GovernanÃ§a:** human-in-the-loop obrigatÃ³rio para decisÃµes crÃ­ticas.