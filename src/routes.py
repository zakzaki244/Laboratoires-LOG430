from flask import Blueprint, jsonify, request
from models import Product, Store, Sale
from db import SessionLocal
from service import Service
from functools import wraps
from flask import request, jsonify

api = Blueprint('api', __name__, url_prefix='/api')
API_TOKEN = "Supermarcher22102002"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "")
        if token != f"Bearer {API_TOKEN}":
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
