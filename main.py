from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
from core.database import init_db, get_connection
import datetime, hashlib, json

app = Flask(__name__)
app.secret_key = "mks-secret-2026"

import json as _json
app.jinja_env.filters['from_json'] = lambda s: _json.loads(s) if s else {}

init_db("clientes_pf")
init_db("clientes_pj")

def init_produtos():
    import os, firebirdsql
    from core.database import get_db_path
    db_path = get_db_path("produtos")
    if not os.path.exists(db_path):
        conn = firebirdsql.create_database(host="localhost",database=db_path,user="SYSDBA",password="masterkey",charset="UTF8")
        cur = conn.cursor()
        cur.execute("""CREATE TABLE PRODUTOS (
            ID INTEGER NOT NULL PRIMARY KEY, SKU VARCHAR(50), CODIGO_BARRAS VARCHAR(50),
            NOME VARCHAR(255), DESCRICAO BLOB SUB_TYPE TEXT,
            CATEGORIA VARCHAR(100), SUBCATEGORIA VARCHAR(100), MARCA VARCHAR(100),
            PRECO_CUSTO DECIMAL(12,2), PRECO_VENDA DECIMAL(12,2), MARGEM DECIMAL(8,2),
            UNIDADE_MEDIDA VARCHAR(20), QTD_EMBALAGEM INTEGER,
            FORNECEDOR_PRINCIPAL VARCHAR(255), CODIGO_FORNECEDOR VARCHAR(50),
            QTD_ESTOQUE DECIMAL(12,3), ESTOQUE_MINIMO DECIMAL(12,3), ESTOQUE_MAXIMO DECIMAL(12,3),
            PESO_BRUTO DECIMAL(10,3), PESO_LIQUIDO DECIMAL(10,3),
            ALTURA DECIMAL(10,3), LARGURA DECIMAL(10,3), COMPRIMENTO DECIMAL(10,3), VOLUME DECIMAL(10,3),
            STATUS VARCHAR(10) DEFAULT 'ativo',
            DATA_CADASTRO VARCHAR(30), DATA_ATUALIZACAO VARCHAR(30), USUARIO_RESPONSAVEL VARCHAR(100),
            PRODUTO_CONTROLADO CHAR(1) DEFAULT 'N', PERMITE_DESCONTO CHAR(1) DEFAULT 'S'
        )""")
        conn.commit(); conn.close()

init_produtos()

def init_pedidos():
    import os, firebirdsql
    from core.database import get_db_path
    db_path = get_db_path("pedidos")
    if not os.path.exists(db_path):
        conn = firebirdsql.create_database(host="localhost",database=db_path,user="SYSDBA",password="masterkey",charset="UTF8")
        cur = conn.cursor()
        cur.execute("""CREATE TABLE PEDIDOS (
            ID INTEGER NOT NULL PRIMARY KEY, NUMERO VARCHAR(20),
            DATA_PEDIDO VARCHAR(10), HORA_PEDIDO VARCHAR(8), STATUS VARCHAR(20) DEFAULT 'aberto',
            COD_VENDEDOR VARCHAR(20), NOME_VENDEDOR VARCHAR(150),
            COD_CLIENTE INTEGER, NOME_CLIENTE VARCHAR(255), CPF_CNPJ VARCHAR(20),
            SUBTOTAL DECIMAL(12,2) DEFAULT 0, DESCONTO DECIMAL(12,2) DEFAULT 0,
            ACRESCIMO DECIMAL(12,2) DEFAULT 0, TOTAL DECIMAL(12,2) DEFAULT 0,
            FORMA_PAGAMENTO VARCHAR(50), OBSERVACOES BLOB SUB_TYPE TEXT,
            USUARIO_CRIOU VARCHAR(100), USUARIO_ALTEROU VARCHAR(100),
            DATA_CRIACAO VARCHAR(30), DATA_ATUALIZACAO VARCHAR(30), LOG_ALTERACOES BLOB SUB_TYPE TEXT
        )""")
        cur.execute("""CREATE TABLE PEDIDO_ITENS (
            ID INTEGER NOT NULL PRIMARY KEY, PEDIDO_ID INTEGER NOT NULL,
            SKU VARCHAR(50), NOME_PRODUTO VARCHAR(255), QUANTIDADE DECIMAL(12,3),
            UNIDADE VARCHAR(20), VALOR_UNITARIO DECIMAL(12,2), VALOR_TOTAL DECIMAL(12,2)
        )""")
        conn.commit(); conn.close()

init_pedidos()

def init_usuarios():
    import os, firebirdsql
    from core.database import get_db_path
    db_path = get_db_path("usuarios")
    if not os.path.exists(db_path):
        conn = firebirdsql.create_database(host="localhost",database=db_path,user="SYSDBA",password="masterkey",charset="UTF8")
        cur = conn.cursor()
        cur.execute("""CREATE TABLE USUARIOS (
            ID INTEGER NOT NULL PRIMARY KEY, LOGIN VARCHAR(50) NOT NULL,
            SENHA_HASH VARCHAR(255) NOT NULL, NOME VARCHAR(150), EMAIL VARCHAR(150),
            PERFIL VARCHAR(20) DEFAULT 'vendedor', ATIVO CHAR(1) DEFAULT 'S',
            PERMISSOES BLOB SUB_TYPE TEXT, DATA_CADASTRO VARCHAR(30), ULTIMO_ACESSO VARCHAR(30)
        )""")
        conn.commit()
        senha = hashlib.sha256("admin123".encode()).hexdigest()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO USUARIOS (ID,LOGIN,SENHA_HASH,NOME,EMAIL,PERFIL,ATIVO,DATA_CADASTRO) VALUES (1,'admin',?,'Administrador','admin@mksys.local','admin','S',?)",(senha,now))
        conn.commit(); conn.close()

init_usuarios()

# Migração: adicionar TROCAR_SENHA se não existir
def _migrar_usuarios():
    try:
        with get_connection("usuarios") as conn:
            cur = conn.cursor()
            try:
                cur.execute("ALTER TABLE USUARIOS ADD TROCAR_SENHA CHAR(1) DEFAULT 'N'")
                conn.commit()
            except Exception:
                pass  # coluna já existe
    except Exception:
        pass
_migrar_usuarios()

def init_fornecedores():
    import os, firebirdsql
    from core.database import get_db_path
    db_path = get_db_path("fornecedores")
    if not os.path.exists(db_path):
        conn = firebirdsql.create_database(host="localhost",database=db_path,user="SYSDBA",password="masterkey",charset="UTF8")
        cur = conn.cursor()
        cur.execute("""CREATE TABLE FORNECEDORES (
            ID INTEGER NOT NULL PRIMARY KEY, TIPO CHAR(2) DEFAULT 'PJ',
            RAZAO_SOCIAL VARCHAR(255), NOME_FANTASIA VARCHAR(150),
            CNPJ VARCHAR(20), CPF VARCHAR(15), IE VARCHAR(20),
            EMAIL VARCHAR(150), TELEFONE VARCHAR(20), CELULAR VARCHAR(20), CONTATO_NOME VARCHAR(150),
            CEP VARCHAR(10), RUA VARCHAR(255), NUMERO VARCHAR(20), COMPLEMENTO VARCHAR(100),
            BAIRRO VARCHAR(100), CIDADE VARCHAR(100), ESTADO VARCHAR(2),
            BANCO VARCHAR(100), AGENCIA VARCHAR(20), CONTA VARCHAR(30), PIX VARCHAR(150),
            PRAZO_PAGAMENTO INTEGER DEFAULT 30, CATEGORIA VARCHAR(100),
            STATUS VARCHAR(10) DEFAULT 'ativo', OBSERVACOES BLOB SUB_TYPE TEXT,
            DATA_CADASTRO VARCHAR(30), DATA_ATUALIZACAO VARCHAR(30)
        )""")
        conn.commit(); conn.close()

init_fornecedores()

def init_financeiro():
    import os, firebirdsql
    from core.database import get_db_path
    db_path = get_db_path("financeiro")
    if not os.path.exists(db_path):
        conn = firebirdsql.create_database(host="localhost",database=db_path,user="SYSDBA",password="masterkey",charset="UTF8")
        cur = conn.cursor()
        cur.execute("""CREATE TABLE CONTAS_RECEBER (
            ID INTEGER NOT NULL PRIMARY KEY, DESCRICAO VARCHAR(255),
            CLIENTE_ID INTEGER, NOME_CLIENTE VARCHAR(255),
            PEDIDO_ID INTEGER, NUMERO_PEDIDO VARCHAR(20),
            VALOR DECIMAL(12,2), VALOR_PAGO DECIMAL(12,2) DEFAULT 0,
            DATA_EMISSAO VARCHAR(10), DATA_VENCIMENTO VARCHAR(10), DATA_PAGAMENTO VARCHAR(10),
            STATUS VARCHAR(20) DEFAULT 'aberto', FORMA_PAGAMENTO VARCHAR(50),
            OBSERVACOES VARCHAR(500), USUARIO_LANCOU VARCHAR(100), DATA_LANCAMENTO VARCHAR(30)
        )""")
        cur.execute("""CREATE TABLE CONTAS_PAGAR (
            ID INTEGER NOT NULL PRIMARY KEY, DESCRICAO VARCHAR(255),
            FORNECEDOR_ID INTEGER, NOME_FORNECEDOR VARCHAR(255), CATEGORIA VARCHAR(100),
            VALOR DECIMAL(12,2), VALOR_PAGO DECIMAL(12,2) DEFAULT 0,
            DATA_EMISSAO VARCHAR(10), DATA_VENCIMENTO VARCHAR(10), DATA_PAGAMENTO VARCHAR(10),
            STATUS VARCHAR(20) DEFAULT 'aberto', FORMA_PAGAMENTO VARCHAR(50),
            OBSERVACOES VARCHAR(500), USUARIO_LANCOU VARCHAR(100), DATA_LANCAMENTO VARCHAR(30)
        )""")
        cur.execute("""CREATE TABLE CATEGORIAS_FIN (
            ID INTEGER NOT NULL PRIMARY KEY, NOME VARCHAR(100), TIPO CHAR(1), COR VARCHAR(10)
        )""")
        conn.commit()
        for c in [(1,"Vendas","R","#4ade80"),(2,"Servicos","R","#38bdf8"),(3,"Outros","R","#a78bfa"),
                  (4,"Fornecedores","P","#f87171"),(5,"Salarios","P","#fb923c"),(6,"Aluguel","P","#facc15"),
                  (7,"Utilidades","P","#94a3b8"),(8,"Marketing","P","#f472b6"),
                  (9,"Logistica","P","#34d399"),(10,"Impostos","P","#f97316")]:
            cur.execute("INSERT INTO CATEGORIAS_FIN (ID,NOME,TIPO,COR) VALUES (?,?,?,?)",c)
        conn.commit(); conn.close()

