# annotation_processor/annotation_processor/importers/preprocessing_utils.py
import logging
import json
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def remove_transcript_version(transcript_id: str) -> str:
    """
    Remove version suffix from Ensembl transcript IDs.
    Converts "ENST00000356175.2" to "ENST00000356175"
    
    Args:
        transcript_id: Transcript ID that may contain a version suffix
        
    Returns:
        Transcript ID without version suffix
    """
    if not transcript_id or not isinstance(transcript_id, str):
        return transcript_id
    
    # Remove version suffix (everything after the last dot if it's followed by digits)
    # Pattern matches: ENST followed by digits, then a dot, then more digits at the end
    match = re.match(r'^(ENST\d+)\.\d+$', transcript_id)
    if match:
        return match.group(1)
    
    # If it doesn't match the expected pattern, return as-is
    return transcript_id

def fix_split_consequence_terms(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Fix rows where 'consequence_terms' might be split across multiple subsequent columns
    due to unescaped commas within the term list during CSV generation.
    Looks for '[' at the start and combines with subsequent columns until ']' is found.

    Args:
        rows: List of row dictionaries (from csv.DictReader).

    Returns:
        List of row dictionaries with 'consequence_terms' potentially fixed.
    """
    fixed_rows = []
    fixed_count = 0
    # Define the expected order of columns that might contain parts of a split consequence_terms
    # This order is based on the VEP output format typically used.
    potential_split_columns = ['consequence_terms', 'hgvs_c', 'hgvs_p', 'protein_position', 'amino_acids', 'codons', 'canonical']

    for row_index, row in enumerate(rows):
        # Check if 'consequence_terms' exists, is a string, starts with '[' but doesn't end with ']'
        consequence_value = row.get('consequence_terms')
        if (isinstance(consequence_value, str) and
                consequence_value.startswith('[') and
                not consequence_value.endswith(']')):

            logger.debug(f"Potential split consequence_terms found in row {row_index+1}: Starting with '{consequence_value}'")
            combined_value = consequence_value
            affected_columns = ['consequence_terms'] # Start with the initial column
            found_end = False

            # Iterate through the *subsequent* potential columns in order
            start_index = potential_split_columns.index('consequence_terms') + 1
            for i in range(start_index, len(potential_split_columns)):
                col_name = potential_split_columns[i]
                col_value = row.get(col_name)

                if col_value is not None: # Check if the column exists in the row
                    col_value_str = str(col_value)
                    # Append the current column's value
                    # Assume comma separation if combining multiple fields
                    combined_value += ',' + col_value_str
                    affected_columns.append(col_name)
                    logger.debug(f"  Appending column '{col_name}': '{col_value_str}' -> Combined: '{combined_value}'")

                    # Check if this column's value contains the closing bracket
                    if ']' in col_value_str:
                        found_end = True
                        logger.debug(f"  Found closing bracket ']' in column '{col_name}'.")
                        break # Stop combining once the closing bracket is found
                else:
                    # If a column in the sequence is missing, we probably can't reliably fix it.
                    logger.warning(f"  Expected column '{col_name}' missing in row {row_index+1} during split field fix. Stopping combination.")
                    break


            if found_end:
                # Create a fixed copy of the row
                fixed_row = row.copy()
                # Set the combined consequence_terms value
                fixed_row['consequence_terms'] = combined_value
                # Clear the values in the *subsequent* columns that were merged
                for col_to_clear in affected_columns[1:]: # Skip the first one ('consequence_terms')
                    fixed_row[col_to_clear] = '' # Or None, depending on desired outcome

                fixed_rows.append(fixed_row)
                fixed_count += 1
                logger.debug(f"Row {row_index+1} fixed. New consequence_terms: '{combined_value}', Cleared columns: {affected_columns[1:]}")
            else:
                # If we didn't find the end bracket, maybe it wasn't a split field after all,
                # or the split is too complex/unexpected. Add the original row.
                logger.warning(f"Could not find closing bracket for potential split consequence_terms in row {row_index+1}. Keeping original row.")
                fixed_rows.append(row)
        else:
            # No fixing needed for this row
            fixed_rows.append(row)

    if fixed_count > 0:
        # Use DEBUG level for less critical progress updates
        logger.debug(f"Fixed {fixed_count} rows with potentially split consequence_terms fields.")

    return fixed_rows


def format_consequence_terms(terms: Optional[str]) -> str:
    """
    Format consequence_terms field (potentially a string representation of a list)
    into a PostgreSQL array literal string (e.g., '{term1,term2,term3}').
    Handles various input formats like '[term1, term2]', 'term1,term2', or just 'term'.
    Crucially, it escapes necessary characters for PostgreSQL array literals.

    Args:
        terms: String representation of consequence terms, or None.

    Returns:
        PostgreSQL array literal string (e.g., '{term1,"term with space",term3}').
        Returns '{}' for empty or None input.
    """
    if not terms:
        return '{}'

    # Standardize input: remove brackets, strip whitespace
    if terms.startswith('[') and terms.endswith(']'):
        terms = terms[1:-1]
    terms = terms.strip()

    if not terms:
        return '{}'

    # Split terms by comma, handling potential extra spaces
    term_list = [term.strip() for term in terms.split(',')]

    # Escape terms for PostgreSQL array literal:
    # - Double quotes around terms containing commas, spaces, braces, backslashes, or double quotes.
    # - Backslash-escape backslashes and double quotes within quoted terms.
    escaped_terms = []
    for term in term_list:
        if not term: continue # Skip empty terms resulting from splitting
        # Characters requiring quoting
        # Use raw string r'...' for backslash to avoid escaping issues in Python itself
        needs_quoting = any(c in term for c in [',', ' ', '{', '}', '\\', '"'])
        if needs_quoting:
            # Escape backslashes and double quotes
            escaped_term = term.replace('\\', '\\\\').replace('"', '\\"')
            escaped_terms.append(f'"{escaped_term}"')
        else:
            escaped_terms.append(term)

    # Join into PostgreSQL array literal format
    formatted_terms = '{' + ','.join(escaped_terms) + '}'
    logger.debug(f"Original terms: '{terms}', Formatted: '{formatted_terms}'") # Added debug log
    return formatted_terms


def preprocess_rows(rows: List[Dict[str, Any]], table: str) -> List[Dict[str, Any]]:
    """
    Preprocess a batch of rows based on the target table's specific needs.
    Handles type conversions, default values, and special formatting.

    Args:
        rows: List of row dictionaries (from csv.DictReader).
        table: Target database table name.

    Returns:
        List of preprocessed row dictionaries ready for insertion.
    """
    # First, fix any split consequence_terms fields if this is the transcript_consequences table
    if table == 'transcript_consequences':
        try:
            rows = fix_split_consequence_terms(rows)
        except Exception as e:
            logger.error(f"Error during fix_split_consequence_terms for table '{table}': {e}", exc_info=True)
            # Decide how to handle: stop processing, or continue with potentially unfixed rows?
            # Let's log and continue for now.
            pass


    processed_rows = []
    for row_index, original_row in enumerate(rows):
        # Make a copy to avoid modifying the original list/dicts
        row = original_row.copy()
        try:
            # --- Generic Preprocessing (Applied to all tables) ---
            # Convert empty strings to None for potential NULL insertion
            for key, value in row.items():
                if isinstance(value, str) and value == '':
                    row[key] = None

            # --- Table-Specific Preprocessing ---
            if table == 'transcript_consequences':
                # Remove transcript version from transcript_id field
                transcript_id = row.get('transcript_id')
                if transcript_id:
                    original_transcript_id = transcript_id
                    row['transcript_id'] = remove_transcript_version(transcript_id)
                    if original_transcript_id != row['transcript_id']:
                        logger.debug(f"Row {row_index+1} (transcript_consequences): Removed version from transcript_id: '{original_transcript_id}' -> '{row['transcript_id']}'")
                
                # Convert consequence_terms string from CSV into a list for TEXT[] column
                terms_str = row.get('consequence_terms')
                if isinstance(terms_str, str):
                    # Split by comma, strip whitespace, remove empty strings
                    term_list = [term.strip() for term in terms_str.split(',') if term.strip()]
                    row['consequence_terms'] = term_list
                elif terms_str is None:
                    # If the original CSV value was empty string, it's now None
                    row['consequence_terms'] = []

            elif table == 'variants':
                # Convert 'alternate_allele' None (originally '') back to space if needed by schema/logic
                # Assuming the schema requires a non-null value here.
                if 'alternate_allele' in row and row['alternate_allele'] is None:
                    row['alternate_allele'] = ' ' # Use space for "empty" allele
                    logger.debug(f"Row {row_index+1} (variants): Set empty alternate_allele to space.")

            elif table == 'samples':
                # Fields with database defaults: remove them if None (originally '') so DB default applies
                default_fields = ['created_at', 'updated_at']
                for field in default_fields:
                    if field in row and row[field] is None:
                        del row[field]
                        logger.debug(f"Row {row_index+1} (samples): Removed empty field '{field}' to use DB default.")

                # Fields that should be NULL if empty (already handled by generic preprocessing)
                # nullable_fields = ['collection_date', 'last_accessed', 'archive_date']

                # Fields that need specific formatting (e.g., JSON)
                json_fields = ['phenotype_terms', 'metadata']
                for field in json_fields:
                    if field in row:
                        value = row[field]
                        if value is None:
                            # Set appropriate empty JSON structure if field is None (originally '')
                            row[field] = '[]' if field == 'phenotype_terms' else '{}'
                            logger.debug(f"Row {row_index+1} (samples): Set empty field '{field}' to empty JSON '{row[field]}'.")
                        elif isinstance(value, str):
                            # Attempt to parse/format if it's a non-empty string
                            if field == 'phenotype_terms':
                                # If it looks like a list of HPO terms "[HP:0001, HP:0002]"
                                if value.startswith('[') and ':' in value:
                                    try:
                                        # Basic parsing: split, strip, filter empty
                                        terms = [term.strip() for term in value.strip('[]').split(',') if term.strip()]
                                        # Convert to proper JSON array string
                                        row[field] = json.dumps(terms)
                                        logger.debug(f"Row {row_index+1} (samples): Formatted phenotype_terms: {row[field]}")
                                    except Exception as json_e:
                                        logger.warning(f"Row {row_index+1} (samples): Could not parse phenotype_terms '{value}' as list: {json_e}. Keeping original.")
                                # Add more robust parsing if needed
                            elif field == 'metadata':
                                # If it looks like JSON, try to validate/reformat
                                try:
                                    parsed_meta = json.loads(value)
                                    # Re-serialize to ensure consistent format
                                    row[field] = json.dumps(parsed_meta)
                                    logger.debug(f"Row {row_index+1} (samples): Validated/Reformatted metadata.")
                                except json.JSONDecodeError:
                                    logger.warning(f"Row {row_index+1} (samples): metadata field '{value}' is not valid JSON. Keeping original string.")
                                    # Decide: keep original, set to '{}', or raise error? Keeping original for now.

            # -- Standardize other potential None/empty values --
            for key, value in row.items():
                # Convert common empty/null representations to None for DB compatibility
                if isinstance(value, str) and value.lower() in ['', 'null', 'none']:
                    row[key] = None

            processed_rows.append(row)

        except Exception as e:
            logger.error(f"Error preprocessing row {row_index+1} for table '{table}': {e}. Skipping row.", exc_info=True)
            logger.error(f"Original row data: {original_row}")
            # Optionally add the failed row to a separate error list/file
            continue # Skip this row and continue with the next

    # Use DEBUG level for less critical progress updates
    logger.debug(f"Preprocessed {len(processed_rows)} rows for table '{table}'.")
    return processed_rows
