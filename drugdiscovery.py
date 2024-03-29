# -*- coding: utf-8 -*-
"""DrugDiscovery.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1u-7effa60F6HpPs7Hf9weeRbJz8p0BPZ

# **Computational Drug Discovery**

# **Part-1**

## **About ChEMBL Database**

The ChEMBL Database is a curated bioactivity data of > 2 Million Compounds.
Using this dataset, we will preprocessing on the *acetylcholinesterase* data.

## **Library Installs and Imports**

### **Installs**
"""

! pip install chembl_webresource_client

! wget https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.2-Linux-x86_64.sh
! chmod +x Miniconda3-py37_4.8.2-Linux-x86_64.sh
! bash ./Miniconda3-py37_4.8.2-Linux-x86_64.sh -b -f -p /usr/local
! conda install -c rdkit rdkit -y
import sys
sys.path.append('/usr/local/lib/python3.7/site-packages/')
# Execution time: 3 mins

! pip install lazypredict

"""### **Imports**"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style = "ticks")
from numpy.random import seed
from numpy.random import randn
from scipy.stats import mannwhitneyu
from rdkit import Chem 
from rdkit.Chem import Descriptors, Lipinski 
from chembl_webresource_client.new_client import new_client
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import VarianceThreshold

"""## **Functions**

### **Lipinski**
"""

def lipinski(smiles, verbose = False):
  moldata = []
  
  for element in smiles:
    mol = Chem.MolFromSmiles(element)
    moldata.append(mol)

  baseDataa = np.arange(1, 1)
  
  i = 0
  for mol in moldata:
    desc_MolWt = Descriptors.MolWt(mol)
    desc_MolLogP = Descriptors.MolWt(mol)
    desc_NumHDonors = Lipinski.NumHDonors(mol)
    desc_NumHAcceptors = Lipinski.NumHAcceptors(mol)

    row = np.array([
        desc_MolWt, 
        desc_MolLogP,
        desc_NumHDonors,
        desc_NumHAcceptors
    ])

    if (i == 0):
      baseData = row
    else:
      baseData = np.vstack([baseData, row]) 
    i = i + 1

  columnsNames = ["MW", "LogP", "NumHDonors", "NumHAcceptors"]
  descriptors = pd.DataFrame(data = baseData, columns = columnsNames)

  return descriptors

"""### **pIC50**"""

def pIC50(input):
  pIC50 = []

  for i in input["standard_value_norm"]:
    molar = i * (10 ** -9) 
    pIC50.append(-np.log10(molar))

  input["pIC50"] = pIC50

  x = input.drop("standard_value_norm", 1)

  return x

"""### **normalization**"""

def norm_value(input):
  norm = []

  for i in input["standard_value"]:
    if i > 100000000:
      i = 100000000
    norm.append(i)

  input["standard_value_norm"] = norm
  x = input.drop("standard_value", 1)

  return x

"""### **Mann-Whitney U Test**

The Mann-Whitney U test, also known as the Wilcoxon rank-sum test, is a non-parametric statistical test used to determine whether two independent samples come from the same population or not. The test compares the median values of the two groups and checks if they are equal. Unlike the t-test, which assumes a normal distribution of the data, the Mann-Whitney U test makes no such assumptions, making it useful for non-normal data distributions.
"""

def mannwhitney(descriptor, verbose = False): 
  seed(1)

  selection = [descriptor, "class"]
  df = df_2class[selection]
  active = df[df["class"] == "active"]
  active = active[descriptor]

  selection = [descriptor, "class"]
  df = df_2class[selection]
  inactive = df[df["class"] == "inactive"]
  inactive = inactive[descriptor]

  stat, p = mannwhitneyu(active, inactive) 

  alpha = 0.05

  if p > alpha:
    interpretation = "Same distribution (fail to reject H0)"
  else: 
    interpretation = "Different distribution (reject H0)"

  results = pd.DataFrame({
      "Descriptor" : descriptor,
      "p" : p,
      "alpha" : alpha,
      "Interpretation" : interpretation
  }, index = [0])

  filename = "mannwhitneyu_" + descriptor + ".csv"
  results.to_csv(filename)

  return results

