## BDSCore

BDSCore é a biblioteca oficial da BDS DataSolution para integração com APIs de dados de mercado e dados proprietários.

### Principais recursos
- Autenticação via chave de API
- Suporte a múltiplas URLs base para diferentes serviços (datapack, datamanagement, dataflex)
- Reutilização de sessão HTTP para eficiência e performance
- Métodos organizados por serviço: `bds.datapack.getFX()`, `bds.datamanagement.getValues()`, entre outros
- Tratamento robusto de erros, incluindo mensagens detalhadas e Correlation ID
- Documentação integrada via docstrings para fácil uso em IDEs

### Instalação

```bash
pip install bdscore
```

### Exemplo de uso

```python
from bdscore import BDSCore

bds = BDSCore(api_key="SUA_CHAVE_AQUI")
fx = bds.datapack.getFX(":all", "2023-10-01", "2023-10-31")
equities = bds.datapack.getEquitiesB3(":all", "2023-10-01", "2023-10-31")
print(equities)
```

### Sobre

Ideal para desenvolvedores que precisam acessar dados financeiros, sincronizar usuários e integrar sistemas com a plataforma BDS DataSolution.
