from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class MemoriaCalculoItem:
    imposto: str
    base_calculo: float
    aliquota: float
    valor_debito: float
    valor_credito: float
    valor_total: float
    detalhamento: Dict = field(default_factory=dict)


@dataclass
class ResultadoImpostos:
    regime: str
    mes: int
    ano: int
    receita_bruta: float = 0
    receita_liquida: float = 0
    custos: float = 0
    despesas: float = 0
    lucro_real: float = 0
    
    # Impostos
    irpj: float = 0
    csll: float = 0
    pis: float = 0
    cofins: float = 0
    iss: float = 0
    icms: float = 0
    
    # Simples Nacional segregados
    das: float = 0
    icms_fora: float = 0
    iss_fora: float = 0
    excedeu_sublimite: bool = False
    excedeu_limite: bool = False
    anexo: str = ""
    faixa: int = 0
    
    # Reforma Tributária 2026
    cbs_transicao: float = 0
    ibs_transicao: float = 0
    total_transicao_2026: float = 0
    
    # Totais e Finais
    subtotal_lucro: float = 0
    total_impostos: float = 0
    lucro_liquido: float = 0
    
    prejuizo_compensado: float = 0
    base_irpj_apos_compensacao: float = 0
    
    memoria: List[MemoriaCalculoItem] = field(default_factory=list)


