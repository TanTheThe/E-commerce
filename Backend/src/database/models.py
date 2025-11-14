import uuid
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Column, Relationship
from datetime import datetime
from typing import Optional, List
from sqlalchemy import text, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB



class Province(SQLModel, table=True):
    __tablename__ = 'province'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    code: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    code_name: str = Field(sa_column=Column(pg.VARCHAR, unique=True, nullable=False))
    division_type: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    phone_code: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    wards: List["Ward"] = Relationship(back_populates="province")
    addresses: List["Address"] = Relationship(back_populates="province")


class Ward(SQLModel, table=True):
    __tablename__ = 'ward'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    code: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    code_name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, index=True))
    short_code_name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    division_type: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    province_id: uuid.UUID = Field(foreign_key="province.id")

    province: Optional[Province] = Relationship(back_populates="wards")
    addresses: List["Address"] = Relationship(back_populates="ward")


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

    ward_id: uuid.UUID = Field(foreign_key="ward.id")
    province_id: uuid.UUID = Field(foreign_key="province.id")

    district: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True), default=None)

    country: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="Việt Nam"), default="Việt Nam")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    user_id: uuid.UUID = Field(foreign_key="user.id")

    user: Optional["User"] = Relationship(back_populates="address", sa_relationship_kwargs={'lazy': 'noload'})
    ward: Optional[Ward] = Relationship(back_populates="addresses", sa_relationship_kwargs={'lazy': 'noload'})
    province: Optional[Province] = Relationship(back_populates="addresses", sa_relationship_kwargs={'lazy': 'noload'})


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


class Supplier_Product(SQLModel, table=True):
    __tablename__ = 'supplier_product'

    supplier_id: uuid.UUID = Field(
        foreign_key="supplier.id",
        primary_key=True,
        nullable=False
    )

    product_id: uuid.UUID = Field(
        foreign_key="product.id",
        primary_key=True,
        nullable=False
    )

    is_active: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default="true"), default=True)

    notes: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP")
        ),
        default=datetime.now
    )

    updated_at: Optional[datetime] = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=True)
    )

    products: Optional["Product"] = Relationship(back_populates="supplier_products", sa_relationship_kwargs={'lazy': 'noload'})
    suppliers: Optional["Supplier"] = Relationship(back_populates="supplier_products", sa_relationship_kwargs={'lazy': 'noload'})


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
    supplier_products: List["Supplier_Product"] = Relationship(back_populates="products", sa_relationship_kwargs={'lazy': 'noload'})
    suppliers: List["Supplier"] = Relationship(back_populates="products", link_model=Supplier_Product, sa_relationship_kwargs={'lazy': 'noload'})


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


class StockReservation(SQLModel, table=True):
    """ Quản lý đặt giữ hàng trong kho.
    Tránh việc bán trùng khi có khách đặt nhưng chưa hoàn tất thanh toán hoặc chưa xử lý đơn hàng """

    __tablename__ = 'stock_reservation'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    warehouse_id: uuid.UUID = Field(foreign_key="warehouse.id", nullable=False)
    product_variant_id: uuid.UUID = Field(foreign_key="product_variant.id", nullable=False)

    # Số lượng sản phẩm được giữ
    quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Cái này giúp trace ngược: đặt giữ này là từ đơn hàng nào, giỏ hàng nào
    reference_id: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=False))  # order_id, cart_id, etc.
    reference_type: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))  # order, cart, etc.

    # active, fulfilled, cancelled, expired
    status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="active"), default="active")

    # Thời gian hết hạn đặt trước
    expires_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    warehouse: Optional["Warehouse"] = Relationship(sa_relationship_kwargs={'lazy': 'noload'})
    product_variant: Optional["Product_Variant"] = Relationship(sa_relationship_kwargs={'lazy': 'noload'})