init_financeiro()

# Para popular produtos com dados de exemplo, rode: py seed_produtos.py

def _migrar_banco():
    migracoes = {
        "clientes_pf": [
            "ALTER TABLE CLIENTES_PF ADD COMPLEMENTO VARCHAR(100)",
            "ALTER TABLE CLIENTES_PF ADD VERIFICADO VARCHAR(20) DEFAULT 'pendente'",
        ],
        "clientes_pj": [
            "ALTER TABLE CLIENTES_PJ ADD COMPLEMENTO VARCHAR(100)",
            "ALTER TABLE CLIENTES_PJ ADD VERIFICADO VARCHAR(20) DEFAULT 'pendente'",
        ],
    }
    for cat, sqls in migracoes.items():
        for sql in sqls:
            try:
                with get_connection(cat) as conn:
                    cur = conn.cursor()
                    cur.execute(sql)
                    conn.commit()
            except Exception:
                pass  # coluna já existe — Firebird lança erro, ignoramos

_migrar_banco()

# ─────────────────────────────────────────────────────────────
# Helpers de formatação (usados nos templates via filtro Jinja2)
# ─────────────────────────────────────────────────────────────
def fmt_cpf(v):
    n = "".join(filter(str.isdigit, str(v or "")))[:11]
    if len(n) == 11: return f"{n[:3]}.{n[3:6]}.{n[6:9]}-{n[9:]}"
    return v or ""

def fmt_cnpj(v):
    n = "".join(filter(str.isdigit, str(v or "")))[:14]
    if len(n) == 14: return f"{n[:2]}.{n[2:5]}.{n[5:8]}/{n[8:12]}-{n[12:]}"
    return v or ""

def fmt_tel(v):
    n = "".join(filter(str.isdigit, str(v or "")))[:11]
    if len(n) == 11: return f"({n[:2]}) {n[2:7]}-{n[7:]}"
    if len(n) == 10: return f"({n[:2]}) {n[2:6]}-{n[6:]}"
    return v or ""

def fmt_cep(v):
    n = "".join(filter(str.isdigit, str(v or "")))[:8]
    if len(n) == 8: return f"{n[:5]}-{n[5:]}"
    return v or ""

def fmt_data(v):
    """AAAA-MM-DD → DD/MM/AAAA"""
    v = str(v or "")
    if "-" in v:
        p = v.split("-")
        if len(p) == 3: return f"{p[2]}/{p[1]}/{p[0]}"
    return v

def fmt_data_hora(v):
    """2026-01-15 09:30:00 → 15/01/2026  ·  09:30"""
    v = str(v or "")
    if " " in v:
        partes = v.split(" ", 1)
        data_part = partes[0]
        hora_part = partes[1][:5] if len(partes) > 1 else ""
        p = data_part.split("-")
        if len(p) == 3:
            data_fmt = f"{p[2]}/{p[1]}/{p[0]}"
            return f"{data_fmt}  ·  {hora_part}" if hora_part else data_fmt
    return fmt_data(v)

def iso_data(v):
    """DD/MM/AAAA → AAAA-MM-DD"""
    v = str(v or "")
    if "/" in v:
        p = v.split("/")
        if len(p) == 3: return f"{p[2]}-{p[1]}-{p[0]}"
    return v

import threading

def consultar_receita(doc_type, doc_val, cliente_id):
    """Tenta consultar a Receita Federal em background e atualiza verificado."""
    import requests as req
    digits = "".join(filter(str.isdigit, str(doc_val)))
    try:
        if doc_type == "cpf":
            # API pública CPF — sem autenticação disponível publicamente,
            # usamos validação matemática como fallback confiável
            # Para consulta real seria necessário certificado gov.br
            status = "matematico"  # válido matematicamente, sem acesso à base nacional
        else:
            # CNPJ — API pública da Receita via receitaws
            r = req.get(f"https://receitaws.com.br/v1/cnpj/{digits}", timeout=8)
            if r.status_code == 200:
                d = r.json()
                status = "ok" if d.get("situacao") == "ATIVA" else "inativo"
            else:
                status = "pendente"
    except Exception:
        status = "pendente"

    # Atualizar no banco
    cat = "clientes_pf" if doc_type == "cpf" else "clientes_pj"
    try:
        with get_connection(cat) as conn:
            cur = conn.cursor()
            tabela = cat.upper()
            cur.execute(f"UPDATE {tabela} SET verificado=? WHERE id=?", (status, cliente_id))
            conn.commit()
    except Exception:
        pass

def validar_cpf(v):
    n = "".join(filter(str.isdigit, str(v or "")))
    if len(n) != 11 or len(set(n)) == 1: return False
    s = sum(int(n[i]) * (10-i) for i in range(9))
    r = (s*10) % 11; r = 0 if r >= 10 else r
    if r != int(n[9]): return False
    s = sum(int(n[i]) * (11-i) for i in range(10))
    r = (s*10) % 11; r = 0 if r >= 10 else r
    return r == int(n[10])

def validar_cnpj(v):
    n = "".join(filter(str.isdigit, str(v or "")))
    if len(n) != 14 or len(set(n)) == 1: return False
    def calc(t):
        s, p = 0, len(t)-7
        for i in range(len(t)):
            s += int(n[i])*p; p -= 1
            if p < 2: p = 9
        r = s % 11; return 0 if r < 2 else 11-r
    return calc(n[:12]) == int(n[12]) and calc(n[:13]) == int(n[13])

def next_id(conn, tabela):
    cur = conn.cursor()
    cur.execute(f"SELECT MAX(id) AS mid FROM {tabela}")
    r = cur.fetchone()
    return (r["mid"] or 0) + 1

def checar_verificacao(doc_type, cliente_id):
    """Retorna (ok, status). Se pendente, tenta verificar na hora."""
    cat = "clientes_pf" if doc_type == "cpf" else "clientes_pj"
    tabela = cat.upper()
    doc_field = "cpf" if doc_type == "cpf" else "cnpj"
    with get_connection(cat) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT {doc_field}, verificado FROM {tabela} WHERE id=?", (cliente_id,))
        r = cur.fetchone()
        if not r:
            return False, "nao_encontrado"
        status = r.get("verificado") or "pendente"
        if status in ("ok", "matematico"):
            return True, status
        if status == "inativo":
            return False, "inativo"
        # Pendente: tenta verificar agora
        if doc_type == "cnpj":
            try:
                import requests as req
                digits = "".join(filter(str.isdigit, str(r.get("cnpj",""))))
                resp = req.get(f"https://receitaws.com.br/v1/cnpj/{digits}", timeout=5)
                if resp.status_code == 200:
                    d = resp.json()
                    novo = "ok" if d.get("situacao") == "ATIVA" else "inativo"
                    cur.execute(f"UPDATE {tabela} SET verificado=? WHERE id=?", (novo, cliente_id))
                    conn.commit()
                    return novo == "ok", novo
            except Exception:
                pass
        else:
            # CPF: sem API pública disponível, mantém como matematico se passou validação
            cur.execute(f"UPDATE {tabela} SET verificado='matematico' WHERE id=?", (cliente_id,))
            conn.commit()
            return True, "matematico"
        return False, "pendente"

app.jinja_env.filters["fmt_cpf"]  = fmt_cpf
app.jinja_env.filters["fmt_cnpj"] = fmt_cnpj
app.jinja_env.filters["fmt_tel"]  = fmt_tel
app.jinja_env.filters["fmt_cep"]  = fmt_cep
app.jinja_env.filters["fmt_data"]      = fmt_data
app.jinja_env.filters["fmt_data_hora"] = fmt_data_hora


# ═════════════════════════════════════════════════════════════
# API — mantida igual ao backend original
# ═════════════════════════════════════════════════════════════

@app.route("/api/ping")
def api_ping():
    if session.get("usuario_id"):
        session["ultimo_ativo"] = datetime.datetime.now().timestamp()
    return jsonify({"ok": True})

@app.route("/api/status")
def api_status():
    return jsonify({"status": "Servidor ativo"}), 200

# ── PF API ──
@app.route("/clientes_pf", methods=["GET"])
def api_list_pf():
    with get_connection("clientes_pf") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clientes_pf")
        rows = cur.fetchall()
        for r in rows:
            r["dependentes"] = json.loads(r["dependentes"]) if r.get("dependentes") else []
        return jsonify(rows), 200

@app.route("/clientes_pf/search", methods=["GET"])
def api_search_pf():
    q = request.args.get("q", "").strip()
    with get_connection("clientes_pf") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clientes_pf")
        rows = cur.fetchall()
        result = []
        qu = q.upper()
        for r in rows:
            r["dependentes"] = json.loads(r["dependentes"]) if r.get("dependentes") else []
            if (qu in (r.get("nome") or "").upper() or
                qu in (r.get("cpf") or "") or
                str(r.get("id","")) == q or
                any(qu in (d.get("nome","") or "").upper() or qu in (d.get("cpf","") or "")
                    for d in r["dependentes"] if isinstance(d, dict))):
                result.append(r)
        return jsonify(result), 200

@app.route("/clientes_pf", methods=["POST"])
def api_create_pf():
    data = request.get_json()
    data_cadastro = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    deps_json = json.dumps(data.get("dependentes", []))
    with get_connection("clientes_pf") as conn:
        novo_id = next_id(conn, "clientes_pf")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO clientes_pf (
                id, nome, cpf, data_nascimento,
                rua, numero, complemento, bairro, cidade, estado, cep,
                telefone, data_cadastro, observacoes, dependentes
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            novo_id, data.get("nome"), data.get("cpf"), data.get("data_nascimento"),
            data.get("rua"), data.get("numero"), data.get("complemento"),
            data.get("bairro"), data.get("cidade"), data.get("estado"), data.get("cep"),
            data.get("telefone"), data_cadastro, data.get("observacoes"), deps_json
        ))
        conn.commit()
        return jsonify({"id": novo_id}), 201

