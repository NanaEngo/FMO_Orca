import os
import subprocess
from pathlib import Path

def run_orca(orca_path, input_file, output_file, logger=None):
    """
    Run ORCA and capture output.

    Args:
        orca_path (str): Path to ORCA executable.
        input_file (str|Path): Input file.
        output_file (str|Path): Output file.

    Returns:
        Path to output file.

    Raises:
        Exception on failure.
    """
    if not os.path.isfile(orca_path) or not os.access(orca_path, os.X_OK):
        raise FileNotFoundError(f"ORCA executable not found or not executable: {orca_path}")
    input_file = Path(input_file)
    output_file = Path(output_file)
    err_file = output_file.with_suffix('.out.err')
    if logger: logger.info(f"Running ORCA: {orca_path} {input_file} > {output_file}")
    with open(output_file, 'w') as f_out, open(err_file, 'w') as f_err:
        subprocess.run([orca_path, str(input_file)], stdout=f_out, stderr=f_err, check=True)
    if logger: logger.info(f"ORCA run complete: {output_file}")
    return str(output_file)