class StockAdjustmentItem(SQLModel, table=True):
    """ Chi tiết điều chỉnh tồn kho. Một lần kiểm kho thì tạo 1 StockAdjustment, 
    trong đó chứa nhiều StockAdjustmentItem (mỗi item ứng với một variant) """

    __tablename__ = 'stock_adjustment_item'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    stock_adjustment_id: uuid.UUID = Field(foreign_key="stock_adjustment.id", nullable=False)
    product_variant_id: uuid.UUID = Field(foreign_key="product_variant.id", nullable=False)

    # Số lượng sản phẩm theo hệ thống (số lượng trong Stock)
    system_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Số lượng thực tế kiểm đếm được ngoài kho.
    actual_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Chênh lệch giữa thực tế và hệ thống
    difference_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Giá nhập của 1 sản phẩm tại thời điểm kiểm kê
    unit_cost: Optional[int] = Field(sa_column=Column(pg.INTEGER, nullable=True))

    # Tổng giá trị cần điều chỉnh = difference_quantity × unit_cost
    adjustment_value: Optional[int] = Field(sa_column=Column(pg.INTEGER, nullable=True))

    reason: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))
    note: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)

    stock_adjustment: Optional["StockAdjustment"] = Relationship(back_populates="adjustment_items", sa_relationship_kwargs={'lazy': 'noload'})
    product_variant: Optional["Product_Variant"] = Relationship(sa_relationship_kwargs={'lazy': 'noload'})


class StockAdjustment(SQLModel, table=True):
    """ Phiếu Điều chỉnh tồn kho - khi số lượng thực tế trong kho khác với số lượng trên hệ thống và cần cập nhật lại """
    __tablename__ = 'stock_adjustment'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    adjustment_code: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, unique=True))
    warehouse_id: uuid.UUID = Field(foreign_key="warehouse.id", nullable=False)

    # inventory_count, damaged_goods, expired, system_correction,...
    reason: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    note: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    # draft, approved, applied
    status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="draft"), default="draft")

    # Tổng giá trị tiền của việc điều chỉnh
    total_adjustment_value: Optional[int] = Field(sa_column=Column(pg.INTEGER, nullable=True))

    created_by: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)
    approved_by: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    approved_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    applied_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    warehouse: Optional["Warehouse"] = Relationship(sa_relationship_kwargs={'lazy': 'noload'})
    adjustment_items: List["StockAdjustmentItem"] = Relationship(back_populates="stock_adjustment", sa_relationship_kwargs={'lazy': 'noload'})


class StockTransaction(SQLModel, table=True):
    """Lịch sử giao dịch kho"""
    __tablename__ = 'stock_transaction'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    warehouse_id: uuid.UUID = Field(foreign_key="warehouse.id", nullable=False)
    stock_id: uuid.UUID = Field(foreign_key="stock.id", nullable=False)
    product_variant_id: uuid.UUID = Field(foreign_key="product_variant.id", nullable=False)

    # inbound (nhập từ NCC), outbound (xuất bán/trả NCC), adjustment (kiểm kê điều chỉnh), damaged (hư hỏng)
    transaction_type: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))

    # Số lượng thay đổi trong giao dịch. Nhập thì số dương (VD: +50), xuất thì số âm (VD: -10)
    quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Số lượng tồn (trong Stock.quantity) trước khi giao dịch
    previous_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Số lượng tồn sau khi giao dịch
    new_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Giá vốn của 1 variant cho lần nhập/xuất này
    unit_cost: Optional[int] = Field(sa_column=Column(pg.INTEGER, nullable=True))

    # Tổng giá vốn = unit_cost * |quantity|
    total_cost: Optional[int] = Field(sa_column=Column(pg.INTEGER, nullable=True))

    # ID tham chiếu đến thực thể gốc gây ra giao dịch
    # VD: goods_receipt_id, order_id, purchase_return_id, stock_adjustment_id
    reference_id: Optional[uuid.UUID] = Field(sa_column=Column(pg.UUID, nullable=True))

    # Loại tham chiếu: goods_receipt, order, purchase_return, adjustment, damaged
    reference_type: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))

    # Lý do thực hiện giao dịch
    reason: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    note: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    # Nhân viên/ai đã thực hiện giao dịch
    performed_by: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)

    warehouse: Optional["Warehouse"] = Relationship(back_populates="stock_transactions", sa_relationship_kwargs={'lazy': 'noload'})
    stock: Optional["Stock"] = Relationship(back_populates="stock_transactions", sa_relationship_kwargs={'lazy': 'noload'})
    product_variant: Optional["Product_Variant"] = Relationship(sa_relationship_kwargs={'lazy': 'noload'})
    user: Optional["User"] = Relationship(sa_relationship_kwargs={'lazy': 'noload'})


