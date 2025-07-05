import re
from pathlib import Path

def parse_orca_output(output_file, logger=None):
    """
    Parse ORCA .out file for excitations and fragment analysis.

    Returns:
        dict with singlet_excitations, triplet_excitations, fragment_analysis
    """
    results = {
        'singlet_excitations': [],
        'triplet_excitations': [],
        'fragment_analysis': {}
    }

    in_singlet, in_triplet, in_pieda = False, False, False

    output_file = Path(output_file)
    if not output_file.exists() or output_file.stat().st_size == 0:
        if logger: logger.error("ORCA output file missing/empty")
        return results

    with open(output_file, 'r') as f:
        for line in f:
            if re.search(r"TD-DFT/TDA.*EXCITED\s*STATES.*SINGLETS", line, re.IGNORECASE):
                in_singlet, in_triplet, in_pieda = True, False, False
                continue
            if re.search(r"TD-DFT/TDA.*EXCITED\s*STATES.*TRIPLETS", line, re.IGNORECASE):
                in_singlet, in_triplet, in_pieda = False, True, False
                continue
            if re.search(r"PIEDA.*FRAGMENT\s*ANALYSIS", line, re.IGNORECASE):
                in_singlet, in_triplet, in_pieda = False, False, True
                continue
            if re.search(r"-{10,}", line):
                in_singlet = in_triplet = False

            if in_singlet and "STATE" in line:
                m = re.search(r"STATE\s+(\d+):\s*E=\s*([\d\.\-]+)\s*eV\s*.*?f=\s*([\d\.\-]+)", line)
                if m:
                    results['singlet_excitations'].append({
                        'state': int(m.group(1)),
                        'energy': float(m.group(2)),
                        'osc_strength': float(m.group(3))
                    })
            if in_triplet and "STATE" in line:
                m = re.search(r"STATE\s+(\d+):\s*E=\s*([\d\.\-]+)\s*eV", line)
                if m:
                    results['triplet_excitations'].append({
                        'state': int(m.group(1)),
                        'energy': float(m.group(2))
                    })
            if in_pieda and "Fragment" in line:
                m = re.search(r"Fragment\s+(\d+)\s+\(\w+\)\s+Total\s+Energy\s*:\s*([\d\.\-]+)", line)
                if m:
                    results['fragment_analysis'][f"Fragment {m.group(1)}"] = {
                        'total_energy': float(m.group(2))
                    }
    if logger:
        logger.info(f"Parsed singlets: {len(results['singlet_excitations'])}, triplets: {len(results['triplet_excitations'])}, fragments: {len(results['fragment_analysis'])}")
    return results