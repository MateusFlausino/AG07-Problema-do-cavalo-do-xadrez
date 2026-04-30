# Relatorio Academico - AG07: Problema do Cavalo do Xadrez

## Identificacao

**Atividade:** Trabalho 07 - Problema do Cavalo do Xadrez  
**Tema:** Algoritmos Geneticos aplicados ao passeio do cavalo  
**Repositorio:** https://github.com/MateusFlausino/AG07-Problema-do-cavalo-do-xadrez  
**Tecnologias utilizadas:** Python, HTML, CSS e JavaScript

## Resumo

Este trabalho apresenta a implementacao de um Algoritmo Genetico (AG) para resolver o problema do passeio do cavalo em um tabuleiro de xadrez 8x8. O objetivo e encontrar uma trajetoria em que o cavalo visite todas as 64 casas do tabuleiro sem repetir nenhuma delas, obedecendo ao movimento em L caracteristico da peca. A solucao desenvolvida utiliza uma representacao por permutacao das casas, selecao por torneio, elitismo, cruzamento ordenado e diferentes operadores de mutacao. Alem do algoritmo em Python, foi construida uma interface web simples para visualizacao do tabuleiro, configuracao dos parametros do AG e exibicao da rota obtida.

## 1. Introducao

O problema do cavalo do xadrez, tambem conhecido como passeio do cavalo, consiste em determinar uma sequencia de movimentos legais que permita ao cavalo visitar todas as casas do tabuleiro exatamente uma vez. Trata-se de um problema classico de busca combinatoria, pois o numero de sequencias possiveis cresce rapidamente conforme o tamanho do tabuleiro.

Algoritmos Geneticos sao metodos inspirados no processo de evolucao natural. Eles trabalham com uma populacao de solucoes candidatas e aplicam operadores como selecao, cruzamento e mutacao para produzir novas geracoes. Ao longo das iteracoes, espera-se que solucoes com melhor desempenho sejam preservadas e combinadas, aumentando a chance de encontrar uma resposta adequada ao problema.

## 2. Objetivos

O objetivo geral deste trabalho e construir uma aplicacao capaz de encontrar e apresentar uma trajetoria valida para o cavalo em um tabuleiro 8x8.

Objetivos especificos:

- Representar cada individuo como uma rota contendo as 64 casas do tabuleiro.
- Garantir que nenhuma casa seja visitada mais de uma vez.
- Avaliar a qualidade das rotas pela quantidade de movimentos validos do cavalo.
- Implementar selecao por torneio, elitismo, cruzamento ordenado e mutacoes por troca, insercao, inversao, embaralhamento e mista.
- Construir uma interface simples com o tabuleiro a esquerda e os controles do AG a direita.
- Apresentar a trajetoria obtida ao final da execucao.

## 3. Descricao do Problema

O tabuleiro foi modelado como uma matriz 8x8, totalizando 64 casas. Cada casa recebeu um indice inteiro entre 0 e 63 e tambem uma notacao equivalente ao xadrez, como `a1`, `b3` e `h8`.

O cavalo pode se mover em L, ou seja, duas casas em uma direcao e uma casa em direcao perpendicular. Assim, a partir de uma casa `(linha, coluna)`, os movimentos possiveis sao:

- `(-2, -1)`
- `(-2, +1)`
- `(-1, -2)`
- `(-1, +2)`
- `(+1, -2)`
- `(+1, +2)`
- `(+2, -1)`
- `(+2, +1)`

Para que uma solucao seja considerada completa, ela deve possuir 64 casas distintas e 63 movimentos validos entre casas consecutivas.

## 4. Modelagem do Algoritmo Genetico

### 4.1 Representacao do Cromossomo

Cada cromossomo e representado por uma permutacao das 64 casas do tabuleiro. Essa escolha garante que uma rota nao repita casas, pois cada posicao aparece apenas uma vez no individuo.

Exemplo simplificado de cromossomo:

```text
[35, 50, 56, 41, ..., 47]
```