class Stock(SQLModel, table=True):
    """Tồn kho theo từng sản phẩm variant trên từng kho"""
    __tablename__ = 'stock'
    __table_args__ = (
        UniqueConstraint(
            "warehouse_id", "product_variant_id",
            name="uq_stock_warehouse_product_variant"
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

    warehouse_id: uuid.UUID = Field(foreign_key="warehouse.id", nullable=False)
    product_variant_id: uuid.UUID = Field(foreign_key="product_variant.id", nullable=False)

    # Tổng số lượng thực tế trong kho
    quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False, server_default="0"), default=0)

    # Số lượng đã giữ cho đơn hàng chưa hoàn tất (đã đặt nhưng chưa xuất)
    reserved_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False, server_default="0"), default=0)

    # Số lượng có thể bán = quantity - reserved_quantity
    available_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False, server_default="0"), default=0)

    # Mức tồn kho tối thiểu - cảnh báo khi còn ít hơn mức này
    min_stock_level: Optional[int] = Field(sa_column=Column(pg.INTEGER, nullable=True), default=0)

    # Mức tồn kho tối đa - cảnh báo khi vượt ngưỡng (tránh ứ đọng)
    max_stock_level: Optional[int] = Field(sa_column=Column(pg.INTEGER, nullable=True))

    # Giá vốn trung bình bình quân gia quyền (weighted average cost)
    cost_price: Optional[int] = Field(sa_column=Column(pg.INTEGER, nullable=True))

    # Giá vốn của lần nhập gần nhất
    last_cost_price: Optional[int] = Field(sa_column=Column(pg.INTEGER, nullable=True))

    # available (có thể bán), low_stock (sắp hết), out_of_stock (hết hàng), discontinued (ngừng kinh doanh)
    status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="available"), default="available")

    # Thời điểm nhập hàng gần nhất
    last_inbound_date: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    # Thời điểm xuất hàng gần nhất
    last_outbound_date: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    warehouse: Optional["Warehouse"] = Relationship(back_populates="stocks", sa_relationship_kwargs={'lazy': 'noload'})
    product_variant: Optional["Product_Variant"] = Relationship(sa_relationship_kwargs={'lazy': 'noload'})
    stock_transactions: List["StockTransaction"] = Relationship(back_populates="stock", sa_relationship_kwargs={'lazy': 'noload'})