@app.route("/clientes_pf/<int:cid>", methods=["PUT"])
def api_update_pf(cid):
    data = request.get_json()
    deps_json = json.dumps(data.get("dependentes", []))
    with get_connection("clientes_pf") as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE clientes_pf SET
                nome=?, cpf=?, data_nascimento=?,
                rua=?, numero=?, complemento=?,
                bairro=?, cidade=?, estado=?, cep=?,
                telefone=?, observacoes=?, dependentes=?
            WHERE id=?
        """, (
            data.get("nome"), data.get("cpf"), data.get("data_nascimento"),
            data.get("rua"), data.get("numero"), data.get("complemento"),
            data.get("bairro"), data.get("cidade"), data.get("estado"), data.get("cep"),
            data.get("telefone"), data.get("observacoes"), deps_json, cid
        ))
        conn.commit()
        return jsonify({"id": cid}), 200

# ── PJ API ──
@app.route("/clientes_pj", methods=["GET"])
def api_list_pj():
    with get_connection("clientes_pj") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clientes_pj")
        rows = cur.fetchall()
        for r in rows:
            r["autorizados"] = json.loads(r["autorizados"]) if r.get("autorizados") else []
        return jsonify(rows), 200

@app.route("/clientes_pj/search", methods=["GET"])
def api_search_pj():
    q = request.args.get("q", "").strip()
    with get_connection("clientes_pj") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clientes_pj")
        rows = cur.fetchall()
        result = []
        qu = q.upper()
        for r in rows:
            r["autorizados"] = json.loads(r["autorizados"]) if r.get("autorizados") else []
            if (qu in (r.get("razao_social") or "").upper() or
                qu in (r.get("nome_fantasia") or "").upper() or
                qu in (r.get("cnpj") or "") or
                qu in (r.get("cpf_responsavel") or "") or
                str(r.get("id","")) == q or
                any(qu in (a.get("nome","") or "").upper() or qu in (a.get("cpf","") or "")
                    for a in r["autorizados"] if isinstance(a, dict))):
                result.append(r)
        return jsonify(result), 200

@app.route("/clientes_pj", methods=["POST"])
def api_create_pj():
    data = request.get_json()
    data_cadastro = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    auts_json = json.dumps(data.get("autorizados", []))
    with get_connection("clientes_pj") as conn:
        novo_id = next_id(conn, "clientes_pj")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO clientes_pj (
                id, cnpj, inscricao_estadual, data_abertura,
                razao_social, nome_fantasia, telefone,
                rua, numero, complemento, bairro, cidade, estado, cep,
                cpf_responsavel, nome_responsavel, telefone_responsavel,
                autorizados, data_cadastro, observacoes
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            novo_id, data.get("cnpj"), data.get("inscricao_estadual"), data.get("data_abertura"),
            data.get("razao_social"), data.get("nome_fantasia"), data.get("telefone"),
            data.get("rua"), data.get("numero"), data.get("complemento"),
            data.get("bairro"), data.get("cidade"), data.get("estado"), data.get("cep"),
            data.get("cpf_responsavel"), data.get("nome_responsavel"), data.get("telefone_responsavel"),
            auts_json, data_cadastro, data.get("observacoes")
        ))
        conn.commit()
        return jsonify({"id": novo_id}), 201

@app.route("/clientes_pj/<int:cid>", methods=["PUT"])
def api_update_pj(cid):
    data = request.get_json()
    auts_json = json.dumps(data.get("autorizados", []))
    with get_connection("clientes_pj") as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE clientes_pj SET
                cnpj=?, inscricao_estadual=?, data_abertura=?,
                razao_social=?, nome_fantasia=?, telefone=?,
                rua=?, numero=?, complemento=?,
                bairro=?, cidade=?, estado=?, cep=?,
                cpf_responsavel=?, nome_responsavel=?, telefone_responsavel=?,
                observacoes=?, autorizados=?
            WHERE id=?
        """, (
            data.get("cnpj"), data.get("inscricao_estadual"), data.get("data_abertura"),
            data.get("razao_social"), data.get("nome_fantasia"), data.get("telefone"),
            data.get("rua"), data.get("numero"), data.get("complemento"),
            data.get("bairro"), data.get("cidade"), data.get("estado"), data.get("cep"),
            data.get("cpf_responsavel"), data.get("nome_responsavel"), data.get("telefone_responsavel"),
            data.get("observacoes"), auts_json, cid
        ))
        conn.commit()
        return jsonify({"id": cid}), 200


# ═════════════════════════════════════════════════════════════
# WEB — páginas HTML via Jinja2
# ═════════════════════════════════════════════════════════════

@app.route("/")
def dashboard():
    with get_connection("clientes_pf") as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM clientes_pf")
        total_pf = cur.fetchone()["total"]
    with get_connection("clientes_pj") as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM clientes_pj")
        total_pj = cur.fetchone()["total"]
    return render_template("dashboard.html", total_pf=total_pf, total_pj=total_pj)


@app.route("/api/clientes-lista")
def api_clientes_lista():
    """Retorna todos os clientes em JSON para busca client-side."""
    if not tem_permissao('clientes','ver'):
        return jsonify([]), 403
    result = []
    with get_connection("clientes_pf") as conn:
        cur = conn.cursor()
        cur.execute("SELECT ID,NOME,CPF,TELEFONE FROM CLIENTES_PF WHERE 1=1")
        for r in cur.fetchall():
            result.append({"id":r["id"],"tipo":"pf","nome":r.get("nome",""),
                           "doc":r.get("cpf",""),"tel":r.get("telefone","")})
    with get_connection("clientes_pj") as conn:
        cur = conn.cursor()
        cur.execute("SELECT ID,RAZAO_SOCIAL,NOME_FANTASIA,CNPJ,TELEFONE FROM CLIENTES_PJ WHERE 1=1")
        for r in cur.fetchall():
            result.append({"id":r["id"],"tipo":"pj",
                           "nome":r.get("razao_social",""),"fantasia":r.get("nome_fantasia",""),
                           "doc":r.get("cnpj",""),"tel":r.get("telefone","")})
    return jsonify(result)

@app.route("/api/produtos-lista")
def api_produtos_lista():
    """Retorna todos os produtos em JSON para busca client-side."""
    if not tem_permissao('produtos','ver'):
        return jsonify([]), 403
    with get_connection("produtos") as conn:
        cur = conn.cursor()
        cur.execute("SELECT ID,SKU,NOME,CATEGORIA,MARCA,PRECO_VENDA,QTD_ESTOQUE,STATUS FROM PRODUTOS WHERE 1=1")
        return jsonify(cur.fetchall())

@app.route("/clientes")
def clientes():
    if not tem_permissao('clientes','ver'): flash('Sem permissão para acessar Clientes.','erro'); return redirect(url_for('dashboard'))
    q = request.args.get("q", "").strip()
    resultados = []

    if len(q) >= 3:
        qu = q.upper()

        with get_connection("clientes_pf") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clientes_pf")
            for r in cur.fetchall():
                deps = json.loads(r["dependentes"]) if r.get("dependentes") else []
                match_titular = qu in (r.get("nome") or "").upper() or qu in (r.get("cpf") or "")
                match_deps = [d for d in deps if isinstance(d, dict) and
                              (qu in (d.get("nome","") or "").upper() or qu in (d.get("cpf","") or ""))]

                if match_titular:
                    r["_tipo"] = "pf"; r["_sub"] = False
                    resultados.append(r)
                elif match_deps:
                    resultados.append({
                        "_tipo": "pf", "_sub": True, "id": r["id"],
                        "nome": f"{match_deps[0].get('nome','')}  ({r['nome']})",
                        "cpf": r["cpf"], "telefone": match_deps[0].get("telefone",""),
                    })

        with get_connection("clientes_pj") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clientes_pj")
            for r in cur.fetchall():
                auts = json.loads(r["autorizados"]) if r.get("autorizados") else []
                match_titular = (qu in (r.get("razao_social") or "").upper() or
                                 qu in (r.get("nome_fantasia") or "").upper() or
                                 qu in (r.get("cnpj") or "") or
                                 qu in (r.get("cpf_responsavel") or ""))
                match_auts = [a for a in auts if isinstance(a, dict) and
                              (qu in (a.get("nome","") or "").upper() or qu in (a.get("cpf","") or ""))]

                if match_titular:
                    r["_tipo"] = "pj"; r["_sub"] = False
                    resultados.append(r)
                elif match_auts:
                    resultados.append({
                        "_tipo": "pj", "_sub": True, "id": r["id"],
                        "nome": f"{match_auts[0].get('nome','')}  ({r['razao_social']})",
                        "cnpj": r["cnpj"], "telefone": match_auts[0].get("telefone",""),
                    })

    return render_template("clientes/lista.html", q=q, resultados=resultados)


# ── PF Web ──
def _get_pf(cid):
    with get_connection("clientes_pf") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clientes_pf WHERE id = ?", (int(cid),))
        r = cur.fetchone()
        if r:
            r["dependentes"] = json.loads(r["dependentes"]) if r.get("dependentes") else []
        return r

