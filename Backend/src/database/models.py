import uuid
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Column, Relationship
from datetime import datetime
from typing import Optional, List
from sqlalchemy import text, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB



class User(SQLModel, table=True):
    __tablename__ = 'user'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    first_name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    last_name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    email: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    password: str = Field(sa_column=Column(pg.VARCHAR, nullable=False), exclude=True)
    phone: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    customer_status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="active"), default="active")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    is_verified: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default=text("false")), default=False)
    is_admin: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default=text("false")), default=False)
    is_customer: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default=text("false")), default=False)
    two_fa_secret: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    two_fa_enabled: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default=text("false")), default=False)
    otp: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    expires_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))


    address: List["Address"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy': 'noload'})
    order: List["Order"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy': 'noload'})
    evaluate: List["Evaluate"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy': 'noload'})
    user_special_offer: List["UserSpecialOffer"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={'lazy': 'noload'}
    )


class Address(SQLModel, table=True):
    __tablename__ = 'address'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    line: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    street: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    ward: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    city: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    district: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    country: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="Việt Nam"), default="Việt Nam")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    user_id: uuid.UUID = Field(foreign_key="user.id")

    user: Optional["User"] = Relationship(back_populates="address", sa_relationship_kwargs={'lazy': 'noload'})


class Order(SQLModel, table=True):
    __tablename__ = 'order'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    code: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    sub_total: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    total_price: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    discount: Optional[int] = Field(sa_column=Column(pg.INTEGER, nullable=True, server_default=text("0")), default=0)
    discount_percent: Optional[int] = Field(sa_column=Column(pg.INTEGER, nullable=True, server_default=text("0")), default=0)
    note: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))

    status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))

    payment_method: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="vnpay"), default="vnpay")
    payment_status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="pending"), default="pending")

    special_offer_id: Optional[uuid.UUID] = Field(foreign_key="special_offer.id", default=None, nullable=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    delivered_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    received_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    address_snapshot: dict = Field(sa_column=Column(pg.JSONB, nullable=False))
    special_offer_snapshot: dict = Field(sa_column=Column(pg.JSONB, nullable=False))

    cancellation_reason: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True), default=None)
    cancellation_status: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True), default=None)
    cancellation_requested_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True), default=None)

    user: Optional["User"] = Relationship(back_populates="order", sa_relationship_kwargs={'lazy': 'noload'})
    order_detail: List["Order_Detail"] = Relationship(back_populates="order",
                                                      sa_relationship_kwargs={'lazy': 'noload'})
    order_status_history: List["OrderStatusHistory"] = Relationship(
        back_populates="order", sa_relationship_kwargs={"lazy": "noload"}
    )
    payments: List["Payment"] = Relationship(back_populates="order", sa_relationship_kwargs={"lazy": "noload"})
    special_offer: Optional["Special_Offer"] = Relationship(
        back_populates="orders", sa_relationship_kwargs={'lazy': 'noload'}
    )
    notifications: List["Notification"] = Relationship(back_populates="order",
                                                       sa_relationship_kwargs={"lazy": "noload"})
    return_orders: List["ReturnOrder"] = Relationship(back_populates="order",
                                                       sa_relationship_kwargs={"lazy": "noload"})


class Order_Detail(SQLModel, table=True):
    __tablename__ = 'order_detail'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    price: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    product_id: uuid.UUID = Field( foreign_key="product.id")
    product_variant_id: uuid.UUID = Field(foreign_key="product_variant.id")
    order_id: uuid.UUID = Field(foreign_key="order.id")
    product_snapshot: Optional[dict] = Field(sa_column=Column(pg.JSONB, nullable=True))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    product: Optional["Product"] = Relationship(back_populates="order_detail", sa_relationship_kwargs={'lazy': 'noload'})
    product_variant: Optional["Product_Variant"] = Relationship(back_populates="order_detail", sa_relationship_kwargs={'lazy': 'noload'})
    order: Optional["Order"] = Relationship(back_populates="order_detail", sa_relationship_kwargs={'lazy': 'noload'})
    evaluate: Optional["Evaluate"] = Relationship(back_populates="order_detail", sa_relationship_kwargs={'lazy': 'noload', "uselist": False})


