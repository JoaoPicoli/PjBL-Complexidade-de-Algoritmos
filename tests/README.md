# Testes de corretude e instrumentação

Os oito casos de `casos_manuais.json` têm no máximo dez elementos. Os conjuntos,
a ordem crescente e a ordem de primeira aparição podem ser conferidos à mão.
Os oito casos foram executados contra as duas implementações com saída
crescente, por autorização local do usuário.

Execute `python src/apoio/executar_testes.py` após o build C. São nove testes
unittest: oito oráculos manuais; 364 sequências exaustivas de comprimento 0..5
sobre três valores; 40 entradas aleatórias; domínio completo embaralhado e
repetido; guardas antes/depois do vetor C; ponteiro nulo para n=0; contrato de
tipos; acumulação de vários bits no mesmo byte; controle positivo de alocação
em DLL separada. Os oráculos usam set/unique só fora das implementações.

Também se valida cada uma das 190 saídas medidas no driver de benchmark.
Resultados em `dados/testes_resultado.json` e `dados/testes_execucao.txt`.
