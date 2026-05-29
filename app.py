import os
from siege_api import list_invoices, download_invoice_xml
from flask import Flask, render_template, request, jsonify
from database import DatabaseManager
from xml_parser import parse_xml_invoice
from calculadora import CalculadoraTributaria

app = Flask(__name__, template_folder="templates", static_folder="static")
db = DatabaseManager()

@app.route("/")
def index():
    # Em produção, este valor poderá ser obtido a partir da sessão de login ou cookies de SSO da sua empresa.
    # Por padrão, ele lerá a variável de ambiente CURRENT_USER ou adotará 'ARTURMMN'.
    user_name = os.getenv("CURRENT_USER", "ARTURMMN")
    return render_template("index.html", user_name=user_name)

# ==========================================
# REST API: EMPRESAS
# ==========================================

@app.route("/api/empresas", methods=["GET"])
def list_empresas():
    try:
        empresas = db.listar_empresas()
        return jsonify(empresas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/empresas/<int:id>", methods=["GET"])
def get_empresa(id):
    try:
        empresa = db.obter_empresa(id)
        if empresa:
            return jsonify(empresa)
        return jsonify({"error": "Empresa não encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/empresas", methods=["POST"])
def save_empresa():
    try:
        data = request.json
        emp_id = db.salvar_empresa(
            nome=data.get("nome"),
            cnpj=data.get("cnpj"),
            regime=data.get("regime"),
            atividade=data.get("atividade"),
            faturamento_anual=float(data.get("faturamento_anual", 0)),
            folha_anual=float(data.get("folha_anual", 0))
        )
        return jsonify({"success": True, "id": emp_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/empresas/<int:id>", methods=["DELETE"])
def delete_empresa(id):
    try:
        db.excluir_empresa(id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# REST API: NOTAS FISCAIS
# ==========================================

@app.route("/api/notas", methods=["GET"])
def list_notas():
    try:
        empresa_id = request.args.get("empresa_id", type=int)
        mes = request.args.get("mes", type=int)
        ano = request.args.get("ano", type=int)
        tipo = request.args.get("tipo")
        
        if not empresa_id:
            return jsonify({"error": "empresa_id é obrigatório"}), 400
            
        notas = db.listar_notas(empresa_id, mes, ano, tipo)
        return jsonify(notas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/notas/<int:id>", methods=["DELETE"])
def delete_nota(id):
    try:
        db.excluir_nota(id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/notas/manual", methods=["POST"])
def save_nota_manual():
    try:
        data = request.json
        success = db.salvar_nota(data)
        if success:
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Falha ao salvar nota"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# XML UPLOAD API
# ==========================================

@app.route("/api/upload", methods=["POST"])
def upload_xml():
    try:
        data = request.json
        empresa_id = data.get("empresa_id")
        filename = data.get("filename")
        xml_content = data.get("xml_content")
        
        if not empresa_id or not xml_content:
            return jsonify({"success": False, "message": "Dados incompletos"}), 400
            
        empresa = db.obter_empresa(empresa_id)
        if not empresa:
            return jsonify({"success": False, "message": "Empresa ativa inválida"}), 400
            
        # Parse XML
        nota_fisc = parse_xml_invoice(xml_content, company_cnpj=empresa["cnpj"])
        if not nota_fisc:
            return jsonify({"success": False, "message": "Falha ao analisar estrutura do XML"}), 400
            
        # Inject default outras_retencoes if missing (3.65% of total)
        if nota_fisc.get("outras_retencoes", 0) == 0:
            try:
                total = float(nota_fisc.get("valor_total", 0))
                nota_fisc["outras_retencoes"] = round(total * 0.0365, 2)
            except Exception:
                nota_fisc["outras_retencoes"] = 0
        
        # Inject details
        nota_fisc["empresa_id"] = empresa_id
        nota_fisc["xml_origem"] = filename
        
        # Save to DB
        success = db.salvar_nota(nota_fisc)
        if success:
            return jsonify({"success": True, "nota_numero": nota_fisc["numero"]})
        return jsonify({"success": False, "message": "Nota já importada ou duplicada"}), 400
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==========================================
# COMPUTATIONS & KPI DASHBOARD
# ==========================================

@app.route("/api/dashboard", methods=["GET"])
def get_dashboard_summary():
    try:
        empresa_id = request.args.get("empresa_id", type=int)
        mes = request.args.get("mes", type=int)
        ano = request.args.get("ano", type=int)
        
        if not empresa_id or not mes or not ano:
            return jsonify({"error": "Parâmetros incompletos"}), 400
            
        empresa = db.obter_empresa(empresa_id)
        if not empresa:
            return jsonify({"error": "Empresa não encontrada"}), 404
            
        # Totals from invoices ledger
        totais = db.obter_totais_periodo(empresa_id, mes, ano)
        
        # Prejuízo fiscal anterior (opcional - fixado em 0 ou buscando no DB se implementado)
        prejuizo_fiscal = 0 # Pode ser expandido
        
        # Executar motor de cálculo com regime atual da empresa
        resultado = CalculadoraTributaria.calcular(
            regime=empresa["regime"],
            mes=mes,
            ano=ano,
            receita_bruta=totais["receita_bruta"],
            custos=totais["custos"],
            despesas=totais["despesas"],
            creditos_pis=totais["creditos_pis"],
            creditos_cofins=totais["creditos_cofins"],
            icms_saida=totais["icms_saida"],
            icms_entrada=totais["icms_entrada"],
            faturamento_anual=totais["faturamento_anual_acumulado"],
            folha_anual=empresa["folha_anual"],
            activity_type=empresa["atividade"],
            prejuizo_fiscal=prejuizo_fiscal
        )
        
        # Gerar Alertas
        alertas = []
        if empresa["regime"] == "simples":
            # Alerta Sublimite R$ 3.6M
            if resultado.excedeu_sublimite:
                alertas.append({
                    "tipo": "warning",
                    "titulo": "Sublimite de Faturamento Excedido (R$ 3.6M)",
                    "descricao": f"O faturamento acumulado de R$ {resultado.faturamento_anual:,.2f} ultrapassou o sublimite. O ISS/ICMS deste período deverá ser recolhido por fora da guia do Simples Nacional pelas regras gerais de débito/crédito normal do município e estado!"
                })
            # Alerta Limite Geral R$ 4.8M
            if resultado.excedeu_limite:
                alertas.append({
                    "tipo": "danger",
                    "titulo": "Limite Geral de Enquadramento Estourado (R$ 4.8M)",
                    "descricao": f"O faturamento acumulado de R$ {resultado.faturamento_anual:,.2f} excedeu o limite geral nacional. A exclusão do Simples Nacional é obrigatória."
                })
        
        if empresa["regime"] in ["presumido", "real"]:
            # Alerta Transição Reforma 2026
            alertas.append({
                "tipo": "info",
                "titulo": "Transição da Reforma Tributária (CBS/IBS)",
                "descricao": f"Apuração modelo 2026 em andamento. Foi provisionado CBS (0,9%) e IBS (0,1%) no valor total de R$ {resultado.total_transicao_2026:,.2f}. Estes tributos estão compensados integralmente no abatimento dos débitos mensais de PIS e COFINS (regra de dupla conformidade)."
            })
            
            # Alerta Adicional IRPJ mensal
            if resultado.base_irpj_apos_compensacao > 20000:
                alertas.append({
                    "tipo": "info",
                    "titulo": "Adicional de IRPJ Incidindo no Mês",
                    "descricao": f"O lucro tributável no mês excedeu R$ 20.000,00. Incidência da alíquota adicional de 10% aplicada sobre a parcela excedente na competência mensal."
                })

        # Carga tributária efetiva
        carga_efetiva = (resultado.total_impostos / totais["receita_bruta"] * 100) if totais["receita_bruta"] > 0 else 0
        
        regime_label = ""
        if empresa["regime"] == "simples": regime_label = "Simples Nacional"
        elif empresa["regime"] == "presumido": regime_label = "Lucro Presumido"
        elif empresa["regime"] == "real": regime_label = "Lucro Real"

        return jsonify({
            "receita_bruta": totais["receita_bruta"],
            "total_impostos": resultado.total_impostos,
            "lucro_liquido": resultado.lucro_liquido,
            "carga_efetiva": carga_efetiva,
            "regime": regime_label,
            "regime_tipo": empresa["regime"],
            "faturamento_anual": totais["faturamento_anual_acumulado"],
            "alertas": alertas
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/comparativo", methods=["GET"])
def get_regimes_comparison():
    try:
        empresa_id = request.args.get("empresa_id", type=int)
        mes = request.args.get("mes", type=int)
        ano = request.args.get("ano", type=int)
        
        if not empresa_id or not mes or not ano:
            return jsonify({"error": "Parâmetros incompletos"}), 400
            
        empresa = db.obter_empresa(empresa_id)
        if not empresa:
            return jsonify({"error": "Empresa não encontrada"}), 404
            
        totais = db.obter_totais_periodo(empresa_id, mes, ano)
        
        # Calcular Simples Nacional
        res_simples = CalculadoraTributaria.calcular(
            regime="simples", mes=mes, ano=ano,
            receita_bruta=totais["receita_bruta"], custos=totais["custos"], despesas=totais["despesas"],
            creditos_pis=totais["creditos_pis"], creditos_cofins=totais["creditos_cofins"],
            icms_saida=totais["icms_saida"], icms_entrada=totais["icms_entrada"],
            faturamento_anual=totais["faturamento_anual_acumulado"],
            folha_anual=empresa["folha_anual"], activity_type=empresa["atividade"]
        )
        
        # Calcular Lucro Presumido
        res_presumido = CalculadoraTributaria.calcular(
            regime="presumido", mes=mes, ano=ano,
            receita_bruta=totais["receita_bruta"], custos=totais["custos"], despesas=totais["despesas"],
            creditos_pis=totais["creditos_pis"], creditos_cofins=totais["creditos_cofins"],
            icms_saida=totais["icms_saida"], icms_entrada=totais["icms_entrada"],
            faturamento_anual=totais["faturamento_anual_acumulado"],
            folha_anual=empresa["folha_anual"], activity_type=empresa["atividade"]
        )
        
        # Calcular Lucro Real
        res_real = CalculadoraTributaria.calcular(
            regime="real", mes=mes, ano=ano,
            receita_bruta=totais["receita_bruta"], custos=totais["custos"], despesas=totais["despesas"],
            creditos_pis=totais["creditos_pis"], creditos_cofins=totais["creditos_cofins"],
            icms_saida=totais["icms_saida"], icms_entrada=totais["icms_entrada"],
            faturamento_anual=totais["faturamento_anual_acumulado"],
            folha_anual=empresa["folha_anual"], activity_type=empresa["atividade"]
        )
        
        return jsonify({
            "simples": res_simples.total_impostos,
            "presumido": res_presumido.total_impostos,
            "real": res_real.total_impostos
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# APURAÇÃO DETAILS: DRE & MEMORIA
# ==========================================

@app.route("/api/apuracao/dre", methods=["GET"])
def get_dre_html():
    try:
        empresa_id = request.args.get("empresa_id", type=int)
        mes = request.args.get("mes", type=int)
        ano = request.args.get("ano", type=int)
        
        if not empresa_id or not mes or not ano:
            return jsonify({"error": "Parâmetros inválidos"}), 400
            
        empresa = db.obter_empresa(empresa_id)
        if not empresa:
            return jsonify({"error": "Empresa não cadastrada"}), 404
            
        totais = db.obter_totais_periodo(empresa_id, mes, ano)
        
        resultado = CalculadoraTributaria.calcular(
            regime=empresa["regime"],
            mes=mes,
            ano=ano,
            receita_bruta=totais["receita_bruta"],
            custos=totais["custos"],
            despesas=totais["despesas"],
            creditos_pis=totais["creditos_pis"],
            creditos_cofins=totais["creditos_cofins"],
            icms_saida=totais["icms_saida"],
            icms_entrada=totais["icms_entrada"],
            faturamento_anual=totais["faturamento_anual_acumulado"],
            folha_anual=empresa["folha_anual"],
            activity_type=empresa["atividade"]
        )
        
        html_content = CalculadoraTributaria.gerar_dre_html(resultado)
        return jsonify({"html": html_content})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/apuracao/memoria", methods=["GET"])
def get_memoria_items():
    try:
        empresa_id = request.args.get("empresa_id", type=int)
        mes = request.args.get("mes", type=int)
        ano = request.args.get("ano", type=int)
        
        if not empresa_id or not mes or not ano:
            return jsonify({"error": "Parâmetros inválidos"}), 400
            
        empresa = db.obter_empresa(empresa_id)
        if not empresa:
            return jsonify({"error": "Empresa não cadastrada"}), 404
            
        totais = db.obter_totais_periodo(empresa_id, mes, ano)
        
        resultado = CalculadoraTributaria.calcular(
            regime=empresa["regime"],
            mes=mes,
            ano=ano,
            receita_bruta=totais["receita_bruta"],
            custos=totais["custos"],
            despesas=totais["despesas"],
            creditos_pis=totais["creditos_pis"],
            creditos_cofins=totais["creditos_cofins"],
            icms_saida=totais["icms_saida"],
            icms_entrada=totais["icms_entrada"],
            faturamento_anual=totais["faturamento_anual_acumulado"],
            folha_anual=empresa["folha_anual"],
            activity_type=empresa["atividade"]
        )
        
        # Serialize list of MemoriaCalculoItem to dictionaries
        serialized_memoria = []
        for item in resultado.memoria:
            serialized_memoria.append({
                "imposto": item.imposto,
                "base_calculo": item.base_calculo,
                "aliquota": item.aliquota,
                "valor_debito": item.valor_debito,
                "valor_credito": item.valor_credito,
                "valor_total": item.valor_total,
                "detalhamento": item.detalhamento
            })
            
        return jsonify({"memoria": serialized_memoria})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# INTEGRAÇÃO SIEG API
# ==========================================

@app.route("/api/sieg/sync", methods=["POST"])
def sync_sieg():
    """Sincroniza notas fiscais da API Sieg para uma empresa.
    Payload JSON esperado:
        {
            "empresa_id": int,
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        }
    Retorna resumo das notas importadas.
    """
    try:
        data = request.json or {}
        empresa_id = data.get("empresa_id")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if not all([empresa_id, start_date, end_date]):
            return jsonify({"error": "Parâmetros obrigatórios: empresa_id, start_date, end_date"}), 400

        empresa = db.obter_empresa(empresa_id)
        if not empresa:
            return jsonify({"error": "Empresa não encontrada"}), 404

        cnpj = empresa["cnpj"]
        invoices = list_invoices(cnpj, start_date, end_date)
        imported = []
        errors = []

        for inv in invoices:
            try:
                xml = download_invoice_xml(inv["id"])
                nota = parse_xml_invoice(xml, company_cnpj=cnpj)
                if not nota:
                    errors.append({"id": inv["id"], "erro": "Falha ao analisar XML"})
                    continue

                # Injetar retenção padrão 3.65% quando ausente
                if nota.get("outras_retencoes", 0) == 0:
                    try:
                        total = float(nota.get("valor_total", 0))
                        nota["outras_retencoes"] = round(total * 0.0365, 2)
                    except Exception:
                        nota["outras_retencoes"] = 0

                nota["empresa_id"] = empresa_id
                nota["xml_origem"] = f"sieg_{inv['id']}.xml"

                if db.salvar_nota(nota):
                    imported.append(nota.get("numero"))
                else:
                    errors.append({"id": inv["id"], "erro": "Nota duplicada ou falha ao salvar"})
            except Exception as inv_err:
                errors.append({"id": inv.get("id", "?"), "erro": str(inv_err)})

        return jsonify({
            "success": True,
            "imported": imported,
            "total_fetched": len(invoices),
            "total_imported": len(imported),
            "errors": errors
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sieg/status", methods=["GET"])
def sieg_status():
    """Verifica se a chave da API Sieg está configurada."""
    from siege_api import SIEG_API_KEY
    configured = bool(SIEG_API_KEY)
    return jsonify({"configured": configured})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