class Categories_Product(SQLModel, table=True):
    __tablename__ = 'categories_product'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    categories_id: uuid.UUID = Field(foreign_key="categories.id")
    product_id: uuid.UUID = Field( foreign_key="product.id")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    categories: Optional["Categories"] = Relationship(back_populates="categories_product",
                                                                  sa_relationship_kwargs={'lazy': 'noload'})
    product: Optional["Product"] = Relationship(back_populates="categories_product",
                                                sa_relationship_kwargs={'lazy': 'noload'})


class Brand(SQLModel, table=True):
    __tablename__ = "brand"
    __table_args__ = (
        Index(
            'ix_brand_name_unique_not_deleted',
            'name',
            unique=True,
            postgresql_where=text('deleted_at IS NULL')
        ),
        Index(
            'ix_brand_slug_unique_not_deleted',
            'slug',
            unique=True,
            postgresql_where=text('deleted_at IS NULL')
        ),
    )

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, 
            nullable=False, 
            primary_key=True, 
            default=uuid.uuid4
        )
    )

    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    slug: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    logo: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    is_active: bool = Field(
        sa_column=Column(pg.BOOLEAN, nullable=False, server_default=text("true")), 
        default=True
    )

    products_count: int = Field(
        sa_column=Column(pg.INTEGER, nullable=False, server_default=text("0")),
        default=0
    )

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), 
        default=datetime.now
    )
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    products: List["Product"] = Relationship(
        back_populates="brand", sa_relationship_kwargs={'lazy': 'noload'}
    )


class Product_Material(SQLModel, table=True):
    __tablename__ = 'product_material'
    
    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, 
            nullable=False, 
            primary_key=True, 
            default=uuid.uuid4
        )
    )
    product_id: uuid.UUID = Field(foreign_key="product.id")
    material_id: uuid.UUID = Field(foreign_key="material.id")
    percentage: Optional[float] = Field(sa_column=Column(pg.FLOAT, nullable=True))
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), 
        default=datetime.now
    )
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    
    product: Optional["Product"] = Relationship(
        back_populates="product_materials", sa_relationship_kwargs={'lazy': 'noload'}
    )
    material: Optional["Material"] = Relationship(
        back_populates="product_materials", sa_relationship_kwargs={'lazy': 'noload'}
    )


class Product_Tag(SQLModel, table=True):
    __tablename__ = 'product_tag'
    
    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, 
            nullable=False, 
            primary_key=True, 
            default=uuid.uuid4
        )
    )
    product_id: uuid.UUID = Field(foreign_key="product.id")
    tag_id: uuid.UUID = Field(foreign_key="tag.id")
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), 
        default=datetime.now
    )
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    
    product: Optional["Product"] = Relationship(
        back_populates="product_tags", sa_relationship_kwargs={'lazy': 'noload'}
    )
    tag: Optional["Tag"] = Relationship(
        back_populates="product_tags", sa_relationship_kwargs={'lazy': 'noload'}
    )


class Material(SQLModel, table=True):
    __tablename__ = "material"
    __table_args__ = (
        Index(
            'ix_material_name_unique_not_deleted',
            'name',
            unique=True,
            postgresql_where=text('deleted_at IS NULL')
        ),
        Index(
            'ix_material_slug_unique_not_deleted',
            'slug',
            unique=True,
            postgresql_where=text('deleted_at IS NULL')
        ),
    )

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, 
            nullable=False, 
            primary_key=True, 
            default=uuid.uuid4
        )
    )

    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    slug: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    is_active: bool = Field(
        sa_column=Column(pg.BOOLEAN, nullable=False, server_default=text("true")), 
        default=True
    )

    products_count: int = Field(
        sa_column=Column(pg.INTEGER, nullable=False, server_default=text("0")),
        default=0
    )

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), 
        default=datetime.now
    )
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    product_materials: List["Product_Material"] = Relationship(
        back_populates="material", sa_relationship_kwargs={'lazy': 'noload'}
    )
    products: List["Product"] = Relationship(
        back_populates="materials", link_model=Product_Material, sa_relationship_kwargs={'lazy': 'noload'}
    )