Cada numero corresponde a uma casa do tabuleiro. A ordem dos numeros representa a ordem de visita do cavalo.

### 4.2 Populacao Inicial

A populacao inicial combina rotas aleatorias com rotas geradas por uma inicializacao heuristica baseada na regra de Warnsdorff. Essa heuristica prioriza casas que possuem menor quantidade de movimentos futuros disponiveis, ajudando a criar individuos iniciais mais competitivos.

Na interface, a inicializacao heuristica pode ser ativada ou desativada pelo usuario.

### 4.3 Funcao de Avaliacao

A funcao de fitness avalia cada rota considerando:

- Quantidade de movimentos validos do cavalo.
- Maior sequencia continua de movimentos validos.
- Quantidade de casas unicas.
- Penalizacoes para rotas invalidas, duplicadas ou incompletas.

A formula implementada foi:

```text
fitness = (movimentos_validos * 100)
        + (maior_sequencia_valida * 2)
        + casas_unicas
        - penalidade_por_duplicacao
        - penalidade_por_tamanho
```

Como o cromossomo e uma permutacao, a restricao de nao repetir casas e preservada naturalmente. Ainda assim, existe uma etapa de reparo para garantir que eventuais alteracoes geradas por operadores geneticos continuem formando uma permutacao valida.

### 4.4 Selecao por Torneio

Na selecao por torneio, alguns individuos sao escolhidos aleatoriamente da populacao. Entre esses candidatos, o individuo com melhor fitness e selecionado para reproducao. Essa estrategia equilibra pressao seletiva e diversidade genetica.

### 4.5 Elitismo

O elitismo preserva diretamente os melhores individuos de uma geracao para a proxima. Dessa forma, boas solucoes nao sao perdidas durante cruzamentos e mutacoes.

### 4.6 Cruzamento Ordenado

O cruzamento ordenado foi utilizado por ser adequado para problemas baseados em permutacoes. Ele copia um trecho de um dos pais e completa o restante da rota com os genes do outro pai, mantendo a ordem relativa e evitando repeticoes.

### 4.7 Operadores de Mutacao

Foram implementados os seguintes operadores:

- **Mutacao por troca:** troca duas casas de posicao na rota.
- **Mutacao por insercao:** remove uma casa de uma posicao e a insere em outra.
- **Mutacao por inversao:** inverte a ordem de um segmento da rota.
- **Mutacao por embaralhamento:** reorganiza aleatoriamente um segmento da rota.
- **Mutacao mista:** seleciona aleatoriamente uma das mutacoes disponiveis.

Esses operadores permitem explorar diferentes regioes do espaco de busca e ajudam a evitar convergencia prematura.

## 5. Implementacao

O projeto foi desenvolvido sem dependencias externas, utilizando apenas a biblioteca padrao do Python no backend e HTML, CSS e JavaScript puro no frontend.

Estrutura principal do projeto:

