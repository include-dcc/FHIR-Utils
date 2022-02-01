#!/usr/bin/env python

"""
    This script is based on the script from KF: https://github.com/kids-first/kf-model-fhir/blob/master/scripts/hpo_codesystem.py

    The primary change is to make it suitable for more than a single ontology using a simple YAML configuration. 

    Input: YAML configuration with details describing original .owl file URL and a few fields required for identifying the codes of interest

    Output: codesystems/{onto_name}_cs.json
"""

import json
import os
import sys

from pathlib import Path

# We'll provide the details for each of our systems by way of a yaml file
from yaml import safe_load

import pdb

# OWL to FHIR transformer compiled from https://github.com/aehrc/fhir-owl
FHIR_OWL_BIN = "fhir-owl-v1.1.jar"


if len(sys.argv) != 2:
    print("You must provide a single argument, the YAML file containing the details required for each of the code systems to be downloaded and converted for use with FHIR")
    print("The YAML file may contain more than one ontology in it. Below is an example of the configuration for HP:")
    print("""hpo:
  url: http://purl.obolibrary.org/obo/hp.owl
  name: Human Phenotype Ontology
  namespace: http://purl.obolibrary.org/obo/HP_
  code_prefix: 'HP:'""")
    sys.exit(1)

config = safe_load(open(sys.argv[1]))

for vocabulary in config.keys():
    data = config[vocabulary]

    outputdir = Path("codesystems")
    outputdir.mkdir(exist_ok=True, parents=True)

    output_filename = outputdir / f"{vocabulary}_cs.json"
    owl_filename = data['url'].split("/")[-1]

    # Convert OWL file to FHIR CodeSystem
    ret = os.system(f"wget -N {data['url']} && java -jar {FHIR_OWL_BIN} -i {owl_filename} -o {output_filename} -id {vocabulary} -name {data['name']} -content not-present -mainNs {data['namespace']} -descriptionProp http://purl.org/dc/elements/1.1/subject -status active -codeReplace _,:")

    if ret != 0:
        sys.exit()

    # Remove cross-references to other ontologies
    with open(output_filename) as hj:
        codes = json.load(hj)

    codes["concept"] = [c for c in codes["concept"] if c["code"].startswith(f"{data['code_prefix']}")]
    for c in codes["concept"]:
        c.pop("designation", None)

    with open(output_filename, "w") as hj:
        json.dump(codes, hj, indent=2)
