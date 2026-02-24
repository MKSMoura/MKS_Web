import os, sys, datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR); sys.path.insert(0, BASE_DIR)
from core.database import get_connection

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

pedidos = [
    # ID,NUMERO,DATA,HORA,STATUS,COD_VEND,NOME_VEND,COD_CLI,NOME_CLI,CPF_CNPJ,DESC,ACRE,FORMA,OBS
    (1,"PED260200001","2026-01-05","09:15:00","faturado", "VND001","Carlos Vendedor",1,"Ana Paula Ferreira",     "52998224725", 0,   0,  "PIX",           "Entrega rapida"),
    (2,"PED260200002","2026-01-12","10:30:00","faturado", "VND001","Carlos Vendedor",2,"Bruno Henrique Souza",   "89706419671", 15,  0,  "Cartao Debito", ""),
    (3,"PED260200003","2026-01-20","14:00:00","cancelado","VND002","Julia Vendedora", 3,"Carla Mendes Oliveira",  "10120230304", 0,   0,  "Dinheiro",      "Cancelado pelo cliente"),
    (4,"PED260200004","2026-02-03","08:45:00","faturado", "VND002","Julia Vendedora", 1,"Supermercados Horizonte","11222333000181",50, 0, "Boleto",        "Pedido grande"),
    (5,"PED260200005","2026-02-10","11:00:00","faturado", "VND001","Carlos Vendedor",5,"Eduarda Santos Ribeiro", "33344455566", 0,   5,  "PIX",           "Frete incluido"),
    (6,"PED260200006","2026-02-18","15:30:00","aberto",   "VND003","Marcos Vendedor", 6,"TechSoft Solucoes",      "66777888000186",0,  0, "A prazo",       "Aguardando aprovacao"),
    (7,"PED260200007","2026-02-23","09:00:00","aberto",   "VND001","Carlos Vendedor",7,"Gabriela Nunes Pereira", "55566677788", 0,   0,  "Cartao Credito",""),
]

itens = {
    1: [("ALI-001","Arroz Branco Tipo 1 5kg",  5,  "SC",18.90),
        ("ALI-008","Leite Integral UHT 1L",    24, "LT", 4.90)],
    2: [("BEB-001","Refrigerante Cola 2L",     12, "UN",12.90),
        ("FRI-002","Batata Chips 150g",         10, "PC", 9.90)],
    3: [("HIG-001","Papel Higienico 12 rolos",  6, "PC",16.90)],
    4: [("ALI-001","Arroz Branco Tipo 1 5kg",  50, "SC",18.90),
        ("ALI-002","Feijao Carioca 1kg",        30, "PC", 9.50),
        ("ALI-005","Oleo de Soja 900ml",        24, "UN", 7.80)],
    5: [("PET-001","Racao Cao Adulto 15kg",      3, "SC",99.90),
        ("PET-003","Areia para Gatos 4kg",       5, "PC",25.90)],
    6: [("LIM-003","Sabao em Po 1kg",           20, "PC",15.90),
        ("LIM-001","Detergente Liquido 500ml",  30, "UN", 4.20)],
    7: [("HIG-003","Shampoo 400ml",              4, "UN",19.90),
        ("HIG-004","Creme Dental 90g",           6, "UN", 6.90),
        ("HIG-005","Desodorante Aerosol 150ml",  4, "UN",14.90)],
}

with get_connection("pedidos") as conn:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM PEDIDOS")
    count = list(cur.fetchone().values())[0]
    if count > 0:
        print(f"Pedidos ja tem {count} registro(s). Seed ignorado.")
    else:
        item_id = 1
        for row in pedidos:
            uid,numero,data,hora,status,cod_v,nome_v,cod_c,nome_c,doc,desc,acre,forma,obs = row
            lista = itens.get(uid,[])
            subtotal = round(sum(q*vu for _,_,q,_,vu in lista), 2)
            total    = round(subtotal - desc + acre, 2)
            log      = f"[{data} {hora}] Criado por admin"
            cur.execute("""INSERT INTO PEDIDOS
                (ID,NUMERO,DATA_PEDIDO,HORA_PEDIDO,STATUS,
                 COD_VENDEDOR,NOME_VENDEDOR,COD_CLIENTE,NOME_CLIENTE,CPF_CNPJ,
                 SUBTOTAL,DESCONTO,ACRESCIMO,TOTAL,FORMA_PAGAMENTO,OBSERVACOES,
                 USUARIO_CRIOU,DATA_CRIACAO,DATA_ATUALIZACAO,LOG_ALTERACOES)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (uid,numero,data,hora,status,cod_v,nome_v,cod_c,nome_c,doc,
                 subtotal,float(desc),float(acre),total,forma,obs,
                 "admin",now,now,log))
            for sku,nome_p,qtd,un,vu in lista:
                cur.execute("""INSERT INTO PEDIDO_ITENS
                    (ID,PEDIDO_ID,SKU,NOME_PRODUTO,QUANTIDADE,UNIDADE,VALOR_UNITARIO,VALOR_TOTAL)
                    VALUES (?,?,?,?,?,?,?,?)""",
                    (item_id,uid,sku,nome_p,float(qtd),un,vu,round(qtd*vu,2)))
                item_id += 1
        conn.commit()
        print(f"Inseridos {len(pedidos)} pedidos com itens!")
