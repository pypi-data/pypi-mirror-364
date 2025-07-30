# rdkit_buildutils

This package provides basic utilities for building molecules from SMILES strings using RDKit, with placeholder substitution support.

This package was developed in a personal context for general scientific support purposes. It is not associated with any specific organization.

## Features

- `convert_r_to_atom_map(smiles_r)`: Converts [R1], [R2], ... placeholders to RDKit-compatible [*:1], [*:2] notation.
- `build_molecule_final(base_smiles, **substituents)`: Replaces mapped atoms in SMILES with substituents and returns the resulting RDKit molecule.

## Installation

```bash
pip install rdkit_buildutils
```

## License

MIT © 2025 Fabio Nelli