class Warehouse(SQLModel, table=True):
    """Kho hàng"""
    __tablename__ = 'warehouse'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    code: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, unique=True))
    address: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    phone: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    email: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))

    manager_id: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)

    is_active: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default="true"), default=True)
    # Có phải là kho mặc định không
    is_default: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default="false"), default=False)

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    manager: Optional["User"] = Relationship(
        back_populates="managed_warehouses",
        sa_relationship_kwargs={
            'lazy': 'noload',
            'foreign_keys': '[Warehouse.manager_id]'
        }
    )
    staff_members: List["User"] = Relationship(
        back_populates="warehouse",
        sa_relationship_kwargs={
            'lazy': 'noload',
            'foreign_keys': '[User.warehouse_id]'
        }
    )

    stocks: List["Stock"] = Relationship(back_populates="warehouse", sa_relationship_kwargs={'lazy': 'noload'})
    stock_transactions: List["StockTransaction"] = Relationship(back_populates="warehouse", sa_relationship_kwargs={'lazy': 'noload'})


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
    staff_status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="active"), default="active")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    deleted_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    is_verified: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default=text("false")), default=False)
    is_admin: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default=text("false")), default=False)
    is_customer: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default=text("false")), default=False)
    is_staff: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default=text("false")), default=False)
    two_fa_secret: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    two_fa_enabled: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default=text("false")), default=False)
    otp_hash: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    otp_attempts: Optional[int] = Field(sa_column=Column(pg.INTEGER, nullable=True), default=0)
    expires_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    warehouse_id: Optional[uuid.UUID] = Field(foreign_key="warehouse.id", nullable=True, default=None)
    warehouse_role: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))  # "manager", "staff", "picker", "checker"

    address: List["Address"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy': 'noload'})
    order: List["Order"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy': 'noload'})
    evaluate: List["Evaluate"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy': 'noload'})
    cash_transactions: List["CashTransaction"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy': 'noload'})
    user_special_offer: List["UserSpecialOffer"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={'lazy': 'noload'}
    )
    managed_warehouses: List["Warehouse"] = Relationship(
        back_populates="manager",
        sa_relationship_kwargs={
            'lazy': 'noload',
            'foreign_keys': '[Warehouse.manager_id]'
        }
    )
    warehouse: Optional["Warehouse"] = Relationship(
        back_populates="staff_members",
        sa_relationship_kwargs={
            'lazy': 'noload',
            'foreign_keys': '[User.warehouse_id]'
        }
    )


class CashTransaction(SQLModel, table=True):
    """Giao dịch thu chi tiền mặt"""
    __tablename__ = 'cash_transaction'

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    )

    # Mã giao dịch: VD: CT001, CT002
    transaction_code: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, unique=True))

    # Loại giao dịch: inflow (thu), outflow (chi), transfer (chuyển khoản nội bộ)
    transaction_type: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))

    # Danh mục giao dịch:
    # - revenue (doanh thu bán hàng)
    # - purchase (chi phí mua hàng)
    # - loan (vay/trả nợ)
    # - refund (hoàn trả)
    # - other (khác)
    category: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))

    # Số tiền giao dịch (luôn dương)
    amount: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Ngày giao dịch
    transaction_date: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False), default=datetime.now)

    # Đối tượng giao dịch (khách hàng, nhà cung cấp, nhân viên...)
    reference_type: Optional[str] = Field(
        sa_column=Column(pg.VARCHAR, nullable=True))  # customer, supplier, employee, other
    reference_id: Optional[uuid.UUID] = Field(sa_column=Column(pg.UUID, nullable=True))
    reference_name: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))

    # Phương thức thanh toán: cash, bank_transfer, card, e_wallet
    payment_method: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))

    # Ghi chú thêm
    notes: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    # Người thực hiện giao dịch
    performed_by: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)

    user: Optional["User"] = Relationship(back_populates="cash_transactions", sa_relationship_kwargs={'lazy': 'noload'})


class SupplierPayment(SQLModel, table=True):
    """Thanh toán cho nhà cung cấp"""
    __tablename__ = 'supplier_payment'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    payment_number: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, unique=True))  # SP001, SP002...

    supplier_id: uuid.UUID = Field(foreign_key="supplier.id", nullable=False)
    purchase_order_id: uuid.UUID = Field(foreign_key="purchase_order.id", nullable=False)

    # Ngày thực hiện thanh toán (ngày bạn chuyển tiền hoặc ghi nhận trong sổ).
    payment_date: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False), default=datetime.now)

    # Số tiền thanh toán cho nhà cung cấp (đơn vị: đồng). Đây là số tiền thật bạn trả, không nhất thiết phải bằng tổng PO.
    amount: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # "cash" → tiền mặt     "bank_transfer" → chuyển khoản
    payment_method: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))

    reference_number: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))  # Mã giao dịch ngân hàng

    # pending, completed, cancelled
    status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="pending"), default="pending")

    notes: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    created_by: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)
    approved_by: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    approved_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    supplier: Optional["Supplier"] = Relationship(back_populates="supplier_payments", sa_relationship_kwargs={'lazy': 'noload'})
    purchase_order: Optional["PurchaseOrder"] = Relationship(back_populates="supplier_payments", sa_relationship_kwargs={'lazy': 'noload'})


