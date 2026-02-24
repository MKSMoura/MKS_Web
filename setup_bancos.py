"""
Cria todos os bancos de dados e tabelas necessários.
Execute antes dos seeds: py setup_bancos.py
"""
import os, sys, hashlib, datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

import firebirdsql
from core.database import get_db_path, FB_HOST, FB_USER, FB_PASS

def criar_banco(nome):
    db_path = get_db_path(nome)
    if os.path.exists(db_path):
        print(f"  [{nome}] já existe, pulando criação.")
        return None
    conn = firebirdsql.create_database(
        host=FB_HOST, database=db_path,
        user=FB_USER, password=FB_PASS, charset="UTF8"
    )
    print(f"  [{nome}] criado em {db_path}")
    return conn

def abrir_banco(nome):
    db_path = get_db_path(nome)
    return firebirdsql.connect(
        host=FB_HOST, database=db_path,
        user=FB_USER, password=FB_PASS, charset="UTF8"
    )

def tabela_existe(conn, nome_tabela):
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM RDB$RELATIONS WHERE RDB$RELATION_NAME=?",
        (nome_tabela.upper(),)
    )
    return cur.fetchone()[0] > 0

# ─────────────────────────────────────────────
print("\n=== CLIENTES PF ===")
conn = criar_banco("clientes_pf")
if conn is None:
    conn = abrir_banco("clientes_pf")
cur = conn.cursor()
if not tabela_existe(conn, "CLIENTES_PF"):
    cur.execute("""
        CREATE TABLE CLIENTES_PF (
            ID INTEGER NOT NULL PRIMARY KEY,
            NOME VARCHAR(255), CPF VARCHAR(20),
            DATA_NASCIMENTO VARCHAR(20),
            RUA VARCHAR(255), NUMERO VARCHAR(20), COMPLEMENTO VARCHAR(100),
            BAIRRO VARCHAR(100), CIDADE VARCHAR(100), ESTADO VARCHAR(20), CEP VARCHAR(20),
            TELEFONE VARCHAR(50), CELULAR VARCHAR(50),
            EMAIL VARCHAR(150),
            DATA_CADASTRO VARCHAR(30), OBSERVACOES BLOB SUB_TYPE TEXT,
            DEPENDENTES BLOB SUB_TYPE TEXT, VERIFICADO VARCHAR(20)
        )""")
    conn.commit()
    print("  Tabela CLIENTES_PF criada.")
else:
    # Adicionar colunas novas se não existirem
    for col, ddl in [
        ("CELULAR",    "ALTER TABLE CLIENTES_PF ADD CELULAR VARCHAR(50)"),
        ("EMAIL",      "ALTER TABLE CLIENTES_PF ADD EMAIL VARCHAR(150)"),
        ("VERIFICADO", "ALTER TABLE CLIENTES_PF ADD VERIFICADO VARCHAR(20)"),
    ]:
        try:
            cur.execute(ddl); conn.commit()
            print(f"  Coluna {col} adicionada.")
        except Exception:
            pass
conn.close()

# ─────────────────────────────────────────────
print("\n=== CLIENTES PJ ===")
conn = criar_banco("clientes_pj")
if conn is None:
    conn = abrir_banco("clientes_pj")
cur = conn.cursor()
if not tabela_existe(conn, "CLIENTES_PJ"):
    cur.execute("""
        CREATE TABLE CLIENTES_PJ (
            ID INTEGER NOT NULL PRIMARY KEY,
            CNPJ VARCHAR(20), INSCRICAO_ESTADUAL VARCHAR(50),
            DATA_ABERTURA VARCHAR(20),
            RAZAO_SOCIAL VARCHAR(255), NOME_FANTASIA VARCHAR(255),
            TELEFONE VARCHAR(50), CELULAR VARCHAR(50), EMAIL VARCHAR(150),
            CEP VARCHAR(20), RUA VARCHAR(255), NUMERO VARCHAR(20),
            COMPLEMENTO VARCHAR(100), BAIRRO VARCHAR(100),
            CIDADE VARCHAR(100), ESTADO VARCHAR(20),
            OBSERVACOES BLOB SUB_TYPE TEXT,
            RESPONSAVEL_NOME VARCHAR(255), RESPONSAVEL_CPF VARCHAR(20),
            RESPONSAVEL_TELEFONE VARCHAR(50),
            CPF_RESPONSAVEL VARCHAR(20), NOME_RESPONSAVEL VARCHAR(255),
            TELEFONE_RESPONSAVEL VARCHAR(50),
            AUTORIZADOS BLOB SUB_TYPE TEXT,
            DATA_CADASTRO VARCHAR(30), VERIFICADO VARCHAR(20)
        )""")
    conn.commit()
    print("  Tabela CLIENTES_PJ criada.")
