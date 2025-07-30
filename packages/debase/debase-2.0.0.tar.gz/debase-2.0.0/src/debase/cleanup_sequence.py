#!/usr/bin/env python3
"""
cleanup_sequence_structured.py - Enhanced protein sequence generator from mutations

This module takes the output from enzyme_lineage_extractor and generates complete
protein sequences by applying mutations throughout the lineage tree.

Usage:
    python cleanup_sequence_structured.py input.csv output.csv
"""

import argparse
import logging
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import pandas as pd

try:
    import google.generativeai as genai  # type: ignore
    GEMINI_OK = True
except ImportError:  # pragma: no cover
    GEMINI_OK = False


# === 1. CONFIGURATION & CONSTANTS === ----------------------------------------

VALID_AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY*")  # Include * for stop codons
VALID_DNA_BASES = set("ACGT")

# Genetic code table for DNA to amino acid translation
GENETIC_CODE = {
    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
}

# Gemini API configuration
GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")

# Configure module logger
log = logging.getLogger(__name__)


# === 2. DATA MODELS === ------------------------------------------------------

@dataclass
class Mutation:
    """Represents a single point mutation."""
    original: str
    position: int
    replacement: str
    
    def __str__(self) -> str:
        return f"{self.original}{self.position}{self.replacement}"


@dataclass
class ComplexMutation:
    """Represents complex mutations like C-terminal modifications."""
    replacement_seq: str
    start_pos: int
    end_pos: int
    extension_seq: str = ""
    has_stop: bool = False
    
    def __str__(self) -> str:
        result = f"{self.replacement_seq}({self.start_pos}-{self.end_pos})"
        if self.extension_seq:
            result += self.extension_seq
        if self.has_stop:
            result += "[STOP]"
        return result


@dataclass
class Variant:
    """Enhanced variant representation with sequence information."""
    enzyme_id: str
    parent_enzyme_id: Optional[str]
    mutations: str
    protein_sequence: Optional[str] = None
    generation: Optional[int] = None
    flag: str = ""
    
    @property
    def has_sequence(self) -> bool:
        return bool(self.protein_sequence and self.protein_sequence.strip())
    
    @property
    def has_complex_mutations(self) -> bool:
        return "complex_mutation" in self.flag


@dataclass
class SequenceGenerationResult:
    """Result of sequence generation attempt."""
    sequence: str
    method: str  # "from_parent", "from_child", "from_ancestor", "from_descendant"
    source_id: str
    confidence: float = 1.0
    notes: str = ""


# === 3. MUTATION PARSING === -------------------------------------------------

class MutationParser:
    """Handles parsing of various mutation formats."""
    
    POINT_MUTATION_PATTERN = re.compile(r"^([A-Za-z\*])([0-9]+)([A-Za-z\*])$")
    COMPLEX_C_TERMINAL_PATTERN = re.compile(r'([A-Z]+)\((\d+)-(\d+)\)([A-Z]*)\[STOP\]')
    COMPLEX_C_TERMINAL_NO_STOP = re.compile(r'([A-Z]+)\((\d+)-(\d+)\)([A-Z]+)')
    
    @classmethod
    def parse_mutations(cls, mutation_str: str) -> List[Mutation]:
        """Parse standard point mutations from a mutation string."""
        if not mutation_str or mutation_str.strip() == "":
            return []
        
        mutations = []
        for mut_str in mutation_str.split(','):
            mut_str = mut_str.strip()
            if not mut_str:
                continue
                
            match = cls.POINT_MUTATION_PATTERN.match(mut_str)
            if match:
                try:
                    orig, pos_str, new = match.groups()
                    mutations.append(Mutation(
                        original=orig.upper(),
                        position=int(pos_str),
                        replacement=new.upper()
                    ))
                except ValueError as e:
                    log.warning(f"Failed to parse mutation '{mut_str}': {e}")
        
        return mutations
    
    @classmethod
    def parse_complex_c_terminal(cls, mutation_str: str) -> Optional[ComplexMutation]:
        """Parse complex C-terminal mutations."""
        # Try pattern with [STOP]
        match = cls.COMPLEX_C_TERMINAL_PATTERN.search(mutation_str)
        if match:
            return ComplexMutation(
                replacement_seq=match.group(1),
                start_pos=int(match.group(2)),
                end_pos=int(match.group(3)),
                extension_seq=match.group(4),
                has_stop=True
            )
        
        # Try pattern without [STOP]
        match = cls.COMPLEX_C_TERMINAL_NO_STOP.search(mutation_str)
        if match:
            return ComplexMutation(
                replacement_seq=match.group(1),
                start_pos=int(match.group(2)),
                end_pos=int(match.group(3)),
                extension_seq=match.group(4),
                has_stop=False
            )
        
        return None
    
    @classmethod
    def detect_complex_mutations(cls, mutation_str: str) -> List[str]:
        """Detect non-standard mutations in the mutation string."""
        if not mutation_str or mutation_str.strip() == "":
            return []
        
        all_muts = [m.strip() for m in mutation_str.split(',') if m.strip()]
        std_muts = {str(m) for m in cls.parse_mutations(mutation_str)}
        
        return [m for m in all_muts if m not in std_muts]


# === 4. SEQUENCE MANIPULATION === --------------------------------------------

