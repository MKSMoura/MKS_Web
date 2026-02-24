import os, sys, datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR); sys.path.insert(0, BASE_DIR)
from core.database import get_connection

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

produtos = [
    # SKU, COD_BARRAS, NOME, CAT, SUBCAT, MARCA, CUSTO, VENDA, UNID, QTD_EMB, FORN, QTD_EST, EST_MIN, EST_MAX
    ("ALI-001","7891234000001","Arroz Branco Tipo 1 5kg",    "Alimentos","Graos",    "Camil",    14.50,18.90,"SC",1,"Camil Alimentos",  150,20,300),
    ("ALI-002","7891234000002","Feijao Carioca 1kg",         "Alimentos","Graos",    "Camil",     6.20, 9.50,"PC",1,"Camil Alimentos",  200,30,400),
    ("ALI-003","7891234000003","Macarrao Espaguete 500g",    "Alimentos","Massas",   "Barilla",   3.80, 6.90,"PC",1,"Barilla Brasil",   180,30,350),
    ("ALI-004","7891234000004","Molho de Tomate 340g",       "Alimentos","Conservas","Heinz",     2.50, 4.90,"UN",1,"Heinz Brasil",     120,20,250),
    ("ALI-005","7891234000005","Oleo de Soja 900ml",         "Alimentos","Oleos",    "Liza",      4.90, 7.80,"UN",1,"Bunge Alimentos",  100,15,200),
    ("ALI-006","7891234000006","Acucar Cristal 1kg",         "Alimentos","Acucar",   "Uniao",     3.20, 5.50,"PC",1,"Acucar Uniao",     180,25,360),
    ("ALI-007","7891234000007","Sal Refinado 1kg",           "Alimentos","Temperos", "Cisne",     1.40, 2.90,"PC",1,"Cisne",            200,30,400),
    ("ALI-008","7891234000008","Leite Integral UHT 1L",      "Alimentos","Laticinios","Italac",   3.10, 4.90,"LT",12,"Italac",          240,40,500),
    ("ALI-009","7891234000009","Cafe Torrado Moido 500g",    "Alimentos","Cafe",     "Pilao",     9.80,14.90,"PC",1,"Pilao",            100,15,200),
    ("ALI-010","7891234000010","Farinha de Trigo 1kg",       "Alimentos","Farinha",  "Dona Benta",4.20, 6.90,"PC",1,"Moinho Pacifico", 150,20,300),
    ("BEB-001","7891234000011","Refrigerante Cola 2L",       "Bebidas",  "Refrig",   "Coca-Cola", 7.20,12.90,"UN",6,"Ambev",            80, 12,160),
    ("BEB-002","7891234000012","Agua Mineral 500ml",         "Bebidas",  "Agua",     "Crystal",   0.90, 2.50,"UN",12,"Crystal",         200,30,400),
    ("BEB-003","7891234000013","Suco de Laranja 1L",         "Bebidas",  "Sucos",    "Del Valle",  4.50, 7.90,"LT",6,"Coca-Cola",        90, 15,180),
    ("BEB-004","7891234000014","Cerveja Long Neck 355ml",    "Bebidas",  "Cervejas", "Heineken",  4.80, 8.90,"UN",24,"Heineken Brasil",  60, 10,120),
    ("BEB-005","7891234000015","Isotônico 500ml",            "Bebidas",  "Energet",  "Gatorade",  3.60, 6.90,"UN",12,"PepsiCo",          70, 12,140),
    ("HIG-001","7891234000016","Papel Higienico 12 rolos",   "Higiene",  "Papel",    "Neve",      9.80,16.90,"PC",4,"Kimberly Clark",   60, 10,120),
    ("HIG-002","7891234000017","Sabonete Barra 90g",         "Higiene",  "Sabonete", "Dove",      2.10, 4.50,"UN",6,"Unilever",          90, 15,180),
    ("HIG-003","7891234000018","Shampoo 400ml",              "Higiene",  "Cabelos",  "Head Shoulders",8.90,19.90,"UN",1,"Procter",       50,  8,100),
    ("HIG-004","7891234000019","Creme Dental 90g",           "Higiene",  "Dental",   "Colgate",   3.40, 6.90,"UN",12,"Colgate-Palmolive",80,12,160),
    ("HIG-005","7891234000020","Desodorante Aerosol 150ml",  "Higiene",  "Desod",    "Rexona",    8.20,14.90,"UN",1,"Unilever",          60, 10,120),
    ("LIM-001","7891234000021","Detergente Liquido 500ml",   "Limpeza",  "Pratos",   "Ypê",       2.10, 4.20,"UN",24,"Ypê",             100,15,200),
    ("LIM-002","7891234000022","Amaciante 2L",               "Limpeza",  "Roupas",   "Downy",     7.90,13.90,"UN",6,"Procter",           60, 10,120),
    ("LIM-003","7891234000023","Sabao em Po 1kg",            "Limpeza",  "Roupas",   "Ariel",     8.50,15.90,"PC",1,"Procter",           70, 12,140),
    ("LIM-004","7891234000024","Agua Sanitaria 1L",          "Limpeza",  "Desinf",   "Qboa",      2.80, 5.50,"UN",12,"Clorox Brasil",    80, 12,160),
    ("LIM-005","7891234000025","Esponja de Aco 60g",         "Limpeza",  "Utensilios","Bom Bril",  1.80, 3.90,"PC",1,"Bom Bril",        120,20,250),
    ("FRI-001","7891234000026","Salgadinho de Milho 100g",   "Snacks",   "Salgados", "Cheetos",   2.90, 5.90,"PC",1,"PepsiCo",           80, 12,160),
    ("FRI-002","7891234000027","Batata Chips 150g",          "Snacks",   "Salgados", "Ruffles",   5.50, 9.90,"PC",1,"PepsiCo",           70, 10,140),
    ("FRI-003","7891234000028","Biscoito Recheado 140g",     "Snacks",   "Biscoitos","Oreo",       3.20, 6.50,"PC",1,"Mondelez",          90, 15,180),
    ("PET-001","7891234000029","Racao Cao Adulto 15kg",      "Pet",      "Racao",    "Pedigree",  55.00,99.90,"SC",1,"Mars Petcare",      30,  5, 60),
    ("PET-002","7891234000030","Racao Gato Adulto 3kg",      "Pet",      "Racao",    "Whiskas",   18.00,34.90,"PC",1,"Mars Petcare",      40,  6, 80),
    ("PET-003","7891234000031","Areia para Gatos 4kg",       "Pet",      "Higiene",  "Pipicat",   14.00,25.90,"PC",1,"Pipicat",           50,  8,100),
    ("FLV-001","7891234000032","Banana Prata kg",            "FLV",      "Frutas",   "A Granel",   2.50, 4.90,"KG",1,"Ceagesp",          50, 10,100),
    ("FLV-002","7891234000033","Tomate Salada kg",           "FLV",      "Verduras", "A Granel",   4.80, 8.90,"KG",1,"Ceagesp",          30,  5, 60),
    ("FLV-003","7891234000034","Batata Inglesa kg",          "FLV",      "Tuberculos","A Granel",  3.20, 5.90,"KG",1,"Ceagesp",          60, 10,120),
    ("PAD-001","7891234000035","Pao Frances 50g",            "Padaria",  "Paes",     "Padaria Local",0.50, 0.99,"UN",10,"Padaria Local", 200,50,500),
    ("PAD-002","7891234000036","Bolo de Chocolate 500g",     "Padaria",  "Bolos",    "Wickbold",  12.00,22.90,"UN",1,"Wickbold",          20,  4, 40),
    ("AC-001", "7891234000037","Chocolate ao Leite 100g",    "Doces",    "Chocolates","Lacta",     4.50, 8.90,"PC",1,"Mondelez",          80, 12,160),
    ("AC-002", "7891234000038","Sorvete Pote 1.5L",          "Doces",    "Sorvetes", "Kibon",     13.00,24.90,"UN",1,"Unilever",          30,  5, 60),
    ("AC-003", "7891234000039","Geleia de Morango 340g",     "Doces",    "Geleias",  "Queensberry",5.80, 9.90,"UN",1,"Queensberry",       50,  8,100),
    ("CON-001","7891234000040","Atum em Lata 170g",          "Conservas","Peixes",   "Coqueiro",   5.20, 9.50,"UN",12,"Coqueiro",         70, 12,140),
]

