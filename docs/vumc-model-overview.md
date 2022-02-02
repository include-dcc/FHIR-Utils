# VUMC FHIR Model Overview
Clarification on what resources the VUMC team are using and how those resources are being used to represent the data within FHIR.

## Study Metadata
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
