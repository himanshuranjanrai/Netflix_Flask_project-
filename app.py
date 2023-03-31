from flask import Flask , render_template ,request,session, redirect ,url_for ,flash
import sqlite3
import json,requests


app = Flask(__name__)
# Assign secret key
app.secret_key ="mysecretkey"

# Create connection to Sqlite3
db = sqlite3.connect('database.db',check_same_thread=False)
c = db.cursor()

# Create table if not exists   
c.execute('''CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT, 
    Email TEXT)''')
db.commit()

# Define Registration 
@app.route('/', methods=['GET','POST'])
def register():
    msg = ""
    if request.method =='POST':
        username = request.form["username"]
        password = request.form["password"]
        Email = request.form["Email"]
        
        # Check if username already exists in db
        c = db.cursor()
        c.execute("SELECT * FROM users WHERE username=?",(username,))
        user = c.fetchone()
        if user:
            # if username exists show error
            msg="Username already exists"
            return render_template('register.html',msg=msg)
        else:
            # if username doesn't exists , insert data in db
            c = db.cursor()
            c.execute("INSERT INTO users(username,password,Email) VALUES(?, ?, ?)",(username, password, Email))
            db.commit()

            #redirect the user to login page
            return redirect('/login')
    else:
        return render_template('register.html')

# Define login route
@app.route('/login', methods=['GET','POST'])
def login():
    msg = ""
    if request.method =='POST':
        username = request.form["username"]
        password = request.form["password"]

        # check if the username and password match the record in database
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        if user:
            session['username'] = user[0]
            #if username & password matches redirect to main webpage
            return render_template('main.html')
        else:
            msg = "Please enter correct login details"
        return render_template('login.html',msg=msg)
        
    else:
        return render_template('login.html')
    
        
@app.route('/main')
def main():
    # if user is in session
    if 'username' in session:
        c = db.cursor()
        c.execute("SELECT * FROM users WHERE username=?",(session['username'],))
        user = c.fetchone()
        #db.close()
        response =requests.get('https://api.fjodt.com/platforms/?authentication_token=RcMV8MvQVE7UYyemNbTZP7vDpjdC5G',verify=False)
        data = json.loads(response.text)
        print(response)
        return render_template('main.html', data=data,user=user)
    else:
        return redirect('/login')

# Update username
@app.route('/update_username',methods=['GET','POST'])
def update_username():
    if request.method == 'POST':
        new_username = request.form["new_username"]
        db = sqlite3.connect('database.db')
        c = db.cursor()
        c.execute("UPDATE users SET username=? WHERE username=?",(new_username,session['username']))
        db.commit()
        db.close()
        # Now session name also updated
        session['username'] = new_username
        return redirect('/main')
    else:
        return render_template('update_username.html')

# Update Password
@app.route('/update_password',methods=['GET','POST'])
def update_password():
    if request.method == 'POST':
        new_password = request.form["new_password"]
        db = sqlite3.connect('database.db')
        c = db.cursor()
        c.execute("UPDATE users SET password=? WHERE username=?",(new_password,session['username']))
        db.commit()
        db.close()
        # Now session name also updated
        return redirect('/main')
        return flash("Password Updated")
    else:
        return render_template('update_password.html')

# Update Email
@app.route('/update_Email',methods=['GET','POST'])
def update_Email():
    if request.method == 'POST':
        new_Email = request.form["new_Email"]
        db = sqlite3.connect('database.db')
        c = db.cursor()
        c.execute("UPDATE users SET Email=? WHERE username=?",(new_Email,session['username']))
        db.commit()
        db.close()
        # Now session name also updated
        return redirect('/main')
        return flash("Email Updated")
        
    else:
        return render_template('update_Email.html')

# Delete user
@app.route('/delete',methods=['GET','POST'])
def delete():
    if request.method == 'POST':
        db = sqlite3.connect('database.db')
        c = db.cursor()
        c.execute("DELETE FROM users WHERE username=?",(session['username'],))
        db.commit()
        db.close()
        session.pop('username',None)
        return redirect('/login')
    else:
        return render_template('delete.html')



if __name__ == "__main__":
    app.run(debug=True)
        
