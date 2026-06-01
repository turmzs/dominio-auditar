from flask import Blueprint, jsonify

bp = Blueprint("xml", __name__, url_prefix="/xml")


@bp.route("/importar", methods=["POST"])
def importar_xml():
    return (
        jsonify(
            {"status": "erro", "message": "Lógica de importação ainda não implementada"}
        ),
        501,
    )


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "module": "xml"}), 200