class PurchaseReturn(SQLModel, table=True):
    """Phiếu trả hàng cho nhà cung cấp"""
    __tablename__ = 'purchase_return'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    # Mã phiếu trả hàng. VD: PR001, PR002...
    return_number: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, unique=True))

    # Liên kết với đơn đặt hàng ban đầu
    purchase_order_id: uuid.UUID = Field(foreign_key="purchase_order.id", nullable=False)

    # Liên kết với phiếu nhập kho (nếu trả hàng từ một phiếu nhập cụ thể)
    goods_receipt_id: Optional[uuid.UUID] = Field(foreign_key="goods_receipt.id", nullable=True)

    # Nhà cung cấp nhận hàng trả
    supplier_id: uuid.UUID = Field(foreign_key="supplier.id", nullable=False)

    # Kho xuất hàng trả
    warehouse_id: uuid.UUID = Field(foreign_key="warehouse.id", nullable=False)

    # Trạng thái: draft, approved, completed, rejected
    status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="draft"), default="draft")

    # Loại trả hàng: return_to_supplier (trả về NCC), exchange (đổi hàng), refund (hoàn tiền)
    return_type: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="return_to_supplier"),
                             default="return_to_supplier")

    # Ngày tạo phiếu trả hàng
    return_date: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False), default=datetime.now)

    # Ngày thực tế gửi hàng trả về cho NCC
    shipped_date: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    # Tổng giá trị hàng trả
    total_return_amount: int = Field(sa_column=Column(pg.INTEGER, nullable=False), default=0)

    # Số tiền NCC đồng ý hoàn lại (có thể khác total_return_amount do phí xử lý, khấu trừ...)
    refund_amount: int = Field(sa_column=Column(pg.INTEGER, nullable=False), default=0)

    # Lý do trả hàng chung
    return_reason: str = Field(sa_column=Column(pg.TEXT, nullable=False))

    # Số phiếu giao nhận trả hàng (do NCC cung cấp khi nhận hàng trả)
    delivery_note_number: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))

    # Nhân viên tạo phiếu trả hàng
    created_by: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)

    # Nhân viên duyệt phiếu trả
    approved_by: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)

    # Nhân viên nhận hàng
    confirmed_by: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)

    completed_by: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)

    notes: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    approved_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    confirmed_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    completed_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    # Relationships
    purchase_order: Optional["PurchaseOrder"] = Relationship(back_populates="purchase_returns",
                                                             sa_relationship_kwargs={'lazy': 'noload'})
    goods_receipt: Optional["GoodsReceipt"] = Relationship(back_populates="purchase_returns",
                                                           sa_relationship_kwargs={'lazy': 'noload'})
    supplier: Optional["Supplier"] = Relationship(back_populates="purchase_returns",
                                                  sa_relationship_kwargs={'lazy': 'noload'})
    warehouse: Optional["Warehouse"] = Relationship(sa_relationship_kwargs={'lazy': 'noload'})
    return_details: List["PurchaseReturnDetail"] = Relationship(back_populates="purchase_return",
                                                                sa_relationship_kwargs={'lazy': 'noload'})


class PurchaseReturnDetail(SQLModel, table=True):
    """Chi tiết phiếu trả hàng cho nhà cung cấp"""
    __tablename__ = 'purchase_return_detail'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    # Thuộc phiếu trả hàng nào
    purchase_return_id: uuid.UUID = Field(foreign_key="purchase_return.id", nullable=False)

    # Sản phẩm biến thể nào được trả
    product_variant_id: uuid.UUID = Field(foreign_key="product_variant.id", nullable=False)

    # Liên kết với chi tiết phiếu nhập kho ban đầu (nếu có)
    goods_receipt_detail_id: Optional[uuid.UUID] = Field(foreign_key="goods_receipt_detail.id", nullable=True)

    # Số lượng trả lại cho nhà cung cấp
    return_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Giá nhập ban đầu của sản phẩm (từ phiếu nhập)
    unit_cost: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Tổng giá trị trả = return_quantity * unit_cost
    total_cost: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Tình trạng hàng trả: damaged (hư hỏng), defective (lỗi), expired (hết hạn), wrong_item (sai hàng)
    condition: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))

    # Lưu bản sao thông tin sản phẩm tại thời điểm trả hàng
    product_snapshot: Optional[dict] = Field(sa_column=Column(JSONB, nullable=True))

    # Hình ảnh/chứng từ về hàng reject
    rejection_evidence: Optional[List[str]] = Field(sa_column=Column(JSONB, nullable=True), default=None)

    notes: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)

    # Relationships
    purchase_return: Optional["PurchaseReturn"] = Relationship(back_populates="return_details",
                                                               sa_relationship_kwargs={'lazy': 'noload'})
    product_variant: Optional["Product_Variant"] = Relationship(sa_relationship_kwargs={'lazy': 'noload'})
    goods_receipt_detail: Optional["GoodsReceiptDetail"] = Relationship(sa_relationship_kwargs={'lazy': 'noload'})