with get_connection("produtos") as conn:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM PRODUTOS")
    count = list(cur.fetchone().values())[0]
    if count > 0:
        print(f"Produtos ja tem {count} registro(s). Seed ignorado.")
    else:
        for i, p in enumerate(produtos, 1):
            sku,cb,nome,cat,subcat,marca,custo,venda,unid,emb,forn,est,est_min,est_max = p
            margem = round((venda - custo) / venda * 100, 2) if venda else 0
            cur.execute("""INSERT INTO PRODUTOS
                (ID,SKU,CODIGO_BARRAS,NOME,CATEGORIA,SUBCATEGORIA,MARCA,
                 PRECO_CUSTO,PRECO_VENDA,MARGEM,UNIDADE_MEDIDA,QTD_EMBALAGEM,
                 FORNECEDOR_PRINCIPAL,QTD_ESTOQUE,ESTOQUE_MINIMO,ESTOQUE_MAXIMO,
                 STATUS,PRODUTO_CONTROLADO,PERMITE_DESCONTO,DATA_CADASTRO,DATA_ATUALIZACAO)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (i,sku,cb,nome,cat,subcat,marca,
                 custo,venda,margem,unid,emb,
                 forn,float(est),float(est_min),float(est_max),
                 "ativo","N","S",now,now))
        conn.commit()
        print(f"Inseridos {len(produtos)} produtos!")
