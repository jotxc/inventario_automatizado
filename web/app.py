import os
import sys
import uuid
from pathlib import Path

import pandas as pd

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, send_file, flash
)

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from controller.inventario_controller import InventarioController

app = Flask(__name__)
app.secret_key = "inventario-rotativo-secret-key-change-in-production"

_ENTRADA_DIR = _PROJECT_ROOT / "data" / "entrada"
_SAIDA_DIR = _PROJECT_ROOT / "data" / "saida"
_HISTORICO_DIR = _PROJECT_ROOT / "data" / "historico"
_ARQUIVO_SAIDA = _SAIDA_DIR / "Documento_Inventario.xlsx"
_ARQUIVO_HISTORICO = _HISTORICO_DIR / "historico_documentos.xlsx"

_ENTRADA_DIR.mkdir(parents=True, exist_ok=True)
_SAIDA_DIR.mkdir(parents=True, exist_ok=True)
_HISTORICO_DIR.mkdir(parents=True, exist_ok=True)

_sessions: dict[str, InventarioController] = {}

_CRITERIOS_UI = {
    "Valor do Lote": "valor",
    "Dias sem Contagem": "dias",
    "Menos Posicoes": "posicoes",
    "Primeira Contagem": "primeira_contagem",
}

_CRITERIOS_SECUNDARIOS = ["Nenhum", "Primeira Contagem", "Dias sem Contagem", "Valor do Lote", "Menos Posicoes"]
_CRITERIO_SECUNDARIO_MAP = {
    "Nenhum": None, "Primeira Contagem": "primeira_contagem",
    "Dias sem Contagem": "dias", "Valor do Lote": "valor", "Menos Posicoes": "posicoes"
}


def _get_controller() -> InventarioController | None:
    sid = session.get("sid")
    if sid and sid in _sessions:
        return _sessions[sid]
    return None


def _formatar_moeda(valor):
    s = f"R$ {float(valor):,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _formatar_data(valor):
    if valor is None or pd.isna(valor):
        return "---"
    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y %H:%M")
    s = str(valor)
    if " " in s:
        return s.split(".")[0]
    return s


def _formatar_valor_tabela(chave, valor):
    if valor is None or pd.isna(valor):
        if chave in ("ultima_contagem",):
            return "---"
        if chave in ("nunca_contado",):
            return "Nao"
        return ""
    if chave in ("valor_lote",):
        return _formatar_moeda(valor)
    if chave in ("ultima_contagem",):
        return _formatar_data(valor)
    if chave in ("nunca_contado",):
        return "Sim" if valor is True or str(valor).lower() == "true" else "Nao"
    if chave in ("quantidade_posicoes", "dias_sem_contagem", "material"):
        return str(int(float(str(valor))))
    return str(valor)


def _render_tabela(df):
    if df is None or df.empty:
        return '<div class="tabela-mensagem">Nenhum lote encontrado para os criterios selecionados.</div>'
    
    colunas = [
        {"chave": "material", "rotulo": "Material", "alinhamento": "left"},
        {"chave": "descricao_material", "rotulo": "Descricao", "alinhamento": "left"},
        {"chave": "lote", "rotulo": "Lote", "alinhamento": "left"},
        {"chave": "tipo_deposito", "rotulo": "Tipo Dep.", "alinhamento": "center"},
        {"chave": "quantidade_posicoes", "rotulo": "Posicoes", "alinhamento": "center"},
        {"chave": "estoque_total", "rotulo": "Est. Total", "alinhamento": "right"},
        {"chave": "valor_lote", "rotulo": "Valor Total", "alinhamento": "right"},
        {"chave": "dias_sem_contagem", "rotulo": "Dias s/ Cont.", "alinhamento": "center"},
        {"chave": "ultima_contagem", "rotulo": "Data Ult. Cont.", "alinhamento": "center"},
        {"chave": "nunca_contado", "rotulo": "1a Contagem?", "alinhamento": "center"},
    ]
    
    html = '<div class="tabela-scroll"><table><thead><tr>'
    for c in colunas:
        html += f'<th class="alinhar-{c["alinhamento"]}" data-chave="{c["chave"]}">{c["rotulo"]}<span class="icone-ordem"></span></th>'
    html += '</tr></thead><tbody>'
    
    for idx, (_, row) in enumerate(df.iterrows()):
        html += '<tr>'
        for c in colunas:
            v = _formatar_valor_tabela(c["chave"], row.get(c["chave"]))
            html += f'<td class="alinhar-{c["alinhamento"]}">{v}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    return html


