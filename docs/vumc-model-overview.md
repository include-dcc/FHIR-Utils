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

## Age Representation
To represent age, we are using the [Relative Date/Time Extension](http://hl7.org/fhir/StructureDefinition/cqf-relativeDateTime") This allows us to embed it anywhere a regular date might be provided however, it is not a specific date. To facilitate this feature, the extension is added to the target field's property which has an "_" preceeding the regular property name. 

Please note the modified property, _valueDateTime below. This would normally be valueDateTime: 
```json        
    {
      "resourceType": "Observation",
      "id": "3",
      "identifier": [ {
        "system": "https://include.org/ds-connect/fhir/observation",
        "value": "ds-connect.5766age_at_registration"
      } ],
      "status": "final",
      "code": {
        "coding": [ {
          "system": "https://nih-ncpi.github.io/ncpi-fhir-ig/data-dictionary/ds-connect/demo",
          "code": "age_at_registration",
          "display": "age_at_registration"
        } ],
        "text": "age_at_registration"
      },
      "subject": {
        "reference": "Patient/1"
      },
      "focus": [ {
        "reference": "ObservationDefinition/2"
      } ],
      "_valueDateTime": {
        "extension": [ {
          "url": "http://hl7.org/fhir/StructureDefinition/cqf-relativeDateTime",
          "extension": [ {
            "url": "target",
            "valueReference": {
              "reference": "Patient/1"
            }
          }, {
            "url": "targetPath",
            "valueString": "birthDate"
          }, {
            "url": "relationship",
            "valueCode": "after"
          }, {
            "url": "offset",
            "valueDuration": {
              "value": 29,
              "system": "http://unitsofmeasure.org",
              "code": "a"
            }
          } ]
        } ]
      }
    }
```
## Participants (Patient)
For each participant a corresponding [Patient](https://hl7.org/fhir/R4/patient.html) resource is created. This provides some whatever details we have access to below:

| Variable Name | FHIR Representation | Possible Codings |
| ------------- | ------------------- | ---------------- |
| sex | gender | [male, female, other, unknown](https://hl7.org/fhir/R4/valueset-administrative-gender.html) |
| race | extension with url "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race" | TBD |
| ethnicity | extension with url "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity" | TBD |

## Study 
To capture the study itself, we use [ResearchStudy](https://hl7.org/fhir/R4/researchstudy.html) which includes a handful of obvious properties:
    * name
    * title
    * description

To capture membership details, we are currently creating groups that represent the various membership groupings such as consent groups, complete study, etc. All of these are stored within the enrollment list property. _It should be noted that, as of last inspection, R5 ResearchStudy is quite different and this will quite likely not be possible once the transition to 5 is made._

### Study Participants
To tie a Patient to the study, we are using [ResearchSubject](https://hl7.org/fhir/R4/researchsubject.html). This is a simple resource with attributes *study* which points to the Study resource and *individual* which points to the Patient resource. 

### Study Groups
For datasets where we have individual consent group information, a group will be created for each distinct consent group. In addition to these consent groups, there will also be a single "complete" group which contains all valid participants of the study. 

Participants of the relevant groups will be added as *Patient References* inside the group's *member* list as *entity* entries. 

### DS-Connection Questionnaire (and DS Diagnosis/Karyotype)
For most of the questions, the column names have been modified to be more "computer friendly" and the actual column name is available as part of the IHQ's code system. The contents of an individual's responses are recorded as follows: 

#### Observations
For each data point for which a answer is recorded, an [Observation](https://hl7.org/fhir/R4/observation.html) will be created. 

    * code - The code for these observations will be the code associated with the question from the IHQ code system. 
    * subject - Reference to the Patient
    * focus - Reference to the formal ObservationDefinition describing this question in the data-dictionary
    * value[x] - Data found at the given column for this particular patient. 

#### Conditions (Any reference to a diagnosis with an Annotation from Mondo or HPO)
For values that were annotated in the google sheet produced by Pierrette and Nicole, data with a Mondo or HPO code with a positive finding are also recorded as [Condition](https://hl7.org/fhir/R4/condition.html) resources. These conditions will have the proper Mondo or HPO code as part of their code property. 

    * code - The code for these conditions will include the relevant code from Mondo or HPO
    * subject - Reference to the patient

In addition to the Mondo or HPO code, there will also be a code referencing the Question/Answer code from the dataset/table's code system. 

Please note that for those responses that aren't indicative of an actual diagnosis of a condition will not become conditions. Those can only be identified as Object resources. 

### HTP 
For HTP, for things that are noted as conditions in the original dataset will be treated to the same process as the DS-Connection Questionnaires. Basically, all non-missing data will be represented as an Observation and anything with a Mondo or HPO annotation will result as a Condition. 

### HTP BMI+ and Encounters
HTP provides BMI, Weight and Height along with an "age at" data point. The measurement components are recorded as Observations and the "age at" component is recorded as an Encounter to which each of the 3 observations refers to. 

#### Encounter
As noted above, all age related dates are encoded using the relative date/time extension. For [Encounters](https://hl7.org/fhir/R4/encounter.html), we associate the relative date with the following field: 
    * period._start 

#### Measurement (Observation)
For measurements, we'll record the measurement in the [Observation](https://hl7.org/fhir/R4/observation.html) resource. 
    * code - Will include any public ontology that is mapped (if there is one) as well as the data-dictionary component associated with the measurement (such as BMI, or Height, etc).
    * subject - Reference to the patient
    * focus - Reference to the ObservationDefinition describing this variable
    * encounter - The encounter where the age_at value is recorded
    * value[x] - The measurement itself. 

### HTP Family Group
While there probably is some family data, I don't currently have it. However, to associate related members together, we are creating [Group](https://hl7.org/fhir/R4/group.html) resources whose members are those individuals with the specified family ID.

### HTP Biospecimen 
(This is still somewhat a work in progress)

For bio-specimen data, we are using the standard FHIR [Specimen](https://hl7.org/fhir/R4/specimen.html) resource. The data I received for HTP contains information for what has been called the Bio-specimen as well as the Sample types. The 3rd type, Derived Sample type is presumably going to be tied to the actual data file deliverable which we haven't received. 

All specimen types that have been annotated with NCIt codes will have their NCIt codes assigned to the type coding. For those where no annotation can be found, the type coding's "text" will record the text representation provided in the data file. 

    * status - "Available" if volume is provided and greater than 0. Otherwise, "Unavailable"
    * type - Code associated with the specimen type
    * subject - reference to the Patient's resource
    * collection.quantity.value (and unit) associated with the value from the data (collection is not present if the value is missing)