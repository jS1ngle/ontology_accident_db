import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk import word_tokenize, pos_tag
import re
import pre_processing
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

sno = nltk.stem.SnowballStemmer('english')
stop_words = set(stopwords.words('english'))
nltk.download('wordnet')

failure_mode_pattern = [(r'(release)$', 'REL'),
                        (r'(explosion)$', 'EXPL'),
                        (r'(deflagration)$', 'DEFL'),
                        (r'(detonation)$', 'DETO'),
                        (r'(reaction)$', 'REAC'),
                        (r'(runaway)$', 'RAWY'),
                        (r'(fire)$', 'FIRE'),
                        (r'(fireball)$', 'FBLL'),
                        (r'(jet)$', 'JET'),
                        (r'(pool)$', 'POOL'),
                        (r'(flash)$', 'FLSH'),
                        (r'(missile)$', 'MISS'),
                        (r'(dust)$', 'DUST'),
                        (r'(smoke)$', 'SMK'),
                        (r'(combustion)$', 'COM'),
                        (r'(vapour)$', 'VAP'),
                        (r'(vapor)$', 'VAP'),
                        (r'(cloud)$', 'CLD'),
                        (r'(bleve)$', 'BLEV'),
                        (r'(debris)$', 'DEB'),
                        (r'(conflagration)$', 'CNFL')]

consequence_pattern = [(r'(injuries)$', 'INS'),
                       (r'(injured)$', 'INS'),
                       (r'(fatalities)$', 'FAT'),
                       (r'(material)$', 'MAT'),
                       (r'(fire)$', 'FIRE'),
                       (r'(structural)$', 'STR'),
                       (r'(structure)$', 'STR'),
                       (r'(deaths)$', 'DED'),
                       (r'(dead)$', 'DED'),
                       (r'(damage)$', 'DMG'),
                       (r'(blast)$', 'BLST'),
                       (r'(wave)$', 'WAVE'),
                       (r'(shock)$', 'SHCK'),
                       (r'(smell)$', 'SML'),
                       (r'(contamination)$', 'CNTM'),
                       (r'(soil)$', 'SOIL'),
                       (r'(collapse)$', 'CLPS'),
                       (r'(destruction)$', 'DEST'),
                       (r'(pollution)$', 'POLL'),
                       (r'(damages)$', 'DMG'),
                       (r'(ecological)$', 'ECO'),
                       (r'(ecologic)$', 'ECO'),
                       (r'(harm)$', 'HARM'),
                       (r'(loss)$', 'LOSS'),
                       (r'(losses)$', 'LOSS'),
                       (r'(establishment)$', 'EST'),
                       (r'(plant)$', 'PLT'),
                       (r'(evacuation)$', 'EVAC'),
                       (r'(production)$', 'PROD'),
                       (r'(explosion)$', 'EXPL'),
                       (r'(crater)$', 'CRAT'),
                       (r'(community)$', 'COM'),
                       (r'(disruption)$', 'DISR'),
                       (r'(water)$', 'WATR'),
                       (r'(odour)$', 'ODOR'),
                       (r'(odor)$', 'ODOR'),
                       (r'(burns)$', 'BURN'),
                       (r'(eye)$', 'EYE'),
                       (r'(skin)$', 'SKIN'),
                       (r'(irritation)$', 'IRRI'),
                       (r'(irritations)$', 'IRRI'),
                       (r'(of)$', 'IN')]


def single_pattern(tagged_sentence, tag1):
    for i in range(len(tagged_sentence)):
        if tagged_sentence[i][1] == tag1:
            tagged_word = tagged_sentence[i][0]
            tag_out = pos_tag(word_tokenize(tagged_word))

            if tag_out[0][1] == 'NNS':
                consequence = pre_processing.snake2camel(lemmatizer.lemmatize(tag_out[0][0]))

            elif tag_out[0][1] == 'JJ':
                st = sno.stem(tag_out[0][0])
                if st[-1] == 'r':
                    st += 'y'
                consequence = pre_processing.snake2camel(st)

            else:
                consequence = pre_processing.snake2camel(tagged_word)

            return consequence

    return ""