class Tag(SQLModel, table=True):
    __tablename__ = 'tag'
    __table_args__ = (
        Index(
            'ix_tag_name_unique_not_deleted',
            'name',
            unique=True,
            postgresql_where=text('deleted_at IS NULL')
        ),
        Index(
            'ix_tag_slug_unique_not_deleted',
            'slug',
            unique=True,
            postgresql_where=text('deleted_at IS NULL')
        ),
    )
    
    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, 
            nullable=False, 
            primary_key=True, 
            default=uuid.uuid4
        )
    )
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    slug: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    is_active: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default=text("true")), default=True)

    products_count: int = Field(
        sa_column=Column(pg.INTEGER, nullable=False, server_default=text("0")),
        default=0
    )
    
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), 
        default=datetime.now
    )
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    
    product_tags: List["Product_Tag"] = Relationship(
        back_populates="tag", sa_relationship_kwargs={'lazy': 'noload'}
    )
    products: List["Product"] = Relationship(
        back_populates="tags", link_model=Product_Tag, sa_relationship_kwargs={'lazy': 'noload'}
    )


class Product(SQLModel, table=True):
    __tablename__ = 'product'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    images: List[str] = Field(sa_column=Column(JSONB, nullable=False))
    description: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))
    short_description: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))
    popularity_score: Optional[int] = Field(sa_column=Column(pg.INTEGER, nullable=False, server_default="0"), default=0)
    total_sold: int = Field(sa_column=Column(pg.INTEGER, nullable=False, server_default="0"),default=0)
    review_count: int = Field(sa_column=Column(pg.INTEGER, nullable=False, server_default="0"), default=0)
    avg_rating: Optional[float] = Field(sa_column=Column(pg.FLOAT, nullable=False, server_default="0"), default=0.0)
    status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="active"), default="active")
    slug: str = Field(sa_column=Column(pg.VARCHAR, nullable=True, unique=True))
    special_offer_id: Optional[uuid.UUID] = Field(foreign_key="special_offer.id", default=None, nullable=True)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    brand_id: Optional[uuid.UUID] = Field(foreign_key="brand.id", nullable=True)

    order_detail: List["Order_Detail"] = Relationship(back_populates="product", sa_relationship_kwargs={'lazy': 'noload'})
    categories_product: List["Categories_Product"] = Relationship(back_populates="product", sa_relationship_kwargs={'lazy': 'noload'})
    product_variant: List["Product_Variant"] = Relationship(back_populates="product", sa_relationship_kwargs={'lazy': 'noload'})
    evaluate: List["Evaluate"] = Relationship(back_populates="product", sa_relationship_kwargs={'lazy': 'noload'})
    categories: List["Categories"] = Relationship(back_populates="products", link_model=Categories_Product, sa_relationship_kwargs={'lazy': 'noload'})
    special_offer: Optional["Special_Offer"] = Relationship(back_populates="products", sa_relationship_kwargs={'lazy': 'noload'})
    brand: Optional["Brand"] = Relationship(back_populates="products", sa_relationship_kwargs={'lazy': 'noload'})
    product_materials: List["Product_Material"] = Relationship(back_populates="product", sa_relationship_kwargs={'lazy': 'noload'})
    materials: List["Material"] = Relationship(back_populates="products", link_model=Product_Material, sa_relationship_kwargs={'lazy': 'noload'})
    product_tags: List["Product_Tag"] = Relationship(back_populates="product", sa_relationship_kwargs={'lazy': 'noload'})
    tags: List["Tag"] = Relationship(back_populates="products", link_model=Product_Tag,sa_relationship_kwargs={'lazy': 'noload'})


