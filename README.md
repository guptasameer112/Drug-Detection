# Drug-Detection
Using chEMBL dataset and RandomForestClassfier to predict pIC50 values of acetylcholinesterase enzyme.

Some additional Information regarding the terminologies used in the project:

*Acetylcholinesterase*: It is involved in transmitting signals between nerve cells, particularly in the brain and muscle. It helps break down enzyme called acetylcholine, preventing excessive simulation of the nerve cells and allows for proper regulation of neurotransmitter levels.

*ChEMBL dataset*: ChEMBL is a comprehensive and freely available dataset which primarily focuses on small molecules and their interactions with biological macromolecules such as proteins and enzymes.
It includes compound structures, activity data, binding affinities, and other relevant properties.

*pIC50* values are a way to measure how strong or effective a compound is in stopping a certain biological activity. The scales tells us about the potency of a compound.
The higher the pIC50 value, the powerful the compound is.
(nM - nanomolar, unit of concentration)

*rdkit*: It is an open-source toolkit for cheminformatics, primarily used for handling and analyzing chemical structures and molecules. It is also useful in chemical structure manipulation, molecular descriptors, chemical informatics analysis, machine learning and data analysis.

*Mann-Whitney U test*: It is a statistical test used to compare two groups of data when the data doesn’t meet certain assumptions. The test provides a p-value, and if the p-value is low, it suggests that there is a significant difference between the groups.

*Lipinski*: These are a set of guidelines used in drug development to determine if a chemical compound has a good chance of becoming an effective oral medication.
Some of the criterias are: Molecular weight, Lipophilicity, Hydrogen bond donors and Hydrogen bond acceptors.

*RandomForestRegressor*: It is a machine learning algorithm used for regression tasks, meaning prediction of continous numerical values. It works on the principle of an ensemble, where multiple decision trees work together to make predictions.
Each decision tree is trained on a random subset of the data and uses a random set of features to make predictions.
Each tree predictes the outcome based on its own set of rules. The final prediction is the average of the predictions made by all the trees.
With RFR, there is no requirement to imputate or remove instances with missing values, it uses the available information in other features to make predictions.

*VarianceThreshold*: It is a feature selection method used in machine learning to remove low-variance features from the dataset.
It is a simple yet effective technique for reducing the dimensionality of the dataset by eliminating features with little or no variance.
It calculates the variance of each feature in the dataset, therefore determining the spread or variability of values within a feature. Features with low variance indicate that they have almost constant values, thereby being less informative for making predictions.
It provides a variance threshold, application of which removes features that have variance lower than the threshold.

SMILES notation helps standardize the representation of chemical structures and enables the calculation of molecular properties needed for evaluating compounds according to Lipinski’s rule of five.
