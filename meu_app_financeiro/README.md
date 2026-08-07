# Meu App Financeiro

App mobile (Android) de controle de despesas e investimentos.
**Python + Flet (Material 3) + SQLite**, arquitetura **MVVM**.

---

## Por que Flet e não KivyMD

| Critério | Flet | KivyMD |
|---|---|---|
| Visual Material Design | Renderiza com **Flutter** — componentes nativos M3 reais | Reimplementação própria do Material |
| Rodar no Windows para ver o front | `flet run` abre uma janela na hora | Funciona, mas com mais atrito |
| Gerar o APK | `flet build apk` | Buildozer, que exige Linux/WSL |
| Componentização | Controles compostos, `PieChart`, `BottomSheet`, `ExpansionTile` prontos | Precisa montar mais coisa na mão |

---

## Estrutura

```
meu_app_financeiro/
├── assets/                      # ícones, fontes e imagens
├── database/                    # única camada que executa SQL
│   ├── connection.py            # caminho do .db (Android usa FLET_APP_STORAGE_DATA)
│   ├── schema.py                # DDL das tabelas
│   ├── repositories.py          # Profile / Category / Transaction / Month
│   └── mock_data.py             # dados falsos do primeiro boot
├── models/                      # entidades puras (dataclasses)
│   ├── category.py
│   ├── transaction.py           # + TransactionType e RECURRING_TYPES
│   └── user_profile.py
├── viewmodels/                  # estado reativo e regras de apresentação
│   ├── observable.py            # add_listener / notify
│   ├── app_state.py             # estado global compartilhado
│   ├── dashboard_viewmodel.py
│   ├── reports_viewmodel.py
│   └── profile_viewmodel.py
├── views/                       # somente Flet, zero regra de negócio
│   ├── dashboard_view.py        # Tela 1
│   ├── reports_view.py          # Tela 2
│   ├── profile_view.py          # Tela 3
│   └── components/
│       ├── theme.py             # tokens de cor/raio/espaçamento
│       ├── balance_card.py      # card do Saldo Disponível
│       ├── section_panel.py     # seção expansível de lançamentos
│       ├── transaction_tile.py  # linha de lançamento
│       ├── transaction_sheet.py # BottomSheet de adicionar/editar
│       ├── donut_chart.py       # gráfico de rosca + legenda
│       └── category_bar.py      # barra de progresso por categoria
├── utils/
│   ├── formatters.py            # R$ 1.234,50 e parsing
│   └── date_utils.py            # competências 'YYYY-MM'
├── main.py                      # composição das dependências + rotas
└── requirements.txt
```

Fluxo de dependências: `views → viewmodels → database → models`.
Nenhuma View importa `sqlite3`; nenhum repositório importa `flet`.

---

## Como executar

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

```bash
pip install -r meu_app_financeiro/requirements.txt
```

```bash
python meu_app_financeiro/main.py
```

Abre uma janela de 412x880 (proporção de celular). Para testar no navegador:

```bash
flet run --web meu_app_financeiro/main.py
```

Para ver o app rodando no seu celular Android sem gerar APK, instale o app
**Flet** na Play Store e rode:

```bash
flet run --android meu_app_financeiro/main.py
```

### Gerar o APK

```bash
flet build apk meu_app_financeiro
```

Exige Flutter SDK, Android SDK e JDK instalados — o Flet baixa o que faltar na
primeira execução.

---

## Banco de dados

Criado automaticamente no primeiro boot e populado com `database/mock_data.py`.
O caminho depende de como você inicia o app, porque o `flet run` define a
variável `FLET_APP_STORAGE_DATA` (o mesmo mecanismo usado no Android):

| Comando | Local do `financeiro.db` |
|---|---|
| `python meu_app_financeiro/main.py` | `meu_app_financeiro/financeiro.db` |
| `flet run ...` | `meu_app_financeiro/storage/data/financeiro.db` |
| APK no Android | pasta de dados privada do app |

**Para começar do zero:** apague o `financeiro.db` correspondente e rode de novo.

| Tabela | Papel |
|---|---|
| `profile` | linha única: nome de exibição e renda padrão |
| `categories` | nome, cor HEX e tipo |
| `transactions` | lançamentos, cada um preso a uma competência `YYYY-MM` |
| `month_settings` | snapshot da renda de cada mês (preserva o histórico) |

---

## Regras de negócio implementadas

**Rollover de mês** (`MonthRepository.ensure_month`) — ao abrir uma competência
que ainda não existe, o app congela a renda vigente do perfil para aquele mês e
copia os lançamentos recorrentes do último mês existente. Despesas variáveis
não são copiadas: zeram na virada.

> Os tipos recorrentes ficam na constante `RECURRING_TYPES`
> (`models/transaction.py`), hoje `FIXED` + `INVESTMENT`. O enunciado só citava
> as fixas, mas investimentos como "Aposentadoria" são aportes mensais — se
> preferir que zerem junto com as variáveis, basta remover `INVESTMENT` de lá.

**Alteração de renda** (`MonthRepository.apply_income_from`) — salvar o perfil
atualiza o mês atual e todos os posteriores. Meses passados mantêm o valor
histórico, então os relatórios antigos não mudam.

**Estado reativo** — `AppState` é um `Observable`. Os ViewModels se registram
nele e as Views se registram nos ViewModels. Salvar o perfil na Tela 3 dispara
`notify()`, que reconstrói o cabeçalho e o saldo da Tela 1 antes mesmo de você
voltar para ela.

---

## Próximos passos sugeridos

- Trocar os `ft.Text` de valor por um input com máscara de moeda.
- Filtro de período na Tela 2 (trimestre / ano).
- Exportar CSV dos lançamentos.
- Testes com `pytest` sobre os repositórios (a camada já está isolada para isso).
