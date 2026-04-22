from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

# Temporary storage (instead of MySQL)
products = []

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
            <td>{{loop.index}}</td>
            <td>{{p.name}}</td>
            <td>{{p.price}}</td>
            <td>{{p.quantity}}</td>
        </tr>
        {% endfor %}
    </table>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML, products=products)

@app.route('/add', methods=['POST'])
def add():
    product = {
        "name": request.form['name'],
        "price": request.form['price'],
        "quantity": request.form['quantity']
    }
    products.append(product)
    return redirect('/')

if __name__ == '__main__':
    app.run()