def _salvar_pf(cid):
    f = request.form
    deps = []
    for i in range(1, 4):
        nome = f.get(f"dep{i}_nome","").strip()
        cpf  = f.get(f"dep{i}_cpf","").strip()
        tel  = f.get(f"dep{i}_tel","").strip()
        ativo = f.get(f"dep{i}_ativo") == "1"
        if nome or cpf:
            deps.append({"nome": nome, "cpf": cpf, "telefone": tel, "ativo": ativo})

    nasc = iso_data(f.get("data_nascimento",""))
    cpf_val = f.get("cpf","").strip()

    # Validar CPF matematicamente
    if not validar_cpf(cpf_val):
        flash(f"CPF {fmt_cpf(cpf_val)} é inválido. Verifique os dígitos.", "erro")
        cliente = _get_pf(int(cid)) if cid else None
        return render_template("clientes/pf_form.html", cliente=cliente,
                               modo="editar" if cid else "novo")

    # Validar CPFs dos dependentes
    for i, dep in enumerate(deps, 1):
        cpf_dep = dep.get("cpf","").strip()
        if cpf_dep and not validar_cpf(cpf_dep):
            flash(f"CPF do dependente {i} ({fmt_cpf(cpf_dep)}) é inválido.", "erro")
            cliente = _get_pf(int(cid)) if cid else None
            return render_template("clientes/pf_form.html", cliente=cliente,
                                   modo="editar" if cid else "novo")

    with get_connection("clientes_pf") as conn:
        cur = conn.cursor()
        # Verificar CPF duplicado
        if cid:
            cur.execute("SELECT id FROM clientes_pf WHERE cpf = ? AND id <> ?", (cpf_val, int(cid)))
        else:
            cur.execute("SELECT id FROM clientes_pf WHERE cpf = ?", (cpf_val,))
        if cur.fetchone():
            flash(f"CPF {fmt_cpf(cpf_val)} já está cadastrado no sistema.", "erro")
            cliente = _get_pf(int(cid)) if cid else None
            return render_template("clientes/pf_form.html", cliente=cliente,
                                   modo="editar" if cid else "novo")
        if cid:
            cur.execute("""
                UPDATE clientes_pf SET
                    nome=?, cpf=?, data_nascimento=?, telefone=?,
                    cep=?, rua=?, numero=?, complemento=?,
                    bairro=?, cidade=?, estado=?, observacoes=?, dependentes=?
                WHERE id=?
            """, (
                f.get("nome"), f.get("cpf"), nasc, f.get("telefone"),
                f.get("cep"), f.get("rua"), f.get("numero"), f.get("complemento"),
                f.get("bairro"), f.get("cidade"), f.get("estado"),
                f.get("observacoes"), json.dumps(deps), int(cid)
            ))
            conn.commit()
            t = threading.Thread(target=consultar_receita, args=("cpf", f.get("cpf",""), int(cid)), daemon=True)
            t.start()
            flash("Cliente atualizado! Verificação na Receita Federal em andamento...", "ok")
            return redirect(url_for("pf_ver", cid=cid))
        else:
            novo_id = next_id(conn, "clientes_pf")
            data_cadastro = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                INSERT INTO clientes_pf (
                    id, nome, cpf, data_nascimento, telefone,
                    cep, rua, numero, complemento,
                    bairro, cidade, estado, observacoes, dependentes, data_cadastro
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                novo_id, f.get("nome"), f.get("cpf"), nasc, f.get("telefone"),
                f.get("cep"), f.get("rua"), f.get("numero"), f.get("complemento"),
                f.get("bairro"), f.get("cidade"), f.get("estado"),
                f.get("observacoes"), json.dumps(deps), data_cadastro
            ))
            conn.commit()
            flash("Cliente cadastrado com sucesso!", "ok")
            return redirect(url_for("pf_ver", cid=novo_id))

@app.route("/clientes/pf/novo", methods=["GET","POST"])
def pf_novo():
    if not tem_permissao('clientes','criar'): flash('Sem permissão para criar clientes.','erro'); return redirect(url_for('clientes'))
    if request.method == "POST": return _salvar_pf(None)
    doc = request.args.get("doc","")
    return render_template("clientes/pf_form.html", cliente=None, modo="novo", doc_pre=doc)

@app.route("/clientes/pf/<int:cid>")
def pf_ver(cid):
    c = _get_pf(cid)
    if not c: flash("Cliente não encontrado.", "erro"); return redirect(url_for("clientes"))
    return render_template("clientes/pf_form.html", cliente=c, modo="ver")

@app.route("/clientes/pf/<int:cid>/editar", methods=["GET","POST"])
def pf_editar(cid):
    if not tem_permissao('clientes','editar'): flash('Sem permissão para editar clientes.','erro'); return redirect(url_for('clientes'))
    if request.method == "POST": return _salvar_pf(cid)
    c = _get_pf(cid)
    if not c: flash("Cliente não encontrado.", "erro"); return redirect(url_for("clientes"))
    return render_template("clientes/pf_form.html", cliente=c, modo="editar")


# ── PJ Web ──
def _get_pj(cid):
    with get_connection("clientes_pj") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clientes_pj WHERE id = ?", (int(cid),))
        r = cur.fetchone()
        if r:
            r["autorizados"] = json.loads(r["autorizados"]) if r.get("autorizados") else []
        return r

def _salvar_pj(cid):
    f = request.form
    auts = []
    for i in range(1, 6):
        nome = f.get(f"aut{i}_nome","").strip()
        cpf  = f.get(f"aut{i}_cpf","").strip()
        tel  = f.get(f"aut{i}_tel","").strip()
        ativo = f.get(f"aut{i}_ativo") == "1"
        if nome or cpf:
            auts.append({"nome": nome, "cpf": cpf, "telefone": tel, "ativo": ativo})

    ab = iso_data(f.get("data_abertura",""))
    cnpj_val = f.get("cnpj","").strip()

    # Validar CNPJ matematicamente
    if not validar_cnpj(cnpj_val):
        flash(f"CNPJ {fmt_cnpj(cnpj_val)} é inválido. Verifique os dígitos.", "erro")
        cliente = _get_pj(int(cid)) if cid else None
        return render_template("clientes/pj_form.html", cliente=cliente,
                               modo="editar" if cid else "novo")

    # Validar CPFs dos autorizados
    for i, aut in enumerate(auts, 1):
        cpf_aut = aut.get("cpf","").strip()
        if cpf_aut and not validar_cpf(cpf_aut):
            flash(f"CPF do autorizado {i} ({fmt_cpf(cpf_aut)}) é inválido.", "erro")
            cliente = _get_pj(int(cid)) if cid else None
            return render_template("clientes/pj_form.html", cliente=cliente,
                                   modo="editar" if cid else "novo")

    with get_connection("clientes_pj") as conn:
        cur = conn.cursor()
        # Verificar CNPJ duplicado
        if cid:
            cur.execute("SELECT id FROM clientes_pj WHERE cnpj = ? AND id <> ?", (cnpj_val, int(cid)))
        else:
            cur.execute("SELECT id FROM clientes_pj WHERE cnpj = ?", (cnpj_val,))
        if cur.fetchone():
            flash(f"CNPJ {fmt_cnpj(cnpj_val)} já está cadastrado no sistema.", "erro")
            cliente = _get_pj(int(cid)) if cid else None
            return render_template("clientes/pj_form.html", cliente=cliente,
                                   modo="editar" if cid else "novo")
        if cid:
            cur.execute("""
                UPDATE clientes_pj SET
                    cnpj=?, inscricao_estadual=?, data_abertura=?,
                    razao_social=?, nome_fantasia=?, telefone=?,
                    cep=?, rua=?, numero=?, complemento=?,
                    bairro=?, cidade=?, estado=?,
                    nome_responsavel=?, cpf_responsavel=?, telefone_responsavel=?,
                    observacoes=?, autorizados=?
                WHERE id=?
            """, (
                f.get("cnpj"), f.get("inscricao_estadual"), ab,
                f.get("razao_social"), f.get("nome_fantasia"), f.get("telefone"),
                f.get("cep"), f.get("rua"), f.get("numero"), f.get("complemento"),
                f.get("bairro"), f.get("cidade"), f.get("estado"),
                f.get("nome_responsavel"), f.get("cpf_responsavel"), f.get("telefone_responsavel"),
                f.get("observacoes"), json.dumps(auts), int(cid)
            ))
            conn.commit()
            t = threading.Thread(target=consultar_receita, args=("cnpj", f.get("cnpj",""), int(cid)), daemon=True)
            t.start()
            flash("Cliente atualizado! Verificação na Receita Federal em andamento...", "ok")
            return redirect(url_for("pj_ver", cid=cid))
        else:
            novo_id = next_id(conn, "clientes_pj")
            data_cadastro = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                INSERT INTO clientes_pj (
                    id, cnpj, inscricao_estadual, data_abertura,
                    razao_social, nome_fantasia, telefone,
                    cep, rua, numero, complemento, bairro, cidade, estado,
                    nome_responsavel, cpf_responsavel, telefone_responsavel,
                    observacoes, autorizados, data_cadastro
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                novo_id, f.get("cnpj"), f.get("inscricao_estadual"), ab,
                f.get("razao_social"), f.get("nome_fantasia"), f.get("telefone"),
                f.get("cep"), f.get("rua"), f.get("numero"), f.get("complemento"),
                f.get("bairro"), f.get("cidade"), f.get("estado"),
                f.get("nome_responsavel"), f.get("cpf_responsavel"), f.get("telefone_responsavel"),
                f.get("observacoes"), json.dumps(auts), data_cadastro
            ))
            conn.commit()
            t = threading.Thread(target=consultar_receita, args=("cnpj", f.get("cnpj",""), novo_id), daemon=True)
            t.start()
            flash("Cliente cadastrado! Verificação na Receita Federal em andamento...", "ok")
            return redirect(url_for("pj_ver", cid=novo_id))

@app.route("/clientes/pj/novo", methods=["GET","POST"])
def pj_novo():
    if not tem_permissao('clientes','criar'): flash('Sem permissão para criar clientes.','erro'); return redirect(url_for('clientes'))
    if request.method == "POST": return _salvar_pj(None)
    doc = request.args.get("doc","")
    return render_template("clientes/pj_form.html", cliente=None, modo="novo", doc_pre=doc)

@app.route("/clientes/pj/<int:cid>")
def pj_ver(cid):
    c = _get_pj(cid)
    if not c: flash("Cliente não encontrado.", "erro"); return redirect(url_for("clientes"))
    return render_template("clientes/pj_form.html", cliente=c, modo="ver")

@app.route("/clientes/pj/<int:cid>/editar", methods=["GET","POST"])
def pj_editar(cid):
    if request.method == "POST": return _salvar_pj(cid)
    c = _get_pj(cid)
    if not c: flash("Cliente não encontrado.", "erro"); return redirect(url_for("clientes"))
    return render_template("clientes/pj_form.html", cliente=c, modo="editar")


# ─────────────────────────────────────────────────────────────
# MÓDULO PEDIDOS
# ─────────────────────────────────────────────────────────────

def _next_id(cat, table):
    with get_connection(cat) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT MAX(ID) FROM {table}")
        r = cur.fetchone(); v = list(r.values())[0] if r else None
        return (v or 0) + 1

def _get_pedido(pid):
    with get_connection("pedidos") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM PEDIDOS WHERE ID=?", (pid,))
        ped = cur.fetchone()
        if not ped: return None, []
        cur.execute("SELECT * FROM PEDIDO_ITENS WHERE PEDIDO_ID=? ORDER BY ID", (pid,))
        itens = cur.fetchall()
        return ped, itens

def _gerar_numero():
    import datetime
    with get_connection("pedidos") as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM PEDIDOS")
        r = cur.fetchone(); n = (list(r.values())[0] or 0) + 1
    d = datetime.datetime.now()
    return f"PED{d.strftime('%y%m')}{n:04d}"

