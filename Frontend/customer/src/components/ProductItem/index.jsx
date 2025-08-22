import React, { useContext } from "react";
import "../ProductItem/style.css"
import { Link } from "react-router-dom";
import Rating from '@mui/material/Rating';
import { FaRegHeart } from "react-icons/fa"
import { IoGitCompareOutline } from "react-icons/io5"
import { MdZoomOutMap } from "react-icons/md"
import Button from "@mui/material/Button";
import { MyContext } from "../../App";

const ProductItem = ({ product = null }) => {
    const context = useContext(MyContext)

    const formatPrice = (price) => {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(price);
    };

    const formatCategories = (categories) => {
        if (!categories || categories.length === 0) {
            return 'Chưa phân loại';
        }

        if (categories.length <= 3) {
            return categories.map(cat => cat.name).join(', ');
        } else {
            const firstTwo = categories.slice(0, 2).map(cat => cat.name).join(', ');
            return `${firstTwo}, ...`;
        }
    };

    const getCategoryNames = (categories) => {
        if (!categories || categories.length === 0) {
            return 'Chưa phân loại';
        }
        return categories.map(cat => cat.name).join(', ');
    };

    const calculateDiscountPercentage = (originalPrice, discountedPrice) => {
        if (!originalPrice || !discountedPrice || originalPrice <= discountedPrice) {
            return 0;
        }
        return Math.round(((originalPrice - discountedPrice) / originalPrice) * 100);
    };

    if (!product) {
        return (
            <div className="productItem shadow-lg rounded-md overflow-hidden border-1 border-[rgba(0,0,0,0.1)]">
                <div className="group imgWrapper w-[100%] overflow-hidden rounded-md relative">
                    <div className="img h-[250px] overflow-hidden bg-gray-200 flex items-center justify-center">
                        <span className="text-gray-500">No Image</span>
                    </div>
                </div>
                <div className="info p-3 py-5">
                    <h6 className="text-[13px] !font-[400] text-gray-500">No Category</h6>
                    <h3 className="text-[13px] title mt-1 font-[500] mb-1 text-[#000]">
                        No Product Data
                    </h3>
                    <Rating name="size-small" value={0} size="small" readOnly />
                    <div className="flex items-center gap-4">
                        <span className="text-gray-500">N/A</span>
                    </div>
                </div>
            </div>
        );
    }

    const mainImage = product.images && product.images.length > 0 ? product.images[0] : null;
    const hoverImage = product.images && product.images.length > 1 ? product.images[1] : mainImage;
    const discountPercentage = calculateDiscountPercentage(product.original_price, product.discounted_price);
    const hasDiscount = product.discounted_price && product.original_price && product.discounted_price < product.original_price;

    return (
        <div className="productItem shadow-lg rounded-md overflow-hidden border-1 border-[rgba(0,0,0,0.1)]">
            <div className="group imgWrapper w-[100%] overflow-hidden rounded-md relative">
                <Link to={`/product/${product.id}`}>
                    <div className="img h-[250px] overflow-hidden">
                        {mainImage ? (
                            <>
                                <img
                                    className="w-full h-full object-cover"
                                    src={mainImage}
                                    alt={product.name}
                                />
                                {hoverImage && hoverImage !== mainImage && (
                                    <img
                                        className="w-full h-full object-cover transition-all duration-700 absolute top-0 left-0 opacity-0 group-hover:opacity-100 group-hover:scale-105"
                                        src={hoverImage}
                                        alt={product.name}
                                    />
                                )}
                            </>
                        ) : (
                            <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                                <span className="text-gray-500">No Image</span>
                            </div>
                        )}
                    </div>
                </Link>

                {hasDiscount && (
                    <div className="absolute top-3 left-3 bg-[#ff5252] text-white px-2 py-1 rounded-md text-[11px] font-[600] z-10">
                        -{discountPercentage}%
                    </div>
                )}

                <div className="actions absolute top-[-200px] right-[5px] z-50 flex items-center gap-2 flex-col w-[50px] transition-all duration-300 group-hover:top-[15px] opacity-0 group-hover:opacity-100">
                    <Button
                        className="!w-[35px] !h-[35px] !min-w-[35px] !rounded-full !bg-white text-black hover:!bg-[#ff5252] hover:text-white group"
                        onClick={() => context?.setOpenProductDetailsModal && context.setOpenProductDetailsModal(true)}
                    >
                        <MdZoomOutMap className="text-[18px] !text-black group-hover:text-white hover:!text-white" />
                    </Button>

                    <Button className="!w-[35px] !h-[35px] !min-w-[35px] !rounded-full !bg-white text-black hover:!bg-[#ff5252] hover:text-white group">
                        <IoGitCompareOutline className="text-[18px] !text-black group-hover:text-white hover:!text-white" />
                    </Button>

                    <Button className="!w-[35px] !h-[35px] !min-w-[35px] !rounded-full !bg-white text-black hover:!bg-[#ff5252] hover:text-white group">
                        <FaRegHeart className="text-[18px] !text-black group-hover:text-white hover:!text-white" />
                    </Button>
                </div>
            </div>

            <div className="info p-3 py-5">
                <h6 className="text-[13px] !font-[400]">
                    <span
                        className="text-gray-600"
                        title={getCategoryNames(product.categories)}
                    >
                        {formatCategories(product.categories)}
                    </span>
                </h6>
                <h3 className="text-[13px] title mt-1 font-[500] mb-1 text-[#000]">
                    <Link to={`/product/${product.id}`} className="link transition-all hover:text-[#ff5252]">
                        {product.name}
                    </Link>
                </h3>
                <Rating
                    name="product-rating"
                    value={product.avg_rating || 0}
                    size="small"
                    readOnly
                    precision={0.1}
                />

                <div className="flex items-center gap-2 mt-2">
                    {product.discounted_price || product.original_price ? (
                        <div className="flex items-center gap-2 flex-wrap">
                            {hasDiscount ? (
                                <>
                                    <span className="price text-[#ff5252] font-[600] text-[14px]">
                                        {formatPrice(product.discounted_price)}
                                    </span>
                                    <span className="original-price text-gray-400 font-[400] text-[12px] line-through">
                                        {formatPrice(product.original_price)}
                                    </span>
                                </>
                            ) : (
                                <span className="price text-[#ff5252] font-[600] text-[14px]">
                                    {formatPrice(product.original_price)}
                                </span>
                            )}
                        </div>
                    ) : (
                        <span className="price text-[#ff5252] font-[600] text-[14px]">
                            Liên hệ
                        </span>
                    )}
                </div>
            </div>
        </div>
    )
}

export default ProductItem