def insert_cliente(conexao, cursor, obj_cliente):
    sql = """
    INSERT INTO cliente (ds_cliente, id_cliente_categoria, ds_telefone, ds_endereco, dh_inclusao, dh_alteracao) VALUES (?, ?, ?, ?, ?, ?)
    """
    valores = (
        obj_cliente.ds_cliente,
        obj_cliente.id_cliente_categoria,
        obj_cliente.ds_telefone,
        obj_cliente.ds_endereco,
        obj_cliente.dh_inclusao,
        obj_cliente.dh_alteracao
    )
    try:
        cursor.execute(sql, valores)
        conexao.commit()
        print("Dados salvos com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        conexao.rollback()

def insert_pedido_status(conexao, cursor, obj_pedido_status):
    sql = """
    INSERT INTO pedido_status (ds_pedido_status) VALUES (?)
    """
    valores = (
        obj_pedido_status.ds_pedido_status,
    )
    try:
        cursor.execute(sql, valores)
        conexao.commit()
        print("Dados salvos com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        conexao.rollback()

def insert_pedido(conexao, cursor, obj_pedido):
    sql = """
    INSERT INTO pedido (id_cliente, id_pedido_status, id_forma_pagamento, vl_valor_total, vl_desconto, dh_inclusao, dh_alteracao) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    valores = (
        obj_pedido.id_cliente,
        obj_pedido.id_pedido_status,
        obj_pedido.id_forma_pagamento,
        obj_pedido.vl_valor_total,
        obj_pedido.vl_desconto,
        obj_pedido.dh_inclusao,
        obj_pedido.dh_alteracao
    )
    try:
        cursor.execute(sql, valores)
        conexao.commit()
        print("Dados salvos com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        conexao.rollback()

def insert_produto_categoria(conexao, cursor, obj_produto_categoria):
    sql = """
    INSERT INTO produto_categoria (ds_produto_categoria, dh_inclusao, dh_alteracao) VALUES (?, ?, ?)
    """
    valores = (
        obj_produto_categoria.ds_produto_categoria,
        obj_produto_categoria.dh_inclusao,
        obj_produto_categoria.dh_alteracao
    )
    try:
        cursor.execute(sql, valores)
        conexao.commit()
        print("Dados salvos com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        conexao.rollback()

def insert_produto(conexao, cursor, obj_produto):
    sql = """
    INSERT INTO produto (ds_produto, id_produto_categoria, id_unidade_medida, vl_estoque, vl_custo, vl_valor, dh_inclusao, dh_alteracao) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    valores = (
        obj_produto.ds_produto,
        obj_produto.id_produto_categoria,
        obj_produto.id_unidade_medida,
        obj_produto.vl_estoque,
        obj_produto.vl_custo,
        obj_produto.vl_valor,
        obj_produto.dh_inclusao,
        obj_produto.dh_alteracao
    )
    try:
        cursor.execute(sql, valores)
        conexao.commit()
        print("Dados salvos com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        conexao.rollback()

def insert_pedido_produto(conexao, cursor, obj_pedido_produto):
    
    sql = """
    INSERT INTO pedido_produto (id_pedido, id_produto, vl_quantidade, vl_unitario, vl_total, dh_inclusao, dh_alteracao) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    valores = (
        obj_pedido_produto.id_pedido,
        obj_pedido_produto.id_produto,
        obj_pedido_produto.vl_quantidade,
        obj_pedido_produto.vl_unitario,
        obj_pedido_produto.vl_total,
        obj_pedido_produto.dh_inclusao,
        obj_pedido_produto.dh_alteracao
    )
    try:
        cursor.execute(sql, valores)
        conexao.commit()
        print("Dados salvos com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        conexao.rollback()