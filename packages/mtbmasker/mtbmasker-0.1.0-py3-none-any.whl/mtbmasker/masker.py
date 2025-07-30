import subprocess
import os
from mtbmasker.utils import check_file_exists, run_cmd

def run_masking_pipeline(input_list_file, query_fasta):
    check_file_exists(input_list_file)
    check_file_exists(query_fasta)

    with open(input_list_file) as f:
        for line in f:
            isolate = line.strip().split("\t")[0]
            genome_fasta = f"{isolate}.fasta"
            if not os.path.exists(genome_fasta):
                typer.echo(f"❌ Genome file {genome_fasta} not found. Skipping.")
                continue

            print(f"\n🔬 Processing: {isolate}")
            blast_db = f"{isolate}_masking"
            blast_output = f"{isolate}_blast.tsv"
            bed_output = f"{isolate}_conservitive_AF19-like_masking_file.bed"

            # 1. Makeblastdb
            run_cmd(f"makeblastdb -in {genome_fasta} -dbtype nucl -out {blast_db}")

            # 2. Run BLASTn
            run_cmd(
                f"blastn -query {query_fasta} -db {blast_db} "
                f"-out {blast_output} -task blastn -perc_identity 75 "
                f"-qcov_hsp_perc 90 -outfmt '6 qseqid qstart qend qlen sseqid sstart send slen sstrand evalue length pident gaps gapopen stitle'"
            )

            # 3. Format to BED
            tmp_bed = f"{isolate}_raw.bed"
            with open(blast_output) as infile, open(tmp_bed, "w") as out:
                for line in infile:
                    parts = line.strip().split("\t")
                    chrom = parts[4]
                    start = min(int(parts[5]), int(parts[6])) - 1
                    end = max(int(parts[5]), int(parts[6]))
                    out.write(f"{chrom}\t{start}\t{end}\n")

            # 4. Sort and merge
            sorted_bed = f"{isolate}_sorted.bed"
            run_cmd(f"bedtools sort -i {tmp_bed} > {sorted_bed}")
            run_cmd(f"bedtools merge -i {sorted_bed} > {bed_output}")

            # Cleanup
            os.remove(tmp_bed)
            os.remove(sorted_bed)
            print(f"✅ Mask created: {bed_output}")
