# AG07 - Problema do Cavalo do Xadrez

Implementação de um Algoritmo Genético para encontrar uma trajetória do cavalo que visite as 64 casas do tabuleiro sem repetir casas.

## Tecnologias

- Python 3, usando apenas a biblioteca padrão.
- HTML, CSS e JavaScript puro para a interface.

## Como executar

```bash
python server.py
```

Depois acesse:

```text
http://127.0.0.1:4173
```

## Modelagem do AG

- Cromossomo: permutação das 64 casas do tabuleiro.
- Restrição de repetição: garantida pela representação em permutação e por reparo após cruzamento/mutação.
- Fitness: quantidade de movimentos válidos em L, com pequeno reforço para a maior sequência válida contínua.
- Objetivo: atingir 63 movimentos válidos entre as 64 casas.

## Operadores implementados

- Seleção por torneio.
- Elitismo.
- Cruzamento ordenado.
- Mutação por troca.
- Mutação por inserção.
- Mutação por inversão.
- Mutação por embaralhamento.
- Mutação mista.

A opção de inicialização heurística usa rotas baseadas na regra de Warnsdorff para criar uma população inicial mais competitiva. Ela pode ser desativada na interface.

## Interface

O tabuleiro ocupa a área esquerda e os controles do Algoritmo Genético ficam à direita. Durante a execução, a rota é desenhada no tabuleiro, as casas recebem a ordem da visita e a trajetória é listada abaixo do tabuleiro.

## Testes

```bash
python -m unittest discover -s tests
```
