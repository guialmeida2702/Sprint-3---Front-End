# ⚙️ MotorWatch — Monitoramento de Motores Industriais

Front-end desenvolvido em **Streamlit** para o TCC de IA, cobrindo as **Sprints 1, 2 e 3**
do desafio de Front-end: cadastro técnico do ativo, dashboards operacionais com
telemetria e séries temporais, e um painel de alertas com apoio à decisão (NLP simulado).

---

## 1. Como executar

```bash
# 1. Crie um ambiente virtual (recomendado)
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Rode a aplicação
streamlit run app.py
```

A aplicação abre em `http://localhost:8501`. Na primeira execução, um *seed* automático
(`data/seed.py`) cadastra 4 motores de exemplo, já com histórico de telemetria sintético,
para que a navegação e o vídeo de demonstração não comecem "vazios".

> Não é necessário nenhum backend externo, banco de dados ou chave de API para rodar o
> projeto — toda a persistência é local (JSON) e toda a telemetria/NLP é simulada, exatamente
> como previsto nos enunciados das três sprints.

---

## 2. Testes automatizados (pytest)

O projeto tem **57 testes automatizados** cobrindo as camadas `core/`, `data/` e
`services/` (lógica de negócio) e um conjunto de testes de integração ponta a
ponta que roda a aplicação real (via `AppTest`) para validar fluxos completos
de navegação — classificação de status, persistência, cadastro/filtro de
equipamentos, geração e conversão de telemetria, montagem de alertas, resumos
de NLP, e a jornada completa do usuário pela interface.

```bash
# Instale as dependências de desenvolvimento (inclui as de produção + pytest)
pip install -r requirements.txt -r requirements-dev.txt

# Rode a suíte completa
pytest

# Com detalhes por teste
pytest -v
```

Estrutura:
```
tests/
├── conftest.py                 # Fixtures: session_state falso + repositório isolado
├── test_config.py              # Classificação de status (Saudável/Atenção/Crítico)
├── test_models.py              # Dataclass Equipment (serialização)
├── test_repository.py          # Persistência JSON (CRUD + isolamento de arquivo)
├── test_equipment_service.py   # Cadastro, busca e filtros
├── test_telemetry_service.py   # Geração/conversão de sinais e simulação de leituras
├── test_alert_service.py       # Montagem de alertas a partir da telemetria
├── test_nlp_service.py         # Resumos textuais (fake NLP) e integração futura
└── test_app_navigation.py      # Integração ponta a ponta (AppTest): navegação real
```

Dois pontos de design que valem destaque:
- **Isolamento total**: a fixture `isolated_repo` redireciona `equipment_service`
  para um arquivo JSON temporário a cada teste, então a suíte nunca lê nem escreve
  em `data/storage/equipment.json` (o "banco" real usado pela aplicação).
- **Testes não-frágeis mesmo com aleatoriedade**: como `telemetry_service` simula
  leituras com ruído aleatório, os testes que dependem de um alerta acontecer
  repetem `tick(force_anomaly=True)` algumas vezes até garantir a condição, em vez
  de assumir sorte na primeira tentativa — a suíte foi validada em 8 execuções
  consecutivas sem nenhuma falha intermitente.

Um workflow de CI (`.github/workflows/tests.yml`) já está configurado para rodar
`pytest` automaticamente a cada `push`/`pull request` no GitHub.

> 🐛 **Bugs reais encontrados e corrigidos durante a revisão do projeto:**
> - **`EquipmentRepository` ignorava o diretório customizado.** O construtor
>   chamava `os.makedirs()` em um diretório fixo em vez do diretório do `path`
>   recebido — um efeito colateral que passaria despercebido em uso manual, mas
>   que os testes de isolamento (`test_repository.py`) expuseram imediatamente.
> - **Navegação para a tela de Detalhe do Equipamento era revertida (crítico).**
>   O `st.radio` do menu lateral guarda seu próprio valor entre reruns; a lógica
>   antiga comparava a escolha do rádio contra `st.session_state.page` a cada
>   rerun e, como "Detalhe" não é uma opção do menu, **forçava a navegação de
>   volta ao menu a cada rerun** — ou seja, clicar em um equipamento na lista ou
>   em um card de alerta nunca abria de fato a ficha técnica. Corrigido em
>   `app.py`, usando `st.session_state.page` como única fonte de verdade e um
>   `on_change` no rádio. Coberto por `tests/test_app_navigation.py`.
> - **Combinação Planta/Área inconsistente no cadastro.** O selectbox de
>   "Planta" ficava dentro do `st.form`, que só reflete mudanças de widgets na
>   submissão — trocar a planta não atualizava a lista de "Área" a tempo,
>   permitindo salvar uma combinação como "Planta Betim" + uma área que
>   pertence a "Planta São Paulo". Corrigido movendo o campo para fora do
>   formulário em `components/equipment_form.py`. Também coberto por
>   `tests/test_app_navigation.py`.
>
> Todos os três já estão corrigidos no código atual e têm teste de regressão
> dedicado — nenhuma ação extra é necessária ao rodar o projeto.

