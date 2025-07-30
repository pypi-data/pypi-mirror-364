# GSNetAct

Please cite this repository if you use this code in your work.

## Prerequisites

- Tested only on python 3.12, should work python 3.7+
- Numpy
- Scanpy
- Dataclasses
- Json
- Scikit-learn (Should come with scanpy but still)
- Requests

## Installing

#### Directly install latest version with pip

```
pip install gsnetact
```

#### Or clone the repository from this source.
```
git clone https://github.com/BMGLab/GSNetAct
```

- Then inside the project directory, do 
```
pip install .
```
The package should be installed. You can use the **-e** flag for automatic updates.

## Usage

You can use every part of this package to develop a further approach to this algorithm.
But for simple analysis, a basic use case below would be : 

```
#!/usr/bin/env python

from gsnetact import runGSNA

import scanpy as sc
import pandas as pd

adata_ = sc.read_h5ad("./test_data/pbmc3k.h5ad")
# Read the anndata object.

jsonFile = pjson("./test_data/deneme.json")
# Parse the json file into a pjson() object.

gsnaObject = runGSNA(adata_, jsonFile, normalized=True)
# Call the createObject function from the package.

df = pd.DataFrame(gsnaObject.X)
# Create a pandas dataframe from the AnnData object's X layer.

df.columns = gsnaObject.var
# Set the column names to the geneset names that are located in the var layer.

df.to_csv("output.csv", sep="\t")
# Create an output file, named  as output.csv.

```

This code firstly imports the **createObject** from the package, which is used for creating an AnnData object
using the analysis results. Then, we specify our file paths. The pathwayScoring package needs two file inputs,
one gene expression data file, and one JSON file that contains genesets and their relations. We then call the 
createObject function to get our files, analyzes them using the pathwayScoring's respected algorihm and creates an AnnData object using scanpy. We can use this object any way we want, for here it is used for creating a csv file 
that contains the scorings. 

For further explanation, check the test files in test/ folder.

## File Format for Genesets 

The file that contains genesets and their relations has to be like this : 
```
{
	"GeneSet1": {
		"Gene1": {
			"Gene2": 0.35,
			"Gene3": 0.77,
			"Gene4": 0.16
		},
		"Gene2": {
			"Gene1": 0.35,
			"Gene3": 0.51
		},
		"Gene3": {
			"Gene1": 0.77,
			"Gene2": 0.51,
			"Gene4": 0.40
		},
		"Gene4": {
			"Gene1": 0.16,
			"Gene3": 0.40
		}
	},
	"GeneSet2": {
		"Gene1": {
			"Gene2": 0.99
		},
		"Gene2": {
			"Gene1": 0.99
		}
	}
}
```
Here, GeneSet1 looks like this: 

![Graph for GeneSet1](/genesets.png)

You can create this format easily though, check below.

## JSON Creator Tool 

You can create the needed JSON file containing genesets with the data from msigdb databases. All you need to do is : 

```
#!/usr/bin/env python

from gsnetact import makeJson

makeJson("Path to your msigdb JSON file.","Name of the JSON file containing genesets, name them whatever you want.")

```
The makeJson function takes your geneset names from msigdb data and finds the relations between individual genes 
using the STRING database.


