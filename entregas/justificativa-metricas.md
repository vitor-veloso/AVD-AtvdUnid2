# Justificativa das métricas — Dashboard

**Projeto:** Anime Insights  
**Autor:** José Veloso  
**Dashboard:** Escolha seu anime

## Público-alvo e objetivo

O painel é destinado a fãs de anime que desejam escolher o próximo título para assistir. As métricas resumem a quantidade de opções disponíveis, a avaliação dos títulos e a presença de séries curtas dentro das preferências selecionadas.

Os dados vêm do Anime Recommendations Database, de CooperUnion, e foram tratados na análise exploratória do projeto. Eles representam um retrato histórico da comunidade do MyAnimeList, não avaliações ou disponibilidade atualizadas em serviços de streaming.

As quatro métricas são recalculadas conforme os filtros laterais de formato, gênero, nota, episódios e membros. O controle de mínimo de membros do ranking afeta somente esse gráfico, sem alterar os indicadores. A seleção de variáveis do laboratório também não altera as métricas.

## Métrica 1: Títulos disponíveis

- **Variável:** `anime_id`, usado para identificar os títulos; a implementação conta as linhas da base filtrada, que deve manter um registro por anime.
- **O que mede:** quantidade de títulos que atendem simultaneamente aos filtros selecionados.
- **Cálculo:** número de registros do recorte filtrado.
- **Por que foi escolhida:** mostra o tamanho do conjunto de opções antes de o usuário examinar os gráficos ou a tabela. Também ajuda a perceber quando os filtros ficaram restritivos demais.
- **Público-alvo:** fãs que procuram animes compatíveis com suas preferências de gênero, formato, avaliação, duração em episódios e popularidade.
- **Qual decisão pode ser apoiada por essa métrica?** Manter, ampliar ou restringir os filtros para obter uma quantidade de opções adequada à exploração.
- **O que comunica ao público-alvo:** “Há esta quantidade de títulos na base que correspondem às suas escolhas.”
- **Limitação:** “disponíveis” significa presentes no recorte da base, não disponíveis para assistir em uma plataforma. Temporadas e outros registros de uma mesma franquia podem ser títulos distintos.

## Métrica 2: Nota média

- **Variável:** `rating`.
- **O que mede:** Basicamente mede a nota média dos animes da seleção 
- **Cálculo:** soma das notas dos títulos filtrados dividida pela quantidade desses títulos. Cada anime tem o mesmo peso.
- **Por que foi escolhida:** Pois dá uma visão geral da seleção sem precisar que se aprofundar diretamente em anime por anime
- **Público-alvo:** fãs que consideram a avaliação da comunidade como um dos critérios para escolher um anime.
- **Qual decisão pode ser apoiada por essa métrica?** Qual seleção de animes pre-selecionar para pesquisar mais sobre e assistir no futuro, de acordo com os gostos individuais da pessoa 
- **O que comunica ao público-alvo:** “Em média, os títulos deste recorte receberam esta nota.”
- **Limitação:** é a média das notas dos animes, não uma média calculada diretamente sobre todas as avaliações individuais dos usuários. Não é ponderada por `members`, pois membros não equivale ao número de avaliações. A média pode esconder diferenças entre os títulos e não garante que um anime corresponda ao gosto pessoal do usuário.

## Métrica 3: Percentual de títulos com nota maior ou igual a 8

- **Variável:** `rating`.
- **O que mede:** participação dos títulos com nota considerada alta segundo o critério adotado no projeto, `rating >= 8`.
- **Cálculo:** `(quantidade de títulos filtrados com nota >= 8 / total de títulos filtrados) × 100`.
- **Por que foi escolhida:** complementa a média ao mostrar quanto do recorte alcança um patamar definido. A média sozinha não informa a proporção de títulos acima desse limite.
- **Público-alvo:** fãs que desejam priorizar animes com avaliações altas na comunidade.
- **Qual decisão pode ser apoiada por essa métrica?** Fazer um pré-seleção de conteúdo de nota 8 ou mair, assim poupando tempo do usuário e selecioando as melhores obras
- **O que comunica ao público-alvo:** “Esta porcentagem das opções selecionadas possui nota de pelo menos 8.”
- **Justificativa do limite:** a nota 8 foi adotada como um critério simples e explícito para destacar avaliações altas em uma escala de até 10. É uma escolha do projeto, não uma classificação oficial de qualidade.
- **Limitação:** a métrica depende diretamente do filtro de nota. Se o usuário selecionar apenas notas a partir de 8, o resultado será 100% por construção. As notas representam a comunidade da fonte e o momento da coleta.

## Métrica 4: Percentual de séries TV curtas

- **Variáveis:** `type` e `episodes`.
- **O que mede:** participação de séries com até 12 episódios entre os títulos do tipo TV presentes no recorte.
- **Cálculo:** `(quantidade de títulos filtrados com type == "TV" e episodes <= 12 / quantidade de títulos filtrados com type == "TV") × 100`.
- **Por que foi escolhida:** acrescenta um critério de extensão da série à escolha, além da avaliação da comunidade. O denominador considera somente séries TV para que filmes de um episódio não sejam classificados como séries curtas.
- **Público-alvo:** Apreciadores de anime que não ganharam na loteria ou possuem vida profissional, que não tem condições de assistir alguma obra como one piece de 1k+ episódios 
- **Qual decisão pode ser apoiada por essa métrica?** Verificar se o recorte oferece uma proporção relevante de séries curtas e ajustar o filtro de episódios conforme a preferência.
- **O que comunica ao público-alvo:** “Entre as séries TV selecionadas, esta porcentagem possui até 12 episódios.”
- **Justificativa do limite:** A quantidade de até 12 episódios geralmente é utilizada na produção de séries limitadas no mundo dos animes 
- **Limitação:** quantidade de episódios não equivale ao tempo total necessário para assistir, pois a duração dos episódios varia. Um registro pode representar apenas uma temporada de uma franquia. Se não houver séries TV no recorte, o aplicativo mostra “Sem séries TV”, pois não há denominador para calcular o percentual.

## Interpretação conjunta e cuidados

As métricas cumprem funções complementares: a quantidade informa o tamanho do recorte, a média resume as avaliações, o percentual com nota alta mostra a concentração acima de um critério e o percentual de séries curtas informa a presença de opções com poucos episódios.

O usuário deve interpretar esses indicadores junto com o ranking, a comparação por gênero e a dispersão entre popularidade e avaliação. Os indicadores apoiam a exploração e não constituem uma recomendação personalizada automática.

Nos filtros de gênero, um título é aceito quando possui pelo menos um dos gêneros selecionados. Ele continua sendo contado uma única vez nas métricas. A separação dos gêneros ocorre apenas no gráfico de notas por gênero, no qual um anime pode participar de mais de um grupo.

Quando nenhum título atende aos filtros, o aplicativo apresenta uma mensagem para ampliar o recorte, em vez de calcular médias e percentuais sem dados.

## Fonte

[Anime Recommendations Database — CooperUnion / Kaggle](https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database).

Tratamento dos dados: `notebooks/EDA_Anime_Recommendations_Jose_Veloso.ipynb`. Base utilizada pelo aplicativo: `data/clean/dataset.csv`.