def context_unit_pattern(tagged_sentence):
    for i in range(len(tagged_sentence) - 1):
        if tagged_sentence[i + 1][1] == 'UNIT':
            unit = tagged_sentence[i][0] + "_" + tagged_sentence[i + 1][0]
            unit = pre_processing.snake2camel(unit)
            return unit

    return ""


def context_consequence_pattern(tagged_sentence, pos_tagged_sentence):
    for i in range(len(tagged_sentence) - 1):
        con = ""
        if tagged_sentence[i][1] == 'POLL' or tagged_sentence[i][1] == 'DEST':

            if len(pos_tagged_sentence) > i + 1:
                if pos_tagged_sentence[i + 1][1] == 'NN':
                    con = tagged_sentence[i][0] + "_" + tagged_sentence[i + 1][0]

        if tagged_sentence[i][1] == 'CNTM':
            if len(pos_tagged_sentence) > i + 1:
                if pos_tagged_sentence[i - 1][1] == 'NN':
                    con = tagged_sentence[i - 1][0] + "_" + tagged_sentence[i][0]

            con = pre_processing.snake2camel(con)
            return con
    return ""


def pair_pattern(tagged_sentence, tag1, tag2):
    for i in range(len(tagged_sentence) - 1):
        first_tag = tagged_sentence[i][1]
        second_tag = tagged_sentence[i + 1][1]
        if first_tag == tag1 and second_tag == tag2:
            first_word = tagged_sentence[i][0]
            second_word = tagged_sentence[i + 1][0]

            tag_out_first = pos_tag(word_tokenize(first_word))
            tag_out_second = pos_tag(word_tokenize(second_word))

            if tag_out_first[0][1] == 'NNS':
                first_word = pre_processing.snake2camel(lemmatizer.lemmatize(first_word))

            if tag_out_second[0][1] == 'NNS':
                second_word = pre_processing.snake2camel(lemmatizer.lemmatize(second_word))

            # exception
            if first_tag == "LOSS" and second_tag == "IN":
                first_word = "MAT"
                second_word = "LOSS"

            consequence = first_word + "_" + second_word
            consequence = consequence.lower()
            consequence = pre_processing.snake2camel(consequence)
            return consequence

    return ""


def triple_pattern(tagged_sentence, tag1, tag2, tag3):
    for i in range(len(tagged_sentence) - 2):
        if tagged_sentence[i][1] == tag1 and tagged_sentence[i + 1][1] == tag2 and tagged_sentence[i + 2][1] == tag3:
            consequence = tagged_sentence[i][0] + "_" + tagged_sentence[i + 1][0] + "_" + tagged_sentence[i + 2][0]
            consequence = pre_processing.snake2camel(consequence)
            return consequence

    return ""


def search_failure_mode_tags(text_input):
    failures = []
    tagger_failure = nltk.RegexpTagger(failure_mode_pattern)
    # ==remove punctuation
    tokenizer = RegexpTokenizer(r'\w+')
    word_tokens = tokenizer.tokenize(text_input)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    tagged_sentence = tagger_failure.tag(filtered_sentence)

    single_pattern_tags = ["REL", "EXPL", "FIRE", "MISS", "SMK", "COM", "DEB", "CNFL", "DETO", "DEFL", "FBLL", ]
    for tag in single_pattern_tags:
        detected1 = single_pattern(tagged_sentence, tag)
        if detected1 and tag != "COM":
            failures.append(detected1)
        if tag == "COM" and detected1:
            failures.append("Fire")

    double_pattern_tags = [["VAP", "CLD"], ["DUST", "EXPL"], ["JET", "FIRE"], ["FLSH", "FIRE"], ["POOL", "FIRE"]]
    for pair_tag in double_pattern_tags:
        detected2 = pair_pattern(tagged_sentence, pair_tag[0], pair_tag[1])
        if detected2:
            failures.append(detected2)

    triple_pattern_tags = [["VAP", "CLD", "EXPL"], ["RAWY", "REAC", "EXPL"]]
    for triple_tag in triple_pattern_tags:
        detected3 = triple_pattern(tagged_sentence, triple_tag[0], triple_tag[1], triple_tag[2])
        if detected3:
            failures.append(detected3)

    failures = pre_processing.resolve_redundancies(failures)

    return failures


