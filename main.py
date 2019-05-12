from flask import Flask, render_template, request, session, jsonify, flash
from flaskext.mysql import MySQL 

from my_forms import ProjectionForm
from pyclasses.predicate import Predicate

import itertools

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey' # this also enables session

# Mysql config
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'see'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
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


def relation_attributes(relation_name):
    """
    Arguments:
        relation_name {str}
    
    Returns:
        tuple(tuple()) -- returns a tuple of tuples such that every element is (Field, Type, Null, Key, Default, Extra)
    """
    cursor.execute(f'DESC {relation_name}')
    return cursor.fetchall() 

def count_rows(predicate, relation_name):
    query = f"SELECT COUNT(*) FROM {relation_name} WHERE {str(predicate)} "
    try:
        cursor.execute(query)
        result = cursor.fetchall() # tuple of tuples
        return result[0][0]
    except:
        flash("Hay un error sintactico en su predicado ")
        return -1

def fetch_result_set(cursor, relation_name, predicate=False):
    query = f"SELECT * FROM {relation_name} " + (
        f" WHERE {predicate}" if predicate else "" )
    # print(query)
    cursor.execute(query)
    return cursor.fetchall()

def is_complete(predicates, relation_name): 
    resultset = fetch_result_set(cursor, relation_name)
    universe = { t: 0 for t in resultset }
    for predicate in predicates:
        resultset = fetch_result_set(cursor, relation_name, str(predicate))
        for t in resultset: universe[t] += 1
    # for k in universe.keys(): print(k, ' => ', universe[k])
    m = next(iter(universe.values())) # fetch the first value from the dict
    return 0 < m and all(m == value for value in universe.values()) # all have the same probability to be accessed

def is_minimal(predicate, relation_name):
    return count_rows(predicate, relation_name) > 0

@app.route('/relation_attributes/<name>', methods=['POST', 'GET'])
def json_attributes(name):
    attrs = relation_attributes(name)
    return jsonify(attrs)

@app.route('/vertical', methods=['GET', 'POST'])
def vertical():
    projection_form = ProjectionForm()
    projection_form.relation.choices = [ (r[0], r[0]) for r in relations ]
    projection_form.selected_attributes.choices = [ (r[0], r[0]) for r in relation_attributes(relations[0][0])]
    
    if projection_form.validate_on_submit():
        relation = projection_form.relation.data
        fragment_count = projection_form.fragment_count.data 
        selected_attributes = projection_form.selected_attributes.data # it returns a list
        print(relation, fragment_count, selected_attributes)
    return render_template('vertical.html', proj_form=projection_form)

def horizontal_handle_add_predicate(request):
    form = request.form 
    attribute = form.get('sel-attribute')           
    operator = form.get('sel-operator')
    value = form.get('txt-value')
    predicate =  Predicate(attribute, operator, value) 
    if is_minimal(predicate, selected_relation):
        predicates.append(predicate)
    else: 
        flash("La seleccion sobre el predicado da conjunto vacio, no fue agregado.")

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

def horizontal_controller_handle_build_terms(predicates, selected_relation):
    if is_complete(predicates, selected_relation): flash("El conjunto de predicados es completo.") 
    predicates = remove_repeated_negations(predicates)
    minterms = []
    for combination in filter(lambda e: len(e) > 0, all_combinations(predicates)): # remove the empty chain for all combination 
        minterms.extend(Predicate.minterms( list(combination) ))
    minterms = [ m for m in minterms if is_minimal(m, selected_relation) ] # remove non relevant minterms 
    combinations = itertools.combinations(minterms, 3) # returns an iterable object, combinations
    for combination in combinations:
        if is_complete(combination, selected_relation):
            print('DONE', combination)
    # print(minterms)    

@app.route('/', methods=['GET', 'POST'])
def horizontal():
    global relation_attr, selected_relation, minterm_predicates

    if request.method == 'POST':
        if 'id-load-relation' in request.form:
            selected_relation = request.form.get('sel-relation', relations[0][0]) # second argument as default, from the first relation, get the name
            cursor.execute( "DESC {}".format(selected_relation) )
            relation_attr = cursor.fetchall()
        if 'id-add-predicate' in request.form: # determines which form was submitted
            horizontal_handle_add_predicate(request)
        if "id-build-minterms" in request.form:
            # horizontal_controller_handle_build_terms(predicates, selected_relation)
            horizontal_controller_handle_build_terms(
                    [ Predicate('numero', '<', '3'), Predicate('numero', '<', '6'), 
                            Predicate('numero', '>=', '3'), Predicate('numero', '>=', '6') ], 
                    'sala_votacion')
    return render_template( 'horizontal.html', relations=relations, relation_attr=relation_attr, 
            selected_relation=selected_relation, minterm_predicates=minterm_predicates,
            predicates=tuple( ( i, str(p) ) for i, p in tuple(enumerate(predicates)) ) )

if __name__ == "__main__":
    app.run(debug=True)