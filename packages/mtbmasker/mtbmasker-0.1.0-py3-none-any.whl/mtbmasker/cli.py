import typer
from mtbmasker.masker import run_masking_pipeline

app = typer.Typer(help="mtbmasker - Create isolate-specific genome masks for MTB.")

@app.command()
def mask(input_list: str, query_fasta: str = "data/genes_to_mask.fasta"):
    """
    Run the full masking pipeline for a list of genome FASTA files.
    Each entry in the input_list should match a genome FASTA file (e.g., ARR1960.LR.Asm.fasta).
    """
    run_masking_pipeline(input_list, query_fasta)

if __name__ == "__main__":
    app()