class GoodsReceiptDetail(SQLModel, table=True):
    """Chi tiết phiếu nhập kho"""
    __tablename__ = 'goods_receipt_detail'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    goods_receipt_id: uuid.UUID = Field(foreign_key="goods_receipt.id", nullable=False)
    product_variant_id: uuid.UUID = Field(foreign_key="product_variant.id", nullable=False)
    po_detail_id: uuid.UUID = Field(foreign_key="purchase_order_detail.id", nullable=False)

    # Số lượng đặt hàng ban đầu trong PO (nếu có). Chỉ để đối chiếu, không bắt buộc
    ordered_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Số lượng thực tế nhận được từ nhà cung cấp (ví dụ giao 100 cái)
    received_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Số lượng chấp nhận nhập kho sau khi kiểm hàng (ví dụ nhận 100 nhưng chỉ 95 đạt chất lượng)
    accepted_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Số lượng từ chối nhập (hàng lỗi, hư, sai mẫu...). Thường = received_quantity - accepted_quantity
    rejected_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False), default=0)

    # Số lượng đã hoàn trả (tổng cộng qua các phiếu hoàn)
    returned_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False), default=0)

    # Giá nhập trên mỗi đơn vị hàng hóa (theo hóa đơn hoặc PO)
    unit_cost: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Thành tiền trước giảm giá = accepted_quantity * unit_cost.
    total_cost: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    rejection_reason: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    # Lưu bản sao JSON thông tin sản phẩm tại thời điểm nhập hàng (ví dụ: tên, SKU, đơn vị tính, giá tại thời điểm đó).
    product_snapshot: Optional[dict] = Field(sa_column=Column(JSONB, nullable=True))

    notes: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)

    # Relationships
    goods_receipt: Optional["GoodsReceipt"] = Relationship(back_populates="receipt_details", sa_relationship_kwargs={'lazy': 'noload'})
    product_variant: Optional["Product_Variant"] = Relationship(sa_relationship_kwargs={'lazy': 'noload'})
    po_detail: Optional["PurchaseOrderDetail"] = Relationship(sa_relationship_kwargs={'lazy': 'noload'})


class GoodsReceipt(SQLModel, table=True):
    """Phiếu nhập kho thực tế"""
    __tablename__ = 'goods_receipt'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    # Mã phiếu nhập. VD: GR001, GR002...
    receipt_number: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, unique=True))

    # Liên kết với đơn đặt hàng tương ứng
    purchase_order_id: uuid.UUID = Field(foreign_key="purchase_order.id", nullable=False)

    # Kho hàng nơi nhập hàng vào
    warehouse_id: uuid.UUID = Field(foreign_key="warehouse.id", nullable=False)
    supplier_id: uuid.UUID = Field(foreign_key="supplier.id", nullable=False)

    parent_receipt_id: Optional[uuid.UUID] = Field(foreign_key="goods_receipt.id", nullable=True, default=None)

    # pending, approved, rejected, completed
    status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="pending"), default="pending")

    # Ngày nhận hàng thực tế (do nhà cung cấp giao đến).
    receipt_date: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False), default=datetime.now)

    # Tổng giá trị hàng nhập thực tế (tính từ GoodsReceiptDetail, có thể khác PO).
    total_received_amount: int = Field(sa_column=Column(pg.INTEGER, nullable=False), default=0)

    # Số phiếu giao hàng (do NCC phát hành kèm theo lô hàng).
    delivery_note_number: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))

    received_by: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)  # Nhân viên trực tiếp nhận hàng tại kho
    inspected_by: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)  # Nhân viên kiểm tra chất lượng hàng nhập
    approved_by: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)  # Người duyệt

    # Cờ báo có sự sai lệch giữa hàng nhận và hàng đặt
    has_discrepancy: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default="false"), default=False)

    # Ghi chú chi tiết về sự sai lệch
    discrepancy_notes: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    # Ghi chú chung (ví dụ: nhập gấp, hàng khuyến mãi...).
    notes: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    received_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False), default=datetime.now)
    inspected_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    approved_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    completed_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    # Relationships
    purchase_order: Optional["PurchaseOrder"] = Relationship(back_populates="goods_receipts", sa_relationship_kwargs={'lazy': 'noload'})
    warehouse: Optional["Warehouse"] = Relationship(sa_relationship_kwargs={'lazy': 'noload'})
    supplier: Optional["Supplier"] = Relationship(back_populates="goods_receipts", sa_relationship_kwargs={'lazy': 'noload'})
    receipt_details: List["GoodsReceiptDetail"] = Relationship(back_populates="goods_receipt", sa_relationship_kwargs={'lazy': 'noload'})
    purchase_returns: List["PurchaseReturn"] = Relationship(back_populates="goods_receipt", sa_relationship_kwargs={'lazy': 'noload'})