---

## 3. Arquitetura e organização do projeto

O projeto foi estruturado para que o **Front-end evolua de forma desacoplada do
modelo/backend** (requisito explícito da Sprint 1), permitindo:
- desenvolver a interface sem depender da entrega do modelo de ML/NLP;
- trocar a fonte dos dados (hoje JSON local + gerador sintético) por uma API real no
  futuro, alterando **apenas** a camada `data/` e `services/`, sem tocar nas telas;
- eventualmente migrar de Streamlit para outro framework alterando apenas `views/` e
  `components/`, já que `core/`, `data/` e `services/` não importam Streamlit onde não é
  necessário (a exceção controlada é `telemetry_service.py`, que usa `st.session_state`
  apenas como cache de sessão).

```
motor_monitor/
├── app.py                     # Ponto de entrada: roteamento + menu lateral
├── core/
│   ├── config.py              # Cores semânticas, faixas dos sensores, plantas/áreas
│   └── models.py              # Dataclass Equipment (contrato único de dados)
├── data/
│   ├── repository.py          # Camada de persistência (JSON hoje, API amanhã)
│   ├── seed.py                 # Dados de exemplo para demonstração
│   └── storage/equipment.json # "Banco de dados" local
├── services/
│   ├── equipment_service.py   # Regras de listagem/filtro/cadastro
│   ├── telemetry_service.py   # Geração e conversão de sinais (raw → engenharia)
│   ├── alert_service.py       # Cálculo de alertas a partir da telemetria
│   └── nlp_service.py         # Resumos textuais (fake NLP, com "seam" para o modelo real)
├── components/                # Peças de UI reutilizáveis entre telas
│   ├── status_badge.py
│   ├── alert_card.py
│   ├── charts.py
│   └── equipment_form.py
└── views/                     # Uma tela = um módulo com função render()
    ├── home_alerts.py         # Sprint 3 — Painel de Alertas (página inicial)
    ├── equipment_list.py      # Sprint 1/2 — Consulta + navegação por planta/área
    ├── equipment_register.py  # Sprint 1 — Cadastro técnico
    └── equipment_detail.py    # Sprint 1/2/3 — Ficha técnica, Dashboard e Histórico
```

**Fluxo de navegação:** `Painel de Alertas (Home)` → `Consulta de Equipamentos` →
`Detalhe do Equipamento` (abas: Ficha Técnica / Dashboard Operacional / Histórico de
Alertas). O cadastro pode ser acessado tanto pela Consulta quanto, em modo de edição,
de dentro da própria Ficha Técnica.

---

## 4. Checklist de atendimento aos enunciados

### Sprint 1 — Fundamentos do Ativo e Interface de Cadastro
| Requisito | Onde está implementado |
|---|---|
| Tela inicial de consulta com lista/databable, clicável | `views/equipment_list.py` (st.dataframe com seleção de linha) |
| Módulo de Cadastro Técnico (Modelo, Fabricante, Potência, Tensão, TAG) | `components/equipment_form.py`, acessível pela Consulta e pela Ficha Técnica |
| Visualização de dados brutos convertidos (Volts, Ampères, RPM) | Aba "Ficha Técnica" → seção "Visualização de dados brutos" em `equipment_detail.py` |
| Framework Streamlit | ✅ |
| UX: latência, human-in-the-loop, cores semânticas | Validação de formulário com feedback (`st.error`/`st.success`), `st.toast` em atualizações, cores verde/amarelo/vermelho consistentes |
| Arquitetura desacoplada do modelo/backend | `core/`, `data/`, `services/` isolados de `views/` |
| Menu lateral (sidebar) já estruturado para crescer | `app.py` |

