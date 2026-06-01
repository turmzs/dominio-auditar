from __future__ import annotations

from flask import Blueprint, jsonify
import importlib
import pkgutil
import pathlib

# Importamos para preencher a lista global
from architecture import ARCHITECTURE
from .registry import get_module_meta, LOADED_MODULES

modules_bp = Blueprint("modules_api", __name__, url_prefix="/api")


@modules_bp.route("/modules/<module_id>/status", methods=["GET"])
def module_status(module_id: str):
    meta = get_module_meta(module_id=module_id, architecture=ARCHITECTURE)
    if not meta:
        return jsonify({"error": "Módulo não encontrado", "module_id": module_id}), 404

    return jsonify(
        {
            "module_id": meta.module_id,
            "label": meta.label,
            "route": meta.route,
            "etapa": meta.etapa,
            "status": meta.status,
            "description": meta.description,
        }
    )


@modules_bp.route("/architecture", methods=["GET"])
def get_architecture():
    """Retorna a lista de todos os módulos carregados para o frontend"""
    # Lógica de varredura movida para cá para evitar o erro de Syntax do registry.py
    base_path = pathlib.Path(__file__).resolve().parent.parent
    for loader, module_name, is_pkg in pkgutil.walk_packages(
        [str(base_path)], prefix=base_path.name + "."
    ):
        try:
            mod = importlib.import_module(module_name)
            bp = getattr(mod, "bp", None)
            if bp:
                parts = module_name.split(".")
                prefix = "/" + parts[-1]
                LOADED_MODULES.append(
                    {"id": module_name, "name": parts[-1], "url": prefix + "/ping"}
                )
        except:
            pass
    return jsonify({"status": "success", "modules": LOADED_MODULES}), 200
