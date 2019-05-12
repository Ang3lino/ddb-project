
class Predicate():
    def __init__(self, attr, op, val):
        self.attr = attr 
        self.op = op 
        self.val = val 

    def __str__(self):
        return ' '.join((self.attr, self.op, self.val))

    def negate(self):
        return '(NOT {})'.format(self.__str__())

    def is_negated(self, other):
        if self.attr == other.attr and self.val == other.val: 
            if self.op == '=': return other.op == '<>'
            if self.op == '<': return other.op == '>='
            if self.op == '>': return other.op == '<='

            if self.op == '<=': return other.op == '>'
            if self.op == '>=': return other.op == '<'
            if self.op == '<>': return other.op == '='
        return False

    @staticmethod
    def minterms(predicates):
        indexes = [] # list of list, where each element from of it is { bb...b (n times) | where b = 0, 1, n = |P| }
        minterms = [] # it'll store the conjunction for all posibilities for each p in predicates
        pr = tuple( (p.negate(), str(p)) for p in predicates )
        init_indexes(indexes, [], 0, len(predicates))
        for seq in indexes:
            minterms.append(' AND '.join(( pr[i][j] for i, j in enumerate(seq) )))
        return minterms

    @staticmethod
    def print_all(predicates):
        for p in predicates: print(str(p))

def init_indexes(indexes, seq, i, n):
    if i == n:
        indexes.append(seq)
    else:
        s, t = seq.copy(), seq.copy() # important to obtain a copy since python parameters are passed by reference
        # print(i, n, seq)
        s.append(0)
        init_indexes(indexes, s, i + 1, n)
        t.append(1)
        init_indexes(indexes, t, i + 1, n)