class SequenceManipulator:
    """Handles application and reversal of mutations on sequences."""
    
    @staticmethod
    def validate_sequence(seq: str) -> bool:
        """Validate that a sequence contains only valid amino acids."""
        return all(aa in VALID_AMINO_ACIDS for aa in seq.upper())
    
    @staticmethod
    def is_dna_sequence(seq: str) -> bool:
        """Check if a sequence is DNA (contains only ACGT)."""
        seq_upper = seq.upper().replace(" ", "").replace("\n", "")
        return all(base in VALID_DNA_BASES for base in seq_upper) and len(seq_upper) > 0
    
    @staticmethod
    def translate_dna_to_protein(dna_seq: str) -> str:
        """Translate DNA sequence to protein sequence.
        
        Args:
            dna_seq: DNA sequence string
            
        Returns:
            Protein sequence string
        """
        # Clean the DNA sequence
        dna_seq = dna_seq.upper().replace(" ", "").replace("\n", "")
        
        # Check if sequence length is multiple of 3
        if len(dna_seq) % 3 != 0:
            log.warning(f"DNA sequence length ({len(dna_seq)}) is not a multiple of 3. Truncating to nearest codon.")
            dna_seq = dna_seq[:-(len(dna_seq) % 3)]
        
        protein_seq = []
        for i in range(0, len(dna_seq), 3):
            codon = dna_seq[i:i+3]
            if len(codon) == 3:
                # Handle unknown codons (with N or other non-standard bases)
                if codon in GENETIC_CODE:
                    protein_seq.append(GENETIC_CODE[codon])
                else:
                    # If codon contains non-standard bases, add 'X' for unknown amino acid
                    protein_seq.append('X')
                    log.debug(f"Unknown codon '{codon}' at position {i}, using 'X' for unknown amino acid")
        
        return ''.join(protein_seq)
    
    @staticmethod
    def determine_indexing(parent_seq: str, mutations: List[Mutation]) -> int:
        """Determine whether mutations use 0-based or 1-based indexing."""
        if not mutations or not parent_seq:
            return 1  # Default to 1-based
        
        # Count matches for each indexing scheme
        zero_matches = sum(
            1 for m in mutations 
            if 0 <= m.position < len(parent_seq) and 
            parent_seq[m.position].upper() == m.original.upper()
        )
        one_matches = sum(
            1 for m in mutations 
            if 0 <= m.position - 1 < len(parent_seq) and 
            parent_seq[m.position - 1].upper() == m.original.upper()
        )
        
        return 0 if zero_matches >= one_matches else 1
    
    @classmethod
    def apply_mutations(cls, parent_seq: str, mutation_str: str) -> Tuple[str, bool]:
        """Apply mutations to a parent sequence.
        
        Returns:
            Tuple[str, bool]: (resulting_sequence, all_mutations_applied_successfully)
        """
        if not parent_seq:
            return "", True
        
        seq = list(parent_seq)
        all_mutations_successful = True
        
        # Apply point mutations
        mutations = MutationParser.parse_mutations(mutation_str)
        if mutations:
            idx_offset = cls.determine_indexing(parent_seq, mutations)
            
            for mut in mutations:
                idx = mut.position - idx_offset
                mutation_applied = False
                
                # Try primary index
                if 0 <= idx < len(seq) and seq[idx].upper() == mut.original.upper():
                    seq[idx] = mut.replacement
                    mutation_applied = True
                else:
                    # Try alternate index
                    alt_idx = mut.position - (1 - idx_offset)
                    if 0 <= alt_idx < len(seq) and seq[alt_idx].upper() == mut.original.upper():
                        seq[alt_idx] = mut.replacement
                        mutation_applied = True
                
                if not mutation_applied:
                    log.error(
                        f"MUTATION MISMATCH: {mut} does not match parent sequence at "
                        f"position {mut.position} (tried both 0- and 1-based indexing). "
                        f"Parent has {seq[idx] if 0 <= idx < len(seq) else 'out-of-bounds'} at position {mut.position}"
                    )
                    all_mutations_successful = False
        
        # Apply complex C-terminal mutations
        complex_mut = MutationParser.parse_complex_c_terminal(mutation_str)
        if complex_mut:
            log.info(f"Applying complex C-terminal mutation: {complex_mut}")
            
            # Convert to 0-indexed
            start_idx = complex_mut.start_pos - 1
            end_idx = complex_mut.end_pos - 1
            
            if 0 <= start_idx <= end_idx < len(seq):
                # Replace the specified region
                seq[start_idx:end_idx + 1] = list(complex_mut.replacement_seq)
                
                # Handle STOP codon
                if complex_mut.has_stop:
                    seq = seq[:start_idx + len(complex_mut.replacement_seq)]
                
                # Add extension if present
                if complex_mut.extension_seq:
                    seq.extend(list(complex_mut.extension_seq))
            else:
                log.error(
                    f"COMPLEX MUTATION MISMATCH: Invalid C-terminal mutation positions: {complex_mut.start_pos}-"
                    f"{complex_mut.end_pos} for sequence of length {len(seq)}"
                )
                all_mutations_successful = False
        
        return "".join(seq), all_mutations_successful
    
    @classmethod
    def reverse_mutations(cls, child_seq: str, mutation_str: str) -> str:
        """Reverse mutations to get parent sequence from child."""
        if not child_seq:
            return ""
        
        seq = list(child_seq)
        mutations = MutationParser.parse_mutations(mutation_str)
        
        if not mutations:
            return child_seq
        
        # Determine indexing by checking which positions have the "new" amino acid
        zero_matches = sum(
            1 for m in mutations 
            if 0 <= m.position < len(child_seq) and 
            child_seq[m.position].upper() == m.replacement.upper()
        )
        one_matches = sum(
            1 for m in mutations 
            if 0 <= m.position - 1 < len(child_seq) and 
            child_seq[m.position - 1].upper() == m.replacement.upper()
        )
        
        idx_offset = 0 if zero_matches >= one_matches else 1
        
        # Reverse mutations (change replacement -> original)
        for mut in mutations:
            idx = mut.position - idx_offset
            if 0 <= idx < len(seq) and seq[idx].upper() == mut.replacement.upper():
                seq[idx] = mut.original
            else:
                alt_idx = mut.position - (1 - idx_offset)
                if 0 <= alt_idx < len(seq) and seq[alt_idx].upper() == mut.replacement.upper():
                    seq[alt_idx] = mut.original
                else:
                    log.warning(
                        f"Cannot reverse mutation {mut}: replacement amino acid "
                        f"not found at expected position"
                    )
        
        return "".join(seq)


# === 5. LINEAGE NAVIGATION === -----------------------------------------------