class PurchaseOrderDetail(SQLModel, table=True):
    """Chi tiết đơn đặt hàng"""
    __tablename__ = 'purchase_order_detail'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    # Chi tiết này thuộc đơn đặt hàng nào.
    purchase_order_id: uuid.UUID = Field(foreign_key="purchase_order.id", nullable=False)

    # Biến thể nào của sản phẩm.
    product_variant_id: uuid.UUID = Field(foreign_key="product_variant.id", nullable=False)

    # Số lượng đặt hàng từ nhà cung cấp.
    quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Số lượng đã nhận thực tế qua các phiếu nhập hàng (GoodsReceipt).
    received_quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False, server_default="0"), default=0)

    # Giá mua của một đơn vị sản phẩm (chưa tính chiết khấu)
    unit_cost: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Tổng tiền
    total_cost: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # Lưu thông tin sản phẩm tại thời điểm đặt
    product_snapshot: Optional[dict] = Field(sa_column=Column(JSONB, nullable=True))

    notes: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)

    # Relationships
    purchase_order: Optional["PurchaseOrder"] = Relationship(back_populates="po_details", sa_relationship_kwargs={'lazy': 'noload'})
    product_variant: Optional["Product_Variant"] = Relationship(sa_relationship_kwargs={'lazy': 'noload'})


class PurchaseOrder(SQLModel, table=True):
    """Đơn đặt hàng từ nhà cung cấp"""
    __tablename__ = 'purchase_order'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    # Mã số đơn đặt hàng, VD: PO001, PO002,...
    po_number: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, unique=True))

    # ID của nhà cung cấp (Supplier) → biết đơn này đặt từ ai.
    supplier_id: uuid.UUID = Field(foreign_key="supplier.id", nullable=False)

    # ID của kho (Warehouse) sẽ nhập hàng về.
    warehouse_id: uuid.UUID = Field(foreign_key="warehouse.id", nullable=False)

    # Trạng thái xử lý đơn hàng: draft, sent, confirmed, completed, cancelled
    status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="draft"), default="draft")

    # Ngày tạo đơn đặt hàng
    order_date: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False), default=datetime.now)

    # Ngày dự kiến NCC giao hàng
    expected_delivery_date: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    # Tổng tiền hàng (chưa tính giảm giá, vận chuyển)
    sub_total: int = Field(sa_column=Column(pg.INTEGER, nullable=False), default=0)
    discount_amount: int = Field(sa_column=Column(pg.INTEGER, nullable=False), default=0)
    shipping_cost: int = Field(sa_column=Column(pg.INTEGER, nullable=False), default=0)

    # Tổng số tiền mà doanh nghiệp phải trả cho đơn hàng = sub_total + shipping_cost - discount_amount
    total_amount: int = Field(sa_column=Column(pg.INTEGER, nullable=False), default=0)

    # unpaid, partially_paid, paid
    payment_status: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="unpaid"), default="unpaid")

    # Số tiền mình trả. Trả thiếu thì payment_status = "partially_paid", trả đủ thì payment_status = "paid"
    paid_amount: int = Field(sa_column=Column(pg.INTEGER, nullable=False, server_default="0"), default=0)

    notes: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    supplier_invoice_urls: Optional[List[str]] = Field(sa_column=Column(JSONB, nullable=True), default=None)

    created_by: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)
    approved_by: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True)

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    approved_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    sent_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    confirmed_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    completed_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    cancelled_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))
    cancellation_reason: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    # Relationships
    supplier: Optional["Supplier"] = Relationship(back_populates="purchase_orders", sa_relationship_kwargs={'lazy': 'noload'})
    warehouse: Optional["Warehouse"] = Relationship(sa_relationship_kwargs={'lazy': 'noload'})
    po_details: List["PurchaseOrderDetail"] = Relationship(back_populates="purchase_order", sa_relationship_kwargs={'lazy': 'noload'})
    goods_receipts: List["GoodsReceipt"] = Relationship(back_populates="purchase_order", sa_relationship_kwargs={'lazy': 'noload'})
    supplier_payments: List["SupplierPayment"] = Relationship(back_populates="purchase_order", sa_relationship_kwargs={'lazy': 'noload'})
    purchase_returns: List["PurchaseReturn"] = Relationship(back_populates="purchase_order", sa_relationship_kwargs={'lazy': 'noload'})


