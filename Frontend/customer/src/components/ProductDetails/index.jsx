import { Rating } from "@mui/material";
import React, { useContext, useState } from "react";
import Button from "@mui/material/Button"
import QtyBox from "../../components/QtyBox";
import { MdOutlineShoppingCart } from "react-icons/md";
import { FaRegHeart } from "react-icons/fa";
import { IoGitCompareOutline } from "react-icons/io5";
import { getDataApi, postDataApi } from "../../utils/api";
import toast from "react-hot-toast";
import { MyContext } from "../../App";

const ProductDetailsComponent = ({ product, onProductUpdated }) => {
    const [selectedVariantIndex, setSelectedVariantIndex] = useState(0);
    const [selectedSize, setSelectedSize] = useState('');
    const [selectedColor, setSelectedColor] = useState('');
    const [quantity, setQuantity] = useState(1);
    const [isAddingToCart, setIsAddingToCart] = useState(false);
    const [animatingImage, setAnimatingImage] = useState(null);

    const context = useContext(MyContext)

    if (!product) {
        return (
            <div className="text-center py-8">
                <div className="text-lg text-gray-500">Không có thông tin sản phẩm</div>
            </div>
        );
    }

    const getColorIdentifier = (color) => color.id || `custom_${color.name}`;

    const formatPrice = (price) => {
        if (!price) return 'N/A';
        return `${price.toLocaleString('vi-VN')}đ`;
    };

    const roundRating = (rating) => {
        if (rating === null || rating === undefined) return 0;

        const decimal = rating - Math.floor(rating);

        if (decimal >= 0.75) {
            return Math.ceil(rating);
        } else if (decimal >= 0.25) {
            return Math.floor(rating) + 0.5;
        } else {
            return Math.floor(rating);
        }
    };

    const availableSizes = [...new Set(product.product_variant?.map(v => v.size).filter(Boolean))];
    const availableColors = product.product_variant?.reduce((acc, variant) => {
        if ((variant.color_id || variant.color_name) && !acc.find(c =>
            (c.id === variant.color_id) || (c.id === null && c.name === variant.color_name)
        )) {
            acc.push({
                id: variant.color_id,
                name: variant.color_name,
                code: variant.color_code,
                image: variant.image
            });
        }
        return acc;
    }, []) || [];

    const getSelectedVariant = () => {
        if (!product.product_variant || product.product_variant.length === 0) return null;

        if (selectedSize && selectedColor !== '') {
            const variant = product.product_variant.find(v => {
                const sizeMatch = v.size === selectedSize;
                let colorMatch = false;

                if (selectedColor.startsWith('custom_')) {
                    const colorName = selectedColor.replace('custom_', '');
                    colorMatch = v.color_name === colorName && !v.color_id;
                } else {
                    colorMatch = v.color_id === selectedColor;
                }

                return sizeMatch && colorMatch;
            });
            if (variant) {
                return variant;
            }
        }

        if (selectedSize) {
            const variant = product.product_variant.find(v => v.size === selectedSize);
            if (variant) return variant;
        }

        if (selectedColor) {
            const variant = product.product_variant.find(v => {
                if (selectedColor.startsWith('custom_')) {
                    const colorName = selectedColor.replace('custom_', '');
                    return v.color_name === colorName && !v.color_id;
                } else {
                    return v.color_id === selectedColor;
                }
            });
            if (variant) return variant;
        }

        return product.product_variant[0];
    };

    const selectedVariant = getSelectedVariant();

    const totalStock = product.product_variant?.reduce((sum, variant) => sum + (variant.quantity || 0), 0) || 0;

    const getPriceRange = () => {
        if (!product.product_variant || product.product_variant.length === 0) {
            return { min: 0, max: 0, hasDiscount: false };
        }

        const finalPrices = product.product_variant.map(v => v.discounted_price || v.original_price);
        const originalPrices = product.product_variant.map(v => v.original_price);
        const hasDiscount = product.product_variant.some(v => v.discounted_price && v.discounted_price < v.original_price);

        return {
            min: Math.min(...finalPrices),
            max: Math.max(...finalPrices),
            originalMin: Math.min(...originalPrices),
            originalMax: Math.max(...originalPrices),
            hasDiscount: hasDiscount
        };
    };

    const priceRange = getPriceRange();

    const handleSizeSelect = (size) => {
        setSelectedSize(size);
        if (selectedColor) {
            const hasVariantWithBoth = product.product_variant.some(v => {
                const sizeMatch = v.size === size;
                let colorMatch = false;

                if (selectedColor.startsWith('custom_')) {
                    const colorName = selectedColor.replace('custom_', '');
                    colorMatch = v.color_name === colorName && !v.color_id;
                } else {
                    colorMatch = v.color_id === selectedColor;
                }

                return sizeMatch && colorMatch;
            });
            if (!hasVariantWithBoth) {
                setSelectedColor('');
            }
        }
    };

    const handleColorSelect = (color) => {
        const identifier = getColorIdentifier(color);
        setSelectedColor(identifier);
        if (selectedSize) {
            const hasVariantWithBoth = product.product_variant.some(v =>
                v.size === selectedSize &&
                (v.color_id === color.id || (color.id === null && v.color_name === color.name))
            );
            if (!hasVariantWithBoth) {
                setSelectedSize('');
            }
        }
    };

    const sortSizes = (sizes) => {
        if (!sizes || !Array.isArray(sizes)) return [];

        const sizeOrder = {
            'XXS': 1, 'XS': 2, 'S': 3, 'M': 4, 'L': 5, 'XL': 6, 'XXL': 7, 'XXXL': 8,
            'xs': 2, 's': 3, 'm': 4, 'l': 5, 'xl': 6, 'xxl': 7
        };

        return [...sizes].sort((a, b) => {
            const sizeA = a?.toString().trim();
            const sizeB = b?.toString().trim();

            if (!sizeA && !sizeB) return 0;
            if (!sizeA) return 1;
            if (!sizeB) return -1;

            const numA = parseFloat(sizeA);
            const numB = parseFloat(sizeB);

            if (!isNaN(numA) && !isNaN(numB)) {
                return numA - numB;
            }

            if (isNaN(numA) && isNaN(numB)) {
                const orderA = sizeOrder[sizeA] || sizeOrder[sizeA.toUpperCase()] || 999;
                const orderB = sizeOrder[sizeB] || sizeOrder[sizeB.toUpperCase()] || 999;

                if (orderA !== orderB) {
                    return orderA - orderB;
                }
                return sizeA.localeCompare(sizeB);
            }

            if (!isNaN(numA) && isNaN(numB)) return -1;
            if (isNaN(numA) && !isNaN(numB)) return 1;

            return 0;
        });
    };

    const getAvailableOptions = () => {
        const filteredSizes = selectedColor
            ? [...new Set(product.product_variant
                ?.filter(v => {
                    let colorMatch = false;
                    if (selectedColor.startsWith('custom_')) {
                        const colorName = selectedColor.replace('custom_', '');
                        colorMatch = v.color_name === colorName && !v.color_id;
                    } else {
                        colorMatch = v.color_id === selectedColor;
                    }
                    return colorMatch && v.size;
                })
                .map(v => v.size))] || []
            : availableSizes;

        const sizeStockInfo = {};
        filteredSizes.forEach(size => {
            if (selectedColor) {
                const variant = product.product_variant.find(v => {
                    const sizeMatch = v.size === size;
                    let colorMatch = false;
                    if (selectedColor.startsWith('custom_')) {
                        const colorName = selectedColor.replace('custom_', '');
                        colorMatch = v.color_name === colorName && !v.color_id;
                    } else {
                        colorMatch = v.color_id === selectedColor;
                    }
                    return sizeMatch && colorMatch;
                });
                sizeStockInfo[size] = variant ? variant.quantity === 0 : true;
            } else {
                sizeStockInfo[size] = false;
            }
        });

        const processedColors = availableColors.map(color => {
            if (selectedSize) {
                const variant = product.product_variant.find(v => {
                    const sizeMatch = v.size === selectedSize;
                    let colorMatch = false;
                    if (color.id === null) {
                        colorMatch = v.color_name === color.name && !v.color_id;
                    } else {
                        colorMatch = v.color_id === color.id;
                    }
                    return sizeMatch && colorMatch;
                });
                return {
                    ...color,
                    isOutOfStock: variant ? variant.quantity === 0 : true
                };
            } else {
                return {
                    ...color,
                    isOutOfStock: false
                };
            }
        });

        const filteredColors = selectedSize
            ? processedColors.filter(color => {
                return product.product_variant.some(v => {
                    const sizeMatch = v.size === selectedSize;
                    let colorMatch = false;
                    if (color.id === null) {
                        colorMatch = v.color_name === color.name && !v.color_id;
                    } else {
                        colorMatch = v.color_id === color.id;
                    }
                    return sizeMatch && colorMatch;
                });
            })
            : processedColors;

        return {
            availableSizes: sortSizes(filteredSizes),
            availableColors: filteredColors,
            sizeStockInfo
        };
    };

    const { availableSizes: displaySizes, availableColors: displayColors, sizeStockInfo } = getAvailableOptions();

    const createFlyingAnimation = (sourceElement, targetElement, imageUrl) => {
        const sourceRect = sourceElement.getBoundingClientRect();
        const targetRect = targetElement.getBoundingClientRect();

        const flyingImage = document.createElement('img');
        flyingImage.src = imageUrl;
        flyingImage.style.cssText = `
        position: fixed;
        top: ${sourceRect.top}px;
        left: ${sourceRect.left}px;
        width: ${sourceRect.width}px;
        height: ${sourceRect.height}px;
        border-radius: 4px;
        z-index: 9999;
        pointer-events: none;
        transition: all 0.8s cubic-bezier(0.2, 0, 0.2, 1);
        object-fit: cover;
    `;

        document.body.appendChild(flyingImage);

        setTimeout(() => {
            flyingImage.style.top = `${targetRect.top + targetRect.height / 2 - 15}px`;
            flyingImage.style.left = `${targetRect.left + targetRect.width / 2 - 15}px`;
            flyingImage.style.width = '30px';
            flyingImage.style.height = '30px';
            flyingImage.style.opacity = '0.7';
            flyingImage.style.transform = 'scale(0.5)';
        }, 50);

        setTimeout(() => {
            document.body.removeChild(flyingImage);
        }, 850);
    };

    const handleAddToCart = async () => {
        if (!selectedSize) {
            toast.error('Vui lòng chọn kích thước');
            return;
        }

        if (!selectedColor) {
            toast.error('Vui lòng chọn màu sắc');
            return;
        }

        if (!selectedVariant || selectedVariant.quantity === 0) {
            toast.error('Sản phẩm đã hết hàng');
            return;
        }

        if (quantity < 1) {
            toast.error('Số lượng phải lớn hơn 0');
            return;
        }

        if (quantity > 999) {
            toast.error('Số lượng tối đa là 999');
            return;
        }

        if (quantity > selectedVariant.quantity) {
            toast.error(`Chỉ còn ${selectedVariant.quantity} sản phẩm`);
            return;
        }

        setIsAddingToCart(true);

        try {
            const cartData = {
                product_variant_id: selectedVariant.id,
                quantity: quantity
            };

            const response = await postDataApi('/customer/cart/', cartData);

            if (response.success) {
                const selectedColorObj = displayColors.find(color =>
                    getColorIdentifier(color) === selectedColor
                );

                if (selectedColorObj && selectedColorObj.image) {
                    const sourceElement = document.querySelector(`[data-color-id="${getColorIdentifier(selectedColorObj)}"] img`);
                    const targetElement = document.querySelector('[aria-label="cart"]') ||
                        document.querySelector('.MuiIconButton-root[aria-label="cart"]') ||
                        document.querySelector('.header-cart-icon') ||
                        document.querySelector('header [title="Cart"]');

                    if (sourceElement && targetElement) {
                        createFlyingAnimation(sourceElement, targetElement, selectedColorObj.image);
                    }
                }

                if (response.data?.items_count !== undefined) {
                    context.setCartItemsCount(response.data.items_count);
                }

                const addedQty = quantity;
                toast.success(`Đã thêm ${addedQty} sản phẩm vào giỏ hàng`);
            } else {
                const rawMsg = response?.data?.detail?.message || response?.data?.detail?.[0]?.msg || "Không thể tạo địa chỉ mới";
                const cleanedMsg = rawMsg.replace(/^Value error,\s*/i, "");
                toast.error(cleanedMsg)
            }
        } catch (error) {
            console.error('Add to cart error:', error);
            toast.error('Không thể thêm vào giỏ hàng');
        } finally {
            setIsAddingToCart(false);
        }
    };

    const handleAddToWishlist = () => {
        // TODO: Implement add to wishlist API call
        console.log('Add to wishlist:', product.id);
    };

    const handleAddToCompare = () => {
        // TODO: Implement add to compare API call
        console.log('Add to compare:', product.id);
    };

    return (
        <>
            <h1 className="text-[24px] font-[600] mb-2">{product.name}</h1>

            <div className="flex items-center gap-1">
                {product.categories && product.categories.length > 0 && (
                    <span className="text-gray-400 text-[13px]">
                        Danh mục: <span className="font-[500] text-black opacity-75">{product.categories.map(c => c.name).join(', ')}</span>
                        <span> | </span>
                    </span>
                )}

                {product.avg_rating ? (
                    <>
                        <Rating
                            name="product-rating"
                            value={roundRating(product.avg_rating)}
                            size="small"
                            readOnly
                        />
                        <span className="text-[13px] font-[500]">
                            {product.avg_rating.toFixed(1)}
                        </span>
                        <span className="text-[13px] cursor-pointer">
                            ({product.review_count || 0} đánh giá)
                        </span>
                    </>
                ) : (
                    <span className="text-[13px] text-gray-400">Chưa có đánh giá</span>
                )}
            </div>

            <div className="flex items-center gap-4 mt-4">
                <div className="flex items-center gap-3">
                    <span className="text-[#ff5252] text-[24px] font-[600]">
                        {selectedVariant
                            ? formatPrice(selectedVariant.discounted_price || selectedVariant.original_price)
                            : priceRange.min === priceRange.max
                                ? formatPrice(priceRange.min)
                                : `${formatPrice(priceRange.min)} - ${formatPrice(priceRange.max)}`
                        }
                    </span>

                    {selectedVariant && selectedVariant.discounted_price && selectedVariant.discounted_price < selectedVariant.original_price && (
                        <>
                            <span className="bg-[#ff5252] text-white text-[12px] px-2 py-1 rounded font-[500]">
                                -{Math.round(((selectedVariant.original_price - selectedVariant.discounted_price) / selectedVariant.original_price) * 100)}%
                            </span>
                            <span className="text-gray-400 text-[16px] line-through">
                                {formatPrice(selectedVariant.original_price)}
                            </span>
                        </>
                    )}
                </div>

                {selectedSize && selectedColor && selectedVariant && (
                    <span className="text-[14px]">
                        Còn lại: <span className={`text-[14px] font-bold ${selectedVariant.quantity > 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {selectedVariant.quantity} sản phẩm
                        </span>
                    </span>
                )}
            </div>

            {product.short_description && (
                <p className="mt-3 pr-10 mb-5">{product.short_description}</p>
            )}

            {displaySizes.length > 0 && (
                <div className="flex items-center gap-3 pt-3">
                    <span className="text-[16px]">Kích thước:</span>
                    <div className="flex items-center gap-1 actions">
                        {displaySizes.map((size) => {
                            const isOutOfStock = sizeStockInfo[size] || false;
                            return (
                                <Button
                                    key={size}
                                    className={`${selectedSize === size ? '!bg-[#ff5252] !text-white' : ''} ${isOutOfStock || isAddingToCart ? 'cursor-not-allowed opacity-50' : ''
                                        }`}
                                    onClick={() => !isOutOfStock && !isAddingToCart && handleSizeSelect(size)}
                                    disabled={isOutOfStock || isAddingToCart}
                                >
                                    {size}
                                </Button>
                            );
                        })}
                    </div>
                </div>
            )}

            {displayColors.length > 0 && (
                <div className="flex items-center gap-3 pt-3">
                    <span className="text-[16px]">Màu sắc:</span>
                    <div className="flex items-center gap-2">
                        {displayColors.map((color) => (
                            <div
                                key={color.id}
                                data-color-id={getColorIdentifier(color)}
                                className={`flex items-center gap-2 p-2 border rounded ${color.isOutOfStock || isAddingToCart ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'
                                    } ${selectedColor === getColorIdentifier(color) ? 'border-[#ff5252] bg-red-50' : 'border-gray-300'}`}
                                onClick={() => !color.isOutOfStock && !isAddingToCart && handleColorSelect(color)}
                            >
                                <img
                                    src={color.image}
                                    alt={color.name}
                                    className="w-8 h-8 object-cover rounded"
                                />
                                <span className="text-sm">{color.name}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <p className="text-[14px] pt-3 mb-2">
                Miễn phí vận chuyển (Thời gian giao hàng dự kiến 2-3 ngày)
            </p>

            {product.total_sold > 0 && (
                <p className="text-[14px] text-gray-600 mb-2">
                    Đã bán: {product.total_sold} sản phẩm
                </p>
            )}

            <div className="flex items-center mt-4 gap-4">
                <div className="qtyBoxWrapper w-[80px]">
                    <QtyBox
                        value={quantity}
                        onChange={setQuantity}
                        max={selectedVariant?.quantity || 1}
                        disabled={!selectedVariant || isAddingToCart}
                    />
                </div>

                <Button
                    className="btn-org flex gap-2"
                    onClick={handleAddToCart}
                    disabled={!selectedVariant || selectedVariant.quantity === 0 || isAddingToCart}
                >
                    <MdOutlineShoppingCart className="text-[22px]" />
                    {isAddingToCart
                        ? 'Đang thêm...'
                        : !selectedVariant
                            ? 'Chọn size và màu'
                            : selectedVariant.quantity > 0
                                ? 'Thêm vào giỏ'
                                : 'Hết hàng'
                    }
                </Button>
            </div>

            <div className="flex items-center gap-4 mt-6">
                <span
                    className="flex items-center gap-2 text-[15px] link cursor-pointer font-[500]"
                    onClick={handleAddToWishlist}
                >
                    <FaRegHeart className="text-[18px]" /> Thêm vào yêu thích
                </span>
                <span
                    className="flex items-center gap-2 text-[15px] link cursor-pointer font-[500]"
                    onClick={handleAddToCompare}
                >
                    <IoGitCompareOutline className="text-[18px]" /> So sánh sản phẩm
                </span>
            </div>
        </>
    );
};

export default ProductDetailsComponent