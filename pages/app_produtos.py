import streamlit as st
import pandas as pd
import sqlite3 

from database import conecta_db

# Importação conforme sua estrutura de arquivos
from crud_create import insert_produto
from crud_delete import delete_produto
from crud_update import update_produto
from crud import produto 

def main():
    # Inicialização de estados
    if 'mostrar_formulario' not in st.session_state:
        st.session_state.mostrar_formulario = False
    if 'modo' not in st.session_state:
        st.session_state.modo = None # 'inserir', 'editar' ou 'excluir'
    if 'item_selecionado' not in st.session_state:
        st.session_state.item_selecionado = None

    # --- CABEÇALHO ---
    col_titulo, col_voltar = st.columns([4, 2], vertical_alignment="bottom")
    with col_titulo:
        st.title("📦 Gestão de Produtos")
    with col_voltar:
        if st.button('🔙 Voltar ao Menu', use_container_width=True):
            st.switch_page("app.py")
    
    st.divider()

    # --- BUSCA E LISTAGEM ---
    df_produtos = pd.DataFrame()
    try:
        with sqlite3.connect('prd_saboresaude.db') as conn:
            # Layout de busca mais moderno
            c_busca, c_vazio = st.columns([2, 1])
            with c_busca:
                busca = st.text_input("Filtrar produtos", placeholder="Digite o nome para pesquisar...", label_visibility="collapsed")
            
            query = f"""
            SELECT 
                p.id_produto AS 'ID',
                p.ds_produto AS 'Produto',
                pc.ds_produto_categoria AS 'Categoria',
                um.ds_unidade_medida AS 'Unidade',
                p.vl_estoque AS 'Estoque',
                p.vl_custo AS 'Custo',
                p.vl_valor AS 'Preço',
                p.id_produto_categoria,
                p.id_unidade_medida
            FROM produto p
            JOIN produto_categoria pc ON p.id_produto_categoria = pc.id_produto_categoria
            JOIN unidade_medida um ON p.id_unidade_medida = um.id_unidade_medida
            WHERE p.ds_produto LIKE '%{busca}%'
            """
            df_produtos = pd.read_sql_query(query, conn)

        # --- MÉTRICAS (UX IMPROVEMENT) ---
        if not df_produtos.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("Total de Itens Cadastrados", len(df_produtos))
            m2.metric("Estoque Total", int(df_produtos['Estoque'].sum()))
            # Cálculo de valor total (Estoque * Preço)
            valor_total = (df_produtos['Estoque'] * df_produtos['Preço']).sum()
            m3.metric("Valor em Estoque Geral", f"R$ {valor_total:,.2f}")
            
            st.write("") # Espaçador
            st.dataframe(
                df_produtos[['ID', 'Produto', 'Categoria', 'Estoque', 'Preço']], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("Nenhum produto encontrado no sistema.")

    except Exception as e:
        st.error(f"Erro ao acessar base de dados: {e}")

    # --- BOTÕES DE AÇÃO ---
    st.write("")
    col_insert, col_update, col_delete = st.columns(3)

    if col_insert.button("➕ Novo Produto", use_container_width=True, type="secondary"):
        st.session_state.mostrar_formulario = True
        st.session_state.modo = 'inserir'
        st.session_state.item_selecionado = None
        st.rerun()

    if col_update.button("📝 Editar Produto", use_container_width=True):
        st.session_state.modo = 'pre-editar'
        st.session_state.mostrar_formulario = False
        st.rerun()

    if col_delete.button("🗑️ Excluir Produto", use_container_width=True):
        st.session_state.modo = 'pre-excluir'
        st.session_state.mostrar_formulario = False
        st.rerun()

    # --- ÁREA DE SELEÇÃO DINÂMICA (CONTEXTUAL) ---
    if not df_produtos.empty:
        lista_nomes = df_produtos['Produto'].tolist()

        if st.session_state.modo == 'pre-editar':
            with st.status("Preparando edição...", expanded=True):
                st.write("Qual produto você deseja modificar?")
                selecionado = st.selectbox("Selecione o produto:", options=lista_nomes, label_visibility="collapsed")
                dados_item = df_produtos[df_produtos['Produto'] == selecionado].iloc[0]
                
                c_ed1, c_ed2 = st.columns(2)
                if c_ed1.button("Abrir Formulário", type="primary", use_container_width=True):
                    st.session_state.mostrar_formulario = True
                    st.session_state.modo = 'editar'
                    st.session_state.item_selecionado = dados_item
                    st.rerun()
                if c_ed2.button("Cancelar", use_container_width=True):
                    st.session_state.modo = None
                    st.rerun()

        elif st.session_state.modo == 'pre-excluir':
            with st.expander("⚠️ Área Crítica: Confirmar Exclusão", expanded=True):
                st.write("Selecione o item para remover permanentemente:")
                selecionado = st.selectbox("Produto para exclusão:", options=lista_nomes, label_visibility="collapsed")
                dados_item = df_produtos[df_produtos['Produto'] == selecionado].iloc[0]

                c_del1, c_del2 = st.columns(2)
                if c_del1.button("Sim, Excluir Agora", type="primary", use_container_width=True):
                    try:
                        conn, cursor = conecta_db()
                        delete_produto(conexao=conn, cursor=cursor, ds_produto=selecionado)
                        conn.close()
                        st.toast(f"Produto '{selecionado}' removido!", icon="✅")
                        st.session_state.modo = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir: {e}")
                
                if c_del2.button("Não, Voltar", use_container_width=True):
                    st.session_state.modo = None
                    st.rerun()

    # --- FORMULÁRIO ÚNICO (ESTILIZADO) ---
    if st.session_state.mostrar_formulario:
        st.divider()
        modo = st.session_state.modo
        item = st.session_state.item_selecionado
        
        titulo_acao = "🚀 Cadastrar Novo Produto" if modo == 'inserir' else f"⚙️ Atualizar: {item['Produto']}"
        st.subheader(titulo_acao)
        
        with st.form("form_produto", clear_on_submit=True):
            ds_produto = st.text_input("Nome Comercial do Produto", value=item['Produto'] if item is not None else "")

            c1, c2 = st.columns(2)
            with c1:
                conn, cursor = conecta_db()
                categorias = cursor.execute("SELECT id_produto_categoria, ds_produto_categoria FROM produto_categoria").fetchall()
                idx_cat = 0
                if item is not None:
                    idx_cat = next((i for i, v in enumerate(categorias) if v[0] == item['id_produto_categoria']), 0)
                
                cat_sel = st.selectbox("Categoria", options=categorias, format_func=lambda x: x[1], index=idx_cat)
                id_cat = cat_sel[0]

            with c2:
                unidades = cursor.execute("SELECT id_unidade_medida, ds_unidade_medida FROM unidade_medida").fetchall()
                idx_uni = 0
                if item is not None:
                    idx_uni = next((i for i, v in enumerate(unidades) if v[0] == item['id_unidade_medida']), 0)
                
                uni_sel = st.selectbox("Unidade de Medida", options=unidades, format_func=lambda x: x[1], index=idx_uni)
                id_uni = uni_sel[0]
                conn.close()

            c3, c4, c5 = st.columns(3)
            with c3:
                vl_est = st.number_input("Qtd em Estoque", min_value=0, step=1, value=int(item['Estoque']) if item is not None else 0)
            with c4:
                vl_cus = st.number_input("Custo Unitário (R$)", min_value=0.0, format="%.2f", value=float(item['Custo']) if item is not None else 0.0)
            with c5:
                vl_val = st.number_input("Preço de Venda (R$)", min_value=0.0, format="%.2f", value=float(item['Preço']) if item is not None else 0.0)

            st.write("") # Espaçador interno
            col_salvar, col_cancelar = st.columns(2)

            with col_salvar:
                if st.form_submit_button("Gravar no Sistema", use_container_width=True, type="primary"):
                    if ds_produto:
                        try:
                            id_atual = item['ID'] if item is not None else None
                            objeto_produto = produto(
                                id_produto=id_atual,
                                ds_produto=ds_produto,
                                id_produto_categoria=id_cat,
                                id_unidade_medida=id_uni,
                                vl_estoque=vl_est,
                                vl_custo=vl_cus,
                                vl_valor=vl_val
                            )
                            
                            conn, cursor = conecta_db()
                            if modo == 'inserir':
                                insert_produto(obj_produto=objeto_produto, conexao=conn, cursor=cursor)
                                st.toast("Produto cadastrado!", icon="🎉")
                            else:
                                update_produto(obj_produto=objeto_produto, conexao=conn, cursor=cursor)
                                st.toast("Dados atualizados!", icon="💾")
                            
                            conn.close()
                            st.session_state.mostrar_formulario = False
                            st.session_state.modo = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro na operação: {e}")
                    else:
                        st.warning("O nome do produto não pode ficar em branco.")

            with col_cancelar:
                # Botão de cancelar dentro do form precisa de lógica especial ou ser fora
                pass
        
        # Botão cancelar fora do form para garantir que o rerun funcione sem submeter
        if st.button("❌ Cancelar e Voltar", use_container_width=True):
            st.session_state.mostrar_formulario = False
            st.session_state.modo = None
            st.rerun()

if __name__ == "__main__":
    main()