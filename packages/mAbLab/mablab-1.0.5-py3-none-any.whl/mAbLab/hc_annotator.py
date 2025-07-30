from antpack import SingleChainAnnotator, VJGeneTool, SequenceScoringTool
import Levenshtein
import copy
from . import fc_constants as Fc
from . import common_methods as cm

class AnnotateHC:
    """
    A class to annotate heavy chains (HC) of antibodies.

    Attributes:
        input_aa (str): Input amino acid sequence.
        germlines (_InferGermline): Germline inference results.
        analysis_results (_HC): Heavy chain analysis results.
    """

    def __init__(self, aa_sequence: str = None) -> None:
        """
        Initialize the AnnotateHC object with an amino acid sequence.

        Args:
            aa_sequence (str): Amino acid sequence of the heavy chain.
        """
        self.input_aa = aa_sequence
        self.germlines = self._InferGermline(self.input_aa)
        self.analysis_results = self._HC(self.input_aa)

    class _HC:
        """
        A class to analyze the heavy chain (HC) of an antibody.

        Attributes:
            isotype (str): Isotype of the antibody.
            allotype (str): Allotype of the antibody.
            subclass (str): Subclass of the antibody.
            hc (_DomainObj): Heavy chain domain object.
            fc (_DomainObj): Fc domain object.
            fd (_DomainObj): Fd domain object.
            hinge (_DomainObj): Hinge domain object.
            vh (_DomainObj): Variable heavy chain domain object.
            ch1 (_DomainObj): CH1 domain object.
            ch2 (_DomainObj): CH2 domain object.
            ch3 (_DomainObj): CH3 domain object.
            cdr1 (_CDRObj): CDR1 object.
            cdr2 (_CDRObj): CDR2 object.
            cdr3 (_CDRObj): CDR3 object.
            input_hc_sequence (str): Input heavy chain sequence.
            reference_fc_sequence (str): Reference Fc sequence.
            aligned_reference_fc_sequence (str): Aligned reference Fc sequence.
            aligned_input_fc_sequence (str): Aligned input Fc sequence.
            levenshtein_ratio (float): Levenshtein ratio for sequence alignment.
            inferred_chain_type (str): Inferred chain type.
            inferred_chain_percent_id (float): Inferred chain percent identity.
            analysis_errors (str): Analysis errors.
            fc_mutations (_MutationObj): Fc mutations.
            hinge_is_modified (bool): Whether the hinge is modified.
        """

        def __init__(self, aa_sequence: str = None) -> None:
            """
            Initialize the _HC object with an amino acid sequence.

            Args:
                aa_sequence (str): Amino acid sequence of the heavy chain.
            """
            self.isotype = str
            self.allotype = str
            self.subclass = str
            self.hc = self._DomainObj()
            self.fc = self._DomainObj()
            self.fd = self._DomainObj()
            self.hinge = self._DomainObj()
            self.vh = self._DomainObj()
            self.ch1 = self._DomainObj()
            self.ch2 = self._DomainObj()
            self.ch3 = self._DomainObj()
            self.cdr1 = self._CDRObj()
            self.cdr2 = self._CDRObj()
            self.cdr3 = self._CDRObj()
            self.input_hc_sequence = aa_sequence
            self.reference_fc_sequence = str
            self.aligned_reference_fc_sequence = str
            self.aligned_input_fc_sequence = str
            self.levenshtein_ratio = float
            self.inferred_chain_type = str
            self.inferred_chain_percent_id = float
            self.analysis_errors = str
            self.fc_mutations = self._MutationObj()
            self.hinge_is_modified = False
            self._reference_hinge_len = int
            self._align_to_nearest_reference_fc()
            self._number_and_annotate_hc()

        class _MutationObj:
            """
            A class to represent mutations in the Fc region.

            Attributes:
                deletion (_MutationSystemObj): Deletions in the Fc region.
                insertion (_MutationSystemObj): Insertions in the Fc region.
                mutation (_MutationSystemObj): Point mutations in the Fc region.
            """

            def __init__(self) -> None:
                """
                Initialize the _MutationObj object.
                """
                self.deletion = self._MutationSystemObj()
                self.insertion = self._MutationSystemObj()
                self.mutation = self._MutationSystemObj()

            class _MutationSystemObj:
                """
                A class to represent a mutation system object.

                Attributes:
                    imgt (list): IMGT numbering for mutations.
                    eu (list): EU numbering for mutations.
                    kabat (list): Kabat numbering for mutations.
                    martin (list): Martin numbering for mutations.
                    aho (list): AHO numbering for mutations.
                """

                def __init__(self) -> None:
                    """
                    Initialize the _MutationSystemObj object.
                    """
                    self.imgt = []
                    self.eu = []
                    self.kabat = []
                    self.martin = []
                    self.aho = []

                def __len__(self) -> int:
                    """
                    Get the length of the mutation system object.

                    Returns:
                        int: Maximum length of the mutation lists.
                    """
                    return max(len(self.imgt), len(self.eu), len(self.kabat), len(self.martin), len(self.aho))

        class _DomainObj:
            """
            A class to represent a domain object.

            Attributes:
                sequence (str): Sequence of the domain.
                numbering (_NumberingSystemObj): Numbering system object.
                annotation (_NumberingSystemObj): Annotation system object.
            """

            def __init__(self) -> None:
                """
                Initialize the _DomainObj object.
                """
                self.sequence = str
                self.numbering = self._NumberingSystemObj()
                self.annotation = self._NumberingSystemObj()

            class _NumberingSystemObj:
                """
                A class to represent a numbering system object.

                Attributes:
                    imgt (list): IMGT numbering.
                    eu (list): EU numbering.
                    kabat (list): Kabat numbering.
                    martin (list): Martin numbering.
                    aho (list): AHO numbering.
                """

                def __init__(self) -> None:
                    """
                    Initialize the _NumberingSystemObj object.
                    """
                    self.imgt = []
                    self.eu = []
                    self.kabat = []
                    self.martin = []
                    self.aho = []

            def collapse_aa_sequence_numbering_and_annotation(self):
                if self.sequence is None or len(self.sequence) < 1:
                    return
                
                del_idx = [index for index, value in enumerate(self.sequence) if value == '-']
                
                def _remove_by_index(item_lst):
                    if item_lst is None:
                        return item_lst
                    
                    for idx in reversed(del_idx):
                        if len(item_lst) >= idx:
                            del item_lst[idx]
                    return item_lst
                
                self.sequence = ''.join(_remove_by_index(list(self.sequence)))
                self.numbering.imgt = _remove_by_index(self.numbering.imgt )
                self.numbering.eu = _remove_by_index(self.numbering.eu)
                self.numbering.kabat = _remove_by_index(self.numbering.kabat)
                self.numbering.martin = _remove_by_index(self.numbering.martin)
                self.numbering.aho = _remove_by_index(self.numbering.aho)
                self.annotation.imgt = _remove_by_index(self.annotation.imgt)
                self.annotation.eu = _remove_by_index(self.annotation.eu)
                self.annotation.kabat = _remove_by_index(self.annotation.kabat)
                self.annotation.martin = _remove_by_index(self.annotation.martin)
                self.annotation.aho = _remove_by_index(self.annotation.aho)
                return
            

        class _CDRObj(_DomainObj):
            """
            A class to represent a CDR object.

            Attributes:
                sequence (_CDRSchemeObj): CDR scheme object.
            """

            def __init__(self) -> None:
                """
                Initialize the _CDRObj object.
                """
                super().__init__()
                self.sequence = self._CDRSchemeObj()

            class _CDRSchemeObj:
                """
                A class to represent a CDR scheme object.

                Attributes:
                    imgt (list): IMGT CDR scheme.
                    eu (list): EU CDR scheme.
                    kabat (list): Kabat CDR scheme.
                    martin (list): Martin CDR scheme.
                    aho (list): AHO CDR scheme.
                """

                def __init__(self) -> None:
                    """
                    Initialize the _CDRSchemeObj object.
                    """
                    self.imgt = []
                    self.eu = []
                    self.kabat = []
                    self.martin = []
                    self.aho = []

        def _align_to_nearest_reference_fc(self) -> None:
            """
            Align the input heavy chain to the nearest Fc reference sequence.
            Defines object properties such as isotype, subclass, and Fc alignment.
            """
            
            def _isotype_by_hinge_match(hc_sequence: str) -> None:
                '''match hinge sequence to identify isotype.  This is ther prefred method to caputre the hinge start index'''
                
                # Match Full Hinge
                for hinge in Fc.hinge:
                    if hinge['sequence'] in hc_sequence:
                        self.isotype = hinge['name']
                        self.hinge_is_modified = False
                        return
                # Else Match 7-mer of hinge
                for hinge in Fc.hinge:
                    for i in range(0, len(hinge['sequence'])-7):
                        segment = hinge['sequence'][i:i+7]
                        if segment in hc_sequence:
                            self.isotype = hinge['name']
                            self.hinge_is_modified = True
                            return
                self.isotype = None
                self.hinge_is_modified = None
                return
            
            def _find_nearest_fc_reference_match_by_alignment(hc_sequence: str) -> None:
                '''Find Nearest Fc Reference Sequence. If hinge is modified this method requires blind truncation and may lead to errors if the Fc has c-terminal fusions or significant modifications'''
                
                def _truncate_input_sequence(hc_sequence: str) -> str:
                    '''truncate HC to Fc by hinge match or by max reference FC length'''
                    if self.hinge_is_modified is False:
                        for hinge in Fc.hinge:
                            if hinge['name'] == self.isotype:
                                return  hc_sequence[hc_sequence.index(hinge['sequence']):]
                    else:
                        max_len = 0
                        for seq in Fc.sequences:
                            fc_seq = seq['sequence']
                            max_len = len(fc_seq) if len(fc_seq) > max_len else max_len
                        max_len += 10
                        return hc_sequence[-1*max_len:] if max_len <= len(hc_sequence) else hc_sequence
                    return
                
                def _get_reference_sequence_by_levenshtein_ratio(truncated_input_sequence: str) -> str:
                    '''Calculate levenshtein ratio and select nearest Fc match'''
                    ratios = []
                    all_fc_seq_dicts = []
                    # Calc Levenshtein ratios
                    for seq in Fc.sequences:
                        ratios.append(Levenshtein.ratio(seq['sequence'], truncated_input_sequence))
                        all_fc_seq_dicts.append(seq)
                    # Identify best Fc Match and add calculated ratio to object
                    max_idx = ratios.index(max(ratios))
                    reference_fc_dict = all_fc_seq_dicts[max_idx]
                    self.levenshtein_ratio = ratios[max_idx]
                    # Prepare Reference Fc for alignment
                    hinge_start_idx = reference_fc_dict['hinge_start_idx']
                    self.isotype = reference_fc_dict['isotype']
                    self.allotype = reference_fc_dict['allotype']
                    self.subclass = reference_fc_dict['subclass']
                    self._reference_hinge_len = reference_fc_dict['hinge_len']
                    self.reference_fc_sequence = reference_fc_dict['sequence'][hinge_start_idx:]
                    return self.reference_fc_sequence
                
                def _align_input_fc_to_reference_fc(truncated_input_sequence: str, truncated_reference_sequence: str) -> None:
                    '''aligns similarly sized sequences via biopython pairwise aligner'''
                    # Align input sequence to top matched reference sequence
                    aligned_ref_seq, aligned_input_seq = cm.pairwise_sequence_alignment(truncated_reference_sequence, truncated_input_sequence)
                    # Trim Aligned Sequences to begin at first Hinge residue
                    ref_start_idx = aligned_ref_seq.index(truncated_reference_sequence[0])
                    self.aligned_reference_fc_sequence = aligned_ref_seq[ref_start_idx:]
                    self.aligned_input_fc_sequence = aligned_input_seq[ref_start_idx:] 
                    return
                    
                # Entry Point
                truncated_input_sequence = _truncate_input_sequence(hc_sequence)
                truncated_reference_sequence = _get_reference_sequence_by_levenshtein_ratio(truncated_input_sequence)
                _align_input_fc_to_reference_fc(truncated_input_sequence, truncated_reference_sequence)
                return
            
            # Entry Point
            _isotype_by_hinge_match(self.input_hc_sequence)
            _find_nearest_fc_reference_match_by_alignment(self.input_hc_sequence)
            return
            
            
        def _number_and_annotate_hc(self) -> None:
            """
            Number and annotate the heavy chain.
            """
                       
            def _get_input_hinge() -> tuple:
                '''Define self.hinge object'''
                hinge_obj = None
                for hinge in Fc.hinge:
                    if hinge['name'] == self.isotype:
                        hinge_obj = hinge
                        
                if hinge_obj is None:
                    raise ValueError("Hinge definition for isotype does not exist in '_Fc_seq.py' ")
                
                count =  0
                idx = 0             
                while count < self._reference_hinge_len:
                    if self.aligned_reference_fc_sequence[idx] != '-':
                        self.hinge.numbering.imgt.append(hinge_obj['imgt'][count])
                        self.hinge.numbering.eu.append(hinge_obj['eu'][count])
                        self.hinge.numbering.kabat.append(hinge_obj['kabat'][count])
                        count += 1
                    else:
                        self.hinge.numbering.imgt.append('-')
                        self.hinge.numbering.eu.append('-')
                        self.hinge.numbering.kabat.append('-')
                    idx += 1

                self.hinge.sequence = self.aligned_input_fc_sequence[:len(self.hinge.numbering.imgt)]
                all_annotations = ['hinge'] * len(self.hinge.sequence)
                self.hinge.numbering.martin = None
                self.hinge.numbering.aho = None
                self.hinge.annotation.martin = None
                self.hinge.annotation.aho = None
                self.hinge.annotation.imgt = copy.deepcopy(all_annotations)
                self.hinge.annotation.eu = copy.deepcopy(all_annotations)
                self.hinge.annotation.kabat = copy.deepcopy(all_annotations)
                self.hinge.collapse_aa_sequence_numbering_and_annotation()
                if self.hinge_is_modified is None:
                    self.hinge_is_modified = True if len(self.hinge.sequence) != self._reference_hinge_len else False
                return 
                
                
            def _get_ref_domain(domain_name):
                dom = self._DomainObj()
                for f in Fc.constant_domains:
                    if f['isotype'] == self.isotype and f['name'] == domain_name:
                        dom.numbering.imgt = f['imgt']
                        dom.numbering.eu = f['eu']
                        dom.numbering.kabat = f['kabat']
                        dom.numbering.martin = None
                        dom.numbering.aho = None
                        dom.sequence = f['sequence']
                        all_annotations = [d + f' [{domain_name}]' for d in f['annotation']]
                        dom.annotation.imgt = all_annotations
                        dom.annotation.eu = all_annotations
                        dom.annotation.kabat = all_annotations
                        dom.annotation.martin = None
                        dom.annotation.aho = None
                        return dom
                raise ValueError ('Appropriate Reference constant domains in "_Fc_seq.py" are undefined!')
            
            def _get_input_vh():
                
                def _calculate(scheme):
                    aligner = SingleChainAnnotator(scheme = scheme)
                    annotation = aligner.analyze_seq(self.input_hc_sequence)
                    numbering, self.inferred_chain_percent_id, chain, self.analysis_errors = annotation
                    self.inferred_chain_percent_id = self.inferred_chain_percent_id * 100
                    chain = chain.upper()
                    self.inferred_chain_type = 'HC' if chain == 'H' else 'Kappa LC' if chain == 'K' else 'Lambda LC' if chain == 'L' else 'unknown'
                    annotation = aligner.assign_cdr_labels(annotation)
                    vh_last_idx = len(annotation) - annotation[::-1].index('fmwk4') - 1
                    return ([str(n) for n in numbering[:vh_last_idx]], [d+' [VH]' for d in annotation[:vh_last_idx]])
                
                self.vh.numbering.imgt, self.vh.annotation.imgt = _calculate('imgt')
                self.vh.numbering.eu, self.vh.annotation.eu = _calculate('imgt')
                self.vh.numbering.kabat, self.vh.annotation.kabat = _calculate('kabat')
                self.vh.numbering.martin, self.vh.annotation.martin = _calculate('martin')
                self.vh.numbering.aho, self.vh.annotation.aho = _calculate('aho')
                self.vh.sequence = self.input_hc_sequence[:len(self.vh.numbering.imgt)]
                return
            
            def rectify_aligned_sequence_with_discriptor_list(aligned_seq: str, descriptor_lst: list) -> list:
                aligned_seq = list(aligned_seq)
                aligned_descriptor_lst = ['-'] * len(aligned_seq)
                desc_idx = 0
                for i in range(len(aligned_seq)):
                    if aligned_seq[i] != '-':
                        aligned_descriptor_lst[i] = str(descriptor_lst[desc_idx]) if desc_idx < len (descriptor_lst) else '-'
                        desc_idx += 1
                return aligned_descriptor_lst
            
            def _annotate_input_ch1(input_ch1_seq):
                ref_ch1_obj = _get_ref_domain('CH1')
                invalid = False
                if len(input_ch1_seq) < 1:
                    invalid = True
                aligned_ref_seq, aligned_input_seq = cm.pairwise_sequence_alignment(ref_ch1_obj.sequence, input_ch1_seq) if not invalid else (None,None)
                # Rectify annotation/numbering to aligned reference sequence
                ref_ch1_obj.sequence = aligned_ref_seq
                ref_ch1_obj.annotation.imgt = rectify_aligned_sequence_with_discriptor_list(aligned_ref_seq, ref_ch1_obj.annotation.imgt) if not invalid else None
                ref_ch1_obj.annotation.eu = rectify_aligned_sequence_with_discriptor_list(aligned_ref_seq, ref_ch1_obj.annotation.eu) if not invalid else None
                ref_ch1_obj.annotation.kabat = rectify_aligned_sequence_with_discriptor_list(aligned_ref_seq, ref_ch1_obj.annotation.kabat,) if not invalid else None
                ref_ch1_obj.numbering.eu = rectify_aligned_sequence_with_discriptor_list(aligned_ref_seq, ref_ch1_obj.numbering.eu) if not invalid else None
                ref_ch1_obj.numbering.imgt = rectify_aligned_sequence_with_discriptor_list(aligned_ref_seq, ref_ch1_obj.numbering.imgt) if not invalid else None
                ref_ch1_obj.numbering.kabat = rectify_aligned_sequence_with_discriptor_list(aligned_ref_seq, ref_ch1_obj.numbering.kabat) if not invalid else None
                # Rectify annotation/numbering to input_seq 
                self.ch1.annotation.imgt = copy.deepcopy(ref_ch1_obj.annotation.imgt) if not invalid else None
                self.ch1.annotation.eu = copy.deepcopy(ref_ch1_obj.annotation.eu) if not invalid else None
                self.ch1.annotation.kabat = copy.deepcopy(ref_ch1_obj.annotation.kabat)  if not invalid else None
                self.ch1.annotation.martin = None
                self.ch1.annotation.aho = None
                self.ch1.numbering.eu = copy.deepcopy(ref_ch1_obj.numbering.eu) if not invalid else None
                self.ch1.numbering.imgt = copy.deepcopy(ref_ch1_obj.numbering.imgt) if not invalid else None
                self.ch1.numbering.kabat = copy.deepcopy(ref_ch1_obj.numbering.kabat) if not invalid else None
                self.ch1.numbering.martin = None
                self.ch1.numbering.aho = None
                self.ch1.sequence = aligned_input_seq if not invalid else None
                # remove '-' from sequence and adjust corresponding annotations/numbering
                self.ch1.collapse_aa_sequence_numbering_and_annotation()
                return
            
            def _annotate_input_fc(input_fc_seq) -> tuple:
                
                def _detect_fc_mutations(aligned_ref_obj, aligned_input_obj):
                    ref_seq_lst = list(aligned_ref_obj.sequence)
                    input_seq_lst = list(aligned_input_obj.sequence)    
                    insertion_idx = [index+1 for index, value in enumerate(ref_seq_lst) if value == '-']
                    deletion_idx = [index for index, value in enumerate(input_seq_lst) if value == '-']
                    mutation_idx = []
                    
                    for i in range(len(ref_seq_lst)):
                        if ref_seq_lst[i] != input_seq_lst[i] and '-' not in [ref_seq_lst[i], input_seq_lst[i]]:
                            mutation_idx.append(i)
                    
                    for ins in insertion_idx:
                        ins = ins if ins < len(aligned_ref_obj.numbering.eu) else len(aligned_ref_obj.numbering.eu) -1 
                        aa = str(input_seq_lst[ins])
                        if aligned_ref_obj.numbering.eu is not None:
                            self.fc_mutations.insertion.eu.append({'name': f"{aligned_ref_obj.numbering.eu[ins]}{aa}", 'position': f"{aligned_ref_obj.numbering.eu[ins]}", 'amino_acid': aa})
                        if aligned_ref_obj.numbering.imgt is not None:
                            self.fc_mutations.insertion.imgt.append({'name': f"{aligned_ref_obj.numbering.imgt[ins]}{aa}", 'position': f"{aligned_ref_obj.numbering.imgt[ins]}", 'amino_acid': aa})
                        if aligned_ref_obj.numbering.kabat is not None:
                            self.fc_mutations.insertion.kabat.append({'name': f"{aligned_ref_obj.numbering.kabat[ins]}{aa}", 'position': f"{aligned_ref_obj.numbering.kabat[ins]}", 'amino_acid': aa})
                        if aligned_ref_obj.numbering.martin is not None:
                            self.fc_mutations.insertion.martin.append({'name': f"{aligned_ref_obj.numbering.martin[ins]}{aa}", 'position': f"{aligned_ref_obj.numbering.martin[ins]}", 'amino_acid': aa})
                        if aligned_ref_obj.numbering.aho is not None:
                            self.fc_mutations.insertion.aho.append({'name': f"{aligned_ref_obj.numbering.aho[ins]}{aa}", 'position': f"{aligned_ref_obj.numbering.aho[ins]}", 'amino_acid': aa})
                    
                    for d in deletion_idx:
                        aa = str(ref_seq_lst[d])
                        if aligned_ref_obj.numbering.eu is not None:
                            self.fc_mutations.deletion.eu.append({'name': f"{aligned_ref_obj.numbering.eu[d]}{aa}", 'position': f"{aligned_ref_obj.numbering.eu[d]}", 'amino_acid': aa})
                        if aligned_ref_obj.numbering.imgt is not None:
                            self.fc_mutations.deletion.imgt.append({'name': f"{aligned_ref_obj.numbering.imgt[d]}{aa}", 'position': f"{aligned_ref_obj.numbering.imgt[d]}", 'amino_acid': aa})
                        if aligned_ref_obj.numbering.kabat is not None:
                            self.fc_mutations.deletion.kabat.append({'name': f"{aligned_ref_obj.numbering.kabat[d]}{aa}", 'position': f"{aligned_ref_obj.numbering.kabat[d]}", 'amino_acid': aa})
                        if aligned_ref_obj.numbering.martin is not None:
                            self.fc_mutations.deletion.martin.append({'name': f"{aligned_ref_obj.numbering.martin[d]}{aa}", 'position': f"{aligned_ref_obj.numbering.martin[d]}", 'amino_acid': aa})
                        if aligned_ref_obj.numbering.aho is not None:
                            self.fc_mutations.deletion.aho.append({'name': f"{aligned_ref_obj.numbering.aho[d]}{aa}", 'position': f"{aligned_ref_obj.numbering.aho[d]}", 'amino_acid': aa})
                            
                    for m in mutation_idx:
                        ref_aa = str(ref_seq_lst[m])
                        mut_aa = str(input_seq_lst[m])
                        if aligned_ref_obj.numbering.eu is not None:
                            self.fc_mutations.mutation.eu.append({'name': f"{ref_aa}{aligned_ref_obj.numbering.eu[m]}{mut_aa}", 'position': f"{aligned_ref_obj.numbering.eu[m]}", 'reference_amino_acid': ref_aa, 'mutant_amino_acid': mut_aa})
                        if aligned_ref_obj.numbering.imgt is not None:
                            self.fc_mutations.mutation.imgt.append({'name': f"{ref_aa}{aligned_ref_obj.numbering.imgt[m]}{mut_aa}", 'position': f"{aligned_ref_obj.numbering.imgt[m]}", 'reference_amino_acid': ref_aa, 'mutant_amino_acid': mut_aa})
                        if aligned_ref_obj.numbering.kabat is not None:
                            self.fc_mutations.mutation.kabat.append({'name': f"{ref_aa}{aligned_ref_obj.numbering.kabat[m]}{mut_aa}", 'position': f"{aligned_ref_obj.numbering.kabat[m]}", 'reference_amino_acid': ref_aa, 'mutant_amino_acid': mut_aa})
                        if aligned_ref_obj.numbering.martin is not None:
                            self.fc_mutations.mutation.martin.append({'name': f"{ref_aa}{aligned_ref_obj.numbering.martin[m]}{mut_aa}", 'position': f"{aligned_ref_obj.numbering.martin[m]}", 'reference_amino_acid': ref_aa, 'mutant_amino_acid': mut_aa})
                        if aligned_ref_obj.numbering.aho is not None:
                            self.fc_mutations.mutation.aho.append({'name': f"{ref_aa}{aligned_ref_obj.numbering.aho[m]}{mut_aa}", 'position': f"{aligned_ref_obj.numbering.aho[m]}", 'reference_amino_acid': ref_aa, 'mutant_amino_acid': mut_aa})
                    return
                
                def _account_for_cterm_fusion(annotation_lst):
                    for i in reversed(range(len(annotation_lst))):
                        if annotation_lst[i] == '-':
                            annotation_lst[i] += ' [Fc-Fusion]'
                        else:
                            break
                    return annotation_lst
                
                ref_ch2_obj = _get_ref_domain('CH2')
                ref_ch3_obj = _get_ref_domain('CH3')
                
                # align reference and input sequences
                invalid = False
                if len(input_fc_seq) < 1:
                    invalid = True
                
                aligned_ref_seq, aligned_input_seq = cm.pairwise_sequence_alignment(ref_ch2_obj.sequence + ref_ch3_obj.sequence, input_fc_seq) if not invalid else (None,None)
                
                # build Fc reference Object
                ref_fc_obj = self._DomainObj()
                ref_fc_obj.sequence = aligned_ref_seq  if aligned_input_seq is not None else None
                ref_fc_obj.annotation.imgt = rectify_aligned_sequence_with_discriptor_list(aligned_ref_seq, ref_ch2_obj.annotation.imgt + ref_ch3_obj.annotation.imgt) if not invalid else None
                ref_fc_obj.annotation.eu = rectify_aligned_sequence_with_discriptor_list(aligned_ref_seq, ref_ch2_obj.annotation.eu + ref_ch3_obj.annotation.eu) if not invalid else None
                ref_fc_obj.annotation.kabat = rectify_aligned_sequence_with_discriptor_list(aligned_ref_seq, ref_ch2_obj.annotation.kabat + ref_ch3_obj.annotation.kabat) if not invalid else None
                ref_fc_obj.annotation.martin = None
                ref_fc_obj.annotation.aho = None
                ref_fc_obj.numbering.eu = rectify_aligned_sequence_with_discriptor_list(aligned_ref_seq, ref_ch2_obj.numbering.eu + ref_ch3_obj.numbering.eu) if not invalid else None
                ref_fc_obj.numbering.imgt = rectify_aligned_sequence_with_discriptor_list(aligned_ref_seq, ref_ch2_obj.numbering.imgt + ref_ch3_obj.numbering.imgt) if not invalid else None
                ref_fc_obj.numbering.kabat = rectify_aligned_sequence_with_discriptor_list(aligned_ref_seq, ref_ch2_obj.numbering.kabat + ref_ch3_obj.numbering.kabat) if not invalid else None
                ref_fc_obj.numbering.martin = None
                ref_fc_obj.numbering.aho = None

                # rectify annotations and numbering to input sequence
                self.fc.sequence = aligned_input_seq if not invalid else None
                self.fc.annotation.imgt = _account_for_cterm_fusion(copy.deepcopy(ref_fc_obj.annotation.imgt)) if not invalid else None
                self.fc.annotation.eu = _account_for_cterm_fusion(copy.deepcopy(ref_fc_obj.annotation.eu)) if not invalid else None
                self.fc.annotation.kabat = _account_for_cterm_fusion(copy.deepcopy(ref_fc_obj.annotation.kabat)) if not invalid else None
                self.fc.annotation.martin = None
                self.fc.annotation.aho = None
                self.fc.numbering.eu = copy.deepcopy(ref_fc_obj.numbering.eu) if not invalid else None
                self.fc.numbering.imgt = copy.deepcopy(ref_fc_obj.numbering.imgt) if not invalid else None
                self.fc.numbering.kabat = copy.deepcopy(ref_fc_obj.numbering.kabat) if not invalid else None
                self.fc.numbering.martin = None
                self.fc.numbering.aho = None
                                
                # Detect Fc Mutations
                if not invalid:
                    _detect_fc_mutations(ref_fc_obj, self.fc)
                    self.fc.collapse_aa_sequence_numbering_and_annotation()
                    ref_fc_obj.collapse_aa_sequence_numbering_and_annotation()
                return
            
            def _construct_ch2_ch3_objs():
                if self.fc.annotation.imgt is None:
                    return
                split_idx = 0
                for i in range(len(self.fc.annotation.imgt)):
                    if '[CH3]' in self.fc.annotation.imgt[i]:
                        split_idx = i
                        break
                self.ch2.sequence = self.fc.sequence[:split_idx]
                self.ch2.annotation.imgt = self.fc.annotation.imgt[:split_idx]
                self.ch2.annotation.eu = self.fc.annotation.eu[:split_idx]
                self.ch2.annotation.kabat = self.fc.annotation.kabat[:split_idx]
                self.ch2.annotation.martin = None
                self.ch2.annotation.aho = None
                self.ch2.numbering.eu = self.fc.numbering.eu[:split_idx]
                self.ch2.numbering.imgt = self.fc.numbering.imgt[:split_idx]
                self.ch2.numbering.kabat = self.fc.numbering.kabat[:split_idx]
                self.ch2.numbering.martin = None
                self.ch2.numbering.aho = None
                self.ch3.sequence = self.fc.sequence[split_idx:]
                self.ch3.annotation.imgt = self.fc.annotation.imgt[split_idx:]
                self.ch3.annotation.eu = self.fc.annotation.eu[split_idx:]
                self.ch3.annotation.kabat = self.fc.annotation.kabat[split_idx:]
                self.ch3.annotation.martin = None
                self.ch3.annotation.aho = None
                self.ch3.numbering.eu = self.fc.numbering.eu[split_idx:]
                self.ch3.numbering.imgt = self.fc.numbering.imgt[split_idx:]
                self.ch3.numbering.kabat = self.fc.numbering.kabat[split_idx:]
                self.ch3.numbering.martin = None
                self.ch3.numbering.aho = None
                return

            def _construct_fd_obj():
                if None in [self.vh.sequence , self.ch1.sequence]:
                    return
                    
                self.fd.sequence = self.vh.sequence + self.ch1.sequence
                self.fd.annotation.imgt = self.vh.annotation.imgt + self.ch1.annotation.imgt
                self.fd.annotation.eu = self.vh.annotation.eu + self.ch1.annotation.eu
                self.fd.annotation.kabat = self.vh.annotation.kabat + self.ch1.annotation.kabat
                self.fd.annotation.martin = self.vh.annotation.martin + ['-'] * len(self.ch1.annotation.kabat)
                self.fd.annotation.aho = self.vh.annotation.aho + ['-'] * len(self.ch1.annotation.kabat)
                self.fd.numbering.eu = self.vh.numbering.eu + self.ch1.numbering.eu
                self.fd.numbering.imgt = self.vh.numbering.imgt + self.ch1.numbering.imgt
                self.fd.numbering.kabat = self.vh.numbering.kabat + self.ch1.numbering.kabat
                self.fd.numbering.martin = self.vh.numbering.martin + ['-'] * len(self.ch1.numbering.kabat)
                self.fd.numbering.aho = self.vh.numbering.aho + ['-'] * len(self.ch1.numbering.kabat)
                return
            
            def _construct_hc_obj():
                if None in [self.fd.sequence , self.hinge.sequence , self.fc.sequence]:
                    return
                self.hc.sequence = self.fd.sequence + self.hinge.sequence + self.fc.sequence
                self.hc.annotation.imgt = self.fd.annotation.imgt + self.hinge.annotation.imgt + self.fc.annotation.imgt
                self.hc.annotation.eu = self.fd.annotation.eu + self.hinge.annotation.eu + self.fc.annotation.eu
                self.hc.annotation.kabat = self.fd.annotation.kabat + self.hinge.annotation.kabat + self.fc.annotation.kabat
                self.hc.annotation.martin = self.fd.annotation.martin + ['-'] * len(self.hinge.annotation.kabat) + ['-'] * len(self.fc.annotation.kabat)
                self.hc.annotation.aho = self.fd.annotation.aho + ['-'] * len(self.hinge.annotation.kabat) + ['-'] * len(self.fc.annotation.kabat)
                self.hc.numbering.eu = self.fd.numbering.eu + self.hinge.numbering.eu + self.fc.numbering.eu
                self.hc.numbering.imgt = self.fd.numbering.imgt + self.hinge.numbering.imgt + self.fc.numbering.imgt
                self.hc.numbering.kabat = self.fd.numbering.kabat + self.hinge.numbering.kabat + self.fc.numbering.kabat
                self.hc.numbering.martin = self.fd.numbering.martin + ['-'] * len(self.hinge.numbering.kabat) + ['-'] * len(self.fc.numbering.kabat)
                self.hc.numbering.aho = self.fd.numbering.aho + ['-'] * len(self.hinge.numbering.kabat) + ['-'] * len(self.fc.numbering.kabat)
                return
            
            def _construct_cdr_obj():
                scheme = [{'name': 'imgt', 'vh_numbering': self.vh.numbering.imgt, 'vh_annotation': self.vh.annotation.imgt},
                            {'name': 'eu', 'vh_numbering': self.vh.numbering.imgt, 'vh_annotation': self.vh.annotation.imgt},
                            {'name': 'martin', 'vh_numbering': self.vh.numbering.martin, 'vh_annotation': self.vh.annotation.martin},
                            {'name': 'kabat', 'vh_numbering': self.vh.numbering.kabat, 'vh_annotation': self.vh.annotation.kabat},
                            {'name': 'aho', 'vh_numbering': self.vh.numbering.aho, 'vh_annotation': self.vh.annotation.aho}]
        
                for s in scheme:
                    seq1 = []
                    num1 = []
                    annote1 = []
                    seq2 = []
                    num2 = []
                    annote2 = []
                    seq3 = []
                    num3 = []
                    annote3 = []
                    annotation = s['vh_annotation']
                    numbering = s['vh_numbering']
                    for i in range(len(self.vh.sequence)):
                        if 'cdr1' in annotation[i]:
                            seq1.append(self.vh.sequence[i])
                            num1.append(numbering[i])
                            annote1.append(annotation[i])
                        elif 'cdr2' in annotation[i]:
                            seq2.append(self.vh.sequence[i])
                            num2.append(numbering[i])
                            annote2.append(annotation[i])
                        elif 'cdr3' in annotation[i]:
                            seq3.append(self.vh.sequence[i])
                            num3.append(numbering[i])
                            annote3.append(annotation[i])
                    if s['name'] == 'imgt':
                        self.cdr1.sequence.imgt = seq1
                        self.cdr1.annotation.imgt = annote1
                        self.cdr1.numbering.imgt = num1
                        self.cdr2.sequence.imgt = seq2
                        self.cdr2.annotation.imgt = annote2
                        self.cdr2.numbering.imgt = num2
                        self.cdr3.sequence.imgt = seq3
                        self.cdr3.annotation.imgt = annote3
                        self.cdr3.numbering.imgt = num3
                    if s['name'] == 'eu':
                        self.cdr1.sequence.eu = seq1
                        self.cdr1.annotation.eu = annote1
                        self.cdr1.numbering.eu = num1
                        self.cdr2.sequence.eu = seq2
                        self.cdr2.annotation.eu = annote2
                        self.cdr2.numbering.eu = num2
                        self.cdr3.sequence.eu = seq3
                        self.cdr3.annotation.eu = annote3
                        self.cdr3.numbering.eu = num3
                    if s['name'] == 'kabat':
                        self.cdr1.sequence.kabat = seq1
                        self.cdr1.annotation.kabat = annote1
                        self.cdr1.numbering.kabat = num1
                        self.cdr2.sequence.kabat = seq2
                        self.cdr2.annotation.kabat = annote2
                        self.cdr2.numbering.kabat = num2
                        self.cdr3.sequence.kabat = seq3
                        self.cdr3.annotation.kabat = annote3
                        self.cdr3.numbering.kabat = num3
                    if s['name'] == 'martin':
                        self.cdr1.sequence.martin = seq1
                        self.cdr1.annotation.martin = annote1
                        self.cdr1.numbering.martin = num1
                        self.cdr2.sequence.martin = seq2
                        self.cdr2.annotation.martin = annote2
                        self.cdr2.numbering.martin = num2
                        self.cdr3.sequence.martin = seq3
                        self.cdr3.annotation.martin = annote3
                        self.cdr3.numbering.martin = num3
                    if s['name'] == 'aho':
                        self.cdr1.sequence.aho = seq1
                        self.cdr1.annotation.aho = annote1
                        self.cdr1.numbering.aho = num1
                        self.cdr2.sequence.aho = seq2
                        self.cdr2.annotation.aho = annote2
                        self.cdr2.numbering.aho = num2
                        self.cdr3.sequence.aho = seq3
                        self.cdr3.annotation.aho = annote3
                        self.cdr3.numbering.aho = num3
                return
            
            # Entry Point
            _get_input_hinge()
            input_fc_sequence = ''.join([aa for aa in self.aligned_input_fc_sequence if aa != '-'])
            input_fd_sequence = self.input_hc_sequence[:-1*len(input_fc_sequence)]
            input_fc_sequence = input_fc_sequence[len(self.hinge.sequence):]
            _get_input_vh()
            input_ch1_sequence = input_fd_sequence[len(self.vh.sequence):]
            _annotate_input_ch1(input_ch1_sequence)
            _annotate_input_fc(input_fc_sequence)
            _construct_ch2_ch3_objs()
            _construct_fd_obj()
            _construct_hc_obj()
            _construct_cdr_obj()
            return
            
        
    class _InferGermline:
        """
        A class to infer the germline of an antibody.

        Attributes:
            humanness (float): Humanness score.
            nearest_v_genes (list): Nearest V genes.
            v_gene_percent_id (float): V gene percent identity.
            nearest_j_genes (list): Nearest J genes.
            j_gene_percent_id (float): J gene percent identity.
            chain_is_passable_as_human (bool): Whether the chain is passable as human.
        """

        def __init__(self, aa_sequence: str = None) -> None:
            """
            Initialize the _InferGermline object with an amino acid sequence.

            Args:
                aa_sequence (str): Amino acid sequence of the heavy chain.
            """
            self.humanness = float
            self.nearest_v_genes = list
            self.v_gene_percent_id = float
            self.nearest_j_genes = list
            self.j_gene_percent_id = float
            self.chain_is_passable_as_human = bool
            self._calculate_germline(aa_sequence)

        def _calculate_germline(self, aa_sequence: str = None) -> None:
            """
            Calculate the germline of the heavy chain.

            Args:
                aa_sequence (str): Amino acid sequence of the heavy chain.
            """
            aligner = SingleChainAnnotator(scheme= 'imgt')
            annotation = aligner.analyze_seq(aa_sequence)
            
            vj_tool = VJGeneTool(database='imgt', scheme='imgt')
            self.nearest_v_genes, self.nearest_j_genes, self.v_gene_percent_id, self.j_gene_percent_id = vj_tool.assign_vj_genes(annotation, aa_sequence, "human", "identity")
            self.nearest_v_genes= self.nearest_v_genes.split('_')
            self.nearest_j_genes= self.nearest_j_genes.split('_')
            self.v_gene_percent_id = self.v_gene_percent_id * 100
            self.j_gene_percent_id = self.j_gene_percent_id * 100
                
            scoring_tool = SequenceScoringTool(offer_classifier_option = False, normalization = "none")
            humanness = scoring_tool.score_seqs(seq_list=[aa_sequence])
            self.humanness = float(humanness[0])
            self.chain_is_passable_as_human = True if humanness >=-100 else False
            return