def _salvar_pedido(pid):
    f = request.form
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    def dec(k):
        v = f.get(k,"").replace(",",".").strip()
        try: return float(v) if v else 0.0
        except: return 0.0

    # Montar itens
    itens = []
    i = 1
    while f.get(f"item_{i}_nome"):
        qtd = dec(f"item_{i}_qtd")
        unit = dec(f"item_{i}_unitario")
        itens.append({
            "sku":      f.get(f"item_{i}_sku","").strip(),
            "nome":     f.get(f"item_{i}_nome","").strip(),
            "qtd":      qtd,
            "unidade":  f.get(f"item_{i}_unidade","UN"),
            "unitario": unit,
            "total":    round(qtd * unit, 2),
        })
        i += 1

    subtotal  = round(sum(it["total"] for it in itens), 2)
    desconto  = dec("desconto")
    acrescimo = dec("acrescimo")
    total     = round(subtotal - desconto + acrescimo, 2)

    # Log
    log_entry = f"[{now_str}] {'Criado' if not pid else 'Alterado'} por {f.get('usuario_alterou','—')}"

    with get_connection("pedidos") as conn:
        cur = conn.cursor()
        if pid:
            ped, _ = _get_pedido(int(pid))
            log_ant = ped.get("log_alteracoes","") or ""
            novo_log = log_ant + "\n" + log_entry
            cur.execute("""UPDATE PEDIDOS SET
                STATUS=?, COD_VENDEDOR=?, NOME_VENDEDOR=?,
                COD_CLIENTE=?, NOME_CLIENTE=?, CPF_CNPJ=?,
                SUBTOTAL=?, DESCONTO=?, ACRESCIMO=?, TOTAL=?,
                FORMA_PAGAMENTO=?, OBSERVACOES=?,
                USUARIO_ALTEROU=?, DATA_ATUALIZACAO=?, LOG_ALTERACOES=?
                WHERE ID=?""", (
                f.get("status","aberto"),
                f.get("cod_vendedor"), f.get("nome_vendedor"),
                f.get("cod_cliente") or None, f.get("nome_cliente"), f.get("cpf_cnpj"),
                subtotal, desconto, acrescimo, total,
                f.get("forma_pagamento"), f.get("observacoes"),
                f.get("usuario_alterou"), now_str, novo_log,
                int(pid)
            ))
            cur.execute("DELETE FROM PEDIDO_ITENS WHERE PEDIDO_ID=?", (int(pid),))
        else:
            pid = _next_id("pedidos","PEDIDOS")
            numero = _gerar_numero()
            cur.execute("""INSERT INTO PEDIDOS (
                ID, NUMERO, DATA_PEDIDO, HORA_PEDIDO, STATUS,
                COD_VENDEDOR, NOME_VENDEDOR,
                COD_CLIENTE, NOME_CLIENTE, CPF_CNPJ,
                SUBTOTAL, DESCONTO, ACRESCIMO, TOTAL,
                FORMA_PAGAMENTO, OBSERVACOES,
                USUARIO_CRIOU, USUARIO_ALTEROU,
                DATA_CRIACAO, DATA_ATUALIZACAO, LOG_ALTERACOES
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                pid, numero,
                now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"),
                f.get("status","aberto"),
                f.get("cod_vendedor"), f.get("nome_vendedor"),
                f.get("cod_cliente") or None, f.get("nome_cliente"), f.get("cpf_cnpj"),
                subtotal, desconto, acrescimo, total,
                f.get("forma_pagamento"), f.get("observacoes"),
                f.get("usuario_criou"), f.get("usuario_alterou"),
                now_str, now_str, log_entry
            ))

        # Reinserir itens
        for idx, it in enumerate(itens, 1):
            iid = _next_id("pedidos","PEDIDO_ITENS") + idx - 1
            cur.execute("""INSERT INTO PEDIDO_ITENS
                (ID,PEDIDO_ID,SKU,NOME_PRODUTO,QUANTIDADE,UNIDADE,VALOR_UNITARIO,VALOR_TOTAL)
                VALUES (?,?,?,?,?,?,?,?)""",
                (iid, pid, it["sku"], it["nome"], it["qtd"],
                 it["unidade"], it["unitario"], it["total"]))
        conn.commit()

    flash("Pedido salvo com sucesso!", "ok")
    return redirect(url_for("pedido_ver", pid=pid))

@app.route("/pedidos")
def pedidos():
    if not tem_permissao('pedidos','ver'): flash('Sem permissão para acessar Pedidos.','erro'); return redirect(url_for('dashboard'))
    q = request.args.get("q","").strip()
    resultados = []
    perfil      = session.get("usuario_perfil","")
    nome_user   = session.get("usuario_nome","")
    so_meus     = (perfil == "vendedor")  # operadores veem só seus pedidos
    with get_connection("pedidos") as conn:
        cur = conn.cursor()
        if len(q) >= 3:
            like = f"%{q.upper()}%"
            if so_meus:
                cur.execute("""SELECT * FROM PEDIDOS
                    WHERE UPPER(NOME_VENDEDOR)=?
                    AND (UPPER(NUMERO) LIKE ? OR UPPER(NOME_CLIENTE) LIKE ?
                         OR UPPER(CPF_CNPJ) LIKE ?)
                    ORDER BY ID DESC""", (nome_user.upper(), like, like, like))
            else:
                cur.execute("""SELECT * FROM PEDIDOS
                    WHERE UPPER(NUMERO) LIKE ? OR UPPER(NOME_CLIENTE) LIKE ?
                       OR UPPER(CPF_CNPJ) LIKE ? OR UPPER(NOME_VENDEDOR) LIKE ?
                    ORDER BY ID DESC""", (like,like,like,like))
        else:
            # Sem busca: mostra os últimos 50 (filtrado por vendedor se operador)
            if so_meus:
                cur.execute("SELECT * FROM PEDIDOS WHERE UPPER(NOME_VENDEDOR)=? ORDER BY ID DESC ROWS 50", (nome_user.upper(),))
            else:
                cur.execute("SELECT * FROM PEDIDOS ORDER BY ID DESC ROWS 50")
        resultados = cur.fetchall()
    return render_template("pedidos/lista.html", resultados=resultados, q=q, so_meus=so_meus)

@app.route("/pedidos/novo", methods=["GET","POST"])
def pedido_novo():
    if not tem_permissao('pedidos','criar'): flash('Sem permissão para criar pedidos.','erro'); return redirect(url_for('pedidos'))
    if request.method == "POST": return _salvar_pedido(None)
    return render_template("pedidos/form.html", pedido=None, itens=[], modo="novo")

@app.route("/pedidos/<int:pid>")
def pedido_ver(pid):
    ped, itens = _get_pedido(pid)
    if not ped: return redirect(url_for("pedidos"))
    return render_template("pedidos/form.html", pedido=ped, itens=itens, modo="ver")

@app.route("/pedidos/<int:pid>/editar", methods=["GET","POST"])
def pedido_editar(pid):
    if not tem_permissao('pedidos','editar'): flash('Sem permissão para editar pedidos.','erro'); return redirect(url_for('pedidos'))
    if request.method == "POST": return _salvar_pedido(pid)
    ped, itens = _get_pedido(pid)
    if not ped: return redirect(url_for("pedidos"))
    return render_template("pedidos/form.html", pedido=ped, itens=itens, modo="editar")

# API clientes para autocomplete
@app.route("/api/busca-cliente")
def api_busca_cliente():
    q = request.args.get("q","").strip()
    if len(q) < 2: return jsonify([])
    like = f"%{q.upper()}%"
    res = []
    with get_connection("clientes_pf") as conn:
        cur = conn.cursor()
        cur.execute("SELECT ID,NOME,CPF FROM CLIENTES_PF WHERE UPPER(NOME) LIKE ? OR CPF LIKE ? ORDER BY NOME ROWS 8", (like,like))
        for r in cur.fetchall():
            res.append({"id":r["id"],"nome":r["nome"],"doc":r["cpf"],"tipo":"PF"})
    with get_connection("clientes_pj") as conn:
        cur = conn.cursor()
        cur.execute("SELECT ID,RAZAO_SOCIAL,CNPJ FROM CLIENTES_PJ WHERE UPPER(RAZAO_SOCIAL) LIKE ? OR CNPJ LIKE ? ORDER BY RAZAO_SOCIAL ROWS 8", (like,like))
        for r in cur.fetchall():
            res.append({"id":r["id"],"nome":r["razao_social"],"doc":r["cnpj"],"tipo":"PJ"})
    return jsonify(res[:10])

# API produtos para autocomplete
@app.route("/api/busca-produto")
def api_busca_produto():
    q = request.args.get("q","").strip()
    if len(q) < 2: return jsonify([])
    like = f"%{q.upper()}%"
    with get_connection("produtos") as conn:
        cur = conn.cursor()
        cur.execute("""SELECT SKU,NOME,PRECO_VENDA,UNIDADE_MEDIDA FROM PRODUTOS
            WHERE UPPER(NOME) LIKE ? OR UPPER(SKU) LIKE ?
            ORDER BY NOME ROWS 8""", (like,like))
        return jsonify([{"sku":r["sku"],"nome":r["nome"],
                         "preco":float(r["preco_venda"] or 0),
                         "unidade":r["unidade_medida"] or "UN"} for r in cur.fetchall()])

# ─────────────────────────────────────────────────────────────
# MÓDULO PRODUTOS
# ─────────────────────────────────────────────────────────────

def _get_produto(pid):
    with get_connection("produtos") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM PRODUTOS WHERE ID=?", (pid,))
        return cur.fetchone()

def _next_prod_id():
    with get_connection("produtos") as conn:
        cur = conn.cursor()
        cur.execute("SELECT MAX(ID) FROM PRODUTOS")
        r = cur.fetchone()
        val = list(r.values())[0] if r else None
        return (val or 0) + 1

def _salvar_produto(pid):
    f = request.form
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def dec(k): 
        v = f.get(k, "").replace(",", ".").strip()
        try: return float(v) if v else None
        except: return None

    def intv(k):
        v = f.get(k, "").strip()
        try: return int(v) if v else None
        except: return None

    nome = f.get("nome", "").strip()
    if not nome:
        flash("Nome do produto é obrigatório.", "erro")
        prod = _get_produto(int(pid)) if pid else None
        return render_template("produtos/form.html", produto=prod, modo="editar" if pid else "novo")

    preco_custo = dec("preco_custo")
    preco_venda = dec("preco_venda")
    margem = None
    if preco_custo and preco_venda and preco_custo > 0:
        margem = round(((preco_venda - preco_custo) / preco_custo) * 100, 2)

    with get_connection("produtos") as conn:
        cur = conn.cursor()
        if pid:
            cur.execute("""
                UPDATE PRODUTOS SET
                    SKU=?, CODIGO_BARRAS=?, NOME=?, DESCRICAO=?,
                    CATEGORIA=?, SUBCATEGORIA=?, MARCA=?,
                    PRECO_CUSTO=?, PRECO_VENDA=?, MARGEM=?,
                    UNIDADE_MEDIDA=?, QTD_EMBALAGEM=?,
                    FORNECEDOR_PRINCIPAL=?, CODIGO_FORNECEDOR=?,
                    QTD_ESTOQUE=?, ESTOQUE_MINIMO=?, ESTOQUE_MAXIMO=?,
                    PESO_BRUTO=?, PESO_LIQUIDO=?,
                    ALTURA=?, LARGURA=?, COMPRIMENTO=?, VOLUME=?,
                    STATUS=?, DATA_ATUALIZACAO=?, USUARIO_RESPONSAVEL=?,
                    PRODUTO_CONTROLADO=?, PERMITE_DESCONTO=?
                WHERE ID=?""", (
                f.get("sku"), f.get("codigo_barras"), nome, f.get("descricao"),
                f.get("categoria"), f.get("subcategoria"), f.get("marca"),
                preco_custo, preco_venda, margem,
                f.get("unidade_medida"), intv("qtd_embalagem"),
                f.get("fornecedor_principal"), f.get("codigo_fornecedor"),
                dec("qtd_estoque"), dec("estoque_minimo"), dec("estoque_maximo"),
                dec("peso_bruto"), dec("peso_liquido"),
                dec("altura"), dec("largura"), dec("comprimento"), dec("volume"),
                f.get("status", "ativo"), now, f.get("usuario_responsavel"),
                "S" if f.get("produto_controlado") else "N",
                "S" if f.get("permite_desconto") else "N",
                int(pid)
            ))
        else:
            novo_id = _next_prod_id()
            cur.execute("""
                INSERT INTO PRODUTOS (
                    ID, SKU, CODIGO_BARRAS, NOME, DESCRICAO,
                    CATEGORIA, SUBCATEGORIA, MARCA,
                    PRECO_CUSTO, PRECO_VENDA, MARGEM,
                    UNIDADE_MEDIDA, QTD_EMBALAGEM,
                    FORNECEDOR_PRINCIPAL, CODIGO_FORNECEDOR,
                    QTD_ESTOQUE, ESTOQUE_MINIMO, ESTOQUE_MAXIMO,
                    PESO_BRUTO, PESO_LIQUIDO,
                    ALTURA, LARGURA, COMPRIMENTO, VOLUME,
                    STATUS, DATA_CADASTRO, DATA_ATUALIZACAO,
                    USUARIO_RESPONSAVEL, PRODUTO_CONTROLADO, PERMITE_DESCONTO
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                novo_id,
                f.get("sku"), f.get("codigo_barras"), nome, f.get("descricao"),
                f.get("categoria"), f.get("subcategoria"), f.get("marca"),
                preco_custo, preco_venda, margem,
                f.get("unidade_medida"), intv("qtd_embalagem"),
                f.get("fornecedor_principal"), f.get("codigo_fornecedor"),
                dec("qtd_estoque"), dec("estoque_minimo"), dec("estoque_maximo"),
                dec("peso_bruto"), dec("peso_liquido"),
                dec("altura"), dec("largura"), dec("comprimento"), dec("volume"),
                f.get("status", "ativo"), now, now,
                f.get("usuario_responsavel"),
                "S" if f.get("produto_controlado") else "N",
                "S" if f.get("permite_desconto") else "N"
            ))
            pid = novo_id
        conn.commit()
    flash("Produto salvo com sucesso!", "ok")
    return redirect(url_for("produto_ver", pid=pid))