"""## **Target Protein**

*We are going to be working on acetylcholinesterase.*

Acetylcholinesterase (AChE) is an enzyme that breaks down the neurotransmitter acetylcholine, which is involved in transmitting signals between nerve cells. When a nerve impulse reaches the end of a nerve cell, it releases acetylcholine, which then binds to receptors on the next nerve cell to continue transmitting the impulse. AChE acts by rapidly breaking down acetylcholine, stopping the transmission of the nerve impulse.

In simple terms, AChE is an enzyme that helps control the transmission of nerve impulses by breaking down a key neurotransmitter. This helps ensure that signals are transmitted smoothly and effectively between nerve cells.
"""

# Target Search for Coronavirus

target = new_client.target
target_query = target.search("acetylcholinesterase")
targets = pd.DataFrame.from_dict(target_query)

"""
  Execution time: 3s
  Prints all the databases present in chEMBL.
"""

targets

"""We are going to be choosing the target enzyme for Homo Sapiens.

Choosing the required *target_chembl_id*, we'll store the related data in a variable "selected_target*.
"""

selected_target = targets.target_chembl_id[0]

# selected_target #CHEMBL220

activity = new_client.activity
res = activity.filter(target_chembl_id = selected_target).filter(standard_type = "IC50")

"""**IC50**:
It is a commonly used measure in pharmacology and toxicology to describe the potency of a drug or toxin. It refers to the concentration of the drug or toxin required to inhibit or halt the activity of a specific biological target (such as an enzyme or cell) by 50%.

For example, if a drug has an IC50 of 1 μM (micro-molar), this means that a concentration of 1 μM of the drug will reduce the activity of the target by 50%. Lower IC50 values indicate that a drug is more potent, as it takes a lower concentration to achieve the same effect.

In simple terms, IC50 is a measure of the potency of a drug or toxin, reflecting the concentration required to inhibit the activity of a specific target by 50%.
"""

df = pd.DataFrame.from_dict(res)
df

"""Saving this result into a csv, for faster use."""

len(df) # (8395, 43)
df.to_csv("acetylcholinesterase_01_bioactivity_data_raw.csv", index =  False)

"""## **Data Preprocessing**

Looking at the data, if there are NA or missing values in the **standard_value** and **canonical_smiles** columns, then drop it.

**Standard_Value**: The standard values in the ChEMBL database are numerical values associated with various activities or properties of chemical compounds. These values are used to compare and rank the potency, efficacy, or safety of different compounds and can be used to inform drug discovery and development.

**Canonical_smiles**: Canonical SMILES (Simplified Molecular Input Line Entry System) is a line notation representation of a chemical structure used in the ChEMBL database to encode the molecular structure of chemical compounds.

Canonical SMILES in the ChEMBL database provides a standardized way of encoding and comparing the molecular structures of chemical compounds, which is important for drug discovery and development.
"""

df2 = df[df.standard_value.notna()]
df2 = df2[df.canonical_smiles.notna()]

df2 # (5835, 43)
len(df2.canonical_smiles.unique()) # 5824

df2_nr = df2.drop_duplicates(["canonical_smiles"])
df2_nr # 5824

"""Now to look at the most important features, we will combine these to a common dataFrame:
1. molecule_chembl_id
2. canonical_simles
3. standard_value
"""

selection = ["molecule_chembl_id", "canonical_smiles", "standard_value"]
df3 = df2_nr[selection]

df3 # 5824 rows × 3 columns

"""Saving this dataframe as well into a CSV file."""

df3.to_csv("acetylcholinesterase_02_bioactivity_data_preprocessed.csv", index = False)

"""## **Class: active, inactive or intermediate**

The bioactivity data is in the IC50 unit. 

Compounds having values of less than 1000 nM will be considered to be active while those greater than 10,000 nM will be considered to be inactive. As for those values in between 1,000 and 10,000 nM will be referred to as intermediate.
"""

df4 = pd.read_csv("acetylcholinesterase_02_bioactivity_data_preprocessed.csv")

bioactivity_threshold = []
for i in df4.standard_value:
  if (float(i) >= 10000):
    bioactivity_threshold.append("inactive")
  elif float(i) <= 1000:
    bioactivity_threshold.append("active")
  else:
    bioactivity_threshold.append("intermediate")

bioactivity_class = pd.Series(bioactivity_threshold, name = "class")
# Convert the column into a panda series

