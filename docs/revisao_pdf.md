# Revisão do PDF

Arquivo: `relatorios_latex/relatorio.pdf`, 17 páginas A4. Compilado com
Tectonic 0.17.0 a partir de LaTeX gerado por Pandoc 3.13. O processo terminou
com código zero; a saída está em `compilacao_pdf.txt`.

Todas as 17 páginas foram renderizadas com Poppler 25.07.0 a 100 dpi e
inspecionadas nas cinco folhas de contato de `tmp/pdfs/`. Foram revistos
sumário, títulos, textos, equações de contagem e probabilidade, a tabela de
bogosort, a tabela comparativa, os tempos nas três escalas, as seis distribuições,
os cinco candidatos de lote NumPy e três figuras. A tabela comparativa tem
cabeçalho próprio na página seguinte à introdução da seção; suas linhas
não foram cortadas. A figura puramente teórica é identificada como tal; as
outras duas separam as observações de tempo das extrapolações. A comparação
completa distingue dois pontos/séries medidos e oito modelos tracejados.

Na primeira compilação havia duas caixas horizontais excedentes. Foram
corrigidas com quebra permitida em caminhos e equações grandes em modo
destacado. Também foi removido um pacote desnecessário que trazia um aviso
de codificação em sua própria fonte. A configuração Fontconfig foi criada
localmente para eliminar a ausência de configuração padrão.

Na atualização com resultados houve também um acento usado fora de `text`
em um subscrito matemático e um trecho de nomes de funções que excedia a
linha. Ambos foram corrigidos; a impressão do log no console Windows foi
ajustada para UTF-8. As páginas foram renderizadas novamente após as correções.

Na versão final:

- Zero avisos `Overfull` ou `Missing character` no log TeX.
- Um aviso `Underfull` de espaçamento em parágrafo, sem corte ou sobreposição
  observado. Não se afirma log inteiramente livre de avisos.
- Dependência explícita das fontes Cambria, Calibri e Consolas do Windows;
  Tectonic avisa sobre os caminhos absolutos dessas fontes. Reproduzir em
  outro sistema exige disponibilizá-las ou adaptar a seleção.
- A extração de texto não contém U+FFFD; a auditoria Poppler encontrou 7.080
  palavras dentro dos limites físicos das páginas na etapa inicial. Na versão
  atual são 8.627 palavras. Isso complementa, mas não
  substitui, a inspeção visual.

O marcador de autoria da skill PDF não estava instalado; a tentativa
`node container_tools/mark_artifact_operation_started.mjs --operation-kind create --expected-output-count 1 --output-format pdf`
falhou com `MODULE_NOT_FOUND`. Não foi criado um substituto para simular
sucesso. O build e a revisão visual do artefato real foram concluídos pelos
comandos registrados.

O marcador também foi tentado na etapa de edição com `--operation-kind edit`
e continuou ausente. A compilação TeX e a inspeção do PDF real foram executadas.

Esta validação trata do documento. As evidências de implementação e medições
ficam em `dados/testes_resultado.json`, nos CSVs e em `dados/memoria_c.json`.
O orçamento C é um limite conservador do build local e os tempos são locais;
essa revisão de layout não transfere tais resultados para outro alvo nem
constitui prova Lean.
