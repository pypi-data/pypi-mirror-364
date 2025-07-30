import os
from Bio import SeqIO
import logging
logger = logging.getLogger(__name__)

def validate_and_list_plasmids(input_dir):
    valid_extensions = ['.fna', '.fa', '.fasta']
    plasmid_files = []
    invalid_files = []

    for fname in os.listdir(input_dir):
        if not any(fname.lower().endswith(ext) for ext in valid_extensions):
            continue
        fpath = os.path.join(input_dir, fname)
        try:
            with open(fpath, 'r') as handle:
                records = list(SeqIO.parse(handle, 'fasta'))
                if len(records) == 0:
                    invalid_files.append(fname)
                else:
                    plasmid_files.append(os.path.abspath(fpath))
        except Exception:
            invalid_files.append(fname)

    if invalid_files:
        logger.warning("Warning: The following files are not valid FASTA files or unreadable:")
        for f in invalid_files:
            logger.warning(f" - {f}")

    # Sort by filename - if you sort by name, it affect the layout of the plot (just the visualization, not the network itrself)!
    # plasmid_files.sort(key=lambda x: os.path.basename(x).lower())

    return plasmid_files

def write_plasmid_list(plasmid_files, output_file="Plasmid_list.txt"):
    with open(output_file, 'w') as f:
        for path in plasmid_files:
            f.write(path + '\n')

def write_plasmid_sizes(plasmid_files, output_file="Plasmid_sizes.txt"):
    with open(output_file, 'w') as f:
        f.write("PlasmidID\tSize\n")
        for path in plasmid_files:
            total_len = 0
            with open(path, 'r') as handle:
                for rec in SeqIO.parse(handle, 'fasta'):
                    total_len += len(rec.seq)
            f.write(f"{os.path.basename(path)}\t{total_len}\n")
