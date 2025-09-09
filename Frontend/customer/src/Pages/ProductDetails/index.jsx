import Breadcrumbs from "@mui/material/Breadcrumbs";
import React, { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import ProductZoom from "../../components/ProductZoom";
import Rating from '@mui/material/Rating';
import { Button } from "@mui/material";
import TextField from '@mui/material/TextField';
import ProductsSlider from '../../components/ProductsSlider'
import ProductDetailsComponent from "../../components/ProductDetails";
import { getDataApi } from "../../utils/api";
import ReviewDetailModal from "../../components/Review/reviewDetailModal";

const ProductDetails = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [activeTab, setActiveTab] = useState(0);
    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(false);
    const [reviews, setReviews] = useState([]);
    const [reviewsLoading, setReviewsLoading] = useState(false);
    const [reviewsTotal, setReviewsTotal] = useState(0);
    const [reviewForm, setReviewForm] = useState({
        content: '',
        rating: 0
    });
    const [selectedReviewId, setSelectedReviewId] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const { id } = useParams();


    const fetchProductDetail = async () => {
        setLoading(true);
        try {
            const response = await getDataApi(`/customer/product/${id}`);

            if (response.success === true) {
                setProduct(response.data || null);
            } else {
                console.error('Failed to fetch product detail:', response.message);
                setProduct(null);
            }
        } catch (error) {
            console.error('Error fetching product detail:', error);
            setProduct(null);
        } finally {
            setLoading(false);
        }
    };

    const fetchReviews = async () => {
        if (!id) return;

        setReviewsLoading(true);
        try {
            const response = await getDataApi(`/customer/evaluate/by-product/${id}`);

            if (response.success === true) {
                setReviews(response.data.data || []);
                setReviewsTotal(response.data.total || 0);
            } else {
                console.error('Failed to fetch reviews:', response.message);
                setReviews([]);
                setReviewsTotal(0);
            }
        } catch (error) {
            console.error('Error fetching reviews:', error);
            setReviews([]);
            setReviewsTotal(0);
        } finally {
            setReviewsLoading(false);
        }
    };

    useEffect(() => {
        if (id) {
            fetchProductDetail();
        }
    }, [id]);

    useEffect(() => {
        if (activeTab === 2 && id) {
            fetchReviews();
        }
    }, [activeTab, id]);

    useEffect(() => {
        const token = localStorage.getItem('accesstoken');
        setIsLoggedIn(!!token);
    }, []);

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString("vi-VN", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric"
        });
    };

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

    const handleReviewFormChange = (field, value) => {
        setReviewForm(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const formatCustomerName = (customer) => {
        if (!customer) return 'Khách hàng ẩn danh';

        const firstName = customer.first_name || '';
        const lastName = customer.last_name || '';

        if (!firstName && !lastName) return 'Khách hàng ẩn danh';

        return `${firstName} ${lastName}`.trim();
    };

    const formatProductVariant = (product) => {
        if (!product) return '';

        let variant = product.name || '';
        if (product.size || product.color_name) {
            const details = [];
            if (product.size) details.push(`Size: ${product.size}`);
            if (product.color_name) details.push(`Màu: ${product.color_name}`);
            variant += ` (${details.join(', ')})`;
        }

        return variant;
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="text-lg">Đang tải...</div>
            </div>
        );
    }

    if (!product) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="text-lg">Không tìm thấy sản phẩm</div>
            </div>
        );
    }

    return (
        <>
            <div className="py-5">
                <div className="container">
                    <Breadcrumbs aria-label="breadcrumb">
                        <Link underline="hover" color="inherit" href="/" className="link transition !text-[14px]">
                            Trang chủ
                        </Link>
                        {product.categories && product.categories.length > 0 && (
                            <Link
                                underline="hover"
                                color="inherit"
                                href={`/category/${product.categories[0].id}`}
                                className="link transition !text-[14px]"
                            >
                                {product.categories[0].name}
                            </Link>
                        )}
                        <Link
                            underline="hover"
                            color="inherit"
                            className="link transition !text-[14px]"
                        >
                            {product.name}
                        </Link>
                    </Breadcrumbs>
                </div>
            </div>

            <section className="bg-white py-5">
                <div className="container flex gap-8">
                    <div className="productZoomContainer w-[40%]">
                        <ProductZoom images={product.images} />
                    </div>
                    <div className="productContent w-[60%] pr-10 pt-5">
                        <ProductDetailsComponent
                            product={product}
                            onProductUpdated={fetchProductDetail}
                        />
                    </div>
                </div>

                <div className="container pt-10">
                    <div className="flex items-center gap-8 mb-5">
                        <span
                            onClick={() => setActiveTab(0)}
                            className={`link text-[17px] cursor-pointer font-[500] ${activeTab === 0 && 'text-[#ff5252]'}`}
                        >
                            Mô tả sản phẩm
                        </span>
                        <span
                            onClick={() => setActiveTab(1)}
                            className={`link text-[17px] cursor-pointer font-[500] ${activeTab === 1 && 'text-[#ff5252]'}`}
                        >
                            Chi tiết sản phẩm
                        </span>
                        <span
                            onClick={() => setActiveTab(2)}
                            className={`link text-[17px] cursor-pointer font-[500] ${activeTab === 2 && 'text-[#ff5252]'}`}
                        >
                            Đánh giá
                        </span>
                    </div>

                    {activeTab === 0 && (
                        <div className="shadow-md w-full py-5 px-8 rounded-md">
                            {product.description ? (
                                <div className="whitespace-pre-line">
                                    {product.description}
                                </div>
                            ) : (
                                <p>Chưa có mô tả cho sản phẩm này.</p>
                            )}
                        </div>
                    )}

                    {activeTab === 1 && (
                        <div className="shadow-md w-full py-5 px-8 rounded-md">
                            <div className="relative overflow-x-auto">
                                <table className="w-full text-sm text-left rtl:text-right text-gray-500">
                                    <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                                        <tr>
                                            <th scope="col" className="px-6 py-3">Thông tin</th>
                                            <th scope="col" className="px-6 py-3">Chi tiết</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr className="bg-white border-b border-gray-200">
                                            <td className="px-6 py-4 font-[500]">Tên sản phẩm</td>
                                            <td className="px-6 py-4 font-[500]">{product.name}</td>
                                        </tr>
                                        {product.categories && product.categories.length > 0 && (
                                            <tr className="bg-white border-b border-gray-200">
                                                <td className="px-6 py-4 font-[500]">Danh mục</td>
                                                <td className="px-6 py-4 font-[500]">
                                                    {product.categories.map(cat => cat.name).join(', ')}
                                                </td>
                                            </tr>
                                        )}
                                        <tr className="bg-white border-b border-gray-200">
                                            <td className="px-6 py-4 font-[500]">Đã bán</td>
                                            <td className="px-6 py-4 font-[500]">{product.total_sold || 0} sản phẩm</td>
                                        </tr>
                                        <tr className="bg-white border-b border-gray-200">
                                            <td className="px-6 py-4 font-[500]">Đánh giá</td>
                                            <td className="px-6 py-4 font-[500]">
                                                {product.avg_rating ? (
                                                    <div className="flex items-center gap-2">
                                                        <Rating
                                                            value={roundRating(product.avg_rating)}
                                                            readOnly
                                                            precision={0.5}
                                                            size="small"
                                                        />
                                                        <span>({product.avg_rating?.toFixed(1)})</span>
                                                    </div>
                                                ) : (
                                                    'Chưa có đánh giá'
                                                )}
                                            </td>
                                        </tr>
                                        <tr className="bg-white border-b border-gray-200">
                                            <td className="px-6 py-4 font-[500]">Số biến thể</td>
                                            <td className="px-6 py-4 font-[500]">{product.product_variant?.length || 0}</td>
                                        </tr>
                                        {product.offer && (
                                            <tr className="bg-white border-b border-gray-200">
                                                <td className="px-6 py-4 font-[500]">Ưu đãi</td>
                                                <td className="px-6 py-4 font-[500]">{product.offer.name}</td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {activeTab === 2 && (
                        <div className="shadow-md w-full py-6 px-8 rounded-md">
                            <div className="w-full productReviewsContainer">
                                <h2 className="text-[20px] font-[600] mb-6">Đánh giá sản phẩm</h2>

                                {reviewsLoading ? (
                                    <div className="flex justify-center items-center py-12">
                                        <div className="text-lg">Đang tải đánh giá...</div>
                                    </div>
                                ) : (
                                    <div className="reviewScroll w-full max-h-[500px] overflow-y-auto overflow-x-hidden mb-8 pr-2">
                                        {reviews.length > 0 ? (
                                            <div className="space-y-6">
                                                {reviews.map((review, index) => (
                                                    <div key={review.id || index} className="review bg-white p-5 rounded-lg border border-gray-200 shadow-sm">
                                                        <div className="flex items-start justify-between">
                                                            <div className="flex-1">
                                                                <div className="flex items-center justify-between mb-3">
                                                                    <h4 className="text-[16px] font-[600] text-gray-800">
                                                                        {formatCustomerName(review.customer)}
                                                                    </h4>
                                                                    <span className="text-[13px] text-gray-500">
                                                                        {formatDate(review.created_at)}
                                                                    </span>
                                                                </div>

                                                                <div className="text-[13px] text-gray-600 mb-3 bg-gray-50 px-3 py-1 rounded-full inline-block">
                                                                    {formatProductVariant(review.product)}
                                                                </div>

                                                                <div className="flex items-center gap-2 mb-4">
                                                                    <Rating
                                                                        name="size-small"
                                                                        value={review.rate || 0}
                                                                        readOnly
                                                                        size="small"
                                                                    />
                                                                    <span className="text-sm font-[500] text-yellow-600">
                                                                        {review.rate}/5
                                                                    </span>
                                                                </div>

                                                                {review.content && (
                                                                    <div className="text-gray-700 text-[14px] leading-relaxed">
                                                                        {review.content}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </div>
                                                        <button
                                                            onClick={() => {
                                                                setSelectedReviewId(review.id);
                                                                setIsModalOpen(true);
                                                            }}
                                                            className="text-blue-600 hover:text-blue-800 text-sm font-medium cursor-pointer"
                                                        >
                                                            Xem chi tiết
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-lg">
                                                <div className="text-lg mb-2">Chưa có đánh giá nào</div>
                                                <div className="text-sm">Hãy là người đầu tiên đánh giá sản phẩm này!</div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>

                <div className="container pt-8">
                    <h2 className="text-[20px] font-[600]">Sản phẩm liên quan</h2>
                    <ProductsSlider items={6} />
                </div>
            </section>
            <ReviewDetailModal
                reviewId={selectedReviewId}
                isOpen={isModalOpen}
                onClose={() => {
                    setIsModalOpen(false);
                    setSelectedReviewId(null);
                }}
            />
        </>
    );
};

export default ProductDetails