class LineageNavigator:
    """Handles navigation through the enzyme lineage tree."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._build_relationships()
    
    def _build_relationships(self) -> None:
        """Build parent-child relationship mappings."""
        self.parent_to_children: Dict[str, List[str]] = {}
        self.child_to_parent: Dict[str, str] = {}
        
        for _, row in self.df.iterrows():
            child_id = row["enzyme_id"]
            parent_id = row.get("parent_enzyme_id")
            
            if parent_id:
                self.child_to_parent[child_id] = parent_id
                if parent_id not in self.parent_to_children:
                    self.parent_to_children[parent_id] = []
                self.parent_to_children[parent_id].append(child_id)
    
    def get_ancestors(self, variant_id: str) -> List[str]:
        """Get all ancestors of a variant in order (immediate parent first)."""
        ancestors = []
        current_id = self.child_to_parent.get(variant_id)
        
        while current_id:
            ancestors.append(current_id)
            current_id = self.child_to_parent.get(current_id)
        
        return ancestors
    
    def get_descendants(self, variant_id: str) -> List[str]:
        """Get all descendants of a variant (breadth-first order)."""
        descendants = []
        queue = [variant_id]
        visited = {variant_id}
        
        while queue:
            current_id = queue.pop(0)
            children = self.parent_to_children.get(current_id, [])
            
            for child in children:
                if child not in visited:
                    visited.add(child)
                    descendants.append(child)
                    queue.append(child)
        
        return descendants
    
    def find_path(self, from_id: str, to_id: str) -> Optional[List[str]]:
        """Find path between two variants if one exists."""
        # Check if to_id is descendant of from_id
        descendants = self.get_descendants(from_id)
        if to_id in descendants:
            # Build path forward
            path = [from_id]
            current = from_id
            
            while current != to_id:
                # Find child that leads to to_id
                for child in self.parent_to_children.get(current, []):
                    if child == to_id or to_id in self.get_descendants(child):
                        path.append(child)
                        current = child
                        break
            
            return path
        
        # Check if to_id is ancestor of from_id
        ancestors = self.get_ancestors(from_id)
        if to_id in ancestors:
            # Build path backward
            path = [from_id]
            current = from_id
            
            while current != to_id:
                parent = self.child_to_parent.get(current)
                if parent:
                    path.append(parent)
                    current = parent
                else:
                    break
            
            return path
        
        return None


# === 6. SEQUENCE GENERATOR === -----------------------------------------------

class SequenceGenerator:
    """Main class for generating protein sequences from mutations."""
    
    def __init__(self, df: pd.DataFrame, strict_mutation_validation: bool = True):
        self.df = df
        self.navigator = LineageNavigator(df)
        self.manipulator = SequenceManipulator()
        self.strict_mutation_validation = strict_mutation_validation
        self._update_ground_truths()
    
    def _update_ground_truths(self) -> None:
        """Update the set of variants with known sequences."""
        self.ground_truth_ids = set(
            self.df[
                self.df["protein_sequence"].notna() & 
                (self.df["protein_sequence"].str.strip() != "")
            ]["enzyme_id"]
        )
    
    def find_best_ground_truth(
        self, 
        variant_id: str, 
        has_complex_mutation: bool
    ) -> Tuple[str, str]:
        """
        Find the best ground truth sequence to use for generation.
        
        Returns:
            (ground_truth_id, direction) where direction is 'up' or 'down'
        """
        # Get variant info
        variant_row = self.df[self.df["enzyme_id"] == variant_id].iloc[0]
        parent_id = variant_row.get("parent_enzyme_id")
        
        # Check for self-referential parent first
        if parent_id and parent_id.strip() and parent_id == variant_id:
            log.warning(f"Self-referential parent detected for {variant_id}")
            return "", ""
        
        # Check for circular dependency
        if parent_id and parent_id.strip():  # Only check if parent_id is not empty
            parent_rows = self.df[self.df["enzyme_id"] == parent_id]
            if not parent_rows.empty:
                parent_parent_id = parent_rows.iloc[0].get("parent_enzyme_id")
                if parent_parent_id and parent_parent_id.strip() and parent_parent_id == variant_id:
                    log.warning(f"Circular dependency detected: {variant_id} <-> {parent_id}")
                    return "", ""
        
        # Check direct parent
        if parent_id in self.ground_truth_ids:
            if not has_complex_mutation:
                return parent_id, "up"
        
        # Check direct children
        direct_children = self.navigator.parent_to_children.get(variant_id, [])
        child_gts = [c for c in direct_children if c in self.ground_truth_ids]
        
        if child_gts:
            if has_complex_mutation:
                return child_gts[0], "down"
            elif parent_id not in self.ground_truth_ids:
                return child_gts[0], "down"
        
        # Check all descendants
        descendants = self.navigator.get_descendants(variant_id)
        desc_gts = [d for d in descendants if d in self.ground_truth_ids]
        
        # Check all ancestors
        ancestors = self.navigator.get_ancestors(variant_id)
        anc_gts = [a for a in ancestors if a in self.ground_truth_ids]
        
        # Prioritize based on mutation type
        if has_complex_mutation and desc_gts:
            return desc_gts[0], "down"
        
        if has_complex_mutation and parent_id in self.ground_truth_ids:
            return parent_id, "up"
        
        # Return closest ground truth
        if anc_gts:
            return anc_gts[0], "up"
        if desc_gts:
            return desc_gts[0], "down"
        
        return "", ""
    
    def generate_from_parent(
        self, 
        variant_id: str, 
        parent_id: str
    ) -> Optional[SequenceGenerationResult]:
        """Generate sequence by applying mutations to parent."""
        # Get the variant to find its campaign
        variant_rows = self.df[self.df["enzyme_id"] == variant_id]
        if variant_rows.empty:
            return None
        
        variant_row = variant_rows.iloc[0]
        variant_campaign = variant_row.get("campaign_id", "")
        mutations = variant_row.get("mutations", "")
        
        if not mutations:
            return None
        
        # Find parent in the same campaign first
        parent_rows = self.df[
            (self.df["enzyme_id"] == parent_id) & 
            (self.df["campaign_id"] == variant_campaign)
        ]
        
        # If not found in same campaign, fall back to any parent with that ID
        if parent_rows.empty:
            parent_rows = self.df[self.df["enzyme_id"] == parent_id]
            if not parent_rows.empty:
                log.warning(f"Parent {parent_id} not found in same campaign {variant_campaign} for variant {variant_id}, using parent from different campaign")
        
        if parent_rows.empty:
            log.error(f"Parent {parent_id} not found for variant {variant_id}")
            return None
        
        parent_row = parent_rows.iloc[0]
        parent_seq = parent_row.get("protein_sequence", "")
        parent_campaign = parent_row.get("campaign_id", "")
        
        if not parent_seq:
            return None
        
        # Log which parent sequence is being used
        if parent_campaign != variant_campaign:
            log.info(f"Using parent {parent_id} from campaign {parent_campaign} for variant {variant_id} in campaign {variant_campaign}")
        else:
            log.info(f"Using parent {parent_id} from same campaign {variant_campaign} for variant {variant_id}")
        
        sequence, mutations_successful = self.manipulator.apply_mutations(parent_seq, mutations)
        
        if not mutations_successful:
            # Check if this might be an exact match case (mutations already present in parent)
            # This happens when an enzyme from another campaign is identified as both parent and exact match
            if parent_id == variant_id or (mutations and parent_seq == sequence):
                log.info(f"Detected exact match scenario for {variant_id} - using parent sequence directly")
                sequence = parent_seq
                mutations_successful = True
            elif self.strict_mutation_validation:
                log.error(f"STRICT MODE: Failed to apply mutations for {variant_id}: mutation mismatch detected. Not populating sequence to prevent incorrect data.")
                return None
            else:
                log.warning(f"Mutation mismatch for {variant_id}, but proceeding with generated sequence (strict_mutation_validation=False)")
                # Continue with the sequence even if mutations failed
        
        return SequenceGenerationResult(
            sequence=sequence,
            method="from_parent",
            source_id=parent_id,
            confidence=1.0
        )
    
    def generate_from_child(
        self, 
        variant_id: str, 
        child_id: str
    ) -> Optional[SequenceGenerationResult]:
        """Generate sequence by reversing mutations from child."""
        child_row = self.df[self.df["enzyme_id"] == child_id].iloc[0]
        child_seq = child_row.get("protein_sequence", "")
        child_mutations = child_row.get("mutations", "")
        
        if not child_seq or not child_mutations:
            return None
        
        sequence = self.manipulator.reverse_mutations(child_seq, child_mutations)
        
        return SequenceGenerationResult(
            sequence=sequence,
            method="from_child",
            source_id=child_id,
            confidence=0.9
        )
    
    def generate_sequence(self, variant_id: str) -> Optional[SequenceGenerationResult]:
        """Generate sequence for a variant using the best available method."""
        log.debug(f"Generating sequence for {variant_id}")
        
        # Check if already has sequence
        variant_row = self.df[self.df["enzyme_id"] == variant_id].iloc[0]
        if variant_row.get("protein_sequence", "").strip():
            return SequenceGenerationResult(
                sequence=variant_row["protein_sequence"],
                method="existing",
                source_id=variant_id,
                confidence=1.0
            )
        
        # Get variant info
        parent_id = variant_row.get("parent_enzyme_id")
        mutations = variant_row.get("mutations", "")
        
        log.debug(f"Variant {variant_id}: parent={parent_id}, mutations={mutations}")
        
        # Check for complex mutations
        complex_muts = MutationParser.detect_complex_mutations(mutations) if mutations else []
        has_complex = bool(complex_muts)
        
        # Find best ground truth
        gt_id, direction = self.find_best_ground_truth(variant_id, has_complex)
        
        if not gt_id:
            log.warning(f"No suitable ground truth found for {variant_id}")
            return None
        
        log.info(f"Using {gt_id} as ground truth ({direction} direction) for {variant_id}")
        
        # Generate based on direction
        if direction == "up" and parent_id and mutations:
            # Always try the declared parent first
            result = self.generate_from_parent(variant_id, parent_id)
            if result:
                return result
            
            # If declared parent fails, try the ground truth (if different)
            if gt_id != parent_id:
                log.info(f"Declared parent {parent_id} failed for {variant_id}, trying ground truth {gt_id}")
                result = self.generate_from_parent(variant_id, gt_id)
                if result:
                    result.confidence = 0.7
                    result.notes = "Generated from non-direct ancestor"
                return result
        else:  # down or no parent/mutations
            direct_children = self.navigator.parent_to_children.get(variant_id, [])
            if gt_id in direct_children:
                return self.generate_from_child(variant_id, gt_id)
            else:
                # Try to find path through direct child
                path = self.navigator.find_path(variant_id, gt_id)
                if path and len(path) > 1:
                    direct_child = path[1]
                    result = self.generate_from_child(variant_id, direct_child)
                    if result:
                        result.confidence = 0.8
                        result.notes = f"Generated via path through {direct_child}"
                    return result
        
        return None


# === 7. GEMINI PARENT IDENTIFICATION === ------------------------------------

def make_gemini_request_with_timeout(model, prompt: str, timeout_seconds: int = 60, max_retries: int = 1) -> Optional[str]:
    """
    Make a Gemini API request with timeout and retry logic.
    
    Args:
        model: The Gemini model instance
        prompt: The prompt to send
        timeout_seconds: Timeout in seconds (default: 60 seconds = 1 minute)
        max_retries: Maximum number of retries (default: 1)
    
    Returns:
        Response text or None if all attempts failed
    """
    for attempt in range(max_retries + 1):
        try:
            # Use ThreadPoolExecutor to implement timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(model.generate_content, prompt)
                
                try:
                    # Wait for the response with timeout
                    response = future.result(timeout=timeout_seconds)
                    return response.text.strip()
                    
                except TimeoutError:
                    log.warning(f"Gemini API request timed out after {timeout_seconds} seconds (attempt {attempt + 1}/{max_retries + 1})")
                    future.cancel()
                    
                    # If this was the last attempt, return None
                    if attempt == max_retries:
                        log.error(f"Gemini API request failed after {max_retries + 1} attempts due to timeout")
                        return None
                    
                    # Wait a bit before retrying
                    wait_time = 5 * (attempt + 1)  # Exponential backoff: 5s, 10s, 15s...
                    log.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    
        except Exception as e:
            log.warning(f"Gemini API request failed with error: {e} (attempt {attempt + 1}/{max_retries + 1})")
            
            if attempt == max_retries:
                log.error(f"Gemini API request failed after {max_retries + 1} attempts")
                return None
            
            # Wait before retrying
            wait_time = 5 * (attempt + 1)
            log.info(f"Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
    
    return None


def identify_parents_with_gemini(df: pd.DataFrame) -> pd.DataFrame:
    """Use Gemini API to identify parent enzymes for entries with missing parent information."""
    if not GEMINI_OK:
        log.warning("Gemini API not available (missing google.generativeai). Skipping parent identification.")
        return df
    
    if not GEMINI_API_KEY:
        log.warning("GEMINI_API_KEY not set. Skipping parent identification.")
        return df
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        log.warning(f"Failed to configure Gemini API: {e}. Skipping parent identification.")
        return df
    
    # Find entries with empty sequences but missing parent information
    entries_needing_parents = []
    for idx, row in df.iterrows():
        protein_sequence = str(row.get("protein_sequence", "")).strip()
        parent_id = str(row.get("parent_enzyme_id", "")).strip()
        
        # Only process entries that have empty sequences AND no parent info
        if (not protein_sequence or protein_sequence.lower() in ["nan", "none", ""]) and (not parent_id or parent_id.lower() in ["nan", "none", ""]):
            enzyme_id = str(row.get("enzyme_id", ""))
            campaign_id = str(row.get("campaign_id", ""))
            generation = str(row.get("generation", ""))
            
            entries_needing_parents.append({
                "idx": idx,
                "enzyme_id": enzyme_id,
                "campaign_id": campaign_id,
                "generation": generation
            })
    
    if not entries_needing_parents:
        log.info("No entries need parent identification from Gemini")
        return df
    
    log.info(f"Found {len(entries_needing_parents)} entries needing parent identification. Querying Gemini...")
    
    # Create a lookup of all available enzyme IDs for context
    available_enzymes = {}
    for idx, row in df.iterrows():
        enzyme_id = str(row.get("enzyme_id", ""))
        campaign_id = str(row.get("campaign_id", ""))
        protein_sequence = str(row.get("protein_sequence", "")).strip()
        generation = str(row.get("generation", ""))
        
        if enzyme_id and enzyme_id.lower() != "nan":
            available_enzymes[enzyme_id] = {
                "campaign_id": campaign_id,
                "has_sequence": bool(protein_sequence and protein_sequence.lower() not in ["nan", "none", ""]),
                "generation": generation
            }
    
    identified_count = 0
    total_entries = len(entries_needing_parents)
    log.info(f"Starting Gemini parent identification for {total_entries} entries...")
    
    for i, entry in enumerate(entries_needing_parents):
        enzyme_id = entry["enzyme_id"]
        campaign_id = entry["campaign_id"]
        generation = entry["generation"]
        
        # Log progress
        if i % 5 == 0:
            log.info(f"Processing parent identification {i+1}/{total_entries}: {enzyme_id}")
        
        # Create context for Gemini
        context_info = []
        context_info.append(f"Enzyme ID: {enzyme_id}")
        context_info.append(f"Campaign ID: {campaign_id}")
        if generation:
            context_info.append(f"Generation: {generation}")
        
        # Add available enzymes from the same campaign for context
        campaign_enzymes = []
        for enz_id, enz_data in available_enzymes.items():
            if enz_data["campaign_id"] == campaign_id:
                status = "with sequence" if enz_data["has_sequence"] else "without sequence"
                gen_info = f"(gen {enz_data['generation']})" if enz_data["generation"] else ""
                campaign_enzymes.append(f"  - {enz_id} {status} {gen_info}")
        
        if campaign_enzymes:
            context_info.append("Available enzymes in same campaign:")
            context_info.extend(campaign_enzymes[:10])  # Limit to first 10 for context
        
        context_text = "\n".join(context_info)
        
        prompt = f"""Identify the parent enzyme for {enzyme_id}.

