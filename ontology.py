from owlready2 import *
import types
import settings

if settings.load_existing_ontology:
    onto = get_ontology("chemical_accident_ontology.owl").load()
else:
    onto = get_ontology("http://test.org/chemical_accident_ontology.owl")

with onto:

    class Accident(Thing):
        pass

    class has_date(Accident >> str):
        pass

    # === Forward declaration
    class HazardousEvent(Thing):
        pass

    class results_in_hazardous_event(Accident >> HazardousEvent):
        pass

    # === Substance
    class Substance(Thing):
        pass

    class cas_number(Substance >> str):
        pass

    class substance_description(Accident >> str):
        pass

    class location_description(Accident >> str):
        pass

    class he_description(Accident >> str):
        pass

    class cause_description(Accident >> str):
        pass

    class consequence_description(Accident >> str):
        pass

    class HazardousAttribute(Thing):
        pass

    class involves_substance(Accident >> Substance):
        pass

    class is_involved_in_accident(Substance >> Accident):
        inverse_property = involves_substance

    class hazardous_event_involves_substance(HazardousEvent >> Substance):
        pass

    class is_involved_in_hazardous_event(Substance >> HazardousEvent):
        inverse_property = hazardous_event_involves_substance

    class is_hazardous_attr_of(HazardousAttribute >> Substance):
        pass

    class has_hazardous_attribute(Substance >> HazardousAttribute):
        inverse_property = is_hazardous_attr_of

    # === Consequence
    class Consequence(Thing):
        pass

    # === Location
    class Location(Thing):
        pass

    class accident_takes_place_in(Accident >> Location):
        pass

    class is_location_of_accident(Location >> Accident):
        inverse_property = accident_takes_place_in

    # ===Hazardous event
    class involves_substance_attribute(HazardousEvent >> HazardousAttribute):
        pass

    class results_in_hazardous_event(Accident >> HazardousEvent):
        pass

    class hazardous_event_takes_place_in(HazardousEvent >> Location):
        pass

    class is_location_of_hazardous_event(Location >> HazardousEvent):
        inverse_property = hazardous_event_takes_place_in

    # ===Cause
    class Cause(Thing):
        pass

    class has_cause(Accident >> Cause):
        pass

    class hazardous_event_has_cause(HazardousEvent >> Cause):
        pass

    class is_cause_of_hazardous_event(Cause >> HazardousEvent):
        inverse_property = hazardous_event_has_cause

    class cause_involves_location(Cause >> Location):
        pass

    class location_is_involved_in_cause(Location >> Cause):
        inverse_property = cause_involves_location

    class cause_involves_substance(Cause >> Substance):
        pass

    class substance_is_involved_in_cause(Substance >> Cause):
        inverse_property = cause_involves_substance

    class is_cause_of(Cause >> Accident):
        inverse_property = has_cause

    class is_consequence_of_hazardous_event(Consequence >> HazardousEvent):
        pass

    class hazardous_event_has_consequence(HazardousEvent >> Consequence):
        inverse_property = is_consequence_of_hazardous_event

    class consequence_involves_location(Consequence >> Location):
        pass

    class location_is_involved_in_consequence(Location >> Consequence):
        inverse_property = consequence_involves_location

    class consequence_involves_substance(Consequence >> Substance):
        pass

    class substance_is_involved_in_consequence(Substance >> Consequence):
        inverse_property = consequence_involves_substance

    class has_consequence(Accident >> Consequence):
        pass

    def predefine_core_concepts():
        # == Substance
        types.new_class("Substance", (Thing,), )
        onto["Substance"].is_a.extend([onto.is_involved_in_hazardous_event.some(onto["HazardousEvent"]),
                                       onto.substance_is_involved_in_cause.some(onto["Cause"]),
                                       onto.substance_is_involved_in_consequence.some(onto["Consequence"]),
                                       onto.is_involved_in_accident.some(onto["Accident"]),
                                       onto.has_hazardous_attribute.some(onto["HazardousAttribute"])])

        types.new_class("HazardousAttribute", (Thing,),)
        onto["HazardousAttribute"].is_a.append(is_hazardous_attr_of.some(onto["Substance"]))

        # == Location
        types.new_class("Location", (Thing,), )
        onto["Location"].is_a.extend([onto.location_is_involved_in_consequence.some(onto["Consequence"]),
                                      onto.location_is_involved_in_cause.some(onto["Cause"]),
                                      onto.is_location_of_hazardous_event.some(onto["HazardousEvent"]),
                                      onto.is_location_of_accident.some(onto["Accident"])])

        # == Consequence
        types.new_class("Consequence", (Thing,), )
        onto["Consequence"].is_a.extend([onto.consequence_involves_location.some(onto["Location"]),
                                         onto.is_consequence_of_hazardous_event.some(onto["HazardousEvent"]),
                                         onto.consequence_involves_substance.some(onto["Substance"])])

        # == Cause
        types.new_class("Cause", (Thing,), )
        onto["Cause"].is_a.extend([onto.cause_involves_location.some(onto["Location"]),
                                   onto.is_cause_of_hazardous_event.some(onto["HazardousEvent"]),
                                   onto.cause_involves_substance.some(onto["Substance"]),
                                   onto.is_cause_of.some(onto["Accident"])])

        # == Hazardous event
        types.new_class("HazardousEvent", (Thing,), )
        onto["HazardousEvent"].is_a.extend([onto.hazardous_event_involves_substance.some(onto["Substance"]),
                                            onto.hazardous_event_takes_place_in.some(onto["Location"]),
                                            onto.hazardous_event_has_cause.some(onto["Cause"]),
                                            onto.hazardous_event_has_consequence.some(onto["Consequence"]),
                                            onto.involves_substance_attribute.some(onto["HazardousAttribute"])])

        # == Accident
        types.new_class("Accident", (Thing,), )
        onto["Accident"].is_a.extend([onto.involves_substance.some(onto["Substance"]),
                                      onto.accident_takes_place_in.some(onto["Location"]),
                                      onto.has_consequence.some(onto["Consequence"]),
                                      onto.has_cause.some(onto["Cause"]),
                                      onto.results_in_hazardous_event.some(onto["HazardousEvent"])])

    def set_disjoint(disjoint_list):
        onto_list = []
        for elem in disjoint_list:
            onto_list.append(onto[elem])
        onto_list = list(filter(None, onto_list))
        AllDisjoint(onto_list)

    def create_location_individual(location):
        found = onto.search(iri="*" + location + "*", _case_sensitive=False)
        if not found:  # Make sure only new locations are added
            Location(location, namespace=onto)

    def create_hazardous_attribute(hazardous_attribute):
        onto["HazardousAttribute"](hazardous_attribute, namespace=onto)

    def create_hazardous_event_individual(he):
        found = onto.search(iri="*" + he + "*", _case_sensitive=False)
        if not found:
            HazardousEvent(he, namespace=onto)

    def create_substance_individual(substance):
        new_subst = Substance(substance["name"], namespace=onto)

        # Create hazardous attributes instances
        for attr in substance["haz_attr"]:
            create_hazardous_attribute(attr)

        # Add restriction regarding hazardous attributes to substance
        if len(substance["haz_attr"]) > 0:
            new_restriction = And(onto.has_hazardous_attribute.value(onto[i]) for i in substance["haz_attr"])
            new_subst.is_a.append(new_restriction)

        if substance["cas"]:
            new_restriction = onto.cas_number.value(substance["cas"])
            new_subst.is_a.append(new_restriction)

    def create_cause_individual(cause, location, substance, hazardous_event):
        if location and substance["name"] and hazardous_event:
            new_restriction = (onto.cause_involves_location.value(onto[location]) & \
                               onto.is_cause_of_hazardous_event.value(onto[hazardous_event]) & \
                               onto.cause_involves_substance.value(onto[substance["name"]]))

            cause_individual = onto[cause]
            if not cause_individual:
                new_cause = Cause(cause, namespace=onto)
                if new_restriction not in new_cause.is_a:
                    new_cause.is_a.append(new_restriction)
            else:
                if new_restriction not in cause_individual.is_a:
                    cause_individual.is_a.append(new_restriction)

    def create_consequence_individual(consequence, location, substance, hazardous_event):
        new_restriction = (onto.consequence_involves_location.value(onto[location]) & \
                           onto.is_consequence_of_hazardous_event.value(onto[hazardous_event]) & \
                           onto.consequence_involves_substance.value(onto[substance["name"]]))

        if not onto[consequence]:
            new_consequence = Consequence(consequence, namespace=onto)
            if new_restriction not in new_consequence.is_a:
                new_consequence.is_a.append(new_restriction)
        else:
            if new_restriction not in onto[consequence].is_a:
                onto[consequence].is_a.append(new_restriction)

    def create_he_individual(he, substance, location):
        if substance and location:
            new_restriction = onto.hazardous_event_involves_substance.value(onto[substance]) & \
                                  onto.hazardous_event_takes_place_in.value(onto[location])

            if not onto[he]:
                new_he = HazardousEvent(he, namespace=onto)
                if new_restriction not in new_he.is_a:
                    new_he.is_a.append(new_restriction)
            else:
                if new_restriction not in onto[he].is_a:
                    onto[he].is_a.append(new_restriction)

    def create_accident_individual(description, date,
                                   involved_substances,
                                   hazardous_events,
                                   consequences,
                                   causes,
                                   locations,
                                   substance_description,
                                   location_description,
                                   he_description,
                                   cause_description,
                                   consequence_description):
        accident = Accident(description, namespace=onto)
        accident.is_a.append(onto.has_date.value(date))

        for cause_ in causes:
            accident.is_a.append(onto.has_cause.value(onto[cause_]))
        for substance_ in involved_substances:
            accident.is_a.append(onto.involves_substance.value(onto[substance_["name"]]))
        for location_ in locations:
            accident.is_a.append(onto.accident_takes_place_in.value(onto[location_]))
        for consequence_ in consequences:
            accident.is_a.append(onto.has_consequence.value(onto[consequence_]))
        for he_ in hazardous_events:
            accident.is_a.append(onto.results_in_hazardous_event.value(onto[he_]))

        accident.substance_description.append(substance_description)
        accident.location_description.append(location_description)
        accident.he_description.append(he_description)
        accident.cause_description.append(cause_description)
        accident.consequence_description.append(consequence_description)

    def save_ontology(ontology_name):
        onto.save(file=ontology_name, format="rdfxml")

