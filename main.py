from flask import Flask, render_template, request

app = Flask(__name__)


from flaskext.mysql import MySQL 

app.config['SECRET_KEY'] = 'mysecretkey' # u r suppossed to be the only who knows this

# https://stackoverflow.com/questions/9845102/using-mysql-in-flaromk
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'see'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

# TODO
# https://stackoverflow.com/questions/19794695/flask-python-buttons

@app.route('/', methods=['GET', 'POST'])
def horizontal():
    cursor.execute("SHOW TABLES")
    relations = cursor.fetchall() # tuple of tuples

    relation_sel = request.form.get('sel-relation')
    if relation_sel != None:
        cursor.execute("DESC {}".format(relation_sel))
        relation_attr = cursor.fetchall()
        return render_template('horizontal.html', relations=relations, 
            relation_attr=relation_attr)
    return render_template('horizontal.html', relations=relations, relation_attr=False)

if __name__ == "__main__":
    app.run(debug=True)