df5 = pd.concat([df4, bioactivity_class], axis = 1)

df5 # 5824 rows × 4 columns

"""Saving to CSV file."""

df5.to_csv("acetylcholinesterase_03_bioactivity_data_curated.csv", index = False)

! zip acetylcholinesterase.zip *.csv

"""# **Part-2**

## **Working on the dataframe**
"""

df = pd.read_csv("acetylcholinesterase_03_bioactivity_data_curated.csv")
df

"""In case of mutiple values separated by ".", we need to take the longest sequence."""

df_no_smiles = df.drop(columns = "canonical_smiles")

smiles = []
for i in df.canonical_smiles.tolist():
  cpd = str(i).split(".")
  cpd_longest = max(cpd, key = len)
  smiles.append(cpd_longest)

smiles = pd.Series(smiles, name = "canonical_smiles")
# smiles

df_clean_smiles = pd.concat([df_no_smiles, smiles], axis = 1)
df_clean_smiles

"""## **Lipinski Descriptors**

Calculate Lipinski descriptors
Christopher Lipinski, a scientist at Pfizer, came up with a set of rule-of-thumb for evaluating the **druglikeness** of compounds. 

Such druglikeness is based on the Absorption, Distribution, Metabolism and Excretion (ADME) that is also known as the pharmacokinetic profile. 

Lipinski analyzed all orally active FDA-approved drugs in the formulation of what is to be known as the Rule-of-Five or Lipinski's Rule.

The Lipinski's Rule stated the following:

**Molecular weight** < 500 Dalton
**Octanol-water partition coefficient** (LogP) < 5
**Hydrogen bond donors** < 5
**Hydrogen bond acceptors** < 10

### **Calculating Descriptors**
"""

df_lipinski = lipinski(df_clean_smiles.canonical_smiles)
df_lipinski # 5824 rows × 4 columns

"""### **Combining DataFrames**"""

df_combined = pd.concat([df, df_lipinski], axis = 1) 
df_combined

"""## **Converting IC50 to pIC50**

To allow IC50 data to be more uniformly distributed, we will convert IC50 to the negative logarithmic scale which is essentially -log10(IC50).

This custom function pIC50() will accept a DataFrame as input and will:

- Take the IC50 values from the standard_value column and converts it from nM to M by multiplying the value by 10
- Take the molar value and apply -log10
- Delete the standard_value column and create a new pIC50 column

We shall first use norm_value() function so that the values in the standard_value column are normalized.
"""

df_norm = norm_value(df_combined)

df_norm
df_norm.standard_value_norm.describe()

df_final = pIC50(df_norm) 
df_final
df_final.pIC50.describe()

"""Saving this to CSV"""

df_final.to_csv("acetylcholinesterase_04_bioactivity_data_3class_pIC50.csv")

"""We don't require the "intermediate" ones, therefore the rows having that will be removed.

### **Getting rid of "intermediate"**
"""

df_2class = df_final[df_final["class"] != "intermediate"]

df_2class # 4366 rows × 8 columns

"""Saving to CSV."""

df_2class.to_csv("acetylcholinesterase_05_bioactivity_data_2class_pIC50.csv")

"""## **EDA (Exploratory Data Analysis)**

Let's see how "frequent active" and "inactive" are.
"""

plt.figure(figsize = (5, 5))

sns.countplot(x = "class", data = df_2class, edgecolor = "black")

plt.xlabel("Bioactivity class", fontsize = 14, fontweight = "bold")
plt.ylabel("Frequency", fontsize = 14, fontweight = "bold")
plt.title("Frequency of active and inactive in column class")

plt.savefig("plot_bioactivity_class.pdf")

"""if we plot a MW vs LogP scattorplot, we can see that there are similar chemical spaces both of the two classes have (there aren't huge separations)."""

# plt.figure(figsize = (5, 5))
# sns.scatterplot(x = "MW", y = "LogP", data = df_2class, hue = "class", size = "pIC50", edgecolor = "black", alpha = 0.7)

# plt.xlabel("MW", fontsize = 14, fontweight = "bold")
# plt.ylabel("LogP", fontsize = 14, fontweight = "bold")
# plt.legend(bbox_to_anchor = (1.05, 1), loc = 2, borderaxespad = 0)
# plt.title("Plot between MW vs LogP, for column class")