def _calcular_totais(df):
    if df is None or df.empty:
        return {"lotes": 0, "posicoes": 0, "valor": "R$ 0,00"}
    total_lotes = len(df)
    total_posicoes = int(df["quantidade_posicoes"].sum()) if "quantidade_posicoes" in df.columns else 0
    total_valor = df["valor_lote"].sum() if "valor_lote" in df.columns else 0
    return {"lotes": total_lotes, "posicoes": total_posicoes, "valor": _formatar_moeda(total_valor)}


# ─── Rotas ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    ctrl = _get_controller()
    if ctrl is None or ctrl.estoque is None:
        return redirect(url_for("upload"))
    
    tipos = (
        ctrl.estoque["tipo_deposito"]
        .drop_duplicates().sort_values()
        .apply(lambda v: str(int(float(str(v)))))
        .tolist()
    )
    
    return render_template("index.html",
        criterios=_CRITERIOS_UI,
        criterios_secundarios=_CRITERIOS_SECUNDARIOS,
        tipos=tipos,
        tem_dados=False,
        tabela_html='<div class="tabela-mensagem">Clique em APLICAR para visualizar os dados.</div>',
        totais={"lotes": 0, "posicoes": 0, "valor": "R$ 0,00"},
        descricao_excluir_qtd=len(ctrl.descricao_excluir) if ctrl else 0,
    )


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        arquivos_ok = 0
        esperados = {"LX02.xlsx", "YMM141.xlsx", "Custos.xlsx"}
        
        for nome_esperado in esperados:
            campo = nome_esperado.replace(".xlsx", "").lower()
            f = request.files.get(campo)
            if f and f.filename:
                dest = _ENTRADA_DIR / nome_esperado
                f.save(str(dest))
                arquivos_ok += 1
        
        if arquivos_ok == 0:
            flash("Selecione pelo menos um arquivo Excel.", "error")
            return redirect(url_for("upload"))
        
        try:
            ctrl = InventarioController()
            ctrl.carregar()
            sid = str(uuid.uuid4())
            _sessions[sid] = ctrl
            session["sid"] = sid
            session.permanent = True
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Erro ao processar dados: {e}", "error")
            return redirect(url_for("upload"))
    
    return render_template("upload.html")


@app.route("/aplicar", methods=["POST"])
def aplicar():
    ctrl = _get_controller()
    if ctrl is None or ctrl.estoque is None:
        return jsonify({"erro": "Dados nao carregados"}), 400
    
    criterio = request.form.get("criterio", "valor")
    criterio_sec_str = request.form.get("criterio_secundario", "Nenhum")
    criterio_sec = _CRITERIO_SECUNDARIO_MAP.get(criterio_sec_str)
    tipo = request.form.get("tipo_deposito", "")
    try:
        limite = int(request.form.get("limite_posicoes", 100))
    except ValueError:
        limite = 100
    modo_sem_maquina = request.form.get("modo_sem_maquina") == "true"
    
    try:
        resultado = ctrl.consultar_estoque(
            criterio=criterio,
            tipo_deposito=tipo,
            limite_posicoes=limite,
            modo_sem_maquina=modo_sem_maquina,
            criterio_secundario=criterio_sec
        )
        
        ctrl.ultima_consulta_sem_exclusao = resultado.copy() if not resultado.empty else None
        resultado = ctrl.aplicar_exclusao(resultado)
        
        tabela_html = _render_tabela(resultado)
        totais = _calcular_totais(resultado)
        
        return jsonify({"tabela": tabela_html, "totais": totais, "ok": True})
    except Exception as e:
        return jsonify({"erro": str(e), "ok": False}), 500


