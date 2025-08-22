import Button from '@mui/material/Button';
import React from 'react';


const ProductDetailOffcanvas = ({ open, onClose, product }) => {
    const formatPrice = (price) => {
        return price ? `${price.toLocaleString('vi-VN')}đ` : 'N/A';
    };

    const hasDiscount = (variant) => {
        return variant.original_price && variant.discounted_price && variant.original_price > variant.discounted_price;
    };

    const calculateDiscountPercent = (original, discounted) => {
        if (!original || !discounted) return 0;
        return Math.round(((original - discounted) / original) * 100);
    };

    return (
        <div className={`fixed inset-0 z-50 ${open ? 'visible' : 'invisible'}`}>
            <div
                className={`fixed inset-0 bg-black transition-opacity duration-300 ${open ? 'opacity-50' : 'opacity-0'}`}
                onClick={onClose}
            ></div>

            <div className={`fixed right-0 top-0 h-full w-[650px] bg-white shadow-xl transform transition-transform duration-300 ${open ? 'translate-x-0' : 'translate-x-full'}`}>
                <div className="flex items-center justify-between p-4 border-b border-[rgba(0,0,0,0.2)]">
                    <h2 className="text-xl font-semibold">Product Details</h2>
                    <Button
                        className="!w-8 !h-8 !min-w-8 !p-0 hover:bg-gray-100"
                        onClick={onClose}
                    >
                        <span className="text-xl">&times;</span>
                    </Button>
                </div>

                <div className="p-4 h-full overflow-y-auto pb-24">
                    {product && (
                        <>
                            <div className="mb-6">
                                <div className="flex items-center gap-4 mb-4">
                                    <img
                                        src={product.images?.[0] || '/placeholder-image.jpg'}
                                        alt={product.name}
                                        className="w-20 h-20 object-cover rounded-md"
                                    />
                                    <div>
                                        <h3 className="font-semibold text-lg mb-2">{product.name}</h3>
                                        <div className="flex gap-2 mb-2">
                                            {product.categories?.map((cat) => (
                                                <span key={cat.id} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                                                    {cat.name}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="mb-6">
                                <h4 className="text-sm font-medium text-gray-700 mb-2">Description</h4>
                                <div className="p-3 bg-gray-50 border border-gray-200 rounded-md">
                                    <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                                        {product.description || 'No description available'}
                                    </p>
                                </div>
                            </div>

                            <div className="mb-6">
                                <h4 className="text-lg font-semibold mb-4">
                                    Product Variants ({product.product_variant?.length || 0})
                                </h4>
                                {product.product_variant && product.product_variant.length > 0 ? (
                                    <div className="space-y-4">
                                        {product.product_variant.map((variant, index) => (
                                            <div key={variant.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                                                <div className="flex items-center justify-between mb-3">
                                                    <h5 className="font-medium text-gray-800">Variant {index + 1}</h5>
                                                    <span className="text-sm text-gray-500 bg-white px-2 py-1 rounded">
                                                        ID: {variant.id}
                                                    </span>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-600 mb-1">
                                                            Size
                                                        </label>
                                                        <div className="p-2 bg-white border border-gray-200 rounded-md">
                                                            <span className={`${variant.size ? 'text-gray-800' : 'text-gray-400 italic'}`}>
                                                                {variant.size || 'None'}
                                                            </span>
                                                        </div>
                                                    </div>

                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-600 mb-1">
                                                            Color
                                                        </label>
                                                        <div className="p-2 bg-white border border-gray-200 rounded-md flex items-center gap-2">
                                                            {variant.color_code && (
                                                                <div
                                                                    className="w-4 h-4 rounded-full border border-gray-300"
                                                                    style={{ backgroundColor: variant.color_code }}
                                                                ></div>
                                                            )}
                                                            <span className={`${variant.color_name ? 'text-gray-800' : 'text-gray-400 italic'}`}>
                                                                {variant.color_name || 'None'}
                                                            </span>
                                                        </div>
                                                    </div>

                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-600 mb-1">
                                                            Original Price
                                                        </label>
                                                        <div className="p-2 bg-white border border-gray-200 rounded-md">
                                                            <span className={`${hasDiscount(variant) ? 'text-gray-400 line-through text-sm' : 'text-gray-800 font-semibold'}`}>
                                                                {formatPrice(variant.original_price)}
                                                            </span>
                                                        </div>
                                                    </div>

                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-600 mb-1">
                                                            {hasDiscount(variant) ? 'Discounted Price' : 'Price'}
                                                        </label>
                                                        <div className="p-2 bg-white border border-gray-200 rounded-md flex items-center gap-2">
                                                            {hasDiscount(variant) ? (
                                                                <>
                                                                    <span className="text-red-600 font-semibold">
                                                                        {formatPrice(variant.discounted_price)}
                                                                    </span>
                                                                    <span className="bg-red-100 text-red-800 text-xs px-1.5 py-0.5 rounded">
                                                                        -{calculateDiscountPercent(variant.original_price, variant.discounted_price)}%
                                                                    </span>
                                                                </>
                                                            ) : (
                                                                <span className="text-gray-800">
                                                                    {formatPrice(variant.discounted_price || variant.original_price)}
                                                                </span>
                                                            )}
                                                        </div>
                                                    </div>

                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-600 mb-1">
                                                            Quantity
                                                        </label>
                                                        <div className="p-2 bg-white border border-gray-200 rounded-md">
                                                            <span className={`${variant.quantity > 0 ? 'text-gray-800' : 'text-red-500'}`}>
                                                                {variant.quantity}
                                                                {variant.quantity === 0 && ' (Out of stock)'}
                                                            </span>
                                                        </div>
                                                    </div>

                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-600 mb-1">
                                                            SKU
                                                        </label>
                                                        <div className="p-2 bg-white border border-gray-200 rounded-md">
                                                            <span className="text-gray-800 font-mono text-sm">
                                                                {variant.sku}
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-gray-500 text-center py-8">
                                        No variants available for this product
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </div>

                <div className="absolute bottom-0 left-0 right-0 bg-white border-t border-[rgba(0,0,0,0.2)] p-4">
                    <div className="flex justify-end">
                        <Button
                            className="px-6 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                            onClick={onClose}
                        >
                            Close
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProductDetailOffcanvas;
