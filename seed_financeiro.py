import os, sys, datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR); sys.path.insert(0, BASE_DIR)
from core.database import get_connection

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

receber = [
    # ID,DESC,CLI_ID,NOME_CLI,PED_ID,NUM_PED,VALOR,PAGO,EMIS,VENC,PGTO,STATUS,FORMA
    (1,"Pedido PED260200001 - Ana Paula",    1,"Ana Paula Ferreira",     1,"PED260200001",136.30,136.30,"2026-01-05","2026-01-12","2026-01-10","recebido","PIX"),
    (2,"Pedido PED260200002 - Bruno Souza",  2,"Bruno Henrique Souza",   2,"PED260200002",228.80,228.80,"2026-01-12","2026-01-19","2026-01-18","recebido","Cartao Debito"),
    (3,"Pedido PED260200004 - Horizonte",    1,"Supermercados Horizonte", 4,"PED260200004",1111.50,1111.50,"2026-02-03","2026-02-17","2026-02-15","recebido","Boleto"),
    (4,"Pedido PED260200005 - Eduarda",      5,"Eduarda Santos Ribeiro", 5,"PED260200005",434.20,434.20,"2026-02-10","2026-02-17","2026-02-16","recebido","PIX"),
    (5,"Pedido PED260200006 - TechSoft",     6,"TechSoft Solucoes",      6,"PED260200006",444.00,0,    "2026-02-18","2026-03-18",None,       "aberto",  "A prazo"),
    (6,"Pedido PED260200007 - Gabriela",     7,"Gabriela Nunes Pereira", 7,"PED260200007",207.10,0,    "2026-02-23","2026-03-02",None,       "aberto",  "Cartao Credito"),
    (7,"Mensalidade Servico Premium Jan",   None,"—",                  None,None,         350.00,350.00,"2026-01-01","2026-01-10","2026-01-08","recebido","PIX"),
]

pagar = [
    # ID,DESC,FORN_ID,NOME_FORN,CAT,VALOR,PAGO,EMIS,VENC,PGTO,STATUS,FORMA
    (1,"NF 12345 - Arroz e Feijao - Camil",  1,"Camil Alimentos",   "Fornecedores",2350.00,2350.00,"2026-01-03","2026-02-02","2026-02-01","pago",  "Boleto"),
    (2,"NF 23456 - Oleo Soja - Bunge",       2,"Bunge Alimentos",   "Fornecedores",1176.00,1176.00,"2026-01-10","2026-02-09","2026-02-08","pago",  "Transferencia"),
    (3,"NF 34567 - Bebidas - Ambev",         3,"Ambev",             "Fornecedores",3120.00,0,      "2026-02-01","2026-03-03",None,       "aberto","Boleto"),
    (4,"Aluguel Galpao Fevereiro",          None,"Imob. Paulista",   "Aluguel",     4500.00,4500.00,"2026-02-01","2026-02-10","2026-02-10","pago",  "Transferencia"),
    (5,"Folha de Pagamento Fevereiro",      None,"—",               "Salarios",    8200.00,8200.00,"2026-02-25","2026-02-28","2026-02-28","pago",  "Transferencia"),
    (6,"NF 45678 - Higiene - Unilever",      4,"Unilever",          "Fornecedores",1890.00,0,      "2026-02-15","2026-03-17",None,       "aberto","Boleto"),
    (7,"Energia Eletrica Fevereiro",        None,"Enel",            "Utilidades",   620.00,0,      "2026-02-20","2026-03-10",None,       "aberto","Debito Automatico"),
]

with get_connection("financeiro") as conn:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM CONTAS_RECEBER")
    cr = list(cur.fetchone().values())[0]
    cur.execute("SELECT COUNT(*) FROM CONTAS_PAGAR")
    cp = list(cur.fetchone().values())[0]
    if cr > 0 or cp > 0:
        print(f"Financeiro ja tem dados (CR:{cr} CP:{cp}). Seed ignorado.")
    else:
        for row in receber:
            uid,desc,cli_id,nome_cli,ped_id,num_ped,valor,pago,emis,venc,pgto,status,forma = row
            cur.execute("""INSERT INTO CONTAS_RECEBER
                (ID,DESCRICAO,CLIENTE_ID,NOME_CLIENTE,PEDIDO_ID,NUMERO_PEDIDO,
                 VALOR,VALOR_PAGO,DATA_EMISSAO,DATA_VENCIMENTO,DATA_PAGAMENTO,
                 STATUS,FORMA_PAGAMENTO,USUARIO_LANCOU,DATA_LANCAMENTO)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (uid,desc,cli_id,nome_cli,ped_id,num_ped,
                 valor,pago,emis,venc,pgto,status,forma,"admin",now))
        for row in pagar:
            uid,desc,fid,nome_f,cat,valor,pago,emis,venc,pgto,status,forma = row
            cur.execute("""INSERT INTO CONTAS_PAGAR
                (ID,DESCRICAO,FORNECEDOR_ID,NOME_FORNECEDOR,CATEGORIA,
                 VALOR,VALOR_PAGO,DATA_EMISSAO,DATA_VENCIMENTO,DATA_PAGAMENTO,
                 STATUS,FORMA_PAGAMENTO,USUARIO_LANCOU,DATA_LANCAMENTO)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (uid,desc,fid,nome_f,cat,
                 valor,pago,emis,venc,pgto,status,forma,"admin",now))
        conn.commit()
        print(f"Inseridos {len(receber)} recebimentos e {len(pagar)} pagamentos!")
