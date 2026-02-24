import os, sys, datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR); sys.path.insert(0, BASE_DIR)
from core.database import get_connection

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Apenas colunas garantidas pelo init_db original
clientes = [
    # ID, NOME, CPF, NASC, RUA, NUM, COMPL, BAIRRO, CIDADE, ESTADO, CEP, TELEFONE, OBS
    (1,"Ana Paula Ferreira",     "52998224725","1990-03-15","Rua das Flores",       "123","Apto 4", "Jardim America",  "Sao Paulo",      "SP","01310100","1132550001","Cliente desde 2021"),
    (2,"Bruno Henrique Souza",   "89706419671","1985-07-22","Av. Paulista",          "900","",       "Bela Vista",      "Sao Paulo",      "SP","01310200","1132550002","Pedidos frequentes"),
    (3,"Carla Mendes Oliveira",  "10120230304","1993-11-08","Rua XV de Novembro",   "45", "Sala 2", "Centro",          "Curitiba",       "PR","80020310","4132550003",""),
    (4,"Daniel Costa Lima",      "22233344455","1978-05-30","Rua Sete de Setembro", "200","",       "Centro",          "Rio de Janeiro", "RJ","20050006","2132550004","Preferencia boleto"),
    (5,"Eduarda Santos Ribeiro", "33344455566","1995-09-14","Rua das Acacias",      "78", "Casa",   "Bairro Novo",     "Belo Horizonte", "MG","30130110","3132550005",""),
    (6,"Felipe Alves Martins",   "44455566677","1982-01-25","Av. Brasil",           "1500","Apto 12","Tambore",        "Barueri",        "SP","06460030","1132550006","Cliente VIP"),
    (7,"Gabriela Nunes Pereira", "55566677788","1999-06-03","Rua Marechal Deodoro", "33", "",       "Centro",          "Florianopolis",  "SC","88010060","4832550007",""),
]

with get_connection("clientes_pf") as conn:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM CLIENTES_PF")
    count = list(cur.fetchone().values())[0]
    if count > 0:
        print(f"Clientes PF ja tem {count} registro(s). Seed ignorado.")
    else:
        for row in clientes:
            uid,nome,cpf,nasc,rua,num,compl,bairro,cidade,estado,cep,tel,obs = row
            cur.execute("""INSERT INTO CLIENTES_PF
                (ID,NOME,CPF,DATA_NASCIMENTO,RUA,NUMERO,COMPLEMENTO,
                 BAIRRO,CIDADE,ESTADO,CEP,TELEFONE,DATA_CADASTRO,OBSERVACOES)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (uid,nome,cpf,nasc,rua,num,compl,bairro,cidade,estado,cep,tel,now,obs))
        conn.commit()
        print(f"Inseridos {len(clientes)} clientes PF!")