def search_consequence_tags(text_input):
    consequences = []
    tokenizer = RegexpTokenizer(r'\w+')  # ==remove punctuation
    word_tokens = tokenizer.tokenize(text_input)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    tagger_consequence = nltk.RegexpTagger(consequence_pattern)
    tagged_sentence = tagger_consequence.tag(filtered_sentence)
    standard_tagged_sentence = pos_tag(filtered_sentence)

    single_pattern_tags = ["INS", "FAT", "DED", "SML", "CNTM", "POLL", "ODOR", "EVAC", "BURN", "BLST"]
    for tag in single_pattern_tags:
        detected1 = single_pattern(tagged_sentence, tag)
        if detected1:
            consequences.append(detected1)

    double_pattern_tags = [["MAT", "LOSS"], ["MAT", "DMG"], ["STR", "DMG"], ["EST", "LOSS"], ["ECO", "HARM"],
                           ["WATR", "POLL"], ["COM", "DISR"], ["EXPL", "CRAT"], ["PROD", "LOSS"], ["LOSS", "IN"],
                           ["SOIL", "CNTM"], ["FIRE", "DMG"], ["EYE", "IRRI"], ["SKIN", "BURN"], ["LOSS", "PROD"],
                           ["SHCK", "WAVE"]]
    for pair_tag in double_pattern_tags:
        detected2 = pair_pattern(tagged_sentence, pair_tag[0], pair_tag[1])
        if detected2:
            consequences.append(detected2)

    triple_pattern_tags = [["LOSS", "IN", "PROD"]]
    for triple_tag in triple_pattern_tags:
        detected3 = triple_pattern(tagged_sentence, triple_tag[0], triple_tag[1], triple_tag[2])
        if detected3:
            consequences.append(detected3)

    con = context_consequence_pattern(tagged_sentence, standard_tagged_sentence)
    if con:
        consequences.append(con)

    consequences = pre_processing.resolve_redundancies(consequences)

    return consequences


unit_pattern = [(r'(pipe)$', 'PI'),
                (r'(pipework)$', 'PI'),
                (r'(piping)$', 'PI'),
                (r'(pipeline)$', 'PI'),
                (r'(line)$', 'PI'),
                (r'(valve)$', 'VLV'),
                (r'(cock)$', 'CCK'),
                (r'(drain)$', 'DRN'),
                (r'(unit)$', 'UNIT'),
                (r'(pump)$', 'PMP'),
                (r'(storehouse)$', 'STR'),
                (r'(warehouse)$', 'STR'),
                (r'(cracking)$', 'CRK'),
                (r'(cracker)$', 'CRK'),
                (r'(separator)$', 'SEP'),
                (r'(reactor)$', 'REAC'),
                (r'(evaporator)$', 'EVAP'),
                (r'(exchanger)$', 'EX'),
                (r'(crude)$', 'CRUD'),
                (r'(heat)$', 'HEAT'),
                (r'(heating)$', 'HEAT'),
                (r'(distillation)$', 'DIST'),
                (r'(column)$', 'CLM'),
                (r'(compressor)$', 'CMP'),
                (r'(cooling)$', 'COOL'),
                (r'(condenser)$', 'COND'),
                (r'(reboiler)$', 'REB'),
                (r'(system)$', 'SYS'),
                (r'(tank)$', 'VESS'),
                (r'(vessel)$', 'VESS'),
                (r'(container)$', 'VESS'),
                (r'(cooling)$', 'JACKET'),
                (r'(drum)$', 'VESS')
                ]


