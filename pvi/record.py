class Record(object):

    """Abstract base class for all Records, so it's not advised to
    create instances of this Record class, only of its subclasses
    """

    def __init__(self, suffix, fields, infos):
        self.suffix = suffix
        self.fields = fields
        self.infos = infos

    @property
    def rtyp(self):
        raise NotImplementedError(self)


class AIRecord(Record):

    def __init__(self, suffix, fields, infos):
        super(AIRecord, self).__init__(suffix, fields, infos)

    @property
    def rtyp(self):
        return "ai"


class AORecord(Record):

    def __init__(self, suffix, fields, infos):
        super(AORecord, self).__init__(suffix, fields, infos)

    @property
    def rtyp(self):
        return "ao"
