from flask import Flask, render_template_string, request, redirect, session

app = Flask(__name__)
app.secret_key = "secret123"

# 🔹 Temporary storage
products = []
cart = []

# 🔹 Dummy login credentials
USERNAME = "admin"
PASSWORD = "1234"

# 🔹 LOGIN PAGE
login_html = """
<h2>🔐 Login</h2>
<form method="POST">
    <input type="text" name="username" placeholder="Username" required><br><br>
    <input type="password" name="password" placeholder="Password" required><br><br>
    <button type="submit">Login</button>
</form>
<p style="color:red;">{{error}}</p>
"""

# 🔹 DASHBOARD
dashboard_html = """
<h1>🛒 Grocery Management System</h1>
<a href="/logout">Logout</a>

<h2>Add Product</h2>
<form method="POST" action="/add_product">
    <input type="text" name="name" placeholder="Product Name" required><br><br>
    <input type="number" name="price" placeholder="Price" required><br><br>
    <button type="submit">Add</button>
</form>

<h2>Products</h2>
{% for p in products %}
<p>{{p.name}} - ₹{{p.price}}
<a href="/add_to_cart/{{loop.index0}}">Add to Cart</a></p>
{% endfor %}

<h2>🧾 Cart</h2>
{% for c in cart %}
<p>{{c.name}} - ₹{{c.price}}</p>
{% endfor %}

<h3>Total: ₹{{total}}</h3>

<form method="POST" action="/checkout">
    <button type="submit">Generate Bill</button>
</form>
"""

# 🔹 BILL PAGE
bill_html = """
<h1>🧾 Final Bill</h1>

{% for c in cart %}
<p>{{c.name}} - ₹{{c.price}}</p>
{% endfor %}

<h2>Total Amount: ₹{{total}}</h2>

<a href="/dashboard">Back</a>
"""

# 🔐 LOGIN ROUTE
@app.route('/', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['user'] = request.form['username']
            return redirect('/dashboard')
        else:
            error = "Invalid Credentials"
    return render_template_string(login_html, error=error)

# 🔹 DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    total = sum(int(c['price']) for c in cart)
    return render_template_string(dashboard_html, products=products, cart=cart, total=total)

# 🔹 ADD PRODUCT
@app.route('/add_product', methods=['POST'])
def add_product():
    products.append({
        "name": request.form['name'],
        "price": request.form['price']
    })
    return redirect('/dashboard')

# 🔹 ADD TO CART
@app.route('/add_to_cart/<int:index>')
def add_to_cart(index):
    cart.append(products[index])
    return redirect('/dashboard')

# 🔹 CHECKOUT
@app.route('/checkout', methods=['POST'])
def checkout():
    total = sum(int(c['price']) for c in cart)
    return render_template_string(bill_html, cart=cart, total=total)

# 🔹 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run()