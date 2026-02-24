"""
SEED COMPLETO — cria bancos, tabelas e dados do zero.
Uso: py seed_tudo.py
"""
import os, sys, datetime, hashlib, json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

import firebirdsql

HOST  = "localhost"
USER  = "SYSDBA"
PASS  = "masterkey"
DATA  = os.path.join(BASE_DIR, "data")
os.makedirs(DATA, exist_ok=True)

NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def h256(s):
    return hashlib.sha256(s.encode()).hexdigest()

def db_path(nome):
    return os.path.join(DATA, f"{nome}.fdb")

def criar_ou_abrir(nome):
    path = db_path(nome)
    if not os.path.exists(path):
        conn = firebirdsql.create_database(
            host=HOST, database=path, user=USER, password=PASS, charset="UTF8")
        print(f"  Banco {nome}.fdb CRIADO")
    else:
        conn = firebirdsql.connect(
            host=HOST, database=path, user=USER, password=PASS, charset="UTF8")
        print(f"  Banco {nome}.fdb ja existe")
    return conn

def tabela_existe(conn, nome):
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM RDB$RELATIONS WHERE RDB$RELATION_NAME=?",
        (nome.upper(),))
    return cur.fetchone()[0] > 0

def coluna_existe(conn, tabela, coluna):
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM RDB$RELATION_FIELDS WHERE RDB$RELATION_NAME=? AND RDB$FIELD_NAME=?",
        (tabela.upper(), coluna.upper()))
    return cur.fetchone()[0] > 0

def contar(conn, tabela):
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {tabela}")
    return cur.fetchone()[0]

def add_col(conn, tabela, col, ddl):
    if not coluna_existe(conn, tabela, col):
        try:
            conn.cursor().execute(f"ALTER TABLE {tabela} ADD {col} {ddl}")
            conn.commit()
            print(f"    Coluna {col} adicionada em {tabela}")
        except Exception as e:
            print(f"    Aviso ao adicionar {col}: {e}")

# ═══════════════════════════════════════════════
print("\n>>> CLIENTES PF")
# ═══════════════════════════════════════════════
conn = criar_ou_abrir("clientes_pf")
cur  = conn.cursor()
if not tabela_existe(conn, "CLIENTES_PF"):
    cur.execute("""CREATE TABLE CLIENTES_PF (
        ID INTEGER NOT NULL PRIMARY KEY,
        NOME VARCHAR(255), CPF VARCHAR(20),
        DATA_NASCIMENTO VARCHAR(20),
        RUA VARCHAR(255), NUMERO VARCHAR(20), COMPLEMENTO VARCHAR(100),
        BAIRRO VARCHAR(100), CIDADE VARCHAR(100), ESTADO VARCHAR(20), CEP VARCHAR(20),
        TELEFONE VARCHAR(50), DATA_CADASTRO VARCHAR(30),
        OBSERVACOES BLOB SUB_TYPE TEXT, DEPENDENTES BLOB SUB_TYPE TEXT
    )""")
    conn.commit()
    print("  Tabela CLIENTES_PF criada")
if contar(conn, "CLIENTES_PF") > 0:
    print("  Ja tem dados, pulando.")
