import time
from pathlib import Path

RECOMMENDED_TDDFT_FUNCTIONALS = ["CAM-B3LYP", "M06-2X", "wB97X-V", "wB97X", "wB97X-3c"]

STDA_PARAMETERS = {
    "wB97X-3c": {"axstda": 0.56, "beta1": 8.00, "alpha1": 4.58},
    "CAM-B3LYP": {"axstda": 0.50, "beta1": 8.00, "alpha1": 4.58},
    "M06-2X": {"axstda": 0.54, "beta1": 8.00, "alpha1": 4.58},
    "wB97X-V": {"axstda": 0.56, "beta1": 8.00, "alpha1": 4.58},
    "wB97X": {"axstda": 0.56, "beta1": 8.00, "alpha1": 4.58}
}

def validate_functional(method, logger=None):
    if method not in RECOMMENDED_TDDFT_FUNCTIONALS and logger:
        logger.warning(f"Functional {method} not recommended: {RECOMMENDED_TDDFT_FUNCTIONALS}")
    return STDA_PARAMETERS.get(method, STDA_PARAMETERS["wB97X-3c"])

def create_orca_input(xyz_file, output_inp, base_name, nprocs, method, solvent,
                      nroots, triplets, maxcore, smiles, logger=None):
    """
    Generate ORCA input file for workflow.

    Args:
        xyz_file (str|Path): Path to xyz file.
        output_inp (str|Path): Path to .inp file.
        ... (see workflow)

    Returns:
        Path to input file.
    """
    xyz_file = Path(xyz_file)
    output_inp = Path(output_inp)
    std_params = validate_functional(method, logger)
    axstda, beta1, alpha1 = std_params["axstda"], std_params["beta1"], std_params["alpha1"]
    triplets_str = "true" if triplets else "false"
    current_date = time.strftime('%Y-%m-%d')
    orca_input_text = f"""# ORCA 6.1 Compound Job for {base_name}
# SMILES: {smiles}
# Generated on: {current_date}
# Three-step calculation: GFN2-xTB optimization -> sTDA/PIEDA -> sTDA on fragments
%base "./results/{base_name}"

%pal
  nprocs {nprocs}
end
%maxcore {maxcore}

%compound
New_Step
  ! Native-GFN2-xTB Opt CPCM({solvent}) VeryTightSCF

  %cpcm
    smd true
    SMDsolvent "{solvent}"
  end

  %frag
    FragProc Connectivity
    PrintLevel 3
    STOREFRAGS true
  end

  * xyzfile 0 1 {xyz_file}
Step_End

New_Step
  ! {method} TightSCF CPCM({solvent}) GCP(HF/MINIS)

  %cpcm
    smd true
    SMDsolvent "{solvent}"
  end

  %tddft
    Mode sTDA
    DoDipoleLength true
    DecomposeFosc true
    Ethresh 10.0
    axstda {axstda}
    beta1 {beta1}
    alpha1 {alpha1}
    NRoots {nroots}
    Triplets {triplets_str}
  end

  %frag
    FragProc FunctionalGroups, Extend
    PrintLevel 3
    STOREFRAGS true
  end
  
  * xyzfile 0 1 ./results/{base_name}_Compound_1.xyz
Step_End

New_Step
  ! {method} TightSCF CPCM({solvent})

  %cpcm
    smd true
    SMDsolvent "{solvent}"
  end

#  %frag
#    FragmentFromFile
#    PrintLevel 3
#  end

  %tddft
    Mode sTDA
    DoDipoleLength true
    DecomposeFosc true
    Ethresh 10.0
    axstda {axstda}
    beta1 {beta1}
    alpha1 {alpha1}
    NRoots {nroots}
    Triplets {triplets_str}
  end

  * xyzfile 0 1 ./results/{base_name}_Compound_1.fragments.xyz
Step_End
End
"""
    output_inp.write_text(orca_input_text)
    if logger: logger.info(f"ORCA input file written: {output_inp}")
    return str(output_inp)
