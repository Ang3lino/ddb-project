class Predicate():
    def __init__(self, attr, op, val):
        self.attr = attr 
        self.op = op 
        self.val = val 

    def __str__(self):
        return ' '.join((self.attr, self.op, self.val))

    def negate(self):
        return '(NOT {})'.format(self.__str__())

    @staticmethod
    def minterms(predicates):
        minterms = []
        pr = ( (str(p), p.negate()) for p in predicates )
        indexes = []
        init_indexes(indexes, [], 0, 1 << len(predicates))

def init_indexes(indexes, seq, i, n):
    if i == n:
        indexes.append(seq)
    else:
        init_indexes(indexes, seq.append(0), i + 1, n)
        init_indexes(indexes, seq.append(1), i + 1, n)