# plt.saveFig("plot_MW_vs_LogP.pdf")

"""### **Box Plots**

**pIC50 value**
"""

plt.figure(figsize = (5, 5))

sns.boxplot(x = "class", y = "pIC50", data = df_2class)

plt.xlabel("Bioactivity class", fontsize = 14, fontweight = "bold")
plt.ylabel("pIC50 value", fontsize = 14, fontweight = "bold")
plt.title("pIC50 value for active and inactive in column class")

plt.savefig("plot_ic50.pdf")

mannwhitney("pIC50")

"""**MW**"""

plt.figure(figsize = (5, 5))

sns.boxplot(x = "class", y = "MW", data = df_2class)

plt.xlabel("Bioactivity class", fontsize = 14, fontweight = "bold")
plt.ylabel("MW", fontsize = 14, fontweight = "bold")
plt.title("MW value for active and inactive in column class")

plt.savefig("plot_MW.pdf")

mannwhitney("MW")

"""**LogP**"""

plt.figure(figsize = (5, 5))

sns.boxplot(x = "class", y = "LogP", data = df_2class)

plt.xlabel("Bioactivity class", fontsize = 14, fontweight = "bold")
plt.ylabel("LogP", fontsize = 1, fontweight = "bold")
plt.title("LogP value for active and inactive in column class")

plt.savefig("plot_LogP.pdf")

mannwhitney("LogP")

"""**NumHDonors**"""

plt.figure(figsize = (5.5, 5.5))

sns.boxplot(x = "class", y = "NumHDonors", data = df_2class)

plt.xlabel("Bioactivity class", fontsize = 14, fontweight = "bold")
plt.ylabel("NumHDonors", fontsize = 14, fontweight = "bold")
plt.title("NumHDonors values for Active and Inactive in Class Columns")

plt.savefig("plot_NumHDonors.pdf")

mannwhitney("NumHDonors")

"""**NumHAcceptors**"""

plt.figure(figsize = (5, 5))

sns.boxplot(x = "class", y = "NumHAcceptors", data = df_2class) 

plt.xlabel("Bioactivity class", fontsize = 14, fontweight = "bold")
plt.ylabel("NumHAcceptors", fontsize = 14, fontweight = "bold")
plt.title("NumHAcceptors value for active and inactive in class column")

plt.savefig("plot_NumHAccptors.pdf")

mannwhitney("NumHAcceptors")

"""**Intepretation**

**Box Plots**
pIC50 values
Taking a look at pIC50 values, the actives and inactives displayed *statistically significant difference*, which is to be expected since threshold values (IC50 < 1,000 nM = Actives while IC50 > 10,000 nM = Inactives, corresponding to pIC50 > 6 = Actives and pIC50 < 5 = Inactives) were used to define actives and inactives.

**Lipinski's descriptors**
All of the 4 Lipinski's descriptors exhibited *statistically significant difference* between the actives and inactives.
"""

! zip -r results.zip . -i *.csv *.pdf

"""# **Part 3**

We will be calculating molecular descriptors that are essentially quantitative description of the compounds in the dataset.

## **PaDEL-Descriptor**

PaDEL-descriptor is a tool for the calculation of molecular descriptors for small molecules used in drug discovery and computational chemistry. It is an open-source software developed by the University of South Australia.

Molecular descriptors are numerical values that describe various properties of small molecules such as size, shape, polarity, and hydrophobicity.

In summary, PaDEL-descriptor is a valuable tool for the calculation of molecular descriptors and their use in computational chemistry and drug discovery.
"""

! wget https://github.com/dataprofessor/bioinformatics/raw/master/padel.zip
! wget https://github.com/dataprofessor/bioinformatics/raw/master/padel.sh

! unzip padel.zip

"""**Loading Data**"""

df3 = pd.read_csv("acetylcholinesterase_04_bioactivity_data_3class_pIC50.csv")
df3

selection = ["canonical_smiles", "molecule_chembl_id"]
df3_selection = df3[selection]
df3_selection.to_csv("molecule.smi", sep = "\t", index = False, header = False)

! cat molecule.smi | head -5

! cat molecule.smi | wc -l

