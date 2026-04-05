import streamlit as st
import pandas as pd
import sqlite3
from database import conecta_db

# Importações do CRUD (Assumindo que seguem o padrão dos outros módulos)
from crud_create import insert_pedido, insert_pedido_produto
from crud_delete import delete_pedido
from crud import pedido, pedido_produto

def main():
    # Inicialização de estados
    if 'mostrar_formulario_pedido' not in st.session_state:
        st.session_state.mostrar_formulario_pedido = False
    if 'modo_pedido' not in st.session_state:
        st.session_state.modo_pedido = None
    if 'carrinho' not in st.session_state:
        st.session_state.carrinho = [] # Lista de dicionários com os produtos do pedido atual

    # --- CABEÇALHO ---
    col_titulo, col_voltar = st.columns([4, 2], vertical_alignment="bottom")
    with col_titulo:
        st.title("📦 Gestão de Pedidos")
    with col_voltar:
        if st.button('🔙 Voltar ao Menu', use_container_width=True):
            st.switch_page("app.py")
    
    st.divider()

    # --- BUSCA E LISTAGEM ---
    df_pedidos = pd.DataFrame()
    try:
        with sqlite3.connect('prd_saboresaude.db') as conn:
            c_busca, _ = st.columns([2, 1])
            with c_busca:
                busca = st.text_input("Filtrar por Cliente ou ID", placeholder="Pesquisar...", label_visibility="collapsed")
            
            query = f"""
            SELECT 
                p.id_pedido AS 'ID',
                c.ds_cliente AS 'Cliente',
                ps.ds_status AS 'Status',
                fp.ds_forma_pagamento AS 'Pagamento',
                p.vl_valor_total AS 'Total (R$)',
                p.vl_desconto AS 'Desconto (R$)',
                p.dh_inclusao AS 'Data'
            FROM pedido p
            LEFT JOIN cliente c ON p.id_cliente = c.id_cliente
            LEFT JOIN pedido_status ps ON p.id_pedido_status = ps.id_pedido_status
            LEFT JOIN forma_pagamento fp ON p.id_forma_pagamento = fp.id_forma_pagamento
            WHERE c.ds_cliente LIKE '%{busca}%' OR p.id_pedido LIKE '%{busca}%'
            ORDER BY p.id_pedido DESC
            """
            df_pedidos = pd.read_sql_query(query, conn)

        if not df_pedidos.empty:
            contagem_status = df_pedidos['Status'].value_counts()
            total_vendas = df_pedidos['Total (R$)'].sum()
            
            cols = st.columns(2 + len(contagem_status))
            cols[0].metric("Qtd Pedidos", len(df_pedidos))
            cols[1].metric("Valor Total", f"R$ {total_vendas:,.2f}")
            for i, (status_nome, total) in enumerate(contagem_status.items()):
                cols[i + 2].metric(status_nome, total)
            
            st.write("")
            st.dataframe(df_pedidos, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum pedido registrado.")

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")

    # --- BOTÕES DE AÇÃO ---
    st.write("")
    c1, c2, c3 = st.columns(3)

    if c1.button("➕ Novo Pedido", use_container_width=True, type="secondary"):
        st.session_state.mostrar_formulario_pedido = True
        st.session_state.modo_pedido = 'inserir'
        st.session_state.carrinho = [] # Limpa o carrinho para um novo pedido
        st.rerun()
        
    if c2.button("🔍 Detalhar Itens", use_container_width=True):
        st.session_state.modo_pedido = 'detalhar'
        st.rerun()

    if c3.button("🗑️ Cancelar Pedido", use_container_width=True):
        st.session_state.modo_pedido = 'pre-excluir'
        st.rerun()

    # --- FORMULÁRIO DE NOVO PEDIDO (CARRINHO) ---
    if st.session_state.mostrar_formulario_pedido:
        st.divider()
        st.subheader("🛒 Registrar Nova Venda")
        
        conn, cursor = conecta_db()
        clientes = cursor.execute("SELECT id_cliente, ds_cliente FROM cliente").fetchall()
        produtos = cursor.execute("SELECT id_produto, ds_produto, vl_valor FROM produto").fetchall()
        formas_pagto = cursor.execute("SELECT id_forma_pagamento, ds_forma_pagamento FROM forma_pagamento").fetchall()
        status_lista = cursor.execute("SELECT id_pedido_status, ds_status FROM pedido_status").fetchall()
        conn.close()

        with st.expander("1. Dados do Cliente e Pagamento", expanded=True):
            col_cli, col_pag, col_stat = st.columns(3)
            with col_cli:
                sel_cliente = st.selectbox("Cliente", options=clientes, format_func=lambda x: x[1])
            with col_pag:
                sel_pagto = st.selectbox("Forma de Pagamento", options=formas_pagto, format_func=lambda x: x[1])
            with col_stat:
                sel_status = st.selectbox("Status Inicial", options=status_lista, format_func=lambda x: x[1])

        with st.expander("2. Adicionar Produtos ao Pedido", expanded=True):
            col_prod, col_qtd, col_add = st.columns([3, 1, 1], vertical_alignment="bottom")
            with col_prod:
                sel_prod = st.selectbox("Selecione o Produto", options=produtos, format_func=lambda x: f"{x[1]} - R$ {x[2]:.2f}")
            with col_qtd:
                qtd = st.number_input("Quantidade", min_value=1, value=1)
            with col_add:
                if st.button("Adicionar", use_container_width=True):
                    item = {
                        "id_produto": sel_prod[0],
                        "nome": sel_prod[1],
                        "qtd": qtd,
                        "preco": sel_prod[2],
                        "subtotal": qtd * sel_prod[2]
                    }
                    st.session_state.carrinho.append(item)
                    st.toast(f"{sel_prod[1]} adicionado!")

            if st.session_state.carrinho:
                df_cart = pd.DataFrame(st.session_state.carrinho)
                st.table(df_cart[['nome', 'qtd', 'preco', 'subtotal']])
                total_pedido = df_cart['subtotal'].sum()
                st.write(f"### Total do Pedido: R$ {total_pedido:.2f}")

        col_acao1, col_acao2 = st.columns(2)
        with col_acao1:
            if st.button("💾 Finalizar e Gravar Pedido", type="primary", use_container_width=True):
                if not st.session_state.carrinho:
                    st.error("Adicione pelo menos um produto!")
                else:
                    try:
                        conn, cursor = conecta_db()
                        # 1. Criar objeto Pedido (Cabeçalho)
                        total_pedido = sum(item['subtotal'] for item in st.session_state.carrinho)
                        obj_p = pedido(
                            id_pedido=None,
                            id_cliente=sel_cliente[0],
                            id_pedido_status=sel_status[0],
                            id_forma_pagamento=sel_pagto[0],
                            vl_valor_total=total_pedido,
                            vl_desconto=0.0
                        )
                        # 2. Inserir Pedido e pegar ID gerado
                        id_gerado = insert_pedido(obj_pedido=obj_p, conexao=conn, cursor=cursor)
                        
                        # 3. Inserir Itens do Pedido
                        for item in st.session_state.carrinho:
                            obj_item = pedido_produto(
                                id_pedido_produto=None,
                                id_pedido=id_gerado,
                                id_produto=item['id_produto'],
                                vl_quantidade=item['qtd'],
                                vl_unitario=item['preco'],
                                vl_total=item['subtotal']
                            )
                            insert_pedido_produto(obj_ped_prod=obj_item, conexao=conn, cursor=cursor)
                        
                        conn.close()
                        st.success(f"Pedido #{id_gerado} realizado com sucesso!")
                        st.session_state.mostrar_formulario_pedido = False
                        st.session_state.carrinho = []
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao gravar pedido: {e}")

        with col_acao2:
            if st.button("❌ Cancelar Cadastro", use_container_width=True):
                st.session_state.mostrar_formulario_pedido = False
                st.session_state.carrinho = []
                st.rerun()

    # --- LÓGICA DE DETALHES E EXCLUSÃO (CHAMANDO CRUD) ---
    if st.session_state.modo_pedido == 'detalhar':
        with st.expander("🔍 Consultar Itens", expanded=True):
            ids_pedidos = df_pedidos['ID'].tolist()
            p_id = st.selectbox("ID do Pedido:", options=ids_pedidos)
            if st.button("Ver Itens"):
                with sqlite3.connect('prd_saboresaude.db') as conn:
                    query_it = f"SELECT pr.ds_produto, pp.vl_quantidade, pp.vl_total FROM pedido_produto pp JOIN produto pr ON pp.id_produto = pr.id_produto WHERE pp.id_pedido = {p_id}"
                    st.table(pd.read_sql_query(query_it, conn))
            if st.button("Fechar"):
                st.session_state.modo_pedido = None
                st.rerun()

    elif st.session_state.modo_pedido == 'pre-excluir':
        with st.status("Confirmar exclusão definitiva", expanded=True):
            id_del = st.number_input("ID do Pedido para apagar:", min_value=1)
            if st.button("Confirmar Exclusão", type="primary"):
                try:
                    conn, cursor = conecta_db()
                    delete_pedido(conexao=conn, cursor=cursor, id_pedido=id_del)
                    conn.close()
                    st.toast(f"Pedido {id_del} removido!", icon="✅")
                    st.session_state.modo_pedido = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao excluir: {e}")

if __name__ == "__main__":
    main()