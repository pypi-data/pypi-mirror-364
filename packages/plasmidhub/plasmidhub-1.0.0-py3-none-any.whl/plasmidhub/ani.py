import os
import subprocess
import logging
logger = logging.getLogger(__name__)

def run_fastani(plasmid_list_file, fragLen=1000, minFrag=3, kmer=14, output_dir=".", threads=None):
    if threads is None:
        threads = 4

    output_file = os.path.join(output_dir, "fastani_raw_results.tsv")
    cmd = [
        "fastANI",
        "--ql", plasmid_list_file,
        "--rl", plasmid_list_file,
        "-o", output_file,
        "--fragLen", str(fragLen),
        "--minFraction", str(minFrag),
        "--kmer", str(kmer),
        "-t", str(threads)
    ]
    logger.info("Running FastANI with command:")
    logger.info(" ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("FastANI failed with error:")
        logger.error(result.stderr)
        exit(1)
    else:
        logger.info("FastANI completed successfully.")
