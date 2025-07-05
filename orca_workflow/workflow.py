import json
import shutil
from pathlib import Path
from .utils import sha256_of_file, sha256_of_string, profile_step

def run_workflow(
    smiles, orca_path, molecule_name, output_dir, logger,
    config, cleanup=True
):
    """
    Orchestration du workflow complet.

    Args:
        smiles (str)
        orca_path (str)
        molecule_name (str)
        output_dir (str|Path)
        logger (Logger)
        config (dict)
        cleanup (bool)
    Returns:
        dict (results)
    """
    from .geometry import smiles_to_xyz
    from .orca_io import create_orca_input
    from .runner import run_orca
    from .parser import parse_orca_output

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True, parents=True)

    # Profiling: SMILES → XYZ
    xyz_path = output_dir / f"{molecule_name}.xyz"
    profiled_smiles_to_xyz = profile_step(logger, "SMILES→XYZ")(smiles_to_xyz)
    xyz_path = profiled_smiles_to_xyz(smiles, xyz_path, force_field=config['force_field'], logger=logger)

    # Profiling: .inp generation
    inp_path = output_dir / f"{molecule_name}.inp"
    profiled_create_orca_input = profile_step(logger, "Create INP")(create_orca_input)
    inp_path = profiled_create_orca_input(
        xyz_path, inp_path, base_name=molecule_name,
        nprocs=config['nprocs'],
        method=config['method'],
        solvent=config['solvent'],
        nroots=config['nroots'],
        triplets=config['triplets'],
        maxcore=config['maxcore'],
        smiles=smiles,
        logger=logger
    )

    # Profiling: ORCA run
    out_path = output_dir / f"{molecule_name}.out"
    profiled_run_orca = profile_step(logger, "Run ORCA")(run_orca)
    out_path = profiled_run_orca(orca_path, inp_path, out_path, logger=logger)

    # Profiling: parse output
    profiled_parse_orca_output = profile_step(logger, "Parse OUT")(parse_orca_output)
    results = profiled_parse_orca_output(out_path, logger=logger)

    # SHA tags
    xyz_sha = sha256_of_file(xyz_path)
    inp_sha = sha256_of_file(inp_path)
    results['xyz_sha256'] = xyz_sha
    results['inp_sha256'] = inp_sha

    # Export JSON
    json_path = output_dir / f"{molecule_name}_results.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Résultats exportés dans {json_path}")

    # Export Markdown
    md_path = output_dir / f"{molecule_name}_results.md"
    with open(md_path, 'w') as md:
        md.write(f"# Résultats ORCA pour {molecule_name}\n")
        md.write(f"- SHA256(xyz): `{xyz_sha}`\n- SHA256(inp): `{inp_sha}`\n\n")
        if results.get('singlet_excitations'):
            md.write("## Singlet Excitations\n\n| State | Energy (eV) | Osc.Strength |\n|---|---|---|\n")
            for exc in results['singlet_excitations']:
                md.write(f"| {exc['state']} | {exc['energy']:.3f} | {exc['osc_strength']:.3f} |\n")
        if results.get('triplet_excitations'):
            md.write("\n## Triplet Excitations\n\n| State | Energy (eV) |\n|---|---|\n")
            for exc in results['triplet_excitations']:
                md.write(f"| {exc['state']} | {exc['energy']:.3f} |\n")
        if results.get('fragment_analysis'):
            md.write("\n## Fragment Analysis\n\n| Fragment | Total Energy (Eh) |\n|---|---|\n")
            for frag, data in results['fragment_analysis'].items():
                md.write(f"| {frag} | {data['total_energy']:.6f} |\n")
    logger.info(f"Résumé Markdown exporté dans {md_path}")

    # Cleanup
    if cleanup:
        for file_path in [xyz_path, inp_path, out_path.with_suffix('.out.err')]:
            try:
                Path(file_path).unlink(missing_ok=True)
                logger.info(f"Suppression du fichier temporaire: {file_path}")
            except Exception:
                pass

    return results