else:
    for col, ddl in [
        ("RESPONSAVEL_NOME",     "ALTER TABLE CLIENTES_PJ ADD RESPONSAVEL_NOME VARCHAR(255)"),
        ("RESPONSAVEL_CPF",      "ALTER TABLE CLIENTES_PJ ADD RESPONSAVEL_CPF VARCHAR(20)"),
        ("RESPONSAVEL_TELEFONE", "ALTER TABLE CLIENTES_PJ ADD RESPONSAVEL_TELEFONE VARCHAR(50)"),
        ("CELULAR",              "ALTER TABLE CLIENTES_PJ ADD CELULAR VARCHAR(50)"),
        ("EMAIL",                "ALTER TABLE CLIENTES_PJ ADD EMAIL VARCHAR(150)"),
        ("VERIFICADO",           "ALTER TABLE CLIENTES_PJ ADD VERIFICADO VARCHAR(20)"),
    ]:
        try:
            cur.execute(ddl); conn.commit()
            print(f"  Coluna {col} adicionada.")
        except Exception:
            pass
conn.close()

# ─────────────────────────────────────────────
print("\n=== PRODUTOS ===")
conn = criar_banco("produtos")
if conn is None:
    conn = abrir_banco("produtos")
cur = conn.cursor()
if not tabela_existe(conn, "PRODUTOS"):
    cur.execute("""
        CREATE TABLE PRODUTOS (
            ID INTEGER NOT NULL PRIMARY KEY,
            SKU VARCHAR(50), CODIGO_BARRAS VARCHAR(50),
            NOME VARCHAR(255), DESCRICAO BLOB SUB_TYPE TEXT,
            CATEGORIA VARCHAR(100), SUBCATEGORIA VARCHAR(100), MARCA VARCHAR(100),
            PRECO_CUSTO DECIMAL(12,2), PRECO_VENDA DECIMAL(12,2), MARGEM DECIMAL(8,2),
            UNIDADE_MEDIDA VARCHAR(20), QTD_EMBALAGEM INTEGER,
            FORNECEDOR_PRINCIPAL VARCHAR(255), CODIGO_FORNECEDOR VARCHAR(50),
            QTD_ESTOQUE DECIMAL(12,3), ESTOQUE_MINIMO DECIMAL(12,3), ESTOQUE_MAXIMO DECIMAL(12,3),
            PESO_BRUTO DECIMAL(10,3), PESO_LIQUIDO DECIMAL(10,3),
            ALTURA DECIMAL(10,3), LARGURA DECIMAL(10,3), COMPRIMENTO DECIMAL(10,3), VOLUME DECIMAL(10,3),
            STATUS VARCHAR(10) DEFAULT 'ativo',
            DATA_CADASTRO VARCHAR(30), DATA_ATUALIZACAO VARCHAR(30),
            USUARIO_RESPONSAVEL VARCHAR(100),
            PRODUTO_CONTROLADO CHAR(1) DEFAULT 'N',
            PERMITE_DESCONTO CHAR(1) DEFAULT 'S'
        )""")
    conn.commit()
    print("  Tabela PRODUTOS criada.")
conn.close()

# ─────────────────────────────────────────────
print("\n=== PEDIDOS ===")
conn = criar_banco("pedidos")
if conn is None:
    conn = abrir_banco("pedidos")
