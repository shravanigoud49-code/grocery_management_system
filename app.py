from flask import Flask
from flask import Flask, render_template, request, redirect
import mysql.connector

# ✅ FIRST create app
app = Flask(__name__)

# ✅ THEN database
db = mysql.connector.connect(
    host="shinkansen.proxy.rlwy.net",
    user="root",
    password="hifIFrIsbTVkpOtJLgehLKIoROCleMkG",
    database="railway",
    port=14321
)

cursor = db.cursor()

# ✅ THEN routes
@app.route('/')
def home():
    return render_template('index.html')

# ✅ RUN
if __name__ == "__main__":
    app.run(debug=True)
def home():
    return render_template('index.html')

# ------------------ ADD PRODUCT ------------------
@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    price = request.form['price']
    qty = request.form['qty']

    cursor.execute(
        "INSERT INTO products (name, price, quantity) VALUES (%s,%s,%s)",
        (name, price, qty)
    )
    db.commit()

    return redirect('/products')

# ------------------ VIEW PRODUCTS ------------------
@app.route('/products')
def products():
    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()
    return render_template('products.html', products=data)

# ------------------ ADD TO CART ------------------
@app.route('/add_to_cart/<name>')
def add_to_cart(name):
    cursor.execute("SELECT price FROM products WHERE name=%s", (name,))
    result = cursor.fetchone()

    if result:
        price = result[0]
        cart.append((name, price, 1, price))

    return redirect('/cart')

# ------------------ VIEW CART ------------------
@app.route('/cart')
def view_cart():
    total = sum(item[3] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

# ------------------ GENERATE BILL ------------------
@app.route('/bill', methods=['POST'])
def generate_bill():
    phone = request.form['phone']

    for item in cart:
        name, price, qty, total = item

        # update stock
        cursor.execute(
            "UPDATE products SET quantity = quantity - %s WHERE name=%s",
            (qty, name)
        )

        # insert into sales
        cursor.execute(
            "INSERT INTO sales (name, quantity, total) VALUES (%s,%s,%s)",
            (name, qty, total)
        )

        # insert into customers
        cursor.execute(
            "INSERT INTO customers (phone, product, quantity, total) VALUES (%s,%s,%s,%s)",
            (phone, name, qty, total)
        )

    db.commit()
    cart.clear()

    return "✅ Bill Generated Successfully!"

# ------------------ CUSTOMER HISTORY ------------------
@app.route('/customers/<phone>')
def customers(phone):
    cursor.execute(
        "SELECT product, quantity, total FROM customers WHERE phone=%s",
        (phone,)
    )
    data = cursor.fetchall()
    return render_template('customers.html', data=data)

# ------------------ RUN APP ------------------
if __name__ == "__main__":
    app.run(debug=True)