def identify_units(text_input):
    units = []
    tagger_consequence = nltk.RegexpTagger(unit_pattern)
    # ==remove punctuation
    tokenizer = RegexpTokenizer(r'\w+')
    word_tokens = tokenizer.tokenize(text_input)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]

    tagged_sentence = tagger_consequence.tag(filtered_sentence)

    single_pattern_tags = ["PI", "VLV", "PMP", "CMP", "CRK", "SEP", "REAC", "EVAP", "VESS", "COND", "REB", "STR"]
    for tag in single_pattern_tags:
        detected1 = single_pattern(tagged_sentence, tag)
        if detected1:
            units.append(detected1)

    uni = context_unit_pattern(tagged_sentence)
    if uni:
        units.append(uni)

    double_pattern_tags = [["HEAT", "EX"], ["DIST", "CLM"], ["DRN", "CCK"], ["CRK", "UNIT"], ["HEAT", "SYS"],
                           ["COOL", "SYS"], ["COOL", "JACK"]]
    for pair_tag in double_pattern_tags:
        detected2 = pair_pattern(tagged_sentence, pair_tag[0], pair_tag[1])
        if detected2:
            units.append(detected2)

    triple_pattern_tags = [["CRUD", "DIST", "UNIT"]]
    for triple_tag in triple_pattern_tags:
        detected3 = triple_pattern(tagged_sentence, triple_tag[0], triple_tag[1], triple_tag[2])
        if detected3:
            units.append(detected3)

    units = pre_processing.resolve_redundancies(units)

    return units


cause_pattern = [(r'(maintenance)$', 'MACE'),
                 (r'(works)$', 'WORK'),
                 (r'(human)$', 'HUMN'),
                 (r'(error)$', 'ERR'),
                 (r'(electrostatic)$', 'ELES'),
                 (r'(failure)$', 'FAIL'),
                 (r'(insufficient)$', 'INSF'),
                 (r'(insulation)$', 'ISO'),
                 (r'(isolation)$', 'ISO'),
                 (r'(corrosion)$', 'CORR'),
                 (r'(ignition)$', 'IGNI'),
                 (r'(blockage)$', 'BLOK'),
                 (r'(fissure)$', 'FISS'),
                 (r'(decomposition)$', 'DECM'),
                 (r'(reaction)$', 'REAC'),
                 (r'(leakage)$', 'LEAK'),
                 (r'(leak)$', 'LEAK'),
                 (r'(overfilling)$', 'OFLL'),
                 (r'(runaway)$', 'RAWY'),
                 (r'(polymerization)$', 'POLY'),
                 (r'(exothermic)$', 'EXO'),
                 (r'(vacuum)$', 'VAC'),
                 (r'(rupture)$', 'RUP'),
                 (r'(crack)$', 'CRCK'),
                 (r'(pressure)$', 'PRSS'),
                 (r'(increase)$', 'INCR'),
                 (r'(impurities)$', 'IMPU'),
                 (r'(erosion)$', 'EROS'),
                 (r'(defect)$', 'DEF'),
                 (r'(material)$', 'MAT'),
                 (r'(training)$', 'TRAN'),
                 (r'(signaling)$', 'SIG'),
                 (r'(signal)$', 'SIG'),
                 (r'(handling)$', 'HAND'),
                 (r'(electric)$', 'ELEC'),
                 (r'(spark)$', 'SPRK'),
                 (r'(vibration)$', 'VIB'),
                 (r'(malfunction)$', 'MALF')]


def search_cause_tags(text_input):
    causes = []
    tagger_cause = nltk.RegexpTagger(cause_pattern)
    # ==remove punctuation
    tokenizer = RegexpTokenizer(r'\w+')
    word_tokens = tokenizer.tokenize(text_input)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    tagged_sentence = tagger_cause.tag(filtered_sentence)

    single_pattern_tags = ["CORR", "FISS", "DECM", "LEAK", "IGNI", "RAWY", "POLY", "RUP", "CRCK", "BLOK", "IMPU",
                           "EROS", "MALF", "VIB", "OFLL", "VAC"]
    for tag in single_pattern_tags:
        detected1 = single_pattern(tagged_sentence, tag)
        if detected1:
            causes.append(detected1)

    double_pattern_tags = [["MACE", "WORK"], ["HUMN", "ERR"], ["ELES", "FAIL"], ["INSF", "ISO"], ["HUMN", "FAIL"],
                           ["DECM", "REAC"], ["RAWY", "REAC"], ["EXO", "POLY"], ["PRSS", "INCR"], ["INSF", "TRAN"],
                           ["MAT", "DEF"], ["SIG", "FAIL"], ["HAND", "ERR"], ["ELEC", "SPRK"]]
    for pair_tag in double_pattern_tags:
        detected2 = pair_pattern(tagged_sentence, pair_tag[0], pair_tag[1])
        if detected2:
            causes.append(detected2)

    causes = pre_processing.resolve_redundancies(causes)

    return causes