class CalculadoraTributaria:
    TABELA_ANEXO_I_COMERCIO = {
        1: {"faixa_anual": 180_000, "aliquota": 0.04, "parcela_deduzir": 0},
        2: {"faixa_anual": 360_000, "aliquota": 0.073, "parcela_deduzir": 5_940},
        3: {"faixa_anual": 720_000, "aliquota": 0.095, "parcela_deduzir": 13_860},
        4: {"faixa_anual": 1_800_000, "aliquota": 0.107, "parcela_deduzir": 22_500},
        5: {"faixa_anual": 3_600_000, "aliquota": 0.143, "parcela_deduzir": 87_300},
        6: {"faixa_anual": 4_800_000, "aliquota": 0.19, "parcela_deduzir": 378_000},
    }

    TABELA_ANEXO_III_SERVICOS = {
        1: {"faixa_anual": 180_000, "aliquota": 0.06, "parcela_deduzir": 0},
        2: {"faixa_anual": 360_000, "aliquota": 0.112, "parcela_deduzir": 9_360},
        3: {"faixa_anual": 720_000, "aliquota": 0.135, "parcela_deduzir": 17_640},
        4: {"faixa_anual": 1_800_000, "aliquota": 0.16, "parcela_deduzir": 35_640},
        5: {"faixa_anual": 3_600_000, "aliquota": 0.21, "parcela_deduzir": 125_640},
        6: {"faixa_anual": 4_800_000, "aliquota": 0.33, "parcela_deduzir": 648_000},
    }

    TABELA_ANEXO_V_SERVICOS = {
        1: {"faixa_anual": 180_000, "aliquota": 0.155, "parcela_deduzir": 0},
        2: {"faixa_anual": 360_000, "aliquota": 0.18, "parcela_deduzir": 4_500},
        3: {"faixa_anual": 720_000, "aliquota": 0.195, "parcela_deduzir": 9_900},
        4: {"faixa_anual": 1_800_000, "aliquota": 0.205, "parcela_deduzir": 17_100},
        5: {"faixa_anual": 3_600_000, "aliquota": 0.23, "parcela_deduzir": 62_100},
        6: {"faixa_anual": 4_800_000, "aliquota": 0.305, "parcela_deduzir": 540_000},
    }

    @classmethod
    def calcular(cls, regime, mes, ano, receita_bruta, custos, despesas, creditos_pis=0, creditos_cofins=0,
                 icms_saida=0, icms_entrada=0, iss_nota=0, faturamento_anual=0, folha_anual=0, activity_type="servicos", prejuizo_fiscal=0):
        
        if faturamento_anual == 0:
            faturamento_anual = receita_bruta * 12

        if regime == "simples":
            return cls._calcular_simples(mes, ano, receita_bruta, faturamento_anual, folha_anual, activity_type)
        elif regime == "presumido":
            return cls._calcular_presumido(mes, ano, receita_bruta, custos, despesas, activity_type)
        elif regime == "real":
            return cls._calcular_real(mes, ano, receita_bruta, custos, despesas, creditos_pis, creditos_cofins, icms_saida, icms_entrada, prejuizo_fiscal, activity_type)
        else:
            raise ValueError(f"Regime tributário desconhecido: {regime}")

    @classmethod
    def _calcular_simples(cls, mes, ano, receita_bruta, faturamento_anual, folha_anual, activity_type):
        res = ResultadoImpostos(regime="Simples Nacional", mes=mes, ano=ano, receita_bruta=receita_bruta)
        
        nome_anexo = "I"
        if activity_type == "comercio":
            tabela = cls.TABELA_ANEXO_I_COMERCIO
            nome_anexo = "Anexo I (Comércio)"
        elif activity_type == "servicos":
            tabela = cls.TABELA_ANEXO_III_SERVICOS
            nome_anexo = "Anexo III (Serviços)"
        elif activity_type == "fator_r":
            fator_r = (folha_anual / faturamento_anual) if faturamento_anual > 0 else 0
            if fator_r >= 0.28:
                tabela = cls.TABELA_ANEXO_III_SERVICOS
                nome_anexo = "Anexo III (Serviços - Fator R >= 28%)"
            else:
                tabela = cls.TABELA_ANEXO_V_SERVICOS
                nome_anexo = "Anexo V (Serviços - Fator R < 28%)"
        else:
            tabela = cls.TABELA_ANEXO_III_SERVICOS
            nome_anexo = "Anexo III (Serviços)"

        # Determinar faixa
        faixa_sel = 6
        faixa_dados = tabela[6]
        for num, dados in tabela.items():
            if faturamento_anual <= dados["faixa_anual"]:
                faixa_sel = num
                faixa_dados = dados
                break

        aliquota_nominal = faixa_dados["aliquota"]
        parcela_deduzir = faixa_dados["parcela_deduzir"]

        # Alíquota efetiva
        if faturamento_anual > 0:
            aliquota_efetiva = (faturamento_anual * aliquota_nominal - parcela_deduzir) / faturamento_anual
        else:
            aliquota_efetiva = aliquota_nominal
            
        aliquota_efetiva = max(0.0, aliquota_efetiva)

        # Regras de sublimites (R$ 3.600.000,00) e exclusão (R$ 4.800.000,00)
        res.excedeu_sublimite = faturamento_anual > 3_600_000.00
        res.excedeu_limite = faturamento_anual > 4_800_000.00
        res.anexo = nome_anexo
        res.faixa = faixa_sel

        aliquota_efetiva_federal = aliquota_efetiva

        if res.excedeu_sublimite:
            # ICMS/ISS recolhidos por fora do Simples
            # Dedução dos percentuais correspondentes na 5ª faixa de partilha
            if activity_type == "comercio":
                aliquota_efetiva_federal = aliquota_efetiva * (1.0 - 0.335)
                res.icms_fora = receita_bruta * aliquota_efetiva * 0.335
                res.icms = 0
            else: # servicos ou fator_r
                partilha_iss = 0.33 if "Anexo III" in nome_anexo else 0.265
                aliquota_efetiva_federal = aliquota_efetiva * (1.0 - partilha_iss)
                res.iss_fora = receita_bruta * aliquota_efetiva * partilha_iss
                res.iss = 0
        else:
            if activity_type == "comercio":
                res.icms = receita_bruta * aliquota_efetiva * 0.34
            else: # servicos
                res.iss = receita_bruta * aliquota_efetiva * 0.33

        res.das = receita_bruta * aliquota_efetiva_federal
        res.total_impostos = res.das + res.icms_fora + res.iss_fora
        res.receita_liquida = receita_bruta - res.total_impostos
        res.lucro_liquido = res.receita_liquida # Simplificado no Simples

        # Memória de Cálculo
        res.memoria.append(MemoriaCalculoItem(
            imposto="DAS (Guia Única Federal)",
            base_calculo=receita_bruta,
            aliquota=aliquota_efetiva_federal * 100,
            valor_debito=res.das,
            valor_credito=0,
            valor_total=res.das,
            detalhamento={
                "faturamento_12m": faturamento_anual,
                "aliquota_nominal": aliquota_nominal * 100,
                "aliquota_efetiva_total": aliquota_efetiva * 100,
                "parcela_deduzir": parcela_deduzir,
                "sublimite_excedido": res.excedeu_sublimite,
                "limite_excedido": res.excedeu_limite
            }
        ))

        if res.excedeu_sublimite:
            if res.icms_fora > 0:
                res.memoria.append(MemoriaCalculoItem(
                    imposto="ICMS (Recolhido por Fora - Sublimite)",
                    base_calculo=receita_bruta,
                    aliquota=aliquota_efetiva * 0.335 * 100,
                    valor_debito=res.icms_fora,
                    valor_credito=0,
                    valor_total=res.icms_fora,
                    detalhamento={"observacao": "Recolhimento via regime de débito e crédito normal estadual"}
                ))
            if res.iss_fora > 0:
                partilha = 0.33 if "Anexo III" in nome_anexo else 0.265
                res.memoria.append(MemoriaCalculoItem(
                    imposto="ISS (Recolhido por Fora - Sublimite)",
                    base_calculo=receita_bruta,
                    aliquota=aliquota_efetiva * partilha * 100,
                    valor_debito=res.iss_fora,
                    valor_credito=0,
                    valor_total=res.iss_fora,
                    detalhamento={"observacao": "Recolhimento direto ao município pelas regras gerais da prefeitura"}
                ))

        return res

    @classmethod
    def _calcular_presumido(cls, mes, ano, receita_bruta, custos, despesas, activity_type):
        res = ResultadoImpostos(
            regime="Lucro Presumido", mes=mes, ano=ano,
            receita_bruta=receita_bruta, custos=custos, despesas=despesas
        )

        presuncoes = {
            "servicos": {"irpj": 0.32, "csll": 0.32},
            "comercio": {"irpj": 0.08, "csll": 0.12},
            "fator_r": {"irpj": 0.32, "csll": 0.32} # Presumido fator R = serviços
        }
        pres = presuncoes.get(activity_type, presuncoes["servicos"])

        # Bases
        base_irpj = receita_bruta * pres["irpj"]
        base_csll = receita_bruta * pres["csll"]

        # IRPJ: 15% + 10% adicional mensal > R$ 20.000
        irpj_normal = base_irpj * 0.15
        irpj_adicional = (base_irpj - 20000) * 0.10 if base_irpj > 20000 else 0
        res.irpj = irpj_normal + irpj_adicional

        # CSLL: 9%
        res.csll = base_csll * 0.09

        # PIS (0.65%) e COFINS (3.0%) cumulativos
        res.pis = receita_bruta * 0.0065
        res.cofins = receita_bruta * 0.03

        if activity_type == "comercio":
            res.icms = receita_bruta * 0.12
        else:
            res.iss = receita_bruta * 0.03

        # Reforma Tributária 2026 - Transição CBS (0.9%) e IBS (0.1%) compensáveis
        res.cbs_transicao = receita_bruta * 0.009
        res.ibs_transicao = receita_bruta * 0.001
        res.total_transicao_2026 = res.cbs_transicao + res.ibs_transicao

        res.subtotal_lucro = res.irpj + res.csll
        res.total_impostos = res.irpj + res.csll + res.pis + res.cofins + res.icms + res.iss
        res.receita_liquida = receita_bruta - (res.pis + res.cofins + res.icms + res.iss)
        res.lucro_real = receita_bruta - custos - despesas - (res.pis + res.cofins + res.icms + res.iss)
        res.lucro_liquido = max(0.0, res.lucro_real - res.subtotal_lucro)

        # Memória de Cálculo
        res.memoria.extend([
            MemoriaCalculoItem("IRPJ", base_irpj, 15.0, irpj_normal, 0, res.irpj, {
                "presuncao_aliquota": pres["irpj"] * 100,
                "irpj_normal": irpj_normal,
                "irpj_adicional_10": irpj_adicional,
                "excesso_base": max(0, base_irpj - 20000)
            }),
            MemoriaCalculoItem("CSLL", base_csll, 9.0, res.csll, 0, res.csll, {
                "presuncao_aliquota": pres["csll"] * 100
            }),
            MemoriaCalculoItem("PIS", receita_bruta, 0.65, res.pis, 0, res.pis, {"regime": "cumulativo"}),
            MemoriaCalculoItem("COFINS", receita_bruta, 3.0, res.cofins, 0, res.cofins, {"regime": "cumulativo"})
        ])

        if activity_type == "comercio":
            res.memoria.append(MemoriaCalculoItem("ICMS", receita_bruta, 12.0, res.icms, 0, res.icms, {"observacao": "Estimado a 12%"}))
        else:
            res.memoria.append(MemoriaCalculoItem("ISS", receita_bruta, 3.0, res.iss, 0, res.iss, {"observacao": "Estimado a 3%"}))

        # CBS and IBS (Transition 2026 - Compensated)
        res.memoria.extend([
            MemoriaCalculoItem("CBS (Transição 2026)", receita_bruta, 0.9, res.cbs_transicao, res.cbs_transicao, 0.0, {"observacao": "Compensado no PIS/COFINS"}),
            MemoriaCalculoItem("IBS (Transição 2026)", receita_bruta, 0.1, res.ibs_transicao, res.ibs_transicao, 0.0, {"observacao": "Compensado no PIS/COFINS"})
        ])

        return res

    @classmethod
    def _calcular_real(cls, mes, ano, receita_bruta, custos, despesas, creditos_pis, creditos_cofins, icms_saida, icms_entrada, prejuizo_fiscal, activity_type):
        res = ResultadoImpostos(
            regime="Lucro Real", mes=mes, ano=ano,
            receita_bruta=receita_bruta, custos=custos, despesas=despesas
        )

        # 1. PIS/COFINS Não Cumulativos (Debito - Credito)
        res.pis = max(0.0, (receita_bruta * 0.0165) - creditos_pis)
        res.cofins = max(0.0, (receita_bruta * 0.076) - creditos_cofins)

        # ICMS ou ISS
        if activity_type == "comercio":
            res.icms = max(0.0, icms_saida - icms_entrada)
        else:
            res.iss = receita_bruta * 0.03 # Geralmente 3% sobre receita bruta

        # Reforma Tributária 2026 - Transição CBS/IBS (neutro, compensável)
        res.cbs_transicao = receita_bruta * 0.009
        res.ibs_transicao = receita_bruta * 0.001
        res.total_transicao_2026 = res.cbs_transicao + res.ibs_transicao

        # Impostos sobre faturamento
        impostos_fat = res.pis + res.cofins + res.icms + res.iss
        
        # Receita Líquida
        res.receita_liquida = receita_bruta - impostos_fat

        # Lucro líquido antes de IRPJ/CSLL (Lucro Real)
        lucro_operacional = receita_bruta - custos - despesas - impostos_fat
        res.lucro_real = max(0.0, lucro_operacional)

        # Compensação de Prejuízo Fiscal (limite de 30% do lucro operacional)
        limite_compensacao = res.lucro_real * 0.30
        res.prejuizo_compensado = min(prejuizo_fiscal, limite_compensacao)
        res.base_irpj_apos_compensacao = res.lucro_real - res.prejuizo_compensado

        if res.lucro_real > 0:
            # IRPJ: 15% + 10% adicional mensal > R$ 20.000
            irpj_normal = res.base_irpj_apos_compensacao * 0.15
            irpj_adicional = (res.base_irpj_apos_compensacao - 20000) * 0.10 if res.base_irpj_apos_compensacao > 20000 else 0
            res.irpj = irpj_normal + irpj_adicional

            # CSLL: 9% (sem compensação de prejuízo na base da CSLL no modelo simplificado, ou aplicando a mesma base)
            # Na regra real brasileira, o prejuízo fiscal compensa IRPJ (LALUR) e a Base de Cálculo Negativa da CSLL compensa na CSLL (LACS), ambos limitados a 30%.
            # Vamos aplicar a mesma compensação para CSLL para simplificar e manter consistência
            res.csll = res.base_irpj_apos_compensacao * 0.09
        else:
            res.irpj = 0
            res.csll = 0

        res.subtotal_lucro = res.irpj + res.csll
        res.total_impostos = impostos_fat + res.subtotal_lucro
        res.lucro_liquido = max(0.0, lucro_operacional - res.subtotal_lucro)

        # Memorias
        res.memoria.extend([
            MemoriaCalculoItem("PIS", receita_bruta, 1.65, receita_bruta * 0.0165, creditos_pis, res.pis, {"regime": "nao_cumulativo"}),
            MemoriaCalculoItem("COFINS", receita_bruta, 7.6, receita_bruta * 0.076, creditos_cofins, res.cofins, {"regime": "nao_cumulativo"})
        ])

        if activity_type == "comercio":
            res.memoria.append(MemoriaCalculoItem("ICMS", receita_bruta, 12.0, icms_saida, icms_entrada, res.icms, {"observacao": "Créditos por entrada"}))
        else:
            res.memoria.append(MemoriaCalculoItem("ISS", receita_bruta, 3.0, res.iss, 0, res.iss, {"observacao": "Faturamento"}))

        if res.lucro_real > 0:
            res.memoria.extend([
                MemoriaCalculoItem("IRPJ", res.base_irpj_apos_compensacao, 15.0, res.irpj, 0, res.irpj, {
                    "lucro_bruto": res.lucro_real,
                    "prejuizo_compensado": res.prejuizo_compensado,
                    "irpj_normal": res.base_irpj_apos_compensacao * 0.15,
                    "irpj_adicional_10": (res.base_irpj_apos_compensacao - 20000) * 0.10 if res.base_irpj_apos_compensacao > 20000 else 0
                }),
                MemoriaCalculoItem("CSLL", res.base_irpj_apos_compensacao, 9.0, res.csll, 0, res.csll, {
                    "lucro_bruto": res.lucro_real,
                    "prejuizo_compensado": res.prejuizo_compensado
                })
            ])
        else:
            res.memoria.extend([
                MemoriaCalculoItem("IRPJ", 0, 15.0, 0, 0, 0, {"observacao": "Sem base de cálculo (prejuízo operacional)"}),
                MemoriaCalculoItem("CSLL", 0, 9.0, 0, 0, 0, {"observacao": "Sem base de cálculo (prejuízo operacional)"})
            ])

        # CBS and IBS (Transition 2026 - Compensated)
        res.memoria.extend([
            MemoriaCalculoItem("CBS (Transição 2026)", receita_bruta, 0.9, res.cbs_transicao, res.cbs_transicao, 0.0, {"observacao": "Compensado no PIS/COFINS"}),
            MemoriaCalculoItem("IBS (Transição 2026)", receita_bruta, 0.1, res.ibs_transicao, res.ibs_transicao, 0.0, {"observacao": "Compensado no PIS/COFINS"})
        ])

        return res

    @classmethod
    def gerar_dre_html(cls, res: ResultadoImpostos) -> str:
        """Gera uma DRE estruturada em HTML premium"""
        is_lucro_real_or_presumido = res.regime in ["Lucro Presumido", "Lucro Real"]
        
        pis_cofins_segregado = f"""
            <div class="dre-row indent">
                <span>PIS</span>
                <span>R$ {res.pis:,.2f}</span>
            </div>
            <div class="dre-row indent">
                <span>COFINS</span>
                <span>R$ {res.cofins:,.2f}</span>
            </div>
        """
        
        icms_iss_segregado = ""
        if res.icms > 0 or res.regime == "Lucro Real" and res.icms == 0:
            icms_iss_segregado += f"""
                <div class="dre-row indent">
                    <span>ICMS</span>
                    <span>R$ {res.icms:,.2f}</span>
                </div>
            """
        if res.iss > 0 or res.regime == "Lucro Real" and res.iss == 0:
            icms_iss_segregado += f"""
                <div class="dre-row indent">
                    <span>ISS</span>
                    <span>R$ {res.iss:,.2f}</span>
                </div>
            """

        reforma_rows = ""
        if is_lucro_real_or_presumido:
            reforma_rows = f"""
                <div class="dre-row indent text-muted">
                    <span>CBS (Transição 2026 - Compensado)</span>
                    <span>R$ {res.cbs_transicao:,.2f}</span>
                </div>
                <div class="dre-row indent text-muted">
                    <span>IBS (Transição 2026 - Compensado)</span>
                    <span>R$ {res.ibs_transicao:,.2f}</span>
                </div>
            """
        
        impostos_fat_total = res.pis + res.cofins + res.icms + res.iss
        if res.regime == "Simples Nacional":
            pis_cofins_segregado = ""
            reforma_rows = ""
            impostos_fat_total = res.das
            icms_iss_segregado = f"""
                <div class="dre-row indent">
                    <span>DAS (Simples Guia Única)</span>
                    <span>R$ {res.das:,.2f}</span>
                </div>
            """
            if res.icms_fora > 0:
                icms_iss_segregado += f"""
                    <div class="dre-row indent warning">
                        <span>ICMS (Recolhido por Fora)</span>
                        <span>R$ {res.icms_fora:,.2f}</span>
                    </div>
                """
                impostos_fat_total += res.icms_fora
            if res.iss_fora > 0:
                icms_iss_segregado += f"""
                    <div class="dre-row indent warning">
                        <span>ISS (Recolhido por Fora)</span>
                        <span>R$ {res.iss_fora:,.2f}</span>
                    </div>
                """
                impostos_fat_total += res.iss_fora

        dre_html = f"""
        <div class="dre-container glass">
            <div class="dre-header">
                <h3>Demonstração do Resultado do Exercício (DRE)</h3>
                <span class="dre-subtitle">{res.regime} &bull; Período: {res.mes:02d}/{res.ano}</span>
            </div>
            <div class="dre-body">
                <div class="dre-row highlight">
                    <span>RECEITA BRUTA</span>
                    <span>R$ {res.receita_bruta:,.2f}</span>
                </div>
                
                <div class="dre-group">
                    <div class="dre-row sub">
                        <span>(-) Deduções e Impostos sobre Faturamento</span>
                        <span>- R$ {impostos_fat_total:,.2f}</span>
                    </div>
                    {pis_cofins_segregado}
                    {icms_iss_segregado}
                    {reforma_rows}
                </div>
                
                <div class="dre-row total">
                    <span>(=) RECEITA LÍQUIDA</span>
                    <span>R$ {res.receita_liquida:,.2f}</span>
                </div>
                
                <div class="dre-row indent">
                    <span>(-) Custos Operacionais</span>
                    <span>- R$ {res.custos:,.2f}</span>
                </div>
                <div class="dre-row indent">
                    <span>(-) Despesas Operacionais</span>
                    <span>- R$ {res.despesas:,.2f}</span>
                </div>
                
                <div class="dre-row total">
                    <span>(=) LUCRO OPERACIONAL / REAL (Base IRPJ)</span>
                    <span>R$ {res.lucro_real:,.2f}</span>
                </div>

                {"".join([
                    f'''
                    <div class="dre-group">
                        <div class="dre-row sub">
                            <span>(-) Impostos sobre o Lucro</span>
                            <span>- R$ {res.subtotal_lucro:,.2f}</span>
                        </div>
                        <div class="dre-row indent">
                            <span>IRPJ</span>
                            <span>R$ {res.irpj:,.2f}</span>
                        </div>
                        <div class="dre-row indent">
                            <span>CSLL</span>
                            <span>R$ {res.csll:,.2f}</span>
                        </div>
                    </div>
                    ''' if res.regime != "Simples Nacional" else ""
                ])}
                
                <div class="dre-row highlight final">
                    <span>(=) LUCRO LÍQUIDO DO PERÍODO</span>
                    <span>R$ {res.lucro_liquido:,.2f}</span>
                </div>
            </div>
        </div>
        """
        return dre_html
