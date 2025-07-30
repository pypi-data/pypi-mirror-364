# mtbmasker

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

### From GitHub (development version):

```bash
pip install git+https://github.com/EtienneNtumba/mtbmasker.git
```

---

## 🚀 Usage

```bash
mtbmasker mask input_list.tsv --query-fasta data/genes_to_mask.fasta
```

**Arguments:**
- `input_list.tsv` — A tab-separated file with one isolate ID per line (without .fasta extension). Each ID must correspond to a `ID.fasta` file present in the working directory.
- `--query-fasta` — Fasta file of problematic/repetitive genes to be masked (default: `data/genes_to_mask.fasta`).

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

## 📚 Citation

If you use this tool in your research, please cite:

> Ntumba, E., Whiley, D., et al. (2025). [Manuscript Title], Journal Name, DOI: xxx

---

## 📂 License

This tool is licensed under the MIT License.

---

## 👥 Authors

- **Etienne Ntumba Kabongo** — Université de Montréal / McGill University
- **Dan Whiley** — Nottingham University
