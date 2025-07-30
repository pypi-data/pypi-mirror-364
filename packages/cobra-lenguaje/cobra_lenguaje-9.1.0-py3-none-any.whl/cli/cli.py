import argparse
import logging
import os
import sys

from backend.src.cli.commands.agix_cmd import AgixCommand
from backend.src.cli.commands.bench_cmd import BenchCommand

from backend.src.cli.commands.bench_transpilers_cmd import BenchTranspilersCommand
from backend.src.cli.commands.benchmarks2_cmd import BenchmarksV2Command
from backend.src.cli.commands.benchmarks_cmd import BenchmarksCommand

from backend.src.cli.commands.cache_cmd import CacheCommand
from backend.src.cli.commands.compile_cmd import CompileCommand
from backend.src.cli.commands.container_cmd import ContainerCommand
from backend.src.cli.commands.crear_cmd import CrearCommand
from backend.src.cli.commands.dependencias_cmd import DependenciasCommand
from backend.src.cli.commands.docs_cmd import DocsCommand
from backend.src.cli.commands.empaquetar_cmd import EmpaquetarCommand
from backend.src.cli.commands.execute_cmd import ExecuteCommand
from backend.src.cli.commands.flet_cmd import FletCommand
from backend.src.cli.commands.init_cmd import InitCommand
from backend.src.cli.commands.interactive_cmd import InteractiveCommand
from backend.src.cli.commands.jupyter_cmd import JupyterCommand
from backend.src.cli.commands.modules_cmd import ModulesCommand
from backend.src.cli.commands.package_cmd import PaqueteCommand
from backend.src.cli.commands.plugins_cmd import PluginsCommand
from backend.src.cli.commands.profile_cmd import ProfileCommand
from backend.src.cli.commands.verify_cmd import VerifyCommand
from backend.src.cli.i18n import setup_gettext, format_traceback, _
from backend.src.cli.plugin import descubrir_plugins
from backend.src.cli.utils import messages





# La configuración de logging solo debe activarse cuando la CLI se ejecuta
# directamente para evitar modificar la configuración global al importar este
# módulo desde las pruebas u otros paquetes.


def main(argv=None):
    """Punto de entrada principal de la CLI."""
    setup_gettext()
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(prog="cobra", description=_("CLI para Cobra"))
    parser.add_argument("--formatear", action="store_true", help=_("Formatea el archivo antes de procesarlo"))
    parser.add_argument("--depurar", action="store_true", help=_("Muestra mensajes de depuración"))
    parser.add_argument("--seguro", action="store_true", help=_("Ejecuta en modo seguro"))
    parser.add_argument("--lang", default=os.environ.get("COBRA_LANG", "es"), help=_("Código de idioma para la interfaz"))
    parser.add_argument("--no-color", action="store_true", help=_("Desactiva colores en la salida"))
    parser.add_argument(
        "--validadores-extra",
        help="Ruta a módulo con validadores personalizados",
    )

    subparsers = parser.add_subparsers(dest="comando")

    comandos = [
        CompileCommand(),
        ExecuteCommand(),
        ModulesCommand(),
        DependenciasCommand(),
        DocsCommand(),
        EmpaquetarCommand(),
        PaqueteCommand(),
        CrearCommand(),
        InitCommand(),
        AgixCommand(),
        JupyterCommand(),
        FletCommand(),
        ContainerCommand(),
        BenchCommand(),
        BenchmarksCommand(),
        BenchmarksV2Command(),
        BenchTranspilersCommand(),
        ProfileCommand(),
        CacheCommand(),
        VerifyCommand(),
        PluginsCommand(),
        InteractiveCommand(),
    ]
    comandos.extend(descubrir_plugins())

    command_map = {}
    for cmd in comandos:
        cmd.register_subparser(subparsers)
        command_map[cmd.name] = cmd

    parser.set_defaults(cmd=command_map["interactive"])

    if argv is None:
        if "PYTEST_CURRENT_TEST" in os.environ:
            argv = []
        else:
            argv = sys.argv[1:]

    args = parser.parse_args(argv)
    setup_gettext(args.lang)
    messages.disable_colors(args.no_color)
    messages.mostrar_logo()
    command = getattr(args, "cmd", command_map["interactive"])
    try:
        resultado = command.run(args)
    except Exception as exc:  # pragma: no cover - trazas manejadas
        logging.exception("Unhandled exception")
        messages.mostrar_error("Ocurri\u00f3 un error inesperado")
        print(format_traceback(exc, args.lang))
        return 1
    return 0 if resultado is None else resultado


if __name__ == "__main__":
    sys.exit(main())