@app.route("/produtos")
def produtos():
    if not tem_permissao('produtos','ver'): flash('Sem permissão para acessar Produtos.','erro'); return redirect(url_for('dashboard'))
    q = request.args.get("q", "").strip()
    resultados = []
    if len(q) >= 3:
        like = f"%{q.upper()}%"
        with get_connection("produtos") as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM PRODUTOS
                WHERE UPPER(NOME) LIKE ? OR UPPER(SKU) LIKE ?
                   OR UPPER(CODIGO_BARRAS) LIKE ? OR UPPER(CATEGORIA) LIKE ?
                   OR UPPER(MARCA) LIKE ?
                ORDER BY NOME""", (like, like, like, like, like))
            resultados = cur.fetchall()
    return render_template("produtos/lista.html", resultados=resultados, q=q)

@app.route("/produtos/novo", methods=["GET","POST"])
def produto_novo():
    if not tem_permissao('produtos','criar'): flash('Sem permissão para criar produtos.','erro'); return redirect(url_for('produtos'))
    if request.method == "POST": return _salvar_produto(None)
    return render_template("produtos/form.html", produto=None, modo="novo")

@app.route("/produtos/<int:pid>")
def produto_ver(pid):
    p = _get_produto(pid)
    if not p: return redirect(url_for("produtos"))
    return render_template("produtos/form.html", produto=p, modo="ver")

@app.route("/produtos/<int:pid>/editar", methods=["GET","POST"])
def produto_editar(pid):
    if not tem_permissao('produtos','editar'): flash('Sem permissão para editar produtos.','erro'); return redirect(url_for('produtos'))
    if request.method == "POST": return _salvar_produto(pid)
    p = _get_produto(pid)
    if not p: return redirect(url_for("produtos"))
    return render_template("produtos/form.html", produto=p, modo="editar")

# API produtos
@app.route("/api/produtos")
def api_produtos():
    with get_connection("produtos") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM PRODUTOS ORDER BY NOME")
        return jsonify(cur.fetchall())

# ═══════════════════════════════════════════════════════════
# AUTENTICAÇÃO
# ═══════════════════════════════════════════════════════════

def tem_permissao(modulo, acao):
    """Verifica se o usuário logado tem permissão para ação no módulo."""
    perfil = session.get("usuario_perfil","")
    if perfil == "admin":
        return True
    # Gerente tem tudo + relatório completo (exceto gestão de usuários)
    if perfil == "administrativo":
        if modulo == "usuarios": return False
        if modulo == "relatorios": return True  # gerente tem completo
        return True
    # Operador — verifica permissões granulares
    perms_json = session.get("usuario_permissoes","")
    if perms_json:
        try:
            perms = json.loads(perms_json)
            return acao in perms.get(modulo, [])
        except:
            return False
    return False

def usuario_logado():
    uid = session.get("usuario_id")
    if not uid: return None
    with get_connection("usuarios") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM USUARIOS WHERE ID=? AND ATIVO='S'", (uid,))
        return cur.fetchone()

def requer_login(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not usuario_logado():
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/login", methods=["GET","POST"])
def login():
    erro = None
    if request.method == "POST":
        login_ = request.form.get("login","").strip()
        senha  = request.form.get("senha","").strip()
        h = hashlib.sha256(senha.encode()).hexdigest()
        with get_connection("usuarios") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM USUARIOS WHERE LOGIN=? AND SENHA_HASH=? AND ATIVO='S'",(login_,h))
            u = cur.fetchone()
        if u:
            session["usuario_id"]       = u["id"]
            session["usuario_nome"]     = u["nome"]
            session["usuario_perfil"]   = u["perfil"]
            session["usuario_permissoes"] = u.get("permissoes","") or ""
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with get_connection("usuarios") as conn:
                cur = conn.cursor()
                cur.execute("UPDATE USUARIOS SET ULTIMO_ACESSO=? WHERE ID=?",(now,u["id"]))
                conn.commit()
            return redirect(url_for("dashboard"))
        erro = "Login ou senha incorretos."
    return render_template("login.html", erro=erro)

@app.route("/meu-perfil", methods=["GET","POST"])
def meu_perfil():
    uid = session.get("usuario_id")
    if not uid: return redirect(url_for("login"))
    u = _get_usuario(uid)
    if not u: return redirect(url_for("login"))
    erro = None
    if request.method == "POST":
        atual  = request.form.get("senha_atual","").strip()
        nova   = request.form.get("nova_senha","").strip()
        conf   = request.form.get("conf_senha","").strip()
        h_atual = hashlib.sha256(atual.encode()).hexdigest()
        if u["senha_hash"] != h_atual:
            erro = "Senha atual incorreta."
        elif len(nova) < 6:
            erro = "Nova senha deve ter ao menos 6 caracteres."
        elif nova != conf:
            erro = "As senhas não coincidem."
        else:
            h_nova = hashlib.sha256(nova.encode()).hexdigest()
            with get_connection("usuarios") as conn:
                cur = conn.cursor()
                cur.execute("UPDATE USUARIOS SET SENHA_HASH=?, TROCAR_SENHA='N' WHERE ID=?", (h_nova, uid))
                conn.commit()
            flash("Senha alterada com sucesso!", "ok")
            return redirect(url_for("meu_perfil"))
    return render_template("usuarios/meu_perfil.html", usuario=u, erro=erro)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ═══════════════════════════════════════════════════════════
# USUÁRIOS (gestão)
# ═══════════════════════════════════════════════════════════

def _get_usuario(uid):
    with get_connection("usuarios") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM USUARIOS WHERE ID=?", (uid,))
        return cur.fetchone()

def _next_usuario_id():
    with get_connection("usuarios") as conn:
        cur = conn.cursor()
        cur.execute("SELECT MAX(ID) FROM USUARIOS")
        r = cur.fetchone(); v = list(r.values())[0] if r else None
        return (v or 0) + 1

@app.route("/usuarios")
def usuarios():
    if not tem_permissao('usuarios','ver'): flash('Sem permissão para acessar Usuários.','erro'); return redirect(url_for('dashboard'))
    with get_connection("usuarios") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM USUARIOS ORDER BY NOME")
        lista = cur.fetchall()
    return render_template("usuarios/lista.html", lista=lista)

@app.route("/usuarios/novo", methods=["GET","POST"])
def usuario_novo():
    if request.method == "POST":
        f = request.form
        senha = f.get("senha","").strip()
        if not senha:
            flash("Senha é obrigatória.", "erro")
            return render_template("usuarios/form.html", usuario=None, modo="novo")
        h = hashlib.sha256(senha.encode()).hexdigest()
        uid = _next_usuario_id()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        perms = json.dumps({
            "clientes": f.getlist("perm_clientes"),
            "produtos":  f.getlist("perm_produtos"),
            "pedidos":   f.getlist("perm_pedidos"),
            "financeiro":  f.getlist("perm_financeiro"),
            "fornecedores":f.getlist("perm_fornecedores"),
            "relatorios":  f.getlist("perm_relatorios"),
            "usuarios":    f.getlist("perm_usuarios"),
        })
        with get_connection("usuarios") as conn:
            cur = conn.cursor()
            cur.execute("""INSERT INTO USUARIOS (ID,LOGIN,SENHA_HASH,NOME,EMAIL,PERFIL,ATIVO,PERMISSOES,DATA_CADASTRO)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (uid, f.get("login"), h, f.get("nome"), f.get("email"),
                 f.get("perfil","vendedor"), "S" if f.get("ativo") else "N", perms, now))
            conn.commit()
        flash("Usuário criado com sucesso!", "ok")
        return redirect(url_for("usuarios"))
    return render_template("usuarios/form.html", usuario=None, modo="novo")