Available enzymes in campaign {campaign_id}:
{chr(10).join(campaign_enzymes[:5])}

Based on enzyme naming patterns, what is the parent?

Respond with ONLY: Parent: [enzyme_id]
If unknown: Parent: Unknown"""
        
        # Use the timeout helper function
        response_text = make_gemini_request_with_timeout(model, prompt)
        
        if response_text:
            # Parse the response
            parent_match = re.search(r'Parent:\s*([^\n]+)', response_text)
            
            if parent_match:
                parent = parent_match.group(1).strip()
                if parent and parent != "Unknown" and parent != "No parent identified":
                    # Prevent self-referential parent assignment
                    if parent == enzyme_id:
                        log.warning(f"Gemini suggested self-referential parent for {enzyme_id}, ignoring")
                        continue
                    # Verify the parent exists in our available enzymes
                    if parent in available_enzymes:
                        df.at[entry["idx"], "parent_enzyme_id"] = parent
                        identified_count += 1
                        log.info(f"Identified parent for {enzyme_id}: {parent}")
                    else:
                        log.warning(f"Gemini suggested parent {parent} for {enzyme_id}, but it's not in available enzymes")
        else:
            log.warning(f"Failed to get response from Gemini for {enzyme_id} after retries")
    
    if identified_count > 0:
        log.info(f"Successfully identified {identified_count} parent enzymes using Gemini API")
    else:
        log.info("No parent enzymes were identified using Gemini API")
    
    return df


# === 8. SEQUENCE SOURCE IDENTIFICATION === -----------------------------------

def identify_sequence_sources_with_gemini(df: pd.DataFrame, debug_dir: Optional[Path] = None) -> pd.DataFrame:
    """Use Gemini API to identify which parent sequences to use for entries with missing sequences."""
    if not GEMINI_OK:
        log.warning("Gemini API not available (missing google.generativeai). Skipping sequence source identification.")
        return df
    
    if not GEMINI_API_KEY:
        log.warning("GEMINI_API_KEY not set. Skipping sequence source identification.")
        return df
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        log.warning(f"Failed to configure Gemini API: {e}. Skipping sequence source identification.")
        return df
    
    # Group by campaign to process each campaign separately
    campaigns = df['campaign_id'].unique()
    
    for campaign_id in campaigns:
        if pd.isna(campaign_id):
            campaign_mask = df['campaign_id'].isna()
            campaign_id_str = "unknown"
        else:
            campaign_mask = df['campaign_id'] == campaign_id
            campaign_id_str = str(campaign_id)
        
        campaign_df = df[campaign_mask]
        
        # Find entries with empty sequences in this campaign
        empty_seq_entries = []
        available_seq_entries = []
        
        for idx, row in campaign_df.iterrows():
            enzyme_id = str(row.get("enzyme_id", ""))
            protein_sequence = str(row.get("protein_sequence", "")).strip()
            parent_id = str(row.get("parent_enzyme_id", "")).strip()
            mutations = str(row.get("mutations", "")).strip()
            generation = str(row.get("generation", ""))
            
            if not protein_sequence or protein_sequence.lower() in ["nan", "none", ""]:
                empty_seq_entries.append({
                    "idx": idx,
                    "enzyme_id": enzyme_id,
                    "parent_id": parent_id if parent_id != "nan" else None,
                    "mutations": mutations if mutations != "nan" else None,
                    "generation": generation
                })
            else:
                available_seq_entries.append({
                    "enzyme_id": enzyme_id,
                    "generation": generation,
                    "seq_length": len(protein_sequence)
                })
        
        # Skip if no empty sequences
        if not empty_seq_entries:
            continue
        
        # Check if this is a partially empty situation (some have sequences, some don't)
        total_entries = len(campaign_df)
        empty_count = len(empty_seq_entries)
        
        log.info(f"Campaign {campaign_id_str}: {empty_count}/{total_entries} entries have empty sequences")
        
        if empty_count == total_entries:
            # All sequences are empty - try to find cross-campaign relationships
            log.info(f"Campaign {campaign_id_str}: All sequences are empty ({empty_count}/{total_entries}). "
                     f"Searching for cross-campaign parent relationships...")
            
            # Get all enzymes with sequences from OTHER campaigns
            other_campaigns_with_seqs = []
            for other_campaign in campaigns:
                if other_campaign == campaign_id or pd.isna(other_campaign):
                    continue
                other_mask = df['campaign_id'] == other_campaign
                other_df = df[other_mask]
                
                for idx, row in other_df.iterrows():
                    protein_sequence = str(row.get("protein_sequence", "")).strip()
                    if protein_sequence and protein_sequence.lower() not in ["nan", "none", ""]:
                        enzyme_id = str(row.get("enzyme_id", ""))
                        generation = str(row.get("generation", ""))
                        other_campaigns_with_seqs.append({
                            "enzyme_id": enzyme_id,
                            "campaign_id": str(other_campaign),
                            "generation": generation,
                            "seq_length": len(protein_sequence)
                        })
            
            if not other_campaigns_with_seqs:
                log.info(f"Campaign {campaign_id_str}: No sequences found in other campaigns to use as cross-campaign parents")
                continue
            
            # Create context for cross-campaign analysis
            context_lines = []
            context_lines.append(f"Empty Campaign: {campaign_id_str} (all {empty_count} enzymes need sequences)")
            context_lines.append(f"\nEnzymes in empty campaign:")
            for entry in empty_seq_entries[:10]:  # Limit for context
                parent_info = f", parent: {entry['parent_id']}" if entry['parent_id'] else ", no parent info"
                mut_info = f", mutations: {entry['mutations'][:50]}..." if entry['mutations'] and len(entry['mutations']) > 50 else f", mutations: {entry['mutations']}" if entry['mutations'] else ""
                context_lines.append(f"  - {entry['enzyme_id']} (gen {entry['generation']}{parent_info}{mut_info})")
            
            context_lines.append(f"\nEnzymes with sequences from OTHER campaigns ({len(other_campaigns_with_seqs)}):")
            for entry in other_campaigns_with_seqs[:15]:  # Limit for context
                # Get the actual sequence for this enzyme
                enzyme_rows = df[df['enzyme_id'] == entry['enzyme_id']]
                if not enzyme_rows.empty:
                    sequence = str(enzyme_rows.iloc[0]['protein_sequence'])
                    context_lines.append(f"  - {entry['enzyme_id']} from {entry['campaign_id']} (gen {entry['generation']}, sequence: {sequence})")
                else:
                    context_lines.append(f"  - {entry['enzyme_id']} from {entry['campaign_id']} (gen {entry['generation']}, {entry['seq_length']} aa)")
            
            context_text = "\n".join(context_lines)
            
            # Find ONE good cross-campaign seed to bootstrap this campaign
            log.info(f"Campaign {campaign_id_str}: Looking for ONE cross-campaign seed to bootstrap sequences...")
            
            # Create a simpler prompt
            prompt = f"""Find ONE enzyme match between campaigns.

