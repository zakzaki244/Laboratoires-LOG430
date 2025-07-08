from flask import Blueprint, jsonify, request
from models.product import Product
from models.store import Store
from models.sale import Sale
from db.db import SessionLocal
from db.db import Base
from functools import wraps
from models.reappro_request import ReapproRequest
from sqlalchemy.orm import joinedload

api = Blueprint('api', __name__, url_prefix='/api')
API_TOKEN = "Supermarcher22102002"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header.split(" ")[1]
        if token != API_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# -------- PRODUITS --------
@api.route("/products", methods=["GET"])
@token_required
def get_products():
    """
    Récupérer la liste de tous les produits
    ---
    security:
      - Bearer: []
    tags:
      - Produits
    responses:
      200:
        description: Liste des produits
        schema:
          type: array
          items:
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: "Oreo"
              category:
                type: string
                example: "Snack"
              price:
                type: number
                example: 2.5
              stock:
                type: integer
                example: 100
              store_id:
                type: integer
                example: 1
    """
    session = SessionLocal()
    produits = session.query(Product).all()
    data = [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "price": p.price,
            "stock": p.stock,
            "store_id": p.store_id
        }
        for p in produits
    ]
    session.close()
    return jsonify(data)

@api.route("/products/<int:pid>", methods=["GET"])
@token_required
def get_product(pid):
    """
    Récupérer un produit par son ID
    ---
    security:
      - Bearer: []
    tags:
      - Produits
    parameters:
      - in: path
        name: pid
        type: integer
        required: true
        description: ID du produit
    responses:
      200:
        description: Le produit demandé
        schema:
          properties:
            id: {type: integer}
            name: {type: string}
            category: {type: string}
            price: {type: number}
            stock: {type: integer}
            store_id: {type: integer}
      404:
        description: Produit non trouvé
    """
    session = SessionLocal()
    produit = session.query(Product).get(pid)
    if not produit:
        return jsonify({"error": "Produit non trouvé"}), 404
    data = {
        "id": produit.id,
        "name": produit.name,
        "category": produit.category,
        "price": produit.price,
        "stock": produit.stock,
        "store_id": produit.store_id
    }
    session.close()
    return jsonify(data)

@api.route("/products", methods=["POST"])
@token_required
def create_product():
    """
    Créer un nouveau produit
    ---
    security:
      - Bearer: []
    tags:
      - Produits
    parameters:
      - in: body
        name: body
        schema:
          properties:
            name: {type: string, example: "Oreo"}
            category: {type: string, example: "Snack"}
            price: {type: number, example: 2.5}
            stock: {type: integer, example: 100}
            store_id: {type: integer, example: 1}
    responses:
      201:
        description: Produit créé avec succès
        schema:
          properties:
            success: {type: boolean, example: true}
            id: {type: integer, example: 12}
    """
    session = SessionLocal()
    data = request.get_json()
    produit = Product(
        name=data["name"],
        category=data.get("category", ""),
        price=float(data["price"]),
        stock=int(data["stock"]),
        store_id=int(data["store_id"])
    )
    session.add(produit)
    session.commit()
    session.close()
    return jsonify({"success": True, "id": produit.id}), 201

@api.route("/products/<int:pid>", methods=["PUT", "PATCH"])
@token_required
def update_product(pid):
    """
    Mettre à jour un produit existant
    ---
    security:
      - Bearer: []
    tags:
      - Produits
    parameters:
      - in: path
        name: pid
        type: integer
        required: true
        description: ID du produit à modifier
      - in: body
        name: body
        schema:
          properties:
            name: {type: string, example: "Oreo"}
            category: {type: string, example: "Snack"}
            price: {type: number, example: 2.5}
            stock: {type: integer, example: 100}
            store_id: {type: integer, example: 1}
    responses:
      200:
        description: Produit mis à jour avec succès
        schema:
          properties:
            success: {type: boolean, example: true}
      404:
        description: Produit non trouvé
    """
    session = SessionLocal()
    produit = session.query(Product).get(pid)
    if not produit:
        session.close()
        return jsonify({"error": "Produit non trouvé"}), 404
    data = request.get_json()
    produit.name = data.get("name", produit.name)
    produit.category = data.get("category", produit.category)
    produit.price = float(data.get("price", produit.price))
    produit.stock = int(data.get("stock", produit.stock))
    produit.store_id = int(data.get("store_id", produit.store_id))
    session.commit()
    session.close()
    return jsonify({"success": True})

@api.route("/products/<int:pid>", methods=["DELETE"])
@token_required
def delete_product(pid):
    """
    Supprimer un produit par son ID
    ---
    security:
      - Bearer: []
    tags:
      - Produits
    parameters:
      - in: path
        name: pid
        type: integer
        required: true
        description: ID du produit à supprimer
    responses:
      200:
        description: Produit supprimé avec succès
        schema:
          properties:
            success: {type: boolean, example: true}
      404:
        description: Produit non trouvé
    """
    session = SessionLocal()
    produit = session.query(Product).get(pid)
    if not produit:
        session.close()
        return jsonify({"error": "Produit non trouvé"}), 404
    session.delete(produit)
    session.commit()
    session.close()
    return jsonify({"success": True})

