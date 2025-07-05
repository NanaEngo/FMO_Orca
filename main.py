from orca_workflow.cli import parse_args, resolve_orca_path, resolve_nprocs
from orca_workflow.config import load_config
from orca_workflow.utils import setup_logger
from orca_workflow.workflow import run_workflow

def main():
    args = parse_args()
    config = load_config(args.config)
    orca_path = resolve_orca_path(args.orca_path)
    config['nprocs'] = resolve_nprocs(config)
    log_dir = args.output_dir
    logger, run_id = setup_logger(log_dir=log_dir)
    logger.info(f"[START RUN_ID={run_id}] Workflow pour {args.molecule_name}")

    try:
        results = run_workflow(
            smiles=args.smiles,
            orca_path=orca_path,
            molecule_name=args.molecule_name,
            output_dir=args.output_dir,
            logger=logger,
            config=config,
            cleanup=args.cleanup
        )
        logger.info("Workflow terminé avec succès.")
    except Exception as e:
        logger.error(f"Erreur critique: {e}")
        exit(1)

if __name__ == '__main__':
    main()