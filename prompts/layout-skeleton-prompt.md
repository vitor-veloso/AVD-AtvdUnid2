# Template: rascunho de layout → esqueleto do app

## Contexto

Sou José Vitor Veloso, aluno da disciplina Análise e Visualização de Dados. Quero criar uma aplicação chamada Anime Insights em Streamlit, com dois dashboards baseados na minha EDA do Anime Recommendations Database, de CooperUnion.

Fonte: https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database

O público-alvo são fãs que desejam explorar animes e escolher o próximo título para assistir. O primeiro dashboard será um laboratório de distribuição e correlação; o segundo apresentará métricas e gráficos que apoiem essa escolha.

## Entrada

Utilize os seguintes arquivos como referência:

- EDA: `notebooks/EDA_Anime_Recommendations_Jose_Veloso.ipynb`.
- Dados tratados: `data/clean/dataset.csv`.
- Layout do Dashboard 1: `entregas/Dash1_rasc.png`.
- Layout do Dashboard 2: `entregas/Dash2_rasc.png`.

As imagens dos layouts acompanham este pedido. Os gráficos desenhados são ilustrativos; todos os resultados devem ser calculados usando o CSV tratado.

Colunas principais:

| Coluna | Significado |
|---|---|
| `anime_id` | Identificador do anime |
| `name` | Nome do anime |
| `genre` | Gêneros separados por vírgula |
| `type` | Formato, como TV, Movie, OVA, ONA, Special e Music |
| `episodes` | Quantidade de episódios |
| `rating` | Nota média do anime |
| `members` | Quantidade de pessoas que adicionaram o título às listas |

A EDA também contém `members_log`, `faixa_rating` e `faixa_popularidade`. `members_log` corresponde a log(1 + members).

### Estrutura geral

Criar duas abas: “Laboratório de análise” e “Escolha seu anime”. Manter à esquerda uma barra lateral com filtros de formato e gênero, sliders de intervalo para nota, episódios e membros e um seletor das variáveis quantitativas do laboratório.

### Dashboard 1 — Laboratório de análise

O painel deve responder:

- Como se distribuem notas, quantidade de episódios e popularidade?
- Como essas variáveis se associam?
- Como os padrões mudam conforme o recorte selecionado?

Apresentar no topo um mapa de calor da correlação de Spearman entre as variáveis selecionadas. Abaixo, dispor um histograma por variável em duas colunas. As variáveis de interesse são `rating`, `episodes` e `members`.

Como episódios e membros possuem forte assimetria, oferecer visualização na escala original e uma opção com transformação log(1 + x), identificando claramente os eixos.

### Dashboard 2 — Escolha seu anime

O painel deve responder:

- Quantos títulos atendem às preferências selecionadas?
- Qual é a avaliação média desse grupo?
- Qual proporção dos títulos possui nota alta?
- Qual proporção das séries TV é curta?
- Quais títulos combinam avaliação e popularidade?

Apresentar quatro métricas em uma linha:

1. **Títulos disponíveis:** quantidade de animes filtrados.
2. **Nota média:** média simples de `rating` no recorte.
3. **Com nota ≥ 8:** percentual dos títulos filtrados com `rating >= 8`.
4. **Séries TV curtas:** percentual de títulos com até 12 episódios entre os títulos `type == "TV"` filtrados.

Abaixo, apresentar três gráficos:

1. **Animes mais bem avaliados:** ranking de até dez títulos por nota. Incluir um mínimo de membros ajustável apenas para esse ranking. Desempatar por membros e identificador.
2. **Notas por gênero:** barras de nota média dos até doze gêneros mais frequentes no recorte, com quantidade de títulos no tooltip.
3. **Popularidade e avaliação:** dispersão de membros versus nota, com eixo de membros logarítmico, cores por formato e identificação do anime no tooltip.

Incluir ao final uma seção expansível para consultar os títulos filtrados.

## Restrições

- Usar Python, Streamlit, Pandas e Plotly.
- Implementar o aplicativo em `app.py`. Carregar a base por meio de `src/data_loader.py`, com cache e caminho resolvido a partir da localização do projeto.
- Ler somente `data/clean/dataset.csv`. Não modificar o notebook ou os dados brutos e não baixar dados a cada interação.
- Manter duas abas, seletor de variáveis e sliders de intervalo funcionais.
- Aplicar os filtros laterais aos dois dashboards. O seletor de variáveis controla somente as visualizações do laboratório.
- Combinar gêneros selecionados por OU: basta o título possuir um deles. Nenhum gênero selecionado significa todos; nenhum formato significa nenhum título. Explicar isso na interface.
- Calcular as quatro métricas sobre o recorte filtrado. Não ponderar notas por membros. Se não houver séries TV, informar que a métrica de séries curtas não se aplica.
- Não confundir membros com quantidade de avaliações, receita ou espectadores únicos de todo o catálogo.
- Separar os gêneros antes da agregação e explicar que um título pode participar de vários gêneros.
- Não incluir identificadores na correlação. Não incluir simultaneamente membros e sua transformação como duas variáveis independentes de interesse.
- Calcular Spearman nas variáveis originais selecionadas. Usar matriz compacta, números legíveis e escala divergente de -1 a 1. Tratar variáveis constantes e amostras insuficientes.
- Não remover outliers automaticamente. A transformação logarítmica é uma opção visual e não deve alterar o recorte usado nas métricas.
- Para histogramas transformados, calcular os intervalos sobre log(1 + x), com rótulos explícitos. Não apenas aplicar escala logarítmica a barras calculadas em intervalos lineares muito largos.
- Tratar filtros sem resultados, nenhuma variável selecionada, ausência de séries TV e ranking vazio com mensagens claras.
- Informar que a base é histórica e que correlação não implica causalidade. Não inventar resultados.

## Formato de saída

Entregue o código completo de `app.py` e `src/data_loader.py`, com comentários curtos explicando carregamento, filtros, métricas e gráficos. Caso necessário, entregue também as alterações de dependências e configuração visual.

Explique brevemente a função de cada seção, as fórmulas das métricas e as escalas dos histogramas.