class Product_Variant(SQLModel, table=True):
    __tablename__ = 'product_variant'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    size: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    price: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    sku: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    image: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    product_id: uuid.UUID = Field(foreign_key="product.id")

    color_id: Optional[uuid.UUID] = Field(foreign_key="color.id", nullable=True)

    color_name: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    color_code: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))

    order_detail: List["Order_Detail"] = Relationship(back_populates="product_variant",
                                                      sa_relationship_kwargs={'lazy': 'noload'})
    product: Optional["Product"] = Relationship(back_populates="product_variant",
                                                sa_relationship_kwargs={'lazy': 'noload'})
    evaluate: List["Evaluate"] = Relationship(back_populates="product_variant",
                                              sa_relationship_kwargs={'lazy': 'noload'})
    color: Optional["Color"] = Relationship(back_populates="product_variant",
                                                sa_relationship_kwargs={'lazy': 'noload'})


class Categories(SQLModel, table=True):
    __tablename__ = 'categories'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    image: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    parent_id: Optional[uuid.UUID] = Field(foreign_key="categories.id", nullable=True)
    type_size: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    slug: str = Field(sa_column=Column(pg.VARCHAR, nullable=True, unique=True))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    categories_product: List["Categories_Product"] = Relationship(back_populates="categories",
                                                sa_relationship_kwargs={'lazy': 'noload'})
    products: List["Product"] = Relationship(back_populates="categories", link_model=Categories_Product, sa_relationship_kwargs={'lazy': 'noload'})
    parent: Optional["Categories"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Categories.id", "lazy": "noload"}
    )
    children: List["Categories"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"lazy": "noload"}
    )

Categories.model_rebuild()

class Evaluate(SQLModel, table=True):
    __tablename__ = 'evaluate'
    __table_args__ = (
        UniqueConstraint('order_detail_id', name='uq_evaluate_order_detail_id'),  # Đảm bảo 1-1
    )

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    comment: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))
    rate: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    image: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    additional_comment: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    additional_image: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    additional_created_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    seller_reply: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))
    seller_reply_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    product_id: uuid.UUID = Field(foreign_key="product.id")
    order_detail_id: uuid.UUID = Field(foreign_key="order_detail.id", nullable=False, unique=True)
    product_variant_id: uuid.UUID = Field(foreign_key="product_variant.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")

    order_detail: Optional["Order_Detail"] = Relationship(back_populates="evaluate",
                                                      sa_relationship_kwargs={'lazy': 'noload', "uselist": False})
    product: Optional["Product"] = Relationship(back_populates="evaluate",
                                                sa_relationship_kwargs={'lazy': 'noload'})
    user: Optional["User"] = Relationship(back_populates="evaluate",
                                                sa_relationship_kwargs={'lazy': 'noload'})
    product_variant: Optional["Product_Variant"] = Relationship(back_populates="evaluate",
                                                            sa_relationship_kwargs={'lazy': 'noload'})


class Special_Offer(SQLModel, table=True):
    __tablename__ = 'special_offer'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    code: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    discount: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    condition: Optional[int] = Field(sa_column=Column(pg.INTEGER, nullable=True))
    type: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    total_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    scope: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="order"), default="order")
    used_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=True, server_default=text("0")), default=0)
    start_time: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    end_time: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    products: List["Product"] = Relationship(back_populates="special_offer", sa_relationship_kwargs={"lazy": "noload"})
    user_special_offer: List["UserSpecialOffer"] = Relationship(
        back_populates="special_offer", sa_relationship_kwargs={'lazy': 'noload'}
    )
    orders: List["Order"] = Relationship(
        back_populates="special_offer", sa_relationship_kwargs={"lazy": "noload"}
    )
    notifications: List["Notification"] = Relationship(back_populates="special_offer", sa_relationship_kwargs={"lazy": "noload"})


