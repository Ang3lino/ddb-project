
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



@app.route('/build_minterms/<relationandpredicates>', methods=['POST', 'GET'])
def build_minterms(relationandpredicates):
    obj = json.loads(relationandpredicates)
    relation = obj['relation']
    predicates = [ Predicate(p['attribute'], p['operator'], p['value']) for p in obj['predicates'] ]
    minterm_predicates = frag.get_complete_minterm_predicates(db, predicates, relation)
    # print(minterm_predicates)
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

from datetime import datetime

@app.route('/vertical_send_site/<fraginfo>', methods=['POST', 'GET'])
def vertical_send_site(fraginfo):
    '''
    fraginfo: 
        site: str,
        relation: str,
        attributes: list<list<str>>
    '''
    req = json.loads(fraginfo)
    # def create_vertical_fragment(self, dbsrc, dbtarget, tablename, attributes):
    relation = req['relation']
    relation_attrs = db.relation_attributes(relation)
    print('peticion: ', req)
    print('atributos de relacion: ', relation_attrs)
    for indexes in req['attributes']:
        selected_attrs = tuple(relation_attrs[int(i)] for i in indexes)
        print('atributosSeleccionados', selected_attrs)
        time = str(datetime.now()).split(' ')[1].replace(':', '_').replace('.', '__')
        db.create_vertical_fragment(
                DBNAME, 
                DBNAME + req['site'], 
                f'{relation}_{time}', 
                tuple(selected_attrs) + db.get_primary_keys_from(relation))
    return jsonify({ 'ok': True })

cursor.execute('SHOW TABLES')
relations = cursor.fetchall() # tuple of tuples
selected_relation = relations[0][0]
relation_attr = db.get_attributes(selected_relation)

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
    print(relation_attr)
    return render_template(
            'vertical.html',
            relations=relations,
            relation_attr=relation_attr
    )

if __name__ == "__main__":
    app.run(debug=True)
