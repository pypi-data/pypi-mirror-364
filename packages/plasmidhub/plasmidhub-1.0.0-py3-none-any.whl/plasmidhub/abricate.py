import os
import subprocess
import shutil
import glob
import logging
logger = logging.getLogger(__name__)

def run_abricate_bulk(input_dir, results_dir, db_list, threads=None):
    os.makedirs(results_dir, exist_ok=True)

    # Use default thread count if not provided
    if threads is None:
        threads = 4

    # Move into input_dir because wildcard expansion happens here
    original_dir = os.getcwd()
    os.chdir(input_dir)

    # Collect all fasta-like files
    fasta_files = sorted(
        glob.glob("*.fna") +
        glob.glob("*.fa") +
        glob.glob("*.fasta")
    )

    if not fasta_files:
        raise RuntimeError(f"No input files found in {input_dir} with .fna/.fa/.fasta extensions.")

    for db in db_list:
        logger.info(f"Running abricate on database: {db}")

        # Build the shell command with all fasta file names
        cmd = f"abricate {' '.join(fasta_files)} --db {db} -t {threads}"

        # Output file path (temporary inside input_dir)
        temp_output = f"{db}.abr"
        with open(temp_output, "w") as out_f:
            subprocess.run(cmd, shell=True, stdout=out_f, stderr=subprocess.DEVNULL)

        # Move the output to results_dir
        final_output_path = os.path.join(results_dir, f"{db}.abr")
        shutil.move(temp_output, final_output_path)
        logger.info(f"Saved: {final_output_path}")

    # Return to original directory
    os.chdir(original_dir)
