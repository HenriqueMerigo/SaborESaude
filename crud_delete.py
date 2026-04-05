def delete_produto(conexao, cursor, ds_produto):
    sql = "DELETE FROM produto WHERE ds_produto = ?"
    
    try:
        cursor.execute(sql, (ds_produto,))
        conexao.commit()
        print("Produto excluído com sucesso!")
    except Exception as e:
        print(f"Erro ao excluir produto: {e}")
        conexao.rollback()

def delete_cliente(conexao, cursor, ds_cliente):
    sql = "DELETE FROM cliente WHERE ds_cliente = ?"
    
    try:
        cursor.execute(sql, (ds_cliente,))
        conexao.commit()
        print("Cliente excluído com sucesso!")
    except Exception as e:
        print(f"Erro ao excluir cliente: {e}")
        conexao.rollback()

def delete_pedido(conexao, cursor, id_pedido):
    sql = "DELETE FROM pedido_produto WHERE id_pedido = ?"
    
    try:
        cursor.execute(sql, (id_pedido,))
        conexao.commit()
        print("Pedido excluído com sucesso!")
    except Exception as e:
        print(f"Erro ao excluir pedido: {e}")
        conexao.rollback()