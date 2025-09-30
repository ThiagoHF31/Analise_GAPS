# 🤝 Guia de Colaboração - Analise_GAPS

## 📋 Estrutura das Branches

### 🏠 `main` (Branch Principal)
- **Propósito**: Código estável e pronto para produção
- **Acesso**: Código atual funcional do WIN$N Financial Analyzer
- **Status**: ✅ Sistema completo implementado

### 🚀 `thay-development` (Branch do Thay)
- **Propósito**: Desenvolvimento e experimentação do Thay
- **Acesso**: Branch dedicada para desenvolvimento colaborativo
- **Recursos**: Inclui README_THAY.md com guias específicos

## 🔄 Workflow de Colaboração

### Para o Thay:

1. **Clone e acesse sua branch**:
```bash
git clone https://github.com/ThiagoHF31/Analise_GAPS.git
cd Analise_GAPS
git checkout thay-development
```

2. **Crie feature branches**:
```bash
git checkout -b feature/nova-analise
# Desenvolva suas modificações
git add .
git commit -m "✨ Add: nova análise de volatilidade"
git push origin feature/nova-analise
```

3. **Crie Pull Request**:
- No GitHub, crie PR de `feature/nova-analise` → `thay-development`
- Após aprovação, merge para `thay-development`

### Para merge na main:

1. **Teste completamente na thay-development**
2. **Crie PR de `thay-development` → `main`**
3. **Review e aprovação**
4. **Merge na main**

## 🛠️ Desenvolvimento Sugerido

### 🎯 Próximas funcionalidades

1. **Análise Sazonal**:
   - Gaps por dia da semana
   - Padrões mensais
   - Análise de volatilidade sazonal

2. **Estratégias Avançadas**:
   - Backtest automatizado
   - Stop loss dinâmico
   - Risk management

3. **Machine Learning**:
   - Predição de fechamento de gaps
   - Classificação de padrões
   - Features engineering

4. **Interface Web**:
   - Dashboard interativo
   - Upload de dados via web
   - Relatórios em tempo real

## 📊 Dados e Estrutura

### Arquivos importantes:
- `run.py` - Executar análise completa
- `config.py` - Configurações modificáveis
- `exemplos_uso.py` - Exemplos de análises customizadas
- `src/` - Módulos do sistema

### Dados gerados:
- `data/processed/dados_limpos_finais.csv` - Dataset final
- `output/graphs/` - Gráficos gerados
- `output/reports/` - Relatórios detalhados

## 🔧 Convenções de Commit

Use prefixos nos commits:
- `✨ Add:` - Nova funcionalidade
- `🐛 Fix:` - Correção de bug
- `📝 Docs:` - Documentação
- `♻️ Refactor:` - Refatoração
- `🎨 Style:` - Formatação
- `🚀 Deploy:` - Deploy/release
- `🧪 Test:` - Testes

## 🚨 Regras importantes

1. **Sempre teste antes de commit**:
   ```bash
   python run.py  # Deve executar sem erros
   ```

2. **Documente modificações**:
   - Atualize README se necessário
   - Comente código complexo
   - Mantenha config.py atualizado

3. **Não modifique main diretamente**:
   - Use sempre branches de feature
   - Passe pela thay-development primeiro

## 📞 Contato e Suporte

- **Issues**: Use GitHub Issues para bugs e sugestões
- **Discussions**: Use GitHub Discussions para dúvidas
- **Code Review**: Sempre solicite review nos PRs

---
**Happy Collaborative Coding!** 🚀🤝