class Supplier(SQLModel, table=True):
    """Nhà cung cấp"""
    __tablename__ = 'supplier'

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    code: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, unique=True))
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))

    contact_person: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    phone: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    email: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    address: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    # Số tài khoản ngân hàng mà NCC cung cấp để thanh toán.
    bank_account: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    bank_name: Optional[str] = Field(sa_column=Column(pg.VARCHAR, nullable=True))

    # Hạn mức công nợ tối đa mà NCC cho phép (VD: 100,000,000 VND)
    credit_limit: Optional[int] = Field(sa_column=Column(pg.INTEGER, nullable=True))

    # Công nợ hiện tại mà doanh nghiệp còn nợ NCC
    current_debt: int = Field(sa_column=Column(pg.INTEGER, nullable=False, server_default="0"), default=0)

    # Trạng thái NCC còn đang hợp tác hay đã ngưng
    is_active: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, server_default="true"), default=True)

    notes: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")), default=datetime.now)
    updated_at: Optional[datetime] = Field(sa_column=Column(pg.TIMESTAMP, nullable=True))

    purchase_orders: List["PurchaseOrder"] = Relationship(back_populates="supplier", sa_relationship_kwargs={'lazy': 'noload'})
    goods_receipts: List["GoodsReceipt"] = Relationship(back_populates="supplier", sa_relationship_kwargs={'lazy': 'noload'})
    supplier_payments: List["SupplierPayment"] = Relationship(back_populates="supplier", sa_relationship_kwargs={'lazy': 'noload'})
    purchase_returns: List["PurchaseReturn"] = Relationship(back_populates="supplier", sa_relationship_kwargs={'lazy': 'noload'})
    products: List["Product"] = Relationship(back_populates="suppliers", link_model=Supplier_Product, sa_relationship_kwargs={'lazy': 'noload'})
    supplier_products: List["Supplier_Product"] = Relationship(back_populates="suppliers", sa_relationship_kwargs={'lazy': 'noload'})


class LoginAttempt(SQLModel, table=True):
    __tablename__ = 'login_attempts'

    __table_args__ = (
        Index('idx_email_attempted_at', 'email', 'attempted_at'),
        Index('idx_ip_attempted_at', 'ip_address', 'attempted_at'),
    )

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    email: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, index=True))
    ip_address: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    is_successful: bool = Field(
        sa_column=Column(pg.BOOLEAN, nullable=False, server_default=text("false")),
        default=False
    )
    attempted_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), index=True),
        default=datetime.now
    )


class Setup2FAAttempt(SQLModel, table=True):
    __tablename__ = 'setup_2fa_attempts'

    __table_args__ = (
        Index('idx_user_id_attempted_at', 'user_id', 'attempted_at'),
    )

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    is_successful: bool = Field(
        sa_column=Column(pg.BOOLEAN, nullable=False, server_default=text("false")),
        default=False
    )
    attempted_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), index=True),
        default=datetime.now
    )


class OTPVerificationAttempt(SQLModel, table=True):
    __tablename__ = 'otp_verification_attempts'

    __table_args__ = (
        Index('idx_otp_user_id_attempted_at', 'user_id', 'attempted_at'),
        Index('idx_otp_ip_attempted_at', 'ip_address', 'attempted_at'),
    )

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    ip_address: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    is_successful: bool = Field(
        sa_column=Column(pg.BOOLEAN, nullable=False, server_default=text("false")),
        default=False
    )
    attempted_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), index=True),
        default=datetime.now
    )











