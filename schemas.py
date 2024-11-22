from typing import Optional, List
from pydantic import BaseModel, condecimal, ConfigDict


# Schéma pour la création d'un utilisateur
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    address: str = None
    phone_number: str = None
    is_admin: bool = False  # Champ pour indiquer si c'est un admin



# Schéma pour la réponse utilisateur
class UserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    is_admin: bool
    address: str  # Assurez-vous que ces champs sont là
    phone_number: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


# Modèle de base pour les catégories
class CategoryBase(BaseModel):
    name: str
    description: str

# Modèle utilisé pour la création d'une catégorie (sans ID)
class CategoryCreate(CategoryBase):
    pass  # Rien à ajouter, tout est hérité de CategoryBase

# Modèle de réponse pour une catégorie, avec l'ID
class CategoryResponse(CategoryBase):
    id: int

    model_config = ConfigDict(arbitrary_types_allowed=True)


# Modèle de base pour les produits
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    category_id: int  # Relation avec la catégorie
    image: Optional[str]  # Rendre l'image optionnelle

    model_config = ConfigDict(arbitrary_types_allowed=True)


# Modèle utilisé pour la création d'un produit (sans ID)
class ProductCreate(ProductBase):
    pass

# Modèle de réponse pour un produit, avec l'ID
class ProductResponse(ProductBase):
    id: int

    model_config = ConfigDict(arbitrary_types_allowed=True)


# Schéma de base pour les commandes
class OrderBase(BaseModel):
    user_id: str
    total_amount: condecimal(max_digits=10, decimal_places=2)

# Schéma utilisé pour la création d'une commande (sans ID)
class OrderCreate(OrderBase):
    pass

class ShippingCreate(BaseModel):
    user_id: str
    address: str
    postal_code: str
    city: str
    phone_number: str
    email: str

class ShippingResponse(ShippingCreate):
    id: int

    model_config = ConfigDict(arbitrary_types_allowed=True)


print("Schemas loaded successfully")