"""## **FingerPrint Descriptors**

Fingerprint descriptors are a type of molecular descriptors used in computational chemistry and drug discovery. 

They are binary numerical representations of a molecule's structural information, typically based on the presence or absence of certain chemical features.
"""

! cat padel.sh

"""**Note: Remove once Files are saved**"""

!bash padel.sh

# The most time consuming cell
# Execution time: over 10 mins

! ls -l

"""## **X and Y Data Matrics**

### **X**
"""

df3_X = pd.read_csv("descriptor_output.csv")
df3_X = df3_X.drop(columns = ["Name"])

df3_X

"""### **Y**"""

df3_Y = df3["pIC50"] 

df3_Y

"""### **Combining X and Y variable**"""

dataset3 = pd.concat([df3_X, df3_Y], axis = 1)
dataset3 
dataset3.to_csv("acetylcholinesterase_06_bioactivity_data_3class_pIC50_pubchem_fp.csv")

"""# **Part 4**

We will be building a regression model of acetylcholinesterase inhibitors using random forest algorithm.
"""

df = read_csv("acetylcholinesterase_06_bioactivity_data_3class_pIC50_pubchem_fp.csv")

"""## **Input & output Features**

The *Acetylcholinesterase* data set contains 881 input features and 1 output variable (pIC50 values).

### **Input Features**
"""

X = df.drop("pIC50", axis = 1)

X
X.shape

"""### **Output Features**

We are supposed to calculate/predict the pIC50 value.
"""

Y = df.pIC50

Y
Y.shape

"""### **Remove low Variance features**"""

selection = VarianceThreshold(threshold = (.8 * (1 - .8)))
X = selection.fit_transform(X)

X.shape

"""### **Data Split (80/20)**"""

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.2)

X_train.shape, Y_train.shape
X_test.shape, Y_test.shape

"""## **Building the Model**"""

model = RandomForestRegressor(n_estimators = 100)
model.fit(X_train, Y_train)

r2 = model.score(X_test, Y_test)   
r2

Y_pred = model.predict(X_test)

"""## **Scatter Plot for pIC50**"""

sns.set(color_codes = True)
sns.set_style("white")

ax = sns.regplot(Y_test, Y_pred, scatter_kws = {"alpha": 0.4})
ax.set_xlabel("Experimental pIC50", fontsize = "large", fontweight = "bold")
ax.set_ylabel("Predicted pIC50", fontsize = "large", fontweight = "bold")
ax.title("Scatter Plot of Experimental vs Predicted pIC50 values")
ax.set_xlim(0, 12)
ax.set_ylim(0, 12)
ax.figure.set_size_inches(5, 5)
plt.show

"""# **Part 5**

We will be comparing several ML algorithms for build regression models of acetylcholinesterase inhibitors.
"""

df = pd.read_csv("acetylcholinesterase_06_bioactivity_data_3class_pIC50_pubchem_fp.csv")

X = df.drop("pIC50", axis = 1)
Y = df.pIC50

"""## **Data Preprocessing**"""

X.shape
selection = VarianceThreshold(threshold = (.8 * (1 - .8)))
X = selection.fit_transform(X)
X.shape

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.2, random_state = 42)

"""## **Comparing ML Algorithms**"""

clf = LazyRegressor(verbose = 0, ignore_warnings = True, custom_metric = None)
models_train, predictions_train = clf.fit(X_train, X_train, Y_train, Y_train)
models_test, predictions_test = clf.fit(X_train, X_test, Y_train, Y_test)

predictions_train
predictions_test

"""## **Data Visualization for Model Performance**"""

plt.figure(figsize = (5, 10))
sns.set_theme(style = "whitegrid")
ax = sns.barplot(y = predictions_train.index, x = "R-Squared", data = predictions_train)
ax.set(xlim = (0, 1))

plt.figure(figsize = (5, 10))
sns.set_theme(style = "whitegrid")
ax = sns.barplot(y = predictions_train.index, x = "RMSE", data = predictions_train)
ax.set(xlim = (0, 10))

plt.figure(figsize = (5, 10))
sns.set_theme(style = "whitegrid")
ax = sns.barplot(y = predictions_train.index, x = "Time Taken", data = predictions_train)
ax.set(xlim = (0, 10))