# -------- MAGASINS --------
@api.route("/magasins", methods=["GET"])
@token_required
def get_magasins():
    """
    Récupérer la liste de tous les magasins
    ---
    security:
      - Bearer: []
    tags:
      - Magasins
    responses:
      200:
        description: Liste des magasins
        schema:
          type: array
          items:
            properties:
              id: {type: integer, example: 1}
              name: {type: string, example: "Magasin A"}
    """
    session = SessionLocal()
    magasins = session.query(Store).all()
    data = [{"id": m.id, "name": m.name} for m in magasins]
    session.close()
    return jsonify(data)

@api.route("/magasins/<int:mid>", methods=["GET"])
@token_required
def get_magasin(mid):
    """
    Récupérer un magasin par son ID, avec ses produits
    ---
    security:
      - Bearer: []
    tags:
      - Magasins
    parameters:
      - in: path
        name: mid
        type: integer
        required: true
        description: ID du magasin
    responses:
      200:
        description: Détail du magasin et ses produits
        schema:
          properties:
            id: {type: integer}
            name: {type: string}
            produits:
              type: array
              items:
                properties:
                  id: {type: integer}
                  name: {type: string}
                  category: {type: string}
                  price: {type: number}
                  stock: {type: integer}
      404:
        description: Magasin non trouvé
    """
    session = SessionLocal()
    magasin = session.query(Store).get(mid)
    if not magasin:
        session.close()
        return jsonify({"error": "Magasin non trouvé"}), 404
    data = {
        "id": magasin.id,
        "name": magasin.name,
        "produits": [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "price": p.price,
                "stock": p.stock
            }
            for p in magasin.products
        ]
    }
    session.close()
    return jsonify(data)

# --------- VENTES/RAPPORT ---------
@api.route("/ventes", methods=["GET"])
@token_required
def get_ventes():
    """
    Récupérer la liste des ventes (toutes les ventes)
    ---
    security:
      - Bearer: []
    tags:
      - Ventes
    responses:
      200:
        description: Liste des ventes
        schema:
          type: array
          items:
            properties:
              id: {type: integer, example: 3}
              timestamp: {type: string, example: "2024-06-12T14:00:00Z"}
              items:
                type: array
                items:
                  properties:
                    product_id: {type: integer}
                    quantity: {type: integer}
    """
    session = SessionLocal()
    ventes = session.query(Sale).all()
    data = []
    for v in ventes:
        data.append({
            "id": v.id,
            "timestamp": v.timestamp.isoformat(),
            "items": [
                {"product_id": item.product_id, "quantity": item.quantity}
                for item in v.items
            ]
        })
    session.close()
    return jsonify(data)

@api.route("/reappro", methods=["POST"])
@token_required
def create_reappro():
    """
    Créer une demande de réapprovisionnement
    ---
    security:
      - Bearer: []
    tags:
      - Réapprovisionnement
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            store_id: {type: integer, example: 2}
            product_id: {type: integer, example: 5}
            quantity: {type: integer, example: 20}
            requested_by: {type: string, example: "Zak"}
    responses:
      201:
        description: Demande créée avec succès
        schema:
          properties:
            success: {type: boolean}
            id: {type: integer}
    """
    data = request.get_json()
    session = SessionLocal()

    demande = ReapproRequest(
        store_id=data["store_id"],
        product_id=data["product_id"],
        quantity=data["quantity"],
        requested_by=data.get("requested_by", "API"),
        status="en attente"
    )

    session.add(demande)
    session.commit()
    session.close()

    return jsonify({"success": True, "id": demande.id}), 201

    @api.route("/reappro", methods=["GET"])
@token_required
def get_reappro_requests():
    """
    Récupérer toutes les demandes de réapprovisionnement en attente
    ---
    security:
      - Bearer: []
    tags:
      - Réapprovisionnement
    responses:
      200:
        description: Liste des demandes
        schema:
          type: array
          items:
            properties:
              id: {type: integer}
              store_id: {type: integer}
              product_id: {type: integer}
              quantity: {type: integer}
              requested_by: {type: string}
              status: {type: string}
    """
    session = SessionLocal()
    demandes = session.query(ReapproRequest)\
        .options(joinedload(ReapproRequest.product), joinedload(ReapproRequest.store))\
        .filter_by(status="en attente").all()

    data = [{
        "id": d.id,
        "store_id": d.store_id,
        "product_id": d.product_id,
        "quantity": d.quantity,
        "requested_by": d.requested_by,
        "status": d.status
    } for d in demandes]

    session.close()
    return jsonify(data)

