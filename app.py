
from flask import Flask, render_template, request, jsonify
from flaskext.mysql import MySQL 

from my_forms import ProjectionForm
from pyclasses.predicate import Predicate
from db import DbHelper

import itertools
import json
import fragmentation_tools as frag

app = Flask(__name__)
app.config.from_pyfile('config.py')

mysql = MySQL()
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

db = DbHelper(conn, cursor)

DBNAME = 'see'

cursor.execute('SHOW TABLES')
relations = cursor.fetchall() # tuple of tuples
selected_relation = relations[0][0]
relation_attr = db.get_attributes(selected_relation)


@app.route('/build_minterms/<relationandpredicates>', methods=['POST', 'GET'])
def build_minterms(relationandpredicates):
    obj = json.loads(relationandpredicates) 
    relation = obj['relation']
    predicates = [ Predicate(p['attribute'], p['operator'], p['value']) for p in obj['predicates'] ]
    minterm_predicates = frag.get_complete_minterm_predicates(db, predicates, relation) 
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
    if frag.is_minimal(db, predicate, relation):
        response['ok'] = True
    else: 
        response['ok'] = False
    return jsonify(response) 

@app.route('/send_site/<dbinfo>', methods=['POST', 'GET'])
def send_site(dbinfo):  
    req = json.loads(dbinfo) # dict('minterms': list(str), 'relation': str)    
    for i, m in enumerate(req['minterms']):
        db.create_fragment_minterm(DBNAME, m, req['relation'], f'{DBNAME}_s{i}')
    return jsonify({ 'ok': True })

@app.route('/', methods=['GET', 'POST'])
def horizontal():
    return render_template( 
            'horizontal.html', 
            relations=relations, 
            relation_attr=relation_attr, 
            selected_relation=selected_relation
    )

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