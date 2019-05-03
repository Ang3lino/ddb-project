from flask import Flask, render_template, request, session

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

predicates = set() # of (tuple(str, str, str))
selected_relation = relations[0][0]

relation_attr = []
minterm_predicates = []

def __selected_relation():
    pass

negate_predicate = lambda predicate: '(NOT %s)' % predicate
predicate_as_str = lambda p: ' '.join(( p[0], p[1], p[2] ))

@app.route('/', methods=['GET', 'POST'])
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
            predicates.add( (attribute, operator, value) )
        if "id-build-minterms" in request.form:
            minterm_predicates = [ ]
            for p in predicates:
                minterm_predicates.extend(( predicate_as_str(p), negate_predicate(predicate_as_str(p)) ))

    return render_template( 'horizontal.html', relations=relations, relation_attr=relation_attr, 
            selected_relation=selected_relation, minterm_predicates=minterm_predicates,
            predicates=tuple( ( i, predicate_as_str(p) ) for i, p in tuple(enumerate(predicates)) ) )

if __name__ == "__main__":
    app.run(debug=True)