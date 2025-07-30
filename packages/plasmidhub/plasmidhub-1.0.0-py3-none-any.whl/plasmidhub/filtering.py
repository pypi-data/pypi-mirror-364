import os
import pandas as pd
import logging
logger = logging.getLogger(__name__)

def strip_paths_in_fastani(input_file):
    """Remove directory paths from plasmid names in FastANI output."""
    df = pd.read_csv(input_file, sep='\t', header=None)
    df.columns = ['Query', 'Reference', 'ANI', 'Matching_Frags_Query', 'Matching_Frags_Ref']
    df['Query'] = df['Query'].apply(os.path.basename)
    df['Reference'] = df['Reference'].apply(os.path.basename)
    df.to_csv(input_file, sep='\t', header=False, index=False)
    
def strip_paths_in_plasmid_list(file_path):
    """Remove directory paths from plasmid names in Plasmid_list.txt."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    stripped_lines = [os.path.basename(line.strip()) + '\n' for line in lines]
    with open(file_path, 'w') as f:
        f.writelines(stripped_lines)

def filter_self_comparisons(input_file, output_file):
    df = pd.read_csv(input_file, sep='\t', header=None)
    df.columns = ['Query', 'Reference', 'ANI', 'Matching_Frags_Query', 'Matching_Frags_Ref']
    df_filtered = df[df['Query'] != df['Reference']]
    df_filtered.to_csv(output_file, sep='\t', index=False)

def add_plasmid_sizes(ani_file, sizes_file, output_file):
    sizes_df = pd.read_csv(sizes_file, sep='\t')
    size_dict = dict(zip(sizes_df['PlasmidID'], sizes_df['Size']))
    ani_df = pd.read_csv(ani_file, sep='\t')
    def get_size(plasmid_id):
        return size_dict.get(plasmid_id, None)
    ani_df['Query_size'] = ani_df['Query'].apply(get_size)
    ani_df['Reference_size'] = ani_df['Reference'].apply(get_size)
    ani_df.to_csv(output_file, sep='\t', index=False)
    
def apply_filters(input_file, output_file, frag_len=1000, coverage_threshold=0.5, ani_threshold=95.0):
    df = pd.read_csv(input_file, sep='\t')

    # Convert matching fragments to base pairs using user-defined fragment length
    df['Matching_Frags_Query_bp'] = df['Matching_Frags_Query'] * frag_len
    df['Matching_Frags_Ref_bp'] = df['Matching_Frags_Ref'] * frag_len

    # Apply filtering logic
    filtered = df[
        (df['Matching_Frags_Query_bp'] > df['Reference_size'] * coverage_threshold) &
        (df['Matching_Frags_Ref_bp'] > df['Query_size'] * coverage_threshold) &
        (df['Matching_Frags_Query_bp'] > df['Query_size'] * coverage_threshold) &
        (df['ANI'] >= ani_threshold)
    ]

    filtered.to_csv(output_file, sep='\t', index=False)
    logger.info(f"[INFO] Applied filters (ANI = {ani_threshold}, coverage = {coverage_threshold*100:.1f}%). ")