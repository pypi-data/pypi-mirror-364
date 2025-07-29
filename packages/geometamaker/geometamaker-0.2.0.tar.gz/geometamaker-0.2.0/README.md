## Introduction

GeoMetaMaker is a Python library for creating human and machine-readable
metadata for geospatial, tabular, and other data formats.

Supported datatypes include:
* everything supported by GDAL
* tabular formats supported by `frictionless`
* compressed formats supported by `frictionless`

## Installation

`mamba install -c conda-forge geometamaker`

## Basic Usage

This library comes with a command-line interface (CLI) called `geometamaker`.
Many of the examples below show how to use the Python interface, and then
how to do the same thing, if possible, using the CLI.

### Creating & adding metadata to file:

##### Python

```python
import geometamaker

data_path = 'data/watershed_gura.shp'
resource = geometamaker.describe(data_path)

resource.set_title('My Dataset')
resource.set_description('all about my dataset')
resource.set_keywords(['hydrology', 'watersheds'])

# For a vector:
resource.set_field_description(
    'field_name',  # the name of an actual field in the vector's table
    description='something about the field',
    units='mm')

# or for a raster:
data_path = 'data/dem.tif'
resource = geometamaker.describe(data_path)
resource.set_band_description(
    1,  # a raster band index, starting at 1
    description='something about the band',
    units='mm')


resource.write()
```
For a complete list of methods and attributes:
https://geometamaker.readthedocs.io/en/latest/index.html

##### CLI
```
geometamaker describe data/watershed_gura.shp
```
The CLI does not provide options for setting metadata properties such as 
keywords, field or band descriptions, or other properties that require 
user-input. If you create a metadata document with the CLI, you may wish 
to add these values manually by editing the 
`watershed_gura.shp.yml` file in a text editor.

### Creating metadata for a collection of files:
Users can create a single metadata document to describe a directory of 
files, with the option of excluding some files using a regular expression,
or limiting the number of subdirectory levels to traverse using the
`depth` or `-d` flag.

#### Python
```python
import geometamaker

collection_path = 'invest/data/invest-sample-data'
metadata = geometamaker.describe_collection(collection_path,
                                            depth=2,
                                            exclude_regex=r'.*\.json$',
                                            describe_files=True)
metadata.write()
```

#### CLI
```
geometamaker describe -d 2 --exclude .*\.json$ data/invest-sample-data
```
These examples will create `invest-sample-data-metadata.yml` as well as
create individual `.yml` documents for each dataset within the directory.

### Validating a metadata document:
If you have manually edited a `.yml` metadata document,
it is a good idea to validate it for correct syntax, properties, and types.

##### Python
```python
import geometamaker

document_path = 'data/watershed_gura.shp.yml'
error = geometamaker.validate(document_path)
print(error)
```

##### CLI
```
geometamaker validate data/watershed_gura.shp.yml
```

### Validating all metadata documents in a directory:

##### Python
```python
import geometamaker

directory_path = 'data/'
yaml_files, messages = geometamaker.validate_dir(data)
for filepath, msg in zip(yaml_files, messages):
    print(f'{filepath}: {msg}')
```

##### CLI
```
geometamaker validate data
```

### Configuring default values for metadata properties:

Users can create a "profile" that will apply some common properties
to all datasets they describe. Profiles can include `contact` information
and/or `license` information.

A profile can be saved to a configuration file so that it will be re-used
everytime you use `geometamaker`.

##### Python
```python
import geometamaker
from geometamaker import models

contact = {
    'individual_name': 'bob'
}
license = {
    'title': 'CC-BY-4'
}

# Two different ways for setting profile attributes:
profile = models.Profile(contact=contact)  # keyword arguments
profile.set_license(**license)             # `set_*` methods

config = geometamaker.Config()
config.save(profile)

# The saved profile will automatically be applied during `describe`:
resource = geometamaker.describe('data/watershed_gura.shp')
```

##### CLI
```
geometamaker config
```
This will prompt the user to enter their profile information.  
Also see `geometamaker config --help`.
