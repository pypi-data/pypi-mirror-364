import typer
from mtbmasker.masker import generate_mask

app = typer.Typer(help="\U0001F9EC MTBMasker: Generate isolate-specific conservative genome masks for Mycobacterium tuberculosis.")

@app.command("mask", help="\U0001F52C Generate isolate-specific conservative genome masks (.bed files) for each isolate using BLASTn alignments and BEDTools.")
def mask(
    input_list: str = typer.Argument(..., help="TSV file with isolate IDs (without .fasta). Each ID must match a .fasta file in the directory."),
    query_fasta: str = typer.Option("data/genes_to_mask.fasta", help="FASTA file of genes to be masked (default: data/genes_to_mask.fasta)."),
    blastn_path: str = typer.Option(None, help="Optional: Path to blastn binary if not in $PATH."),
    makeblastdb_path: str = typer.Option(None, help="Optional: Path to makeblastdb binary if not in $PATH."),
    bedtools_path: str = typer.Option(None, help="Optional: Path to bedtools binary if not in $PATH."),
    threads: int = typer.Option(4, help="Number of threads to use for BLASTn (default: 4)."),
    output_dir: str = typer.Option(".", help="Directory to save output BED files (default: current directory).")
):
    """
    Main masking command. Uses BLASTn to align input genomes against query_fasta and generates merged BED files per isolate.
    """
    generate_mask(
        input_list=input_list,
        query_fasta=query_fasta,
        blastn_path=blastn_path,
        makeblastdb_path=makeblastdb_path,
        bedtools_path=bedtools_path,
        threads=threads,
        output_dir=output_dir
    )

if __name__ == "__main__":
    app()
