import os, sys, datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR); sys.path.insert(0, BASE_DIR)
from core.database import get_connection

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

clientes = [
    # ID, CNPJ, IE, RAZAO, FANTASIA, TEL, CEP, RUA, NUM, COMPL, BAIRRO, CIDADE, ESTADO,
    #     CPF_RESP, NOME_RESP, TEL_RESP, OBS
    (1,"11222333000181","111222333444","Supermercados Horizonte Ltda","Hiper Horizonte",
       "1133001100","01310001","Av. Paulista","1000","Loja 1","Bela Vista","Sao Paulo","SP",
       "12345678901","Marcos Horizonte","11991000001","Rede com 3 filiais"),
    (2,"22333444000182","222333444555","Distribuidora Norte Sul S.A.","Norte Sul Dist.",
       "2133001200","20040020","Rua da Alfandega","50","","Centro","Rio de Janeiro","RJ",
       "23456789012","Fernanda Norte","21991000002","Grande volume"),
    (3,"33444555000183","333444555666","Papelaria Central Eireli","Papel e Cia",
       "4133001300","80010000","Rua XV de Novembro","200","Sala 3","Centro","Curitiba","PR",
       "34567890123","Roberto Central","41991000003",""),
    (4,"44555666000184","444555666777","Farmacia Bem Estar ME","Bem Estar",
       "3133001400","30130010","Av. Afonso Pena","800","","Centro","Belo Horizonte","MG",
       "45678901234","Lucia Bem Estar","31991000004","Pedidos mensais"),
    (5,"55666777000185","555666777888","Construtora Alfa Beta Ltda","Alfa Beta Obras",
       "4733001500","89010100","Rua Blumenau","450","","Centro","Joinville","SC",
       "56789012345","Carlos Alfa","47991000005",""),
    (6,"66777888000186","666777888999","TechSoft Solucoes LTDA","TechSoft",
       "5133001600","90010150","Av. Borges de Medeiros","300","Andar 5","Centro Hist.","Porto Alegre","RS",
       "67890123456","Patricia Tech","51991000006","Cliente VIP"),
    (7,"77888999000187","777888999000","Agro Campo Verde Ltda","Campo Verde",
       "6733001700","77001000","Av. Goias","1200","","Setor Central","Goiania","GO",
       "78901234567","Jose Campo","67991000007","Sazonalidade set/out"),
]

with get_connection("clientes_pj") as conn:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM CLIENTES_PJ")
    count = list(cur.fetchone().values())[0]
    if count > 0:
        print(f"Clientes PJ ja tem {count} registro(s). Seed ignorado.")
    else:
        for row in clientes:
            uid,cnpj,ie,razao,fantasia,tel,cep,rua,num,compl,bairro,cidade,estado,cpf_r,nome_r,tel_r,obs = row
            cur.execute("""INSERT INTO CLIENTES_PJ
                (ID,CNPJ,INSCRICAO_ESTADUAL,RAZAO_SOCIAL,NOME_FANTASIA,
                 TELEFONE,CEP,RUA,NUMERO,COMPLEMENTO,BAIRRO,CIDADE,ESTADO,
                 CPF_RESPONSAVEL,NOME_RESPONSAVEL,TELEFONE_RESPONSAVEL,
                 DATA_CADASTRO,OBSERVACOES)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (uid,cnpj,ie,razao,fantasia,tel,cep,rua,num,compl,bairro,cidade,estado,
                 cpf_r,nome_r,tel_r,now,obs))
        conn.commit()
        print(f"Inseridos {len(clientes)} clientes PJ!")
