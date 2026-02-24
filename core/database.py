import firebirdsql
import os
from contextlib import contextmanager

FB_HOST   = "localhost"
FB_USER   = "SYSDBA"
FB_PASS   = "masterkey"
DB_FOLDER = os.path.abspath("data")
os.makedirs(DB_FOLDER, exist_ok=True)

def get_db_path(category: str) -> str:
    return os.path.join(DB_FOLDER, f"{category.lower()}.fdb")

def init_db(category: str):
    db_path = get_db_path(category)
    if os.path.exists(db_path):
        return
    conn = firebirdsql.create_database(
        host=FB_HOST, database=db_path,
        user=FB_USER, password=FB_PASS, charset='UTF8'
    )
    cursor = conn.cursor()
    if category.lower() == "clientes_pf":
        cursor.execute("""
            CREATE TABLE CLIENTES_PF (
                ID INTEGER NOT NULL PRIMARY KEY,
                NOME VARCHAR(255), CPF VARCHAR(20),
                DATA_NASCIMENTO VARCHAR(20), RUA VARCHAR(255),
                NUMERO VARCHAR(20), COMPLEMENTO VARCHAR(100),
                BAIRRO VARCHAR(100), CIDADE VARCHAR(100),
                ESTADO VARCHAR(20), CEP VARCHAR(20),
                TELEFONE VARCHAR(50), DATA_CADASTRO VARCHAR(30),
                OBSERVACOES BLOB SUB_TYPE TEXT,
                DEPENDENTES BLOB SUB_TYPE TEXT
            )""")
    elif category.lower() == "clientes_pj":
        cursor.execute("""
            CREATE TABLE CLIENTES_PJ (
                ID INTEGER NOT NULL PRIMARY KEY,
                CNPJ VARCHAR(20), INSCRICAO_ESTADUAL VARCHAR(50),
                DATA_ABERTURA VARCHAR(20), RAZAO_SOCIAL VARCHAR(255),
                NOME_FANTASIA VARCHAR(255), TELEFONE VARCHAR(50),
                CEP VARCHAR(20), RUA VARCHAR(255), NUMERO VARCHAR(20),
                COMPLEMENTO VARCHAR(100), BAIRRO VARCHAR(100),
                CIDADE VARCHAR(100), ESTADO VARCHAR(20),
                OBSERVACOES BLOB SUB_TYPE TEXT,
                CPF_RESPONSAVEL VARCHAR(20), NOME_RESPONSAVEL VARCHAR(255),
                TELEFONE_RESPONSAVEL VARCHAR(50),
                AUTORIZADOS BLOB SUB_TYPE TEXT, DATA_CADASTRO VARCHAR(30)
            )""")
    conn.commit()
    conn.close()

def init_produtos():
    """Inicializa o banco de produtos (separado dos clientes)."""
    from core.database import get_db_path, FB_HOST, FB_USER, FB_PASS
    import os, firebirdsql
    db_path = get_db_path("produtos")
    if os.path.exists(db_path):
        return
    conn = firebirdsql.create_database(
        host=FB_HOST, database=db_path,
        user=FB_USER, password=FB_PASS, charset="UTF8"
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE PRODUTOS (
            ID INTEGER NOT NULL PRIMARY KEY,
            SKU VARCHAR(50),
            CODIGO_BARRAS VARCHAR(50),
            NOME VARCHAR(255),
            DESCRICAO BLOB SUB_TYPE TEXT,
            CATEGORIA VARCHAR(100),
            SUBCATEGORIA VARCHAR(100),
            MARCA VARCHAR(100),
            PRECO_CUSTO DECIMAL(12,2),
            PRECO_VENDA DECIMAL(12,2),
            MARGEM DECIMAL(8,2),
            UNIDADE_MEDIDA VARCHAR(20),
            QTD_EMBALAGEM INTEGER,
            FORNECEDOR_PRINCIPAL VARCHAR(255),
            CODIGO_FORNECEDOR VARCHAR(50),
            QTD_ESTOQUE DECIMAL(12,3),
            ESTOQUE_MINIMO DECIMAL(12,3),
            ESTOQUE_MAXIMO DECIMAL(12,3),
            PESO_BRUTO DECIMAL(10,3),
            PESO_LIQUIDO DECIMAL(10,3),
            ALTURA DECIMAL(10,3),
            LARGURA DECIMAL(10,3),
            COMPRIMENTO DECIMAL(10,3),
            VOLUME DECIMAL(10,3),
            STATUS VARCHAR(10) DEFAULT 'ativo',
            DATA_CADASTRO VARCHAR(30),
            DATA_ATUALIZACAO VARCHAR(30),
            USUARIO_RESPONSAVEL VARCHAR(100),
            PRODUTO_CONTROLADO CHAR(1) DEFAULT 'N',
            PERMITE_DESCONTO CHAR(1) DEFAULT 'S'
        )""")
    conn.commit()
    conn.close()

class FirebirdDictCursor:
    def __init__(self, cursor):
        self._cursor = cursor
    def execute(self, query, params=None):
        if params is not None and len(params) > 0:
            return self._cursor.execute(query, tuple(params) if isinstance(params, list) else params)
        return self._cursor.execute(query)
    def fetchall(self):
        rows = self._cursor.fetchall()
        if not rows: return []
        cols = [d[0].lower() for d in self._cursor.description]
        return [dict(zip(cols, r)) for r in rows]
    def fetchone(self):
        row = self._cursor.fetchone()
        if not row: return None
        cols = [d[0].lower() for d in self._cursor.description]
        return dict(zip(cols, row))
    def __getattr__(self, n): return getattr(self._cursor, n)

@contextmanager
def get_connection(category: str):
    db_path = get_db_path(category)
    if not os.path.exists(db_path):
        init_db(category)
    conn = firebirdsql.connect(
        host=FB_HOST, database=db_path,
        user=FB_USER, password=FB_PASS, charset='UTF8'
    )
    orig = conn.cursor
    conn.cursor = lambda *a, **k: FirebirdDictCursor(orig(*a, **k))
    try:
        yield conn
    except Exception:
        conn.rollback(); raise
    finally:
        conn.close()
