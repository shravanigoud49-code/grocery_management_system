from flask import Flask, render_template_string, request, redirect, session, send_file
import sqlite3
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("grocery.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER, qty INTEGER)")
    db.execute("CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY, name TEXT, qty INTEGER, total INTEGER)")
    db.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT, phone TEXT)")
    db.commit()

init_db()

# default admin
db = get_db()
user = db.execute("SELECT * FROM users WHERE username='admin'").fetchone()
if not user:
    db.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)", ("admin","1234","admin"))
    db.commit()

# ---------------- CUSTOMER TEMP STORAGE ----------------
customer = {}

# ---------------- UI ----------------
dashboard_html = """
<!DOCTYPE html>
<html>
<head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body { background-color:#121212; color:white; }
.card { border-radius:15px; }
</style>
</head>

<body>

<nav class="navbar navbar-dark bg-dark">
<div class="container-fluid">
<span class="navbar-brand">🛒 Grocery System</span>
<a href="/logout" class="btn btn-danger">Logout</a>
</div>
</nav>

<div class="container mt-4">

{% if role=='admin' %}
<a href="/admin" class="btn btn-warning">Admin</a>
<a href="/graph" class="btn btn-info">Graph</a>
{% endif %}

<div class="row mt-3">

<div class="col-md-4">
<div class="card bg-secondary p-3">
<h5>Add Product</h5>
<form method="POST" action="/add">
<input class="form-control mb-2" name="name" placeholder="Name" required>
<input class="form-control mb-2" name="price" placeholder="Price" required>
<input class="form-control mb-2" name="qty" placeholder="Stock" required>
<button class="btn btn-success w-100">Add</button>
</form>
</div>

<div class="card bg-secondary mt-3 p-3">
<h5>Customer</h5>
<form method="POST" action="/set_customer">
<input class="form-control mb-2" name="cust_name" placeholder="Customer Name" required>
<input class="form-control mb-2" name="cust_phone" placeholder="Phone" required>
<button class="btn btn-info w-100">Save</button>
</form>
</div>
</div>

<div class="col-md-8">
<div class="card bg-secondary p-3">
<h5>Products</h5>
<table class="table table-dark">
<tr><th>Name</th><th>Price</th><th>Stock</th><th>Action</th></tr>
{% for p in products %}
<tr>
<td>{{p.name}}</td>
<td>{{p.price}}</td>
<td>{{p.qty}}</td>
<td><a href="/cart/{{p.id}}" class="btn btn-primary btn-sm">Add</a></td>
</tr>
{% endfor %}
</table>
</div>
</div>

</div>

<div class="card bg-secondary mt-4 p-3">
<h5>Cart</h5>
{% for c in cart %}
<p>{{c.name}} x {{c.qty}}</p>
{% endfor %}
<h4>Total: {{total}}</h4>

<form method="POST" action="/checkout">
<button class="btn btn-success w-100">Generate Bill</button>
</form>
</div>

</div>
</body>
</html>
"""

login_html = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<body class="bg-dark text-white d-flex justify-content-center align-items-center vh-100">
<div class="card p-4 bg-secondary">
<h3>Login</h3>
<form method="POST">
<input class="form-control mb-2" name="username">
<input class="form-control mb-2" type="password" name="password">
<button class="btn btn-light w-100">Login</button>
</form>
<p>{{error}}</p>
</div>
</body>
"""

admin_html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

<style>
body { background-color:#121212; color:white; }
.card { border-radius:15px; }
</style>
</head>

<body>

<nav class="navbar navbar-dark bg-dark shadow">
<div class="container-fluid">
<span class="navbar-brand">⚙ Admin Panel</span>
<a href="/dashboard" class="btn btn-secondary">⬅ Back</a>
</div>
</nav>

<div class="container mt-4">

<div class="card bg-secondary p-3 shadow">
<h4>📦 Manage Products</h4>

<table class="table table-dark table-hover mt-3">
<tr>
<th>Name</th>
<th>Price</th>
<th>Stock</th>
<th>Action</th>
</tr>

{% for p in products %}
<tr>
<td>{{p.name}}</td>
<td>₹{{p.price}}</td>
<td>{{p.qty}}</td>
<td>
<a href="/delete/{{p.id}}" class="btn btn-danger btn-sm">Delete</a>
</td>
</tr>
{% endfor %}

</table>

</div>

</div>

</body>
</html>
"""

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET","POST"])
def login():
    error=""
    if request.method=="POST":
        db=get_db()
        user=db.execute("SELECT * FROM users WHERE username=? AND password=?",
                        (request.form['username'],request.form['password'])).fetchone()
        if user:
            session['user']=user['username']
            session['role']=user['role']
            return redirect("/dashboard")
        else:
            error="Invalid"
    return render_template_string(login_html,error=error)

