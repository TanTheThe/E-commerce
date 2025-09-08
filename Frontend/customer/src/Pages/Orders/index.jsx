import React, { useEffect, useState } from "react";
import AccountSideBar from "../../components/AccountSideBar";
import Button from "@mui/material/Button";
import { FaAngleDown, FaAngleUp } from "react-icons/fa";
import Badge from "../../components/Badge";
import { Collapse } from "react-collapse";
import { useNavigate, useSearchParams } from "react-router-dom";
import { FiCheck, FiChevronDown, FiChevronUp, FiClock, FiTruck, FiStar, FiX, FiCamera, FiMessageSquare } from "react-icons/fi";
import { getDataApi } from "../../utils/api";

const Orders = () => {
    const navigate = useNavigate();
    const [searchParams, setSearchParams] = useSearchParams();
    const [activeTab, setActiveTab] = useState('pending');
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [expandedOrders, setExpandedOrders] = useState({});
    const [pagination, setPagination] = useState({
        skip: 0,
        limit: 10,
        total: 0
    });
    const [showEvaluateModal, setShowEvaluateModal] = useState(false);
    const [showAdditionalModal, setShowAdditionalModal] = useState(false);
    const [showViewModal, setShowViewModal] = useState(false);
    const [selectedVariant, setSelectedVariant] = useState(null);
    const [evaluationData, setEvaluationData] = useState(null);
    const [evaluateForm, setEvaluateForm] = useState({
        rate: 5,
        comment: '',
        image: null
    });
    const [additionalForm, setAdditionalForm] = useState({
        additional_comment: '',
        additional_image: null
    });

    const tabs = [
        {
            key: 'pending',
            label: 'Chờ xác nhận',
            icon: FiClock,
            color: 'text-yellow-600',
            bgColor: 'bg-yellow-50',
            borderColor: 'border-yellow-200',
            status: 'Pending'
        },
        {
            key: 'confirmed',
            label: 'Đã xác nhận',
            icon: FiCheck,
            color: 'text-blue-600',
            bgColor: 'bg-blue-50',
            borderColor: 'border-blue-200',
            status: 'Confirmed'
        },
        {
            key: 'shipping',
            label: 'Đang giao hàng',
            icon: FiTruck,
            color: 'text-orange-600',
            bgColor: 'bg-orange-50',
            borderColor: 'border-orange-200',
            status: 'Shipping'
        },
        {
            key: 'delivered',
            label: 'Đã giao hàng',
            icon: FiCheck,
            color: 'text-green-600',
            bgColor: 'bg-green-50',
            borderColor: 'border-green-200',
            status: 'Delivered'
        }
    ];

    const fetchOrders = async (status, skip = 0, limit = 10) => {
        try {
            setLoading(true);
            const response = await getDataApi(`/customer/order/status/${status}?skip=${skip}&limit=${limit}`);
            if (response.success) {
                setOrders(response.data.data || []);
                setPagination({
                    skip,
                    limit,
                    total: response.data.total || 0
                });
            }
        } catch (err) {
            setError('Không thể tải danh sách đơn hàng');
            console.error('Error fetching orders:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const tabFromUrl = searchParams.get('tab') || 'pending';
        setActiveTab(tabFromUrl);

        const currentTab = tabs.find(tab => tab.key === tabFromUrl);
        if (currentTab) {
            fetchOrders(currentTab.status, 0, 10);
        }
    }, [searchParams]);

    const handleTabClick = (tab) => {
        setActiveTab(tab.key);
        setSearchParams({ tab: tab.key });
        fetchOrders(tab.status, 0, 10);
    };

    const handlePageChange = (newSkip) => {
        const currentTab = tabs.find(tab => tab.key === activeTab);
        if (currentTab) {
            fetchOrders(currentTab.status, newSkip, pagination.limit);
        }
    };

    const toggleOrderExpansion = (orderCode) => {
        setExpandedOrders(prev => ({
            ...prev,
            [orderCode]: !prev[orderCode]
        }));
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('vi-VN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const resetEvaluateForm = () => {
        setEvaluateForm({
            rate: 5,
            comment: '',
            image: null
        });
    };

    const resetAdditionalForm = () => {
        setAdditionalForm({
            additional_comment: '',
            additional_image: null
        });
    };

    const handleOpenEvaluate = (variant) => {
        setSelectedVariant(variant);
        resetEvaluateForm();
        setShowEvaluateModal(true);
    };

    const handleOpenAdditional = (variant) => {
        setSelectedVariant(variant);
        resetAdditionalForm();
        setShowAdditionalModal(true);
    };

    const handleOpenView = async (variant) => {
        try {
            const response = await getDataApi(`/customer/evaluate/${variant.evaluation_id}`);
            if (response.success) {
                setEvaluationData(response.data.content);
                setSelectedVariant(variant);
                setShowViewModal(true);
            }
        } catch (error) {
            console.error('Error fetching evaluation:', error);
        }
    };

    const handleSubmitEvaluate = async () => {
        try {
            const formData = new FormData();
            formData.append('order_detail_id', selectedVariant.order_detail_id);
            formData.append('rate', evaluateForm.rate);
            formData.append('comment', evaluateForm.comment);
            if (evaluateForm.image) {
                formData.append('image', evaluateForm.image);
            }

            await postDataApi('/customer/evaluate/', formData);
            setShowEvaluateModal(false);

            const currentTab = tabs.find(tab => tab.key === activeTab);
            if (currentTab) {
                fetchOrders(currentTab.status, pagination.skip, pagination.limit);
            }
        } catch (error) {
            console.error('Error submitting evaluation:', error);
        }
    };

    const handleSubmitAdditional = async () => {
        try {
            const formData = new FormData();
            formData.append('additional_comment', additionalForm.additional_comment);
            if (additionalForm.additional_image) {
                formData.append('additional_image', additionalForm.additional_image);
            }

            await putDataApi(`/customer/evaluate/${selectedVariant.evaluation_id}/supplement`, formData);
            setShowAdditionalModal(false);

            const currentTab = tabs.find(tab => tab.key === activeTab);
            if (currentTab) {
                fetchOrders(currentTab.status, pagination.skip, pagination.limit);
            }
        } catch (error) {
            console.error('Error submitting additional evaluation:', error);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[#ff5252] mx-auto mb-4"></div>
                    <p className="text-gray-600">Đang tải danh sách đơn hàng...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="text-red-500 text-6xl mb-4">⚠️</div>
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">Có lỗi xảy ra</h2>
                    <p className="text-gray-600 mb-4">{error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="px-6 py-2 bg-[#ff5252] text-white rounded-lg hover:bg-[#e53e3e] transition-colors cursor-pointer"
                    >
                        Thử lại
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="container mx-auto px-4 max-w-6xl">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-800 mb-2">Đơn hàng của tôi</h1>
                    <p className="text-gray-600">Theo dõi và quản lý các đơn hàng của bạn</p>
                </div>

                <div className="bg-white rounded-lg shadow-sm mb-6">
                    <div className="p-6 border-b border-gray-200">
                        <h2 className="text-xl font-bold text-gray-800 mb-4">Trạng thái đơn hàng</h2>

                        <div className="flex flex-wrap gap-4">
                            {tabs.map((tab) => {
                                const Icon = tab.icon;
                                const isActive = activeTab === tab.key;

                                return (
                                    <button
                                        key={tab.key}
                                        onClick={() => handleTabClick(tab)}
                                        className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-all duration-300 cursor-pointer hover:scale-105 hover:shadow-md ${isActive
                                            ? `${tab.bgColor} ${tab.borderColor} ${tab.color} shadow-md`
                                            : 'bg-gray-100 border-gray-300 text-gray-600 hover:bg-gray-200 hover:border-gray-400'
                                            }`}
                                    >
                                        <Icon className="text-lg" />
                                        <span className="font-medium">{tab.label}</span>
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    {orders.length === 0 ? (
                        <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                            <div className="text-gray-400 text-6xl mb-4">📦</div>
                            <h3 className="text-xl font-bold text-gray-800 mb-2">Không có đơn hàng nào</h3>
                            <p className="text-gray-600 mb-6">Bạn chưa có đơn hàng nào ở trạng thái này</p>
                            <button
                                onClick={() => navigate('/')}
                                className="px-6 py-2 bg-[#ff5252] text-white rounded-lg hover:bg-[#e53e3e] transition-colors cursor-pointer"
                            >
                                Tiếp tục mua sắm
                            </button>
                        </div>
                    ) : (
                        orders.map((orderItem) => {
                            const isExpanded = expandedOrders[orderItem.order.code];
                            const displayItems = isExpanded ? orderItem.order_detail : orderItem.order_detail.slice(0, 1);

                            return (
                                <div key={orderItem.order.code} className="bg-white rounded-lg shadow-sm overflow-hidden">
                                    <div className="p-6">
                                        <div className="flex items-center justify-between mb-4">
                                            <div>
                                                <p className="text-sm text-gray-600">Mã đơn hàng</p>
                                                <p className="font-bold text-[#ff5252]">#{orderItem.order.code}</p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-sm text-gray-600">Ngày đặt</p>
                                                <p className="font-medium">{formatDate(orderItem.order.created_at)}</p>
                                            </div>
                                        </div>

                                        <div className="mb-4">
                                            <div className="space-y-4">
                                                {displayItems.map((product, index) => (
                                                    <div key={index} className="flex items-start gap-4 p-3 bg-gray-50 rounded-lg">
                                                        <div className="w-20 h-20 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                                                            <img
                                                                src={product.variant_image}
                                                                alt={product.name}
                                                                className="w-full h-full object-cover"
                                                            />
                                                        </div>
                                                        <div className="flex-1 min-w-0">
                                                            <h4 className="font-medium text-gray-800 mb-2 line-clamp-2">{product.name}</h4>
                                                            <div className="space-y-1 mb-2">
                                                                {product.variants ? product.variants.map((variant, vIndex) => (
                                                                    <div key={vIndex} className="space-y-2">
                                                                        <div className="text-sm text-gray-600">
                                                                            <span>Size: {variant.size}</span>
                                                                            <span className="mx-2">•</span>
                                                                            <span>Màu: {variant.color_name}</span>
                                                                            <span className="mx-2">•</span>
                                                                            <span>SL: {variant.quantity}</span>
                                                                        </div>

                                                                        {activeTab === 'delivered' && (
                                                                            <div className="flex gap-2 flex-wrap">
                                                                                {!variant.has_evaluation ? (
                                                                                    <button
                                                                                        onClick={() => handleOpenEvaluate(variant)}
                                                                                        className="px-3 py-1 text-xs bg-[#ff5252] text-white rounded-md hover:bg-[#e53e3e] transition-colors cursor-pointer"
                                                                                    >
                                                                                        Đánh giá
                                                                                    </button>
                                                                                ) : !variant.has_additional_evaluation ? (
                                                                                    <>
                                                                                        <button
                                                                                            onClick={() => handleOpenView(variant)}
                                                                                            className="px-3 py-1 text-xs bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors cursor-pointer"
                                                                                        >
                                                                                            Xem đánh giá
                                                                                        </button>
                                                                                        <button
                                                                                            onClick={() => handleOpenAdditional(variant)}
                                                                                            className="px-3 py-1 text-xs bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors cursor-pointer"
                                                                                        >
                                                                                            Đánh giá bổ sung
                                                                                        </button>
                                                                                    </>
                                                                                ) : (
                                                                                    <>
                                                                                        <button
                                                                                            onClick={() => handleOpenView(variant)}
                                                                                            className="px-3 py-1 text-xs bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors cursor-pointer"
                                                                                        >
                                                                                            Xem đánh giá
                                                                                        </button>
                                                                                        <button
                                                                                            onClick={() => handleOpenView(variant, 'additional')}
                                                                                            className="px-3 py-1 text-xs bg-purple-500 text-white rounded-md hover:bg-purple-600 transition-colors cursor-pointer"
                                                                                        >
                                                                                            Xem đánh giá bổ sung
                                                                                        </button>
                                                                                    </>
                                                                                )}
                                                                            </div>
                                                                        )}
                                                                    </div>
                                                                )) : (
                                                                    <div className="space-y-2">
                                                                        <div className="text-sm text-gray-600">
                                                                            <span>Size: {product.size}</span>
                                                                            <span className="mx-2">•</span>
                                                                            <span>Màu: {product.color_name}</span>
                                                                            <span className="mx-2">•</span>
                                                                            <span>SL: {product.quantity}</span>
                                                                        </div>

                                                                        {activeTab === 'delivered' && (
                                                                            <div className="flex gap-2 flex-wrap">
                                                                                {!product.has_evaluation ? (
                                                                                    <button
                                                                                        onClick={() => handleOpenEvaluate(product)}
                                                                                        className="px-3 py-1 text-xs bg-[#ff5252] text-white rounded-md hover:bg-[#e53e3e] transition-colors cursor-pointer"
                                                                                    >
                                                                                        Đánh giá
                                                                                    </button>
                                                                                ) : !product.has_additional_evaluation ? (
                                                                                    <>
                                                                                        <button
                                                                                            onClick={() => handleOpenView(product)}
                                                                                            className="px-3 py-1 text-xs bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors cursor-pointer"
                                                                                        >
                                                                                            Xem đánh giá
                                                                                        </button>
                                                                                        <button
                                                                                            onClick={() => handleOpenAdditional(product)}
                                                                                            className="px-3 py-1 text-xs bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors cursor-pointer"
                                                                                        >
                                                                                            Đánh giá bổ sung
                                                                                        </button>
                                                                                    </>
                                                                                ) : (
                                                                                    <>
                                                                                        <button
                                                                                            onClick={() => handleOpenView(product)}
                                                                                            className="px-3 py-1 text-xs bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors cursor-pointer"
                                                                                        >
                                                                                            Xem đánh giá
                                                                                        </button>
                                                                                        <button
                                                                                            onClick={() => handleOpenView(product, 'additional')}
                                                                                            className="px-3 py-1 text-xs bg-purple-500 text-white rounded-md hover:bg-purple-600 transition-colors cursor-pointer"
                                                                                        >
                                                                                            Xem đánh giá bổ sung
                                                                                        </button>
                                                                                    </>
                                                                                )}
                                                                            </div>
                                                                        )}
                                                                    </div>
                                                                )}
                                                            </div>
                                                            <div className="flex items-center gap-2">
                                                                <span className="text-lg font-bold text-[#ff5252]">
                                                                    {product.price_after_discount?.toLocaleString('vi-VN')}đ
                                                                </span>
                                                                {product.price_before_discount && product.price_before_discount !== product.price_after_discount && (
                                                                    <span className="text-sm text-gray-500 line-through">
                                                                        {product.price_before_discount?.toLocaleString('vi-VN')}đ
                                                                    </span>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>

                                            {orderItem.order_detail.length > 1 && (
                                                <div className="mt-3">
                                                    <button
                                                        onClick={() => toggleOrderExpansion(orderItem.order.code)}
                                                        className="text-[#ff5252] hover:text-[#e53e3e] text-sm font-medium transition-colors cursor-pointer flex items-center gap-1"
                                                    >
                                                        {isExpanded ? (
                                                            <>
                                                                <span>Thu gọn</span>
                                                                <FiChevronUp className="text-lg" />
                                                            </>
                                                        ) : (
                                                            <>
                                                                <span>Xem thêm {orderItem.order_detail.length - 1} sản phẩm</span>
                                                                <FiChevronDown className="text-lg" />
                                                            </>
                                                        )}
                                                    </button>
                                                </div>
                                            )}
                                        </div>

                                        <div className="flex items-center justify-between border-t pt-4">
                                            <div>
                                                <p className="text-sm text-gray-600">Tổng tiền</p>
                                                <div className="flex items-center gap-2">
                                                    <p className="text-xl font-bold text-[#ff5252]">
                                                        {orderItem.order.total_price?.toLocaleString('vi-VN')}đ
                                                    </p>
                                                    {orderItem.order.discount > 0 && (
                                                        <span className="text-sm text-green-600 font-medium">
                                                            (Giảm {orderItem.order.discount?.toLocaleString('vi-VN')}đ)
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                            <button
                                                onClick={() => navigate(`/order-detail/${orderItem.order.order_id}`)}
                                                className="px-6 py-2 bg-[#ff5252] text-white rounded-lg hover:bg-[#e53e3e] transition-colors cursor-pointer"
                                            >
                                                Xem chi tiết
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            );
                        })
                    )}
                </div>

                {orders.length > 0 && pagination.total > pagination.limit && (
                    <div className="flex items-center justify-center mt-8 gap-2">
                        <button
                            onClick={() => handlePageChange(Math.max(0, pagination.skip - pagination.limit))}
                            disabled={pagination.skip === 0}
                            className={`px-4 py-2 rounded-lg border transition-colors ${pagination.skip === 0
                                ? 'border-gray-300 text-gray-400 cursor-not-allowed'
                                : 'border-[#ff5252] text-[#ff5252] hover:bg-[#ff5252] hover:text-white cursor-pointer'
                                }`}
                        >
                            Trang trước
                        </button>

                        <span className="px-4 py-2 text-gray-600">
                            Trang {Math.floor(pagination.skip / pagination.limit) + 1} / {Math.ceil(pagination.total / pagination.limit)}
                        </span>

                        <button
                            onClick={() => handlePageChange(pagination.skip + pagination.limit)}
                            disabled={pagination.skip + pagination.limit >= pagination.total}
                            className={`px-4 py-2 rounded-lg border transition-colors ${pagination.skip + pagination.limit >= pagination.total
                                ? 'border-gray-300 text-gray-400 cursor-not-allowed'
                                : 'border-[#ff5252] text-[#ff5252] hover:bg-[#ff5252] hover:text-white cursor-pointer'
                                }`}
                        >
                            Trang sau
                        </button>
                    </div>
                )}
            </div>
            {showEvaluateModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-bold text-gray-800">Đánh giá sản phẩm</h3>
                            <button onClick={() => setShowEvaluateModal(false)} className="text-gray-500 hover:text-gray-700">
                                <FiX className="text-xl" />
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Đánh giá sao</label>
                                <div className="flex gap-1">
                                    {[1, 2, 3, 4, 5].map(star => (
                                        <button
                                            key={star}
                                            onClick={() => setEvaluateForm(prev => ({ ...prev, rate: star }))}
                                            className={`text-2xl ${star <= evaluateForm.rate ? 'text-yellow-400' : 'text-gray-300'} hover:text-yellow-400 transition-colors`}
                                        >
                                            <FiStar className={star <= evaluateForm.rate ? 'fill-current' : ''} />
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Nhận xét</label>
                                <textarea
                                    value={evaluateForm.comment}
                                    onChange={(e) => setEvaluateForm(prev => ({ ...prev, comment: e.target.value }))}
                                    className="w-full p-3 border border-gray-300 rounded-lg resize-none"
                                    rows="4"
                                    placeholder="Chia sẻ trải nghiệm của bạn về sản phẩm..."
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Hình ảnh (tùy chọn)</label>
                                <input
                                    type="file"
                                    accept="image/*"
                                    onChange={(e) => setEvaluateForm(prev => ({ ...prev, image: e.target.files[0] }))}
                                    className="w-full p-2 border border-gray-300 rounded-lg"
                                />
                            </div>
                        </div>

                        <div className="flex gap-3 mt-6">
                            <button
                                onClick={() => setShowEvaluateModal(false)}
                                className="flex-1 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                                Hủy
                            </button>
                            <button
                                onClick={handleSubmitEvaluate}
                                className="flex-1 py-2 bg-[#ff5252] text-white rounded-lg hover:bg-[#e53e3e] transition-colors"
                            >
                                Gửi đánh giá
                            </button>
                        </div>
                    </div>
                </div>
            )}
            {showAdditionalModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-bold text-gray-800">Đánh giá bổ sung</h3>
                            <button onClick={() => setShowAdditionalModal(false)} className="text-gray-500 hover:text-gray-700">
                                <FiX className="text-xl" />
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Nhận xét bổ sung</label>
                                <textarea
                                    value={additionalForm.additional_comment}
                                    onChange={(e) => setAdditionalForm(prev => ({ ...prev, additional_comment: e.target.value }))}
                                    className="w-full p-3 border border-gray-300 rounded-lg resize-none"
                                    rows="4"
                                    placeholder="Thêm nhận xét sau khi sử dụng sản phẩm..."
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Hình ảnh bổ sung (tùy chọn)</label>
                                <input
                                    type="file"
                                    accept="image/*"
                                    onChange={(e) => setAdditionalForm(prev => ({ ...prev, additional_image: e.target.files[0] }))}
                                    className="w-full p-2 border border-gray-300 rounded-lg"
                                />
                            </div>
                        </div>

                        <div className="flex gap-3 mt-6">
                            <button
                                onClick={() => setShowAdditionalModal(false)}
                                className="flex-1 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                                Hủy
                            </button>
                            <button
                                onClick={handleSubmitAdditional}
                                className="flex-1 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                            >
                                Gửi bổ sung
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {showViewModal && evaluationData && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-bold text-gray-800">Chi tiết đánh giá</h3>
                            <button onClick={() => setShowViewModal(false)} className="text-gray-500 hover:text-gray-700">
                                <FiX className="text-xl" />
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div className="flex gap-3 p-3 bg-gray-50 rounded-lg">
                                <div className="w-16 h-16 bg-gray-200 rounded-lg overflow-hidden">
                                    <img
                                        src={evaluationData.product.variant_image}
                                        alt={evaluationData.product.name}
                                        className="w-full h-full object-cover"
                                    />
                                </div>
                                <div className="flex-1">
                                    <h4 className="font-medium text-gray-800">{evaluationData.product.name}</h4>
                                    <p className="text-sm text-gray-600">
                                        Size: {evaluationData.product.size} • Màu: {evaluationData.product.color_name}
                                    </p>
                                </div>
                            </div>

                            <div>
                                <div className="flex items-center gap-2 mb-2">
                                    <div className="flex">
                                        {[1, 2, 3, 4, 5].map(star => (
                                            <FiStar
                                                key={star}
                                                className={`text-lg ${star <= evaluationData.rate ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
                                            />
                                        ))}
                                    </div>
                                    <span className="text-sm text-gray-600">
                                        {new Date(evaluationData.created_at).toLocaleDateString('vi-VN')}
                                    </span>
                                </div>

                                {evaluationData.comment && (
                                    <p className="text-gray-700 mb-2">{evaluationData.comment}</p>
                                )}

                                {evaluationData.image && (
                                    <img
                                        src={evaluationData.image}
                                        alt="Evaluation"
                                        className="w-full max-w-xs rounded-lg"
                                    />
                                )}
                            </div>

                            {evaluationData.additional_evaluation.has_additional && (
                                <div className="border-t pt-4">
                                    <div className="flex items-center gap-2 mb-2">
                                        <FiMessageSquare className="text-green-500" />
                                        <span className="text-sm font-medium text-green-600">Đánh giá bổ sung</span>
                                        <span className="text-sm text-gray-600">
                                            {new Date(evaluationData.additional_evaluation.created_at).toLocaleDateString('vi-VN')}
                                        </span>
                                    </div>

                                    {evaluationData.additional_evaluation.comment && (
                                        <p className="text-gray-700 mb-2">{evaluationData.additional_evaluation.comment}</p>
                                    )}

                                    {evaluationData.additional_evaluation.image && (
                                        <img
                                            src={evaluationData.additional_evaluation.image}
                                            alt="Additional Evaluation"
                                            className="w-full max-w-xs rounded-lg"
                                        />
                                    )}
                                </div>
                            )}

                            {evaluationData.seller_reply.has_reply && (
                                <div className="border-t pt-4">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="text-sm font-medium text-blue-600">Phản hồi từ người bán</span>
                                        <span className="text-sm text-gray-600">
                                            {new Date(evaluationData.seller_reply.replied_at).toLocaleDateString('vi-VN')}
                                        </span>
                                    </div>
                                    <p className="text-gray-700 bg-blue-50 p-3 rounded-lg">{evaluationData.seller_reply.content}</p>
                                </div>
                            )}
                        </div>

                        <div className="mt-6">
                            <button
                                onClick={() => setShowViewModal(false)}
                                className="w-full py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                            >
                                Đóng
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Orders