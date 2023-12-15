import cog

tripleq = '"' + '"' + '"'


def cogclass(name, doc, pairs, indent=""):
    """
    Build a basic class containing only properties and their string values.
    """
    cog.outl(f"{indent}class {name}:")
    cog.outl(f"{indent}    {tripleq}{doc}{tripleq}")
    cog.outl("")
    for prop, key in pairs:
        cog.outl(f'{indent}    {prop} = "{key}"')
    cog.outl("")


def cogtuple(name, thistuple, indent=""):
    """
    Build a tuple containing string values.
    """
    cog.outl(f"{indent}{name} = (")
    for val in thistuple:
        cog.outl(f'{indent}    "{val}",')
    cog.outl(f"{indent})")


def cognamingclass(name, doc, triplets, indent=""):
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
    properties = [triplet[0] for triplet in triplets]
    keys = [triplet[1] for triplet in triplets]
    values = [triplet[2] for triplet in triplets]
    propkeypairs = [(triplet[0], triplet[1]) for triplet in triplets]

    cogclass(name, doc, propkeypairs)
    cogtuple("_properties", properties, indent="    ")
    cog.outl("")
    cogtuple("_keys", keys, indent="    ")
    cog.outl("")
    cogtuple("_values", values, indent="    ")
    cog.outl("")
    cogclass("_friendly_class", "", zip(properties, values), indent="    ")
    cog.outl("")
    cog.outl("    _friendly_tuple = tuple(zip(_keys, _values))")
    cog.outl("")
    cog.outl("    _friendly_dict = dict(_friendly_tuple)")
    cog.outl("")
    cog.outl("")
