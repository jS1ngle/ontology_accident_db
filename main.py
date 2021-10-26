import xml.etree.ElementTree as et
import ontology
import pre_processing
import term_extraction
import substance
import json
import pprint
from owlready2 import *
import settings

# ===json output
accident_data = []
substance_list_usage_counter = 0

pp = pprint.PrettyPrinter(indent=4)


# ===Read and process substances list
def read_and_tokenize_substance_db(filename):
    substances_in_list = []
    e = et.parse(filename).getroot()
    for atype in e.findall('name'):
        substance = atype.text.lower()
        substances_in_list.append(substance)
    return substances_in_list


def does_file_exists(file_path_and_name):
    return os.path.exists(file_path_and_name)


if settings.check_json:
    empty_substances = 0

    with open(settings.json_file_name) as data_file:
        data = json.load(data_file)

        for acc_case in data:
            if not acc_case["substance"]:
                empty_substances += 1
        print("Cases without substance:  " + str(empty_substances))

if settings.enhance_json:
    with open(settings.json_file_name, "r") as data_file:
        data = json.load(data_file)

        for acc_case in data:
            for subst in acc_case["substance"]:
                if not subst["name"] and subst["cas"]:
                    substance_name = substance.get_name_from_cas(subst["cas"])
                    subst["name"] = substance_name

    with open(settings.json_file_name, 'w') as data_file:
        json.dump(data, data_file, indent=4)

# ===== PREPROCESSED DATA==================================
if settings.create_preprocessing_json:
    start_time = time.time()
    i = settings.start_case_json

    e = et.parse(settings.database_file_name)
    root = e.getroot()

    # = Get substances
    substancesList = read_and_tokenize_substance_db('substances_list.xml')
    accident_cases = [accident_cases for accident_cases in e.findall('record')]

    for record in accident_cases[settings.start_case_json:settings.max_entries]:

        print("=== Case " + str(i))

        # ===== DATE
        date = record.find("StartDate").text

        hazardous_event = []
        potential_causes = []
        potentially_involved_units = []
        potential_consequences = []
        substance_text = None
        global_location_texts = None
        global_cause_texts = None
        global_consequence_texts = None
        global_hazardous_event_texts = None

        # =====SUBSTANCE
        potential_substance = []
        involved_substances = []
        substance_dict = {}

        if settings.find_substance_marker_active:
            # ===Identify cas number
            casNumbers, substance_text = pre_processing.get_cas_numbers(record)
            # ===search for substance name based on CAS number
            if casNumbers:
                for cas in casNumbers:
                    substance_name = pre_processing.find_name_from_cas(cas)

                    if isinstance(substance_name, (list,)):
                        continue

                    substance_name = substance_name.lower()
                    potential_substance.append(substance_name)
                    substance_dict["name"] = pre_processing.name_preparation_substance(substance_name)
                    substance_dict["cas"] = cas
                    substance_cid = substance.get_cid_of(substance_name)
                    haz_attr = substance.get_hazardous_attribute_of(str(substance_cid))
                    haz_attr = pre_processing.name_preparation(haz_attr)
                    substance_dict["haz_attr"] = haz_attr
                    involved_substances.append(substance_dict)
                    substance_dict = {}
            else:
                # ==search deeper in case no cas number is specified
                potential_substance = pre_processing.search_text_for_substance(record, substancesList)
                for subst in potential_substance:
                    substance_list_usage_counter += len(potential_substance)
                    substance_dict["name"] = pre_processing.name_preparation_substance(subst)
                    substance_dict["cas"] = ""
                    substance_cid = substance.get_cid_of(subst)
                    haz_attr = substance.get_hazardous_attribute_of(str(substance_cid))
                    haz_attr = pre_processing.name_preparation(haz_attr)
                    substance_dict["haz_attr"] = haz_attr
                    involved_substances.append(substance_dict)
                    substance_dict = {}

        # ===== LOCATION / EQUIPMENT
        if settings.find_unit_marker_active:
            potentially_involved_units, global_location_texts = term_extraction.get_specific_concepts(record,
                                                                                                      term_extraction.categories_of_locations,
                                                                                                      "units",
                                                                                                      settings.global_location_texts)
        # ===== HAZARDOUS EVENT
        if settings.find_hazard_marker_active:
            hazardous_event, global_hazardous_event_texts = term_extraction.get_specific_concepts(record,
                                                                                                  term_extraction.categories_of_failure_modes,
                                                                                                  "hazardous_events",
                                                                                                  settings.global_hazardous_event_texts)

        # ====== CAUSES
        if settings.find_causes_marker_active:
            potential_causes, global_cause_texts = term_extraction.get_specific_concepts(record,
                                                                                         term_extraction.categories_of_causes,
                                                                                         "causes",
                                                                                         settings.global_cause_texts)

        # ====== CONSEQUENCES
        if settings.find_consequences_marker_active:
            potential_consequences, global_consequence_texts = term_extraction.get_specific_concepts(record,
                                                                                                     term_extraction.categories_of_consequences,
                                                                                                     "consequences",
                                                                                                     settings.global_consequence_texts)

        tmp_dict = {"position": i, "date": date, "substance": involved_substances,
                    "unit": pre_processing.prepare_json_population(potentially_involved_units, "units")}

        temp_list = pre_processing.prepare_json_population(hazardous_event, "hazardous_events")
        temp_list = pre_processing.filter_fragmental_redundancies(temp_list)
        tmp_dict["hazardous_event"] = temp_list

        tmp_dict["causes"] = pre_processing.prepare_json_population(potential_causes, "causes")
        tmp_dict["consequences"] = pre_processing.prepare_json_population(potential_consequences, "consequences")

        tmp_dict["substance_description"] = substance_text
        tmp_dict["location_description"] = global_location_texts
        tmp_dict["he_description"] = global_hazardous_event_texts
        tmp_dict["causes_description"] = global_cause_texts
        tmp_dict["consequences_description"] = global_consequence_texts

        accident_data.append(tmp_dict)

        if i >= settings.max_entries - 1:
            print("Number of substances found in substance list: " + str(substance_list_usage_counter))
            file_present = does_file_exists(settings.json_file_name)
            if file_present:
                with open(settings.json_file_name, 'a+') as outfile:
                    json.dump(accident_data, outfile, indent=4)
            else:
                with open(settings.json_file_name, 'w') as file:
                    json.dump(accident_data, file, indent=4)

        i += 1

