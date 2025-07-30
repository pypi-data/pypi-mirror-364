import os
import typer
from mtbmasker.utils import check_file_exists, run_cmd

def generate_mask(
    input_list,
    query_fasta,
    blastn_path=None,
    makeblastdb_path=None,
    bedtools_path=None,
    threads=4,
    output_dir="."
):
    check_file_exists(input_list)
    check_file_exists(query_fasta)

    # Set commands (with optional custom paths)
    blastn = blastn_path or "blastn"
    makeblastdb = makeblastdb_path or "makeblastdb"
    bedtools = bedtools_path or "bedtools"

    with open(input_list) as f:
        for line in f:
            isolate = line.strip().split("\t")[0]
            genome_fasta = f"{isolate}.fasta"
            if not os.path.exists(genome_fasta):
                typer.echo(f"❌ Genome file {genome_fasta} not found. Skipping.")
                continue

            typer.echo(f"\n🔬 Processing: {isolate}")
            blast_db = os.path.join(output_dir, f"{isolate}_masking")
            blast_output = os.path.join(output_dir, f"{isolate}_blast.tsv")
            bed_output = os.path.join(output_dir, f"{isolate}_conservitive_AF19-like_masking_file.bed")

            # 1. Makeblastdb
            run_cmd(f"{makeblastdb} -in {genome_fasta} -dbtype nucl -out {blast_db}")

            # 2. Run BLASTn
            run_cmd(
                f"{blastn} -query {query_fasta} -db {blast_db} "
                f"-out {blast_output} -task blastn -perc_identity 75 "
                f"-qcov_hsp_perc 90 -num_threads {threads} "
                f"-outfmt '6 qseqid qstart qend qlen sseqid sstart send slen sstrand evalue length pident gaps gapopen stitle'"
            )

            # 3. Format to BED
            tmp_bed = os.path.join(output_dir, f"{isolate}_raw.bed")
            with open(blast_output) as infile, open(tmp_bed, "w") as out:
                for line in infile:
                    parts = line.strip().split("\t")
                    chrom = parts[4]
                    start = min(int(parts[5]), int(parts[6])) - 1
                    end = max(int(parts[5]), int(parts[6]))
                    out.write(f"{chrom}\t{start}\t{end}\n")

            # 4. Sort and merge
            sorted_bed = os.path.join(output_dir, f"{isolate}_sorted.bed")
            run_cmd(f"{bedtools} sort -i {tmp_bed} > {sorted_bed}")
            run_cmd(f"{bedtools} merge -i {sorted_bed} > {bed_output}")

            # Cleanup
            os.remove(tmp_bed)
            os.remove(sorted_bed)
            typer.echo(f"✅ Mask created: {bed_output}")
