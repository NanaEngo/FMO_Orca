from rdkit import Chem
from rdkit.Chem import AllChem
from pathlib import Path

def smiles_to_xyz(smiles, output_xyz="molecule.xyz", force_field='MMFF94', max_iters=500, logger=None):
    """
    Convert SMILES to 3D geometry and write XYZ file.

    Args:
        smiles (str): SMILES string.
        output_xyz (str|Path): Output file path for .xyz.
        force_field (str): 'MMFF94' or 'UFF'.
        max_iters (int): Maximum iterations for optimization.
        logger: Logger instance (optional).

    Returns:
        Path to output xyz.

    Raises:
        ValueError, Exception
    """
    if not smiles or not isinstance(smiles, str):
        raise ValueError("SMILES string must be non-empty and a valid string")
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("Invalid SMILES string")
    if logger: logger.info(f"SMILES parsed: {mol.GetNumAtoms()} atoms")

    mol = Chem.AddHs(mol)
    if logger: logger.info("Hydrogens added")

    # Embed with retry
    for seed in [42, 31415, 271828]:
        params = AllChem.ETKDGv3()
        params.randomSeed = seed
        params.useRandomCoords = True
        if AllChem.EmbedMolecule(mol, params) != -1:
            break
    else:
        raise ValueError("Failed to generate 3D coords")

    # Optimize
    if force_field.upper() == 'MMFF94':
        props = AllChem.MMFFGetMoleculeProperties(mol)
        ff = AllChem.MMFFGetMoleculeForceField(mol, props)
        if ff: ff.Minimize(maxIts=max_iters)
        else:
            if logger: logger.warning("Fallback to UFF")
            AllChem.UFFOptimizeMolecule(mol, maxIters=max_iters)
    else:
        AllChem.UFFOptimizeMolecule(mol, maxIters=max_iters)

    output_xyz = Path(output_xyz)
    xyz_block = Chem.MolToXYZBlock(mol)
    output_xyz.write_text(xyz_block)
    if logger: logger.info(f"XYZ written: {output_xyz}")
    return str(output_xyz)