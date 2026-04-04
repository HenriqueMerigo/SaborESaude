from database import conecta_db
from datetime import datetime


import os

def localiza_tabela(tabela):
    tabelas_validas = [
        'cliente_categoria', 'cliente', 'forma_pagamento', 
        'pedido_status', 'pedido', 'produto_categoria', 
        'unidade_medida', 'produto', 'pedido_produto'
    ]
    
    if tabela in tabelas_validas:
        print(f"Você escolheu a tabela {tabela}.")
        return tabela
    else:
        print("Opção inválida.")
        return None

class BaseTabela:
    def __init__(self):
        self.dh_inclusao = datetime.now()
        self.dh_alteracao = datetime.now()
class cliente(BaseTabela):
    def __init__(self, id_cliente, ds_cliente, id_cliente_categoria, ds_telefone, ds_endereco):
        super().__init__()  
        self.id_cliente = id_cliente
        self.ds_cliente = ds_cliente
        self.id_cliente_categoria = id_cliente_categoria
        self.ds_telefone = ds_telefone
        self.ds_endereco = ds_endereco
class pedido_status(BaseTabela):
    def __init__(self, id_pedido_status, ds_pedido_status):
        super().__init__()
        self.id_pedido_status = id_pedido_status
        self.ds_pedido_status = ds_pedido_status
class pedido(BaseTabela):
    def __init__(self, id_pedido, id_cliente, id_pedido_status, id_forma_pagamento, vl_valor_total, vl_desconto):
        super().__init__()
        self.id_pedido = id_pedido
        self.id_cliente = id_cliente
        self.id_pedido_status = id_pedido_status
        self.id_forma_pagamento = id_forma_pagamento
        self.vl_valor_total = vl_valor_total
        self.vl_desconto = vl_desconto
class produto_categoria(BaseTabela):
    def __init__(self, id_produto_categoria, ds_produto_categoria):
        super().__init__()
        self.id_produto_categoria = id_produto_categoria
        self.ds_produto_categoria = ds_produto_categoria
class produto(BaseTabela):
    def __init__(self, id_produto, ds_produto, id_produto_categoria, id_unidade_medida, vl_estoque, vl_custo, vl_valor):
        super().__init__()
        self.id_produto = id_produto

        self.ds_produto = ds_produto

        self.id_produto_categoria = id_produto_categoria
        self.id_unidade_medida = id_unidade_medida
        self.vl_estoque = vl_estoque
        self.vl_custo = vl_custo
        self.vl_valor = vl_valor
class pedido_produto(BaseTabela):
    def __init__(self, id_pedido_produto, id_pedido, id_produto, vl_quantidade, vl_unitario, vl_total):
        super().__init__()
        self.id_pedido_produto = id_pedido_produto
        self.id_pedido = id_pedido
        self.id_produto = id_produto
        self.vl_quantidade = vl_quantidade
        self.vl_unitario = vl_unitario
        self.vl_total = vl_total


def __main__():
    conexao, cursor = conecta_db()
    tabela = input("Digite o nome da tabela que deseja acessar: ")
    localiza_tabela(tabela)
    

if __name__ == "__main__":
    os.system('cls')
    __main__()