# ===== ONTOLOGY ===========================================
if settings.create_ontology:
    start_time = time.time()
    i = settings.star_case_ontology

    with open(settings.json_file_name) as data_file:
        data = json.load(data_file)

        if settings.create_basic_ontology:
            # === Basic classes and relationships
            ontology.predefine_core_concepts()

            for acc_case in data:
                print("==============================")
                print("Basic entry   " + str(i))

                # === Location
                for jLocation in acc_case["unit"]:
                    # settings.global_locations_detected += " " + jLocation
                    ontology.create_location_individual(jLocation)

                # === Forward declaration of hazardous_events (for causes and consequences)
                for jHe in acc_case["hazardous_event"]:
                    ontology.create_hazardous_event_individual(jHe)

                # === Substance
                for jSubstance in acc_case["substance"]:
                    if not jSubstance["name"]:
                        continue
                    else:
                        ontology.create_substance_individual(jSubstance)

                if i >= len(data) - 1:
                    if settings.create_basic_ontology:
                        ontology.save_ontology("chemical_accident_ontology.owl")
                    settings.basic_concepts_created = True
                    i = 0
                    break

                i += 1

        if settings.basic_concepts_created:
            for acc_case in data:
                print("==============================")
                print("Cause entry   " + str(i))

                # === Cause
                for jCause in acc_case["causes"]:
                    settings.global_causes_detected += " " + jCause
                    for substance_ in acc_case["substance"]:
                        substance = substance_["name"]
                        for location_ in acc_case["unit"]:
                            for he in acc_case["hazardous_event"]:
                                ontology.create_cause_individual(jCause, location_, substance_, he)

                if i >= len(data) - 1:
                    if settings.create_basic_ontology:
                        ontology.save_ontology("chemical_accident_ontology.owl")
                    cause_concepts_created = True
                    i = 0
                    break

                i += 1

        if settings.basic_concepts_created and cause_concepts_created:
            for acc_case in data:
                print("==============================")
                print("Consequence entry   " + str(i))

                for jConsequence in acc_case["consequences"]:
                    settings.global_consequence_detected += " " + jConsequence
                    for substance_ in acc_case["substance"]:
                        substance = substance_["name"]
                        for location_ in acc_case["unit"]:
                            for he in acc_case["hazardous_event"]:
                                ontology.create_consequence_individual(jConsequence, location_, substance_, he)

                if i >= len(data) - 1:
                    if settings.create_basic_ontology:
                        ontology.save_ontology("chemical_accident_ontology.owl")
                    consequence_concepts_created = True
                    i = 0
                    break

                i += 1

        if settings.basic_concepts_created and cause_concepts_created and consequence_concepts_created:
            for acc_case in data:
                print("==============================")
                print("HE entry   " + str(i))

                # ===Hazardous event
                for jHe in acc_case["hazardous_event"]:
                    for substance_ in acc_case["substance"]:
                        substance = substance_["name"]
                        for location_ in acc_case["unit"]:
                            ontology.create_he_individual(jHe, substance, location_)

                if i >= len(data) - 1:
                    if settings.create_basic_ontology:
                        ontology.save_ontology("chemical_accident_ontology.owl")
                    he_concepts_created = True
                    i = 0
                    break

                i += 1

        if settings.basic_concepts_created and cause_concepts_created and consequence_concepts_created and he_concepts_created:
            for acc_case in data:
                print("==============================")
                print("Complete accident entry   " + str(i))
                date = acc_case["date"]
                # ===Create accident
                ontology.create_accident_individual("Accident_" + str(i),
                                                    date,
                                                    acc_case["substance"],
                                                    acc_case["hazardous_event"],
                                                    acc_case["consequences"],
                                                    acc_case["causes"],
                                                    acc_case["unit"],
                                                    acc_case["substance_description"],
                                                    acc_case["location_description"],
                                                    acc_case["he_description"],
                                                    acc_case["causes_description"],
                                                    acc_case["consequences_description"],
                                                    )

                if i >= len(data) - 1:
                    if settings.create_basic_ontology:
                        ontology.save_ontology("chemical_accident_ontology.owl")
                    i = 0
                    break

                i += 1

    with open(settings.json_file_name) as data_file:
        data = json.load(data_file)


