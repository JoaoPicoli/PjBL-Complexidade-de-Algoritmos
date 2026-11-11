-- Caminhos longos podem quebrar em separadores sem alterar o texto exibido.
function Code(el)
  local escapes = {
    ['\\'] = '\\textbackslash{}', ['{'] = '\\{', ['}'] = '\\}',
    ['_'] = '\\_', ['%'] = '\\%', ['&'] = '\\&', ['#'] = '\\#',
    ['$'] = '\\$', ['^'] = '\\textasciicircum{}', ['~'] = '\\textasciitilde{}'
  }
  local pieces = {}
  for i = 1, #el.text do
    local c = el.text:sub(i, i)
    table.insert(pieces, escapes[c] or c)
    if c == '/' or c == '_' or c == '-' or c == '.' then
      table.insert(pieces, '\\allowbreak{}')
    end
  end
  return pandoc.RawInline('latex', '\\texttt{' .. table.concat(pieces) .. '}')
end
