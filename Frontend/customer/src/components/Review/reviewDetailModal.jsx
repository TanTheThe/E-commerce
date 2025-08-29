import React, { useState, useEffect } from 'react';
import { Rating } from '@mui/material';
import { getDataApi } from "../../utils/api";


const ReviewDetailModal = ({ reviewId, isOpen, onClose }) => {
    const [reviewDetail, setReviewDetail] = useState(null);
    const [loading, setLoading] = useState(false);

    const fetchReviewDetail = async () => {
        if (!reviewId) return;

        setLoading(true);
        try {
            const response = await getDataApi(`/customer/evaluate/${reviewId}`);

            if (response.success === true) {
                setReviewDetail(response.data || null);
            } else {
                console.error('Failed to fetch review detail:', response.message);
                setReviewDetail(null);
            }
        } catch (error) {
            console.error('Error fetching review detail:', error);
            setReviewDetail(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (isOpen && reviewId) {
            fetchReviewDetail();
        }
    }, [isOpen, reviewId]);

    const formatDate = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString("vi-VN", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        });
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

    const handleOverlayClick = (e) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 flex items-center justify-center z-50 p-4"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}
            onClick={handleOverlayClick}
        >
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-gray-200">
                <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                    <h2 className="text-xl font-semibold text-gray-800">Chi tiết đánh giá</h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 text-2xl font-bold cursor-pointer"
                    >
                        ×
                    </button>
                </div>

                <div className="p-6">
                    {loading ? (
                        <div className="flex justify-center items-center py-12">
                            <div className="text-lg">Đang tải...</div>
                        </div>
                    ) : reviewDetail ? (
                        <div className="space-y-6">
                            <div className="bg-gray-50 p-4 rounded-lg">
                                <div className="flex items-center justify-between mb-3">
                                    <h3 className="text-lg font-semibold text-gray-800">
                                        {formatCustomerName(reviewDetail.customer)}
                                    </h3>
                                    <span className="text-sm text-gray-500">
                                        {formatDate(reviewDetail.created_at)}
                                    </span>
                                </div>

                                {reviewDetail.product && (
                                    <div className="text-sm mb-3 bg-white px-3 py-1 rounded-full inline-block text-red-500">
                                        {formatProductVariant(reviewDetail.product)}
                                    </div>
                                )}

                                <div className="flex items-center gap-2 mb-3">
                                    <Rating
                                        name="review-rating"
                                        value={reviewDetail.rate || 0}
                                        readOnly
                                        size="small"
                                    />
                                    <span className="text-sm font-medium text-yellow-600">
                                        {reviewDetail.rate}/5
                                    </span>
                                </div>
                            </div>

                            {reviewDetail.comment && (
                                <div>
                                    <h4 className="text-md font-medium text-gray-800 mb-2">Đánh giá:</h4>
                                    <div className="bg-gray-50 p-4 rounded-lg text-gray-700 text-sm leading-relaxed">
                                        {reviewDetail.comment}
                                    </div>
                                </div>
                            )}

                            {reviewDetail.image && (
                                <div>
                                    <h4 className="text-md font-medium text-gray-800 mb-2">Hình ảnh đánh giá:</h4>
                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                                        {Array.isArray(reviewDetail.image) ? (
                                            reviewDetail.image.map((img, index) => (
                                                <img
                                                    key={index}
                                                    src={img}
                                                    alt={`Đánh giá`}
                                                    className="w-full h-32 object-cover rounded-lg border border-gray-200"
                                                />
                                            ))
                                        ) : (
                                            <img
                                                src={reviewDetail.image}
                                                alt="Đánh giá"
                                                className="w-full h-32 object-cover rounded-lg border border-gray-200"
                                            />
                                        )}
                                    </div>
                                </div>
                            )}

                            {reviewDetail.additional_comment && (
                                <div>
                                    <div className="flex items-center justify-between mb-2">
                                        <h4 className="text-md font-medium text-gray-800">Đánh giá bổ sung:</h4>
                                        {reviewDetail.additional_created_at && (
                                            <span className="text-xs text-gray-500">
                                                {formatDate(reviewDetail.additional_created_at)}
                                            </span>
                                        )}
                                    </div>
                                    <div className="bg-blue-50 p-4 rounded-lg text-gray-700 text-sm leading-relaxed border-l-4 border-blue-400">
                                        {reviewDetail.additional_comment}
                                    </div>
                                </div>
                            )}

                            {reviewDetail.additional_image && (
                                <div>
                                    <h4 className="text-md font-medium text-gray-800 mb-2">Hình ảnh bổ sung:</h4>
                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                                        {Array.isArray(reviewDetail.additional_image) ? (
                                            reviewDetail.additional_image.map((img, index) => (
                                                <img
                                                    key={index}
                                                    src={img}
                                                    alt={`Bổ sung ${index + 1}`}
                                                    className="w-full h-32 object-cover rounded-lg border border-gray-200"
                                                />
                                            ))
                                        ) : (
                                            <img
                                                src={reviewDetail.additional_image}
                                                alt="Bổ sung"
                                                className="w-full h-32 object-cover rounded-lg border border-gray-200"
                                            />
                                        )}
                                    </div>
                                </div>
                            )}

                            {reviewDetail.seller_reply && (
                                <div>
                                    <div className="flex items-center justify-between mb-2">
                                        <h4 className="text-md font-medium text-gray-800">Phản hồi từ người bán:</h4>
                                        {reviewDetail.seller_reply_at && (
                                            <span className="text-xs text-gray-500">
                                                {formatDate(reviewDetail.seller_reply_at)}
                                            </span>
                                        )}
                                    </div>
                                    <div className="bg-green-50 p-4 rounded-lg text-gray-700 text-sm leading-relaxed border-l-4 border-green-400">
                                        {reviewDetail.seller_reply}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="flex justify-center items-center py-12">
                            <div className="text-center">
                                <div className="text-lg mb-2 text-gray-600">Không tìm thấy chi tiết đánh giá</div>
                                <div className="text-sm text-gray-500">Vui lòng thử lại sau</div>
                            </div>
                        </div>
                    )}
                </div>

                <div className="sticky bottom-0 bg-white border-t border-gray-200 px-6 py-4">
                    <button
                        onClick={onClose}
                        className="w-full bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-lg transition duration-200 cursor-pointer"
                    >
                        Đóng
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ReviewDetailModal;