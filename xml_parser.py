import xml.etree.ElementTree as ET
import re
import os
from datetime import datetime

def parse_xml_invoice(xml_content_or_path, company_cnpj=None):
    """
    Parses a Brazilian NF-e or NFS-e XML.
    Strips namespaces and retrieves information robustly.
    
    Args:
        xml_content_or_path: String of XML content, file path, or bytes.
        company_cnpj: CNPJ of the active company to determine if it is an Entrada or Saida.
        
    Returns:
        dict: Extracted invoice data.
    """
    try:
        # Load XML
        if isinstance(xml_content_or_path, str):
            if os.path.exists(xml_content_or_path):
                tree = ET.parse(xml_content_or_path)
                root = tree.getroot()
            else:
                # Treat as XML string
                root = ET.fromstring(xml_content_or_path)
        elif isinstance(xml_content_or_path, bytes):
            root = ET.fromstring(xml_content_or_path)
        else:
            raise ValueError("Invalid XML input format")

        # Helper to search for elements ignoring namespace
        def find_elements_by_name(element, name):
            found = []
            for el in element.iter():
                clean_tag = el.tag.split('}')[-1]
                if clean_tag == name:
                    found.append(el)
            return found

        def get_first_text(element, name, default=""):
            els = find_elements_by_name(element, name)
            if els and els[0].text:
                return els[0].text.strip()
            return default

        def clean_cnpj_cpf(val):
            if not val:
                return ""
            return re.sub(r'\D', '', val)

        # Check if NF-e (goods) or NFS-e (services)
        # NF-e typically has '<infNFe>' or '<NFe>'
        # NFS-e has '<Servico>' or '<Valores>' or '<Nfse>'
        is_nfe = len(find_elements_by_name(root, "infNFe")) > 0 or len(find_elements_by_name(root, "NFe")) > 0

        # Pre-initialize data
        data = {
            "numero": "",
            "data_emissao": "",
            "tipo": "saida", # Default
            "emitente_cnpj": "",
            "emitente_nome": "",
            "destinatario_cnpj": "",
            "destinatario_nome": "",
            "cfop": "",
            "valor_total": 0.0,
            "valor_pis": 0.0,
            "valor_cofins": 0.0,
            "valor_csll": 0.0,
            "valor_irpj": 0.0,
            "valor_iss": 0.0,
            "valor_icms": 0.0,
            "outras_retencoes": 0.0,
            "xml_origem": ""
        }

        if is_nfe:
            # --- PARSING NF-e ---
            data["numero"] = get_first_text(root, "nNF")
            
            # Data de Emissao
            dh_emi = get_first_text(root, "dhEmi")
            if not dh_emi:
                dh_emi = get_first_text(root, "dEmi")
            
            if dh_emi:
                # extract YYYY-MM-DD
                data["data_emissao"] = dh_emi[:10]
            else:
                data["data_emissao"] = datetime.now().strftime("%Y-%m-%d")

            # Emitente
            emit_el = find_elements_by_name(root, "emit")
            if emit_el:
                data["emitente_cnpj"] = clean_cnpj_cpf(get_first_text(emit_el[0], "CNPJ"))
                data["emitente_nome"] = get_first_text(emit_el[0], "xNome")

            # Destinatario
            dest_el = find_elements_by_name(root, "dest")
            if dest_el:
                cnpj = get_first_text(dest_el[0], "CNPJ")
                if not cnpj:
                    cnpj = get_first_text(dest_el[0], "CPF")
                data["destinatario_cnpj"] = clean_cnpj_cpf(cnpj)
                data["destinatario_nome"] = get_first_text(dest_el[0], "xNome")

            # CFOP (pega o primeiro CFOP que achar nas tags det)
            data["cfop"] = get_first_text(root, "CFOP")

            # Totais
            tot_el = find_elements_by_name(root, "ICMSTot")
            if tot_el:
                data["valor_total"] = float(get_first_text(tot_el[0], "vNF", "0"))
                data["valor_icms"] = float(get_first_text(tot_el[0], "vICMS", "0"))
                data["valor_pis"] = float(get_first_text(tot_el[0], "vPIS", "0"))
                data["valor_cofins"] = float(get_first_text(tot_el[0], "vCOFINS", "0"))
                # NF-e normally does not have IRPJ/CSLL directly in the main totals unless retained (ex: vIR, vCSLL)
                # But it can have retentions under '<retTrib>'
                ret_trib = find_elements_by_name(root, "retTrib")
                if ret_trib:
                    data["valor_pis"] = float(get_first_text(ret_trib[0], "vRetPIS", str(data["valor_pis"])))
                    data["valor_cofins"] = float(get_first_text(ret_trib[0], "vRetCOFINS", str(data["valor_cofins"])))
                    data["valor_csll"] = float(get_first_text(ret_trib[0], "vCSLL", "0"))
                    data["valor_irpj"] = float(get_first_text(ret_trib[0], "vIRRF", "0"))

        else:
            # --- PARSING NFS-e ---
            data["numero"] = get_first_text(root, "Numero")
            if not data["numero"]:
                data["numero"] = get_first_text(root, "nNF") # fallback
                
            data_emi = get_first_text(root, "DataEmissao")
            if not data_emi:
                data_emi = get_first_text(root, "dhEmi")
            if data_emi:
                data["data_emissao"] = data_emi[:10]
            else:
                data["data_emissao"] = datetime.now().strftime("%Y-%m-%d")

            # Prestador (Emitente na nota de serviço)
            prestador_el = find_elements_by_name(root, "PrestadorServico")
            if not prestador_el:
                prestador_el = find_elements_by_name(root, "IdentificacaoPrestador")
            if not prestador_el:
                prestador_el = find_elements_by_name(root, "emit")
                
            if prestador_el:
                cnpj = get_first_text(prestador_el[0], "CNPJ")
                data["emitente_cnpj"] = clean_cnpj_cpf(cnpj)
                data["emitente_nome"] = get_first_text(prestador_el[0], "RazaoSocial")
                if not data["emitente_nome"]:
                    data["emitente_nome"] = get_first_text(prestador_el[0], "xNome")

            # Tomador (Destinatário na nota de serviço)
            tomador_el = find_elements_by_name(root, "TomadorServico")
            if not tomador_el:
                tomador_el = find_elements_by_name(root, "IdentificacaoTomador")
            if not tomador_el:
                tomador_el = find_elements_by_name(root, "dest")
                
            if tomador_el:
                cnpj = get_first_text(tomador_el[0], "CNPJ")
                if not cnpj:
                    cnpj = get_first_text(tomador_el[0], "CPF")
                data["destinatario_cnpj"] = clean_cnpj_cpf(cnpj)
                data["destinatario_nome"] = get_first_text(tomador_el[0], "RazaoSocial")
                if not data["destinatario_nome"]:
                    data["destinatario_nome"] = get_first_text(tomador_el[0], "xNome")

            # Valores do Serviço
            val_el = find_elements_by_name(root, "Valores")
            if not val_el:
                val_el = find_elements_by_name(root, "valores")
                
            if val_el:
                data["valor_total"] = float(get_first_text(val_el[0], "ValorServicos", "0"))
                if data["valor_total"] == 0:
                    data["valor_total"] = float(get_first_text(val_el[0], "vServ", "0"))
                
                data["valor_iss"] = float(get_first_text(val_el[0], "ValorIss", "0"))
                if data["valor_iss"] == 0:
                    data["valor_iss"] = float(get_first_text(val_el[0], "vISS", "0"))
                    
                data["valor_pis"] = float(get_first_text(val_el[0], "ValorPis", "0"))
                if data["valor_pis"] == 0:
                    data["valor_pis"] = float(get_first_text(val_el[0], "vPIS", "0"))
                    
                data["valor_cofins"] = float(get_first_text(val_el[0], "ValorCofins", "0"))
                if data["valor_cofins"] == 0:
                    data["valor_cofins"] = float(get_first_text(val_el[0], "vCOFINS", "0"))
                    
                data["valor_csll"] = float(get_first_text(val_el[0], "ValorCsll", "0"))
                if data["valor_csll"] == 0:
                    data["valor_csll"] = float(get_first_text(val_el[0], "vCSLL", "0"))
                    
                data["valor_irpj"] = float(get_first_text(val_el[0], "ValorIr", "0"))
                if data["valor_irpj"] == 0:
                    # check for vIR or vIRRF
                    data["valor_irpj"] = float(get_first_text(val_el[0], "vIR", "0"))
                    
                data["outras_retencoes"] = float(get_first_text(val_el[0], "OutrasRetencoes", "0"))
                if data["outras_retencoes"] == 0:
                    # check for vOutrasRetencoes (standard Auditar fix: 3.65% or OutrasRetencoes)
                    data["outras_retencoes"] = float(get_first_text(val_el[0], "vOutrasRetencoes", "0"))
            
            # Default service CFOP is usually 5933 (prestação de serviço dentro do estado) or similar
            data["cfop"] = get_first_text(root, "CFOP", "5933")

        # Determine if invoice is Entrada or Saida based on active company CNPJ
        if company_cnpj:
            clean_company = clean_cnpj_cpf(company_cnpj)
            if clean_company:
                if clean_cnpj_cpf(data["destinatario_cnpj"]) == clean_company:
                    data["tipo"] = "entrada"
                elif clean_cnpj_cpf(data["emitente_cnpj"]) == clean_company:
                    data["tipo"] = "saida"

        # Format CNPJs with standard mask for cleaner displaying
        def format_cnpj_cpf(val):
            val = clean_cnpj_cpf(val)
            if len(val) == 14:
                return f"{val[:2]}.{val[2:5]}.{val[5:8]}/{val[8:12]}-{val[12:]}"
            elif len(val) == 11:
                return f"{val[:3]}.{val[3:6]}.{val[6:9]}-{val[9:]}"
            return val

        data["emitente_cnpj"] = format_cnpj_cpf(data["emitente_cnpj"])
        data["destinatario_cnpj"] = format_cnpj_cpf(data["destinatario_cnpj"])

        return data

    except Exception as e:
        print(f"Erro ao analisar XML: {e}")
        return None
