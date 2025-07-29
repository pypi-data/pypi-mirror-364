#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Chinese to English Translation Script
High-performance version with multi-threading, batch processing, and advanced optimizations
"""

import os
import re
import json
import time
import requests
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path
import hashlib
from collections import defaultdict
import urllib.parse

class EnhancedChineseTranslator:
    def __init__(self, translation_service='google', max_workers=5, batch_size=10, rate_limit=0.05):
        """
        Initialize enhanced translator with concurrent processing capabilities
        
        Args:
            translation_service: 'google', 'baidu', 'youdao', 'deepl'
            max_workers: Maximum number of concurrent translation threads
            batch_size: Number of texts to process in one batch
            rate_limit: Minimum time between API calls per thread (seconds)
        """
        self.translation_service = translation_service
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.rate_limit = rate_limit
        
        # Thread-safe cache and rate limiting
        self.translation_cache = {}
        self.cache_lock = threading.Lock()
        self.rate_limit_lock = threading.Lock()
        self.last_request_times = defaultdict(float)
        
        # Cache file
        self.cache_file = 'translation_cache.json'
        self.load_cache()
        
        # Regex patterns
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        self.string_patterns = {
            'single_quoted': re.compile(r"'([^'\\]|\\.)*'"),
            'double_quoted': re.compile(r'"([^"\\\\]|\\\\.)*"'),
            'multi_line_comment': re.compile(r'/\*.*?\*/', re.DOTALL),
            'dart_multiline_comment': re.compile(r'///.*$', re.MULTILINE),  # Process /// first
            'single_line_comment': re.compile(r'//.*$', re.MULTILINE),
            'hash_comment': re.compile(r'#.*$', re.MULTILINE),
        }
        
        # Statistics
        self.stats = {
            'total_translations': 0,
            'cache_hits': 0,
            'api_calls': 0,
            'failed_translations': 0,
            'processing_time': 0
        }
    
    def load_cache(self):
        """Load translation cache from file (thread-safe)"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.translation_cache = json.load(f)
                print(f"📥 Loaded {len(self.translation_cache)} cached translations")
        except Exception as e:
            print(f"⚠️ Could not load cache: {e}")
            self.translation_cache = {}
    
    def save_cache(self):
        """Save translation cache to file (thread-safe)"""
        try:
            with self.cache_lock:
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self.translation_cache, f, ensure_ascii=False, indent=2)
                print(f"💾 Saved {len(self.translation_cache)} translations to cache")
        except Exception as e:
            print(f"⚠️ Could not save cache: {e}")
    
    def rate_limit_wait(self, thread_id: int):
        """Thread-safe rate limiting"""
        with self.rate_limit_lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_times[thread_id]
            if time_since_last < self.rate_limit:
                time.sleep(self.rate_limit - time_since_last)
            self.last_request_times[thread_id] = time.time()
    
    def translate_with_google_batch(self, texts: List[str], thread_id: int) -> List[str]:
        """Batch translate multiple texts using Google Translate API"""
        if not texts:
            return []
        
        self.rate_limit_wait(thread_id)
        
        try:
            # For batch processing, we can send multiple texts separated by newlines
            # and then split the result
            combined_text = '\n'.join(texts)
            
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'zh-cn',
                'tl': 'en',
                'dt': 't',
                'q': combined_text
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            if result and result[0]:
                # Extract translated text
                translated_parts = []
                for item in result[0]:
                    if item and len(item) > 0:
                        translated_parts.append(item[0])
                
                if translated_parts:
                    combined_translation = ''.join(translated_parts)
                    # Split back into individual translations
                    translations = combined_translation.split('\n')
                    
                    # Ensure we have the same number of translations as inputs
                    while len(translations) < len(texts):
                        translations.append(texts[len(translations)])
                    
                    self.stats['api_calls'] += 1
                    return translations[:len(texts)]
            
            return texts
            
        except Exception as e:
            print(f"⚠️ Google Translate batch error: {e}")
            self.stats['failed_translations'] += len(texts)
            return texts
    
    def translate_with_google_single(self, text: str, thread_id: int) -> str:
        """Single text translation using Google Translate"""
        self.rate_limit_wait(thread_id)
        
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'zh-cn',
                'tl': 'en',
                'dt': 't',
                'q': text
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result and result[0] and result[0][0]:
                self.stats['api_calls'] += 1
                return result[0][0][0]
            
            return text
            
        except Exception as e:
            print(f"⚠️ Google Translate error for '{text[:30]}...': {e}")
            self.stats['failed_translations'] += 1
            return text
    
    def translate_texts_batch(self, texts: List[str]) -> List[str]:
        """
        Translate multiple texts using concurrent batch processing
        """
        if not texts:
            return []
        
        # Check cache first and separate cached vs uncached texts
        cached_results = {}
        uncached_texts = []
        uncached_indices = []
        
        with self.cache_lock:
            for i, text in enumerate(texts):
                if text in self.translation_cache:
                    cached_results[i] = self.translation_cache[text]
                    self.stats['cache_hits'] += 1
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
        
        # If all texts are cached, return immediately
        if not uncached_texts:
            return [cached_results.get(i, texts[i]) for i in range(len(texts))]
        
        # Process uncached texts in batches using thread pool
        translated_results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit batch translation tasks
            future_to_indices = {}
            
            for i in range(0, len(uncached_texts), self.batch_size):
                batch_texts = uncached_texts[i:i + self.batch_size]
                batch_indices = uncached_indices[i:i + self.batch_size]
                
                thread_id = i // self.batch_size
                
                if len(batch_texts) == 1:
                    # Single text translation
                    future = executor.submit(
                        self.translate_with_google_single, 
                        batch_texts[0], 
                        thread_id
                    )
                    future_to_indices[future] = [(batch_indices[0], batch_texts[0])]
                else:
                    # Batch translation
                    future = executor.submit(
                        self.translate_with_google_batch, 
                        batch_texts, 
                        thread_id
                    )
                    future_to_indices[future] = list(zip(batch_indices, batch_texts))
            
            # Collect results
            for future in as_completed(future_to_indices):
                indices_and_texts = future_to_indices[future]
                
                try:
                    result = future.result()
                    
                    if isinstance(result, list):
                        # Batch result
                        for (index, original_text), translation in zip(indices_and_texts, result):
                            translated_results[index] = translation
                            # Cache the translation
                            with self.cache_lock:
                                self.translation_cache[original_text] = translation
                    else:
                        # Single result
                        index, original_text = indices_and_texts[0]
                        translated_results[index] = result
                        # Cache the translation
                        with self.cache_lock:
                            self.translation_cache[original_text] = result
                    
                except Exception as e:
                    print(f"⚠️ Translation task failed: {e}")
                    # Use original texts as fallback
                    for index, original_text in indices_and_texts:
                        translated_results[index] = original_text
        
        # Combine cached and translated results
        final_results = []
        for i in range(len(texts)):
            if i in cached_results:
                final_results.append(cached_results[i])
            elif i in translated_results:
                final_results.append(translated_results[i])
            else:
                final_results.append(texts[i])
        
        self.stats['total_translations'] += len(texts)
        return final_results
    
    def preprocess_text_for_translation(self, text: str) -> str:
        """Preprocess text to improve translation quality"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Handle common programming terms that shouldn't be translated
        # Add markers around them to preserve them during translation
        programming_terms = [
            # Basic types
            r'\bMediaType\b', r'\bString\b', r'\bbool\b', r'\bint\b', r'\bdouble\b',
            r'\bList\b', r'\bMap\b', r'\bvoid\b', r'\btry\b', r'\bcatch\b',
            r'\bfinal\b', r'\bstatic\b', r'\bclass\b', r'\benum\b',
            # Class names and specific terms
            r'\bDuplicateGroup\b', r'\bImageSearchItem\b', r'\bEmailClassificationResult\b',
            r'\bImageQualityResult\b', r'\bVideoMetadata\b', r'\bImageSearchResult\b',
            r'\bDuplicateDetectionResult\b', r'\bChannelManager\b', r'\bMethodChannel\b',
            r'\bEventChannel\b', r'\bPlatformException\b', r'\bmediaId\b', r'\bMedia\s*ID\b',
            # Method names
            r'\bdebugPrint\b', r'\binvokeMethod\b', r'\bfromMap\b', r'\btoMap\b',
            # Technical terms
            r'\bAPI\b', r'\bUI\b', r'\bJSON\b', r'\bHTTP\b', r'\bURL\b', r'\bID\b'
        ]
        
        for term in programming_terms:
            text = re.sub(term, lambda m: f"__PRESERVE__{m.group()}__PRESERVE__", text, flags=re.IGNORECASE)
        
        return text
    
    def postprocess_translated_text(self, text: str) -> str:
        """Postprocess translated text to restore preserved terms"""
        # Restore preserved programming terms
        text = re.sub(r'__PRESERVE__(.+?)__PRESERVE__', r'\1', text)
        
        # Apply general, universal fixes only
        universal_fixes = [
            # Fix Chinese punctuation (universal)
            (r'，', r', '),
            (r'。', r'. '),
            (r'：', r': '),
            
            # Fix common translation patterns (universal)
            (r'\bfail\b(?=\s*[:;,.]|$)', r'failed'),
            (r'\bAnalysis\b', r'Parse'),  # "Parse" should be "Parse"
            (r'\bIn-house\b(?=\s+\w)', r'in'),  # "In-house" often becomes "In-house"
            
            # Fix specific concatenated patterns (universal) - only for known problematic combinations
            (r'([a-z])(failed)$', r'\1 \2'),  # Fix "...failed" at end of words
            (r'([A-Z]{2,})(cannot|can\'t)', r'\1 \2'),  # Fix "IDcannot" -> "ID cannot"
            
            # Fix common awkward phrases (universal)
            (r'\bCan\'t be empty\b', r'cannot be empty'),
            (r'\bReturn on failure\s*null\b', r'returns null on failure'),
        ]
        
        for pattern, replacement in universal_fixes:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Final cleanup: fix multiple spaces and trim
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    def escape_quotes_in_translation(self, translation: str, original_context: str, context_type: str) -> str:
        """
        Escape quotes in translated text based on the string context
        """
        if context_type not in ['single_quoted', 'double_quoted']:
            return translation
        
        # Detect the quote type used in the original context
        if context_type == 'single_quoted':
            # Escape single quotes in translation
            translation = translation.replace("'", "\\'")
        elif context_type == 'double_quoted':
            # Escape double quotes in translation
            translation = translation.replace('"', '\\"')
        
        return translation
    
    def find_chinese_in_content(self, content: str) -> List[Tuple[str, int, int, str]]:
        """
        Enhanced Chinese text detection with mixed Chinese-English sentence support
        """
        chinese_found = []
        all_matches = []
        
        # Process patterns in specific order to avoid conflicts
        processed_ranges = []
        
        # Process each pattern type with conflict avoidance
        pattern_order = ['dart_multiline_comment', 'single_line_comment', 'multi_line_comment', 'hash_comment', 'single_quoted', 'double_quoted']
        
        for pattern_name in pattern_order:
            if pattern_name not in self.string_patterns:
                continue
                
            pattern = self.string_patterns[pattern_name]
            for match in pattern.finditer(content):
                start, end = match.span()
                matched_text = match.group()
                
                # Check if this range conflicts with already processed ranges
                conflicts = any(
                    start < p_end and end > p_start
                    for p_start, p_end in processed_ranges
                )
                
                if conflicts:
                    continue
                
                # Check if this string/comment contains any Chinese characters
                if self.chinese_pattern.search(matched_text):
                    if pattern_name in ['single_quoted', 'double_quoted']:
                        # For strings: extract content between quotes
                        inner_content = matched_text[1:-1]
                        if self.chinese_pattern.search(inner_content):
                            all_matches.append({
                                'text': inner_content,
                                'start': start + 1,
                                'end': end - 1,
                                'context': pattern_name,
                                'full_match': matched_text
                            })
                            processed_ranges.append((start, end))
                    elif pattern_name == 'dart_multiline_comment':
                        # For /// comments: extract content after ///
                        if matched_text.startswith('///'):
                            comment_content = matched_text[3:].strip()
                            if self.chinese_pattern.search(comment_content):
                                # Find the actual position of the content
                                content_start_offset = matched_text.find(comment_content)
                                all_matches.append({
                                    'text': comment_content,
                                    'start': start + content_start_offset,
                                    'end': start + content_start_offset + len(comment_content),
                                    'context': pattern_name,
                                    'full_match': matched_text
                                })
                                processed_ranges.append((start, end))
                    elif pattern_name == 'single_line_comment':
                        # For // comments: extract content after // (but skip if starts with ///)
                        if matched_text.startswith('//') and not matched_text.startswith('///'):
                            comment_content = matched_text[2:].strip()
                            if self.chinese_pattern.search(comment_content):
                                content_start_offset = matched_text.find(comment_content)
                                all_matches.append({
                                    'text': comment_content,
                                    'start': start + content_start_offset,
                                    'end': start + content_start_offset + len(comment_content),
                                    'context': pattern_name,
                                    'full_match': matched_text
                                })
                                processed_ranges.append((start, end))
                    elif pattern_name == 'multi_line_comment':
                        # For /* */ comments: extract content between markers
                        if matched_text.startswith('/*') and matched_text.endswith('*/'):
                            comment_content = matched_text[2:-2].strip()
                            if self.chinese_pattern.search(comment_content):
                                content_start_offset = matched_text.find(comment_content)
                                all_matches.append({
                                    'text': comment_content,
                                    'start': start + content_start_offset,
                                    'end': start + content_start_offset + len(comment_content),
                                    'context': pattern_name,
                                    'full_match': matched_text
                                })
                                processed_ranges.append((start, end))
                    elif pattern_name == 'hash_comment':
                        # For # comments: extract content after #
                        if matched_text.startswith('#'):
                            comment_content = matched_text[1:].strip()
                            if self.chinese_pattern.search(comment_content):
                                content_start_offset = matched_text.find(comment_content)
                                all_matches.append({
                                    'text': comment_content,
                                    'start': start + content_start_offset,
                                    'end': start + content_start_offset + len(comment_content),
                                    'context': pattern_name,
                                    'full_match': matched_text
                                })
                                processed_ranges.append((start, end))
        
        # Find standalone Chinese text not in strings/comments
        covered_ranges = [(m['start'], m['end']) for m in all_matches]
        
        for chinese_match in self.chinese_pattern.finditer(content):
            start, end = chinese_match.span()
            chinese_text = chinese_match.group()
            
            # Skip if too short
            if len(chinese_text.strip()) < 2:
                continue
            
            # Check if this range overlaps with existing matches
            is_covered = any(
                start >= covered_start and end <= covered_end
                for covered_start, covered_end in covered_ranges
            )
            
            if not is_covered:
                all_matches.append({
                    'text': chinese_text,
                    'start': start,
                    'end': end,
                    'context': 'code',
                    'full_match': chinese_text
                })
        
        # Sort by position and remove duplicates
        all_matches.sort(key=lambda x: x['start'])
        seen = set()
        for match in all_matches:
            key = (match['text'], match['start'], match['end'])
            if key not in seen:
                seen.add(key)
                chinese_found.append((
                    match['text'],
                    match['start'],
                    match['end'],
                    match['context']
                ))
        
        return chinese_found
    
    def _is_text_file(self, file_path: Path) -> bool:
        """
        Check if a file is a readable text file
        """
        # Skip hidden files and common non-text files
        if file_path.name.startswith('.'):
            return False
        
        # Common binary file extensions to skip
        binary_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db', '.sqlite',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg', '.webp',
            '.mp3', '.wav', '.flac', '.mp4', '.avi', '.mov', '.mkv', '.wmv',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
            '.class', '.jar', '.war', '.ear', '.pyc', '.pyo',
            '.o', '.obj', '.lib', '.a', '.node'
        }
        
        if file_path.suffix.lower() in binary_extensions:
            return False
        
        # Try to read a small portion to check if it's text
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)  # Try to read first 1KB
            return True
        except (UnicodeDecodeError, PermissionError, OSError):
            # If we can't read it as UTF-8 text, it's probably binary
            return False
    
    def translate_file(self, file_path: str, output_path: str = None, backup: bool = True) -> bool:
        """
        Enhanced file translation with batch processing and progress tracking
        """
        start_time = time.time()
        
        try:
            print(f"📝 Processing: {file_path}")
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create backup if requested
            if backup and output_path is None:
                backup_path = file_path + '.backup'
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"💾 Created backup: {backup_path}")
            
            # Find all Chinese text
            chinese_found = self.find_chinese_in_content(content)
            
            if not chinese_found:
                print("✅ No Chinese text found")
                return True
            
            print(f"🔍 Found {len(chinese_found)} Chinese text instances")
            
            # Extract all Chinese texts for batch translation
            chinese_texts = [item[0] for item in chinese_found]
            
            # Preprocess texts
            preprocessed_texts = [
                self.preprocess_text_for_translation(text) 
                for text in chinese_texts
            ]
            
            print(f"🚀 Starting batch translation with {self.max_workers} threads...")
            
            # Batch translate all texts
            translated_texts = self.translate_texts_batch(preprocessed_texts)
            
            # Postprocess translations
            final_translations = [
                self.postprocess_translated_text(text) 
                for text in translated_texts
            ]
            
            # Apply translations to content (from end to start to maintain positions)
            translated_content = content
            for i in reversed(range(len(chinese_found))):
                chinese_text, start, end, context = chinese_found[i]
                translation = final_translations[i]
                
                # Get the original context around the Chinese text to determine quote type
                original_context = content[max(0, start-10):min(len(content), end+10)]
                
                # Escape quotes in translation if it's inside a string literal
                escaped_translation = self.escape_quotes_in_translation(
                    translation, original_context, context
                )
                
                translated_content = translated_content[:start] + escaped_translation + translated_content[end:]
            
            # Write output
            output_file = output_path or file_path
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            
            processing_time = time.time() - start_time
            self.stats['processing_time'] += processing_time
            
            print(f"✅ Translation completed in {processing_time:.2f}s: {output_file}")
            print(f"📊 Stats - Cache hits: {self.stats['cache_hits']}, API calls: {self.stats['api_calls']}, Failed: {self.stats['failed_translations']}")
            return True
            
        except Exception as e:
            print(f"❌ Error translating {file_path}: {e}")
            return False
    
    def translate_directory(self, directory_path: str, file_patterns: List[str] = None, 
                          output_dir: str = None, backup: bool = True) -> int:
        """
        Enhanced directory translation with parallel file processing
        """
        directory = Path(directory_path)
        if not directory.exists():
            print(f"❌ Directory not found: {directory_path}")
            return 0
        
        # Find all files
        all_files = []
        
        if file_patterns is None:
            # If no patterns specified, find all readable text files
            for file_path in directory.rglob('*'):
                if file_path.is_file() and self._is_text_file(file_path):
                    all_files.append(file_path)
        else:
            # Use specified patterns
            for pattern in file_patterns:
                files = list(directory.rglob(pattern))
                all_files.extend(files)
        
        if not all_files:
            if file_patterns is None:
                print(f"❌ No readable text files found in directory: {directory_path}")
            else:
                print(f"❌ No files found matching patterns: {file_patterns}")
            return 0
        
        print(f"📁 Found {len(all_files)} files to process")
        
        # Create output directory if specified
        if output_dir:
            output_directory = Path(output_dir)
            output_directory.mkdir(parents=True, exist_ok=True)
        
        # Process files with limited parallelism to avoid overwhelming the API
        success_count = 0
        
        with ThreadPoolExecutor(max_workers=min(3, len(all_files))) as executor:
            # Submit file processing tasks
            future_to_file = {}
            
            for file_path in all_files:
                if output_dir:
                    relative_path = file_path.relative_to(directory)
                    output_file = output_directory / relative_path
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    output_path = str(output_file)
                else:
                    output_path = None
                
                future = executor.submit(
                    self.translate_file, 
                    str(file_path), 
                    output_path, 
                    backup
                )
                future_to_file[future] = file_path
            
            # Collect results with progress tracking
            completed = 0
            for future in as_completed(future_to_file):
                completed += 1
                file_path = future_to_file[future]
                
                try:
                    success = future.result()
                    if success:
                        success_count += 1
                    print(f"📈 Progress: {completed}/{len(all_files)} files completed")
                except Exception as e:
                    print(f"❌ Failed to process {file_path}: {e}")
        
        print(f"\n{'='*60}")
        print(f"✅ Successfully translated {success_count}/{len(all_files)} files")
        print(f"📊 Total stats:")
        print(f"  - Total translations: {self.stats['total_translations']}")
        print(f"  - Cache hits: {self.stats['cache_hits']}")
        print(f"  - API calls: {self.stats['api_calls']}")
        print(f"  - Failed translations: {self.stats['failed_translations']}")
        print(f"  - Total processing time: {self.stats['processing_time']:.2f}s")
        print(f"{'='*60}")
        
        return success_count
    
    def print_performance_stats(self):
        """Print detailed performance statistics"""
        cache_hit_rate = (self.stats['cache_hits'] / max(self.stats['total_translations'], 1)) * 100
        failure_rate = (self.stats['failed_translations'] / max(self.stats['total_translations'], 1)) * 100
        
        print(f"\n📊 Performance Statistics:")
        print(f"  ├─ Total translations: {self.stats['total_translations']}")
        print(f"  ├─ Cache hit rate: {cache_hit_rate:.1f}%")
        print(f"  ├─ API calls made: {self.stats['api_calls']}")
        print(f"  ├─ Failed translations: {self.stats['failed_translations']} ({failure_rate:.1f}%)")
        print(f"  ├─ Total processing time: {self.stats['processing_time']:.2f}s")
        
        if self.stats['total_translations'] > 0:
            avg_time = self.stats['processing_time'] / self.stats['total_translations']
            print(f"  └─ Average time per translation: {avg_time*1000:.1f}ms")


def main():
    """Enhanced main function with advanced options"""
    parser = argparse.ArgumentParser(description='Enhanced Chinese to English translator with multi-threading')
    parser.add_argument('path', nargs='?', default='.', help='File or directory path to translate')
    parser.add_argument('-o', '--output', help='Output file/directory path')
    parser.add_argument('-s', '--service', choices=['google', 'baidu'], default='google',
                       help='Translation service to use (default: google)')
    parser.add_argument('--patterns', nargs='*', default=None,
                       help='File patterns to match (default: all readable text files)')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup files')
    parser.add_argument('--workers', type=int, default=5,
                       help='Maximum number of worker threads (default: 5)')
    parser.add_argument('--batch-size', type=int, default=10,
                       help='Batch size for translations (default: 10)')
    parser.add_argument('--rate-limit', type=float, default=0.05,
                       help='Rate limit between API calls in seconds (default: 0.05)')
    
    args = parser.parse_args()
    
    # Initialize enhanced translator
    translator = EnhancedChineseTranslator(
        translation_service=args.service,
        max_workers=args.workers,
        batch_size=args.batch_size,
        rate_limit=args.rate_limit
    )
    
    print(f"🚀 Enhanced Chinese Translator")
    print(f"  ├─ Service: {args.service}")
    print(f"  ├─ Workers: {args.workers}")
    print(f"  ├─ Batch size: {args.batch_size}")
    print(f"  └─ Rate limit: {args.rate_limit}s")
    
    path = Path(args.path)
    start_time = time.time()
    
    if path.is_file():
        # Translate single file
        success = translator.translate_file(
            str(path), 
            args.output, 
            backup=not args.no_backup
        )
        result = "successful" if success else "failed"
        print(f"\n🎯 Single file translation {result}!")
        
    elif path.is_dir():
        # Translate directory
        success_count = translator.translate_directory(
            str(path),
            file_patterns=args.patterns,
            output_dir=args.output,
            backup=not args.no_backup
        )
        
        if success_count > 0:
            print(f"\n🎉 Directory translation completed! {success_count} files processed successfully.")
        else:
            print("\n❌ No files were translated successfully!")
    
    else:
        print(f"❌ Path not found: {args.path}")
        return
    
    # Save cache and show performance stats
    translator.save_cache()
    translator.print_performance_stats()
    
    total_time = time.time() - start_time
    print(f"\n⏱️  Total execution time: {total_time:.2f}s")
    
    print("\n📋 Tips:")
    print("  - Check translated files for accuracy")
    print("  - Use higher --workers for faster processing")
    print("  - Increase --rate-limit if hitting API limits")
    print("  - Backup files can restore originals if needed")


if __name__ == "__main__":
    main()