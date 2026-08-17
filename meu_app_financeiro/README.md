# Fincheck

App mobile (Android) de controle de despesas e investimentos.
**Python + Flet (Material 3) + SQLite**, arquitetura **MVVM**.

## Identidade visual

| Token | HEX | Onde aparece |
|---|---|---|
| Verde Fincheck | `#104535` | Cabeçalhos, card de saldo, splash, fundo do ícone |
| Dourado Fincheck | `#CDAD56` | Valor do saldo, indicador da navegação, logotipo |

Os assets ficam em `assets/` — veja o [README de lá](assets/README.md) para saber
como o ícone foi extraído da arte original e por que o logotipo horizontal tem
uma limitação no ícone adaptativo do Android.

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
gerar_apk.bat
```

O script já exporta `JAVA_HOME`, `ANDROID_HOME` e o `PATH` do toolchain e passa
todos os parâmetros da marca (nome, bundle id, cor da splash, ícone adaptativo).
O APK sai em `meu_app_financeiro/build/apk/`.

**Toolchain instalado em `C:\Users\Usuario\dev`:**

| Componente | Caminho | Realmente necessário? |
|---|---|---|
| Android SDK | `dev\android-sdk` | **Sim** — platform-tools, plataformas 35 e 36, build-tools |
| JDK 17 (Temurin) | `dev\jdk17` | Não — o Flet baixa o próprio |
| Flutter 3.44.9 | `dev\flutter` | Não — o Flet baixa o próprio |

> **Nota:** o `flet build` baixa e gerencia as **próprias cópias do Flutter**
> (3.29.2, fixada pelo Flet 0.28.3) **e do JDK**, em `~\AppData\Local\flet\`.
> As instalações do sistema são ignoradas. O único pré-requisito real é o
> **Android SDK** — o JDK e o Flutter instalados à parte acabaram não sendo
> usados pela build. Ficam aí porque são úteis para outras tarefas Android, mas
> podem ser apagados sem quebrar o `gerar_apk.bat`.

Nada disso foi adicionado às suas variáveis de ambiente permanentes — o
`gerar_apk.bat` define tudo só durante a execução.

### Licenças do Android SDK

O `sdkmanager --licenses` lê do console, então redirecionar `y` por pipe não
funciona em terminal não interativo — a primeira build falhou exatamente aí.
O que resolve é dar um stdin de arquivo de verdade ao processo:

```powershell
Start-Process -FilePath lic.cmd -RedirectStandardInput yes.txt -NoNewWindow -Wait
```

As licenças já estão aceitas em `dev\android-sdk\licenses`, então isso só volta a
ser necessário se você recriar o SDK do zero.

---

## Banco de dados

Criado automaticamente no primeiro boot, **vazio**: sem categorias, sem
lançamentos e com renda zero. O app pede que você defina a renda no Perfil.

Para desenvolver com a interface preenchida, rode com a variável de ambiente
`FINCHECK_SEED=1` — aí sim `database/mock_data.py` é aplicado. Nunca ligue isso
numa build de produção.

```powershell
$env:FINCHECK_SEED=1; python meu_app_financeiro\main.py
```

O banco é migrado sozinho: instalações anteriores à tabela `series` ganham a
coluna e um vínculo por grupo (descrição + categoria + tipo), sem perder nada.
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
| `profile` | linha única: nome, salário, VR e VA padrão |
| `categories` | nome, cor HEX, tipo e se aceita VR/VA (`meal_eligible`) |
| `series` | vigência dos recorrentes (`start_month`, `end_month`) |
| `transactions` | lançamentos, presos a uma competência e a uma carteira (`funding`) |
| `month_settings` | snapshot de salário, VR e VA de cada mês (preserva o histórico) |

---

## Regras de negócio implementadas

**Carteiras: salário, VR e VA** — cada lançamento registra de qual saldo saiu
(`transactions.funding`). Os três têm saldo independente: gastar o VR não
consome o salário. VR e VA são opcionais — em branco no Perfil, as carteiras
nem aparecem na tela.

Quem pode pagar o quê:

| Lançamento | Salário | VR / VA |
|---|:---:|:---:|
| Despesa fixa ou variável, categoria de alimentação | sim | sim |
| Despesa fixa ou variável, demais categorias | sim | não |
| Investimento | sim | não |

> "Categoria de alimentação" é o campo `categories.meal_eligible`, marcado por
> você ao criar a categoria — não o nome literal "Alimentação". Como o app nasce
> sem categorias, travar na string quebraria se você chamasse de "Comida" ou
> "Mercado".

A restrição é aplicada em `DashboardViewModel._validate_funding`, não só na
interface: se um VR chegar para uma categoria que não aceita, o lançamento cai
para o salário em vez de ser gravado errado. O mesmo vale quando o benefício não
está configurado.

**Séries (vigência dos recorrentes)** — todo lançamento fixo ou de investimento
pertence a uma linha da tabela `series`, que guarda `start_month` e `end_month`.
É essa identidade que permite dizer "repete até tal mês" e "encerra daqui em
diante"; sem ela cada mês teria apenas linhas soltas, sem relação entre si.

| `end_month` | Efeito |
|---|---|
| `NULL` | Repete indefinidamente |
| `'2026-12'` | Repete até dezembro/2026 e para |

**Rollover de mês** (`MonthRepository.ensure_month`) — ao abrir uma competência
que ainda não existe, o app congela a renda vigente do perfil para aquele mês e
copia os lançamentos das séries **ainda vigentes** (`end_month` nulo ou maior ou
igual ao mês). Despesas variáveis não são copiadas: zeram na virada.

**Excluir um recorrente encerra a série** (`SeriesRepository.end_before`) — some
do mês atual e dos próximos; os meses anteriores ficam intactos. Não é um
`DELETE` da série inteira: o `end_month` vira o mês anterior, preservando o
histórico. Se a série tinha começado no próprio mês, aí sim ela é removida por
completo, porque não sobrou ocorrência nenhuma.

**Estender a data final repovoa** (`SeriesRepository.sync`) — se você aumentar o
prazo de uma fixa, os meses que já estavam abertos e ficaram sem o lançamento
são preenchidos de novo. Sem isso haveria um buraco entre a data antiga e a nova.

**Histórico é somente leitura** — o Dashboard navega entre meses, mas só o mês
corrente aceita edição. Em meses passados os botões de adicionar, editar e
excluir somem, aparece a faixa "Mês encerrado" e os ViewModels ignoram qualquer
escrita (a trava está no ViewModel, não só na UI). `AppState.open_month` também
se recusa a materializar competências passadas — navegar para trás nunca cria
dados.

> Os tipos recorrentes ficam na constante `RECURRING_TYPES`
> (`models/transaction.py`), hoje `FIXED` + `INVESTMENT`. O seletor "Repetir até"
> aparece para os dois: a mecânica de vigência é a mesma, e um aporte mensal
> também costuma ter prazo.

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
