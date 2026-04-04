def delete_produto(conexao, cursor, ds_produto):
    sql = "DELETE FROM produto WHERE ds_produto = ?"
    
    try:
        cursor.execute(sql, (ds_produto,))
        conexao.commit()
        print("Produto excluído com sucesso!")
    except Exception as e:
        print(f"Erro ao excluir produto: {e}")
        conexao.rollback()