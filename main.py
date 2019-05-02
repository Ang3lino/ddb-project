from flask import Flask, render_template, request

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

@app.route('/', methods=['GET', 'POST'])
def horizontal():
    cursor.execute("SHOW TABLES")
    relations = cursor.fetchall() # tuple of tuples

    relation_attr = False
    predicate = False

    if request.method == 'POST':
        # if 'id-load-relation' in request.form:
        relation_sel = request.form.get('sel-relation', relations[0][0]) # second argument as default, from the first relation, get the name
        cursor.execute("DESC {}".format(relation_sel))
        relation_attr = cursor.fetchall()
        if 'id-add-predicate' in request.form: # determines which form was submitted
            attribute = request.form.get('sel-attribute')           
            operator = request.form.get('sel-operator')
            value = request.form.get('txt-value')
            predicate = ' '.join((attribute, operator, value)) # second argument must be an iterable object
    return render_template('horizontal.html', relations=relations, relation_attr=relation_attr, 
            predicate=predicate)

if __name__ == "__main__":
    app.run(debug=True)