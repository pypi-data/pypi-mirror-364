#!/usr/bin/env python3
"""
CER-based word alignment across languages.
ASR Metrics class for evaluating speech recognition performance.
"""

import logging
from collections import Counter
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from karma.metrics.base_metric_abs import BaseMetric
from karma.registries.metrics_registry import register_metric
# Import language-specific aligners
from karma.metrics.asr.base_aligner import BaseCERAligner
from karma.metrics.asr.lang.english_aligner import EnglishCERAligner
from karma.metrics.asr.lang.hindi_aligner import HindiCERAligner
logger = logging.getLogger(__name__)

@dataclass
class EvalResult:
    semantic_wer: float
    semantic_cer: float
    entity_wer: Optional[float] = None
    num_sentences: int = 0
    total_ref_words: int = 0
    additional_info: Optional[Dict] = None

@register_metric(
    name = "asr_semantic_metric",
#  required_args = ["language"]     #obtained from the dataset argument
)
class ASRSemanticMetrics(BaseMetric):
    def __init__(self, metric_name: str, language = "en", **kwargs):
        super().__init__(metric_name, **kwargs)
        self.language = language
        self.cer_threshold = 0.4

    @staticmethod
    def get_aligner(language: str, cer_threshold: float = 0.4) -> BaseCERAligner:
        """Factory function to get language-specific aligner."""
        aligners = {
            'english': EnglishCERAligner,
            'hindi': HindiCERAligner,
            'en': EnglishCERAligner,
            'hi': HindiCERAligner,
        }
        
        if language.lower() not in aligners:
            available = ', '.join(aligners.keys())
            raise ValueError(f"Unsupported language: {language}. Available: {available}")
        
        aligner = aligners[language.lower()](cer_threshold)
            # Add keyword WER method to the instance
        def calculate_keyword_wer(reference_text: str, reference_annotations: str, hypothesis_text: str):
            """Calculate keyword-specific WER using existing error rate calculation."""
            alignments = aligner.process_keywords_for_wer(
                reference_text, reference_annotations, hypothesis_text, aligner
            )
            results = aligner.calculate_error_rates(alignments)
            #aligner.print_alignment_visual(alignments) #enable for debugging
            return results
        
        # Bind the method to the aligner instance
        aligner.calculate_keyword_wer = calculate_keyword_wer
        
        return aligner

    @staticmethod
    def _process_utterance(args):
        """Helper function for multiprocessing - moved outside to make it picklable."""
        idx, ref, hyp, language, cer_threshold = args
        utt_id = f"utterance_{idx}"
        
        try:
            # Create aligner in the worker process to avoid pickling issues
            aligner = ASRSemanticMetrics.get_aligner(language, cer_threshold)
            alignments = aligner.align_words_dp(ref, hyp)
            
            # Calculate statistics
            stats = aligner.calculate_error_rates(alignments)
            
            # Calculate character-level statistics for weighted CER
            ref_chars = 0
            edit_distance = 0
            for alignment in alignments:
                if alignment.ref_words and alignment.hyp_words:
                    ref_text = ' '.join(alignment.ref_words)
                    chars = len(ref_text.replace(' ', ''))
                    ref_chars += chars
                    edit_distance += alignment.character_error_rate * chars
            
            return {
                'success': True,
                'utt_id': utt_id,
                'total_ref_words': stats['total_ref_words'],
                'word_correct': stats['word_correct'],
                'word_substitutions': stats['word_substitutions'],
                'word_deletions': stats['word_deletions'],
                'word_insertions': stats['word_insertions'],
                'ref_chars': ref_chars,
                'edit_distance': edit_distance
            }
            
        except Exception as e:
            logger.error(f"Error processing utterance {utt_id}: {e}")
            return {
                'success': False,
                'utt_id': utt_id,
                'error': str(e)
            }

    @staticmethod
    def process_for_wer(aligner: BaseCERAligner, predictions: List[str], references: List[str]) -> EvalResult:
        """Process reference and hypothesis files with utterance ID alignment."""
        if len(predictions) != len(references):
            raise ValueError(f"Mismatch in ref/hyp count: {len(references)} refs vs {len(predictions)} predictions")
        
        if len(references) == 0:
            logger.info("No data to process!")
            return EvalResult(
                semantic_wer=0.0, semantic_cer=0.0, num_sentences=0, total_ref_words=0
            )

        # Initialize accumulators
        total_ref_words = 0
        total_correct = 0
        total_substitutions = 0
        total_deletions = 0
        total_insertions = 0
        total_ref_chars = 0
        total_edit_distance = 0
        processed_count = 0
            
        # Prepare arguments for multiprocessing
        from multiprocessing import Pool, cpu_count
        import os
        
        # Use 75% of available cores, but at least 1
        num_processes = max(1, int(cpu_count() * 0.75))
        
        # Get aligner parameters to pass to workers (avoid passing aligner object)
        language = aligner.__class__.__name__.replace('CERAligner', '').lower()
        if language == 'english':
            language = 'en'
        elif language == 'hindi':
            language = 'hi'
        cer_threshold = aligner.cer_threshold
        
        # Create argument tuples for each utterance (without aligner object)
        args_list = [(idx, ref, hyp, language, cer_threshold) for idx, (ref, hyp) in enumerate(zip(references, predictions))]
        
        # Process utterances in parallel
        with Pool(processes=num_processes) as pool:
            results = pool.map(ASRSemanticMetrics._process_utterance, args_list)
        
        # Accumulate results from all processes
        for result in results:
            if result['success']:
                total_ref_words += result['total_ref_words']
                total_correct += result['word_correct']
                total_substitutions += result['word_substitutions']
                total_deletions += result['word_deletions']
                total_insertions += result['word_insertions']
                total_ref_chars += result['ref_chars']
                total_edit_distance += result['edit_distance']
                processed_count += 1
            else:
                logger.info(f"Skipping utterance {result['utt_id']} due to error...")
                
        # Calculate dataset-wide statistics
        dataset_wer = round((total_substitutions + total_deletions + total_insertions) / max(total_ref_words, 1), 3)
        dataset_weighted_cer = round(total_edit_distance / total_ref_chars if total_ref_chars > 0 else 0.0, 3)
    
        # Optional: Write output files
        # with open(file_stats_output, 'w', encoding='utf-8') as f:
        #     f.write('\n'.join(file_stats_lines))
        # print(f"\nFile-specific statistics written to: {file_stats_output}")
        
        return EvalResult(
            semantic_wer=dataset_wer, 
            semantic_cer=dataset_weighted_cer, 
            num_sentences=processed_count,
            total_ref_words=int(total_ref_words),
        )
    
    @staticmethod
    def process_keywords_for_wer(aligner: BaseCERAligner, predictions: List[str], references: List[str], entities: List[str]) -> Tuple[int, float]:
        """Process keywords for WER calculation."""
        if len(predictions) != len(references):
            raise ValueError(f"Mismatch in ref/hyp count: {len(references)} refs vs {len(predictions)} predictions")
        
        if len(references) == 0:
            logger.info("No data to process!")
            return (0, 0.0)

        # Initialize accumulators
        total_ref_words = 0
        total_correct = 0
        total_substitutions = 0
        total_deletions = 0
        total_insertions = 0
        total_ref_chars = 0
        total_edit_distance = 0
        processed_count = 0
            
        # Process each utterance pair
        for idx, (ref, hyp, annotation) in enumerate(zip(references, predictions, entities)):
            utt_id = f"utterance_{idx}"  # FIXED: Added utt_id definition
            try:
                # Parse annotations
                try:
                    annotations = eval(annotation)  # Use ast.literal_eval for safety in production
                except:
                    raise ValueError("Could not parse reference annotations")
                
                # Extract keywords
                reference_keywords = aligner.extract_keywords_from_text(ref, annotations)

                alignments = aligner.align_keywords(reference_keywords, hyp)
                # Print results
                #aligner.print_alignment_visual(alignments) #to be used for debugging
                # Calculate statistics
                stats = aligner.calculate_error_rates(alignments)

                # Accumulate dataset-wide statistics
                total_ref_words += stats['total_ref_words']
                total_correct += stats['word_correct']
                total_substitutions += stats['word_substitutions']
                total_deletions += stats['word_deletions']
                total_insertions += stats['word_insertions']

                # Accumulate character-level statistics for weighted CER
                for alignment in alignments:
                    if alignment.ref_words and alignment.hyp_words:
                        ref_text = ' '.join(alignment.ref_words)
                        ref_chars = len(ref_text.replace(' ', ''))
                        total_ref_chars += ref_chars
                        total_edit_distance += alignment.character_error_rate * ref_chars
                
                processed_count += 1
                
                # Optional: Add file-specific stats to output (using utterance ID instead of index)
                # file_stats_lines.append(
                #     f"{utt_id}\t{stats['total_ref_words']}\t{stats['word_correct']}\t"
                #     f"{stats['word_substitutions']}\t{stats['word_deletions']}\t{stats['word_insertions']}\t"
                #     f"{stats['wer']:.4f}\t{stats['weighted_word_cer']:.4f}"
                # )
            except Exception as e:
                logger.error(f"Error processing utterance {utt_id}: {e}")
                logger.info("Skipping this utterance...")
                continue
            
        # Calculate dataset-wide statistics
        dataset_wer = round((total_substitutions + total_deletions + total_insertions) / max(total_ref_words, 1), 3)  
        #dataset_weighted_cer = round(total_edit_distance / total_ref_chars if total_ref_chars > 0 else 0.0, 2)
        
        return (int(total_ref_words), dataset_wer)

    def evaluate(self, predictions: List[str], references: List[str], **kwargs) -> EvalResult:
        """
        Evaluate ASR predictions against references.
        
        Args:
            predictions: List of hypothesis transcriptions
            references: List of reference transcriptions
            **kwargs: Additional parameters including:
                - language: Language code (e.g., 'english', 'hindi', 'en', 'hi') - REQUIRED
                
        Returns:
            Dictionary containing evaluation results
        """
        # Extract language from cli
        language = kwargs.get("language")
        entities = kwargs.get("entities", [])
        
        # Handle None or missing language parameter
        if language is None:
            language = self.language  # Use instance default
        
        # Ensure language is a string
        if not isinstance(language, str):
            raise ValueError(f"Language parameter must be a string, got {type(language)}")
        
        try:
            logger.info(f"Creating {language} aligner...")
            # Get language-specific aligner
            aligner = self.get_aligner(language)
            logger.info(f"Aligner created successfully")
            
            # Validate inputs
            if not predictions or not references:
                raise ValueError("Both predictions and references must be non-empty lists")
            
            # Process files
            logger.info(f"Processing {len(references)} utterances...")
            logger.info("Using default aligner to obtain semWER")
            results = self.process_for_wer(aligner, predictions, references) 
            entity_wer = None
            if entities:
                logger.info("Entities found, using keyword aligner")
                total_ref_words, entity_wer = self.process_keywords_for_wer(aligner, predictions, references, entities) 
            
            return EvalResult(
                semantic_wer=results.semantic_wer,
                semantic_cer=results.semantic_cer,
                num_sentences=results.num_sentences,
                entity_wer=entity_wer,
                total_ref_words=total_ref_words
            )
            
        except Exception as e:
            logger.error(f"Error: {e}")
            raise  # Re-raise instead of sys.exit for better error handling