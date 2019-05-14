from flask import Flask, render_template, request, session, jsonify, flash
from flaskext.mysql import MySQL 

from my_forms import ProjectionForm
from pyclasses.predicate import Predicate

import itertools
import json

app = Flask(__name__)
app.config.from_pyfile('config.py')

mysql = MySQL()
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()


# global variables
cursor.execute('SHOW TABLES')
relations = cursor.fetchall()  # relations = cursor.fetchall() # tuple of tuples

predicates = list() # of (tuple(str, str, str))
selected_relation = relations[0][0]

relation_attr = []
minterm_predicates = []

from db import DbHelper

db = DbHelper(conn, cursor)


def is_complete(predicates, relation_name): 
    resultset = db.select_all(relation_name)
    universe = { t: 0 for t in resultset }
    for predicate in predicates:
        resultset = db.select_all(relation_name, str(predicate))
        for t in resultset: universe[t] += 1
    # for k in universe.keys(): print(k, ' => ', universe[k])
    m = next(iter(universe.values())) # fetch the first value from the dict
    return 0 < m and all(m == value for value in universe.values()) # all have the same probability to be accessed

def is_minimal(predicate, relation_name):
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

def get_complete_minterm_predicates(predicates, selected_relation):
    # if is_complete(predicates, selected_relation): flash("El conjunto de predicados es completo.") 
    minterms = []
    predicates = remove_repeated_negations(predicates)
    for combination in filter(lambda e: len(e) > 0, all_combinations(predicates)): # remove the empty chain for all combination 
        minterms.extend(Predicate.minterms( list(combination) ))
    minterms = [ m for m in minterms if is_minimal(m, selected_relation) ] # remove non relevant minterms 
    combinations = itertools.combinations(minterms, 3) # returns an iterable object, combinations
    result = []
    for combination in combinations:
        if is_complete(combination, selected_relation):
            print(combination)
            result.append(combination)
    return result

@app.route('/build_minterms/<relationandpredicates>', methods=['POST', 'GET'])
def build_minterms(relationandpredicates):
    obj = json.loads(relationandpredicates) 
    relation = obj['relation']
    predicates = [ Predicate(p['attribute'], p['operator'], p['value']) for p in obj['predicates'] ]
    minterm_predicates = get_complete_minterm_predicates(predicates, relation) 
    print(minterm_predicates)
    return jsonify(minterm_predicates)

@app.route('/relation_attributes/<name>', methods=['POST', 'GET'])
def json_attributes(name):
    attrs = db.relation_attributes(name)
    return jsonify(attrs)

@app.route('/append_predicate/<jsobject>', methods=['POST', 'GET'])
def append_predicate(jsobject):
    obj = json.loads(jsobject) 
    relation, attribute = obj['relation'], obj['attribute']
    operator, value     = obj['operator'], obj['value']
    predicate =  Predicate(attribute, operator, value) 
    response = dict()
    if is_minimal(predicate, relation):
        predicates.append(predicate)
        response['ok'] = True
    else: 
        flash("La seleccion sobre el predicado da conjunto vacio, no fue agregado.")
        response['ok'] = False
    return jsonify(response) 

@app.route('/send_site/<minterms>', methods=['POST', 'GET'])
def send_site(minterms):
    print(minterms)
    raise
    req = json.loads(minterms)
    return jsonify(req)

@app.route('/', methods=['GET', 'POST'])
def horizontal():
    global relation_attr, selected_relation, minterm_predicates

    selected_relation = request.form.get('sel-relation', relations[0][0]) # second argument as default, from the first relation, get the name
    cursor.execute( "DESC {}".format(selected_relation) )
    relation_attr = cursor.fetchall()
    
    # testing
    # db.create_fragment_minterm(db.relation_attributes('sala_votacion'), 'see', 'numero < 3', 'sala_votacion', 'see_s1')

    return render_template( 'horizontal.html', relations=relations, relation_attr=relation_attr, 
            selected_relation=selected_relation, minterm_predicates=minterm_predicates,
            predicates=tuple( ( i, str(p) ) for i, p in tuple(enumerate(predicates)) ) )

@app.route('/vertical', methods=['GET', 'POST'])
def vertical():
    projection_form = ProjectionForm()
    projection_form.relation.choices = [ (r[0], r[0]) for r in relations ]
    projection_form.selected_attributes.choices = [ (r[0], r[0]) for r in db.relation_attributes(relations[0][0])]
    
    if projection_form.validate_on_submit():
        relation = projection_form.relation.data
        fragment_count = projection_form.fragment_count.data 
        selected_attributes = projection_form.selected_attributes.data # it returns a list
        print(relation, fragment_count, selected_attributes)
    return render_template('vertical.html', proj_form=projection_form)

if __name__ == "__main__":
    app.run(debug=True)