from typing import Optional

import tqdm
from chemlog.alg_classification.charge_classifier import get_charge_category
from chemlog.alg_classification.peptide_size_classifier import get_n_amino_acid_residues
from chemlog.alg_classification.proteinogenics_classifier import (
    get_proteinogenic_amino_acids,
)
from chemlog.alg_classification.substructure_classifier import (
    is_diketopiperazine,
    is_emericellamide,
)
from chemlog.cli import CLASSIFIERS, _smiles_to_mol, strategy_call
from chemlog_extra.alg_classification.by_element_classification import (
    XMolecularEntityClassifier,
    OrganoXCompoundClassifier,
)
from functools import lru_cache

from .base_predictor import BasePredictor

AA_DICT = {
    "A": "L-alanine",
    "C": "L-cysteine",
    "D": "L-aspartic acid",
    "E": "L-glutamic acid",
    "F": "L-phenylalanine",
    "G": "glycine",
    "H": "L-histidine",
    "I": "L-isoleucine",
    "K": "L-lysine",
    "L": "L-leucine",
    "M": "L-methionine",
    "fMet": "N-formylmethionine",
    "N": "L-asparagine",
    "O": "L-pyrrolysine",
    "P": "L-proline",
    "Q": "L-glutamine",
    "R": "L-arginine",
    "S": "L-serine",
    "T": "L-threonine",
    "U": "L-selenocysteine",
    "V": "L-valine",
    "W": "L-tryptophan",
    "Y": "L-tyrosine",
}


class ChemlogExtraPredictor(BasePredictor):

    CHEMLOG_CLASSIFIER = None

    def __init__(self, model_name: str, **kwargs):
        super().__init__(model_name, **kwargs)
        self.chebi_graph = kwargs.get("chebi_graph", None)
        self.classifier = self.CHEMLOG_CLASSIFIER()

    def predict_smiles_tuple(self, smiles_list: tuple[str]) -> list:
        mol_list = [_smiles_to_mol(smiles) for smiles in smiles_list]
        res = self.classifier.classify(mol_list)
        if self.chebi_graph is not None:
            for sample in res:
                sample_additions = dict()
                for cls in sample:
                    if sample[cls] == 1:
                        successors = list(self.chebi_graph.predecessors(cls))
                        if successors:
                            for succ in successors:
                                sample_additions[str(succ)] = 1
                sample.update(sample_additions)
        return res


class ChemlogXMolecularEntityPredictor(ChemlogExtraPredictor):

    CHEMLOG_CLASSIFIER = XMolecularEntityClassifier


class ChemlogOrganoXCompoundPredictor(ChemlogExtraPredictor):

    CHEMLOG_CLASSIFIER = OrganoXCompoundClassifier


