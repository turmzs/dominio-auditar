"""
Calculadora de Impostos Brasileiros
Implementa cálculos para Simples Nacional, Lucro Presumido e Lucro Real
"""


class CalculadoraImpostos:
    """Calculadora de impostos para diferentes regimes tributários"""

    # Tabelas do Simples Nacional 2024
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

    @staticmethod
    def calcular_simples_nacional(
        receita_bruta, faturamento_anual=0, tipo_atividade="comercio", **kwargs
    ):
        """
        Calcula impostos pelo Simples Nacional
        Baseado nas alíquotas da tabela 2024 com parcela a deduzir
        E regras de sublimite do ICMS/ISS de R$ 3,6 milhões e limite geral de R$ 4,8 milhões.

        Args:
            receita_bruta: Receita bruta mensal
            faturamento_anual: Faturamento acumulado no ano (para definir a alíquota)
            tipo_atividade: 'comercio' (Anexo I), 'servicos' (Anexo III) ou 'fator_r' (Anexo III se payroll >= 28%, else V)
            folha_salarios_anual: Folha de salários acumulada 12 meses (para Fator R)

        Returns:
            dict: Detalhamento dos impostos
        """
        # Se faturamento_anual não fornecido, estimar com base na receita mensal
        if faturamento_anual == 0:
            faturamento_anual = receita_bruta * 12

        # Escolher a tabela correta baseada no tipo de atividade e Fator R
        nome_anexo = "I"
        if tipo_atividade == "comercio":
            tabela = CalculadoraImpostos.TABELA_ANEXO_I_COMERCIO
            nome_anexo = "I"
        elif tipo_atividade == "servicos":
            tabela = CalculadoraImpostos.TABELA_ANEXO_III_SERVICOS
            nome_anexo = "III"
        elif tipo_atividade == "fator_r":
            # Lógica Fator R: Folha / Faturamento >= 28% -> Anexo III, senão Anexo V
            folha_12 = kwargs.get("folha_salarios_anual", 0)
            faturamento_12 = faturamento_anual
            fator_r = (folha_12 / faturamento_12) if faturamento_12 > 0 else 0

            if fator_r >= 0.28:
                tabela = CalculadoraImpostos.TABELA_ANEXO_III_SERVICOS
                nome_anexo = "III (Fator R >= 28%)"
            else:
                tabela = CalculadoraImpostos.TABELA_ANEXO_V_SERVICOS
                nome_anexo = "V (Fator R < 28%)"
        else:
            tabela = CalculadoraImpostos.TABELA_ANEXO_III_SERVICOS
            nome_anexo = "III"

        # Encontrar a faixa correta
        faixa_encontrada = None
        num_faixa = 0
        for num, dados in tabela.items():
            if faturamento_anual <= dados["faixa_anual"]:
                faixa_encontrada = dados
                num_faixa = num
                break

        # Se a receita for muito alta (última faixa), pega a última faixa
        if faixa_encontrada is None:
            faixa_encontrada = list(tabela.values())[-1]
            num_faixa = list(tabela.keys())[-1]

        # === FÓRMULA OFICIAL DA RECEITA FEDERAL ===
        # Alíquota Efetiva = (RBT12 × Alíquota Nominal - Parcela a Deduzir) / RBT12
        aliquota = faixa_encontrada["aliquota"]
        parcela_deduzir = faixa_encontrada["parcela_deduzir"]

        # Calcula a alíquota efetiva total sobre o RBT12
        aliquota_efetiva = (
            faturamento_anual * aliquota - parcela_deduzir
        ) / faturamento_anual
        aliquota_efetiva = max(0, aliquota_efetiva)  # Nunca negativa

        # Regras de Sublimite (R$ 3.600.000,00) e Limite Geral (R$ 4.800.000,00)
        excedeu_sublimite = faturamento_anual > 3_600_000.00
        excedeu_limite = faturamento_anual > 4_800_000.00

        icms_estimado_fora = 0
        iss_estimado_fora = 0

        if excedeu_sublimite:
            # Se ultrapassar o sublimite, ICMS/ISS são recolhidos por fora do DAS.
            # Deduz-se a repartição do ICMS/ISS correspondente à faixa limite (5ª faixa) da alíquota efetiva.
            # No Anexo I, a partilha do ICMS na 5ª faixa é 33,50%
            # No Anexo III, a partilha do ISS na 5ª faixa é 33,00%
            # No Anexo V, a partilha do ISS na 5ª faixa é 26,50%
            if tipo_atividade == "comercio":
                aliquota_efetiva_federal = aliquota_efetiva * (1.0 - 0.335)
                icms_estimado_fora = receita_bruta * aliquota_efetiva * 0.335
                icms_estimado = 0
                iss = 0
            elif tipo_atividade == "servicos":
                aliquota_efetiva_federal = aliquota_efetiva * (1.0 - 0.33)
                iss_estimado_fora = receita_bruta * aliquota_efetiva * 0.33
                icms_estimado = 0
                iss = 0
            elif tipo_atividade == "fator_r":
                folha_12 = kwargs.get("folha_salarios_anual", 0)
                faturamento_12 = faturamento_anual
                fator_r = (folha_12 / faturamento_12) if faturamento_12 > 0 else 0
                if fator_r >= 0.28:
                    aliquota_efetiva_federal = aliquota_efetiva * (1.0 - 0.33)
                    iss_estimado_fora = receita_bruta * aliquota_efetiva * 0.33
                else:
                    aliquota_efetiva_federal = aliquota_efetiva * (1.0 - 0.265)
                    iss_estimado_fora = receita_bruta * aliquota_efetiva * 0.265
                icms_estimado = 0
                iss = 0
            else:
                aliquota_efetiva_federal = aliquota_efetiva * (1.0 - 0.33)
                iss_estimado_fora = receita_bruta * aliquota_efetiva * 0.33
                icms_estimado = 0
                iss = 0
        else:
            aliquota_efetiva_federal = aliquota_efetiva
            if tipo_atividade == "comercio":
                icms_estimado = receita_bruta * aliquota_efetiva * 0.34
                iss = 0
            else:
                iss = receita_bruta * aliquota_efetiva * 0.33
                icms_estimado = 0

        # DAS Mensal (Apenas a parte que vai na guia única)
        valor_das = receita_bruta * aliquota_efetiva_federal
        # Carga tributária total considera o DAS + impostos recolhidos por fora
        total_impostos = valor_das + icms_estimado_fora + iss_estimado_fora

        descricao = (
            f"Anexo {nome_anexo} | Faixa {num_faixa} | "
            f"Alíq. Nominal: {aliquota * 100:.2f}% | "
            f"Alíq. Efetiva DAS: {aliquota_efetiva_federal * 100:.2f}%"
        )
        if excedeu_sublimite:
            descricao += " (ICMS/ISS recolhidos por fora)"
        if excedeu_limite:
            descricao += " ⚠️ EXCEDEU LIMITE GERAL 4.8M"

        return {
            "regime": "Simples Nacional",
            "anexo": nome_anexo,
            "faixa": num_faixa,
            "faturamento_anual": faturamento_anual,
            "aliquota_nominal": aliquota * 100,
            "aliquota_efetiva": aliquota_efetiva * 100,
            "aliquota_efetiva_federal": aliquota_efetiva_federal * 100,
            "parcela_deduzir_anual": parcela_deduzir,
            "das": valor_das,
            "iss": iss,
            "icms": icms_estimado,
            "iss_fora": iss_estimado_fora,
            "icms_fora": icms_estimado_fora,
            "excedeu_sublimite": excedeu_sublimite,
            "excedeu_limite": excedeu_limite,
            "total_impostos": total_impostos,
            "descricao": descricao,
        }

    @staticmethod
    def calcular_lucro_presumido(receita_bruta, tipo_atividade="servicos"):
        """
        Calcula impostos pelo Lucro Presumido
        Baseado nas regras da Receita Federal

        Args:
            receita_bruta: Receita bruta mensal
            tipo_atividade: 'servicos', 'comercio', 'industria' ou 'transporte'

        Returns:
            dict: Detalhamento dos impostos
        """
        # Definir percentuais de presunção por tipo de atividade
        presuncoes = {
            "servicos": {"irpj": 0.32, "csll": 0.32},  # Serviços
            "comercio": {"irpj": 0.08, "csll": 0.12},  # Comércio
            "industria": {"irpj": 0.08, "csll": 0.12},  # Indústria
            "transporte": {"irpj": 0.16, "csll": 0.16},  # Transporte
        }

        pres = presuncoes.get(tipo_atividade, presuncoes["servicos"])

        # Calcular bases de cálculo
        base_irpj = receita_bruta * pres["irpj"]
        base_csll = receita_bruta * pres["csll"]

        # Calcular IRPJ: 15% sobre a base
        irpj = base_irpj * 0.15
        # Adicional de IRPJ (10% sobre o excedente de R$ 20.000 MENSAL na base de cálculo)
        if base_irpj > 20000:
            irpj += (base_irpj - 20000) * 0.10

        # Calcular CSLL: 9% sobre a base
        csll = base_csll * 0.09

        # PIS: 0,65% sobre receita bruta
        pis = receita_bruta * 0.0065

        # COFINS: 3% sobre receita bruta
        cofins = receita_bruta * 0.03

        # ISS (para serviços) - geralmente 2-5% - informativo, não entra no total federal
        if tipo_atividade == "servicos":
            iss = receita_bruta * 0.03
            icms = 0
        else:
            iss = 0
            # ICMS varia por estado (4-18%), usando média 12% - informativo
            icms = receita_bruta * 0.12

        # Total de impostos federais (IRPJ + CSLL + PIS + COFINS) - conforme expectativa do usuário
        total_impostos = irpj + csll + pis + cofins

        # Reforma Tributária 2026 (Transição - CBS 0.9% e IBS 0.1%)
        cbs_transicao = receita_bruta * 0.009
        ibs_transicao = receita_bruta * 0.001
        total_transicao_2026 = cbs_transicao + ibs_transicao

        return {
            "regime": "Lucro Presumido",
            "tipo_atividade": tipo_atividade,
            "presuncao_irpj": pres["irpj"] * 100,
            "presuncao_csll": pres["csll"] * 100,
            "base_irpj": base_irpj,
            "base_csll": base_csll,
            "irpj": irpj,
            "csll": csll,
            "pis": pis,
            "cofins": cofins,
            "pis_cofins": pis + cofins,
            "iss": iss,
            "icms": icms,
            "cbs_transicao": cbs_transicao,
            "ibs_transicao": ibs_transicao,
            "total_transicao_2026": total_transicao_2026,
            "total_impostos": total_impostos,
            "descricao": f'Presunção IRPJ: {pres["irpj"]*100:.0f}% | CSLL: {pres["csll"]*100:.0f}% | Transição 2026: CBS/IBS 1% compensado',
        }

    @staticmethod
    def calcular_lucro_real(receita_bruta, custos, despesas, creditos=0, iss_rate=0.03, icms_rate=0.12):
        """
        Calcula impostos pelo Lucro Real
        Baseado nas regras da Receita Federal
        """
        # Calcular o lucro líquido (base de cálculo)
        lucro_liquido = receita_bruta - custos - despesas

        # Se prejuízo, a base é zero para cálculo
        base_calculo = max(0, lucro_liquido)

        # Calcular IRPJ: 15% sobre a base + adicional de 10% s/ excedente de 20k
        irpj = base_calculo * 0.15
        if base_calculo > 20000:
            irpj += (base_calculo - 20000) * 0.10

        # Calcular CSLL: 9% sobre a base
        csll = base_calculo * 0.09

        # PIS/COFINS Não-Cumulativo (1,65% e 7,6%)
        pis_debito = receita_bruta * 0.0165
        cofins_debito = receita_bruta * 0.076

        # 'creditos' is expected to be a monetary amount (R$) representing eligible credits.
        # Subtract monetary credits directly from debits (do NOT multiply by the rate again).
        pis_credito = creditos
        cofins_credito = creditos

        pis_final = max(0, pis_debito - pis_credito)
        cofins_final = max(0, cofins_debito - cofins_credito)

        # ISS/ICMS (Informativo) - use configurable rates (defaults: ISS 3%, ICMS 12%)
        iss = receita_bruta * iss_rate
        # ICMS default is computed as a straight percentage of revenue; if revenues are ICMS-included, callers should pre-adjust.
        icms = receita_bruta * icms_rate

        impostos_sobre_lucro = irpj + csll
        impostos_sobre_faturamento = pis_final + cofins_final
        total_impostos = impostos_sobre_lucro + impostos_sobre_faturamento

        # Reforma Tributária 2026 (Transição - CBS 0.9% e IBS 0.1%)
        cbs_transicao = receita_bruta * 0.009
        ibs_transicao = receita_bruta * 0.001
        total_transicao_2026 = cbs_transicao + ibs_transicao

        return {
            "regime": "Lucro Real",
            "lucro_liquido": lucro_liquido,
            "base_calculo": base_calculo,
            "irpj": irpj,
            "csll": csll,
            "pis": pis_final,
            "cofins": cofins_final,
            "pis_debito": pis_debito,
            "pis_credito": pis_credito,
            "cofins_debito": cofins_debito,
            "cofins_credito": cofins_credito,
            "iss": iss,
            "icms": icms,
            "cbs_transicao": cbs_transicao,
            "ibs_transicao": ibs_transicao,
            "total_transicao_2026": total_transicao_2026,
            "impostos_sobre_lucro": impostos_sobre_lucro,
            "impostos_sobre_faturamento": impostos_sobre_faturamento,
            "total_impostos": total_impostos,
            "descricao": f"Lucro: R$ {lucro_liquido:,.2f} | Créditos: R$ {creditos:,.2f} | Transição 2026: CBS/IBS 1% compensado",
        }

    @staticmethod
    def calcular_lucro_presumido_trimestral(
        receita_bruta_trimestral, tipo_atividade="servicos"
    ):
        """
        Calcula os impostos federais do Lucro Presumido para um trimestre.

        Args:
            receita_bruta_trimestral: Soma da receita dos 3 meses do trimestre
            tipo_atividade: 'servicos', 'comercio', 'industria' ou 'transporte'

        Returns:
            dict: Dicionário com os valores detalhados dos impostos trimestrais
        """
        # Define as alíquotas de presunção
        presuncoes = {
            "servicos": {"irpj": 0.32, "csll": 0.32},
            "comercio": {"irpj": 0.08, "csll": 0.12},
            "industria": {"irpj": 0.08, "csll": 0.12},
            "transporte": {"irpj": 0.16, "csll": 0.16},
        }

        pres = presuncoes.get(tipo_atividade, presuncoes["servicos"])

        # Calcula as BASES DE CÁLCULO trimestrais
        base_irpj_trimestral = receita_bruta_trimestral * pres["irpj"]
        base_csll_trimestral = receita_bruta_trimestral * pres["csll"]

        # Calcula o IRPJ (com adicional TRIMESTRAL - R$ 60.000)
        irpj_normal = base_irpj_trimestral * 0.15
        if base_irpj_trimestral > 60000:  # Limite TRIMESTRAL
            excesso = base_irpj_trimestral - 60000
            irpj_adicional = excesso * 0.10
            irpj_total = irpj_normal + irpj_adicional
        else:
            irpj_total = irpj_normal
            irpj_adicional = 0

        # Calcula os outros impostos
        csll_total = base_csll_trimestral * 0.09
        pis_total = receita_bruta_trimestral * 0.0065
        cofins_total = receita_bruta_trimestral * 0.03

        # ISS (para serviços) - informativo, não entra no total federal
        if tipo_atividade == "servicos":
            iss_total = receita_bruta_trimestral * 0.03
            icms_total = 0
        else:
            iss_total = 0
            icms_total = receita_bruta_trimestral * 0.12

        # Soma tudo
        total_impostos = irpj_total + csll_total + pis_total + cofins_total

        # Retorna todos os valores
        return {
            "regime": "Lucro Presumido Trimestral",
            "tipo_atividade": tipo_atividade,
            "receita_bruta_trimestral": round(receita_bruta_trimestral, 2),
            "presuncao_irpj": pres["irpj"] * 100,
            "presuncao_csll": pres["csll"] * 100,
            "base_irpj_trimestral": round(base_irpj_trimestral, 2),
            "base_csll_trimestral": round(base_csll_trimestral, 2),
            "irpj_normal": round(irpj_normal, 2),
            "irpj_adicional": round(irpj_adicional, 2),
            "irpj_total": round(irpj_total, 2),
            "csll_total": round(csll_total, 2),
            "pis_total": round(pis_total, 2),
            "cofins_total": round(cofins_total, 2),
            "iss_total": round(iss_total, 2),
            "icms_total": round(icms_total, 2),
            "total_impostos_trimestral": round(total_impostos, 2),
            "media_mensal_impostos": round(total_impostos / 3, 2),
            "descricao": f'Presunção IRPJ: {pres["irpj"]*100:.0f}% | CSLL: {pres["csll"]*100:.0f}%',
        }

    @staticmethod
    def calcular_lucro_real_trimestral(dados_trimestre):
        """
        Calcula impostos do Lucro Real para um trimestre consolidado.
        """
        receita_total = sum(d["receita"] for d in dados_trimestre)
        custos_total = sum(d["custos"] for d in dados_trimestre)
        despesas_total = sum(d["despesas"] for d in dados_trimestre)
        creditos_total = sum(d["creditos"] for d in dados_trimestre)

        lucro_antes_impostos = receita_total - custos_total - despesas_total
        base_calculo = max(0, lucro_antes_impostos)

        irpj_normal = base_calculo * 0.15
        irpj_adicional = 0
        if base_calculo > 60000:
            irpj_adicional = (base_calculo - 60000) * 0.10
        irpj_total = irpj_normal + irpj_adicional

        csll_total = base_calculo * 0.09
        pis_final = max(0, (receita_total - creditos_total) * 0.0165)
        cofins_final = max(0, (receita_total - creditos_total) * 0.076)

        total_federais = irpj_total + csll_total + pis_final + cofins_final

        return {
            "receita_total": receita_total,
            "custos_total": custos_total,
            "despesas_total": despesas_total,
            "lucro_trimestral": lucro_antes_impostos,
            "base_calculo": base_calculo,
            "irpj_normal": irpj_normal,
            "irpj_adicional": irpj_adicional,
            "irpj_total": irpj_total,
            "csll_total": csll_total,
            "pis_total": pis_final,
            "cofins_total": cofins_final,
            "total_impostos_trimestral": total_federais,
            "media_mensal_impostos": total_federais / 3,
        }

    @staticmethod
    def calcular_impostos(
        receita_bruta,
        regime,
        custos=0,
        despesas=0,
        faturamento_anual=0,
        tipo_atividade="comercio",
    ):
        """
        Calcula impostos baseado no regime tributário

        Args:
            receita_bruta: Receita bruta mensal
            regime: 'simples', 'presumido' ou 'real'
            custos: Total de custos (para lucro real)
            despesas: Total de despesas (para lucro real)
            faturamento_anual: Faturamento acumulado (para simples)
            tipo_atividade: 'comercio' ou 'servicos' (para simples e presumido)

        Returns:
            dict: Detalhamento dos impostos
        """
        if regime == "simples":
            return CalculadoraImpostos.calcular_simples_nacional(
                receita_bruta, faturamento_anual, tipo_atividade
            )
        elif regime == "presumido":
            return CalculadoraImpostos.calcular_lucro_presumido(
                receita_bruta, tipo_atividade
            )
        elif regime == "real":
            return CalculadoraImpostos.calcular_lucro_real(
                receita_bruta, custos, despesas
            )
        else:
            raise ValueError(f"Regime tributário inválido: {regime}")


# Função auxiliar para uso rápido
def calcular_impostos_auto(receita_bruta, regime, **kwargs):
    """Função de conveniência para calcular impostos"""
    calc = CalculadoraImpostos()
    return calc.calcular_impostos(receita_bruta, regime, **kwargs)