class UserSpecialOffer(SQLModel, table=True):
    __tablename__ = 'user_special_offer'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    user_id: uuid.UUID = Field(foreign_key="user.id")
    special_offer_id: uuid.UUID = Field(foreign_key="special_offer.id")
    used_at: Optional[datetime] = Field(default=None)

    user: Optional["User"] = Relationship(back_populates="user_special_offer", sa_relationship_kwargs={'lazy': 'noload'})
    special_offer: Optional["Special_Offer"] = Relationship(back_populates="user_special_offer",
                                                sa_relationship_kwargs={'lazy': 'noload'})


class Color(SQLModel, table=True):
    __tablename__ = 'color'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    code: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    product_variant: List["Product_Variant"] = Relationship(back_populates="color",
                                                                sa_relationship_kwargs={'lazy': 'noload'})


class Size(SQLModel, table=True):
    __tablename__ = 'size'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    type: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, index=True))


class Cart(SQLModel, table=True):
    __tablename__ = "cart"

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4)
    )

    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP))
    deleted_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP))

    user: Optional["User"] = Relationship(sa_relationship_kwargs={"lazy": "noload"})
    items: List["Cart_Item"] = Relationship(back_populates="cart", sa_relationship_kwargs={"lazy": "noload"})


class Cart_Item(SQLModel, table=True):
    __tablename__ = "cart_item"
    __table_args__ = (
        UniqueConstraint(
            "cart_id", "product_id", "product_variant_id",
            name="uq_cart_item_cart_product_variant"
        ),
    )

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4)
    )

    cart_id: uuid.UUID = Field(foreign_key="cart.id", nullable=False)
    product_id: uuid.UUID = Field(foreign_key="product.id", nullable=False)
    product_variant_id: uuid.UUID = Field(foreign_key="product_variant.id", nullable=True)

    quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False, server_default="1"), default=1)
    price: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP))
    deleted_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP))

    cart: Optional["Cart"] = Relationship(back_populates="items", sa_relationship_kwargs={"lazy": "noload"})
    product: Optional["Product"] = Relationship(sa_relationship_kwargs={"lazy": "noload"})
    product_variant: Optional["Product_Variant"] = Relationship(sa_relationship_kwargs={"lazy": "noload"})


class OrderStatusHistory(SQLModel, table=True):
    __tablename__ = "order_status_history"

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    )

    order_id: uuid.UUID = Field(foreign_key="order.id", nullable=False)
    status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
        default=datetime.now
    )

    order: Optional["Order"] = Relationship(
        back_populates="order_status_history", sa_relationship_kwargs={"lazy": "noload"}
    )


class Payment(SQLModel, table=True):
    __tablename__ = "payment"

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    )
    order_id: uuid.UUID = Field(foreign_key="order.id", nullable=False)

    payment_gateway: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))  # vnpay, momo, paypal...

    txn_ref: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, unique=True)) # vnp_TxnRef
    transaction_no: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))   # vnp_TransactionNo
    bank_tran_no: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True)) # vnp_BankTranNo
    bank_code: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))  # vnp_BankCode
    card_type: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))  # vnp_CardType

    amount: int = Field(sa_column=Column(pg.INTEGER, nullable=False))           # vnp_Amount / 100
    order_info: str = Field(sa_column=Column(pg.VARCHAR, nullable=True))        # vnp_OrderInfo

    response_code: str = Field(sa_column=Column(pg.VARCHAR, nullable=True))  # vnp_ResponseCode
    transaction_status: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))  # vnp_TransactionStatus
    status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="success"), default="success")

    pay_date: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
        default=datetime.now,
    )

    order: Optional["Order"] = Relationship(back_populates="payments", sa_relationship_kwargs={"lazy": "noload"})
    payment_refunds: List["PaymentRefund"] = Relationship(back_populates="payment", sa_relationship_kwargs={"lazy": "noload"})