@api.route("/reappro/<int:rid>", methods=["PUT"])
@token_required
def valider_reappro(rid):
    """
    Valider une demande de réapprovisionnement
    ---
    security:
      - Bearer: []
    tags:
      - Réapprovisionnement
    parameters:
      - name: rid
        in: path
        type: integer
        required: true
      - name: body
        in: body
        schema:
          properties:
            action: {type: string, example: "valider"}
    responses:
      200:
        description: Demande validée
      404:
        description: Demande non trouvée
    """
    from models.reappro_request import ReapproRequest
    session = SessionLocal()
    req = session.query(ReapproRequest).get(rid)

    if not req:
        session.close()
        return jsonify({"error": "Demande non trouvée"}), 404

    if req.status != "en attente":
        session.close()
        return jsonify({"error": "Déjà traitée"}), 400

    centre = session.query(Store).filter_by(name="Centre Logistique").first()
    prod_centre = session.query(Product).filter_by(store_id=centre.id, name=req.product.name).first()
    prod_mag = session.query(Product).filter_by(store_id=req.store_id, name=req.product.name).first()

    if prod_centre and prod_centre.stock >= req.quantity:
        prod_centre.stock -= req.quantity
        if prod_mag:
            prod_mag.stock += req.quantity
        else:
            prod_mag = Product(
                name=prod_centre.name,
                category=prod_centre.category,
                price=prod_centre.price,
                stock=req.quantity,
                store_id=req.store_id
            )
            session.add(prod_mag)
        req.status = "validée"
        session.commit()
        session.close()
        return jsonify({"success": True})
    else:
        session.close()
        return jsonify({"error": "Stock insuffisant"}), 400


@api.route("/reappro/<int:rid>", methods=["DELETE"])
@token_required
def supprimer_reappro(rid):
    """
    Supprimer une demande de réapprovisionnement
    ---
    security:
      - Bearer: []
    tags:
      - Réapprovisionnement
    parameters:
      - name: rid
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Supprimée avec succès
      404:
        description: Demande non trouvée
    """
    session = SessionLocal()
    req = session.query(ReapproRequest).get(rid)
    if not req:
        session.close()
        return jsonify({"error": "Demande non trouvée"}), 404
    session.delete(req)
    session.commit()
    session.close()
    return jsonify({"success": True})

@api.route("/sale", methods=["POST"])
@token_required
def create_sale():
    """
    Enregistrer une vente
    ---
    security:
      - Bearer: []
    tags:
      - Ventes
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            items:
              type: array
              items:
                properties:
                  product_id: {type: integer}
                  quantity: {type: integer}
    responses:
      201:
        description: Vente enregistrée
    """
    from models.sale_item import SaleItem
    session = SessionLocal()
    data = request.get_json()
    items_data = data.get("items", [])

    vente = Sale()
    session.add(vente)
    session.flush()

    for item in items_data:
        produit = session.query(Product).get(item["product_id"])
        qte = int(item["quantity"])
        if not produit or produit.stock < qte:
            session.rollback()
            session.close()
            return jsonify({"error": f"Stock insuffisant pour produit ID {produit.id}"}), 400

        produit.stock -= qte
        item_obj = SaleItem(
            sale_id=vente.id,
            product_id=produit.id,
            quantity=qte
        )
        session.add(item_obj)

    session.commit()
    session.close()
    return jsonify({"success": True, "sale_id": vente.id}), 201

@api.route("/refund", methods=["POST"])
@token_required
def refund_sale():
    """
    Annuler une vente par ID
    ---
    security:
      - Bearer: []
    tags:
      - Ventes
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            sale_id: {type: integer}
    responses:
      200:
        description: Vente annulée
    """
    from models.sale_item import SaleItem
    data = request.get_json()
    sid = int(data["sale_id"])
    session = SessionLocal()
    vente = session.query(Sale).get(sid)
    if not vente:
        session.close()
        return jsonify({"error": "Vente non trouvée"}), 404

    for item in vente.items:
        produit = session.query(Product).get(item.product_id)
        if produit:
            produit.stock += item.quantity
        session.delete(item)

    session.delete(vente)
    session.commit()
    session.close()
    return jsonify({"success": True})

@api.route("/rapport", methods=["GET"])
@token_required
def get_rapport():
    """
    Rapport consolidé des ventes et des stocks
    ---
    security:
      - Bearer: []
    tags:
      - Rapports
    responses:
      200:
        description: Rapport global
    """
    from models.sale_item import SaleItem
    session = SessionLocal()
    magasins = session.query(Store).all()
    data = {}

    for magasin in magasins:
        ventes = (
            session.query(Sale)
            .join(SaleItem)
            .join(Product)
            .filter(Product.store_id == magasin.id)
            .all()
        )
        produits = session.query(Product).filter_by(store_id=magasin.id).all()
        stocks = [{"name": p.name, "stock": p.stock} for p in produits]
        data[magasin.name] = {
            "ventes": len(ventes),
            "stocks": stocks
        }

    session.close()
    return jsonify(data)

@api.route("/products/search", methods=["GET"])
@token_required
def search_products():
    """
    Recherche de produits par nom
    ---
    security:
      - Bearer: []
    tags:
      - Produits
    parameters:
      - name: q
        in: query
        type: string
        required: true
    responses:
      200:
        description: Résultats de la recherche
    """
    term = request.args.get("q", "").lower()
    session = SessionLocal()
    produits = session.query(Product).filter(Product.name.ilike(f"%{term}%")).all()
    results = [{
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "price": p.price,
        "stock": p.stock,
        "store_id": p.store_id
    } for p in produits]
    session.close()
    return jsonify(results)