@app.route("/usuarios/<int:uid>")
def usuario_ver(uid):
    u = _get_usuario(uid)
    if not u: return redirect(url_for("usuarios"))
    return render_template("usuarios/form.html", usuario=u, modo="ver")

@app.route("/usuarios/<int:uid>/resetar-senha", methods=["POST"])
def usuario_resetar_senha(uid):
    if not tem_permissao('usuarios','editar'):
        flash('Sem permissão.','erro'); return redirect(url_for('usuarios'))
    u = _get_usuario(uid)
    if not u: return redirect(url_for('usuarios'))
    nova = request.form.get("nova_senha","").strip()
    if len(nova) < 6:
        flash('Senha deve ter ao menos 6 caracteres.','erro')
        return redirect(url_for('usuario_ver', uid=uid))
    h = hashlib.sha256(nova.encode()).hexdigest()
    with get_connection("usuarios") as conn:
        cur = conn.cursor()
        cur.execute("UPDATE USUARIOS SET SENHA_HASH=?, TROCAR_SENHA='S' WHERE ID=?",(h, uid))
        conn.commit()
    flash(f'Senha de {u["nome"]} redefinida. Usuário deverá trocar no próximo acesso.','ok')
    return redirect(url_for('usuario_ver', uid=uid))

@app.route("/usuarios/<int:uid>/editar", methods=["GET","POST"])
def usuario_editar(uid):
    if request.method == "POST":
        f = request.form
        with get_connection("usuarios") as conn:
            cur = conn.cursor()
            updates = {"NOME": f.get("nome"), "EMAIL": f.get("email"),
                       "PERFIL": f.get("perfil","vendedor"),
                       "ATIVO": "S" if f.get("ativo") else "N"}
            nova_senha = f.get("senha","").strip()
            if nova_senha:
                updates["SENHA_HASH"] = hashlib.sha256(nova_senha.encode()).hexdigest()
            updates["PERMISSOES"] = json.dumps({
                "clientes":    f.getlist("perm_clientes"),
                "produtos":    f.getlist("perm_produtos"),
                "pedidos":     f.getlist("perm_pedidos"),
                "financeiro":  f.getlist("perm_financeiro"),
                "fornecedores":f.getlist("perm_fornecedores"),
                "relatorios":  f.getlist("perm_relatorios"),
                "usuarios":    f.getlist("perm_usuarios"),
            })
            sets = ", ".join(f"{k}=?" for k in updates)
            cur.execute(f"UPDATE USUARIOS SET {sets} WHERE ID=?",
                        list(updates.values()) + [uid])
            conn.commit()
        flash("Usuário atualizado.", "ok")
        return redirect(url_for("usuario_ver", uid=uid))
    u = _get_usuario(uid)
    if not u: return redirect(url_for("usuarios"))
    return render_template("usuarios/form.html", usuario=u, modo="editar")

# ═══════════════════════════════════════════════════════════
# FORNECEDORES
# ═══════════════════════════════════════════════════════════

def _get_fornecedor(fid):
    with get_connection("fornecedores") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM FORNECEDORES WHERE ID=?", (fid,))
        return cur.fetchone()

def _next_forn_id():
    with get_connection("fornecedores") as conn:
        cur = conn.cursor()
        cur.execute("SELECT MAX(ID) FROM FORNECEDORES")
        r = cur.fetchone(); v = list(r.values())[0] if r else None
        return (v or 0) + 1

def _salvar_fornecedor(fid):
    f = request.form
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    campos = dict(
        TIPO=f.get("tipo","PJ"), RAZAO_SOCIAL=f.get("razao_social"),
        NOME_FANTASIA=f.get("nome_fantasia"), CNPJ=f.get("cnpj","").replace(".","").replace("/","").replace("-",""),
        CPF=f.get("cpf","").replace(".","").replace("-",""), IE=f.get("ie"),
        EMAIL=f.get("email"), TELEFONE=f.get("telefone","").replace("(","").replace(")","").replace(" ","").replace("-",""),
        CELULAR=f.get("celular","").replace("(","").replace(")","").replace(" ","").replace("-",""),
        CONTATO_NOME=f.get("contato_nome"),
        CEP=f.get("cep","").replace("-",""), RUA=f.get("rua"), NUMERO=f.get("numero"),
        COMPLEMENTO=f.get("complemento"), BAIRRO=f.get("bairro"),
        CIDADE=f.get("cidade"), ESTADO=f.get("estado"),
        BANCO=f.get("banco"), AGENCIA=f.get("agencia"), CONTA=f.get("conta"), PIX=f.get("pix"),
        PRAZO_PAGAMENTO=int(f.get("prazo_pagamento") or 30),
        CATEGORIA=f.get("categoria"), STATUS=f.get("status","ativo"),
        OBSERVACOES=f.get("observacoes"), DATA_ATUALIZACAO=now
    )
    with get_connection("fornecedores") as conn:
        cur = conn.cursor()
        if fid:
            sets = ", ".join(f"{k}=?" for k in campos)
            cur.execute(f"UPDATE FORNECEDORES SET {sets} WHERE ID=?",
                        list(campos.values()) + [int(fid)])
        else:
            campos["DATA_CADASTRO"] = now
            campos["ID"] = _next_forn_id()
            ks = ", ".join(campos.keys()); vs = ", ".join("?" * len(campos))
            cur.execute(f"INSERT INTO FORNECEDORES ({ks}) VALUES ({vs})", list(campos.values()))
            fid = campos["ID"]
        conn.commit()
    flash("Fornecedor salvo!", "ok")
    return redirect(url_for("fornecedor_ver", fid=fid))

@app.route("/fornecedores")
def fornecedores():
    if not tem_permissao('fornecedores','ver'): flash('Sem permissão para acessar Fornecedores.','erro'); return redirect(url_for('dashboard'))
    q = request.args.get("q","").strip()
    resultados = []
    if len(q) >= 3:
        like = f"%{q.upper()}%"
        with get_connection("fornecedores") as conn:
            cur = conn.cursor()
            cur.execute("""SELECT * FROM FORNECEDORES
                WHERE UPPER(RAZAO_SOCIAL) LIKE ? OR UPPER(NOME_FANTASIA) LIKE ?
                   OR CNPJ LIKE ? OR CPF LIKE ? OR UPPER(CIDADE) LIKE ?
                ORDER BY RAZAO_SOCIAL""", (like,like,like,like,like))
            resultados = cur.fetchall()
    return render_template("fornecedores/lista.html", resultados=resultados, q=q)

@app.route("/fornecedores/novo", methods=["GET","POST"])
def fornecedor_novo():
    if not tem_permissao('fornecedores','criar'): flash('Sem permissão.','erro'); return redirect(url_for('fornecedores'))
    if request.method == "POST": return _salvar_fornecedor(None)
    return render_template("fornecedores/form.html", fornecedor=None, modo="novo")

@app.route("/fornecedores/<int:fid>")
def fornecedor_ver(fid):
    f = _get_fornecedor(fid)
    if not f: return redirect(url_for("fornecedores"))
    return render_template("fornecedores/form.html", fornecedor=f, modo="ver")

@app.route("/fornecedores/<int:fid>/editar", methods=["GET","POST"])
def fornecedor_editar(fid):
    if not tem_permissao('fornecedores','editar'): flash('Sem permissão.','erro'); return redirect(url_for('fornecedores'))
    if request.method == "POST": return _salvar_fornecedor(fid)
    f = _get_fornecedor(fid)
    if not f: return redirect(url_for("fornecedores"))
    return render_template("fornecedores/form.html", fornecedor=f, modo="editar")

@app.route("/api/busca-fornecedor")
def api_busca_fornecedor():
    q = request.args.get("q","").strip()
    if len(q) < 2: return jsonify([])
    like = f"%{q.upper()}%"
    with get_connection("fornecedores") as conn:
        cur = conn.cursor()
        cur.execute("""SELECT ID,RAZAO_SOCIAL,CNPJ FROM FORNECEDORES
            WHERE UPPER(RAZAO_SOCIAL) LIKE ? OR CNPJ LIKE ?
            ORDER BY RAZAO_SOCIAL ROWS 8""", (like,like))
        return jsonify([{"id":r["id"],"nome":r["razao_social"],"doc":r["cnpj"]} for r in cur.fetchall()])

# ═══════════════════════════════════════════════════════════
# FINANCEIRO
# ═══════════════════════════════════════════════════════════

def _next_fin_id(tabela):
    with get_connection("financeiro") as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT MAX(ID) FROM {tabela}")
        r = cur.fetchone(); v = list(r.values())[0] if r else None
        return (v or 0) + 1

def _fin_lista(tabela, q=""):
    with get_connection("financeiro") as conn:
        cur = conn.cursor()
        if q and len(q) >= 3:
            like = f"%{q.upper()}%"
            cur.execute(f"""SELECT * FROM {tabela}
                WHERE UPPER(DESCRICAO) LIKE ? OR UPPER(NOME_{"CLIENTE" if "RECEBER" in tabela else "FORNECEDOR"}) LIKE ?
                   OR STATUS LIKE ?
                ORDER BY DATA_VENCIMENTO""", (like,like,like))
        else:
            cur.execute(f"SELECT * FROM {tabela} ORDER BY DATA_VENCIMENTO ROWS 200")
        return cur.fetchall()