Empty campaign {campaign_id_str} enzymes (need sequences):
{chr(10).join([f"- {e['enzyme_id']}" for e in empty_seq_entries[:5]])}

Other campaign enzymes WITH sequences:
{chr(10).join([f"- {e['enzyme_id']} from {e['campaign_id']}" for e in other_campaigns_with_seqs[:10]])}

Find the BEST matching pair. Prioritize:
1. EXACT name matches (e.g., BORG1 in empty campaign matches BORG1 with sequence)
2. Similar enzyme names

For exact name matches, use the SAME enzyme_id for both target and source.

Return JSON:
{{
  "seed_enzyme": {{
    "target_enzyme_id": "enzyme from empty campaign",
    "source": {{
      "enzyme_id": "matching enzyme with sequence"
    }}
  }}
}}"""
                
            try:
                log.info(f"Campaign {campaign_id_str}: Making Gemini API request for cross-campaign seed...")
                
                # Save debug information if debug_dir is provided
                if debug_dir:
                    import time
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    prompt_file = debug_dir / f"cross_campaign_seed_{campaign_id_str}_prompt_{timestamp}.txt"
                    prompt_file.write_text(prompt)
                
                # Use the timeout helper function
                response_text = make_gemini_request_with_timeout(model, prompt)
                
                # Save response if debug_dir is provided
                if debug_dir and response_text:
                    response_file = debug_dir / f"cross_campaign_seed_{campaign_id_str}_response_{timestamp}.txt"
                    response_file.write_text(response_text)
                
                # Parse the JSON response
                import json
                if response_text:
                    try:
                        # Clean the response text if it contains markdown
                        if '```json' in response_text:
                            response_text = response_text.split('```json')[1].split('```')[0].strip()
                        elif '```' in response_text:
                            response_text = response_text.split('```')[1].split('```')[0].strip()
                        
                        seed_data = json.loads(response_text)
                        seed_info = seed_data.get('seed_enzyme', {})
                        
                        if seed_info:
                            target_enzyme_id = seed_info.get('target_enzyme_id', '')
                            relationship_type = seed_info.get('relationship_type', '').upper()
                            source_info = seed_info.get('source', {})
                            source_enzyme_id = source_info.get('enzyme_id', '')
                            source_campaign_id = source_info.get('campaign_id', '')
                            confidence = float(seed_info.get('confidence', 0.5))
                            reason = seed_info.get('reason', '')
                            
                            # Clean up enzyme IDs in case they contain extra text
                            if ' from ' in source_enzyme_id:
                                source_enzyme_id = source_enzyme_id.split(' from ')[0].strip()
                            if ' from ' in target_enzyme_id:
                                target_enzyme_id = target_enzyme_id.split(' from ')[0].strip()
                            
                            # Debug logging
                            log.debug(f"Parsed seed data: target={target_enzyme_id}, source={source_enzyme_id}, source_campaign={source_campaign_id}")
                        
                            log.info(f"Campaign {campaign_id_str}: Found seed - {target_enzyme_id} from {source_enzyme_id} from campaign {source_campaign_id} ({relationship_type}, confidence: {confidence})")
                            log.info(f"Reason: {reason}")
                            
                            if source_enzyme_id:
                                # Find the source enzyme's sequence in the dataframe
                                # Prefer sequences from OTHER campaigns (not the current empty campaign)
                                source_rows = df[df['enzyme_id'] == source_enzyme_id]
                                if source_rows.empty:
                                    log.warning(f"Source enzyme {source_enzyme_id} not found in dataframe")
                                else:
                                    # Look for a row with a sequence, preferring other campaigns
                                    source_sequence = None
                                    source_row_idx = None
                                    
                                    # First, try to find a row with sequence from a different campaign
                                    for idx, row in source_rows.iterrows():
                                        seq = str(row['protein_sequence']).strip()
                                        if seq and seq.lower() not in ["nan", "none", ""]:
                                            # Check if this is from a different campaign
                                            if row['campaign_id'] != campaign_id:
                                                source_sequence = seq
                                                source_row_idx = idx
                                                log.info(f"Found source sequence for {source_enzyme_id} from campaign {row['campaign_id']}")
                                                break
                                
                                    # If not found in other campaigns, try any row with sequence
                                    if not source_sequence:
                                        for idx, row in source_rows.iterrows():
                                            seq = str(row['protein_sequence']).strip()
                                            if seq and seq.lower() not in ["nan", "none", ""]:
                                                source_sequence = seq
                                                source_row_idx = idx
                                                log.info(f"Found source sequence for {source_enzyme_id} from same campaign {row['campaign_id']}")
                                                break
                                
                                    if not source_sequence:
                                        log.warning(f"Source enzyme {source_enzyme_id} has no sequence in any campaign")
                                    else:
                                        # Find the target enzyme in our empty list
                                        seed_found = False
                                        
                                        # First check if this is a same-name match (e.g., BORG1 -> BORG1)
                                        if target_enzyme_id == source_enzyme_id:
                                            # This is an exact name match across campaigns
                                            for entry in empty_seq_entries:
                                                if entry['enzyme_id'] == target_enzyme_id:
                                                    # Direct copy for exact match
                                                    df.at[entry['idx'], 'protein_sequence'] = source_sequence
                                                    current_flag = str(df.at[entry['idx'], 'flag']) if pd.notna(df.at[entry['idx'], 'flag']) else ""
                                                    df.at[entry['idx'], 'flag'] = current_flag + " gemini_cross_campaign_exact_name"
                                                    log.info(f"Set seed sequence for {target_enzyme_id} from exact name match in another campaign (length: {len(source_sequence)})")
                                                    seed_found = True
                                                    break
                                        
                                        # Otherwise look for the target normally
                                        if not seed_found:
                                            log.debug(f"Looking for target_enzyme_id='{target_enzyme_id}' in empty_seq_entries")
                                            for entry in empty_seq_entries:
                                                log.debug(f"Comparing '{entry['enzyme_id']}' == '{target_enzyme_id}': {entry['enzyme_id'] == target_enzyme_id}")
                                                if entry['enzyme_id'] == target_enzyme_id:
                                                    if relationship_type == "EXACT_MATCH":
                                                        # Exact match - copy sequence directly
                                                        df.at[entry['idx'], 'protein_sequence'] = source_sequence
                                                        current_flag = str(df.at[entry['idx'], 'flag']) if pd.notna(df.at[entry['idx'], 'flag']) else ""
                                                        df.at[entry['idx'], 'flag'] = current_flag + " gemini_cross_campaign_seed_exact"
                                                        log.info(f"Set seed sequence for {target_enzyme_id} from exact match {source_enzyme_id} (length: {len(source_sequence)})")
                                                        seed_found = True
                                                        
                                                    elif relationship_type == "BEST_PARENT":
                                                        # Parent relationship - apply mutations to get the target sequence
                                                        target_mutations = entry.get('mutations', '').strip()
                                                        if target_mutations:
                                                            # Apply mutations using SequenceManipulator
                                                            manipulator = SequenceManipulator()
                                                            mutated_sequence, success = manipulator.apply_mutations(source_sequence, target_mutations)
                                                            
                                                            if success:
                                                                df.at[entry['idx'], 'protein_sequence'] = mutated_sequence
                                                                current_flag = str(df.at[entry['idx'], 'flag']) if pd.notna(df.at[entry['idx'], 'flag']) else ""
                                                                df.at[entry['idx'], 'flag'] = current_flag + " gemini_cross_campaign_seed_parent"
                                                                log.info(f"Set seed sequence for {target_enzyme_id} by applying mutations {target_mutations} to parent {source_enzyme_id} (length: {len(mutated_sequence)})")
                                                                seed_found = True
                                                            else:
                                                                log.warning(f"Failed to apply mutations {target_mutations} to parent {source_enzyme_id} for {target_enzyme_id}")
                                                        else:
                                                            # No mutations - use parent sequence directly
                                                            df.at[entry['idx'], 'protein_sequence'] = source_sequence
                                                            current_flag = str(df.at[entry['idx'], 'flag']) if pd.notna(df.at[entry['idx'], 'flag']) else ""
                                                            df.at[entry['idx'], 'flag'] = current_flag + " gemini_cross_campaign_seed_parent_no_mutations"
                                                            log.info(f"Set seed sequence for {target_enzyme_id} from parent {source_enzyme_id} (no mutations, length: {len(source_sequence)})")
                                                            seed_found = True
                                                    break
                                        
                                        if seed_found:
                                            log.info(f"Campaign {campaign_id_str}: Successfully set cross-campaign seed. Local processing will handle the rest.")
                                        else:
                                            # Debug: log what's in empty_seq_entries
                                            available_ids = [e['enzyme_id'] for e in empty_seq_entries]
                                            log.warning(f"Campaign {campaign_id_str}: Could not find target enzyme {target_enzyme_id} in empty list. Available: {available_ids}")
                
                    except json.JSONDecodeError as e:
                        log.warning(f"Failed to parse JSON response for cross-campaign seed: {e}")
                        log.debug(f"Response text: {response_text}")
                else:
                    log.warning(f"Failed to get response from Gemini for cross-campaign seed identification after retries")
                
            except Exception as e:
                log.warning(f"Failed to identify cross-campaign seed for {campaign_id_str}: {e}")
            continue
        
        log.info(f"Campaign {campaign_id_str}: Found {empty_count}/{total_entries} entries with empty sequences. "
                 f"Querying Gemini for sequence sources...")
        
        # Create context for Gemini
        context_lines = []
        context_lines.append(f"Campaign: {campaign_id_str}")
        context_lines.append(f"\nEnzymes WITH sequences ({len(available_seq_entries)}):")
        for entry in available_seq_entries[:15]:  # Limit to first 15 for context
            context_lines.append(f"  - {entry['enzyme_id']} (gen {entry['generation']}, {entry['seq_length']} aa)")
        
        context_lines.append(f"\nEnzymes WITHOUT sequences ({len(empty_seq_entries)}):")
        for entry in empty_seq_entries[:15]:  # Limit to first 15 for context
            parent_info = f", parent: {entry['parent_id']}" if entry['parent_id'] else ", no parent info"
            mut_info = f", mutations: {entry['mutations'][:50]}..." if entry['mutations'] and len(entry['mutations']) > 50 else f", mutations: {entry['mutations']}" if entry['mutations'] else ""
            context_lines.append(f"  - {entry['enzyme_id']} (gen {entry['generation']}{parent_info}{mut_info})")
        
        context_text = "\n".join(context_lines)
        
        # Process all empty sequences in a single request
        identified_count = 0
        
        # Create request for all empty sequences
        request_list = []
        for entry in empty_seq_entries[:20]:  # Limit to first 20 to avoid overly long prompts
            parent_info = f", parent: {entry['parent_id']}" if entry['parent_id'] else ""
            mut_info = f", mutations: {entry['mutations'][:30]}" if entry['mutations'] else ""
            request_list.append(f"{entry['enzyme_id']} (gen {entry['generation']}{parent_info}{mut_info})")
        
        prompt = f"""Match enzymes without sequences to enzymes with sequences.

