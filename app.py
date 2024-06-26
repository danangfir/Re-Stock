from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

class Node:
    def __init__(self, sku, name, price, stock):
        self.sku = sku
        self.name = name
        self.price = price
        self.stock = stock
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, sku, name, price, stock):
        if not self.root:
            self.root = Node(sku, name, price, stock)
        else:
            self._insert(self.root, sku, name, price, stock)

    def _insert(self, node, sku, name, price, stock):
        if sku < node.sku:
            if node.left:
                self._insert(node.left, sku, name, price, stock)
            else:
                node.left = Node(sku, name, price, stock)
        elif sku > node.sku:
            if node.right:
                self._insert(node.right, sku, name, price, stock)
            else:
                node.right = Node(sku, name, price, stock)
        else:
            node.stock += stock

    def find(self, sku):
        return self._find(self.root, sku)

    def _find(self, node, sku):
        if not node:
            return None
        if sku == node.sku:
            return node
        elif sku < node.sku:
            return self._find(node.left, sku)
        else:
            return self._find(node.right, sku)
        
    def delete(self, sku):
        self.root = self._delete(self.root, sku)

    def _delete(self, node, sku):
        if not node:
            return None
        if sku < node.sku:
            node.left = self._delete(node.left, sku)
        elif sku > node.sku:
            node.right = self._delete(node.right, sku)
        else:
            if not node.left:
                return node.right
            elif not node.right:
                return node.left
            else:
                successor = self._find_min(node.right)
                node.sku = successor.sku
                node.name = successor.name
                node.price = successor.price
                node.stock = successor.stock
                node.right = self._delete(node.right, successor.sku)
        return node

    def _find_min(self, node):
        while node.left:
            node = node.left
        return node

stock_bst = BST()
transactions = []

class Transaction:
    def __init__(self, customer_name, sku, quantity, subtotal):
        self.customer_name = customer_name
        self.sku = sku
        self.quantity = quantity
        self.subtotal = subtotal

@app.route('/')
def main_menu():
    return render_template('menu.html')

@app.route('/manage_stock', methods=['GET', 'POST'])
def manage_stock():
    if request.method == 'POST':
        sku = request.form['sku']
        name = request.form['name']
        try:
            price = float(request.form['price'])
            stock = int(request.form['stock'])
        except ValueError:
            flash('Harga dan stok harus berupa angka.')
            return redirect(url_for('manage_stock'))
        stock_bst.insert(sku, name, price, stock)
        flash('Data stok barang berhasil ditambahkan.')
        return redirect(url_for('main_menu'))
    return render_template('manage_stock.html')

@app.route('/restock', methods=['GET', 'POST'])
def restock():
    if request.method == 'POST':
        sku = request.form['sku']
        try:
            stock = int(request.form['stock'])
        except ValueError:
            flash('Jumlah stok harus berupa angka.')
            return redirect(url_for('restock'))
        node = stock_bst.find(sku)
        if node:
            node.stock += stock
        else:
            flash('SKU tidak ditemukan. Silakan tambahkan stok terlebih dahulu.')
            return redirect(url_for('restock'))
        flash('Stok barang berhasil diperbarui.')
        return redirect(url_for('main_menu'))
    return render_template('restock.html')

@app.route('/manage_transactions', methods=['GET', 'POST'])
def manage_transactions():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        sku = request.form['sku']
        try:
            quantity = int(request.form['quantity'])
        except ValueError:
            flash('Jumlah beli harus berupa angka.')
            return redirect(url_for('manage_transactions'))
        node = stock_bst.find(sku)
        if node and node.stock >= quantity:
            subtotal = node.price * quantity
            node.stock -= quantity
            transaction = Transaction(customer_name, sku, quantity, subtotal)
            transactions.append(transaction)
            flash('Transaksi berhasil dicatat.')
            return redirect(url_for('main_menu'))
        else:
            flash('Stok tidak mencukupi atau SKU tidak ditemukan.')
            return redirect(url_for('manage_transactions'))
    return render_template('manage_transactions.html')

@app.route('/view_transactions')
def view_transactions():
    return render_template('view_transactions.html', transactions=transactions)

@app.route('/view_transactions_sorted')
def view_transactions_sorted():
    sorted_transactions = sorted(transactions, key=lambda x: x.subtotal, reverse=True)
    return render_template('view_transactions_sorted.html', transactions=sorted_transactions)

@app.route('/view_stock')
def view_stock():
    items = []
    def inorder(node):
        if node:
            inorder(node.left)
            items.append(node)
            inorder(node.right)
    inorder(stock_bst.root)
    return render_template('view_stock.html', items=items)

@app.route('/delete_stock', methods=['GET', 'POST'])
def delete_stock():
    if request.method == 'POST':
        sku = request.form['sku']
        node = stock_bst.find(sku)
        if node:
            stock_bst.delete(sku)
            flash('Stok barang berhasil dihapus.')
        else:
            flash('SKU tidak ditemukan.')
        return redirect(url_for('main_menu'))
    return render_template('delete_stock.html')

@app.route('/exit')
def exit_program_route():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Tidak dapat menutup server')
    func()
    raise SystemExit('Aplikasi telah ditutup')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    try:
        return main_menu()
    except SystemExit as e:
        print(str(e))

def main_menu():
    return render_template('menu.html', exit_program_url=url_for('exit_program_route'))

if __name__ == '__main__':
    app.run(debug=True)
