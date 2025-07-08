from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from flasgger import Swagger
from flask_cors import CORS
from flask import Blueprint
from services.service import Service
from db.db import SessionLocal
from models.product import Product
from models.store import Store
from models.reappro_request import ReapproRequest
from models.sale import Sale
from models.sale_item import SaleItem

web = Blueprint('web', __name__)

svc = Service()


@web.app_context_processor
def inject_centre_id():
    return dict(centre_id=get_centre_logistique_id())

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            flash("Veuillez vous connecter.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@web.route("/")
@login_required
def index():
    from db.db import SessionLocal
    from models.store import Store
    session_db = SessionLocal()
    magasins = session_db.query(Store).all()
    session_db.close()
    return render_template("index.html", magasins=magasins, centre_id=get_centre_logistique_id())



@web.route("/reapprovisionnement/<int:product_id>", methods=["POST"])
@login_required
def reapprovisionnement(product_id):
    from db.db import SessionLocal
    from models.product import Product
    qte = int(request.form["qte"])
    session_db = SessionLocal()
    produit = session_db.query(Product).get(product_id)
    session_db.close()
    flash(f"Demande de réapprovisionnement de {qte}x {produit.name} envoyée à la logistique.")
    return redirect(url_for('stock'))

@web.route("/login", methods=["GET", "POST"])
def login():
    from db.db import SessionLocal
    from models.store import Store
    session_db = SessionLocal()
    magasins = session_db.query(Store).all()
    session_db.close()
    message = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        role = request.form.get("role", "")
        store_id = request.form.get("store_id", None)
        if username and role:
            session["username"] = username
            session["role"] = role
            # Si c'est un employé ou responsable on garde le store_id
            if role in ["employe", "responsable"] and store_id:
                session["store_id"] = int(store_id)
            else:
                session.pop("store_id", None)
            flash(f"Connecté en tant que {role} ({username})")
            return redirect(url_for("index"))
        else:
            message = "Veuillez remplir tous les champs"
    return render_template("login.html", message=message, magasins=magasins,centre_id=get_centre_logistique_id())

@web.route("/reapprovisionnement/<int:product_id>", methods=["POST"])
@login_required
def reapprovisionnement_magasin(product_id):
    from db.db import SessionLocal
    from models.product import Product
    from models.reappro_request import ReapproRequest
    from models.store import Store
    session_db = SessionLocal()

    store_id = session.get("store_id")
    quantity = int(request.form.get("qte", 1))
    requested_by = session.get("username")
    # Enregistre la demande
    demande = ReapproRequest(
        store_id=store_id,
        product_id=product_id,
        quantity=quantity,
        requested_by=requested_by,
        status="en attente"
    )
    session_db.add(demande)
    session_db.commit()
    session_db.close()
    flash("Demande de réapprovisionnement envoyée au responsable logistique.")
    return redirect(url_for('stock'))

@web.route("/demande_reappro", methods=["GET", "POST"])
@login_required
def demande_reappro():
    if session.get("role") != "logistique":
        flash("Accès réservé au responsable logistique.")
        return redirect(url_for("index"))
    from db.db import SessionLocal
    from models.product import Product
    from models.reappro_request import ReapproRequest
    from models.store import Store
    session_db = SessionLocal()

    # Validation d’une demande
    if request.method == "POST":
        req_id = int(request.form["request_id"])
        req = session_db.query(ReapproRequest).get(req_id)
        if req and req.status == "en attente":
            # Approvisionne le magasin (retire du centre logistique, ajoute au magasin)
            centre = session_db.query(Store).filter_by(name="Centre Logistique").first()
            prod_centre = session_db.query(Product).filter_by(store_id=centre.id, name=req.product.name).first()
            prod_mag = session_db.query(Product).filter_by(store_id=req.store_id, name=req.product.name).first()

            if prod_centre and prod_centre.stock >= req.quantity:
                prod_centre.stock -= req.quantity
                if prod_mag:
                    prod_mag.stock += req.quantity
                else:
                    # Si le produit n'existe pas dans le magasin, crée-le
                    prod_mag = Product(
                        name=prod_centre.name,
                        category=prod_centre.category,
                        price=prod_centre.price,
                        stock=req.quantity,
                        store_id=req.store_id
                    )
                    session_db.add(prod_mag)
                req.status = "validée"
                session_db.commit()
                flash("Réapprovisionnement validé !")
            else:
                flash("Stock insuffisant au centre logistique !")
        session_db.close()
        return redirect(url_for("demande_reappro"))

    # Affichage des demandes en attente
    demandes = (
        session_db.query(ReapproRequest)
        .filter_by(status="en attente")
        .all()
    )
    session_db.close()
    return render_template("demande_reappro.html", demandes=demandes, centre_id=get_centre_logistique_id())

@web.route("/logout")
def logout():
    session.clear()
    flash("Déconnecté")
    return redirect(url_for("login"))

@web.route("/magasins")
def magasins():
    from db.db import SessionLocal
    from models.store import Store
    session = SessionLocal()
    magasins = session.query(Store).all()
    session.close()
    return render_template("magasins.html", magasins=magasins, centre_id=get_centre_logistique_id())

@web.route("/search", methods=["GET", "POST"])
@login_required
def search():
    results = []
    if request.method == "POST":
        term = request.form["term"]
        results = svc.search(term)
    return render_template("search.html", results=results, centre_id=get_centre_logistique_id())

@web.route("/store/<int:store_id>/stock")
@login_required
def store_stock(store_id):
    from db.db import SessionLocal
    from models.product import Product
    from models.store import Store
    session_db = SessionLocal()
    store = session_db.query(Store).get(store_id)
    produits = session_db.query(Product).filter_by(store_id=store_id).all()
    session_db.close()
    return render_template("stock.html", store=store, produits=produits, centre_id=get_centre_logistique_id())


@web.route("/stock")
@login_required
def stock():
    from db.db import SessionLocal
    from models.product import Product
    from models.store import Store
    session_db = SessionLocal()
    store = None
    produits = []

    store_id = session.get("store_id")  # magasin assigné en session
    if store_id:
        store = session_db.query(Store).get(store_id)
        produits = session_db.query(Product).filter_by(store_id=store_id).all()
    else:
        # Si pas de magasin (gestionnaire), montrer tous les produits
        produits = session_db.query(Product).all()
    session_db.close()
    return render_template("stock.html", produits=produits, store=store, centre_id=get_centre_logistique_id())


@web.route("/sale", methods=["GET", "POST"])
@login_required
def sale():
    from db.db import SessionLocal
    from models.product import Product
    store_id = session.get("store_id")
    produits = []
    session_db = SessionLocal()
    if store_id:
        produits = session_db.query(Product).filter_by(store_id=store_id).all()
    else:
        # Gestionnaire : toutes les ventes possibles (optionnel)
        produits = session_db.query(Product).all()
    session_db.close()
    
    message = ""
    if request.method == "POST":
        cart = []
        for produit in produits:
            qte = request.form.get(f"qte_{produit.id}", "0")
            try:
                qte = int(qte)
            except ValueError:
                qte = 0
            if qte > 0:
                if qte > produit.stock:
                    message = f"Stock insuffisant pour {produit.name}"
                    return render_template("sale.html", produits=produits, message=message, centre_id=get_centre_logistique_id())
                cart.append((produit.id, qte))
        if cart:
            try:
                sale_id = svc.sale(cart)
                flash(f"Vente #{sale_id} enregistrée !")
                return redirect(url_for("sale"))
            except Exception as e:
                message = str(e)
        else:
            message = "Aucun article sélectionné."
    return render_template("sale.html", produits=produits, message=message, centre_id=get_centre_logistique_id())


@web.route("/refund", methods=["GET", "POST"])
@login_required
def refund():
    message = ""
    if request.method == "POST":
        sid = request.form.get("sale_id", "")
        try:
            svc.refund(int(sid))
            flash(f"Vente #{sid} annulée.")
            return redirect(url_for("refund"))
        except Exception as e:
            message = str(e)
    return render_template("refund.html", message=message, centre_id=get_centre_logistique_id())

@web.route("/products", methods=["GET", "POST"])
@login_required
def manage_products():
    if session.get("role") == "employe":
        flash("Accès refusé.")
        return redirect(url_for("index"))
    from db.db import SessionLocal
    from models.product import Product
    from models.store import Store
    session_db = SessionLocal()

    # Création d'un nouveau produit
    if request.method == "POST" and "create" in request.form:
        name = request.form["name"]
        category = request.form["category"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        store_id = int(request.form["store_id"])
        nouveau = Product(name=name, category=category, price=price, stock=stock, store_id=store_id)
        session_db.add(nouveau)
        session_db.commit()
        flash("Produit créé avec succès.")

    # Modification d'un produit (inline)
    if request.method == "POST" and "edit" in request.form:
        prod_id = int(request.form["prod_id"])
        produit = session_db.query(Product).get(prod_id)
        produit.name = request.form["name"]
        produit.category = request.form["category"]
        produit.price = float(request.form["price"])
        produit.stock = int(request.form["stock"])
        produit.store_id = int(request.form["store_id"])
        session_db.commit()
        flash("Produit mis à jour.")

    # Suppression
    if request.method == "POST" and "delete" in request.form:
        prod_id = int(request.form["prod_id"])
        produit = session_db.query(Product).get(prod_id)
        session_db.delete(produit)
        session_db.commit()
        flash("Produit supprimé.")

    # Affichage produits et magasins
    produits = session_db.query(Product).all()
    magasins = session_db.query(Store).all()
    session_db.close()
    return render_template("products.html", produits=produits, magasins=magasins)



@web.route("/rapport")
@login_required
def rapport():
    if session.get("role") != "gestionnaire":
        flash("Accès réservé aux gestionnaires de la maison mère.")
        return redirect(url_for("index"))
    from db.db import SessionLocal
    from models.product import Product
    from models.sale import Sale
    from models.sale_item import SaleItem
    session_db = SessionLocal()
    # Ventes par magasin
    magasins = session_db.query(Store).all()
    ventes_par_magasin = {}
    produits_vendus = {}
    for magasin in magasins:
        ventes = (
            session_db.query(Sale)
            .join(SaleItem)
            .join(Product)
            .filter(Product.store_id == magasin.id)
            .all()
        )
        ventes_par_magasin[magasin.name] = len(ventes)
        # Récupérer produits les plus vendus
        items = (
            session_db.query(Product.name, SaleItem.quantity)
            .join(SaleItem, Product.id == SaleItem.product_id)
            .filter(Product.store_id == magasin.id)
            .all()
        )
        produits_vendus[magasin.name] = items
    # Stock restant par magasin
    stocks = {}
    for magasin in magasins:
        produits = session_db.query(Product).filter_by(store_id=magasin.id).all()
        stocks[magasin.name] = [(p.name, p.stock) for p in produits]

    session_db.close()
    return render_template(
        "rapport.html",
        ventes_par_magasin=ventes_par_magasin,
        produits_vendus=produits_vendus,
        stocks=stocks, 
        centre_id=get_centre_logistique_id(),
    )

