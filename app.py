from flask import Flask, render_template_string, request, redirect
import mysql.connector

app = Flask(__name__)

# 🔹 MySQL Connection (Change credentials if needed)
db = mysql.connector.connect(
    host="localhost",        # change if using online DB
    user="root",
    password="",
    database="grocery_db"
)

cursor = db.cursor()

# 🔹 Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    price FLOAT,
    quantity INT
)
""")
db.commit()

# 🔹 HTML Template (No separate file needed)
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Grocery Management</title>
</head>
<body style="font-family: Arial; background-color: #f2f2f2; text-align:center;">

    <h1>🛒 Grocery Management System</h1>

    <form method="POST" action="/add">
        <input type="text" name="name" placeholder="Product Name" required><br><br>
        <input type="number" name="price" placeholder="Price" required><br><br>
        <input type="number" name="quantity" placeholder="Quantity" required><br><br>
        <button type="submit">Add Product</button>
    </form>

    <h2>📦 Product List</h2>

    <table border="1" style="margin:auto;">
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Price</th>
            <th>Quantity</th>
        </tr>
        {% for p in products %}
        <tr>
            <td>{{p[0]}}</td>
            <td>{{p[1]}}</td>
            <td>{{p[2]}}</td>
            <td>{{p[3]}}</td>
        </tr>
        {% endfor %}
    </table>

</body>
</html>
"""

# 🔹 Home Route (IMPORTANT for deployment)
@app.route('/')
def home():
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return render_template_string(HTML, products=products)

# 🔹 Add Product
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    price = request.form['price']
    quantity = request.form['quantity']

    cursor.execute(
        "INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s)",
        (name, price, quantity)
    )
    db.commit()

    return redirect('/')

# 🔹 Run App
if __name__ == '__main__':
    app.run(debug=True)