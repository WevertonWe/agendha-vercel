# Guia de Scripts do Sistema Agendha

Para melhorar a organização e manutenção, os scripts utilitários foram organizados em subpastas dentro de `app/scripts/`.

## Estrutura de Pastas

### 📂 /banco_de_dados
Scripts relacionados à estrutura (DDL), integridade e correções do banco de dados SQLite.
*   `create_audit_table.py`: Cria a tabela de auditoria se não existir.
*   `create_user_bruna.py`: Script auxiliar para criação de usuário.
*   `fix_db_pedreiros.py`: Adiciona coluna `pedreiro_id` em beneficiários.
*   `fix_financeiro.py`: Cria tabelas do módulo financeiro (Projetos, Rubricas, Lançamentos).
*   `fix_lowercase.py`: Normaliza dados para lowercase.
*   `fix_map_owners.py`: Ajusta owners do mapa.
*   `verificar_db.py`: Lista tabelas e verifica conexão básica com o banco.

### 📂 /manutencao
Scripts de rotina, verificação de logs e processos preventivos.
*   `check_logs.py`: Verifica logs de acesso recentes.
*   `check_time.py`: Valida consistência de timezone (Bahia) nos logs.
*   `safeguard_db.py`: Cria backup de segurança do banco.
*   `verify_backup.py`: Testa o serviço de backup criando e verificando snapshots.

### 📂 /debug_testes
Scripts utilizados para diagnóstico de erros e testes de estresse/performance.
*   `debug_500.py`: Simula requisições para investigar erros 500.
*   `debug_banco.py`: Inspeção detalhada do banco e tabelas.
*   `debug_db_connection.py`: Testa o pool de conexões com o banco.
*   `stress_nav.py`: Teste de carga em navegação (simula usuários).
*   `stress_test_audit.py`: Teste de carga e integridade na auditoria.
*   `stress_test_connection.py`: Teste de concorrência no dashboard de auditoria.
*   `test_persistence.py`: Verifica se o banco na raiz está persistindo dados corretamente.
*   `teste_banco.py`: Verificação geral do arquivo do banco.
*   `teste_login.py`: Testa validação de senha (bcrypt) manualmente.

### 📂 /migracoes
Scripts de ETL (Extract, Transform, Load) e importação de dados legados.
*   *(Vazio inicialmente - destinado a scripts de importação de CSV/Drive)*

---

## Como Executar

Com a nova estrutura, você deve executar os scripts **a partir da raiz do projeto**, ajustando o caminho.

**Exemplos:**

*   Verificar o banco:
    ```bash
    python app/scripts/banco_de_dados/verificar_db.py
    ```

*   Testar persistência:
    ```bash
    python app/scripts/debug_testes/test_persistence.py
    ```

*   Rodar manutenção:
    ```bash
    python app/scripts/manutencao/check_logs.py
    ```

Os scripts foram ajustados para localizar automaticamente o `agendha.db` na raiz do projeto.
