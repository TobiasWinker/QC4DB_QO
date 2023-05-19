class DataFormat():

    # Index of the query in the data table
    query: int
    # Index of the first
    first: int
    # Number of values. Is treated as a maximum. -1 means no limit
    n: int

    def __init__(self, query: int, first: int, n: int):
        self.query = query
        self.first = first
        self.n = n


DEFAULT_FORMAT = DataFormat(0, 1, -1)
