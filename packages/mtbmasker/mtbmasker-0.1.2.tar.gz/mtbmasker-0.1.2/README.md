# mtbmasker

## 👥 Authors

- **Etienne Ntumba Kabongo** — Université de Montréal / McGill University
- **Dan Whiley** — Nottingham University

**mtbmasker** is a Python command-line tool designed to generate isolate-specific conservative genome masks for *Mycobacterium tuberculosis* (MTB) genomes. This is particularly useful for downstream variant calling and phylogenomic analyses by masking problematic genomic regions (e.g., PE/PPE genes, IS elements, and other repetitive loci).

---

## ✨ Features

- Generates genome masks per isolate using BLASTn alignment against predefined repetitive genes.
- Supports custom isolate genome files and gene query sets.
- Automatically formats coordinates to BED, sorts, and merges overlapping masked regions.
- Outputs high-quality, isolate-specific `.bed` files for genome masking.

---

## 🧬 Use case

This tool was originally developed for comparative genomics and transmission studies of *Mycobacterium tuberculosis* complex (MTBC) isolates, including *M. africanum*. It ensures that inter-lineage diversity is respected during masking.

---

## 🔧 Installation

### From PyPI (stable version):
```bash
pip install mtbmasker
```

### From GitHub (development version):
```bash
pip install git+https://github.com/EtienneNtumba/mtbmasker.git
```

---

## 🚀 Usage

### Basic Command
```bash
mtbmasker mask input_list.tsv --query-fasta data/genes_to_mask.fasta
```

### Help Output
```
Usage: mtbmasker mask [OPTIONS] INPUT_LIST

  🔬 Generate isolate-specific conservative genome masks (.bed files) for
  each isolate using BLASTn alignments and BEDTools.

Arguments:
  INPUT_LIST    Path to TSV file with isolate IDs (without .fasta extension) [required]

Options:
  --query-fasta TEXT     Path to fasta file containing genes to be masked [default: data/genes_to_mask.fasta]
  --blastn-path TEXT     Optional: Path to custom blastn binary
  --makeblastdb-path TEXT Optional: Path to makeblastdb binary
  --bedtools-path TEXT   Optional: Path to bedtools binary
  --threads INTEGER      Number of threads to use [default: 4]
  --output-dir TEXT      Directory to save output BED files [default: current directory]
  --help                 Show this message and exit.
```

### Command-Line Options Explained

**Required Arguments:**
- `INPUT_LIST` — Path to a tab-separated file containing one isolate ID per line (without .fasta extension). Each ID must correspond to a `<ID>.fasta` file present in the working directory.

**Optional Flags:**
- `--query-fasta` — Path to FASTA file containing problematic/repetitive genes to be masked. Default: `data/genes_to_mask.fasta`
- `--blastn-path` — Custom path to blastn executable if not in system PATH
- `--makeblastdb-path` — Custom path to makeblastdb executable if not in system PATH  
- `--bedtools-path` — Custom path to bedtools executable if not in system PATH
- `--threads` — Number of CPU threads to use for parallel processing. Default: 4
- `--output-dir` — Directory where output BED files will be saved. Default: current working directory

---

## 📁 Example

**input_list.tsv:**
```
ARR1960.LR.Asm
QC-9.LR.Asm
N1177.LR.Asm
```

Each listed isolate must have a corresponding `ARR1960.LR.Asm.fasta`, etc., in the current directory.

---

## 🔬 Requirements

- Python ≥ 3.8
- BLAST+
- BEDTools
- Typer

Both BLAST and BEDTools must be installed and available in your `$PATH` or via a conda environment.

---

## 📄 Output

For each isolate, the following file is generated:

```
<isolate>_conservitive_AF19-like_masking_file.bed
```

This BED file contains sorted and merged coordinates of masked regions.

---


## 📂 License

This tool is licensed under the MIT License.

---

## 👥 Authors

- **Etienne Ntumba Kabongo** — Université de Montréal / McGill University
- **Dan Whiley** — Nottingham University
