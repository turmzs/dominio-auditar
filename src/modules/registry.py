"""Registry de módulos para o menu -> backend.

A ideia é mapear module_id (ex.: 'clientes', 'nfe', 'entradas') para
informações de status/etapa e (futuramente) handlers/blueprints.

Por enquanto, retornamos placeholder consistente e habilitamos expansão.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import importlib
import pkgutil
import pathlib


@dataclass(frozen=True)
class ModuleMeta:
    module_id: str
    label: str
    route: str | None
    etapa: Optional[int]
    status: str = "em_desenvolvimento"  # em_desenvolvimento | pronto
    description: str = ""
    # payload extra reservado para o futuro
    extra: Optional[Dict[str, Any]] = None


# Registry base: por enquanto preenchido em runtime a partir de architecture.py.
# Mantemos uma estrutura aqui para caso queira overrides.
_OVERRIDE: Dict[str, ModuleMeta] = {}


def make_registry_from_architecture(architecture: Dict[str, Any]) -> Dict[str, ModuleMeta]:
    """Gera registry a partir de ARCHITECTURE do architecture.py."""
    registry: Dict[str, ModuleMeta] = {}

    def upsert(module_id: str, label: str, route: str | None, etapa: Optional[int]):
        if not module_id:
            return
        # Override tem precedência
        if module_id in _OVERRIDE:
            registry[module_id] = _OVERRIDE[module_id]
            return
        registry[module_id] = ModuleMeta(
            module_id=module_id,
            label=label,
            route=route,
            etapa=etapa,
        )

    for area_key, area in architecture.items():
        etapa = area.get("etapa")
        for m in area.get("modules", []):
            mid = m.get("id")
            label = m.get("label")
            route = m.get("route")
            upsert(mid, label, route, etapa)

            for sub in m.get("submodules", []) or []:
                smid = sub.get("id")
                slabel = sub.get("label")
                sroute = sub.get("route")
                upsert(smid, slabel, sroute, etapa)

                for item in sub.get("items", []) or []:
                    iid = item.get("id")
                    ilabel = item.get("label")
                    iroute = item.get("route")
                    upsert(iid, ilabel, iroute, etapa)

    return registry


def get_module_meta(module_id: str, architecture: Dict[str, Any]) -> Optional[ModuleMeta]:
    reg = make_registry_from_architecture(architecture)
    return reg.get(module_id)


# Armazenamos os módulos carregados para a API de arquitetura
LOADED_MODULES = []

def get_module_meta(module_name):
    """Função de compatibilidade para evitar erros no app.py"""
    return {"name": module_name, "status": "active"}


def _register_module_blueprint(app, module_name: str, bp) -> str:
    """Registra blueprint respeitando url_prefix já definido no módulo."""
    parts = module_name.split('.')
    inferred = '/' + (parts[-1] if len(parts) < 3 else '/'.join(parts[1:-1]))
    existing = (bp.url_prefix or '').strip()
    if existing:
        if not existing.startswith('/'):
            existing = '/' + existing
        app.register_blueprint(bp)
        url_base = existing
    else:
        app.register_blueprint(bp, url_prefix=inferred)
        url_base = inferred

    LOADED_MODULES.append({
        'id': module_name,
        'name': parts[-1].replace('_', ' ').title(),
        'url': url_base + '/ping',
    })
    return url_base


def load_all_routes(app):
    """Registra automaticamente todos os Blueprints encontrados em src/ e motor_fiscal/."""
    # 1. Registrar a API de Arquitetura primeiro
    try:
        from src.modules.routes import modules_bp
        app.register_blueprint(modules_bp)
        print('[Registry] API de Arquitetura registrada!')
    except Exception as e:
        print(f'[Registry] Erro ao registrar API: {e}')

    # 2. Varredura de pacotes com blueprints
    project_root = pathlib.Path(__file__).resolve().parent.parent.parent
    scan_roots = [
        (project_root / 'src', 'src'),
        (project_root / 'motor_fiscal', 'motor_fiscal'),
    ]

    for base_path, prefix_name in scan_roots:
        if not base_path.is_dir():
            continue
        for loader, module_name, is_pkg in pkgutil.walk_packages(
            [str(base_path)], prefix=prefix_name + '.'
        ):
            try:
                mod = importlib.import_module(module_name)
                bp = getattr(mod, 'bp', None)
                if bp:
                    _register_module_blueprint(app, module_name, bp)
                    print(f'[Registry] Registrado: {module_name}')
            except Exception as e:
                print(f'[Registry] Erro no modulo {module_name}: {e}')


