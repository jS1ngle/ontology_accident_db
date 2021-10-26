# =====SETTINGS===========================================
json_file_name = 'preprocessed_data.json'

find_substance_marker_active = True
find_unit_marker_active = True
find_hazard_marker_active = True
find_causes_marker_active = True
find_consequences_marker_active = True

create_ontology = True
create_preprocessing_json = False

# max entries 889
start_case_json = 0
max_entries = 889
star_case_ontology = 0

load_existing_ontology = False

create_basic_ontology = True
create_causes_ontology = True

show_number_global_terms = False
show_number_identified_terms = True

check_json = False
enhance_json = False

if not create_basic_ontology and create_causes_ontology:
    basic_concepts_created = True
else:
    basic_concepts_created = False

# ====Names
database_file_name = "eMARS_Export_filled.xml"

# ===Global list
global_location_texts = ""
global_cause_texts = ""
global_consequence_texts = ""
global_hazardous_event_texts = ""

global_locations_detected = ""
global_causes_detected = ""
global_consequence_detected = ""
global_hazardous_event_detected = ""
global_substances_detected = ""

haz_e_list = []
found_locations = []
hazardousEvent = []
found_substances = []
