def update_produto(conexao, cursor, obj_produto):

    sql = """
    UPDATE produto 
    SET ds_produto = ?, 
        id_produto_categoria = ?, 
        id_unidade_medida = ?, 
        vl_estoque = ?, 
        vl_custo = ?, 
        vl_valor = ?
    WHERE ds_produto = '?'
    """
    valores = (
        obj_produto.ds_produto,
        obj_produto.id_produto_categoria,
        obj_produto.id_unidade_medida,
        obj_produto.vl_estoque,
        obj_produto.vl_custo,
        obj_produto.vl_valor,
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
    WHERE ds_cliente = '?'
    """
    valores = (
        obj_cliente.ds_cliente,
        obj_cliente.ds_telefone,
        obj_cliente.ds_endereco,
    )
    
    try:
        cursor.execute(sql, valores)
        conexao.commit()
        print("Cliente atualizado com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar cliente: {e}")
        conexao.rollback()