categories_of_locations = ['InstallationUnitdescription',
                           'ProcessMajorOccurencesEquipmentType',
                           'ProcessInitiatingEventsEquipmentType',
                           'TransferMajorOccurencesEquipmentType',
                           'TransferInitiatingEventsEquipmentType',
                           'TransportMajorOccurencesEquipmentType',
                           'TransportInitiatingEventsEquipmentType',
                           'StorageInitiatingEventsEquipmentType',
                           'StorageMajorOccurencesEquipmentType'
                           'SiteDescription',
                           'SiteDescriptionOther']

categories_of_causes = ['CausesOfAccident',
                        'OrganizationalCausativeFactorType',
                        'PlantEquipmentCausativeFactorType',
                        'HumanCausativeFactorType',
                        'ExternalCauses',
                        'CausesOther']

categories_of_consequences = ['HumanOnSiteQuantity',
                              'HumanOnSiteQuantityEffect',
                              'HumanOffSiteQuantity',
                              'HumanOffSiteQuantityEffect',
                              'EnvironmentalOnSiteQuantity',
                              'EnvironmentalOnSiteQuantityEffect',
                              'EnvironmentalOffSiteQuantity',
                              'EnvironmentalOffSiteQuantityEffect',
                              'CostOnSiteQuantity',
                              'CostOnSiteQuantityEffect',
                              'CostOffSiteQuantity',
                              'CostOffSiteQuantityEffect',
                              'DisruptionOnSiteQuantity',
                              'DisruptionOnSiteQuantityEffect',
                              'DisruptionOnSiteQuantityEffect2',
                              'DisruptionOffSiteQuantityEffect',
                              'Consequences']

categories_of_failure_modes = ['AccidentDescription',
                               'DominoEffects',
                               'NatechEvents',
                               'TransboundaryEffects',
                               'Contractors',
                               'ReleaseMajorOccurences',
                               'ReleaseInitiatingEvents',
                               'FireMajorOccurences',
                               'FireInitiatingEvents',
                               'ExplosionMajorOccurences',
                               'ExplosionInitiatingEvents',
                               'TransportMajorOccurences',
                               'TransportInitiatingEvents',
                               'AccidentDescriptionOther']


def statistical_analysis(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)

    tokenizer = RegexpTokenizer(r'\w+')
    word_tokens = tokenizer.tokenize(text)

    filtered_sentence = [w for w in word_tokens if not w in stop_words]

    fdist = nltk.FreqDist(filtered_sentence)

    for word, frequency in fdist.most_common(50):
        print(u'{};{}'.format(word, frequency))


def identify_unit(record, db_section):
    potential_units = []

    installation_unit_description = record.find(db_section)
    if installation_unit_description is None:
        return potential_units
    else:
        installation_unit_description = installation_unit_description.text

        unit_dict = {}
        if installation_unit_description is None:
            potential_units = []
        else:
            if db_section == 'InstallationUnitdescription':
                unit_dict['category'] = 'Installation'
            elif db_section == ('ProcessMajorOccurencesEquipmentType' or 'ProcessInitiatingEventsEquipmentType'):
                unit_dict['category'] = 'Process'
            elif db_section == ('TransferMajorOccurencesEquipmentType' or 'TransferInitiatingEventsEquipmentType' or
                                'TransportMajorOccurencesEquipmentType' or 'TransportInitiatingEventsEquipmentType'):
                unit_dict['category'] = 'Transportation'
            elif db_section == ('StorageInitiatingEventsEquipmentType' or 'StorageMajorOccurencesEquipmentType'):
                unit_dict['category'] = 'Storage'
            elif db_section == ('SiteDescription' or 'SiteDescriptionOther'):
                unit_dict['category'] = 'Site'

            unit_dict['units'] = identify_units(installation_unit_description.lower())

            if unit_dict['units']:
                potential_units.append(unit_dict)

    return potential_units


