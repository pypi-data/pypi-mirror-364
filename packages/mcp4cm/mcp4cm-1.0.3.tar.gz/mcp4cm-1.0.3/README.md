# MCP4CM - Model Cleansing Pipeline for Conceptual Models

## Overview

`mcp4cm` is a Python library dedicated to cleaning and processing conceptual modeling datasets. It specifically supports UML and ArchiMate datasets, providing a streamlined workflow for dataset loading, filtering, data extraction, and deduplication.

## Key Features

* **Dataset Loading:** Supports UML (`MODELSET`) and ArchiMate (`EAMODELSET`) datasets.
* **Data Filtering:** Provides comprehensive filters to remove invalid or irrelevant data.
* **Data Extraction:** Enables detailed analysis of dataset contents, including naming conventions and class structures.
* **Deduplication:** Offers both exact and near-duplicate detection techniques using hashing and TF-IDF-based approaches.

## Usage

To use the `mcp4cm` library, follow these steps:

### Create a virtual environment using uv package manager

In order to install `uv`, you can use the following link - [uv install](https://docs.astral.sh/uv/getting-started/installation/)

In case of Linux or MacOS, it is straightforward using the installation page.
In case of windows - First Follow instructions for windows on installation page

If you get an error due to execution policy:
2. run powershell as administrator and change policies with this command:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You should now be able to run the `uv` command in your terminal.

Once you have `uv` installed, you can create a virtual environment using the following command:

```bash/powershell
uv init
uv venv
source .venv/bin/activate
```

### Install the required packages
After creating the virtual environment, you need to install the required packages. You can do this by running the following command:

```bash
uv pip install -r requirements.txt
```

### Downloading the data
To use the library, you need to download the datasets. The datasets are not included in the repository due to their size. You can download the zip file of the datasets them from the following drive link:
- MCP4CM Dataset: [MCP4CM Datasets](https://drive.google.com/file/d/1ZSTQvsim_sCX76qfx86Df3bHDtFM7tR0/view?usp=sharing)

- Unzip the data folder in the root directory of the repository. 

```
unzip data.zip
```

The structure should look like this:
```
mcp4cm/
data/
    modelset/
    eamodelset/
README.md
requirements.txt
LICENSE

## Testing the Library
You can test the library in the jupyter notebook - test_mcp4cm.ipynb. This notebook contains examples of how to use the library for dataset loading, filtering, data extraction, and deduplication.

## Usage

### Dataset Loading

```python
from mcp4cm.dataloading import load_dataset
from mcp4cm.base import DatasetType

uml_dataset = load_dataset(DatasetType.MODELSET, 'data/modelset')
archimate_dataset = load_dataset(DatasetType.EAMODELSET, 'data/eamodelset')
```

### Filtering and Data Extraction

#### UML Dataset

```python
from mcp4cm.uml.data_extraction import (
    filter_empty_or_invalid_files,
    filter_models_without_names,
    filter_models_by_name_count,
    filter_models_with_empty_class_names,
    find_files_with_comments,
    extract_names_counts_from_dataset,
    get_word_counts_from_dataset,
    get_name_length_distribution,
    filter_models_by_name_length_or_stopwords,
    filter_dummy_names,
    filter_dummy_classes,
    filter_classes_by_generic_pattern,
    filter_models_by_sequential_and_dummy_words
)

filter_empty_or_invalid_files(uml_dataset)
filter_models_without_names(uml_dataset)
filter_models_by_name_count(uml_dataset)
filter_models_with_empty_class_names(uml_dataset)
find_files_with_comments(uml_dataset)
extract_names_counts_from_dataset(uml_dataset, plt_figs=True)
get_word_counts_from_dataset(uml_dataset, plt_fig=True, topk=20)
get_name_length_distribution(uml_dataset, plt_fig=True)
filter_models_by_name_length_or_stopwords(uml_dataset)
filter_dummy_names(uml_dataset)
filter_dummy_classes(uml_dataset)
filter_classes_by_generic_pattern(uml_dataset)
filter_models_by_sequential_and_dummy_words(uml_dataset)
```

#### ArchiMate Dataset

```python
from mcp4cm.archimate.data_extraction import (
    extract_names_counts_from_dataset,
    get_word_counts_from_dataset,
    get_name_length_distribution,
    filter_models_by_name_length_or_stopwords,
    filter_dummy_names
)

extract_names_counts_from_dataset(archimate_dataset, plt_figs=True)
get_word_counts_from_dataset(archimate_dataset, plt_fig=True, topk=20)
get_name_length_distribution(archimate_dataset, plt_fig=True)
filter_models_by_name_length_or_stopwords(archimate_dataset)
filter_dummy_names(archimate_dataset)
```

### Deduplication

```python
from mcp4cm.generic.duplicate_detection import (
    detect_duplicates_by_hash,
    tfidf_near_duplicate_detector
)

detect_duplicates_by_hash(uml_dataset, plt_fig=True)

# TF-IDF-based near duplicate detection
tfidf_near_duplicate_detector(uml_dataset, key='names', plt_fig=True)
tfidf_near_duplicate_detector(archimate_dataset, key='names', plt_fig=True)
tfidf_near_duplicate_detector(archimate_dataset, key='names_with_layers_and_types', plt_fig=True)
```

## Visualization

The library includes built-in visualization options (`plt_fig=True`) for quick insights into dataset characteristics.

## Contributing

Contributions are welcome. Please fork the repository, create a feature branch, and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