class PaymentRefund(SQLModel, table=True):
    __tablename__ = "payment_refund"

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    )

    payment_id: uuid.UUID = Field(foreign_key="payment.id", nullable=False)

    refund_type: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))  # e.g. "02" (Hoàn toàn), "03" (Một phần)
    refund_amount: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    refund_reason: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))

    txn_ref: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))  # vnp_TxnRef
    bank_code: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))  # vnp_BankCode

    transaction_no: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))  # từ VNPAY trả về
    transaction_status: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))  # vnp_TransactionStatus
    response_code: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="pending"), default="pending")
    note: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))

    attempt_count: int = Field(sa_column=Column(pg.INTEGER, nullable=False, server_default="0"), default=0)

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
        default=datetime.now,
    )

    payment: Optional["Payment"] = Relationship(back_populates="payment_refunds", sa_relationship_kwargs={"lazy": "noload"})


class Notification(SQLModel, table=True):
    __tablename__ = 'notification'

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    )

    # Loại người nhận thông báo ('admin', 'customer')
    recipient_type: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))

    # id nếu customer nhận, null nếu admin
    recipient_id: Optional[uuid.UUID] = Field(sa_column=Column(pg.UUID, nullable=True))

    # Giống bên trên, nhưng mà là người gửi.
    sender_type: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    sender_id: Optional[uuid.UUID] = Field(sa_column=Column(pg.UUID, nullable=True))

    type: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    title: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    message: str = Field(sa_column=Column(pg.TEXT, nullable=False))

    # Thông báo liên quan đến 1 đơn hàng cụ thể
    order_id: Optional[uuid.UUID] = Field(foreign_key="order.id", nullable=True)
    special_offer_id: Optional[uuid.UUID] = Field(foreign_key="special_offer.id", nullable=True)
    return_order_id: Optional[uuid.UUID] = Field(foreign_key="return_order.id", nullable=True)

    # Đánh dấu thông báo đã đọc hay chưa.
    is_read: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default="false"), default=False)
    read_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    # Dành cho notification yêu cầu action (như approve cancel request)
    action_type: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    action_data: Optional[str] = Field(sa_column=Column(pg.JSON, nullable=True))

    # Đánh dấu notification đã được xử lý (cho những notification cần action)
    is_processed: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default="false"), default=False)
    processed_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
        default=datetime.now
    )

    order: Optional["Order"] = Relationship(back_populates="notifications", sa_relationship_kwargs={"lazy": "noload"})
    special_offer: Optional["Special_Offer"] = Relationship(back_populates="notifications", sa_relationship_kwargs={"lazy": "noload"})
    return_order: Optional["ReturnOrder"] = Relationship(back_populates="notifications",
                                                         sa_relationship_kwargs={"lazy": "noload"})

class ReturnOrder(SQLModel, table=True):
    __tablename__ = "return_order"

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    )
    order_id: uuid.UUID = Field(foreign_key="order.id", nullable=False)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    reason: str = Field(sa_column=Column(pg.VARCHAR, nullable=False)) 
    status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="pending"))  
    note: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")))
    approved_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    rejected_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    refunded_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    order: Optional["Order"] = Relationship(back_populates="return_orders", sa_relationship_kwargs={"lazy": "noload"})
    user: Optional["User"] = Relationship(sa_relationship_kwargs={"lazy": "noload"})
    return_items: List["ReturnItem"] = Relationship(back_populates="return_order", sa_relationship_kwargs={"lazy": "noload"})
    notifications: List["Notification"] = Relationship(back_populates="return_order",
                                                       sa_relationship_kwargs={"lazy": "noload"})

class ReturnItem(SQLModel, table=True):
    __tablename__ = "return_item"

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    )
    return_order_id: uuid.UUID = Field(foreign_key="return_order.id", nullable=False)
    order_detail_id: uuid.UUID = Field(foreign_key="order_detail.id", nullable=False)

    quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    refund_amount: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    images: List[str] = Field(sa_column=Column(JSONB, nullable=False))

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")))

    return_order: Optional["ReturnOrder"] = Relationship(back_populates="return_items", sa_relationship_kwargs={"lazy": "noload"})
    order_detail: Optional["Order_Detail"] = Relationship(sa_relationship_kwargs={"lazy": "noload"})






    

    
