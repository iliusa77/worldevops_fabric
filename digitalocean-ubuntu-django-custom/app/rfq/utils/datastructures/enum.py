import re


class EnumMetaclass(type):

    """Metaclass for nicer 'enum' types. It provides the subclasses of Enum with
    a set of pre-generated 'pretified' constants and methods to access them.
    """
    #
    # Utility functions
    #

    @classmethod
    def slugify(cls, value):
        """Simplified version of Django's slugify filter. It doesn't require
        complicated unicode checks or HTML safety.
        """
        value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
        return re.sub('[-\s]+', '-', value)

    @classmethod
    def human_friendly(cls, value):
        """Create a nicely capitalized version of the constant's name"""
        parts = value.split('_')
        return ' '.join([p.capitalize() if len(p) > 1 else p for p in parts])

    @classmethod
    def camel_case(cls, value):
        """Creates a camelCase version of the constant's name"""
        parts = value.split('_')

        result = ''
        for i in range(0, len(parts)):
            part = parts[i]
            result += part.capitalize() if i else part.lower()

        return result

    @classmethod
    def should_exclude(cls, name, value):
        """Defines if the attribute should be excluded from the Enum"""
        result = name.startswith("_")
        result |= callable(value)
        result |= isinstance(value, classmethod)
        result |= isinstance(value, property)

        return result

    #
    # Metaclass magic
    #
    def __new__(meta, name, bases, attrs):
        "Create string versions of the constant names and stores them for later use"
        user_friendly = []
        camel_cased = []
        slugs = []
        values = []

        sorted_attrs = sorted(attrs.items(), lambda x, y: cmp(x[1], y[1]))

        for key, value in sorted_attrs:
            # Ignore hidden attributes
            if not meta.should_exclude(key, value):
                user_friendly.append(meta.human_friendly(key))
                slugs.append(meta.slugify(key))
                camel_cased.append(meta.camel_case(key))
                values.append(value)

        # Append the new attributes
        attrs['_user_friendly'] = user_friendly
        attrs['_slugs'] = slugs
        attrs['_values'] = values
        attrs['_camel_cased'] = camel_cased

        return type.__new__(meta, name, bases, attrs)


class Enum(object):
    __metaclass__ = EnumMetaclass

    @classmethod
    def as_user_friendly(cls):
        return zip(cls._values, cls._user_friendly)

    @classmethod
    def as_slugs(cls):
        return zip(cls._values, cls._slugs)

    @classmethod
    def as_user_friendly_slugs(cls):
        return zip(cls._slugs, cls._user_friendly)

    @classmethod
    def as_values(cls):
        return cls._values

    #
    # Deserialization
    #
    @classmethod
    def from_slug(cls, slug):
        """Returns the value associated with this slug"""
        if not slug in cls._slugs:
            raise KeyError
        else:
            return cls._values[cls._slugs.index(slug)]

    @classmethod
    def to_slug(cls, value):
        """Returns the slug corresponding to a value"""
        if not value in cls._values:
            raise KeyError
        else:
            return cls._slugs[cls._values.index(value)]

    @classmethod
    def to_camel_case(cls, value):
        """Returns the camelCased constant name for this value"""
        if not value in cls._values:
            raise KeyError
        else:
            return cls._camel_cased[cls._values.index(value)]
