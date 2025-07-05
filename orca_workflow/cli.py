import argparse
import os
from .utils import detect_orca_in_path, get_logical_cpu_count

def parse_args():
    parser = argparse.ArgumentParser(description="Workflow ORCA FMO")
    parser.add_argument('--smiles', required=True, help="SMILES string de la molécule")
    parser.add_argument('--molecule_name', default="molecule", help="Nom de la molécule")
    parser.add_argument('--orca_path', default=None, help="Chemin vers l'exécutable ORCA")
    parser.add_argument('--output_dir', default="output", help="Répertoire de sortie")
    parser.add_argument('--config', default=None, help="Fichier YAML de configuration")
    parser.add_argument('--cleanup', action="store_true", help="Supprimer les fichiers temporaires")
    return parser.parse_args()

def resolve_orca_path(orca_path_arg):
    if orca_path_arg:
        return orca_path_arg
    found = detect_orca_in_path()
    if found:
        return found
    raise FileNotFoundError("ORCA non trouvé dans $PATH ou via --orca_path")

def resolve_nprocs(config):
    if config.get('nprocs') is None:
        return get_logical_cpu_count()
    return config['nprocs']