from flask import Flask, render_template, request, session, jsonify

from my_forms import ProjectionForm
from pyclasses.predicate import Predicate

app = Flask(__name__)

from flaskext.mysql import MySQL 

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

@app.route('/relation_attributes/<name>', methods=['POST', 'GET'])
def json_attributes(name):
    attrs = relation_attributes(name)
    return jsonify(attrs)

@app.route('/', methods=['GET', 'POST'])
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

@app.route('/horizontal', methods=['GET', 'POST'])
def horizontal():
    global predicates, relation_attr, selected_relation, minterm_predicates

    if request.method == 'POST':
        if 'id-load-relation' in request.form:
            selected_relation = request.form.get('sel-relation', relations[0][0]) # second argument as default, from the first relation, get the name
            cursor.execute( "DESC {}".format(selected_relation) )
            relation_attr = cursor.fetchall()
        if 'id-add-predicate' in request.form: # determines which form was submitted
            attribute = request.form.get('sel-attribute')           
            operator = request.form.get('sel-operator')
            value = request.form.get('txt-value')
            predicates.append( Predicate(attribute, operator, value) )
        if "id-build-minterms" in request.form:
            minterm_predicates = Predicate.minterms(predicates)

    return render_template( 'horizontal.html', relations=relations, relation_attr=relation_attr, 
            selected_relation=selected_relation, minterm_predicates=minterm_predicates,
            predicates=tuple( ( i, str(p) ) for i, p in tuple(enumerate(predicates)) ) )

if __name__ == "__main__":
    app.run(debug=True)