cur = conn.cursor()
if not tabela_existe(conn, "PEDIDOS"):
    cur.execute("""
        CREATE TABLE PEDIDOS (
            ID INTEGER NOT NULL PRIMARY KEY,
            NUMERO VARCHAR(20), DATA_PEDIDO VARCHAR(10), HORA_PEDIDO VARCHAR(8),
            STATUS VARCHAR(20) DEFAULT 'aberto',
            COD_VENDEDOR VARCHAR(20), NOME_VENDEDOR VARCHAR(150),
            COD_CLIENTE INTEGER, NOME_CLIENTE VARCHAR(255), CPF_CNPJ VARCHAR(20),
            SUBTOTAL DECIMAL(12,2) DEFAULT 0, DESCONTO DECIMAL(12,2) DEFAULT 0,
            ACRESCIMO DECIMAL(12,2) DEFAULT 0, TOTAL DECIMAL(12,2) DEFAULT 0,
            FORMA_PAGAMENTO VARCHAR(50), OBSERVACOES BLOB SUB_TYPE TEXT,
            USUARIO_CRIOU VARCHAR(100), USUARIO_ALTEROU VARCHAR(100),
            DATA_CRIACAO VARCHAR(30), DATA_ATUALIZACAO VARCHAR(30),
            LOG_ALTERACOES BLOB SUB_TYPE TEXT
        )""")
    conn.commit()
    print("  Tabela PEDIDOS criada.")
if not tabela_existe(conn, "PEDIDO_ITENS"):
    cur.execute("""
        CREATE TABLE PEDIDO_ITENS (
            ID INTEGER NOT NULL PRIMARY KEY,
            PEDIDO_ID INTEGER NOT NULL,
            SKU VARCHAR(50), NOME_PRODUTO VARCHAR(255),
            QUANTIDADE DECIMAL(12,3), UNIDADE VARCHAR(20),
            VALOR_UNITARIO DECIMAL(12,2), VALOR_TOTAL DECIMAL(12,2)
        )""")
    conn.commit()
    print("  Tabela PEDIDO_ITENS criada.")
conn.close()

# ─────────────────────────────────────────────
print("\n=== FORNECEDORES ===")
conn = criar_banco("fornecedores")
if conn is None:
    conn = abrir_banco("fornecedores")
cur = conn.cursor()
if not tabela_existe(conn, "FORNECEDORES"):
    cur.execute("""
        CREATE TABLE FORNECEDORES (
            ID INTEGER NOT NULL PRIMARY KEY,
            TIPO CHAR(2) DEFAULT 'PJ',
            RAZAO_SOCIAL VARCHAR(255), NOME_FANTASIA VARCHAR(150),
            CNPJ VARCHAR(20), CPF VARCHAR(15), IE VARCHAR(20),
            EMAIL VARCHAR(150), TELEFONE VARCHAR(20), CELULAR VARCHAR(20),
            CONTATO_NOME VARCHAR(150),
            CEP VARCHAR(10), RUA VARCHAR(255), NUMERO VARCHAR(20),
            COMPLEMENTO VARCHAR(100), BAIRRO VARCHAR(100),
            CIDADE VARCHAR(100), ESTADO VARCHAR(2),
            BANCO VARCHAR(100), AGENCIA VARCHAR(20), CONTA VARCHAR(30), PIX VARCHAR(150),
            PRAZO_PAGAMENTO INTEGER DEFAULT 30,
            CATEGORIA VARCHAR(100), STATUS VARCHAR(10) DEFAULT 'ativo',
            OBSERVACOES BLOB SUB_TYPE TEXT,
            DATA_CADASTRO VARCHAR(30), DATA_ATUALIZACAO VARCHAR(30)
        )""")
    conn.commit()
    print("  Tabela FORNECEDORES criada.")
conn.close()

# ─────────────────────────────────────────────
print("\n=== FINANCEIRO ===")
conn = criar_banco("financeiro")
if conn is None:
    conn = abrir_banco("financeiro")