```text
.
|-- knight_ga.py
|-- server.py
|-- static/
|   |-- index.html
|   |-- styles.css
|   `-- app.js
|-- tests/
|   `-- test_knight_ga.py
|-- README.md
`-- .gitignore
```

Arquivos principais:

- `knight_ga.py`: contem a modelagem do tabuleiro, avaliacao das rotas e operadores do Algoritmo Genetico.
- `server.py`: servidor HTTP em Python para servir a interface e executar o AG via eventos em tempo real.
- `static/index.html`: estrutura da interface.
- `static/styles.css`: estilos visuais do tabuleiro, controles e metricas.
- `static/app.js`: comunicacao com o servidor, renderizacao da rota e atualizacao das metricas.
- `tests/test_knight_ga.py`: testes unitarios dos principais operadores.

## 6. Interface

A interface foi organizada em duas areas principais:

- A esquerda, ocupando aproximadamente 2/3 da tela, fica o tabuleiro de xadrez 8x8.
- A direita, ocupando aproximadamente 1/3 da tela, ficam os controles do Algoritmo Genetico.

Os controles permitem configurar:

- Tamanho da populacao.
- Numero maximo de geracoes.
- Tamanho do torneio.
- Quantidade de individuos preservados por elitismo.
- Taxa de cruzamento.
- Taxa de mutacao.
- Tipo de mutacao.
- Semente aleatoria.
- Uso de inicializacao heuristica.

Durante a execucao, a aplicacao exibe:

- Geracao atual.
- Quantidade de movimentos validos.
- Quantidade de movimentos invalidos.
- Quantidade de casas unicas visitadas.
- Valor de fitness.
- Tempo de execucao.
- Trajetoria obtida.

## 7. Resultado Obtido

Em uma execucao de validacao com semente `7`, populacao `30` e limite de `2` geracoes, o algoritmo encontrou uma solucao completa ja na geracao inicial, devido a inicializacao heuristica.

Metricas da solucao:

- Casas visitadas: `64/64`.
- Movimentos validos: `63/63`.
- Movimentos invalidos: `0`.
- Maior sequencia valida: `63`.
- Fitness: `6490`.

Trajetoria obtida:

```text
d4 -> c2 -> a1 -> b3 -> c1 -> d3 -> e1 -> g2
-> h4 -> f3 -> h2 -> f1 -> d2 -> b1 -> a3 -> b5
-> a7 -> c8 -> e7 -> g8 -> h6 -> f5 -> g7 -> e8
-> d6 -> c4 -> b2 -> a4 -> b6 -> a8 -> c7 -> a6
-> c5 -> b7 -> a5 -> c6 -> b8 -> d7 -> f8 -> h7
-> g5 -> e6 -> d8 -> f7 -> h8 -> g6 -> e5 -> g4
-> e3 -> d1 -> f2 -> h1 -> g3 -> h5 -> f6 -> e4
-> c3 -> a2 -> b4 -> d5 -> f4 -> e2 -> g1 -> h3
```

Essa trajetoria visita todas as casas exatamente uma vez e todos os deslocamentos consecutivos respeitam o movimento em L do cavalo.

## 8. Como Executar

Execute o servidor:

```bash
python server.py
```

Depois acesse no navegador:

```text
http://127.0.0.1:4173
```

Observacao: a porta padrao utilizada e `4173`, pois a porta `8000` estava bloqueada no ambiente de desenvolvimento usado durante a validacao.

## 9. Testes

Os testes unitarios podem ser executados com:

```bash
python -m unittest discover -s tests
```

Os testes verificam:

- Preservacao de permutacao no cruzamento ordenado.
- Preservacao de permutacao nos operadores de mutacao.
- Geracao de rotas sem repeticao pela heuristica.
- Emissao de payload de progresso pelo Algoritmo Genetico.

Resultado obtido na validacao:

```text
Ran 4 tests
OK
```

## 10. Conclusao

O Algoritmo Genetico implementado foi capaz de encontrar uma rota valida para o passeio do cavalo no tabuleiro 8x8, visitando as 64 casas sem repeticao. A representacao por permutacao mostrou-se adequada para manter a restricao principal do problema, enquanto o cruzamento ordenado e os operadores de mutacao permitiram explorar diferentes possibilidades de rota.

A utilizacao de elitismo contribuiu para preservar boas solucoes entre geracoes, e a inicializacao heuristica baseada na regra de Warnsdorff acelerou significativamente a busca por trajetorias completas. A interface web tambem facilitou a observacao do comportamento do algoritmo e a interpretacao da solucao final.

Portanto, a atividade atingiu o objetivo proposto, apresentando uma implementacao funcional, configuravel e visual do Algoritmo Genetico aplicado ao problema do cavalo do xadrez.

## Referencias

HOLLAND, John H. *Adaptation in Natural and Artificial Systems*. University of Michigan Press, 1975.

GOLDBERG, David E. *Genetic Algorithms in Search, Optimization, and Machine Learning*. Addison-Wesley, 1989.

LINDEN, Ricardo. *Algoritmos Geneticos*. Brasport, 2012.
