import rdflib
from rdflib.term import Literal
from rdflib.term import URIRef
from itertools import groupby



TYPE_PRED = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
DOMAIN_PRED = URIRef('http://www.w3.org/2000/01/rdf-schema#domain')
RANGE_PRED = URIRef('http://www.w3.org/2000/01/rdf-schema#range')
LABEL_PRED = URIRef('http://www.w3.org/2000/01/rdf-schema#label')
COMMENT_PRRD = URIRef('http://www.w3.org/2000/01/rdf-schema#comment')
DEFINEDBY_PRED = URIRef('http://www.w3.org/2000/01/rdf-schema#isDefinedBy')

SKIPPABLE_PREDS = [DEFINEDBY_PRED]

PROP_TYPE1 = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#Property')
PROP_TYPE2 = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#Property')
CLASS_TYPE = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#Class')


def get_types(g):
    """
    Find all the top-level kinds in a RDF graph.
    """
    types = set()
    for subj, pred, obj in g:
        if pred == TYPE_PRED:
            types.add(obj)
    return sorted(types)


def get_subjects_by_type(g, typeval):
    """
    Find all all subjects of type `typeval`.
    """
    return g.subjects(predicate=TYPE_PRED, object=typeval)


# all_props = 
# # A class --> property mapping (all properties that have domain one of these classes)


def build_class_props_map(g):
    class_props_map = {}

    # build dict with classes and class attrs first...
    all_classes = get_subjects_by_type(g, CLASS_TYPE)
    for aclass in all_classes:
        class_dict = {'properties':{}}
        class_dict['uri'] = aclass
        short_aclass = g.namespace_manager.normalizeUri(aclass)
        class_props_map[short_aclass] = class_dict
        for pred, obj in g.predicate_objects(subject=aclass):
            if pred in SKIPPABLE_PREDS:
                continue
            short_pred = g.namespace_manager.normalizeUri(pred)
            if isinstance(obj, URIRef):
                short_obj = g.namespace_manager.normalizeUri(obj)
                class_dict[short_pred] = short_obj
            elif isinstance(obj, Literal):
                class_dict[short_pred] = obj.value
            else:
                print('found unexpected obj kind', kind(obj))

    # now attach all the properties
    all_props = []
    all_props.extend(g.subjects(predicate=TYPE_PRED, object=PROP_TYPE1))
    all_props.extend(g.subjects(predicate=TYPE_PRED, object=PROP_TYPE2))
    for prop in all_props:
        prop_dict = {}
        for pred, obj in g.predicate_objects(subject=prop):
            if pred in SKIPPABLE_PREDS:
                continue
            if pred == DOMAIN_PRED:
                aclass = obj
                short_aclass = g.namespace_manager.normalizeUri(aclass)
                short_prop = g.namespace_manager.normalizeUri(prop)
                class_props_map[short_aclass]['properties'][short_prop] = prop_dict
            short_pred = g.namespace_manager.normalizeUri(pred)
            if isinstance(obj, URIRef):
                short_obj = g.namespace_manager.normalizeUri(obj)
                prop_dict[short_pred] = short_obj
            elif isinstance(obj, Literal):
                prop_dict[short_pred] = obj.value
            else:
                print('found unexpected obj kind', kind(obj))

    return class_props_map


def print_class_props_map(g, class_props_map):
    for short_aclass, aclass_dict in class_props_map.items():
        print(short_aclass, 'label=', aclass_dict.get('rdfs:label'))
        for short_prop, prop_dict in aclass_dict['properties'].items():
            print(short_prop +'\t' + prop_dict.get('rdfs:range', ''))
        print()
