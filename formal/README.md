# Diagnóstico Lean e checkpoint

Nenhum arquivo Lean foi criado: `lean`, `lake` e `elan` não foram encontrados
no PATH. Não há toolchain fixada, configuração Lake ou dependência Mathlib.
Ver `docs/ambiente.json` para as tentativas de versão e seus erros.

A skill lean4-doctor foi aplicada. Sem `lean4-codex.env`, o plugin opcional
resolve para `vendor/lean4-plugin`, inexistente; os guias opcionais foram
registrados como ausentes. Não há scripts de plugin a executar.

As skills lean4-formalize, lean4-prove e lean4-checkpoint foram lidas; não
foram substituídas por uma skill de aprendizado. Formalização e prova não
foram iniciadas sem ambiente utilizável. A passagem por checkpoint registra:

- Compilação: não executável por ausência de Lean/Lake no PATH.
- Escopo de declarações reivindicadas: vazio; nenhuma prova Lean reivindicada.
- `sorry`/axiomas locais: não há fontes Lean; isto não constitui auditoria
  transitiva do kernel. `#print axioms` não foi executado.
- Versões Lean/Lake/Mathlib: não disponíveis neste diagnóstico.

Se o ambiente for disponibilizado, formalizar a contagem triangular e o
tamanho do bitmap, compilar primeiro cada arquivo com `lake env lean`, depois
`lake build`. Criar auditoria que importe os módulos e execute `#print axioms`
para cada definição/lema em escopo, registrando `sorryAx`, axiomas customizados
e hipóteses lógicas. Não há motivo para modelar segundos de hardware aqui.
