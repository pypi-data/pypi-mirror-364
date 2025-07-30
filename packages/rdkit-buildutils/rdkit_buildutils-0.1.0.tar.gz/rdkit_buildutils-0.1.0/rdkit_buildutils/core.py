"""
Core utilities for RDKit molecule construction with placeholder substitution.
"""

from rdkit import Chem
import re

def build_molecule_final(base_smiles, **substituents):
    """
    Builds a molecule by replacing [*:n] placeholders in a base SMILES string
    with substituents provided as keyword arguments (r1='CC', r2='O', etc.).

    Args:
        base_smiles (str): SMILES with [*:1], [*:2], ... placeholders.
        **substituents: Dictionary of substituents, keyed as 'r1', 'r2', etc.

    Returns:
        Chem.Mol or None: The constructed molecule, or None if an error occurs.
    """
    mol = Chem.MolFromSmiles(base_smiles)
    if not mol:
        print(f"Error: Invalid base SMILES: {base_smiles}")
        return None

    current_mol = Chem.RWMol(mol)

    placeholder_atoms = {
        atom.GetAtomMapNum(): atom
        for atom in current_mol.GetAtoms()
        if atom.GetAtomMapNum() != 0
    }

    placeholder_numbers = sorted(placeholder_atoms.keys())

    if not placeholder_numbers:
        print("No placeholders found in the base molecule.")
        return current_mol.GetMol()

    for num in placeholder_numbers:
        key = f"r{num}"
        if key not in substituents:
            print(f"Error: Substituent for R{num} not provided.")
            return None

        substituent_smiles = substituents[key]
        placeholder_atom = placeholder_atoms[num]
        placeholder_idx = placeholder_atom.GetIdx()

        neighbors = placeholder_atom.GetNeighbors()
        if len(neighbors) != 1:
            print(f"Error: Placeholder [*:{num}] must have exactly one neighbor.")
            return None

        neighbor_atom = neighbors[0]
        neighbor_idx = neighbor_atom.GetIdx()

        if not substituent_smiles:
            current_mol.RemoveAtom(placeholder_idx)
        else:
            group_mol = Chem.MolFromSmiles(substituent_smiles)
            if not group_mol:
                print(f"Error: Invalid substituent SMILES for {key}: {substituent_smiles}")
                return None

            combined = Chem.CombineMols(current_mol.GetMol(), group_mol)
            rw_combined = Chem.RWMol(combined)
            attach_idx = rw_combined.GetNumAtoms() - group_mol.GetNumAtoms()

            rw_combined.AddBond(neighbor_idx, attach_idx, Chem.BondType.SINGLE)
            rw_combined.RemoveAtom(placeholder_idx)

            current_mol = rw_combined

        placeholder_atoms = {
            atom.GetAtomMapNum(): atom
            for atom in current_mol.GetAtoms()
            if atom.GetAtomMapNum() != 0
        }

    final_mol = current_mol.GetMol()
    Chem.SanitizeMol(final_mol)

    for atom in final_mol.GetAtoms():
        atom.SetAtomMapNum(0)

    return final_mol


def convert_r_to_atom_map(smiles_r):
    """
    Converts a SMILES string with [R1], [R2], ... placeholders to RDKit's [*:1], [*:2], ... format.

    Args:
        smiles_r (str): Input SMILES with [R1], [R2], etc.

    Returns:
        str: SMILES with [*:n] placeholders.
    """
    pattern = r'\[R(\d+)\]'

    def replace_r(match):
        number = match.group(1)
        return f'[*:{number}]'

    return re.sub(pattern, replace_r, smiles_r)
