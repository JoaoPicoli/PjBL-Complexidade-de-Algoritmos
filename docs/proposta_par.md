# Decisão técnica da equipe: par 2/5

**Estado em 11/11/2026: implementação local autorizada pelo usuário.** A equipe
adotou as estratégias 2/5 e saída crescente nas duas versões. Esta decisão
não é aprovação do professor. O requisito de aprovação prévia do enunciado
(seções 3 e 4.3) continua sem evidência de atendimento; o usuário informou que
não pode consultar o professor agora e autorizou expressamente a continuidade
local. Nenhum contato com o professor foi feito.

A autorização posterior substitui a interrupção local da etapa anterior,
sem reclassificar a decisão da equipe como autorização docente.

## Embarca: estratégia 2, heapsort iterativo e varredura

Ordenar o vetor residente de inteiros sem sinal de 16 bits com heapsort
iterativo in-place. Em seguida, compactar os valores distintos no início do
mesmo vetor, devolvendo o comprimento lógico da saída.

- Tempo: limite determinístico O(n log n), mais Θ(n) para a varredura.
- Heap auxiliar: zero alocações; pilha: O(1), sem recursão.
- Entrada: 2n bytes; a saída reutiliza seu prefixo, sem segundo vetor.
- Corretude exata; saída crescente, sem preservar a ordem original.
- A classe O(1) sozinha não comprova 256 bytes. O build GCC 16.2.0 local foi
  instrumentado e auditado: heap zero, estático auxiliar gravável zero,
  frame de 56 bytes e limite conservador de 104 bytes com convenção Win64
  e alinhamento. Repetir a auditoria no alvo embarcado antes de transferir
  esse resultado para outro sensor/ABI.

É preferível à força bruta pelo crescimento do tempo. Bitmap requer 8.192 bytes,
32 vezes o limite. Hash e AVL armazenam até 65.536 chaves. Quicksort recursivo
introduz pilha dependente de n; mergesort convencional reserva Θ(n) de heap.
O plano exclui qsort de memória interna não caracterizada.

## Datacenter: estratégia 5, bitmap exato em Python

Alocar um bitmap empacotado de 65.536 bits (8.192 bytes). Para cada leitura,
marcar o bit correspondente, acumulando OR para índices de byte repetidos
com `numpy.bitwise_or.at`. Após a marcação, percorrer os bits do domínio
em ordem e produzir um vetor `uint16` crescente. Usar lotes para limitar
temporários; comparar tamanho de lote e memória antes da seleção final.
Não usar `set` ou `numpy.unique` no algoritmo. Oráculos independentes fora
do cronômetro podem usar essas estruturas nos testes.

- Tempo: Θ(n + U + d), com U = 65.536 e d ≤ min(n,U); portanto Θ(n) para
  U fixo e n ≥ 1.
- Heap: bitmap Θ(U/8), buffers de lote Θ(min(n,c)) e temporários de emissão
  Θ(U+d), além dos cabeçalhos; medir picos e separar a saída. Pilha O(1)
  em profundidade de chamadas, sem atribuir a ela bytes não medidos.
- Saída compacta de uint16: 2d bytes, no máximo 131.072 bytes. Uma lista de
  objetos Python tem outro custo e deverá ser medida separadamente.
- Determinístico e exato, sem colisões nem falsos positivos.

O domínio permite endereçamento direto e elimina o pior caso de colisões do
hash e os fatores logarítmicos da AVL e da ordenação. Bloom precisaria tolerar
perda de valores e, com 1% de falsos positivos e domínio completo, usa mais
bits que este bitmap exato.

Foram medidos n = 10³, 10⁵ e 10⁷ com entrada previamente gerada, cinco
repetições, incluindo inicialização do bitmap e produção da saída, excluindo
geração/cópia. O lote selecionado é 65.536; pico rastreado de 730.080 bytes
com domínio completo, incluindo a saída. Em n=10⁷, todas as 30 observações
locais do bitmap ficaram abaixo de 2 s (máximo 0,1026721 s). A máquina local
não foi identificada como a referência da disciplina: o prazo nela continua
sem comprovação. Ver `resultados_locais.md` para método e limitações.

## Registro e condição acadêmica

Decisão e autorização: mensagem do usuário nesta sessão em 11/11/2026:
"Adote o par 2/5 como decisão técnica da equipe" e "Autorizo a continuidade
da implementação local com esse par". Contrato posterior explícito: saída
crescente nas duas implementações. Se houver aprovação docente posteriormente,
registrar o par, data e referência verificável. Até lá, assinalar a pendência
acadêmica sem impedir o trabalho local já autorizado.

Os custos, provas e alternativas estão em `analise_teorica.md`; o protocolo
experimental está em `plano_experimental.md`.
