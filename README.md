# Protheus Automation Bot

Este projeto é uma automação desenvolvida em Python utilizando a biblioteca **Playwright** para interagir com o sistema ERP TOTVS Protheus. 

O objetivo principal desta automação é realizar atualizações em massa no cadastro de produtos, lendo dados de um arquivo CSV e aplicando as alterações na interface web do Protheus.

## Funcionalidades

- **Login Automático**: Realiza login no portal Protheus e seleciona a filial e módulo automaticamente.
- **Processamento em Lote**: Lê um arquivo `data.csv` contendo códigos de produtos e novos parâmetros fiscais.
- **Busca e Atualização**: Pesquisa cada produto no grid, abre a tela de alteração e atualiza os campos "Grupo de Tributação" e "NCM".
- **Resiliência**: Possui mecanismos de recuperação de erros, como tentativa de reabrir modais ou recarregar a página em caso de falhas, além de logs de erro.

## Estrutura do Projeto

- `main.py`: Ponto de entrada da aplicação. Gerencia o fluxo principal.
- `protheus_bot.py`: Contém a classe `ProtheusBot` com toda a lógica de interação com o navegador.
- `config.py`: Arquivo de configuração (utiliza variáveis de ambiente).
- `csv_processor.py`: Utilitário para leitura do arquivo CSV.
- `data.csv`: Arquivo de exemplo com os dados a serem processados.

## Pré-requisitos

- Python 3.8+
- Playwright

## Instalação

1. Clone o repositório.
2. Instale as dependências:
   ```bash
   pip install playwright
   playwright install
   ```

## Configuração

Por segurança, as credenciais e URLs não estão hardcoded no projeto. Você deve configurar as seguintes variáveis de ambiente ou editar o arquivo `config.py` para testes locais:

- `PROTHEUS_USER`: Seu usuário do Protheus.
- `PROTHEUS_PASSWORD`: Sua senha.
- `PROTHEUS_URL`: URL de acesso ao WebApp do Protheus.

## Como Executar

1. Prepare o arquivo `data.csv` com as colunas: `codigo_produto`, `novo_grtrib`, `Pos.IPI/NCM`.
2. Execute o script principal:
   ```bash
   python main.py
   ```

## Aviso Legal

Este código é para fins demonstrativos e educacionais. As informações sensíveis foram removidas e substituídas por dados fictícios.
