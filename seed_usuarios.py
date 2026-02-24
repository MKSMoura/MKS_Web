import os, sys, datetime, hashlib, json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR); sys.path.insert(0, BASE_DIR)
from core.database import get_connection

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def h(s): return hashlib.sha256(s.encode()).hexdigest()

perms_gerente  = json.dumps({"clientes":["ver","criar","editar"],"produtos":["ver","criar","editar"],"pedidos":["ver","criar","editar"],"financeiro":["ver"],"fornecedores":["ver"],"relatorios":["ver","completo"],"usuarios":[]})
perms_vendedor = json.dumps({"clientes":["ver","criar"],"produtos":["ver"],"pedidos":["ver","criar","editar"],"financeiro":[],"fornecedores":[],"relatorios":["ver"],"usuarios":[]})
perms_fin      = json.dumps({"clientes":["ver"],"produtos":["ver"],"pedidos":["ver"],"financeiro":["ver","criar","editar"],"fornecedores":["ver","criar","editar"],"relatorios":["ver","completo"],"usuarios":[]})
perms_estoque  = json.dumps({"clientes":[],"produtos":["ver","criar","editar"],"pedidos":["ver"],"financeiro":[],"fornecedores":["ver"],"relatorios":["ver"],"usuarios":[]})

usuarios = [
    # ID, LOGIN, SENHA, NOME, EMAIL, PERFIL, PERMS, TROCAR
    (1,"admin",    "admin123",   "Administrador",     "admin@mksys.local",     "admin",    None,          "N"),
    (2,"gerente",  "gerente123", "Gerente Comercial", "gerente@mksys.local",   "gerente",  perms_gerente, "S"),
    (3,"carlos",   "carlos123",  "Carlos Vendedor",   "carlos@mksys.local",    "operador", perms_vendedor,"S"),
    (4,"julia",    "julia123",   "Julia Vendedora",   "julia@mksys.local",     "operador", perms_vendedor,"S"),
    (5,"marcos",   "marcos123",  "Marcos Vendedor",   "marcos@mksys.local",    "operador", perms_vendedor,"S"),
    (6,"financeiro","fin123",    "Usuario Financeiro","financeiro@mksys.local","operador", perms_fin,     "S"),
    (7,"estoque",  "estoque123", "Controle Estoque",  "estoque@mksys.local",   "operador", perms_estoque, "S"),
]

with get_connection("usuarios") as conn:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM USUARIOS")
    count = list(cur.fetchone().values())[0]
    if count > 0:
        print(f"Usuarios ja tem {count} registro(s). Seed ignorado.")
    else:
        # Verificar se coluna TROCAR_SENHA existe
        try:
            cur.execute("ALTER TABLE USUARIOS ADD TROCAR_SENHA CHAR(1) DEFAULT 'N'")
            conn.commit()
        except Exception:
            pass

        for uid,login,senha,nome,email,perfil,perms,trocar in usuarios:
            cur.execute("""INSERT INTO USUARIOS
                (ID,LOGIN,SENHA_HASH,NOME,EMAIL,PERFIL,ATIVO,PERMISSOES,DATA_CADASTRO,TROCAR_SENHA)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (uid,login,h(senha),nome,email,perfil,"S",perms,now,trocar))
        conn.commit()
        print(f"Inseridos {len(usuarios)} usuarios!")
        print()
        print("Logins:")
        for _,login,senha,nome,_,perfil,_,_ in usuarios:
            print(f"  {login:12} / {senha:12}  ({perfil})")