else:
    dados = [
        (1,"Ana Paula Ferreira",     "529.982.247-25","1990-03-15","Rua das Flores",       "123","Apto 4", "Jardim America",  "Sao Paulo",      "SP","01310-100","(11) 3255-0001",""),
        (2,"Bruno Henrique Souza",   "897.064.196-71","1985-07-22","Av. Paulista",          "900","",       "Bela Vista",      "Sao Paulo",      "SP","01310-200","(11) 3255-0002","Pedidos frequentes"),
        (3,"Carla Mendes Oliveira",  "101.202.303-04","1993-11-08","Rua XV de Novembro",   "45", "Sala 2", "Centro",          "Curitiba",       "PR","80020-310","(41) 3255-0003",""),
        (4,"Daniel Costa Lima",      "222.333.444-55","1978-05-30","Rua Sete de Setembro", "200","",       "Centro",          "Rio de Janeiro", "RJ","20050-006","(21) 3255-0004","Preferencia boleto"),
        (5,"Eduarda Santos Ribeiro", "333.444.555-66","1995-09-14","Rua das Acacias",      "78", "Casa",   "Bairro Novo",     "Belo Horizonte", "MG","30130-110","(31) 3255-0005",""),
        (6,"Felipe Alves Martins",   "444.555.666-77","1982-01-25","Av. Brasil",           "1500","Apto 12","Tambore",        "Barueri",        "SP","06460-030","(11) 3255-0006","Cliente VIP"),
        (7,"Gabriela Nunes Pereira", "555.666.777-88","1999-06-03","Rua Marechal Deodoro", "33", "",       "Centro",          "Florianopolis",  "SC","88010-060","(48) 3255-0007",""),
    ]
    for uid,nome,cpf,nasc,rua,num,comp,bairro,cidade,uf,cep,tel,obs in dados:
        cur.execute("""INSERT INTO CLIENTES_PF
            (ID,NOME,CPF,DATA_NASCIMENTO,RUA,NUMERO,COMPLEMENTO,
             BAIRRO,CIDADE,ESTADO,CEP,TELEFONE,DATA_CADASTRO,OBSERVACOES)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (uid,nome,cpf,nasc,rua,num,comp,bairro,cidade,uf,cep,tel,NOW,obs))
    conn.commit()
    print(f"  {len(dados)} clientes PF inseridos")
conn.close()

# ═══════════════════════════════════════════════
print("\n>>> CLIENTES PJ")
# ═══════════════════════════════════════════════
conn = criar_ou_abrir("clientes_pj")
cur  = conn.cursor()
if not tabela_existe(conn, "CLIENTES_PJ"):
    cur.execute("""CREATE TABLE CLIENTES_PJ (
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
    print("  Tabela CLIENTES_PJ criada")
if contar(conn, "CLIENTES_PJ") > 0:
    print("  Ja tem dados, pulando.")
else:
    dados = [
        (1,"11.222.333/0001-81","111.222.333.444","Supermercados Horizonte Ltda","Hiper Horizonte","(11) 3300-1100","01310-001","Av. Paulista",         "1000","Loja 1","Bela Vista",    "Sao Paulo",      "SP","12345678901","Marcos Horizonte","(11) 99100-0001","Rede 3 filiais"),
        (2,"22.333.444/0001-82","222.333.444.555","Distribuidora Norte Sul S.A.","Norte Sul Dist.","(21) 3300-1200","20040-020","Rua da Alfandega",     "50",  "",     "Centro",         "Rio de Janeiro", "RJ","23456789012","Fernanda Norte",  "(21) 99100-0002","Grande volume"),
        (3,"33.444.555/0001-83","333.444.555.666","Papelaria Central Eireli",    "Papel e Cia",   "(41) 3300-1300","80010-000","Rua XV de Novembro",   "200", "S.3",  "Centro",         "Curitiba",       "PR","34567890123","Roberto Central", "(41) 99100-0003",""),
        (4,"44.555.666/0001-84","444.555.666.777","Farmacia Bem Estar ME",       "Bem Estar",     "(31) 3300-1400","30130-010","Av. Afonso Pena",      "800", "",     "Centro",         "Belo Horizonte", "MG","45678901234","Lucia Bem Estar", "(31) 99100-0004","Pedidos mensais"),
        (5,"55.666.777/0001-85","555.666.777.888","Construtora Alfa Beta Ltda",  "Alfa Beta",     "(47) 3300-1500","89010-100","Rua Blumenau",         "450", "",     "Centro",         "Joinville",      "SC","56789012345","Carlos Alfa",     "(47) 99100-0005",""),
        (6,"66.777.888/0001-86","666.777.888.999","TechSoft Solucoes LTDA",      "TechSoft",      "(51) 3300-1600","90010-150","Av. Borges de Medeiros","300","Sl.5", "Centro Hist.",   "Porto Alegre",   "RS","67890123456","Patricia Tech",   "(51) 99100-0006","Cliente VIP"),
        (7,"77.888.999/0001-87","777.888.999.000","Agro Campo Verde Ltda",       "Campo Verde",   "(67) 3300-1700","77001-000","Av. Goias",            "1200","",     "Setor Central",  "Goiania",        "GO","78901234567","Jose Campo",      "(67) 99100-0007","Sazonalidade set/out"),
    ]
    for uid,cnpj,ie,razao,fantasia,tel,cep,rua,num,comp,bairro,cidade,uf,cpf_r,nome_r,tel_r,obs in dados:
        cur.execute("""INSERT INTO CLIENTES_PJ
            (ID,CNPJ,INSCRICAO_ESTADUAL,RAZAO_SOCIAL,NOME_FANTASIA,
             TELEFONE,CEP,RUA,NUMERO,COMPLEMENTO,BAIRRO,CIDADE,ESTADO,
             CPF_RESPONSAVEL,NOME_RESPONSAVEL,TELEFONE_RESPONSAVEL,
             DATA_CADASTRO,OBSERVACOES)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (uid,cnpj,ie,razao,fantasia,tel,cep,rua,num,comp,bairro,cidade,uf,
             cpf_r,nome_r,tel_r,NOW,obs))
    conn.commit()
    print(f"  {len(dados)} clientes PJ inseridos")
conn.close()

# ═══════════════════════════════════════════════
print("\n>>> PRODUTOS")
# ═══════════════════════════════════════════════
conn = criar_ou_abrir("produtos")
cur  = conn.cursor()
if not tabela_existe(conn, "PRODUTOS"):
    cur.execute("""CREATE TABLE PRODUTOS (
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
    print("  Tabela PRODUTOS criada")
if contar(conn, "PRODUTOS") > 0:
    print("  Ja tem dados, pulando.")
else:
    # SKU, CB, NOME, CAT, SUBCAT, MARCA, CUSTO, VENDA, UNID, EMB, FORN, EST, EMIN, EMAX
    dados = [
        ("ALI-001","7891234000001","Arroz Branco Tipo 1 5kg",  "Alimentos","Graos",    "Camil",     14.50,18.90,"SC", 1,"Camil Alimentos",  150,20,300),
        ("ALI-002","7891234000002","Feijao Carioca 1kg",        "Alimentos","Graos",    "Camil",      6.20, 9.50,"PC", 1,"Camil Alimentos",  200,30,400),
        ("ALI-003","7891234000003","Macarrao Espaguete 500g",   "Alimentos","Massas",   "Barilla",    3.80, 6.90,"PC", 1,"Barilla Brasil",   180,30,350),
        ("ALI-004","7891234000004","Molho de Tomate 340g",      "Alimentos","Conservas","Heinz",      2.50, 4.90,"UN", 1,"Heinz Brasil",     120,20,250),
        ("ALI-005","7891234000005","Oleo de Soja 900ml",        "Alimentos","Oleos",    "Liza",       4.90, 7.80,"UN", 1,"Bunge Alimentos",  100,15,200),
        ("ALI-006","7891234000006","Acucar Cristal 1kg",        "Alimentos","Acucar",   "Uniao",      3.20, 5.50,"PC", 1,"Acucar Uniao",     180,25,360),
        ("ALI-007","7891234000007","Sal Refinado 1kg",          "Alimentos","Temperos", "Cisne",      1.40, 2.90,"PC", 1,"Cisne",            200,30,400),
        ("ALI-008","7891234000008","Leite Integral UHT 1L",     "Alimentos","Laticinios","Italac",    3.10, 4.90,"LT",12,"Italac",           240,40,500),
        ("ALI-009","7891234000009","Cafe Torrado Moido 500g",   "Alimentos","Cafe",     "Pilao",      9.80,14.90,"PC", 1,"Pilao",            100,15,200),
        ("ALI-010","7891234000010","Farinha de Trigo 1kg",      "Alimentos","Farinhas", "Dona Benta", 4.20, 6.90,"PC", 1,"Moinho Pacifico",  150,20,300),
        ("BEB-001","7891234000011","Refrigerante Cola 2L",      "Bebidas",  "Refrig",   "Coca-Cola",  7.20,12.90,"UN", 6,"Ambev",             80,12,160),
        ("BEB-002","7891234000012","Agua Mineral 500ml",        "Bebidas",  "Agua",     "Crystal",    0.90, 2.50,"UN",12,"Crystal",          200,30,400),
        ("BEB-003","7891234000013","Suco de Laranja 1L",        "Bebidas",  "Sucos",    "Del Valle",  4.50, 7.90,"LT", 6,"Coca-Cola",         90,15,180),
        ("BEB-004","7891234000014","Cerveja Long Neck 355ml",   "Bebidas",  "Cervejas", "Heineken",   4.80, 8.90,"UN",24,"Heineken Brasil",   60,10,120),
        ("BEB-005","7891234000015","Isotonico 500ml",           "Bebidas",  "Energet",  "Gatorade",   3.60, 6.90,"UN",12,"PepsiCo",           70,12,140),
        ("HIG-001","7891234000016","Papel Higienico 12 rolos",  "Higiene",  "Papel",    "Neve",       9.80,16.90,"PC", 4,"Kimberly Clark",   60,10,120),
        ("HIG-002","7891234000017","Sabonete Barra 90g",        "Higiene",  "Sabonete", "Dove",       2.10, 4.50,"UN", 6,"Unilever",          90,15,180),
        ("HIG-003","7891234000018","Shampoo 400ml",             "Higiene",  "Cabelos",  "Head Shoulders",8.90,19.90,"UN",1,"Procter",        50, 8,100),
        ("HIG-004","7891234000019","Creme Dental 90g",          "Higiene",  "Dental",   "Colgate",    3.40, 6.90,"UN",12,"Colgate-Palmolive", 80,12,160),
        ("HIG-005","7891234000020","Desodorante Aerosol 150ml", "Higiene",  "Desod",    "Rexona",     8.20,14.90,"UN", 1,"Unilever",          60,10,120),
        ("LIM-001","7891234000021","Detergente Liquido 500ml",  "Limpeza",  "Pratos",   "Ype",        2.10, 4.20,"UN",24,"Ype",              100,15,200),
        ("LIM-002","7891234000022","Amaciante 2L",              "Limpeza",  "Roupas",   "Downy",      7.90,13.90,"UN", 6,"Procter",           60,10,120),
        ("LIM-003","7891234000023","Sabao em Po 1kg",           "Limpeza",  "Roupas",   "Ariel",      8.50,15.90,"PC", 1,"Procter",           70,12,140),
        ("LIM-004","7891234000024","Agua Sanitaria 1L",         "Limpeza",  "Desinf",   "Qboa",       2.80, 5.50,"UN",12,"Clorox Brasil",     80,12,160),
        ("LIM-005","7891234000025","Esponja de Aco 60g",        "Limpeza",  "Utensilios","Bom Bril",  1.80, 3.90,"PC", 1,"Bom Bril",        120,20,250),
        ("FRI-001","7891234000026","Salgadinho de Milho 100g",  "Snacks",   "Salgados", "Cheetos",    2.90, 5.90,"PC", 1,"PepsiCo",           80,12,160),
        ("FRI-002","7891234000027","Batata Chips 150g",         "Snacks",   "Salgados", "Ruffles",    5.50, 9.90,"PC", 1,"PepsiCo",           70,10,140),
        ("FRI-003","7891234000028","Biscoito Recheado 140g",    "Snacks",   "Biscoitos","Oreo",        3.20, 6.50,"PC", 1,"Mondelez",          90,15,180),
        ("PET-001","7891234000029","Racao Cao Adulto 15kg",     "Pet",      "Racao",    "Pedigree",  55.00,99.90,"SC", 1,"Mars Petcare",       30, 5, 60),
        ("PET-002","7891234000030","Racao Gato Adulto 3kg",     "Pet",      "Racao",    "Whiskas",   18.00,34.90,"PC", 1,"Mars Petcare",       40, 6, 80),
        ("PET-003","7891234000031","Areia para Gatos 4kg",      "Pet",      "Higiene",  "Pipicat",   14.00,25.90,"PC", 1,"Pipicat",           50, 8,100),
        ("FLV-001","7891234000032","Banana Prata kg",           "FLV",      "Frutas",   "A Granel",   2.50, 4.90,"KG", 1,"Ceagesp",           50,10,100),
        ("FLV-002","7891234000033","Tomate Salada kg",          "FLV",      "Verduras", "A Granel",   4.80, 8.90,"KG", 1,"Ceagesp",           30, 5, 60),
        ("FLV-003","7891234000034","Batata Inglesa kg",         "FLV",      "Tuberculos","A Granel",  3.20, 5.90,"KG", 1,"Ceagesp",           60,10,120),
        ("PAD-001","7891234000035","Pao Frances 50g",           "Padaria",  "Paes",     "Padaria Local",0.50,0.99,"UN",10,"Padaria Local",   200,50,500),
        ("PAD-002","7891234000036","Bolo de Chocolate 500g",    "Padaria",  "Bolos",    "Wickbold",  12.00,22.90,"UN", 1,"Wickbold",          20, 4, 40),
        ("AC-001", "7891234000037","Chocolate ao Leite 100g",   "Doces",    "Chocolates","Lacta",     4.50, 8.90,"PC", 1,"Mondelez",          80,12,160),
        ("AC-002", "7891234000038","Sorvete Pote 1.5L",         "Doces",    "Sorvetes", "Kibon",     13.00,24.90,"UN", 1,"Unilever",          30, 5, 60),
        ("AC-003", "7891234000039","Geleia de Morango 340g",    "Doces",    "Geleias",  "Queensberry",5.80, 9.90,"UN", 1,"Queensberry",       50, 8,100),
        ("CON-001","7891234000040","Atum em Lata 170g",         "Conservas","Peixes",   "Coqueiro",   5.20, 9.50,"UN",12,"Coqueiro",          70,12,140),
    ]
    for i, (sku,cb,nome,cat,sub,marca,custo,venda,unid,emb,forn,est,emin,emax) in enumerate(dados, 1):
        margem = round((venda-custo)/venda*100, 2) if venda else 0
        cur.execute("""INSERT INTO PRODUTOS
            (ID,SKU,CODIGO_BARRAS,NOME,CATEGORIA,SUBCATEGORIA,MARCA,
             PRECO_CUSTO,PRECO_VENDA,MARGEM,UNIDADE_MEDIDA,QTD_EMBALAGEM,
             FORNECEDOR_PRINCIPAL,QTD_ESTOQUE,ESTOQUE_MINIMO,ESTOQUE_MAXIMO,
             STATUS,PRODUTO_CONTROLADO,PERMITE_DESCONTO,DATA_CADASTRO,DATA_ATUALIZACAO)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (i,sku,cb,nome,cat,sub,marca,custo,venda,margem,unid,emb,
             forn,float(est),float(emin),float(emax),
             "ativo","N","S",NOW,NOW))
    conn.commit()
    print(f"  {len(dados)} produtos inseridos")
conn.close()

# ═══════════════════════════════════════════════
print("\n>>> FORNECEDORES")
# ═══════════════════════════════════════════════
conn = criar_ou_abrir("fornecedores")
cur  = conn.cursor()
if not tabela_existe(conn, "FORNECEDORES"):
    cur.execute("""CREATE TABLE FORNECEDORES (
        ID INTEGER NOT NULL PRIMARY KEY,
        TIPO CHAR(2) DEFAULT 'PJ',
        RAZAO_SOCIAL VARCHAR(255), NOME_FANTASIA VARCHAR(150),
        CNPJ VARCHAR(20), CPF VARCHAR(15), IE VARCHAR(20),
        EMAIL VARCHAR(150), TELEFONE VARCHAR(20), CELULAR VARCHAR(20),
        CONTATO_NOME VARCHAR(150),
        CEP VARCHAR(10), RUA VARCHAR(255), NUMERO VARCHAR(20),
        COMPLEMENTO VARCHAR(100), BAIRRO VARCHAR(100),
        CIDADE VARCHAR(100), ESTADO VARCHAR(2),
        BANCO VARCHAR(100), AGENCIA VARCHAR(20), CONTA VARCHAR(30),
        PIX VARCHAR(150), PRAZO_PAGAMENTO INTEGER DEFAULT 30,
        CATEGORIA VARCHAR(100), STATUS VARCHAR(10) DEFAULT 'ativo',
        OBSERVACOES BLOB SUB_TYPE TEXT,
        DATA_CADASTRO VARCHAR(30), DATA_ATUALIZACAO VARCHAR(30)
    )""")
    conn.commit()
    print("  Tabela FORNECEDORES criada")
if contar(conn, "FORNECEDORES") > 0:
    print("  Ja tem dados, pulando.")
else:
    dados = [
        (1,"Camil Alimentos S.A.",     "Camil",       "11.111.111/0001-91","vendas@camil.com.br",    "(11) 3000-1001","Joao Camil",   "09930-460","Av. das Nacoes Unidas","12901","Brooklin",         "Sao Paulo","SP","Bradesco","vendas@camil.com.br",     30,"Alimentos"),
        (2,"Bunge Alimentos S.A.",     "Bunge",       "22.222.222/0001-92","sac@bunge.com.br",        "(15) 3000-1002","Maria Bunge",  "13062-610","Rua Min. Joao Inverse","800",  "Chacara Primavera","Campinas", "SP","Itau",    "sac@bunge.com.br",        28,"Alimentos"),
        (3,"Ambev S.A.",               "Ambev",       "33.333.333/0001-93","ambev@ambev.com.br",      "(11) 3000-1003","Pedro Ambev",  "05427-070","Rua Dr. Renato Paes",  "1017","Pinheiros",        "Sao Paulo","SP","Bradesco","pix@ambev.com.br",         21,"Bebidas"),
        (4,"Unilever Brasil Ltda",     "Unilever",    "44.444.444/0001-94","trade@unilever.com",      "(11) 3000-1004","Sandra Uni",   "04749-000","Av. Jabaquara",        "3467","Mirandopolis",     "Sao Paulo","SP","Santander","trade@unilever.com",       30,"Higiene"),
        (5,"Nestle Brasil Ltda",       "Nestle",      "55.555.555/0001-95","nestle@nestle.com.br",    "(11) 3000-1005","Carlos Nestle","04795-100","Av. das Nacoes Unidas","12995","Brooklin Novo",    "Sao Paulo","SP","Itau",    "nestle@nestle.com.br",     30,"Alimentos"),
        (6,"Mars Petcare Brasil Ltda", "Mars Petcare","66.666.666/0001-96","petcare@mars.com",        "(11) 3000-1006","Laura Mars",   "06454-000","Av. Dr. Chucri Zaidan","920",  "Vila Cordeiro",    "Sao Paulo","SP","Bradesco","petcare@mars.com",         45,"Pet"),
        (7,"PepsiCo do Brasil Ltda",   "PepsiCo",     "77.777.777/0001-97","pepsico@pepsico.com",     "(11) 3000-1007","Andre Pepsi",  "06010-903","Av. das Nacoes Unidas","7221","Pinheiros",        "Sao Paulo","SP","Santander","pepsico@pepsico.com",      30,"Bebidas"),
    ]
    for uid,razao,fantasia,cnpj,email,tel,contato,cep,rua,num,bairro,cidade,uf,banco,pix,prazo,cat in dados:
        cur.execute("""INSERT INTO FORNECEDORES
            (ID,TIPO,RAZAO_SOCIAL,NOME_FANTASIA,CNPJ,EMAIL,TELEFONE,CONTATO_NOME,
             CEP,RUA,NUMERO,BAIRRO,CIDADE,ESTADO,BANCO,PIX,
             PRAZO_PAGAMENTO,CATEGORIA,STATUS,DATA_CADASTRO,DATA_ATUALIZACAO)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (uid,"PJ",razao,fantasia,cnpj,email,tel,contato,
             cep,rua,num,bairro,cidade,uf,banco,pix,prazo,cat,"ativo",NOW,NOW))
    conn.commit()
    print(f"  {len(dados)} fornecedores inseridos")
conn.close()

# ═══════════════════════════════════════════════
print("\n>>> PEDIDOS")
# ═══════════════════════════════════════════════
conn = criar_ou_abrir("pedidos")
cur  = conn.cursor()
if not tabela_existe(conn, "PEDIDOS"):
    cur.execute("""CREATE TABLE PEDIDOS (
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
    cur.execute("""CREATE TABLE PEDIDO_ITENS (
        ID INTEGER NOT NULL PRIMARY KEY,
        PEDIDO_ID INTEGER NOT NULL,
        SKU VARCHAR(50), NOME_PRODUTO VARCHAR(255),
        QUANTIDADE DECIMAL(12,3), UNIDADE VARCHAR(20),
        VALOR_UNITARIO DECIMAL(12,2), VALOR_TOTAL DECIMAL(12,2)
    )""")
    conn.commit()
    print("  Tabelas PEDIDOS e PEDIDO_ITENS criadas")
if contar(conn, "PEDIDOS") > 0:
    print("  Ja tem dados, pulando.")
else:
    pedidos = [
        (1,"PED260200001","2026-01-05","09:15","faturado", "VND001","Carlos Vendedor",1,"Ana Paula Ferreira",     "52998224725",   0, 0,"PIX",           "Entrega rapida"),
        (2,"PED260200002","2026-01-12","10:30","faturado", "VND001","Carlos Vendedor",2,"Bruno Henrique Souza",   "89706419671",  15, 0,"Cartao Debito", ""),
        (3,"PED260200003","2026-01-20","14:00","cancelado","VND002","Julia Vendedora", 3,"Carla Mendes Oliveira",  "10120230304",   0, 0,"Dinheiro",      "Cancelado pelo cliente"),
        (4,"PED260200004","2026-02-03","08:45","faturado", "VND002","Julia Vendedora", 1,"Supermercados Horizonte","11222333000181",50, 0,"Boleto",        "Pedido grande"),
        (5,"PED260200005","2026-02-10","11:00","faturado", "VND001","Carlos Vendedor",5,"Eduarda Santos Ribeiro", "33344455566",   0, 5,"PIX",           "Frete incluido"),
        (6,"PED260200006","2026-02-18","15:30","aberto",   "VND003","Marcos Vendedor", 6,"TechSoft Solucoes",      "66777888000186",0, 0,"A prazo",       "Aguardando aprovacao"),
        (7,"PED260200007","2026-02-23","09:00","aberto",   "VND001","Carlos Vendedor",7,"Gabriela Nunes Pereira", "55566677788",   0, 0,"Cartao Credito",""),
    ]
    itens = {
        1:[("ALI-001","Arroz Branco 5kg",    5, "SC",18.90),("ALI-008","Leite UHT 1L",      24,"LT", 4.90)],
        2:[("BEB-001","Refrig. Cola 2L",    12, "UN",12.90),("FRI-002","Batata Chips 150g", 10,"PC", 9.90)],
        3:[("HIG-001","Papel Hig. 12un",     6, "PC",16.90)],
        4:[("ALI-001","Arroz Branco 5kg",   50, "SC",18.90),("ALI-002","Feijao Carioca 1kg",30,"PC", 9.50),("ALI-005","Oleo Soja 900ml",24,"UN",7.80)],
        5:[("PET-001","Racao Cao 15kg",      3, "SC",99.90),("PET-003","Areia Gatos 4kg",   5,"PC",25.90)],
        6:[("LIM-003","Sabao Po 1kg",       20, "PC",15.90),("LIM-001","Detergente 500ml",  30,"UN", 4.20)],
        7:[("HIG-003","Shampoo 400ml",       4, "UN",19.90),("HIG-004","Creme Dental 90g",  6,"UN", 6.90),("HIG-005","Desod. Aerosol",4,"UN",14.90)],
    }
    item_id = 1
    for uid,numero,data,hora,status,cod_v,nome_v,cod_c,nome_c,doc,desc,acre,forma,obs in pedidos:
        lista    = itens.get(uid,[])
        subtotal = round(sum(q*vu for _,_,q,_,vu in lista), 2)
        total    = round(subtotal - desc + acre, 2)
        cur.execute("""INSERT INTO PEDIDOS
            (ID,NUMERO,DATA_PEDIDO,HORA_PEDIDO,STATUS,
             COD_VENDEDOR,NOME_VENDEDOR,COD_CLIENTE,NOME_CLIENTE,CPF_CNPJ,
             SUBTOTAL,DESCONTO,ACRESCIMO,TOTAL,FORMA_PAGAMENTO,OBSERVACOES,
             USUARIO_CRIOU,DATA_CRIACAO,DATA_ATUALIZACAO)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (uid,numero,data,hora,status,cod_v,nome_v,cod_c,nome_c,doc,
             subtotal,float(desc),float(acre),total,forma,obs,"admin",NOW,NOW))
        for sku,nome_p,qtd,un,vu in lista:
            cur.execute("""INSERT INTO PEDIDO_ITENS
                (ID,PEDIDO_ID,SKU,NOME_PRODUTO,QUANTIDADE,UNIDADE,VALOR_UNITARIO,VALOR_TOTAL)
                VALUES (?,?,?,?,?,?,?,?)""",
                (item_id,uid,sku,nome_p,float(qtd),un,vu,round(qtd*vu,2)))
            item_id += 1
    conn.commit()
    print(f"  {len(pedidos)} pedidos com itens inseridos")
conn.close()

# ═══════════════════════════════════════════════
print("\n>>> FINANCEIRO")
# ═══════════════════════════════════════════════
conn = criar_ou_abrir("financeiro")
cur  = conn.cursor()
if not tabela_existe(conn, "CONTAS_RECEBER"):
    cur.execute("""CREATE TABLE CONTAS_RECEBER (
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
    print("  Tabela CONTAS_RECEBER criada")
if not tabela_existe(conn, "CONTAS_PAGAR"):
    cur.execute("""CREATE TABLE CONTAS_PAGAR (
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
    print("  Tabela CONTAS_PAGAR criada")
if not tabela_existe(conn, "CATEGORIAS_FIN"):
    cur.execute("""CREATE TABLE CATEGORIAS_FIN (
        ID INTEGER NOT NULL PRIMARY KEY,
        NOME VARCHAR(100), TIPO CHAR(1), COR VARCHAR(10)
    )""")
    conn.commit()
    for c in [(1,"Vendas","R","#4ade80"),(2,"Servicos","R","#38bdf8"),(3,"Outros","R","#a78bfa"),
              (4,"Fornecedores","P","#f87171"),(5,"Salarios","P","#fb923c"),(6,"Aluguel","P","#facc15"),
              (7,"Utilidades","P","#94a3b8"),(8,"Marketing","P","#f472b6"),
              (9,"Logistica","P","#34d399"),(10,"Impostos","P","#f97316")]:
        cur.execute("INSERT INTO CATEGORIAS_FIN (ID,NOME,TIPO,COR) VALUES (?,?,?,?)", c)
    conn.commit()
    print("  Tabela CATEGORIAS_FIN criada com 10 categorias")
cr = contar(conn,"CONTAS_RECEBER")
cp = contar(conn,"CONTAS_PAGAR")
if cr > 0 or cp > 0:
    print(f"  Ja tem dados (CR:{cr} CP:{cp}), pulando.")
else:
    receber = [
        (1,"Ped.PED260200001 - Ana Paula",    1,"Ana Paula Ferreira",     1,"PED260200001", 136.30,136.30,"2026-01-05","2026-01-12","2026-01-10","recebido","PIX"),
        (2,"Ped.PED260200002 - Bruno",        2,"Bruno Henrique Souza",   2,"PED260200002", 228.80,228.80,"2026-01-12","2026-01-19","2026-01-18","recebido","Cartao Debito"),
        (3,"Ped.PED260200004 - Horizonte",    1,"Supermercados Horizonte", 4,"PED260200004",1111.50,1111.50,"2026-02-03","2026-02-17","2026-02-15","recebido","Boleto"),
        (4,"Ped.PED260200005 - Eduarda",      5,"Eduarda Santos Ribeiro", 5,"PED260200005", 434.20,434.20,"2026-02-10","2026-02-17","2026-02-16","recebido","PIX"),
        (5,"Ped.PED260200006 - TechSoft",     6,"TechSoft Solucoes",      6,"PED260200006", 444.00,  0,   "2026-02-18","2026-03-18",None,        "aberto",  "A prazo"),
        (6,"Ped.PED260200007 - Gabriela",     7,"Gabriela Nunes Pereira", 7,"PED260200007", 207.10,  0,   "2026-02-23","2026-03-02",None,        "aberto",  "Cartao Credito"),
        (7,"Mensalidade Servico Premium Jan", None,"—",                  None,None,          350.00,350.00,"2026-01-01","2026-01-10","2026-01-08","recebido","PIX"),
    ]
    pagar = [
        (1,"NF 12345 Arroz Feijao Camil",    1,"Camil Alimentos",   "Fornecedores",2350.00,2350.00,"2026-01-03","2026-02-02","2026-02-01","pago",  "Boleto"),
        (2,"NF 23456 Oleo Soja Bunge",       2,"Bunge Alimentos",   "Fornecedores",1176.00,1176.00,"2026-01-10","2026-02-09","2026-02-08","pago",  "Transferencia"),
        (3,"NF 34567 Bebidas Ambev",         3,"Ambev",             "Fornecedores",3120.00,    0,  "2026-02-01","2026-03-03",None,        "aberto","Boleto"),
        (4,"Aluguel Galpao Fevereiro",      None,"Imob. Paulista",   "Aluguel",     4500.00,4500.00,"2026-02-01","2026-02-10","2026-02-10","pago",  "Transferencia"),
        (5,"Folha de Pagamento Fevereiro",  None,"—",               "Salarios",    8200.00,8200.00,"2026-02-25","2026-02-28","2026-02-28","pago",  "Transferencia"),
        (6,"NF 45678 Higiene Unilever",      4,"Unilever",          "Fornecedores",1890.00,    0,  "2026-02-15","2026-03-17",None,        "aberto","Boleto"),
        (7,"Energia Eletrica Fevereiro",    None,"Enel",            "Utilidades",   620.00,    0,  "2026-02-20","2026-03-10",None,        "aberto","Debito Automatico"),
    ]
    for uid,desc,cli_id,nome_cli,ped_id,num_ped,valor,pago,emis,venc,pgto,status,forma in receber:
        cur.execute("""INSERT INTO CONTAS_RECEBER
            (ID,DESCRICAO,CLIENTE_ID,NOME_CLIENTE,PEDIDO_ID,NUMERO_PEDIDO,
             VALOR,VALOR_PAGO,DATA_EMISSAO,DATA_VENCIMENTO,DATA_PAGAMENTO,
             STATUS,FORMA_PAGAMENTO,USUARIO_LANCOU,DATA_LANCAMENTO)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (uid,desc,cli_id,nome_cli,ped_id,num_ped,valor,pago,emis,venc,pgto,status,forma,"admin",NOW))
    for uid,desc,fid,nome_f,cat,valor,pago,emis,venc,pgto,status,forma in pagar:
        cur.execute("""INSERT INTO CONTAS_PAGAR
            (ID,DESCRICAO,FORNECEDOR_ID,NOME_FORNECEDOR,CATEGORIA,
             VALOR,VALOR_PAGO,DATA_EMISSAO,DATA_VENCIMENTO,DATA_PAGAMENTO,
             STATUS,FORMA_PAGAMENTO,USUARIO_LANCOU,DATA_LANCAMENTO)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (uid,desc,fid,nome_f,cat,valor,pago,emis,venc,pgto,status,forma,"admin",NOW))
    conn.commit()
    print(f"  {len(receber)} recebimentos e {len(pagar)} pagamentos inseridos")
conn.close()

# ═══════════════════════════════════════════════
print("\n>>> USUARIOS")
# ═══════════════════════════════════════════════
conn = criar_ou_abrir("usuarios")
cur  = conn.cursor()
if not tabela_existe(conn, "USUARIOS"):
    cur.execute("""CREATE TABLE USUARIOS (
        ID INTEGER NOT NULL PRIMARY KEY,
        LOGIN VARCHAR(50) NOT NULL, SENHA_HASH VARCHAR(255) NOT NULL,
        NOME VARCHAR(150), EMAIL VARCHAR(150),
        PERFIL VARCHAR(20) DEFAULT 'vendedor',
        ATIVO CHAR(1) DEFAULT 'S',
        PERMISSOES BLOB SUB_TYPE TEXT,
        TROCAR_SENHA CHAR(1) DEFAULT 'N',
        DATA_CADASTRO VARCHAR(30), ULTIMO_ACESSO VARCHAR(30)
    )""")
    conn.commit()
    print("  Tabela USUARIOS criada")
else:
    # garantir coluna TROCAR_SENHA em banco antigo
    add_col(conn, "USUARIOS", "TROCAR_SENHA", "CHAR(1) DEFAULT 'N'")

if contar(conn, "USUARIOS") > 0:
    print("  Ja tem dados, pulando.")
else:
    pv = json.dumps({"clientes":["ver","criar"],"produtos":["ver"],"pedidos":["ver","criar","editar"],"financeiro":[],"fornecedores":[],"relatorios":["ver"],"usuarios":[]})
    pg = json.dumps({"clientes":["ver","criar","editar"],"produtos":["ver","criar","editar"],"pedidos":["ver","criar","editar"],"financeiro":["ver"],"fornecedores":["ver"],"relatorios":["ver","completo"],"usuarios":[]})
    pf = json.dumps({"clientes":["ver"],"produtos":["ver"],"pedidos":["ver"],"financeiro":["ver","criar","editar"],"fornecedores":["ver","criar","editar"],"relatorios":["ver","completo"],"usuarios":[]})
    pe = json.dumps({"clientes":[],"produtos":["ver","criar","editar"],"pedidos":["ver"],"financeiro":[],"fornecedores":["ver"],"relatorios":["ver"],"usuarios":[]})

    usuarios = [
        (1,"admin",     "admin123",  "Administrador",     "admin@mksys.local",     "admin",   None,"N"),
        (2,"administrativo",   "administrativo123","Administrativo Comercial",  "administrativo@mksys.local",   "administrativo", pg,  "S"),
        (3,"carlos",    "carlos123", "Carlos Vendedor",    "carlos@mksys.local",    "vendedor",pv,  "S"),
        (4,"julia",     "julia123",  "Julia Vendedora",    "julia@mksys.local",     "vendedor",pv,  "S"),
        (5,"marcos",    "marcos123", "Marcos Vendedor",    "marcos@mksys.local",    "vendedor",pv,  "S"),
        (6,"financeiro","fin123",    "Usuario Financeiro", "financeiro@mksys.local","vendedor",pf,  "S"),
        (7,"estoque",   "estoque123","Controle Estoque",   "estoque@mksys.local",   "vendedor",pe,  "S"),
    ]
    for uid,login,senha,nome,email,perfil,perms,trocar in usuarios:
        cur.execute("""INSERT INTO USUARIOS
            (ID,LOGIN,SENHA_HASH,NOME,EMAIL,PERFIL,ATIVO,PERMISSOES,TROCAR_SENHA,DATA_CADASTRO)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (uid,login,h256(senha),nome,email,perfil,"S",perms,trocar,NOW))
    conn.commit()
    print(f"  {len(usuarios)} usuarios inseridos")
    print()
    print("  Logins:")
    for _,login,senha,_,_,perfil,_,_ in usuarios:
        print(f"    {login:12} / {senha:12}  [{perfil}]")
conn.close()

print("\n" + "="*50)
print("  PRONTO! Todos os bancos populados.")
print("  Login admin: admin / admin123")
print("="*50 + "\n")
