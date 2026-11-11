# Leitura e fontes

Foram extraídas e lidas todas as páginas dos cinco PDFs locais com pypdf 7.0.0:
enunciado (5), Aula 01 (42), Aula 02 (44), Aula 03 (48) e Aula 04 (44).
Total: 183 páginas. Uma primeira extração parou por codificação cp1252;
a leitura foi repetida com saída UTF-8 e dividida em blocos para evitar
truncamento. A página 2 do enunciado e a 42 da Aula 03 foram renderizadas
com Poppler e inspecionadas visualmente para conferir catálogo e números.
Os PDFs de entrada não foram alterados; os hashes foram registrados antes
da criação dos entregáveis.

Os dois links em `learning_references/notion_links.txt` são:

- https://melted-ray-4c3.notion.site/Aula-08-Complexidade-de-tempo-o-m-todo-da-substitui-o-8b781ce66c4282d3a2b2012755ae4de3
- https://melted-ray-4c3.notion.site/Aula-09-rvore-de-Recurs-o-e-Teorema-Mestre-e2b81ce66c42820fbd04013100407c3e?source=copy_link

Consulta pela ferramenta web em 11/11/2026: indisponível para ambos. O arquivo
de links foi lido, mas não se afirma leitura do conteúdo das páginas Notion.

As demonstrações e hipóteses são próprias deste relatório. Três cuidados
evitam copiar simplificações das fontes sem verificar:

- Unária: o catálogo diz "exponencial em disco". Com valores de 16 bits, a
  representação 1^x0 tem n ≤ L ≤ 65536n bits; cresce linearmente em n.
- Quicksort médio: duas metades iguais são uma intuição; a recorrência de
  expectativa usa a média sobre as posições dos pivôs, explicitada na análise.
- Aula 03 p. 42: 2^50 operações a 10^9/s equivalem a aproximadamente 13,03
  dias, não 35 mil anos. A fonte foi preservada e o cálculo foi refeito.

O registro arXiv:2609.00065 foi consultado para atribuição solicitada pela skill
SymPy. Autores e versão corrente v2 constam nas referências do relatório.
