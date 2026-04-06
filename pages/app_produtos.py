import streamlit as st
import pandas as pd
import sqlite3
from database import conecta_db

# Importações do CRUD de produtos
from crud_create import insert_produto
from crud_update import update_produto
from crud_delete import delete_produto
from crud import produto

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
        st.title("🍎 Gestão de Produtos")
    with col_voltar:
        if st.button('🔙 Voltar ao Menu', use_container_width=True):
            st.switch_page("app.py")
    
    st.divider()

    # --- BUSCA E LISTAGEM ---
    df_produtos = pd.DataFrame()
    try:
        # Nota: Idealmente usar a função conecta_db() aqui também para manter o padrão
        with sqlite3.connect('prd_saboresaude.db') as conn:
            c_busca, _ = st.columns([2, 1])
            with c_busca:
                busca = st.text_input("Filtrar produtos", placeholder="Nome do produto...", label_visibility="collapsed")
            
            query = f"""
            SELECT 
                p.id_produto AS 'ID',
                p.ds_produto AS 'Produto',
                pc.ds_produto_categoria AS 'Categoria',
                um.ds_unidade_medida AS 'Unidade',
                p.vl_estoque AS 'Estoque',
                p.vl_valor AS 'Preço (R$)',
                p.id_produto_categoria,
                p.id_unidade_medida,
                p.vl_custo
            FROM produto p
            LEFT JOIN produto_categoria pc ON p.id_produto_categoria = pc.id_produto_categoria
            LEFT JOIN unidade_medida um ON p.id_unidade_medida = um.id_unidade_medida
            WHERE p.ds_produto LIKE '%{busca}%'
            """
            df_produtos = pd.read_sql_query(query, conn)

        if not df_produtos.empty:
            contagem_cat = df_produtos['Categoria'].value_counts()
            cols = st.columns(1 + len(contagem_cat))
            cols[0].metric("Total Itens", len(df_produtos))
            for i, (cat, qtd) in enumerate(contagem_cat.items()):
                cols[i+1].metric(cat, qtd)

            st.write("")
            st.dataframe(df_produtos[['ID', 'Produto', 'Categoria', 'Unidade', 'Estoque', 'Preço (R$)']], 
                         use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum produto cadastrado.")

    except Exception as e:
        st.error(f"Erro ao carregar produtos: {e}")

    # --- BOTÕES DE AÇÃO ---
    st.write("")
    c1, c2, c3 = st.columns(3)
    if c1.button("➕ Novo Produto", use_container_width=True):
        st.session_state.mostrar_formulario = True
        st.session_state.modo = 'inserir'
        st.session_state.item_selecionado = None
        st.rerun()

    if c2.button("📝 Editar Produto", use_container_width=True):
        st.session_state.modo = 'pre-editar'
        st.session_state.mostrar_formulario = False
        st.rerun()

    if c3.button("🗑️ Excluir Produto", use_container_width=True):
        st.session_state.modo = 'pre-excluir'
        st.session_state.mostrar_formulario = False
        st.rerun()

    # --- ÁREA DE SELEÇÃO DINÂMICA ---
    if not df_produtos.empty:
        if st.session_state.modo == 'pre-editar':
            with st.status("🔍 Selecione o produto para modificar", expanded=True):
                lista_nomes = df_produtos['Produto'].tolist()
                selecionado = st.selectbox("Produto:", options=lista_nomes, key="sb_editar")
                
                # Encontrar a linha completa do produto selecionado
                dados_item = df_produtos[df_produtos['Produto'] == selecionado].iloc[0]
                
                col_conf1, col_conf2 = st.columns(2)
                if col_conf1.button("✅ Confirmar Seleção", type="primary", use_container_width=True):
                    st.session_state.item_selecionado = dados_item.to_dict()
                    st.session_state.modo = 'editar'
                    st.session_state.mostrar_formulario = True
                    st.rerun()
                if col_conf2.button("Cancelar", use_container_width=True):
                    st.session_state.modo = None
                    st.rerun()

        elif st.session_state.modo == 'pre-excluir':
            with st.expander("⚠️ Confirmar exclusão de produto", expanded=True):
                lista_nomes = df_produtos['Produto'].tolist()
                selecionado = st.selectbox("Produto a remover:", options=lista_nomes, key="sb_deletar")
                dados_item = df_produtos[df_produtos['Produto'] == selecionado].iloc[0]

                if st.button(f"Remover {selecionado} permanentemente", type="primary", use_container_width=True):
                    try:
                        conn, cursor = conecta_db()
                        delete_produto(conexao=conn, cursor=cursor, ds_produto=selecionado)
                        conn.close()
                        st.toast(f"Produto {selecionado} removido!", icon="✅")
                        st.session_state.modo = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao deletar: {e}")

    # --- FORMULÁRIO ---
    if st.session_state.mostrar_formulario:
        st.divider()
        modo = st.session_state.modo
        item = st.session_state.item_selecionado
        
        st.subheader("📝 Editar Produto" if modo == 'editar' else "🚀 Novo Produto")
        
        with st.form("form_prod"):
            nome = st.text_input("Nome do Produto", value=item['Produto'] if item else "")
            
            conn, cursor = conecta_db()
            cats = cursor.execute("SELECT id_produto_categoria, ds_produto_categoria FROM produto_categoria").fetchall()
            ums = cursor.execute("SELECT id_unidade_medida, ds_unidade_medida FROM unidade_medida").fetchall()
            conn.close()
            
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                idx_cat = 0
                if item:
                    idx_cat = next((i for i, v in enumerate(cats) if v[0] == item['id_produto_categoria']), 0)
                sel_cat = st.selectbox("Categoria", options=cats, format_func=lambda x: x[1], index=idx_cat)
            
            with c_f2:
                idx_um = 0
                if item:
                    idx_um = next((i for i, v in enumerate(ums) if v[0] == item['id_unidade_medida']), 0)
                sel_um = st.selectbox("Unidade Medida", options=ums, format_func=lambda x: x[1], index=idx_um)

            c_f3, c_f4, c_f5 = st.columns(3)
            with c_f3:
                custo = st.number_input("Custo (R$)", value=float(item['vl_custo']) if item else 0.0, format="%.2f")
            with c_f4:
                preco = st.number_input("Preço Venda (R$)", value=float(item['Preço (R$)']) if item else 0.0, format="%.2f")
            with c_f5:
                estoque = st.number_input("Estoque", value=float(item['Estoque']) if item else 0.0)

            if st.form_submit_button("Confirmar e Salvar", type="primary", use_container_width=True):
                try:
                    # Recuperamos o ID para garantir que ele seja enviado no objeto
                    id_prod_salvar = int(item['ID']) if modo == 'editar' and item else None
                    
                    obj_p = produto(
                        id_produto=id_prod_salvar,
                        ds_produto=nome,
                        id_produto_categoria=sel_cat[0],
                        id_unidade_medida=sel_um[0],
                        vl_estoque=estoque,
                        vl_custo=custo,
                        vl_valor=preco
                    )
                    
                    conn, cursor = conecta_db()
                    if modo == 'inserir':
                        insert_produto(obj_produto=obj_p, conexao=conn, cursor=cursor)
                        st.success("Produto inserido com sucesso!")
                    else:
                        # Agora o obj_p carrega o ID, e sua função atualizada usará ele no WHERE
                        update_produto(obj_produto=obj_p, conexao=conn, cursor=cursor)
                        st.success("Produto atualizado com sucesso!")
                    
                    conn.close()
                    
                    # Limpeza de estado após sucesso
                    st.session_state.mostrar_formulario = False
                    st.session_state.modo = None
                    st.session_state.item_selecionado = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro na gravação: {e}")

        if st.button("❌ Descartar Alterações", use_container_width=True):
            st.session_state.mostrar_formulario = False
            st.session_state.modo = None
            st.session_state.item_selecionado = None
            st.rerun()

if __name__ == "__main__":
    main()