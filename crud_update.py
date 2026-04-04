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