Campaign: {campaign_id_str}

Need sequences for:
{chr(10).join(request_list)}

Available with sequences:
{chr(10).join([f"- {e['enzyme_id']}" for e in available_seq_entries[:15]])}

For each enzyme needing sequence, provide source:
enzyme_id -> source_enzyme_id
Use "None" if no match."""
        
        try:
            log.info(f"Campaign {campaign_id_str}: Making single Gemini API request for {len(empty_seq_entries)} enzymes...")
            
            # Save debug information if debug_dir is provided
            if debug_dir:
                import time
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                prompt_file = debug_dir / f"sequence_source_{campaign_id_str}_prompt_{timestamp}.txt"
                prompt_file.write_text(prompt)
            
            # Use the timeout helper function
            response_text = make_gemini_request_with_timeout(model, prompt)
            
            # Save response if debug_dir is provided
            if debug_dir and response_text:
                response_file = debug_dir / f"sequence_source_{campaign_id_str}_response_{timestamp}.txt"
                response_file.write_text(response_text)
            
            # Parse the response
            if response_text:
                for line in response_text.split('\n'):
                    if '->' in line:
                        parts = line.split('->')
                        if len(parts) == 2:
                            target_enzyme = parts[0].strip()
                            source_enzyme = parts[1].strip()
                            
                            if source_enzyme and source_enzyme != "None":
                                # Find the target enzyme in our list
                                for entry in empty_seq_entries:
                                    if entry['enzyme_id'] == target_enzyme:
                                        # Verify the source enzyme exists and has a sequence
                                        source_rows = df[df['enzyme_id'] == source_enzyme]
                                        if not source_rows.empty:
                                            source_seq = source_rows.iloc[0]['protein_sequence']
                                            if source_seq and str(source_seq).strip() and str(source_seq) != "nan":
                                                # Update the parent_enzyme_id if it's missing
                                                if not entry['parent_id']:
                                                    df.at[entry['idx'], 'parent_enzyme_id'] = source_enzyme
                                                    df.at[entry['idx'], 'flag'] = df.at[entry['idx'], 'flag'] + " gemini_suggested_parent"
                                                    identified_count += 1
                                                    log.info(f"Set {source_enzyme} as parent for {target_enzyme} (Gemini suggestion)")
                                                elif entry['parent_id'] != source_enzyme:
                                                    # Log if Gemini suggests a different parent than what's recorded
                                                    log.info(f"Gemini suggests {source_enzyme} as source for {target_enzyme}, "
                                                           f"but parent is recorded as {entry['parent_id']}")
                                        break
                
        except Exception as e:
            log.warning(f"Failed to identify sequence sources: {e}")
        
        if identified_count > 0:
            log.info(f"Campaign {campaign_id_str}: Successfully identified {identified_count} sequence sources using Gemini")
    
    return df


# === 9. MAIN PROCESSOR === ---------------------------------------------------

class SequenceProcessor:
    """Main processor for handling the complete workflow."""
    
    def __init__(self, input_csv: Path, output_csv: Path, debug_dir: Optional[Path] = None, strict_mutation_validation: bool = True):
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.debug_dir = debug_dir
        self.strict_mutation_validation = strict_mutation_validation
        self.df = None
        self.generator = None
    
    def load_data(self) -> None:
        """Load and prepare the input data."""
        self.df = pd.read_csv(self.input_csv, keep_default_na=False)
        
        # Detect and handle column format automatically
        self._normalize_columns()
        
        # Translate DNA sequences to protein sequences if needed
        self._translate_dna_sequences()
        
        log.info(
            f"Loaded {len(self.df)} rows, "
            f"{sum(self.df['protein_sequence'].str.strip() == '')} empty sequences"
        )
        
        # Ensure required columns exist
        if "flag" not in self.df.columns:
            self.df["flag"] = ""
        
        # Initialize generator
        self.generator = SequenceGenerator(self.df, strict_mutation_validation=self.strict_mutation_validation)
    
    def _translate_dna_sequences(self) -> None:
        """Translate DNA sequences to protein sequences if no amino acid sequences exist."""
        manipulator = SequenceManipulator()
        
        # First check if ANY sequences are amino acid sequences
        has_amino_acid = False
        for idx, row in self.df.iterrows():
            seq = str(row.get("protein_sequence", "")).strip()
            if seq and seq.lower() not in ["nan", "none", ""]:
                if not manipulator.is_dna_sequence(seq):
                    has_amino_acid = True
                    break
        
        # If we found amino acid sequences, don't translate anything
        if has_amino_acid:
            log.info("Found amino acid sequences in data, skipping DNA translation")
            return
        
        # No amino acid sequences found, check for DNA sequences in dna_seq column
        if "dna_seq" in self.df.columns:
            dna_count = 0
            for idx, row in self.df.iterrows():
                protein_seq = str(row.get("protein_sequence", "")).strip()
                dna_seq = str(row.get("dna_seq", "")).strip()
                
                # If protein_sequence is empty but dna_seq has content, translate it
                if (not protein_seq or protein_seq.lower() in ["nan", "none", ""]) and \
                   (dna_seq and dna_seq.lower() not in ["nan", "none", ""]):
                    if manipulator.is_dna_sequence(dna_seq):
                        # Translate DNA to protein
                        translated_seq = manipulator.translate_dna_to_protein(dna_seq)
                        self.df.at[idx, "protein_sequence"] = translated_seq
                        
                        # Add flag to indicate this was translated from DNA
                        if "flag" not in self.df.columns:
                            self.df["flag"] = ""
                        existing_flag = str(self.df.at[idx, "flag"]).strip()
                        self.df.at[idx, "flag"] = f"{existing_flag} dna_translated".strip()
                        dna_count += 1
            
            if dna_count > 0:
                log.info(f"Translated {dna_count} DNA sequences from dna_seq column to protein sequences")
        
        # Also check if DNA sequences are mistakenly in protein_sequence column
        dna_count = 0
        for idx, row in self.df.iterrows():
            seq = str(row.get("protein_sequence", "")).strip()
            if seq and seq.lower() not in ["nan", "none", ""]:
                if manipulator.is_dna_sequence(seq):
                    # Translate DNA to protein
                    protein_seq = manipulator.translate_dna_to_protein(seq)
                    self.df.at[idx, "protein_sequence"] = protein_seq
                    
                    # Add flag to indicate this was translated from DNA
                    existing_flag = str(self.df.at[idx, "flag"]).strip()
                    self.df.at[idx, "flag"] = f"{existing_flag} dna_translated".strip()
                    dna_count += 1
        
        if dna_count > 0:
            log.info(f"Translated {dna_count} DNA sequences to protein sequences")
    
    def _normalize_columns(self) -> None:
        """Automatically detect and normalize column names from different formats."""
        # Check if this is enzyme_lineage_extractor format
        if "variant_id" in self.df.columns:
            log.info("Detected enzyme_lineage_extractor format, converting columns...")
            
            # Rename columns
            column_mapping = {
                "variant_id": "enzyme_id",
                "parent_id": "parent_enzyme_id",
                "aa_seq": "protein_sequence"
            }
            
            self.df = self.df.rename(columns=column_mapping)
            
            # Convert mutation format from semicolon to comma-separated
            if "mutations" in self.df.columns:
                self.df["mutations"] = self.df["mutations"].str.replace(";", ",")
            
            log.info("Column conversion complete")
        
        # Verify required columns exist
        required_columns = ["enzyme_id", "parent_enzyme_id", "mutations", "protein_sequence"]
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        
        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}. "
                f"Found columns: {list(self.df.columns)}"
            )
    
    def flag_complex_mutations(self) -> None:
        """Flag variants with complex mutations."""
        complex_count = 0
        
        for idx, row in self.df.iterrows():
            if row.get("mutations", ""):
                complex_muts = MutationParser.detect_complex_mutations(row["mutations"])
                if complex_muts:
                    self.df.at[idx, "flag"] = "complex_mutation"
                    complex_count += 1
                    log.info(
                        f"Variant {row['enzyme_id']} has complex mutations: {complex_muts}"
                    )
        
        log.info(f"Flagged {complex_count} variants with complex mutations")
    
    def process_simple_mutations(self) -> None:
        """Process variants with simple point mutations."""
        processed = 0
        
        for idx, row in self.df.iterrows():
            # Skip if already has sequence or has complex mutations
            if (row.get("protein_sequence", "").strip() or 
                "complex_mutation" in str(row.get("flag", ""))):
                continue
            
            variant_id = row["enzyme_id"]
            result = self.generator.generate_sequence(variant_id)
            
            if result and result.method == "from_parent":
                self.df.at[idx, "protein_sequence"] = result.sequence
                
                # Check for unexpected length changes
                parent_seq = self.df[
                    self.df["enzyme_id"] == result.source_id
                ]["protein_sequence"].iloc[0]
                
                if len(result.sequence) != len(parent_seq):
                    self.df.at[idx, "flag"] = "unexpected_length_change"
                    log.warning(
                        f"Unexpected length change for {variant_id} "
                        f"with standard mutations"
                    )
                
                processed += 1
        
        log.info(f"Processed {processed} variants with simple mutations")
    
    def process_complex_mutations(self) -> None:
        """Process variants with complex mutations."""
        complex_variants = self.df[
            self.df["flag"].str.contains("complex_mutation", na=False)
        ]["enzyme_id"].tolist()
        
        log.info(f"Processing {len(complex_variants)} variants with complex mutations")
        
        processed = 0
        for variant_id in complex_variants:
            idx = self.df[self.df["enzyme_id"] == variant_id].index[0]
            
            if self.df.at[idx, "protein_sequence"]:
                continue
            
            result = self.generator.generate_sequence(variant_id)
            
            if result:
                self.df.at[idx, "protein_sequence"] = result.sequence
                
                # Check length changes
                parent_id = self.df.at[idx, "parent_enzyme_id"]
                parent_row = self.df[self.df["enzyme_id"] == parent_id]
                
                if not parent_row.empty and parent_row.iloc[0]["protein_sequence"]:
                    parent_seq = parent_row.iloc[0]["protein_sequence"]
                    if len(result.sequence) != len(parent_seq):
                        self.df.at[idx, "flag"] = "complex_mutation length_change"
                        log.info(
                            f"Length change for {variant_id}: "
                            f"{len(parent_seq)} -> {len(result.sequence)}"
                        )
                
                processed += 1
        
        log.info(f"Processed {processed} complex mutation variants")
    
    def process_remaining(self) -> None:
        """Process any remaining variants."""
        # Update ground truths with newly generated sequences
        self.generator._update_ground_truths()
        
        remaining = self.df[
            self.df["protein_sequence"].str.strip() == ""
        ]["enzyme_id"].tolist()
        
        if not remaining:
            return
        
        log.info(f"Processing {len(remaining)} remaining variants: {remaining}")
        
        # Sort by generation if available
        if "generation" in self.df.columns:
            remaining.sort(
                key=lambda x: self.df[
                    self.df["enzyme_id"] == x
                ]["generation"].iloc[0] if x in self.df["enzyme_id"].values else float('inf')
            )
        
        processed = 0
        max_iterations = len(remaining) * 2  # Prevent infinite loops
        iteration = 0
        
        for variant_id in remaining:
            iteration += 1
            if iteration > max_iterations:
                log.warning(f"Stopping process_remaining after {max_iterations} iterations to prevent infinite loop")
                break
                
            idx = self.df[self.df["enzyme_id"] == variant_id].index[0]
            
            if self.df.at[idx, "protein_sequence"]:
                continue
            
            log.debug(f"Attempting to generate sequence for {variant_id} (iteration {iteration})")
            result = self.generator.generate_sequence(variant_id)
            
            if result:
                self.df.at[idx, "protein_sequence"] = result.sequence
                
                # Add generation method to flag
                method_flag = f"generated_{result.method}"
                if result.confidence < 1.0:
                    method_flag += f"_conf{result.confidence:.1f}"
                
                existing_flag = self.df.at[idx, "flag"]
                self.df.at[idx, "flag"] = f"{existing_flag} {method_flag}".strip()
                
                processed += 1
                
                # Update ground truths for next iterations
                self.generator._update_ground_truths()
        
        log.info(f"Processed {processed} remaining variants")
    
    def backward_pass(self) -> None:
        """Work backward from terminal variants to fill remaining gaps."""
        missing = self.df[
            self.df["protein_sequence"].str.strip() == ""
        ]["enzyme_id"].tolist()
        
        if not missing:
            return
        
        log.info(
            f"Backward pass: attempting to fill {len(missing)} remaining sequences"
        )
        
        # Find terminal variants (no children) with sequences
        all_parents = set(self.df["parent_enzyme_id"].dropna())
        terminal_variants = [
            v for v in self.generator.ground_truth_ids 
            if v not in all_parents
        ]
        
        log.info(f"Found {len(terminal_variants)} terminal variants with sequences")
        
        # Sort missing by generation (latest first)
        if "generation" in self.df.columns:
            missing.sort(
                key=lambda x: self.df[
                    self.df["enzyme_id"] == x
                ]["generation"].iloc[0] if x in self.df["enzyme_id"].values else 0,
                reverse=True
            )
        
        processed = 0
        for variant_id in missing:
            idx = self.df[self.df["enzyme_id"] == variant_id].index[0]
            
            if self.df.at[idx, "protein_sequence"]:
                continue
            
            result = self.generator.generate_sequence(variant_id)
            
            if result:
                self.df.at[idx, "protein_sequence"] = result.sequence
                self.df.at[idx, "flag"] += " backward_from_terminal"
                processed += 1
                
                # Update ground truths
                self.generator._update_ground_truths()
        
        log.info(f"Backward pass: filled {processed} sequences")
    
    def save_results(self) -> None:
        """Save the processed data."""
        # Final statistics
        empty_final = sum(self.df["protein_sequence"].str.strip() == "")
        length_changes = sum(self.df["flag"].str.contains("length_change", na=False))
        complex_mutations = sum(self.df["flag"].str.contains("complex_mutation", na=False))
        
        log.info(
            f"Final results: {len(self.df)} rows, {empty_final} empty, "
            f"{complex_mutations} complex mutations, {length_changes} length changes"
        )
        
        # Save to CSV
        self.df.to_csv(self.output_csv, index=False)
        log.info(f"Saved results to {self.output_csv}")
    
    def run(self) -> None:
        """Run the complete processing pipeline with campaign-based processing."""
        log.info("Starting sequence generation pipeline")
        
        # Load data
        self.load_data()
        
        # Process each campaign separately
        campaigns = self.df['campaign_id'].unique()
        log.info(f"Processing {len(campaigns)} campaigns: {list(campaigns)}")
        
        for campaign_id in campaigns:
            if pd.isna(campaign_id):
                campaign_id = "unknown"
            
            log.info(f"Processing campaign: {campaign_id}")
            
            # Filter data for this campaign
            campaign_mask = self.df['campaign_id'] == campaign_id
            if pd.isna(campaign_id):
                campaign_mask = self.df['campaign_id'].isna()
            
            # Store original dataframe
            original_df = self.df
            
            # Process only this campaign's data
            self.df = self.df[campaign_mask].copy()
            
            # Rebuild relationships for this campaign
            self.generator = SequenceGenerator(self.df, strict_mutation_validation=self.strict_mutation_validation)
            
            # Flag complex mutations
            self.flag_complex_mutations()
            
            # Process in order
            self.process_simple_mutations()
            self.process_complex_mutations()
            self.process_remaining()
            self.backward_pass()
            
            # Use Gemini to identify parent enzymes for entries with missing sequences
            log.info(f"Identifying parents with Gemini for campaign: {campaign_id}")
            self.df = identify_parents_with_gemini(self.df)
            
            # Rebuild relationships after parent identification
            self.generator = SequenceGenerator(self.df, strict_mutation_validation=self.strict_mutation_validation)
            
            # Try to fill sequences again after parent identification
            log.info(f"Attempting to fill sequences after parent identification for campaign: {campaign_id}")
            self.process_remaining()
            
            # Update the original dataframe with results
            original_df.loc[campaign_mask, :] = self.df
            
            # Restore original dataframe
            self.df = original_df
            
            log.info(f"Completed campaign: {campaign_id}")
        
        # After processing all campaigns, check for any remaining empty sequences
        # and use Gemini to identify sequence sources (including cross-campaign relationships)
        empty_count = sum(self.df["protein_sequence"].str.strip() == "")
        total_count = len(self.df)
        
        if empty_count > 0:
            log.info(f"Found {empty_count}/{total_count} empty sequences after initial processing. "
                     "Using Gemini to identify sequence sources (including cross-campaign relationships)...")
            self.df = identify_sequence_sources_with_gemini(self.df, self.debug_dir)
            
            # Process campaigns again after identifying new parent relationships
            log.info("Reprocessing campaigns after sequence source identification...")
            
            for campaign_id in campaigns:
                if pd.isna(campaign_id):
                    campaign_id = "unknown"
                
                log.info(f"Reprocessing campaign: {campaign_id}")
                
                # Filter data for this campaign
                campaign_mask = self.df['campaign_id'] == campaign_id
                if pd.isna(campaign_id):
                    campaign_mask = self.df['campaign_id'].isna()
                
                # Store original dataframe
                original_df = self.df
                
                # Process only this campaign's data
                self.df = self.df[campaign_mask].copy()
                
                # Rebuild relationships for this campaign
                self.generator = SequenceGenerator(self.df, strict_mutation_validation=self.strict_mutation_validation)
                
                # Try to fill sequences again
                self.process_remaining()
                
                # Update the original dataframe with results
                original_df.loc[campaign_mask, :] = self.df
                
                # Restore original dataframe
                self.df = original_df
                
                log.info(f"Completed reprocessing campaign: {campaign_id}")
        
        # Save results
        self.save_results()
        
        log.info("Pipeline completed")


# === 8. CLI INTERFACE === ----------------------------------------------------

def setup_logging(verbose: int = 0) -> None:
    """Configure logging based on verbosity level."""
    if verbose >= 2:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(argv: Optional[List[str]] = None) -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="cleanup_sequence_structured",
        description="Generate protein sequences from mutation data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input_csv",
        type=Path,
        help="Input CSV file with enzyme lineage data"
    )
    parser.add_argument(
        "output_csv",
        type=Path,
        help="Output CSV file with generated sequences"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (use -vv for debug output)"
    )
    parser.add_argument(
        "--debug-dir",
        type=Path,
        help="Directory to save debug information (Gemini prompts and responses)"
    )
    parser.add_argument(
        "--allow-mutation-mismatches",
        action="store_true",
        help="Allow sequence generation even when mutations don't match (default: strict validation)"
    )
    
    args = parser.parse_args(argv)
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Process the data (format detection is automatic)
    strict_validation = not args.allow_mutation_mismatches
    processor = SequenceProcessor(
        args.input_csv, 
        args.output_csv, 
        getattr(args, 'debug_dir', None),
        strict_mutation_validation=strict_validation
    )
    processor.run()


if __name__ == "__main__":
    main()