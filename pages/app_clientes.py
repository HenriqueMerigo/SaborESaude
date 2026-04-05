import streamlit as st
import pandas as pd
import sqlite3 

from database import conecta_db
from crud_create import insert_cliente
from crud_delete import delete_cliente
from crud_update import update_cliente
from crud import cliente

def main():
    # Inicialização de estados
    if 'mostrar_formulario' not in st.session_state:
        st.session_state.mostrar_formulario = False
    if 'modo' not in st.session_state:
        st.session_state.modo = None
    if 'item_selecionado' not in st.session_state:
        st.session_state.item_selecionado = None

    # --- CABEÇALHO ---
    col_titulo, col_voltar = st.columns([4, 2], vertical_alignment="bottom")
    with col_titulo:
        st.title("👤 Gestão de Clientes")
    with col_voltar:
        if st.button('🔙 Voltar ao Menu', use_container_width=True):
            st.switch_page("app.py")
    
    st.divider()

    # --- BUSCA E LISTAGEM ---
    df_clientes = pd.DataFrame()
    try:
        with sqlite3.connect('prd_saboresaude.db') as conn:
            c_busca, _ = st.columns([2, 1])
            with c_busca:
                busca = st.text_input("Filtrar clientes", placeholder="Nome do cliente...", label_visibility="collapsed")
            
            query = f"""
            SELECT 
                c.id_cliente AS 'ID',
                c.ds_cliente AS 'Cliente',
                cc.ds_categoria AS 'Categoria',                
                c.ds_telefone AS 'Telefone',
                c.ds_endereco AS 'Endereço',
                c.id_cliente_categoria
            FROM cliente c
            LEFT JOIN cliente_categoria cc ON c.id_cliente_categoria = cc.id_cliente_categoria
            WHERE c.ds_cliente LIKE '%{busca}%'
            """
            df_clientes = pd.read_sql_query(query, conn)

        # --- SEÇÃO DE MÉTRICAS (UX IMPROVEMENT) ---
        if not df_clientes.empty:
            # Métrica Geral
            st.subheader("Resumo da Base")
            m_total = st.columns(1)
            m_total[0].metric("Total de Clientes", len(df_clientes))

            # Métricas por Categoria
            # Contamos as ocorrências de cada categoria usando Pandas
            contagem_categorias = df_clientes['Categoria'].value_counts()
            
            if not contagem_categorias.empty:
                # Criamos colunas dinamicamente com base no número de categorias encontradas
                cols = st.columns(len(contagem_categorias))
                for i, (cat_nome, total) in enumerate(contagem_categorias.items()):
                    cols[i].metric(f"Categoria: {cat_nome}", total)
            
            st.write("") # Espaçador
            st.dataframe(
                df_clientes[['ID', 'Cliente', 'Categoria', 'Telefone', 'Endereço']], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("Nenhum cliente cadastrado no sistema.")

    except Exception as e:
        st.error(f"Erro ao acessar base de dados: {e}")

    # --- BOTÕES DE AÇÃO ---
    st.write("")
    col_insert, col_update, col_delete = st.columns(3)

    if col_insert.button("➕ Novo Cliente", use_container_width=True, type="secondary"):
        st.session_state.mostrar_formulario = True
        st.session_state.modo = 'inserir'
        st.session_state.item_selecionado = None
        st.rerun()

    if col_update.button("📝 Editar Cliente", use_container_width=True):
        st.session_state.modo = 'pre-editar'
        st.session_state.mostrar_formulario = False
        st.rerun()

    if col_delete.button("🗑️ Excluir Cliente", use_container_width=True):
        st.session_state.modo = 'pre-excluir'
        st.session_state.mostrar_formulario = False
        st.rerun()

    # --- ÁREA DE SELEÇÃO DINÂMICA ---
    if not df_clientes.empty:
        lista_nomes = df_clientes['Cliente'].tolist()

        if st.session_state.modo == 'pre-editar':
            with st.status("Preparando edição...", expanded=True):
                selecionado = st.selectbox("Escolha o cliente para editar:", options=lista_nomes)
                dados_item = df_clientes[df_clientes['Cliente'] == selecionado].iloc[0]
                
                c_ed1, c_ed2 = st.columns(2)
                if c_ed1.button("Confirmar para Editar", type="primary", use_container_width=True):
                    st.session_state.mostrar_formulario = True
                    st.session_state.modo = 'editar'
                    st.session_state.item_selecionado = dados_item
                    st.rerun()
                if c_ed2.button("Cancelar", use_container_width=True):
                    st.session_state.modo = None
                    st.rerun()

        elif st.session_state.modo == 'pre-excluir':
            with st.expander("⚠️ Confirmar Exclusão", expanded=True):
                selecionado = st.selectbox("Escolha o cliente para remover:", options=lista_nomes)
                dados_item = df_clientes[df_clientes['Cliente'] == selecionado].iloc[0]

                c_del1, c_del2 = st.columns(2)
                if c_del1.button("Sim, Remover", type="primary", use_container_width=True):
                    try:
                        conn, cursor = conecta_db()
                        delete_cliente(conexao=conn, cursor=cursor, id_cliente=dados_item['ID'])
                        conn.close()
                        st.toast(f"Cliente '{selecionado}' removido!", icon="✅")
                        st.session_state.modo = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir: {e}")
                if c_del2.button("Manter Cliente", use_container_width=True):
                    st.session_state.modo = None
                    st.rerun()

    # --- FORMULÁRIO ---
    if st.session_state.mostrar_formulario:
        st.divider()
        modo = st.session_state.modo
        item = st.session_state.item_selecionado
        
        st.subheader("🚀 Novo Cadastro" if modo == 'inserir' else f"⚙️ Atualizando: {item['Cliente']}")
        
        with st.form("form_cliente"):
            nome = st.text_input("Nome Completo", value=item['Cliente'] if item is not None else "")
            
            conn, cursor = conecta_db()
            cats = cursor.execute("SELECT id_cliente_categoria, ds_categoria FROM cliente_categoria").fetchall()
            idx_cat = 0
            if item is not None:
                idx_cat = next((i for i, v in enumerate(cats) if v[0] == item['id_cliente_categoria']), 0)
            
            cat_sel = st.selectbox("Categoria de Cliente", options=cats, format_func=lambda x: x[1], index=idx_cat)
            conn.close()

            col_tel, col_end = st.columns([1, 2])
            with col_tel:
                telefone = st.text_input("Telefone", value=item['Telefone'] if item is not None else "")
            with col_end:
                endereco = st.text_input("Endereço Completo", value=item['Endereço'] if item is not None else "")

            st.write("")
            if st.form_submit_button("Confirmar e Salvar", type="primary", use_container_width=True):
                if nome:
                    try:
                        obj_cli = cliente(
                            id_cliente=item['ID'] if item is not None else None,
                            ds_cliente=nome,
                            id_cliente_categoria=cat_sel[0],
                            ds_telefone=telefone,
                            ds_endereco=endereco
                        )
                        
                        conn, cursor = conecta_db()
                        if modo == 'inserir':
                            insert_cliente(obj_cliente=obj_cli, conexao=conn, cursor=cursor)
                            st.toast("Cliente cadastrado com sucesso!", icon="🎉")
                        else:
                            update_cliente(obj_cliente=obj_cli, conexao=conn, cursor=cursor)
                            st.toast("Dados atualizados!", icon="💾")
                        
                        conn.close()
                        st.session_state.mostrar_formulario = False
                        st.session_state.modo = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro na gravação: {e}")
                else:
                    st.warning("O nome do cliente é obrigatório.")

        if st.button("❌ Descartar Alterações", use_container_width=True):
            st.session_state.mostrar_formulario = False
            st.session_state.modo = None
            st.rerun()

if __name__ == "__main__":
    main()