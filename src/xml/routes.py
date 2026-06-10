from flask import Blueprint, jsonify, request

from importer_service import FiscalImporter

import tempfile
from pathlib import Path

bp = Blueprint("xml", __name__, url_prefix="/xml")


@bp.route("/importar", methods=["POST"])
def importar_xml():
    try:
        # Parâmetros para a interface
        tipo_movimento = request.form.get("tipo_movimento")  # 'entrada', 'saida', 'servico' (opcional)
        origem = request.form.get("origem")  # 'local', 'sieg', 'sefaz'
        if not origem:
            origem = "local"

        files = request.files.getlist("files") or (
            [request.files["file"]] if "file" in request.files else []
        )

        if not files and origem == "local":
            return (
                jsonify(
                    {
                        "status": "erro",
                        "message": "Nenhum arquivo enviado para importação local",
                    }
                ),
                400,
            )

        company_id = request.form.get("empresa_id") or request.args.get("empresa_id")
        if not company_id:
            try:
                from src.models.base import Company
                from src.database.session import get_session

                session = get_session()
                company = session.query(Company).first()
                company_id = str(getattr(company, "id", "") or "")
            except Exception:
                company_id = None

        if not company_id:
            return (
                jsonify({"status": "erro", "message": "Parâmetro empresa_id é obrigatório"}),
                400,
            )

        company_id_int = int(company_id)
        results = []

        from motor_fiscal.engine.executor import FiscalExecutor
        executor = FiscalExecutor()
        importer = FiscalImporter(company_id=company_id_int)

        if origem == "local":
            for file in files:
                try:
                    suffix = Path(file.filename or "xml").suffix or ".xml"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        file.save(tmp.name)
                        tmp_path = tmp.name

                    import_result = importer.import_xml(tmp_path)

                    try:
                        Path(tmp_path).unlink(missing_ok=True)
                    except Exception:
                        pass

                    if import_result.get("status") == "success":
                        movement_id = import_result.get("movement_id")
                        alert_count = executor.processar_movimento(movement_id)

                        results.append(
                            {
                                "filename": file.filename,
                                "status": "sucesso",
                                "movement_id": movement_id,
                                "alerts": alert_count,
                                "duplicate": bool(import_result.get("duplicate")),
                            }
                        )
                    else:
                        results.append(
                            {
                                "filename": file.filename,
                                "status": "erro",
                                "message": import_result.get(
                                    "message", "Falha ao processar XML"
                                ),
                            }
                        )
                except Exception as e:
                    results.append(
                        {
                            "filename": getattr(file, "filename", None),
                            "status": "erro",
                            "message": str(e),
                        }
                    )

        elif origem == "sieg":
            return (
                jsonify(
                    {
                        "status": "aviso",
                        "message": "Integração SIEG em desenvolvimento",
                    }
                ),
                501,
            )
        elif origem == "sefaz":
            return (
                jsonify(
                    {
                        "status": "aviso",
                        "message": "Integração SEFAZ em desenvolvimento",
                    }
                ),
                501,
            )
        else:
            return (
                jsonify(
                    {
                        "status": "erro",
                        "message": "Origem de importação inválida",
                    }
                ),
                400,
            )

        success_count = sum(1 for r in results if r.get("status") == "sucesso")

        return (
            jsonify(
                {
                    "status": "concluido",
                    "total_arquivos": len(files) if origem == "local" else 0,
                    "sucessos": success_count,
                    "erros": len(results) - success_count,
                    "detalhes": results,
                    "tipo_movimento": tipo_movimento,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"status": "erro", "message": str(e)}), 500


@bp.route("/tipos", methods=["GET"])
def listar_tipos_suportados():
    from src.xml.parsers.registry import supported_document_types
    return jsonify(supported_document_types()), 200


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "xml"}), 200

