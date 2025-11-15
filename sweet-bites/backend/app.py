from flask import Flask, render_template, session, redirect, url_for, request, jsonify
import os
app = Flask(__name__, template_folder="../templates", static_folder="../static", static_url_path="/static")
app.secret_key = os.environ.get("FLASK_SECRET","devsecret")
CAKES = [
    {"id":1,"name":"Strawberry Dream","price":25.99,"image":"static/images/image1.jpg"},
    {"id":2,"name":"Chocolate Heaven","price":29.99,"image":"static/images/image2.jpg"},
    {"id":3,"name":"Vanilla Delight","price":22.99,"image":"static/images/image3.jpg"},
    {"id":4,"name":"Pink Velvet","price":27.99,"image":"static/images/image4.jpg"}
]
def get_cart(): return session.get("cart", {})
def save_cart(cart): session["cart"] = cart
@app.route("/")
def index(): return render_template("index.html", cakes=CAKES, cart_count=sum(get_cart().values()))
@app.route("/add_to_cart/<int:cake_id>", methods=["POST"])
def add_to_cart(cake_id):
    cart = get_cart()
    cake = next((c for c in CAKES if c["id"] == cake_id), None)
    if not cake: return jsonify({"success":False,"message":"not found"}), 404
    key = str(cake_id)
    cart[key] = cart.get(key, 0) + 1
    save_cart(cart)
    return jsonify({"success":True,"cart_count":sum(cart.values())})
@app.route("/cart")
def cart():
    cart = get_cart(); items = []; total = 0
    for cake_id, qty in cart.items():
        cake = next((c for c in CAKES if str(c['id']) == cake_id), None)
        if cake:
            item_total = cake['price'] * qty
            total += item_total
            items.append({"cake": cake, "qty": qty, "item_total": item_total})
    return render_template("cart.html", cart_items=items, total=round(total, 2))
@app.route("/update_cart", methods=["POST"])
def update_cart():
    cart = get_cart()
    for key, value in request.form.items():
        if key.startswith("qty_"):
            cid = key.split("_",1)[1]
            try:
                q = int(value)
                if q > 0:
                    cart[cid] = q
                else:
                    cart.pop(cid, None)
            except:
                pass
    save_cart(cart)
    return redirect(url_for("cart"))
@app.route("/checkout", methods=["GET","POST"])
def checkout():
    cart = get_cart(); items = []; total = 0
    for cake_id, qty in cart.items():
        cake = next((c for c in CAKES if str(c['id']) == cake_id), None)
        if cake:
            item_total = cake['price'] * qty
            total += item_total
            items.append({"cake": cake, "qty": qty, "item_total": item_total})
    total = round(total,2)
    if request.method == "POST":
        name = request.form.get("name"); card = request.form.get("card")
        if not name or not card or len(card.strip()) < 6:
            error = "Provide valid name and card (demo)."
            return render_template("checkout.html", cart_items=items, total=total, error=error)
        session.pop("cart", None)
        order_id = os.urandom(6).hex()
        return render_template("confirm.html", order_id=order_id, name=name, total=total)
    return render_template("checkout.html", cart_items=items, total=total, error=None)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=True)