@app.route("/gerar", methods=["POST"])
def gerar():
    ctrl = _get_controller()
    if ctrl is None or ctrl.estoque is None:
        return jsonify({"erro": "Dados nao carregados"}), 400
    
    if not ctrl.aplicacao_realizada:
        return jsonify({"erro": "Clique em APLICAR primeiro para visualizar os dados antes de gerar o documento.", "ok": False}), 400
    
    criterio = request.form.get("criterio", "valor")
    criterio_sec_str = request.form.get("criterio_secundario", "Nenhum")
    criterio_sec = _CRITERIO_SECUNDARIO_MAP.get(criterio_sec_str)
    tipo = request.form.get("tipo_deposito", "")
    try:
        limite = int(request.form.get("limite_posicoes", 100))
    except ValueError:
        limite = 100
    modo_sem_maquina = request.form.get("modo_sem_maquina") == "true"
    baixas_por_ultimo = request.form.get("baixas_por_ultimo") == "true"
    
    try:
        resultado = ctrl.gerar(
            criterio=criterio,
            tipo_deposito=tipo,
            limite_posicoes=limite,
            modo_sem_maquina=modo_sem_maquina,
            criterio_secundario=criterio_sec,
            baixas_por_ultimo=baixas_por_ultimo
        )
        
        session["ultimo_resultado"] = {
            "criterio": criterio,
            "tipo_deposito": tipo,
            "total_lotes": len(resultado.get("sugestao", [])),
            "total_posicoes": int(resultado["sugestao"]["quantidade_posicoes"].sum()) if not resultado["sugestao"].empty else 0,
            "total_valor": float(resultado["sugestao"]["valor_lote"].sum()) if not resultado["sugestao"].empty else 0,
            "arquivo": "Documento_Inventario.xlsx",
            "data_geracao": _formatar_data(resultado.get("data_geracao", "")),
            "id_geracao": resultado.get("id_geracao", ""),
        }
        
        return jsonify({"ok": True, "redirect": url_for("resultado")})
    except Exception as e:
        return jsonify({"erro": str(e), "ok": False}), 500


@app.route("/resultado")
def resultado():
    ctrl = _get_controller()
    if ctrl is None:
        return redirect(url_for("upload"))
    
    r = session.get("ultimo_resultado")
    if not r:
        return redirect(url_for("index"))
    
    tem_documento = _ARQUIVO_SAIDA.exists()
    
    return render_template("resultado.html",
        criterio=r["criterio"],
        tipo_deposito=r["tipo_deposito"],
        total_lotes=r["total_lotes"],
        total_posicoes=r["total_posicoes"],
        total_valor=_formatar_moeda(r["total_valor"]),
        data_geracao=r["data_geracao"],
        id_geracao=r["id_geracao"],
        tem_documento=tem_documento,
    )


@app.route("/historico")
def historico():
    ctrl = _get_controller()
    if ctrl is None:
        return redirect(url_for("upload"))
    
    try:
        geracoes = ctrl.listar_geracoes_historico()
    except Exception:
        geracoes = None
    
    tem_historico = _ARQUIVO_HISTORICO.exists()
    
    geracoes_list = []
    if geracoes is not None and not geracoes.empty:
        for _, row in geracoes.iterrows():
            doc_val = row.get("documento")
            doc_str = str(doc_val) if (pd.notna(doc_val) and str(doc_val).strip()) else ""
            geracoes_list.append({
                "id_geracao": row.get("id_geracao", ""),
                "data_geracao": _formatar_data(row.get("data_geracao", "")),
                "tipo_deposito": str(int(float(str(row.get("tipo_deposito", ""))))) if row.get("tipo_deposito") and pd.notna(row.get("tipo_deposito")) else "",
                "documento": doc_str,
                "total_lotes": int(row.get("total_lotes_geracao", 0)),
                "total_posicoes": int(row.get("total_posicoes_geracao", 0)),
                "total_valor": _formatar_moeda(row.get("total_valor_geracao", 0)),
            })
    
    return render_template("historico.html",
        geracoes=geracoes_list,
        tem_historico=tem_historico,
    )