# ---------------- DASHBOARD ----------------
cart=[]

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    db=get_db()
    products=db.execute("SELECT * FROM products").fetchall()
    total=sum(c['price']*c['qty'] for c in cart)
    return render_template_string(dashboard_html,products=products,cart=cart,total=total,role=session.get("role"))

# ---------------- CUSTOMER ----------------
@app.route("/set_customer", methods=["POST"])
def set_customer():
    global customer
    customer = {
        "name": request.form['cust_name'],
        "phone": request.form['cust_phone']
    }
    return redirect("/dashboard")

# ---------------- ADD PRODUCT ----------------
@app.route("/add",methods=["POST"])
def add():
    db=get_db()
    db.execute("INSERT INTO products (name,price,qty) VALUES (?,?,?)",
               (request.form['name'],request.form['price'],request.form['qty']))
    db.commit()
    return redirect("/dashboard")

# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete(id):
    db=get_db()
    db.execute("DELETE FROM products WHERE id=?",(id,))
    db.commit()
    return redirect("/admin")

# ---------------- CART ----------------
@app.route("/cart/<int:id>")
def add_cart(id):
    db=get_db()
    p=db.execute("SELECT * FROM products WHERE id=?",(id,)).fetchone()

    if p['qty'] <= 0:
        return "Out of stock"

    db.execute("UPDATE products SET qty=qty-1 WHERE id=?",(id,))
    db.commit()

    cart.append({"name":p['name'],"price":p['price'],"qty":1})
    return redirect("/dashboard")

# ---------------- CHECKOUT ----------------
@app.route("/checkout",methods=["POST"])
def checkout():
    db=get_db()
    total=0

    doc=SimpleDocTemplate("bill.pdf")
    styles=getSampleStyleSheet()
    content=[]

    content.append(Paragraph("Grocery Bill", styles['Title']))
    content.append(Paragraph(str(datetime.now()), styles['Normal']))

    content.append(Paragraph(f"Customer: {customer.get('name','')}", styles['Normal']))
    content.append(Paragraph(f"Phone: {customer.get('phone','')}", styles['Normal']))

    content.append(Paragraph("---------------------", styles['Normal']))

    for c in cart:
        item_total=c['price']*c['qty']
        total+=item_total

        db.execute("INSERT INTO sales (name,qty,total) VALUES (?,?,?)",
                   (c['name'],c['qty'],item_total))

        content.append(Paragraph(f"{c['name']} x {c['qty']} = ₹{item_total}", styles['Normal']))

    db.commit()

    content.append(Paragraph("---------------------", styles['Normal']))
    content.append(Paragraph(f"Total: ₹{total}", styles['Heading2']))

    doc.build(content)

    cart.clear()
    customer.clear()

    return send_file("bill.pdf",as_attachment=True)

# ---------------- GRAPH ----------------
@app.route("/graph")
def graph():
    db=get_db()
    data=db.execute("SELECT name,SUM(total) as total FROM sales GROUP BY name").fetchall()

    names=[d['name'] for d in data]
    totals=[d['total'] for d in data]

    plt.figure()
    plt.bar(names,totals)
    plt.savefig("graph.png")

    return send_file("graph.png")

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    db=get_db()
    products=db.execute("SELECT * FROM products").fetchall()
    return render_template_string(admin_html,products=products)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__=="__main__":
    app.run()