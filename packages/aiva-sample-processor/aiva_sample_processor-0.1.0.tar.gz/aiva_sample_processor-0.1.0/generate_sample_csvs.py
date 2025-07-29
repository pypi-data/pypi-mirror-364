#!/usr/bin/env python3
"""
Generate CSVs for importing sample variants into the database.
This script processes OpenCRAVAT CSV files and generates CSVs for the variants,
transcript_consequences, and sample_variants tables.
"""
import argparse
import csv
import gzip
import json
import logging
import os
import re
import hashlib
import sys
import uuid
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

# Import transcript version removal function
from importers.preprocessing_utils import remove_transcript_version

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Import VRS generator
try:
    # Use the aiva-vrs package
    from aiva_vrs import generate_vrs_id, normalize_chromosome
    logger.info("Successfully imported VRS generator from aiva-vrs package")
except ImportError:
    logger.error("Could not import aiva-vrs package. Please install it with: pip install aiva-vrs")
    sys.exit(1)

def format_pg_array(items):
    """Format a list of strings as a PostgreSQL array literal (e.g., '{term1,"term2"}')."""
    if not items or not isinstance(items, list):
        return '{}'

    # Escape terms for PostgreSQL array literal:
    # - Double quotes around terms containing commas, spaces, braces, backslashes, or double quotes.
    # - Backslash-escape backslashes and double quotes within quoted terms.
    escaped_items = []
    for item in items:
        if not isinstance(item, str):
            item = str(item) # Ensure item is a string
        if not item:
            escaped_items.append('NULL') # Represent empty strings or None as NULL if needed, or skip
            continue

        # Characters requiring quoting in PG array literals
        needs_quoting = any(c in item for c in [',', ' ', '{', '}', '\\', '"'])
        if needs_quoting:
            # Escape backslashes and double quotes
            escaped_item = item.replace('\\', '\\\\').replace('"', '\\"')
            escaped_items.append(f'"{escaped_item}"')
        else:
            escaped_items.append(item)

    # Join into PostgreSQL array literal format
    return '{' + ','.join(escaped_items) + '}'

def generate_sample_id(sample_name):
    """
    Generate a consistent sample ID based on the sample name.
    
    Args:
        sample_name: The name of the sample
        
    Returns:
        A consistent sample ID as an MD5 hash
    """
    # Use only the sample name to ensure deterministic IDs
    # This ensures the same sample name always gets the same ID
    return hashlib.md5(sample_name.encode()).hexdigest()

def extract_protein_position(hgvs_p):
    """Extract numeric position from HGVS protein notation."""
    if not hgvs_p or not isinstance(hgvs_p, str) or not hgvs_p.startswith('p.'):
        return None
    try:
        # Extract first numeric position after 'p.'
        match = re.search(r'p\.\D*(\d+)', hgvs_p)
        return int(match.group(1)) if match else None
    except:
        return None

def is_main_chromosome(chrom):
    """Check if a chromosome is a main chromosome (1-22, X, Y, MT) and not an alt contig.
    
    Args:
        chrom: Chromosome name (without 'chr' prefix)
        
    Returns:
        True if it's a main chromosome, False otherwise
    """
    # List of valid main chromosomes
    main_chromosomes = [
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
        '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
        '21', '22', 'X', 'Y', 'MT', 'M'
    ]
    
    return chrom in main_chromosomes