### Sprint 2 — Visualização Operacional e Dashboards
| Requisito | Onde está implementado |
|---|---|
| Navegação por Planta/Área | Filtros em `equipment_list.py`; breadcrumb na página de detalhe |
| Dashboard de telemetria (Temperatura, Vibração, Corrente…) | Aba "Dashboard Operacional" — gauges por sensor |
| Gráficos temporais (séries históricas) | `components/charts.py` (`time_series_chart`, Plotly) |
| Alertas e status com cores verde/amarelo/vermelho | `core/config.py` (`STATUS_COLORS`) aplicado em badges, cards e gauges |
| Imagem da placa do motor associada ao cadastro | Upload/exibição na aba "Ficha Técnica" |
| Gráficos com Plotly integrados ao Streamlit | ✅ |
| Dados históricos persistidos entre telas | `st.session_state.telemetry_store`, gerado na Sprint 1/2 e consumido em todas as telas |

### Sprint 3 — Inteligência Operacional e Apoio à Decisão
| Requisito | Onde está implementado |
|---|---|
| Painel de Alertas como página inicial (antes da seleção de equipamento) | `views/home_alerts.py`, definida como página `HOME` em `app.py` |
| Resumos inteligentes (NLP, ainda que simulado) | `services/nlp_service.py`, com *seam* (`external_summary`) pronto para o modelo real |
| Apoio inicial à decisão (cards de recomendação) | Campo "Ação recomendada" em `components/alert_card.py` |
| Botão de atualização / timer automático | Botão manual sempre disponível; timer automático via `streamlit-autorefresh` (com aviso amigável caso o pacote não esteja instalado) |
| Simulação garantida de alerta ao atualizar | `_refresh_all(ensure_alert=True)` em `home_alerts.py` |
| Componentização (cards de alerta reaproveitáveis) | `render_alert_card()` usado tanto no Painel quanto no Histórico do equipamento |
| Gestão de estado dinâmica (Saudável → Atenção → Crítico) | `telemetry_service.equipment_overall_status()`, recalculado a cada rerun |
| Arquitetura desacoplada do processamento do modelo | `alert_service.py` consome apenas a interface pública de `telemetry_service` e `nlp_service` |
| Cores semânticas consistentes | Reuso de `core/config.py` em todas as telas/sprints |

---

## 5. Como preparar os demais entregáveis

### Repositório GitHub
```bash
git init
git add .
git commit -m "MotorWatch - Front-end Sprints 1, 2 e 3"
git branch -M main
git remote add origin <URL_DO_SEU_REPOSITORIO>
git push -u origin main
```
Sugestão: crie o repositório vazio no GitHub primeiro (sem README/gitignore) e cole a
URL no lugar de `<URL_DO_SEU_REPOSITORIO>`. Ao fazer o primeiro `push`, o workflow em
`.github/workflows/tests.yml` roda automaticamente os 57 testes na aba **Actions** do
GitHub — um bom indicador de qualidade para mostrar à banca.

### Vídeo de demonstração — roteiro sugerido (3 a 5 min)
1. Abra pelo **Painel de Alertas** (Sprint 3): mostre os cards, clique em "Atualizar
   agora" e destaque o novo alerta simulado com o resumo textual e a recomendação.
2. Vá em **Consulta de Equipamentos** (Sprint 1): filtre por planta/área (Sprint 2) e
   clique em uma linha para abrir um equipamento.
3. Na tela de detalhe, percorra as 3 abas:
   - **Ficha Técnica**: dados cadastrais, edição do cadastro, dados brutos convertidos.
   - **Dashboard Operacional**: gauges coloridos e gráficos de série temporal (Sprint 2).
   - **Histórico de Alertas**: reaproveitamento do card de alerta (Sprint 3).
4. Feche cadastrando um novo motor em **Novo Cadastro**, mostrando a validação de campos
   obrigatórios e o feedback de sucesso.

---

## 6. Próximos passos (transparência para bancas futuras)

- `services/nlp_service.py` está pronto para receber a saída real do modelo de NLP via
  parâmetro `external_summary`/`external_recommendation`, sem exigir mudança nas telas.
- `data/repository.py` pode ser substituído por uma implementação que consome uma API
  REST/FastAPI do backend, mantendo a mesma assinatura de métodos.
- `services/telemetry_service.py` pode trocar o gerador sintético por uma leitura real de
  um broker MQTT/Kafka ou de um banco de série temporal, mantendo `get_series()`,
  `latest_readings()` e `tick()` como contrato público.