@app.route("/visao-geral")
def visao_geral():
    ctrl = _get_controller()
    if ctrl is None:
        return redirect(url_for("upload"))
    
    try:
        visao = ctrl.obter_visao_geral()
    except Exception:
        visao = None
    
    tipos_list = []
    if visao is not None and not visao.empty:
        visao = visao.sort_values("percentual_primeira_contagem", ascending=False)
        for _, row in visao.iterrows():
            pct_primeira = float(row["percentual_primeira_contagem"])
            pct_contados = 100 - pct_primeira
            
            if pct_primeira >= 60:
                cor_critica = "var(--cor-erro)"
                texto_status = "Critico"
            elif pct_primeira >= 30:
                cor_critica = "var(--cor-aviso)"
                texto_status = "Atencao"
            else:
                cor_critica = "var(--cor-sucesso)"
                texto_status = "OK"
            
            tipos_list.append({
                "tipo_deposito": str(int(float(str(row["tipo_deposito"])))),
                "total_lotes": int(row["total_lotes"]),
                "lotes_nunca_contados": int(row["lotes_nunca_contados"]),
                "pct_contados": round(pct_contados, 1),
                "pct_primeira": round(pct_primeira, 1),
                "texto_status": texto_status,
                "cor_critica": cor_critica,
                "media_dias": int(round(row.get("media_dias_sem_contagem", 0))),
                "max_dias": int(row.get("max_dias_sem_contagem", 0)),
                "valor_total": _formatar_moeda(row.get("valor_pendente", 0)),
                "valor_primeira": _formatar_moeda(row.get("valor_pendente_primeira_contagem", 0)),
            })
    
    return render_template("visao_geral.html", tipos=tipos_list)


@app.route("/download/documento")
def download_documento():
    if _ARQUIVO_SAIDA.exists():
        return send_file(str(_ARQUIVO_SAIDA), as_attachment=True, download_name="Documento_Inventario.xlsx")
    flash("Nenhum documento gerado ainda.", "warning")
    return redirect(url_for("index"))


@app.route("/download/historico")
def download_historico():
    if _ARQUIVO_HISTORICO.exists():
        return send_file(str(_ARQUIVO_HISTORICO), as_attachment=True, download_name="historico_documentos.xlsx")
    flash("Historico nao encontrado.", "warning")
    return redirect(url_for("historico"))


@app.route("/excluir-geracao/<id_geracao>", methods=["POST"])
def excluir_geracao(id_geracao):
    ctrl = _get_controller()
    if ctrl is None:
        return jsonify({"erro": "Sessao invalida"}), 400
    try:
        sucesso = ctrl.excluir_geracao_historico(id_geracao)
        return jsonify({"ok": sucesso})
    except Exception as e:
        return jsonify({"erro": str(e), "ok": False}), 500


@app.route("/atualizar-documento/<id_geracao>", methods=["POST"])
def atualizar_documento(id_geracao):
    ctrl = _get_controller()
    if ctrl is None:
        return jsonify({"erro": "Sessao invalida"}), 400
    numero = request.form.get("numero", "").strip()
    if not numero:
        return jsonify({"erro": "Numero invalido"}), 400
    try:
        sucesso, mensagem = ctrl.atualizar_numero_documento(id_geracao, numero)
        return jsonify({"ok": sucesso, "mensagem": mensagem})
    except Exception as e:
        return jsonify({"erro": str(e), "ok": False}), 500


# ─── Rotas de Exclusao de Descricao ─────────────────────────────────────

@app.route("/descricoes", methods=["GET"])
def listar_descricoes():
    ctrl = _get_controller()
    if ctrl is None or ctrl.sugestao_base is None or ctrl.sugestao_base.empty:
        return jsonify({"erro": "Aplique os criterios primeiro.", "descricoes": [], "excluidos": []}), 200

    descricoes = sorted(ctrl.sugestao_base["descricao_material"].dropna().unique().tolist())
    return jsonify({
        "descricoes": descricoes,
        "excluidos": sorted(ctrl.descricao_excluir)
    })


@app.route("/aplicar-exclusao", methods=["POST"])
def aplicar_exclusao():
    ctrl = _get_controller()
    if ctrl is None or ctrl.sugestao_base is None:
        return jsonify({"erro": "Nenhum dado carregado."}), 400

    manter = set(request.form.getlist("descricoes"))
    valores_unicos = set(ctrl.sugestao_base["descricao_material"].dropna().unique().tolist())
    if len(manter) < len(valores_unicos):
        ctrl.descricao_excluir = valores_unicos - manter
    else:
        ctrl.descricao_excluir = set()

    dados = ctrl.aplicar_exclusao(ctrl.ultima_consulta_sem_exclusao) if ctrl.ultima_consulta_sem_exclusao is not None else None
    if dados is not None:
        tabela_html = _render_tabela(dados)
        totais = _calcular_totais(dados)
    else:
        tabela_html = '<div class="tabela-mensagem">Nenhum dado.</div>'
        totais = {"lotes": 0, "posicoes": 0, "valor": "R$ 0,00"}

    return jsonify({
        "ok": True,
        "tabela": tabela_html,
        "totais": totais,
        "qtd_excluidos": len(ctrl.descricao_excluir)
    })