def process_opencravat_csv(
    csv_path, 
    output_dir, 
    assembly='GRCh38', 
    compress=True,
    owner_id='user-1',
    group_id=None,
    is_public='false',
    sample_type='blood',
    status='processed',
    review_status='not_reviewed',
    view_status='none',
    archive_status='active',
    clinical_notes='',
    phenotype_terms='[]'
):
    """Process an OpenCRAVAT CSV file and generate CSVs for database import.
    
    Args:
        csv_path: Path to the OpenCRAVAT CSV file
        output_dir: Directory to write output CSVs to
        assembly: Genome assembly (GRCh37 or GRCh38)
        compress: Whether to compress output files with gzip
        owner_id: User ID of the owner
        group_id: Group ID for the samples
        is_public: Whether samples are public (true/false)
        sample_type: Type of sample (blood, tissue, etc.)
        status: Sample processing status
        review_status: Review status of the sample
        view_status: View status of the sample
        archive_status: Archive status of the sample
        clinical_notes: Clinical notes for the sample
        phenotype_terms: JSON array of phenotype terms
        
    Returns:
        Tuple of (variants_csv_path, transcript_csv_path, sample_variants_csv_path, samples_csv_path)
    """
    logger.info(f"Processing OpenCRAVAT CSV file: {csv_path}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output file paths
    base_name = os.path.basename(csv_path).split('.')[0]
    
    # Define file paths with or without .gz extension based on compress flag
    ext = '.csv.gz' if compress else '.csv'
    variants_csv = os.path.join(output_dir, f"{base_name}_variants{ext}")
    transcript_csv = os.path.join(output_dir, f"{base_name}_transcript_consequences{ext}")
    sample_variants_csv = os.path.join(output_dir, f"{base_name}_sample_variants{ext}")
    # Samples CSV is never compressed
    samples_csv = os.path.join(output_dir, f"{base_name}_samples.csv")
    
    # Open output files with appropriate writer (gzip or regular)
    # Ensure Unix line endings and proper encoding
    if compress:
        variants_file = gzip.open(variants_csv, 'wt', newline='\n', encoding='utf-8')
        sample_variants_file = gzip.open(sample_variants_csv, 'wt', newline='\n', encoding='utf-8')
        transcript_file = gzip.open(transcript_csv, 'wt', newline='\n', encoding='utf-8')
    else:
        variants_file = open(variants_csv, 'w', newline='\n', encoding='utf-8')
        sample_variants_file = open(sample_variants_csv, 'w', newline='\n', encoding='utf-8')
        transcript_file = open(transcript_csv, 'w', newline='\n', encoding='utf-8')
    
    samples_file = open(samples_csv, 'w', newline='\n', encoding='utf-8')
    
    # Create CSV writers with proper quoting for fields that might contain commas
    variants_writer = csv.DictWriter(variants_file, fieldnames=[
        'id', 'chromosome', 'position', 'reference_allele', 'alternate_allele'
    ], quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    variants_writer.writeheader()
    
    # Updated fieldnames to match the actual database schema
    sample_variants_writer = csv.DictWriter(sample_variants_file, fieldnames=[
        'id', 'sample_id', 'variant_id', 'chromosome', 'zygosity', 
        'quality', 'depth', 'allele_depth', 'allele_frequency', 'flags', 'created_at', 'updated_at'
    ], quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    sample_variants_writer.writeheader()
    
    # Create transcript writer
    transcript_writer = csv.DictWriter(transcript_file, fieldnames=[
        'id', 'variant_id', 'chromosome', 'transcript_id', 'gene_id',
        'consequence_terms', 'hgvs_c', 'hgvs_p', 'protein_position',
        'amino_acids', 'codons', 'canonical'
    ], quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    transcript_writer.writeheader()
    
    # Updated fieldnames to match the actual database schema
    samples_writer = csv.DictWriter(samples_file, fieldnames=[
        'id', 'name', 'description', 'owner_id', 'group_id', 'is_public',
        'patient_id', 'sample_type', 'collection_date', 'trio_group_id',
        'trio_role', 'status', 'review_status', 'metadata', 'clinical_notes',
        'phenotype_terms', 'variant_count', 'created_at', 'updated_at',
        'last_accessed', 'access_count', 'view_status', 'archive_status'
    ], quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    samples_writer.writeheader()
    
    # Track minimal information
    sample_id_map = {}  # Maps sample_name to sample_id
    sample_variant_counts = {}  # Tracks variant counts per sample
    
    # Determine if the input file is gzipped
    is_gzipped = csv_path.endswith('.gz')
    open_func = gzip.open if is_gzipped else open
    open_mode = 'rt' if is_gzipped else 'r'

    # Process the CSV file in a single pass
    with open_func(csv_path, open_mode, encoding='utf-8') as f:
        # Skip comment lines
        comment_lines = []
        for line in f:
            if line.startswith('#'):
                comment_lines.append(line)
            else:
                break
        
        # Reset file pointer to beginning
        f.seek(0)
        
        # Skip all comment lines
        for _ in range(len(comment_lines)):
            next(f)
        
        # Use csv.DictReader for the main processing
        reader = csv.DictReader(f)
        
        # Process each row
        for row in tqdm(reader, desc="Processing rows", unit="row"):
            try:
                # Extract sample names - may contain multiple samples separated by semicolons
                sample_names_str = row.get('samples', '')
                if not sample_names_str:
                    continue
                    
                # Split into individual sample names
                sample_names = sample_names_str.split(';')
                
                # Get the number of samples for this variant
                num_samples = len(sample_names)
                
                # Extract fields that might have multiple values (one per sample)
                zygosity_values = row.get('vcfinfo.zygosity', '').split(';') if row.get('vcfinfo.zygosity', '') else ['']*num_samples
                filter_values = row.get('vcfinfo.filter', '').split(';') if row.get('vcfinfo.filter', '') else ['']*num_samples
                phred_values = row.get('vcfinfo.phred', '').split(';') if row.get('vcfinfo.phred', '') else ['']*num_samples
                alt_reads_values = row.get('vcfinfo.alt_reads', '').split(';') if row.get('vcfinfo.alt_reads', '') else ['']*num_samples
                tot_reads_values = row.get('vcfinfo.tot_reads', '').split(';') if row.get('vcfinfo.tot_reads', '') else ['']*num_samples
                af_values = row.get('vcfinfo.af', '').split(';') if row.get('vcfinfo.af', '') else ['']*num_samples
                hap_block_values = row.get('vcfinfo.hap_block', '').split(';') if row.get('vcfinfo.hap_block', '') else ['']*num_samples
                hap_strand_values = row.get('vcfinfo.hap_strand', '').split(';') if row.get('vcfinfo.hap_strand', '') else ['']*num_samples
                
                # Ensure all value lists have the same length as sample_names
                # If they're shorter, pad with empty strings
                def pad_list(lst, target_length):
                    return lst + [''] * (target_length - len(lst)) if len(lst) < target_length else lst[:target_length]
                
                zygosity_values = pad_list(zygosity_values, num_samples)
                filter_values = pad_list(filter_values, num_samples)
                phred_values = pad_list(phred_values, num_samples)
                alt_reads_values = pad_list(alt_reads_values, num_samples)
                tot_reads_values = pad_list(tot_reads_values, num_samples)
                af_values = pad_list(af_values, num_samples)
                hap_block_values = pad_list(hap_block_values, num_samples)
                hap_strand_values = pad_list(hap_strand_values, num_samples)
                
                # Process each sample separately
                for i, sample_name in enumerate(sample_names):
                    # Create sample record if not already processed
                    if sample_name not in sample_id_map:
                        sample_id = generate_sample_id(sample_name)
                        sample_id_map[sample_name] = sample_id
                        sample_variant_counts[sample_id] = 0
                        
                        # Create and write sample record immediately
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        samples_writer.writerow({
                            'id': sample_id,
                            'name': f"{sample_name}",
                            'description': f"Imported from {os.path.basename(csv_path)}",
                            'owner_id': owner_id,
                            'group_id': group_id,
                            'is_public': is_public,
                            'patient_id': sample_name,
                            'sample_type': sample_type,
                            'collection_date': '',
                            'trio_group_id': '',
                            'trio_role': '',
                            'status': status,
                            'review_status': review_status,
                            'metadata': '{}',
                            'clinical_notes': clinical_notes,
                            'phenotype_terms': phenotype_terms,
                            'variant_count': '0',  # Will be updated at the end
                            'created_at': timestamp,
                            'updated_at': timestamp,
                            'last_accessed': '',
                            'access_count': '0',
                            'view_status': view_status,
                            'archive_status': archive_status
                        })
                    
                    # Get sample ID
                    sample_id = sample_id_map[sample_name]
                    
                    # Update variant count
                    sample_variant_counts[sample_id] += 1
                
                # Process variant information
                chrom = row.get('chrom', '').replace('chr', '')
                pos = row.get('pos', '')
                ref = row.get('ref_base', '')
                alt = row.get('alt_base', '')
                
                # Skip alt contigs and only process main chromosomes
                if not is_main_chromosome(chrom):
                    continue
                
                # Handle special cases for indels and empty alleles
                if ref == '-':
                    ref = ''
                if alt == '-':
                    alt = ''
                
                # Handle empty alleles properly for CSV export
                # Keep empty strings for insertions/deletions, but ensure they're not None
                if ref is None:
                    ref = ''
                if alt is None:
                    alt = ''
                
                # Ensure we have strings, not None values
                ref = str(ref) if ref is not None else ''
                alt = str(alt) if alt is not None else ''
                
                # Generate VRS ID - handle special cases for empty alleles
                try:
                    # For empty alleles, we need to handle them in a way that VRS can process
                    vrs_ref = ref if ref else '-'  # Use '-' for empty ref in VRS
                    vrs_alt = alt if alt else '-'  # Use '-' for empty alt in VRS
                    vrs_id = generate_vrs_id(chrom, pos, vrs_ref, vrs_alt, assembly)
                except Exception as e:
                    # If VRS ID generation fails, create a fallback ID
                    logger.warning(f"VRS ID generation failed for {chrom}:{pos}:{ref}:{alt}, using fallback: {e}")
                    fallback_string = f"{chrom}:{pos}:{ref}:{alt}"
                    vrs_id = f"ga4gh:VA:{chrom}:{hashlib.md5(fallback_string.encode()).hexdigest()}"
                
                # Write variant record directly
                variants_writer.writerow({
                    'id': vrs_id,
                    'chromosome': chrom,
                    'position': pos,
                    'reference_allele': ref,
                    'alternate_allele': alt,
                })
                
                # Process each sample separately for sample_variants
                for i, sample_name in enumerate(sample_names):
                    sample_id = sample_id_map[sample_name]
                    
                    # Get the sample-specific values for this iteration
                    zygosity = zygosity_values[i] if i < len(zygosity_values) else ''
                    filter_value = filter_values[i] if i < len(filter_values) else ''
                    phred = phred_values[i] if i < len(phred_values) else ''
                    allele_depth = alt_reads_values[i] if i < len(alt_reads_values) else ''
                    depth = tot_reads_values[i] if i < len(tot_reads_values) else ''
                    allele_frequency = af_values[i] if i < len(af_values) else ''
                    hap_block = hap_block_values[i] if i < len(hap_block_values) else ''
                    hap_strand = hap_strand_values[i] if i < len(hap_strand_values) else ''
                    quality = row.get('qual', '')
                    
                    # Clean and validate numeric fields
                    def clean_numeric_field(value):
                        """Clean numeric field, return empty string if invalid."""
                        if not value or value in ['', 'NA', 'NULL', 'None']:
                            return ''
                        try:
                            float(value)  # Test if it's a valid number
                            return str(value).strip()
                        except (ValueError, TypeError):
                            return ''
                    
                    # Write sample variant record directly
                    sample_variants_writer.writerow({
                        'id': str(uuid.uuid4()),
                        'sample_id': sample_id,
                        'variant_id': vrs_id,
                        'chromosome': chrom,
                        'zygosity': zygosity or '',
                        'quality': clean_numeric_field(quality),
                        'depth': clean_numeric_field(depth),
                        'allele_depth': clean_numeric_field(allele_depth),
                        'allele_frequency': clean_numeric_field(allele_frequency),
                        'flags': '{}',
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                # Process transcript information
                # First, add the primary transcript from the main columns
                primary_transcript_id = row.get('transcript', '')
                primary_gene_id = row.get('hugo', '')
                primary_consequence = row.get('so', '')
                primary_hgvs_c = row.get('cchange', '')
                primary_hgvs_p = row.get('achange', '')
                
                # Extract protein position from HGVSp
                primary_protein_position = ''
                if primary_hgvs_p:
                    match = re.search(r'p\.[A-Za-z]+(\d+)[A-Za-z]+', primary_hgvs_p)
                    if match:
                        primary_protein_position = match.group(1)
                
                # Write primary transcript record directly
                if primary_transcript_id:
                    # Remove version from transcript ID
                    clean_transcript_id = remove_transcript_version(primary_transcript_id)
                    transcript_writer.writerow({
                        'id': str(uuid.uuid4()),
                        'variant_id': vrs_id,
                        'chromosome': chrom,
                        'transcript_id': clean_transcript_id,
                        'gene_id': primary_gene_id,
                        'consequence_terms': primary_consequence,
                        'hgvs_c': primary_hgvs_c,
                        'hgvs_p': primary_hgvs_p,
                        'protein_position': primary_protein_position,
                        'amino_acids': '',
                        'codons': '',
                        'canonical': 'true'
                    })
                
                # Process all_mappings field (if present)
                all_mappings = row.get('all_mappings', '')
                if all_mappings:
                    mappings = [m.strip() for m in all_mappings.split(';')]
                    for mapping in mappings:
                        if not mapping:
                            continue
                        
                        parts = mapping.split(':')
                        if len(parts) >= 6:
                            transcript_id = parts[0].strip()
                            gene_id = parts[1].strip()
                            consequence = parts[3].strip()
                            hgvs_p = parts[4].strip()
                            hgvs_c = parts[5].strip()
                            
                            # Remove version from transcript ID
                            clean_transcript_id = remove_transcript_version(transcript_id)
                            clean_primary_transcript_id = remove_transcript_version(primary_transcript_id)
                            
                            # Skip if this is the same as the primary transcript (after version removal)
                            if clean_transcript_id == clean_primary_transcript_id:
                                continue
                            
                            # Extract protein position
                            protein_position = ''
                            if hgvs_p and hgvs_p.startswith('p.'):
                                match = re.search(r'p\.[A-Za-z]+(\d+)[A-Za-z]+', hgvs_p)
                                if match:
                                    protein_position = match.group(1)
                            
                            # Write transcript record directly
                            transcript_writer.writerow({
                                'id': str(uuid.uuid4()),
                                'variant_id': vrs_id,
                                'chromosome': chrom,
                                'transcript_id': clean_transcript_id,
                                'gene_id': gene_id,
                                'consequence_terms': consequence,
                                'hgvs_c': hgvs_c,
                                'hgvs_p': hgvs_p,
                                'protein_position': protein_position,
                                'amino_acids': '',
                                'codons': '',
                                'canonical': 'false'
                            })
                
                # Process JSON transcript data if present
                try:
                    if row.get('all_transcripts'):
                        transcript_data = json.loads(row.get('all_transcripts', '[]'))
                        for transcript in transcript_data:
                            transcript_id = transcript.get('transcript_id', '')
                            gene_id = transcript.get('gene_id', '')
                            gene_symbol = transcript.get('gene_symbol', '')
                            consequences = transcript.get('consequence_terms', [])
                            hgvs_c = transcript.get('cdna_change', '')
                            hgvs_p = transcript.get('protein_change', '')
                            canonical = transcript.get('canonical', False)
                            
                            if not gene_id and gene_symbol:
                                gene_id = gene_symbol
                            
                            protein_position = ''
                            if hgvs_p:
                                match = re.search(r'p\.[A-Za-z]+(\d+)[A-Za-z]+', hgvs_p)
                                if match:
                                    protein_position = match.group(1)
                            
                            consequence_terms = format_pg_array(consequences) if consequences else '[]'
                            
                            # Remove version from transcript ID
                            clean_transcript_id = remove_transcript_version(transcript_id)
                            clean_primary_transcript_id = remove_transcript_version(primary_transcript_id)
                            
                            # Skip if this is the same as the primary transcript (after version removal)
                            if clean_transcript_id == clean_primary_transcript_id:
                                continue
                                
                            # Write transcript record directly
                            transcript_writer.writerow({
                                'id': str(uuid.uuid4()),
                                'variant_id': vrs_id,
                                'chromosome': chrom,
                                'transcript_id': clean_transcript_id,
                                'gene_id': gene_id,
                                'consequence_terms': consequence_terms,
                                'hgvs_c': hgvs_c,
                                'hgvs_p': hgvs_p,
                                'protein_position': protein_position,
                                'amino_acids': '',
                                'codons': '',
                                'canonical': 'true' if canonical else 'false'
                            })
                except (json.JSONDecodeError, TypeError):
                    pass
                
            except Exception as e:
                logger.warning(f"Error processing row: {e}")
                continue
    
    # Close output files
    variants_file.close()
    sample_variants_file.close()
    transcript_file.close()
    samples_file.close()
    
    # Update variant counts in samples file
    with open(samples_csv, 'r', newline='\n', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Update variant counts
    for row in rows:
        sample_id = row['id']
        if sample_id in sample_variant_counts:
            row['variant_count'] = str(sample_variant_counts[sample_id])
    
    # Write back to samples file with proper formatting
    with open(samples_csv, 'w', newline='\n', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames, 
                               quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    
    logger.info(f"Generated variants CSV: {variants_csv}")
    logger.info(f"Generated transcript consequences CSV: {transcript_csv}")
    logger.info(f"Generated sample variants CSV: {sample_variants_csv}")
    logger.info(f"Generated samples CSV: {samples_csv}")
    
    return variants_csv, transcript_csv, sample_variants_csv, samples_csv

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Generate CSVs for importing sample variants into the database.')
    
    # Required arguments
    parser.add_argument('--input', required=True, help='Path to the OpenCRAVAT CSV file')
    parser.add_argument('--output-dir', required=True, help='Directory to write output CSVs to')
    
    # Optional arguments with defaults
    parser.add_argument('--assembly', default='GRCh38', choices=['GRCh37', 'GRCh38'], help='Genome assembly')
    parser.add_argument('--no-compress', action='store_true', help='Do not compress output files')
    
    # Sample metadata
    parser.add_argument('--owner-id', default='user-1', help='User ID of the owner')
    parser.add_argument('--group-id', required=True, help='Group ID for the samples')
    parser.add_argument('--is-public', choices=['true', 'false'], default='false', help='Whether samples are public')
    parser.add_argument('--sample-type', default='blood', help='Type of sample (blood, tissue, etc.)')
    parser.add_argument('--status', default='processed', help='Sample processing status')
    parser.add_argument('--review-status', default='not_reviewed', help='Review status of the sample')
    parser.add_argument('--view-status', default='none', help='View status of the sample')
    parser.add_argument('--archive-status', default='active', help='Archive status of the sample')
    parser.add_argument('--clinical-notes', default='', help='Clinical notes for the sample')
    parser.add_argument('--phenotype-terms', default='[]', help='JSON array of phenotype terms')
    
    args = parser.parse_args()
    
    # Process the OpenCRAVAT CSV file
    process_opencravat_csv(
        args.input, 
        args.output_dir, 
        assembly=args.assembly, 
        compress=not args.no_compress,
        owner_id=args.owner_id,
        group_id=args.group_id,
        is_public=args.is_public,
        sample_type=args.sample_type,
        status=args.status,
        review_status=args.review_status,
        view_status=args.view_status,
        archive_status=args.archive_status,
        clinical_notes=args.clinical_notes,
        phenotype_terms=args.phenotype_terms
    )

if __name__ == '__main__':
    main()