cur = conn.cursor()
if not tabela_existe(conn, "CONTAS_RECEBER"):
    cur.execute("""
        CREATE TABLE CONTAS_RECEBER (
            ID INTEGER NOT NULL PRIMARY KEY,
            DESCRICAO VARCHAR(255),
            CLIENTE_ID INTEGER, NOME_CLIENTE VARCHAR(255),
            PEDIDO_ID INTEGER, NUMERO_PEDIDO VARCHAR(20),
            VALOR DECIMAL(12,2), VALOR_PAGO DECIMAL(12,2) DEFAULT 0,
            DATA_EMISSAO VARCHAR(10), DATA_VENCIMENTO VARCHAR(10), DATA_PAGAMENTO VARCHAR(10),
            STATUS VARCHAR(20) DEFAULT 'aberto',
            FORMA_PAGAMENTO VARCHAR(50), OBSERVACOES VARCHAR(500),
            USUARIO_LANCOU VARCHAR(100), DATA_LANCAMENTO VARCHAR(30)
        )""")
    conn.commit()
    print("  Tabela CONTAS_RECEBER criada.")
if not tabela_existe(conn, "CONTAS_PAGAR"):
    cur.execute("""
        CREATE TABLE CONTAS_PAGAR (
            ID INTEGER NOT NULL PRIMARY KEY,
            DESCRICAO VARCHAR(255),
            FORNECEDOR_ID INTEGER, NOME_FORNECEDOR VARCHAR(255),
            CATEGORIA VARCHAR(100),
            VALOR DECIMAL(12,2), VALOR_PAGO DECIMAL(12,2) DEFAULT 0,
            DATA_EMISSAO VARCHAR(10), DATA_VENCIMENTO VARCHAR(10), DATA_PAGAMENTO VARCHAR(10),
            STATUS VARCHAR(20) DEFAULT 'aberto',
            FORMA_PAGAMENTO VARCHAR(50), OBSERVACOES VARCHAR(500),
            USUARIO_LANCOU VARCHAR(100), DATA_LANCAMENTO VARCHAR(30)
        )""")
    conn.commit()
    print("  Tabela CONTAS_PAGAR criada.")
if not tabela_existe(conn, "CATEGORIAS_FIN"):
    cur.execute("""
        CREATE TABLE CATEGORIAS_FIN (
            ID INTEGER NOT NULL PRIMARY KEY,
            NOME VARCHAR(100), TIPO CHAR(1), COR VARCHAR(10)
        )""")
    conn.commit()
    for c in [(1,"Vendas","R","#4ade80"),(2,"Servicos","R","#38bdf8"),
              (3,"Outros","R","#a78bfa"),(4,"Fornecedores","P","#f87171"),
              (5,"Salarios","P","#fb923c"),(6,"Aluguel","P","#facc15"),
              (7,"Utilidades","P","#94a3b8"),(8,"Marketing","P","#f472b6"),
              (9,"Logistica","P","#34d399"),(10,"Impostos","P","#f97316")]:
        cur.execute("INSERT INTO CATEGORIAS_FIN (ID,NOME,TIPO,COR) VALUES (?,?,?,?)", c)
    conn.commit()
    print("  Tabela CATEGORIAS_FIN criada com categorias padrão.")
conn.close()

# ─────────────────────────────────────────────
print("\n=== USUARIOS ===")
conn = criar_banco("usuarios")
if conn is None:
    conn = abrir_banco("usuarios")
cur = conn.cursor()
if not tabela_existe(conn, "USUARIOS"):
    cur.execute("""
        CREATE TABLE USUARIOS (
            ID INTEGER NOT NULL PRIMARY KEY,
            LOGIN VARCHAR(50) NOT NULL, SENHA_HASH VARCHAR(255) NOT NULL,
            NOME VARCHAR(150), EMAIL VARCHAR(150),
            PERFIL VARCHAR(20) DEFAULT 'operador',
            ATIVO CHAR(1) DEFAULT 'S',
            PERMISSOES BLOB SUB_TYPE TEXT,
            TROCAR_SENHA CHAR(1) DEFAULT 'N',
            DATA_CADASTRO VARCHAR(30), ULTIMO_ACESSO VARCHAR(30)
        )""")
    conn.commit()
    print("  Tabela USUARIOS criada.")
else:
    # Garantir coluna TROCAR_SENHA em bancos existentes
    try:
        cur.execute("ALTER TABLE USUARIOS ADD TROCAR_SENHA CHAR(1) DEFAULT 'N'")
        conn.commit()
        print("  Coluna TROCAR_SENHA adicionada.")
    except Exception:
        pass
conn.close()

print("\n✓ Todos os bancos prontos! Agora rode: py seed_tudo.py\n")