@app.route("/limpar-exclusao", methods=["POST"])
def limpar_exclusao():
    ctrl = _get_controller()
    if ctrl is None:
        return jsonify({"erro": "Sessao invalida"}), 400

    ctrl.descricao_excluir = set()

    dados = ctrl.ultima_consulta_sem_exclusao
    if dados is not None:
        tabela_html = _render_tabela(dados)
        totais = _calcular_totais(dados)
    else:
        tabela_html = '<div class="tabela-mensagem">Nenhum dado.</div>'
        totais = {"lotes": 0, "posicoes": 0, "valor": "R$ 0,00"}

    return jsonify({
        "ok": True,
        "tabela": tabela_html,
        "totais": totais,
        "qtd_excluidos": 0
    })


# ─── Rotas de Detalhes / Resumo do Documento ────────────────────────────

@app.route("/detalhes-geracao/<id_geracao>")
def detalhes_geracao(id_geracao):
    ctrl = _get_controller()
    if ctrl is None:
        return jsonify({"erro": "Sessao invalida"}), 400
    try:
        detalhes = ctrl.obter_detalhes_geracao(id_geracao)
        if detalhes is None or detalhes.empty:
            return jsonify({"erro": "Nenhum detalhe encontrado.", "dados": []}), 200

        colunas = [
            {"chave": "material", "rotulo": "Material"},
            {"chave": "lote", "rotulo": "Lote"},
            {"chave": "tipo_deposito", "rotulo": "Tipo Dep."},
            {"chave": "quantidade_posicoes", "rotulo": "Posicoes"},
            {"chave": "valor_lote", "rotulo": "Valor"},
        ]
        linhas = []
        for _, row in detalhes.iterrows():
            linha = {}
            for c in colunas:
                v = row.get(c["chave"])
                if c["chave"] == "valor_lote":
                    linha[c["chave"]] = _formatar_moeda(v) if pd.notna(v) else "---"
                elif c["chave"] == "quantidade_posicoes":
                    linha[c["chave"]] = str(int(float(str(v)))) if pd.notna(v) else "0"
                else:
                    linha[c["chave"]] = str(v) if pd.notna(v) else "---"
            linhas.append(linha)

        return jsonify({"ok": True, "colunas": colunas, "dados": linhas})
    except Exception as e:
        return jsonify({"erro": str(e), "ok": False}), 500


@app.route("/resumo-documento/<id_geracao>")
def resumo_documento(id_geracao):
    ctrl = _get_controller()
    if ctrl is None:
        return redirect(url_for("upload"))
    try:
        detalhes = ctrl.obter_detalhes_geracao(id_geracao)
        if detalhes is None or detalhes.empty:
            return render_template("resumo_documento.html", id_geracao=id_geracao, tem_dados=False, dados=[])

        linhas = []
        for _, row in detalhes.iterrows():
            linhas.append({
                "material": str(row.get("material", "")) if pd.notna(row.get("material")) else "",
                "lote": str(row.get("lote", "")) if pd.notna(row.get("lote")) else "",
                "tipo_deposito": str(int(float(str(row.get("tipo_deposito", ""))))) if pd.notna(row.get("tipo_deposito")) and row.get("tipo_deposito") != "" else "",
                "quantidade_posicoes": str(int(float(str(row.get("quantidade_posicoes", 0))))) if pd.notna(row.get("quantidade_posicoes")) else "0",
                "valor_lote": _formatar_moeda(row.get("valor_lote", 0)) if pd.notna(row.get("valor_lote")) else "R$ 0,00",
            })

        return render_template("resumo_documento.html", id_geracao=id_geracao, tem_dados=True, dados=linhas)
    except Exception as e:
        return render_template("resumo_documento.html", id_geracao=id_geracao, tem_dados=False, dados=[], erro=str(e))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
