import os, sys, datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR); sys.path.insert(0, BASE_DIR)
from core.database import get_connection

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

fornecedores = [
    # ID,RAZAO,FANTASIA,CNPJ,EMAIL,TEL,CONTATO,CEP,RUA,NUM,BAIRRO,CIDADE,ESTADO,BANCO,PIX,PRAZO,CAT
    (1,"Camil Alimentos S.A.",       "Camil",       "11111111000191","vendas@camil.com.br",    "1130001001","Joao Camil",   "09930460","Av. das Nacoes Unidas","12901","Brooklin",        "Sao Paulo","SP","Bradesco","vendas@camil.com.br",     30,"Alimentos"),
    (2,"Bunge Alimentos S.A.",       "Bunge",       "22222222000192","sac@bunge.com.br",        "1530001002","Maria Bunge",  "13062610","Rua Min. Joao Inverse","800",  "Chacara Primavera","Campinas", "SP","Itau",    "sac@bunge.com.br",        28,"Alimentos"),
    (3,"Ambev S.A.",                 "Ambev",       "33333333000193","ambev@ambev.com.br",      "1130001003","Pedro Ambev",  "05427070","Rua Dr. Renato Paes",  "1017","Pinheiros",       "Sao Paulo","SP","Bradesco","pix@ambev.com.br",         21,"Bebidas"),
    (4,"Unilever Brasil Ltda",       "Unilever",    "44444444000194","trade@unilever.com",      "1130001004","Sandra Uni",   "04749000","Av. Jabaquara",        "3467","Mirandopolis",    "Sao Paulo","SP","Santander","trade@unilever.com",       30,"Higiene"),
    (5,"Nestle Brasil Ltda",         "Nestle",      "55555555000195","nestle@nestle.com.br",    "1130001005","Carlos Nestle","04795100","Av. das Nacoes Unidas","12995","Brooklin Novo",   "Sao Paulo","SP","Itau",    "nestle@nestle.com.br",     30,"Alimentos"),
    (6,"Mars Petcare Brasil Ltda",   "Mars Petcare","66666666000196","petcare@mars.com",        "1130001006","Laura Mars",   "06454000","Av. Dr. Chucri Zaidan","920",  "Vila Cordeiro",   "Sao Paulo","SP","Bradesco","petcare@mars.com",         45,"Pet"),
    (7,"PepsiCo do Brasil Ltda",     "PepsiCo",     "77777777000197","pepsico@pepsico.com",     "1130001007","Andre Pepsi",  "06010903","Av. das Nacoes Unidas","7221","Pinheiros",       "Sao Paulo","SP","Santander","pepsico@pepsico.com",      30,"Bebidas"),
]

with get_connection("fornecedores") as conn:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM FORNECEDORES")
    count = list(cur.fetchone().values())[0]
    if count > 0:
        print(f"Fornecedores ja tem {count} registro(s). Seed ignorado.")
    else:
        for row in fornecedores:
            uid,razao,fantasia,cnpj,email,tel,contato,cep,rua,num,bairro,cidade,estado,banco,pix,prazo,cat = row
            cur.execute("""INSERT INTO FORNECEDORES
                (ID,TIPO,RAZAO_SOCIAL,NOME_FANTASIA,CNPJ,EMAIL,TELEFONE,CONTATO_NOME,
                 CEP,RUA,NUMERO,BAIRRO,CIDADE,ESTADO,BANCO,PIX,
                 PRAZO_PAGAMENTO,CATEGORIA,STATUS,DATA_CADASTRO,DATA_ATUALIZACAO)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (uid,"PJ",razao,fantasia,cnpj,email,tel,contato,
                 cep,rua,num,bairro,cidade,estado,banco,pix,
                 prazo,cat,"ativo",now,now))
        conn.commit()
        print(f"Inseridos {len(fornecedores)} fornecedores!")
