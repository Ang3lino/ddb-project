
import itertools

from pyclasses.predicate import Predicate

def is_complete(db, predicates, relation_name): 
    resultset = db.select_all(relation_name)
    universe = { t: 0 for t in resultset }
    for predicate in predicates:
        resultset = db.select_all(relation_name, str(predicate))
        for t in resultset: universe[t] += 1
    # for k in universe.keys(): print(k, ' => ', universe[k])
    m = next(iter(universe.values())) # fetch the first value from the dict
    return 0 < m and all(m == value for value in universe.values()) # all have the same probability to be accessed

def is_minimal(db, predicate, relation_name):
    return db.count_rows(predicate, relation_name) > 0

def all_combinations(ss):
    return itertools.chain(*map(lambda x: itertools.combinations(ss, x), 
            range(0, len(ss) + 1)))

def remove_repeated_negations(predicates):
    repeated = list()
    for i, _ in enumerate(predicates):
        for j in range(i + 1, len(predicates)):
            if predicates[i].is_negated(predicates[j]):
                repeated.append(predicates[j])
    return list( filter(lambda e: not (e in repeated), predicates) )

def remove_all(source, targets):
    return list( filter(lambda e: not (e in targets), source) )

def get_complete_minterm_predicates(db, predicates, selected_relation):
    minterms = []
    predicates = remove_repeated_negations(predicates)
    for combination in filter(lambda e: len(e) > 0, all_combinations(predicates)): # remove the empty chain for all combination 
        minterms.extend(Predicate.minterms( list(combination) ))
    minterms = [ m for m in minterms if is_minimal(db, m, selected_relation) ] # remove non relevant minterms 
    combinations = itertools.combinations(minterms, 3) # returns an iterable object, combinations
    result = []
    for combination in combinations:
        if is_complete(db, combination, selected_relation):
            print(combination)
            result.append(combination)
    return result