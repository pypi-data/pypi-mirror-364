## BDSCore

BDSCore é a biblioteca oficial da BDS DataSolution para integração com APIs de dados de mercado e dados proprietários.

### Principais recursos
- Autenticação via chave de API BDS
- Suporte a múltiplas URLs base para diferentes serviços (DataPack, DataManagement, DataFlex)
- Reutilização de sessão HTTP para eficiência e performance
- Métodos organizados por serviço: `bds.datapack.getFX()`, `bds.datamanagement.getValues()`, entre outros
- Tratamento robusto de erros, incluindo mensagens detalhadas
- Documentação integrada via docstrings para fácil uso em IDEs

### Instalação

```bash
pip install bdscore
```

### Quick Start

```python
from bdscore import BDSCore

bds = BDSCore(api_key="SUA_CHAVE_AQUI")
fx = bds.datapack.getFX(":all", "2023-10-01", "2023-10-31")
equities = bds.datapack.getEquitiesB3(":all", "2023-10-01", "2023-10-31")
print(equities)
```

### Sobre

A BDS DataSolution é especialista em dados, informações e geradora de insights para o mercado financeiro. Utiliza as mais eficientes tecnologias de Inteligência Artificial para acelerar e potencializar decisões.

O propósito da biblioteca **BDSCore** é justamente conectar você, desenvolvedor ou empresa, a esse ecossistema de dados e inteligência da BDS. Com ela, você pode acessar de forma simples, segura e eficiente todos os dados, APIs e funcionalidades oferecidas pelo BDS Market Data Hub, integrando diretamente os recursos de Big Data, Analytics e IA ao seu sistema ou aplicação.

Desenvolvemos um novo modelo de negócios, o BDS Market Data Hub, que oferece soluções completas de Big Data as a Service (BDaaS), Platform as a Service (PaaS), experiência em Analytics e Inteligência Artificial. A biblioteca BDSCore é o canal oficial para essa integração, permitindo que você consuma, compartilhe e monetize dados e algoritmos dentro da plataforma.

Além de oferecer soluções flexíveis e customizáveis, o BDS Market Data Hub permite que nossos parceiros utilizem os dados e disponibilizem na nossa solução, de maneira gratuita ou cobrando, novos dados, informações, análises ou algoritmos. O objetivo maior é trazer parceiros especialistas, monetizar seus trabalhos, ampliar a oferta e agregar muito mais valor às informações para potencializar as suas decisões. A BDSCore facilita esse processo, tornando a integração técnica rápida e padronizada.

### Contato

- Site: [bdsdatasolution.com.br](https://bdsdatasolution.com.br)
- E-mail: comercial@bdsdatasolution.com.br