# ===== JSON ANALYSIS ======================================
if settings.check_json:
    with open(settings.json_file_name) as data_file:
        data = json.load(data_file)

    locations = []
    he = []
    cause = []
    consequence = []
    cas = []
    substances = []
    no_case_with_substance = 0
    haza_text = ""

    for acc_case in data:

        for jLocation in acc_case["unit"]:
            locations.append(jLocation)

        for jHe in acc_case["hazardous_event"]:
            he.append(jHe)

        substance_considered = False
        for jSubstance in acc_case["substance"]:
            if jSubstance["cas"]:
                cas.append(jSubstance["cas"])
            if jSubstance["name"] and not substance_considered:
                no_case_with_substance += 1
                substance_considered = True
            if jSubstance["name"] and not jSubstance["cas"]:
                substances.append(jSubstance["name"])
            for jHaza in jSubstance["haz_attr"]:
                haza_text += jHaza + " "

        for jCause in acc_case["causes"]:
            cause.append(jCause)

        for jConsequence in acc_case["consequences"]:
            consequence.append(jConsequence)

    cas = list(filter(None, cas))
    cas = list(dict.fromkeys(cas))
    print("Cas numbers detected:  ", len(cas))
    print("Number of cases with substance (at least 1):  ", no_case_with_substance)

    substances = list(filter(None, substances))
    substances = list(dict.fromkeys(substances))
    print("Substance names without cas number detected:  ", len(substances))
    print("Total number detected substances:  ", len(substances) + len(cas))

    he = list(filter(None, he))
    he = list(dict.fromkeys(he))
    print("Hazardous events detected:  ", len(he))

    locations = list(filter(None, locations))
    locations = list(dict.fromkeys(locations))
    print("Locations detected:  ", len(locations))

    cause = list(filter(None, cause))
    cause = list(dict.fromkeys(cause))
    print("Causes detected:  ", len(cause))

    consequence = list(filter(None, consequence))
    consequence = list(dict.fromkeys(consequence))
    print("Consequences detected:  ", len(consequence))

    print("Frequency of detected hazardous attributes")
    term_extraction.statistical_analysis(haza_text)

print("--- %s seconds ---" % (time.time() - start_time))