def identify_causes(record, db_section):
    causes = []

    cause_description = record.find(db_section)
    if cause_description is None:
        return causes
    else:
        cause_description = cause_description.text

        cause_dict = {}

        if cause_description is None:
            causes = []
        else:
            if db_section == ('CausesOfAccident' or 'CausesOther'):
                cause_dict['category'] = 'General'
            elif db_section == 'OrganizationalCausativeFactorType':
                cause_dict['category'] = 'Organization'
            elif db_section == 'PlantEquipmentCausativeFactorType':
                cause_dict['category'] = 'Equipment'
            elif db_section == 'HumanCausativeFactorType':
                cause_dict['category'] = 'Human'
            elif db_section == 'ExternalCauses':
                cause_dict['category'] = 'External'

            cause_dict['causes'] = search_cause_tags(cause_description.lower())

            if cause_dict['causes']:
                causes.append(cause_dict)

    return causes


def identify_consequences(record, db_section):
    consequences = []

    consequence_description = record.find(db_section)
    if consequence_description is None:
        return consequences
    else:
        cause_description = consequence_description.text

        consequence_dict = {}

        if cause_description is None:
            consequences = []
        else:
            if db_section == ('HumanOnSiteQuantity' or 'HumanOnSiteQuantityEffect' or
                              'HumanOffSiteQuantity' or 'HumanOffSiteQuantityEffect'):
                consequence_dict['category'] = 'Human'
            elif db_section == ('EnvironmentalOnSiteQuantity' or 'EnvironmentalOnSiteQuantityEffect' or
                                'EnvironmentalOffSiteQuantity' or 'EnvironmentalOffSiteQuantityEffect'):
                consequence_dict['category'] = 'Environment'
            elif db_section == ('CostOnSiteQuantity' or 'CostOnSiteQuantityEffect' or
                                'CostOffSiteQuantity' or 'CostOffSiteQuantityEffect'):
                consequence_dict['category'] = 'Cost'
            elif db_section == ('DisruptionOnSiteQuantity' or 'DisruptionOnSiteQuantityEffect' or
                                'DisruptionOnSiteQuantityEffect2' or 'DisruptionOffSiteQuantityEffect'):
                consequence_dict['category'] = 'Disruption'
            elif db_section == 'Consequences':
                consequence_dict['category'] = 'General'

            consequence_dict['consequences'] = search_consequence_tags(cause_description.lower())

            if consequence_dict['consequences']:
                consequences.append(consequence_dict)

    return consequences


def identify_failure_modes(record, db_section):
    failures = []

    failure_description = record.find(db_section)
    if failure_description is None:
        return failures
    else:
        failure_description = failure_description.text

        failure_dict = {}

        if failure_description is None:
            failures = []
        else:
            failure_dict['category'] = 'General'
            failure_dict['failure_mode'] = search_failure_mode_tags(failure_description.lower())

            if failure_dict['failure_mode']:
                failures.append(failure_dict)

    return failures


def get_specific_concepts(accident_record, categories_of_concepts, concept, global_concept_texts):
    potential_concept = []

    for category in categories_of_concepts:

        if concept == "units":
            found_concept = identify_unit(accident_record, category)

        if concept == "causes":
            found_concept = identify_causes(accident_record, category)

        if concept == "consequences":
            found_concept = identify_consequences(accident_record, category)

        if concept == "hazardous_events":
            found_concept = identify_failure_modes(accident_record, category)

        record_node = accident_record.find(category)

        if record_node is not None:
            cat = record_node.text
            if cat is not None:
                global_concept_texts += " " + cat

        potential_concept += found_concept

    global_concept_texts = concept + ": " + global_concept_texts

    return potential_concept, global_concept_texts
