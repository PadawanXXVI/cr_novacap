
# ✅ Roteiro de Testes – Sistema de Processos (CR/NOVACAP)

---

## 👤 1. Cadastro e Recuperação de Acesso

- [ ] Realizar cadastro de novo usuário
- [ ] Verificar se o novo usuário aparece no painel admin (não aprovado)
- [ ] Aprovar usuário e confirmar login bem-sucedido
- [ ] Testar redefinição de senha com dados válidos
- [ ] Testar redefinição com dados incorretos (erro esperado)

---

## 🔐 2. Autenticação de Usuários

- [ ] Testar login com credenciais válidas
- [ ] Testar login com senha incorreta
- [ ] Testar login com usuário não aprovado
- [ ] Testar login com usuário bloqueado
- [ ] Testar acesso a rota protegida sem login (redireciona para login)
- [ ] Testar logout e redirecionamento correto

---

## 🗂 3. Dashboard de Processos

- [ ] Verificar se todos os cards numéricos aparecem corretamente:
  - Total de Processos
  - Atendidos
  - SECRE vs CR
  - Diretoria das Cidades vs Diretoria de Obras
  - Devolvidos à RA
  - SGIA
- [ ] Conferir responsividade da tela
- [ ] Testar botão de navegação para Cadastro de Processo
- [ ] Testar botão para Listar Processos
- [ ] Testar botão Sair do Sistema

---

## 📝 4. Cadastro de Processo

- [ ] Verificar se o campo “Número do Processo” aceita máscara e número puro
- [ ] Testar cadastro com todas as datas preenchidas corretamente
- [ ] Verificar se o sistema rejeita duplicidade de número de processo
- [ ] Testar checkbox: vistoria, ofício, encerramento pela RA
- [ ] Testar campo de status inicial, RA e tipo de demanda
- [ ] Confirmar redirecionamento após sucesso

---

## 🔍 5. Listagem e Visualização

- [ ] Pesquisar por número de processo (parcial e completo)
- [ ] Filtrar por status
- [ ] Verificar se a lista mostra RA, tipo e status atual
- [ ] Clicar em visualizar e conferir:
  - Dados gerais
  - Última observação
  - Histórico de movimentações (se houver)

---

## ✏️ 6. Alteração de Processo

- [ ] Escolher processo e mudar status
- [ ] Informar observação, responsável técnico e data manualmente
- [ ] Verificar se o novo status atualiza corretamente
- [ ] Confirmar que nova movimentação aparece no histórico

---

## 📤 7. Relatórios e Exportações

- [ ] Acessar página de relatórios gerenciais
- [ ] Verificar totais: processos e tramitações
- [ ] Testar exportação de tramitações filtradas por:
  - [ ] RA
  - [ ] Técnico
  - [ ] Status
  - [ ] Período (início e fim)
  - [ ] Combinação de filtros
- [ ] Verificar formato do CSV gerado
- [ ] Testar leitura do arquivo no Excel

---

## 🎨 8. Interface e Responsividade

- [ ] Conferir centralização dos elementos principais (cards, formulários, botões)
- [ ] Testar tela em:
  - [ ] Desktop
  - [ ] Tablet
  - [ ] Celular
  - [ ] TV (projetor ou emulador)
- [ ] Validar identidade visual da NOVACAP (fundo, cores, fontes)
