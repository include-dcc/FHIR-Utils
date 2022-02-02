# VUMC FHIR Model Overview
Clarification on what resources the VUMC team are using and how those resources are being used to represent the data within FHIR.

## Study Metadata-Data Dictionary
To capture the structure of the datasets as we receive them, we are processing the dataset's data-dictionary and recording it into FHIR as mix of resources which will be used throughout the data items that have been loaded. 

### Data Dictionary (ActivityDefinition)
Each table of data is represented as a single [ActivityDefinition](https://hl7.org/fhir/R4/activitydefinition.html). This resource contains a list of each of that table's "columns" inside the *observationResultRequirement* property as a list of ObservationDefinitions. 

### Data Column (ObservationDefinition)
When we get a fully descriptive data dictionary, these fields will be represented as [ObservationDefinitions](https://hl7.org/fhir/R4/observationdefinition.html) which can specify the following:

| Data Component | Property in FHIR |
| -------------- | ---------------- |
| Column Name | name (TBD) |
| Column Description | description |
| Data Type Permitted | permittedDataType which can be from the values "Quantity, CodeableConcept, string, boolean, integer, Range, Ratio, SampledData, time, dateTime, Period" |
| min/max for numerics | qualifiedInterval.range |
| Categorical values for drop box type questions | validCodedValueSet |

So far, the data dictionaries we've received for DS-Connect and HTP have been very different and not always as complete as they could be. It may be worth defining a formal format for groups to use to ensure that we can describe this data as completely as possible. 

### Codes
We use CodeSystems and ValueSets to itemize each column and any categorical response that may be found inside a given dataset. 

For all CodeSystems described below, a comprehensive ValueSet is also created. 

#### Column IDs as Codes
Column names are represented as Codes inside a data table's [CodeSystem](https://hl7.org/fhir/R4/codesystem.html) where the code is a short form of the name (if the name is cumbersome enough to warrant transformation) and the Display is either the long form of the name or the description found inside the data dictionary. 

Because we are using Whistle to do the transformation into FHIR objects, we also strip out various characters from the column names such as: Whitespace, Slashes ('/', '\') and other characters that may restrict property names in standard programming languages. 

All data associated with a given variable (column) will be coded with the variable's Code (so, an Observation's code will include a code from the appropriate ValueSet). 

#### Categorical Values as Codes
Similarly to the variables themselves, for those variables with a "dropbox" or "radio button" type, we create a CodeSystem specifically for the answers to that question. The script that generates these will attempt to recognize answer lists that are common across multiple questions and build only a single CodeSystem for the answer set. 

All categorical responses will be coded with the corresponding code from the question's answer list. 

## Study 
To capture the study itself, we use [ResearchStudy](https://hl7.org/fhir/R4/researchstudy.html) which includes a handful of obvious properties:
    * name
    * title
    * description

To capture membership details, we are currently creating groups that represent the various membership groupings such as consent groups, complete study, etc. All of these are stored within the enrollment list property. _It should be noted that, as of last inspection, R5 ResearchStudy is quite different and this will quite likely not be possible once the transition to 5 is made._

