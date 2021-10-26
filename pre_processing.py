import re
from nltk.corpus import wordnet
import pubchempy as pcp
import itertools

from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))


def remove_duplicates(original_list):
    processed_list = []
    seen = set()
    for x in original_list:
        if x not in seen:
            processed_list.append(x)
            seen.add(x)
    return processed_list


def get_cas_numbers(record):
    complete_information = ""
    # =====Get CAS numbers
    substance_description = str(record.find('SubstanceClassification').text)
    if substance_description:
        complete_information = "1. " + substance_description + " "
    substance_description = substance_description.lower()

    if substance_description is None:
        cas_numbers_a = []
    else:
        cas_numbers_a = re.findall(r'\d+-\d+-\d+', substance_description)

    substance_involved = record.find('SubstanceInvolved').text
    if substance_involved:
        complete_information += "2. " + substance_involved

    if substance_involved is None:
        cas_numbers_b = []
    else:
        cas_numbers_b = re.findall(r'\d+-\d+-\d+', substance_involved)

    # ==measure similarity
    cas_nums = cas_numbers_a + cas_numbers_b
    cas_numbers = []

    for word in cas_nums:
        if word not in cas_numbers and not word.startswith('0'):
            cas_numbers.append(word)

    return cas_numbers, complete_information


def filter_fragmental_redundancies(initial_list):
    if len(initial_list) > 1:
        max_string = max(initial_list, key=len)

        for item in list(initial_list):
            if item in max_string and item is not max_string:
                initial_list.remove(item)

        for item in list(initial_list):
            if any(item in s and item is not s and len(item) < len(s) for s in initial_list):
                initial_list.remove(item)

    return initial_list


def search_text_for_substance(record, substances_list):
    # ==search deeper in case no cas number is specified
    substance_description = str(record.find('SubstanceClassification').text)
    substance_description += (" " + str(record.find('SubstanceInvolved').text))
    substance_description += (" " + str(record.find('AccidentDescription').text))

    substance_description = substance_description.lower()

    potential_substance = []
    for substance in substances_list:
        if substance in substance_description:
            potential_substance.append(substance)

    potential_substance = filter_fragmental_redundancies(potential_substance)
    potential_substance = list(dict.fromkeys(potential_substance))

    return potential_substance


def find_name_from_cas(cas_number):
    name = []
    try:
        syn = pcp.get_synonyms(cas_number, 'name', 'substance')
    except pcp.PubChemPyError as e:
        return name
    for d in syn:
        for k, v in d.items():
            if k == 'Synonym':
                name = v[0]
                break
        else:
            continue
        break
    return name


# see https://rodic.fr/blog/camelcase-and-snake_case-strings-conversion-with-python/
def snake2camel(name):
    return re.sub(r'(?:^|_)([a-z])', lambda x: x.group(1).upper(), name)


def has_numbers(input_string):
    return any(char.isdigit() for char in input_string)


# see https://stackoverflow.com/questions/30184331/how-to-delete-synonyms/30184763
def in_synonyms(list_of_synonym_lists, word):
    for index, synonym_list in enumerate(list_of_synonym_lists):
        if word in synonym_list:
            return index
    return -1


def get_synonyms(word):
    syn = []
    for synset in wordnet.synsets(word):
        for lemma in synset.lemma_names():
            syn.append(lemma)
    return syn


def resolve_redundancies(input_data):
    input_data = list(dict.fromkeys(input_data))

    if len(input_data) > 1:
        for a, b in itertools.combinations(input_data, 2):
            synonym_a = get_synonyms(a)
            synonym_b = get_synonyms(b)
            if a and b:
                if not any(a in s for s in input_data) or not any(
                        b in s for s in input_data):
                    break

                match = not set(synonym_a).isdisjoint(synonym_b)
                if match:
                    if a:
                        input_data.remove(b)
                    else:
                        input_data.remove(a)
                    if len(input_data) < 2:
                        break

    return input_data


def remove_verbs(input_list):
    output = []
    for it in input_list:
        tmp = wordnet.synsets(it)[0].pos()
        if not tmp == 'v':
            it = it.replace(" ", "_")
            it = snake2camel(it)
            output.append(it)
        else:
            continue
    return output


# tree search algorithm
def locate_by_name(e, name):
    if e.get('name', None) == name:
        return e
    for child in e.get('children', []):
        result = locate_by_name(child, name)
        if result is not None:
            return result
    return None


def name_preparation(list):
    prep = []
    for e in list:
        if isinstance(e, str):
            e = e.replace(" ", "_").lower()
            e = snake2camel(e)
            prep.append(e)
    return prep


def name_preparation_substance(name):
    if isinstance(name, str):
        if has_numbers(name):
            name = ""
        name = name.replace("-", " ").lower()
        name = name.replace(" ", "_")
        name = re.sub("[\(\[].*?[\)\]]", "", name)
        name = name.split(',', 1)[0]
        name = snake2camel(name)
        name = name.replace("_", "")
    else:
        name = ""
    return name


def contains(lst, target):
    for i in lst:
        if target(i):
            return True
    return False


def prepare_json_population(concept, target):
    content = []

    for elem in concept:
        if not elem:
            continue
        else:
            if target == "units":
                dict_element = elem['units']
            if target == "causes":
                dict_element = elem['causes']
            if target == "hazardous_events":
                dict_element = elem['failure_mode']
        if target == "consequences":
            dict_element = elem['consequences']

        for de in dict_element:
            content.append(de)

    content = list(filter(None, content))
    content = list(dict.fromkeys(content))

    return content


def merge_category_text(record, categories_of_concepts):
    merged_test = ""

    for category in categories_of_concepts:
        category_text = record.find(category)
        if category_text is None:
            continue
        else:
            text = category_text.text
            if text:
                merged_test = merged_test + " " + text

    return merged_test


def preprocess_text(text_frag):
    stripped = re.sub('[^\w\s]', '', text_frag)
    stripped = re.sub('_', '', stripped)
    stripped = re.sub('\s+', ' ', stripped)

    raw_text = stripped.lower().split()
    filt_text = []

    for word in raw_text:
        if word not in stop_words:
            filt_text.append(word)

    return filt_text


# pre-processing and tokenization
def make_bags_of_words(text_frag):

    stripped = re.sub('[^\w\s]', '', text_frag)
    stripped = re.sub('_', '', stripped)
    stripped = re.sub('\s+', ' ', stripped)

    raw_text = stripped.lower().split()
    text = ""

    for word in raw_text:
        if word not in stop_words:
            text = text + " " + word

    word_set = set(raw_text)
    word_dict = dict.fromkeys(word_set, 0)
    for word in raw_text:
        word_dict[word] += 1

    return word_dict
