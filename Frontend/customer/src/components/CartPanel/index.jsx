import Button from "@mui/material/Button";
import React, { useContext, useEffect, useState } from "react";
import { MdOutlineDeleteOutline } from "react-icons/md";
import { Link, useNavigate } from "react-router-dom";
import { deleteDataApi, getDataApi } from "../../utils/api";
import toast from "react-hot-toast";
import { MyContext } from "../../App";

const CartPanel = () => {
    const [cartData, setCartData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [loadingMore, setLoadingMore] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const [page, setPage] = useState(1);
    const [allVariants, setAllVariants] = useState([]);
    const [isDeleting, setIsDeleting] = useState(new Set());
    const [quantities, setQuantities] = useState({});
    const [selectedVariants, setSelectedVariants] = useState(new Set());

    const { addItemsToCheckout, setOpenCartPanel } = useContext(MyContext);
    const navigate = useNavigate();

    const getCurrentQuantity = (cartItemId, originalQuantity) => {
        return quantities[cartItemId] !== undefined ? quantities[cartItemId] : originalQuantity;
    };

    const updateQuantity = (cartItemId, newQuantity) => {
        if (newQuantity < 1) return;
        setQuantities(prev => ({
            ...prev,
            [cartItemId]: newQuantity
        }));
    };

    const QuantityControls = ({ variant }) => {
        const currentQty = getCurrentQuantity(variant.cart_item_id, variant.quantity);

        return (
            <div className="flex items-center gap-2">
                <button
                    onClick={() => updateQuantity(variant.cart_item_id, currentQty - 1)}
                    disabled={currentQty <= 1}
                    className="w-6 h-6 flex items-center justify-center bg-gray-200 rounded text-sm hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    -
                </button>
                <span className="mx-2 min-w-[30px] text-center">{currentQty}</span>
                <button
                    onClick={() => updateQuantity(variant.cart_item_id, currentQty + 1)}
                    disabled={currentQty >= variant.max_quantity}
                    className="w-6 h-6 flex items-center justify-center bg-gray-200 rounded text-sm hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    +
                </button>
            </div>
        );
    };

    const fetchCartData = async (pageNum = 1, append = false) => {
        if (pageNum === 1) {
            setLoading(true);
        } else {
            setLoadingMore(true);
        }

        try {
            const response = await getDataApi(`/customer/cart/?skip=${(pageNum - 1) * 30}&limit=30`);
            if (response.success) {
                if (pageNum === 1) {
                    setCartData(response.data);
                    setAllVariants(response.data.products || []);
                } else {
                    setAllVariants(prev => [...prev, ...(response.data.products || [])]);
                }

                const totalVariants = response.data.products?.reduce((sum, product) => sum + product.variants.length, 0) || 0;
                setHasMore(totalVariants === 30);
            } else {
                console.error('Failed to fetch cart:', response.message);
            }
        } catch (error) {
            console.error('Error fetching cart:', error);
        } finally {
            setLoading(false);
            setLoadingMore(false);
        }
    };

    const handleScroll = (e) => {
        const { scrollTop, scrollHeight, clientHeight } = e.target;

        if (scrollHeight - scrollTop === clientHeight && hasMore && !loadingMore) {
            const nextPage = page + 1;
            setPage(nextPage);
            fetchCartData(nextPage, true);
        }
    };

    useEffect(() => {
        fetchCartData(1);
    }, []);

    const getColorDisplay = (variant) => {
        if (variant.color_name) {
            return variant.color_name;
        }
        return null;
    };

    const isVariantSelected = (cartItemId) => {
        return selectedVariants.has(cartItemId);
    };

    const isProductFullySelected = (product) => {
        return product.variants.every(variant => selectedVariants.has(variant.cart_item_id));
    };

    const isProductPartiallySelected = (product) => {
        return product.variants.some(variant => selectedVariants.has(variant.cart_item_id)) &&
            !isProductFullySelected(product);
    };

    const handleDeleteItem = async (itemId) => {
        await handleDeleteItems([itemId]);
    };

    const handleDeleteItems = async (itemIds) => {
        setIsDeleting(prev => new Set([...prev, ...itemIds]));

        try {
            const response = await deleteDataApi('/customer/cart/', {
                item_ids: itemIds
            });

            if (response.success) {
                const { deleted_count, invalid_count } = response.data;

                if (invalid_count && invalid_count > 0) {
                    toast.warning(`Có ${invalid_count} sản phẩm không thể xóa`);
                }

                setSelectedVariants(prev => {
                    const newSet = new Set(prev);
                    itemIds.forEach(id => newSet.delete(id));
                    return newSet;
                });

                setQuantities(prev => {
                    const newQty = { ...prev };
                    itemIds.forEach(id => delete newQty[id]);
                    return newQty;
                });

                await fetchCartData(1);
            } else {
                toast.error(response.message || 'Không thể xóa sản phẩm');
            }
        } catch (error) {
            console.error('Delete items error:', error);
            toast.error('Có lỗi xảy ra');
        } finally {
            setIsDeleting(prev => {
                const newSet = new Set(prev);
                itemIds.forEach(id => newSet.delete(id));
                return newSet;
            });
        }
    };

    const handleDeleteSelected = async () => {
        if (selectedVariants.size === 0) {
            toast.warning('Vui lòng chọn sản phẩm cần xóa');
            return;
        }

        const selectedIds = Array.from(selectedVariants);
        await handleDeleteItems(selectedIds);
    };

    const toggleVariant = (cartItemId) => {
        setSelectedVariants(prev => {
            const newSet = new Set(prev);
            if (newSet.has(cartItemId)) {
                newSet.delete(cartItemId);
            } else {
                newSet.add(cartItemId);
            }
            return newSet;
        });
    };

    const toggleProduct = (product) => {
        setSelectedVariants(prev => {
            const newSet = new Set(prev);
            const isFullySelected = product.variants.every(variant => newSet.has(variant.cart_item_id));

            if (isFullySelected) {
                product.variants.forEach(variant => {
                    newSet.delete(variant.cart_item_id);
                });
            } else {
                product.variants.forEach(variant => {
                    newSet.add(variant.cart_item_id);
                });
            }
            return newSet;
        });
    };

    const getTotalPrice = () => {
        return allVariants.reduce((total, product) =>
            total + product.variants.reduce((sum, variant) => {
                if (selectedVariants.has(variant.cart_item_id)) {
                    return sum + (variant.unit_price * getCurrentQuantity(variant.cart_item_id, variant.quantity));
                }
                return sum;
            }, 0), 0
        );
    };

    const handleCheckout = () => {
        if (selectedVariants.size === 0) {
            toast.warning('Vui lòng chọn sản phẩm cần mua');
            return;
        }

        const selectedItems = [];
        allVariants.forEach(product => {
            product.variants.forEach(variant => {
                if (selectedVariants.has(variant.cart_item_id)) {
                    selectedItems.push({
                        ...variant,
                        product_name: product.product_name,
                        product_id: product.product_id,
                        quantity: getCurrentQuantity(variant.cart_item_id, variant.quantity),
                        color_name: getColorDisplay(variant)
                    });
                }
            });
        });

        const totalPrice = getTotalPrice();

        addItemsToCheckout(selectedItems, totalPrice);

        setOpenCartPanel(false);

        navigate('/cart');
    };

    return (
        <>
            <div className='scroll w-full max-h-[800px] overflow-y-scroll overflow-x-hidden py-3 px-4' onScroll={handleScroll}>
                {loading ? (
                    <div className="text-center py-4">Đang tải...</div>
                ) : !cartData || !allVariants || allVariants.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                        Giỏ hàng trống
                    </div>
                ) : (
                    <>
                        {allVariants.map((product) => (
                            <div key={product.product_id} className="product-group mb-6">
                                <div className="product-header mb-3 pb-2 border-b-2 border-gray-200 flex items-center gap-3">
                                    <div className="relative">
                                        <input
                                            type="checkbox"
                                            checked={isProductFullySelected(product)}
                                            ref={checkbox => {
                                                if (checkbox) checkbox.indeterminate = isProductPartiallySelected(product);
                                            }}
                                            onChange={() => toggleProduct(product)}
                                            className="w-4 h-4 accent-[#ff5252] cursor-pointer"
                                        />
                                    </div>
                                    <h3 className="text-[16px] font-[600] text-gray-800">
                                        <Link to={`/product/${product.product_id}`} className="link transition-all">
                                            {product.product_name}
                                        </Link>
                                    </h3>
                                </div>

                                <div className="variants-list">
                                    {product.variants.map((variant, index) => {
                                        const colorName = getColorDisplay(variant);

                                        return (
                                            <div key={variant.cart_item_id} className={`cartItem w-full flex items-center gap-4 pb-4 mb-4 ${index < product.variants.length - 1 ? 'border-b border-gray-100' : ''}`}>
                                                <div className="flex items-center">
                                                    <input
                                                        type="checkbox"
                                                        checked={isVariantSelected(variant.cart_item_id)}
                                                        onChange={() => toggleVariant(variant.cart_item_id)}
                                                        className="w-4 h-4 mr-3 accent-[#ff5252] cursor-pointer"
                                                    />
                                                </div>

                                                <div className="img w-[25%] overflow-hidden h-[80px] rounded-md">
                                                    <img
                                                        src={variant.image || '/default-product.jpg'}
                                                        alt={`${product.product_name} - ${variant.size} ${colorName}`}
                                                        className='w-full h-full object-cover'
                                                    />
                                                </div>

                                                <div className='info w-[75%] pr-5 relative'>
                                                    <div className="text-[13px] text-gray-600 mb-2 flex gap-3">
                                                        {variant.size && <span>Size: <strong>{variant.size}</strong></span>}
                                                        {colorName && <span>Màu: <strong>{colorName}</strong></span>}
                                                    </div>

                                                    <div className="flex items-center justify-between mb-2">
                                                        <div className="flex items-center gap-2">
                                                            <span className="text-[12px] text-gray-500">Số lượng:</span>
                                                            <QuantityControls variant={variant} />
                                                        </div>
                                                        <div className="text-right">
                                                            <div className="text-[14px] text-[#ff5252] font-bold">
                                                                {variant.unit_price?.toLocaleString('vi-VN')}đ
                                                            </div>
                                                            <div className="text-[12px] text-gray-500">
                                                                Tổng: {(variant.unit_price * getCurrentQuantity(variant.cart_item_id, variant.quantity))?.toLocaleString('vi-VN')}đ
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <MdOutlineDeleteOutline
                                                        className={`absolute top-[5px] right-[5px] cursor-pointer text-[18px] link transition-all ${isDeleting.has(variant.cart_item_id) ? 'opacity-50 cursor-not-allowed' : ''
                                                            }`}
                                                        onClick={() => !isDeleting.has(variant.cart_item_id) && handleDeleteItem(variant.cart_item_id)}
                                                    />
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        ))}

                        {loadingMore && (
                            <div className="text-center py-4 text-gray-500">
                                Đang tải thêm...
                            </div>
                        )}
                    </>
                )}
            </div>

            <br />

            <div className="bottomInfo py-3 px-4 w-full border-t border-[rgba(0,0,0,0.1)]">
                <div className="flex items-center justify-between w-full mb-3">
                    <div className="flex items-center gap-4">
                        <span className="text-[#ff5252] font-bold text-[16px]">
                            Tổng: {getTotalPrice()?.toLocaleString('vi-VN')}đ
                        </span>
                        {selectedVariants.size > 0 && (
                            <span className="text-sm text-gray-600">
                                ({selectedVariants.size} sản phẩm được chọn)
                            </span>
                        )}
                    </div>
                    <div className="flex gap-2">
                        {selectedVariants.size > 0 && (
                            <button
                                onClick={handleDeleteSelected}
                                disabled={isDeleting.size > 0}
                                className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md font-[500] transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                Xóa đã chọn
                            </button>
                        )}
                        <button
                            onClick={handleCheckout}
                            disabled={selectedVariants.size === 0}
                            className="bg-[#ff5252] hover:bg-[#e53e3e] text-white px-6 py-2 rounded-md font-[500] transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Mua hàng
                        </button>
                    </div>
                </div>
            </div>
        </>
    )
}

export default CartPanel