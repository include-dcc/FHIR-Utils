# FHIR-Utils
Scripts used to help with ingestion into FHIR for various datasets. 

These are better suited for living outside any particular dataset ingestion repository. 

## Include Codesystems
A script has been provided inside the subdirectory, include-codesystems, to download .owl files and convert them to FHIR CodeSystems. Included is a YAML configuration file for pulling [Mondo](https://mondo.monarchinitiative.org/) and [Human Phenotype](https://hpo.jax.org/app/) ontologies in their entirety. 

This script uses a JAR file from https://github.com/aehrc/fhir-owl  This currently assumed to have been downloaded into the current working directory. 
