def update_produto(conexao, cursor, obj_produto):
    # 1. Removi as aspas do primeiro ?
    # 2. Mantive o WHERE id_produto = ?
    sql = """
    UPDATE produto 
    SET ds_produto = ?, 
        id_produto_categoria = ?, 
        id_unidade_medida = ?, 
        vl_estoque = ?, 
        vl_custo = ?, 
        vl_valor = ?
    WHERE id_produto = ?
    """
    
    # 3. Adicionei o obj_produto.id_produto ao final da tupla!
    valores = (
        obj_produto.ds_produto,
        obj_produto.id_produto_categoria,
        obj_produto.id_unidade_medida,
        obj_produto.vl_estoque,
        obj_produto.vl_custo,
        obj_produto.vl_valor,
        obj_produto.id_produto  # <--- ESSA LINHA É VITAL
    )
    
    try:
        cursor.execute(sql, valores)
        conexao.commit()
        print("Produto atualizado com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar produto: {e}")
        conexao.rollback()

def update_cliente(conexao, cursor, obj_cliente):

    sql = """
    UPDATE cliente 
    SET ds_cliente = ?, 
        ds_telefone = ?, 
        ds_endereco = ?, 
        dh_alteracao = CURRENT_TIMESTAMP
    WHERE id_cliente = ?
    """
    valores = (
        obj_cliente.ds_cliente,
        obj_cliente.ds_telefone,
        obj_cliente.ds_endereco,
        obj_cliente.id_cliente  # <--- ID do cliente para o WHERE
    )
    
    try:
        cursor.execute(sql, valores)
        conexao.commit()
        print("Cliente atualizado com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar cliente: {e}")
        conexao.rollback()