class ChemlogPeptidesPredictor(BasePredictor):
    def __init__(self, model_name: str, **kwargs):
        super().__init__(model_name, **kwargs)
        self.strategy = "algo"
        self.chebi_graph = kwargs.get("chebi_graph", None)
        self.classifier_instances = {
            k: v() for k, v in CLASSIFIERS[self.strategy].items()
        }
        # fmt: off
        self.peptide_labels = [
            "15841", "16670", "24866", "25676", "25696", "25697", "27369", "46761", "47923",
            "48030", "48545", "60194", "60334", "60466", "64372", "65061", "90799", "155837"
        ]
        # fmt: on
        print(f"Initialised ChemLog model {self.model_name}")

    @lru_cache(maxsize=100)
    def predict_smiles(self, smiles: str) -> Optional[dict]:
        mol = _smiles_to_mol(smiles)
        if mol is None:
            return None
        pos_labels = [
            label
            for label in self.peptide_labels
            if label
            in strategy_call(self.strategy, self.classifier_instances, mol)[
                "chebi_classes"
            ]
        ]
        if self.chebi_graph:
            indirect_pos_labels = [
                str(pr)
                for label in pos_labels
                for pr in self.chebi_graph.predecessors(label)
            ]
            pos_labels = list(set(pos_labels + indirect_pos_labels))
        return {
            label: (1 if label in pos_labels else 0)
            for label in self.peptide_labels + pos_labels
        }

    def predict_smiles_tuple(self, smiles_list: tuple[str]) -> list:
        results = []
        for i, smiles in tqdm.tqdm(enumerate(smiles_list)):
            results.append(self.predict_smiles(smiles))

        for classifier in self.classifier_instances.values():
            classifier.on_finish()

        return results

    def get_chemlog_result_info(self, smiles):
        """Get classification for single molecule with additional information."""
        mol = _smiles_to_mol(smiles)
        if mol is None or not smiles:
            return {"error": "Failed to parse SMILES"}

        charge_category = get_charge_category(mol)
        n_amino_acid_residues, add_output = get_n_amino_acid_residues(mol)
        if n_amino_acid_residues > 1:
            proteinogenics, proteinogenics_locations, _ = get_proteinogenic_amino_acids(
                mol, add_output["amino_residue"], add_output["carboxy_residue"]
            )
        else:
            proteinogenics, proteinogenics_locations, _ = [], [], []
        results = {
            "charge_category": charge_category.name,
            "n_amino_acid_residues": n_amino_acid_residues,
            "proteinogenics": proteinogenics,
            "proteinogenics_locations": proteinogenics_locations,
        }

        if n_amino_acid_residues == 5:
            emericellamide = is_emericellamide(mol)
            results["emericellamide"] = emericellamide[0]
            if emericellamide[0]:
                results["emericellamide_atoms"] = emericellamide[1]
        if n_amino_acid_residues == 2:
            diketopiperazine = is_diketopiperazine(mol)
            results["2,5-diketopiperazines"] = diketopiperazine[0]
            if diketopiperazine[0]:
                results["2,5-diketopiperazines_atoms"] = diketopiperazine[1]

        return {**results, **add_output}

    def build_explain_blocks_atom_allocations(self, atoms, cls_name):
        return [
            ("heading", cls_name),
            (
                "text",
                f"The peptide has been identified as an instance of '"
                f"{cls_name}'. This was decided based on the presence of the following structure:",
            ),
            ("single", atoms),
        ]

    def build_explain_blocks_peptides(self, info):
        blocks = []
        if "error" in info:
            blocks.append(
                (
                    "text",
                    f"An error occurred while processing the molecule: {info['error']}",
                )
            )
            return blocks
        blocks.append(("heading", "Functional groups"))
        if len(info["amide_bond"]) == 0:
            blocks.append(
                (
                    "text",
                    "The molecule does not contain any amide. Therefore, it cannot be a peptide, "
                    "peptide anion, peptide zwitterion or peptide cation.",
                )
            )
            return blocks
        blocks.append(
            ("text", "The molecule contains the following functional groups:")
        )
        blocks.append(
            (
                "tabs",
                {
                    "Amide": info["amide_bond"],
                    "Carboxylic acid derivative": info["carboxy_residue"],
                    "Amino group": [[a] for a in info["amino_residue"]],
                },
            )
        )
        blocks.append(("heading", "Identifying the peptide structure"))
        if len(info["chunks"]) == 0:
            blocks.append(
                (
                    "text",
                    "All atoms in the molecule are connected via a chain of carbon atoms. "
                    "Therefore, the molecule cannot be a peptide, peptide anion, peptide zwitterion "
                    "or peptide cation.",
                )
            )
            return blocks
        blocks.append(
            (
                "text",
                "To divide up the molecule into potential amino acids, it has been split into the "
                f"{len(info['chunks'])} 'building blocks' (based on heteroatoms).",
            )
        )
        blocks.append(
            (
                "text",
                "For each, we have checked if it constitutes an amino acid residue.",
            )
        )
        if len(info["chunks"]) == len(info["longest_aa_chain"]):
            blocks.append(
                (
                    "text",
                    "All chunks have been identified as amino acid residues that are connected "
                    "via amide bonds:",
                )
            )
            blocks.append(("tabs", {"Amino acid residue": info["longest_aa_chain"]}))
        elif len(info["longest_aa_chain"]) == 0:
            blocks.append(("tabs", {"Chunks": info["chunks"]}))
            blocks.append(
                (
                    "text",
                    "In these chunks, no amino acids have been identified. "
                    "Therefore, the molecule cannot be a peptide, "
                    "peptide anion, peptide zwitterion or peptide cation.",
                )
            )
            return blocks
        else:
            blocks.append(
                (
                    "text",
                    f"{len(info['longest_aa_chain'])} of these chunks have been identified as amino acid "
                    f"residues and are connected via amide bonds:",
                )
            )
            blocks.append(
                (
                    "tabs",
                    {
                        "Chunks": info["chunks"],
                        "Amino acid residue": info["longest_aa_chain"],
                    },
                )
            )
        if len(info["longest_aa_chain"]) < 2:
            blocks.append(
                (
                    "text",
                    "Only one amino acid has been identified. Therefore, the molecule cannot be a "
                    "peptide, peptide anion, peptide zwitterion or peptide cation.",
                )
            )
            return blocks

        blocks.append(("heading", "Charge-based classification"))
        if info["charge_category"] == "SALT":
            blocks.append(
                (
                    "text",
                    "The molecule consists of disconnected anionic and cationic fragments. "
                    "Therefore, we classify it as a peptide salt. Since there is no class 'peptide salt'"
                    "in ChEBI, no prediction is made.",
                )
            )
            return blocks
        elif info["charge_category"] == "CATION":
            blocks.append(
                (
                    "text",
                    "The molecule has a net positive charge, therefore it is a 'peptide cation'.",
                )
            )
            return blocks
        elif info["charge_category"] == "ANION":
            blocks.append(
                (
                    "text",
                    "The molecule has a net negative charge, therefore it is a 'peptide anion'.",
                )
            )
            return blocks
        elif info["charge_category"] == "ZWITTERION":
            blocks.append(
                (
                    "text",
                    "The molecule is overall neutral, but a zwitterion, i.e., it contains connected "
                    "(but non-adjacent) atoms with opposite charges.",
                )
            )
            if info["n_amino_acid_residues"] == 2:
                blocks.append(
                    (
                        "text",
                        "Since we have identified 2 amino acid residues, the final classification is "
                        "'dipeptide zwitterion'.",
                    )
                )
            if info["n_amino_acid_residues"] == 3:
                blocks.append(
                    (
                        "text",
                        "Since we have identified 3 amino acid residues, the final classification is "
                        "'tripeptide zwitterion'.",
                    )
                )
            return blocks
        subclasses_dict = {
            2: "di",
            3: "tri",
            4: "tetra",
            5: "penta",
            6: "oligo",
            7: "oligo",
            8: "oligo",
            9: "oligo",
            10: "poly",
        }
        blocks.append(
            (
                "text",
                "The molecule is overall neutral and not a zwitterion. Therefore, it is a peptide.",
            )
        )
        blocks.append(
            (
                "text",
                f"More specifically, since we have identified "
                f"{info['n_amino_acid_residues']} amino acid residues,"
                f"the final classification is '{subclasses_dict[min(10, info['n_amino_acid_residues'])]}peptide'.",
            )
        )
        return blocks

    def build_explain_blocks_proteinogenics(self, proteinogenics, atoms):
        blocks = [("heading", "Proteinogenic amino acids")]
        if len(proteinogenics) == 0:
            blocks.append(
                ("text", "No proteinogenic amino acids have been identified.")
            )
            return blocks
        blocks.append(
            (
                "text",
                "In addition to the classification, we have searched for the residues of 23 "
                "proteinogenic amino acids in the molecule.",
            )
        )
        blocks.append(
            ("text", "The following proteinogenic amino acids have been identified:")
        )
        proteinogenics_dict = {AA_DICT[aa]: [] for aa in proteinogenics}
        for aa, atoms_aa in zip(proteinogenics, atoms):
            proteinogenics_dict[AA_DICT[aa]].append(atoms_aa)
        blocks.append(("tabs", proteinogenics_dict))
        return blocks

    def explain_smiles(self, smiles) -> dict:
        info = self.get_chemlog_result_info(smiles)
        zero_blocks = [
            (
                "text",
                "Results for peptides and peptide-related classes (e.g. peptide anion, depsipeptide) have been calculated"
                " with a rule-based system. The following shows which parts of the molecule were identified as relevant"
                " structures and have influenced the classification.",
            )
        ]
        highlight_blocks = zero_blocks + self.build_explain_blocks_peptides(info)

        for chebi_id, internal_name in [
            (64372, "emericellamide"),
            (65061, "2,5-diketopiperazines"),
        ]:
            if f"{internal_name}_atoms" in info:
                highlight_blocks += self.build_explain_blocks_atom_allocations(
                    info[f"{internal_name}_atoms"], internal_name
                )
        highlight_blocks += self.build_explain_blocks_proteinogenics(
            info["proteinogenics"], info["proteinogenics_locations"]
        )
        return {
            "smiles": smiles,
            "highlights": highlight_blocks,
        }
