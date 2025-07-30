fimep
================

**fimep** is a Python package with a command-line interface (CLI) that
leverages a deep learning model to predict effectors. it integrates
predictions from multiple effector prediction programs to provide
improved accuracy in identifying pathogen effector proteins. The package
supports predictions for fungi, bacteria, oomycete, and can handle all
kingdoms simultaneously.

------------------------------------------------------------------------

## Installation

To use **fimep**, install it from [PyPI](https://pypi.org/) using:

``` bash
pip install fimep
```

Optional: users can create a virtual environment using
[mamba](https://mamba.readthedocs.io/en/latest/user_guide/mamba.html) or
[python venv](https://docs.python.org/3/library/venv.html) before
installing **fimep**.

------------------------------------------------------------------------

## Supported tools and kingdoms

| Kingdom      | Supported tools                                     |
|--------------|-----------------------------------------------------|
| **Fungi**    | EffectorP-3.0, deepredeff, WideEffHunter            |
| **Bacteria** | deepredeff, EffectiveT3, T3SEpp                     |
| **Oomycete** | EffectorP-3.0, deepredeff, WideEffHunter, EffectorO |
| **All**      | All tools above                                     |

------------------------------------------------------------------------

## Usage

**fimep** can be used in two ways:

1.  **Single workflow** (`runall`): Complete analysis from raw tool
    outputs to final predictions
2.  **Step-by-step**: Individual steps for more control over the process

### Single workflow usage

It is best practice to type in each command into the terminal directly.

#### Note

- **WideEffHunter**: Requires the `complete` input file and `predicted`
  output file from WideEffHunter program.

#### For fungi

``` bash
fimep runall \
    --effectorp fungi_effp.txt \
    --deepredeff dr_result.csv \
    --wideeffhunter complete.fasta pred.fasta \
    --kingdom fungi \
    --output final_fungi_prediction.csv
```

#### For oomycetes

``` bash
fimep runall \
    --effectorp ep_result.txt \
    --deepredeff dr_result.csv \
    --effectoro eo_result.csv \
    --wideeffhunter complete.fasta pred.fasta \
    --kingdom oomycete \
    --output final_oomycete_prediction.csv
```

#### For bacteria

``` bash
fimep runall \
    --t3sepp t3sepp_result.txt \
    --deepredeff dr_result.csv \
    --effectivet3 et3_result.csv \
    --kingdom bacteria \
    --output final_bacteria_prediction.csv
```

------------------------------------------------------------------------

### Step-by-step usage

The usage include the subcommand and options which are explained below:

``` bash
fimep <subcommand> [options]
```

#### Available subcommands:

| Command | Description |
|----|----|
| `merge_predictions` | Merge formatted prediction results into one CSV |
| `encode_predictions` | Encode predictions into model input format |
| `predict` | Run the trained deep learning model on encoded input |
| `preprocess_effectorp` | Format raw EffectorP output into standard structure |
| `preprocess_effectiveT3` | Format raw EffectiveT3 output |
| `preprocess_effectoro` | Format raw EffectorO output |
| `preprocess_deepredeff` | Format raw deepredeff output |
| `preprocess_wideeffhunter` | Format WideEffHunter predictions from FASTA files |
| `preprocess_t3sepp` | Format T3SEpp output |

#### Required options

- `input` - Input file path
- `output` - Output file path
- `--kingdom` - fungi, oomycete or bacteria
- `--pred` - predicted effector output from WideEffHunter (only used for
  WideEffHunter)

#### Special cases

- **WideEffHunter**: Requires the `complete` input files and `predicted`
  output file from WideEffHunter program.
- **Merge**: Accepts multiple input files followed by output file

##### 1. Preprocess individual tool outputs

Process raw outputs from various effector prediction programs:

``` bash
# Format EffectorP results
fimep preprocess_effectorp --input effectorp_result.txt --output formatted_ep_output.csv --kingdom fungi


# Format deepredeff results
fimep preprocess_deepredeff --input deepredeff_result.csv --output formatted_dr_output.csv --kingdom fungi


# Format WideEffHunter results 
fimep preprocess_wideeffhunter --input complete_seq_file.fasta --pred predicted_wideeffhunter_output.fasta --output formatted_we_output.csv --kingdom oomycete


# Format T3SEpp results (bacteria only) 
fimep preprocess_t3sepp --input t3sepp_result.txt --output formatted_t3p_output.csv --kingdom bacteria


# Format EffectiveT3 results (bacteria only)
fimep preprocess_effectiveT3 --input effectiveT3_result.csv --output formatted_et3_output.csv --kingdom bacteria


# Format EffectorO results (oomycete only)
fimep preprocess_effectoro --input effectoro_result.csv --output formatted_eo_output.csv --kingdom oomycete

```

##### 2. Merge formatted predictions

Combine multiple prediction files for fungal pathogens into a single
dataset:

``` bash
fimep merge_prediction --input formatted_dr_output.csv formatted_et3_output.csv formatted_t3p_output.csv --output merged_data.csv
```

##### 3. Encode merged data

Encode and scale the merged predictions for model input:

``` bash
fimep encode --input merged_data.csv --output encoded_output.csv --kingdom fungi
```

##### 4. Generate final prediction

``` bash
fimep predict --input encoded_input.csv --output final_predictions.csv
```

------------------------------------------------------------------------

## Output format

The final output is a CSV file with two columns:

- `Identifier`: Sequence identifier
- `Pred_Label`: Final prediction (Effector/Non-Effector)

Example:

| Identifier | Pred_Label   |
|------------|--------------|
| seq1       | Effector     |
| seq2       | Non-Effector |
| seq3       | Effector     |

------------------------------------------------------------------------

## Contact

For issues, questions or contributions, please open an issue on the
[GitHub repository](https://github.com/LoveBio/fimep/issues) or contact
us via [email](mailto:lovekayode1@gmail.com).

------------------------------------------------------------------------

## License

MIT License © 2025 Love Odunlami
