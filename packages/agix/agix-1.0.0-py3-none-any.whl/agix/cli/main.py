# src/agix/cli/main.py

import argparse

from src.agix.cli import qualia_shell
from src.agix.cli.commands import simulate, inspect, evaluate


def main():
    parser = argparse.ArgumentParser(
        description="AGI Core CLI - Interfaz de línea de comandos para simulación, inspección y evaluación de agentes."
    )

    subparsers = parser.add_subparsers(title="comandos disponibles", dest="command")

    # Subcomando: simulate
    sim_parser = subparsers.add_parser(
        "simulate", help="Simula un agente", description="Simula un agente AGI simple en un entorno mínimo"
    )
    simulate.build_parser(sim_parser)

    # Subcomando: inspect
    insp_parser = subparsers.add_parser(
        "inspect", help="Inspecciona el agente", description="Inspecciona el estado reflexivo del agente AGI"
    )
    inspect.build_parser(insp_parser)

    # Subcomando: evaluate
    eval_parser = subparsers.add_parser(
        "evaluate", help="Evalúa el agente", description="Evaluación del agente AGI"
    )
    evaluate.build_parser(eval_parser)

    # Subcomando: qualia
    qualia_parser = subparsers.add_parser(
        "qualia", help="Shell interactivo de Qualia", description="Interactúa con QualiaSpirit"
    )
    qualia_shell.build_parser(qualia_parser)

    # Parsear argumentos
    args = parser.parse_args()

    if args.command == "simulate":
        simulate.run_simulation(args)
    elif args.command == "inspect":
        inspect.run_inspection(args)
    elif args.command == "evaluate":
        evaluate.run_evaluation(args)
    elif args.command == "qualia":
        qualia_shell.run_shell(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
