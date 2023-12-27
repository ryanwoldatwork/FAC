from pathlib import Path
import cog

TRIPLEQ = '"' + '"' + '"'


def to_screaming_snake(text):
    no_hyphens = text.replace("-", "_")
    no_spaces = no_hyphens.replace(" ", "_")
    return no_spaces.upper()


def load_semiconstants_path():
    current = Path(".").absolute()
    while current.name != "semiconstants":
        current = current.parent
    return current


def cogclass(name, doc, pairs, indent=None):
    """
    Build a basic class containing only properties and their string values.
    """
    if indent is None:
        indent = ""
    cog.outl(f"{indent}class {name}:")
    cog.outl(f"{indent}    {TRIPLEQ}{doc}{TRIPLEQ}")
    cog.outl("")
    for prop, key in pairs:
        cog.outl(f'{indent}    {prop} = "{key}"')
    cog.outl("")


def cogtuple(name, thistuple, indent=None):
    """
    Build a tuple containing string values.
    """
    if indent is None:
        indent = ""
    cog.outl(f"{indent}{name} = (")
    for val in thistuple:
        cog.outl(f'{indent}    "{val}",')
    cog.outl(f"{indent})")


def cogi18ntuple(name, thistuple, indent=None):
    """
    Build a tuple containing string values.
    """
    if indent is None:
        indent = ""
    cog.outl(f"{indent}{name} = (")
    for val in thistuple:
        cog.outl(f'{indent}    _("{val}"),')
    cog.outl(f"{indent})")


def cognamingclass(name, doc, triplets, indent=None, i18n=None):
    """
    Build a class that has "constant" class properties, internal representation
    values for those properties, and "friendly" values for those properties.

    The "constant" class properties are direct properties of the constructed class.

    In addition, the class will have these properties, each a tuple containing the
    strings for the properties, keys, and values:

    +   _properties
    +   _keys
    +   _values

    In addition:

    _friendly_class
        A class with the same property names as the containing class but
        with the friendly strings, not the internal representation strings, as the
        values.
    _friendly_tuple
        A tuple containing two-element tuples of the internal representation strings
        and the friendly strings.
    _friendly_dict
        A dict that has the internal representation strings as keys and the friendly
        strings as values.
    """
    if indent is None:
        indent = ""
    properties = [triplet[0] for triplet in triplets]
    keys = [triplet[1] for triplet in triplets]
    values = [triplet[2] for triplet in triplets]
    propkeypairs = [(triplet[0], triplet[1]) for triplet in triplets]

    cogclass(name, doc, propkeypairs, indent=indent)
    cogtuple("_properties", properties, indent="    " + indent)
    cog.outl("")
    cogtuple("_keys", keys, indent="    " + indent)
    cog.outl("")
    if i18n:
        cogi18ntuple("_values", values, indent="    " + indent)
    else:
        cogtuple("_values", values, indent="    " + indent)
    cog.outl("")
    cogclass(
        "_friendly_class",
        f"Friendly names class for {name}",
        zip(properties, values),
        indent="    " + indent,
    )
    cog.outl(indent + "    _friendly_tuple = tuple(zip(_keys, _values))")
    cog.outl("")
    cog.outl(indent + "    _friendly_dict = dict(_friendly_tuple)")
    cog.outl("")
    cog.outl("")