@app.route("/financeiro")
def financeiro():
    if not tem_permissao('financeiro','ver'): flash('Sem permissão para acessar o Financeiro.','erro'); return redirect(url_for('dashboard'))
    aba = request.args.get("aba","receber")
    q   = request.args.get("q","").strip()
    tab = "CONTAS_RECEBER" if aba == "receber" else "CONTAS_PAGAR"
    registros = _fin_lista(tab, q)
    # Totais
    totais = {"aberto":0,"recebido":0,"vencido":0}
    hoje = datetime.date.today().isoformat()
    for r in registros:
        v = float(r.get("valor") or 0)
        vp = float(r.get("valor_pago") or 0)
        if r.get("status") in ("pago","recebido"): totais["recebido"] += vp
        elif r.get("data_vencimento","") < hoje:    totais["vencido"]  += (v - vp)
        else:                                        totais["aberto"]   += (v - vp)
    with get_connection("financeiro") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM CATEGORIAS_FIN ORDER BY NOME")
        categorias = cur.fetchall()
    return render_template("financeiro/lista.html",
        registros=registros, aba=aba, q=q, totais=totais, categorias=categorias, hoje=hoje)

def _salvar_lancamento(tipo, lid=None):
    f  = request.form
    tab = "CONTAS_RECEBER" if tipo == "receber" else "CONTAS_PAGAR"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    def dec(k):
        v = f.get(k,"").replace(",",".").strip()
        try: return float(v) if v else 0.0
        except: return 0.0
    campos = dict(
        DESCRICAO=f.get("descricao"), VALOR=dec("valor"),
        VALOR_PAGO=dec("valor_pago"),
        DATA_EMISSAO=f.get("data_emissao"),
        DATA_VENCIMENTO=f.get("data_vencimento"),
        DATA_PAGAMENTO=f.get("data_pagamento") or None,
        STATUS=f.get("status","aberto"),
        FORMA_PAGAMENTO=f.get("forma_pagamento"),
        OBSERVACOES=f.get("observacoes"),
        USUARIO_LANCOU=f.get("usuario_lancou"),
        DATA_LANCAMENTO=now,
    )
    if tipo == "receber":
        campos["CLIENTE_ID"]    = f.get("cliente_id") or None
        campos["NOME_CLIENTE"]  = f.get("nome_cliente")
        campos["PEDIDO_ID"]     = f.get("pedido_id") or None
        campos["NUMERO_PEDIDO"] = f.get("numero_pedido")
    else:
        campos["FORNECEDOR_ID"]   = f.get("fornecedor_id") or None
        campos["NOME_FORNECEDOR"] = f.get("nome_fornecedor")
        campos["CATEGORIA"]       = f.get("categoria")
    with get_connection("financeiro") as conn:
        cur = conn.cursor()
        if lid:
            sets = ", ".join(f"{k}=?" for k in campos)
            cur.execute(f"UPDATE {tab} SET {sets} WHERE ID=?", list(campos.values()) + [int(lid)])
        else:
            campos["ID"] = _next_fin_id(tab)
            ks = ", ".join(campos.keys()); vs = ", ".join("?" * len(campos))
            cur.execute(f"INSERT INTO {tab} ({ks}) VALUES ({vs})", list(campos.values()))
            lid = campos["ID"]
        conn.commit()
    flash("Lançamento salvo!", "ok")
    return redirect(url_for("financeiro", aba=tipo))

@app.route("/financeiro/receber/novo", methods=["GET","POST"])
def receber_novo():
    if not tem_permissao('financeiro','criar'): flash('Sem permissão.','erro'); return redirect(url_for('financeiro',aba='receber'))
    if request.method == "POST": return _salvar_lancamento("receber")
    return render_template("financeiro/form.html", reg=None, tipo="receber", modo="novo")

@app.route("/financeiro/receber/<int:lid>", methods=["GET","POST"])
def receber_ver(lid):
    if request.method == "POST": return _salvar_lancamento("receber", lid)
    with get_connection("financeiro") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM CONTAS_RECEBER WHERE ID=?", (lid,))
        r = cur.fetchone()
    return render_template("financeiro/form.html", reg=r, tipo="receber", modo="ver")

@app.route("/financeiro/receber/<int:lid>/editar", methods=["GET","POST"])
def receber_editar(lid):
    if request.method == "POST": return _salvar_lancamento("receber", lid)
    with get_connection("financeiro") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM CONTAS_RECEBER WHERE ID=?", (lid,))
        r = cur.fetchone()
    return render_template("financeiro/form.html", reg=r, tipo="receber", modo="editar")

@app.route("/financeiro/pagar/novo", methods=["GET","POST"])
def pagar_novo():
    if not tem_permissao('financeiro','criar'): flash('Sem permissão.','erro'); return redirect(url_for('financeiro',aba='pagar'))
    if request.method == "POST": return _salvar_lancamento("pagar")
    with get_connection("financeiro") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM CATEGORIAS_FIN WHERE TIPO='P' ORDER BY NOME")
        cats = cur.fetchall()
    return render_template("financeiro/form.html", reg=None, tipo="pagar", modo="novo", categorias=cats)

@app.route("/financeiro/pagar/<int:lid>", methods=["GET","POST"])
def pagar_ver(lid):
    if request.method == "POST": return _salvar_lancamento("pagar", lid)
    with get_connection("financeiro") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM CONTAS_PAGAR WHERE ID=?", (lid,))
        r = cur.fetchone()
        cur.execute("SELECT * FROM CATEGORIAS_FIN WHERE TIPO='P' ORDER BY NOME")
        cats = cur.fetchall()
    return render_template("financeiro/form.html", reg=r, tipo="pagar", modo="ver", categorias=cats)

@app.route("/financeiro/pagar/<int:lid>/editar", methods=["GET","POST"])
def pagar_editar(lid):
    if request.method == "POST": return _salvar_lancamento("pagar", lid)
    with get_connection("financeiro") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM CONTAS_PAGAR WHERE ID=?", (lid,))
        r = cur.fetchone()
        cur.execute("SELECT * FROM CATEGORIAS_FIN WHERE TIPO='P' ORDER BY NOME")
        cats = cur.fetchall()
    return render_template("financeiro/form.html", reg=r, tipo="pagar", modo="editar", categorias=cats)

# ═══════════════════════════════════════════════════════════
# RELATÓRIOS
# ═══════════════════════════════════════════════════════════

@app.route("/relatorios")
def relatorios():
    if not tem_permissao('relatorios','ver'):
        flash('Sem permissão para acessar Relatórios.','erro')
        return redirect(url_for('dashboard'))
    return render_template("relatorios/index.html")

@app.route("/relatorios/pedidos")
def relatorio_pedidos():
    if not tem_permissao('relatorios','ver'):
        flash('Sem permissão.','erro'); return redirect(url_for('dashboard'))
    perfil    = session.get("usuario_perfil","")
    nome_user = session.get("usuario_nome","")
    relatorio_completo = tem_permissao('relatorios','completo')
    data_ini = request.args.get("data_ini","")
    data_fim = request.args.get("data_fim","")
    status   = request.args.get("status","")
    vendedor = request.args.get("vendedor","")

    with get_connection("pedidos") as conn:
        cur = conn.cursor()
        where = ["1=1"]
        params = []
        # Restrito: só seus próprios pedidos
        if not relatorio_completo:
            where.append("UPPER(NOME_VENDEDOR)=?")
            params.append(nome_user.upper())
        else:
            if vendedor:
                where.append("UPPER(NOME_VENDEDOR) LIKE ?")
                params.append(f"%{vendedor.upper()}%")
        if data_ini: where.append("DATA_PEDIDO >= ?"); params.append(data_ini)
        if data_fim: where.append("DATA_PEDIDO <= ?"); params.append(data_fim)
        if status:   where.append("STATUS=?"); params.append(status)
        sql = f"SELECT * FROM PEDIDOS WHERE {' AND '.join(where)} ORDER BY DATA_PEDIDO DESC, ID DESC"
        cur.execute(sql, params)
        pedidos_lista = cur.fetchall()

    totais = {
        "qtd":     len(pedidos_lista),
        "subtotal":sum(float(p.get("subtotal") or 0) for p in pedidos_lista),
        "desconto":sum(float(p.get("desconto") or 0) for p in pedidos_lista),
        "total":   sum(float(p.get("total") or 0) for p in pedidos_lista),
    }
    return render_template("relatorios/pedidos.html",
        pedidos=pedidos_lista, totais=totais,
        filtros={"data_ini":data_ini,"data_fim":data_fim,"status":status,"vendedor":vendedor},
        relatorio_completo=relatorio_completo)

@app.route("/relatorios/financeiro")
def relatorio_financeiro():
    if not tem_permissao('relatorios','completo'):
        flash('Sem permissão para relatório financeiro.','erro'); return redirect(url_for('relatorios'))
    data_ini = request.args.get("data_ini","")
    data_fim = request.args.get("data_fim","")
    tipo_aba = request.args.get("tipo","receber")
    tab = "CONTAS_RECEBER" if tipo_aba == "receber" else "CONTAS_PAGAR"
    nome_col = "NOME_CLIENTE" if tipo_aba == "receber" else "NOME_FORNECEDOR"
    with get_connection("financeiro") as conn:
        cur = conn.cursor()
        where = ["1=1"]; params = []
        if data_ini: where.append("DATA_VENCIMENTO >= ?"); params.append(data_ini)
        if data_fim: where.append("DATA_VENCIMENTO <= ?"); params.append(data_fim)
        cur.execute(f"SELECT * FROM {tab} WHERE {' AND '.join(where)} ORDER BY DATA_VENCIMENTO", params)
        registros = cur.fetchall()
    totais = {
        "qtd": len(registros),
        "valor": sum(float(r.get("valor") or 0) for r in registros),
        "pago":  sum(float(r.get("valor_pago") or 0) for r in registros),
        "pendente": sum(float(r.get("valor") or 0) - float(r.get("valor_pago") or 0)
                       for r in registros if r.get("status") not in ("pago","recebido","cancelado")),
    }
    return render_template("relatorios/financeiro.html",
        registros=registros, totais=totais, tipo=tipo_aba,
        filtros={"data_ini":data_ini,"data_fim":data_fim,"tipo":tipo_aba})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
