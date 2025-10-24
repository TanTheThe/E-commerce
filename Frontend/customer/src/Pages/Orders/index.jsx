import React, { useEffect, useState } from "react";
import AccountSideBar from "../../components/AccountSideBar";
import Button from "@mui/material/Button";
import { FaAngleDown, FaAngleUp } from "react-icons/fa";
import Badge from "../../components/Badge";
import { Collapse } from "react-collapse";
import { useNavigate, useSearchParams } from "react-router-dom";
import { FiCheck, FiChevronDown, FiChevronUp, FiClock, FiTruck, FiStar, FiX, FiCamera, FiMessageSquare } from "react-icons/fi";
import { getDataApi, postDataApi, putDataApi } from "../../utils/api";
import EvaluationButtons from "../Evaluate/evaluationButton";
import EvaluateModal from "../Evaluate/evaluateModal";
import AdditionalEvaluateModal from "../Evaluate/additionalEvalModal";
import ViewEvaluationModal from "../Evaluate/viewEvalModal";
import toast from "react-hot-toast";
import CancelOrderModal from "./cancelOrder";
import ReturnModal from "./returnModal";

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
    const [showCancelModal, setShowCancelModal] = useState(false);
    const [selectedOrder, setSelectedOrder] = useState(null);
    const [cancelForm, setCancelForm] = useState({
        reason: '',
        reason_detail: ''
    });
    const [showReturnModal, setShowReturnModal] = useState(false);
    const [returnForm, setReturnForm] = useState({
        reason: '',
        note: '',
        images: [],
        return_items: []
    });

    const tabs = [
        {
            key: 'pending',
            label: 'Chờ xác nhận',
            icon: FiClock,
            color: 'text-yellow-600',
            bgColor: 'bg-yellow-50',
            borderColor: 'border-yellow-200',
            status: 'pending'
        },
        {
            key: 'confirmed',
            label: 'Đã xác nhận',
            icon: FiCheck,
            color: 'text-blue-600',
            bgColor: 'bg-blue-50',
            borderColor: 'border-blue-200',
            status: 'confirmed'
        },
        {
            key: 'shipping',
            label: 'Đang giao hàng',
            icon: FiTruck,
            color: 'text-orange-600',
            bgColor: 'bg-orange-50',
            borderColor: 'border-orange-200',
            status: 'shipping'
        },
        {
            key: 'delivered',
            label: 'Đã giao hàng',
            icon: FiCheck,
            color: 'text-green-600',
            bgColor: 'bg-green-50',
            borderColor: 'border-green-200',
            status: 'delivered'
        },
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

    const handleOpenReturnModal = async (orderItem) => {
        try {
            const response = await getDataApi(`/customer/return-order/check-eligibility/${orderItem.order.order_id}`);

            if (response.success && response.data.eligible) {
                setSelectedOrder(orderItem);
                setReturnForm({
                    reason: '',
                    note: '',
                    return_items: orderItem.order_detail.flatMap(detail =>
                        detail.variants ? detail.variants.map(variant => ({
                            order_detail_id: variant.order_detail_id,
                            quantity: variant.quantity,
                            selected: false,
                            images: [],
                            product_name: detail.name,
                            product_image: detail.variant_image,
                            price_after_discount: detail.price_after_discount,
                            size: variant.size,
                            color_name: variant.color_name
                        })) : [{
                            order_detail_id: detail.order_detail_id,
                            quantity: detail.quantity,
                            selected: false,
                            images: [],
                            product_name: detail.name,
                            product_image: detail.variant_image,
                            price_after_discount: detail.price_after_discount,
                            size: detail.size,
                            color_name: detail.color_name
                        }]
                    )
                });
                setShowReturnModal(true);
            } else {
                toast.error(response.data.detail.message || 'Đơn hàng này không đủ điều kiện để trả hàng');
            }
        } catch (error) {
            console.error('Error checking return eligibility:', error);
            toast.error('Có lỗi xảy ra khi kiểm tra điều kiện trả hàng');
        }
    };

    const handleSubmitReturn = async () => {
        try {
            const selectedItems = returnForm.return_items.filter(item => item.selected);

            if (selectedItems.length === 0) {
                toast.error('Vui lòng chọn ít nhất một sản phẩm để trả hàng');
                return;
            }

            const itemsWithoutEnoughImages = selectedItems.filter(item => !item.images || item.images.length < 5);
            if (itemsWithoutEnoughImages.length > 0) {
                toast.error('Mỗi sản phẩm cần ít nhất 5 ảnh');
                return;
            }

            const submitData = {
                reason: returnForm.reason,
                note: returnForm.note,
                return_items: selectedItems.map(item => ({
                    order_detail_id: item.order_detail_id,
                    quantity: item.quantity,
                    images: item.images.map(img => img.base64)
                }))
            };

            const res = await postDataApi(`/customer/return-order/${selectedOrder.order.order_id}`, submitData);

            if (res.success) {
                toast.success(res.message);
                setShowReturnModal(false);

                returnForm.return_items.forEach(item => {
                    if (item.images) {
                        item.images.forEach(img => {
                            if (img.url) URL.revokeObjectURL(img.url);
                        });
                    }
                });

                const currentTab = tabs.find(tab => tab.key === activeTab);
                if (currentTab) {
                    fetchOrders(currentTab.status, pagination.skip, pagination.limit);
                }
            } else {
                toast.error(res.data.detail.message || 'Có lỗi xảy ra khi tạo yêu cầu trả hàng');
            }
        } catch (error) {
            console.error('Error submitting return request:', error);
            toast.error('Có lỗi xảy ra khi tạo yêu cầu trả hàng');
        }
    };

    const handleConfirmReceived = async (orderId) => {
        try {
            const response = await putDataApi(`/customer/order/confirm-received/${orderId}`);

            if (response.success) {
                toast.success(response.message);

                const currentTab = tabs.find(tab => tab.key === activeTab);
                if (currentTab) {
                    fetchOrders(currentTab.status, pagination.skip, pagination.limit);
                }
            } else {
                toast.error(response.data.detail.message || 'Có lỗi xảy ra khi xác nhận nhận hàng');
            }
        } catch (error) {
            console.error('Error confirming order received:', error);
            toast.error('Có lỗi xảy ra khi xác nhận nhận hàng');
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
        if (evaluateForm.image && evaluateForm.image.url) {
            URL.revokeObjectURL(evaluateForm.image.url);
        }

        setEvaluateForm({
            rate: 5,
            comment: '',
            image: null
        });
    };

    const resetAdditionalForm = () => {
        if (additionalForm.additional_image?.url) {
            URL.revokeObjectURL(additionalForm.additional_image.url);
        }

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

    const handleOpenCancelModal = (orderItem) => {
        setSelectedOrder(orderItem);
        setCancelForm({ reason: '', reason_detail: '' });
        setShowCancelModal(true);
    };

    const handleCancelOrder = async () => {
        try {
            const submitData = {
                reason: cancelForm.reason,
                reason_detail: cancelForm.reason_detail || null
            };

            const res = await postDataApi(`/customer/order/${selectedOrder.order.order_id}/cancel`, submitData);

            if (res.success) {
                toast.success(res.message);
                setShowCancelModal(false);

                const currentTab = tabs.find(tab => tab.key === activeTab);
                if (currentTab) {
                    fetchOrders(currentTab.status, pagination.skip, pagination.limit);
                }
            } else {
                toast.error(res.data.detail.message || 'Có lỗi xảy ra khi hủy đơn hàng');
            }
        } catch (error) {
            console.error('Error cancelling order:', error);
            toast.error('Có lỗi xảy ra khi hủy đơn hàng');
        }
    };

    const handleOpenView = async (variant) => {
        try {
            const response = await getDataApi(`/customer/evaluate/${variant.evaluation_id}`);
            if (response.success) {
                setEvaluationData(response.data);
                setSelectedVariant(variant);
                setShowViewModal(true);
            }
        } catch (error) {
            console.error('Error fetching evaluation:', error);
        }
    };

    const handleSubmitEvaluate = async () => {
        try {
            const submitData = {
                order_detail_id: selectedVariant.order_detail_id,
                rate: evaluateForm.rate,
                comment: evaluateForm.comment
            };

            if (evaluateForm.image && evaluateForm.image.base64) {
                submitData.image = evaluateForm.image.base64;
            }

            const res = await postDataApi('/customer/evaluate/', submitData);
            if (res.success) {
                toast.success(res.message);
                setShowEvaluateModal(false);
            } else {
                toast.error(res.data.detail.message);
            }

            if (evaluateForm.image && evaluateForm.image.url) {
                URL.revokeObjectURL(evaluateForm.image.url);
            }

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
            const submitData = {
                additional_comment: additionalForm.additional_comment
            };

            if (additionalForm.additional_image && additionalForm.additional_image.base64) {
                submitData.additional_image = additionalForm.additional_image.base64;
            }

            const res = await putDataApi(`/customer/evaluate/${selectedVariant.evaluation_id}/supplement`, submitData);
            if (res.success) {
                toast.success(res.message);
                setShowAdditionalModal(false);
            } else {
                toast.error(res.data.detail.message);
            }

            if (additionalForm.additional_image && additionalForm.additional_image.url) {
                URL.revokeObjectURL(additionalForm.additional_image.url);
            }

            const currentTab = tabs.find(tab => tab.key === activeTab);
            if (currentTab) {
                fetchOrders(currentTab.status, pagination.skip, pagination.limit);
            }
        } catch (error) {
            console.error('Error submitting additional evaluation:', error);
        }
    };

    useEffect(() => {
        return () => {
            if (evaluateForm.image && evaluateForm.image.url) {
                URL.revokeObjectURL(evaluateForm.image.url);
            }
            if (additionalForm.additional_image && additionalForm.additional_image.url) {
                URL.revokeObjectURL(additionalForm.additional_image.url);
            }
        };
    }, [evaluateForm.image, additionalForm.additional_image]);

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
                                                                                <EvaluationButtons
                                                                                    item={variant}
                                                                                    onEvaluate={handleOpenEvaluate}
                                                                                    onViewEvaluation={handleOpenView}
                                                                                    onAdditionalEvaluation={handleOpenAdditional}
                                                                                />
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
                                                                                <EvaluationButtons
                                                                                    item={product}
                                                                                    onEvaluate={handleOpenEvaluate}
                                                                                    onViewEvaluation={handleOpenView}
                                                                                    onAdditionalEvaluation={handleOpenAdditional}
                                                                                />
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

                                                {orderItem.order.has_pending_cancellation && (
                                                    <div className="mt-2">
                                                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                                            🔄 Đang chờ duyệt hủy đơn
                                                        </span>
                                                        {orderItem.order.cancellation_reason && (
                                                            <p className="text-xs text-gray-600 mt-1">
                                                                Lý do: {orderItem.order.cancellation_reason}
                                                            </p>
                                                        )}
                                                    </div>
                                                )}
                                            </div>

                                            <div className="flex gap-2">
                                                <button
                                                    onClick={() => navigate(`/order-detail/${orderItem.order.order_id}`)}
                                                    className="px-6 py-2 bg-[#ff5252] text-white rounded-lg hover:bg-[#e53e3e] transition-colors cursor-pointer"
                                                >
                                                    Xem chi tiết
                                                </button>

                                                {activeTab === 'delivered' && orderItem.order.status === 'delivered' && (
                                                    <button
                                                        onClick={() => handleConfirmReceived(orderItem.order.order_id)}
                                                        className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors cursor-pointer"
                                                    >
                                                        Đã nhận hàng
                                                    </button>
                                                )}

                                                {activeTab === 'delivered' && orderItem.order.status === 'received' && (
                                                    <>
                                                        {orderItem.order.has_return_orders ? (
                                                            <div className="px-6 py-2 bg-yellow-100 text-yellow-800 rounded-lg border border-yellow-200">
                                                                <span className="text-sm font-medium">
                                                                    📦 Đơn hàng hiện đang trong quá trình hoàn trả
                                                                </span>
                                                            </div>
                                                        ) : (
                                                            <button
                                                                onClick={() => handleOpenReturnModal(orderItem)}
                                                                className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors cursor-pointer"
                                                            >
                                                                Trả hàng
                                                            </button>
                                                        )}
                                                    </>
                                                )}

                                                {orderItem.order.can_show_cancel_button && (
                                                    <button
                                                        onClick={() => handleOpenCancelModal(orderItem)}
                                                        className="px-6 py-2 border-2 border-red-500 text-red-500 rounded-lg hover:bg-red-500 hover:text-white transition-colors cursor-pointer"
                                                    >
                                                        Hủy đơn hàng
                                                    </button>
                                                )}
                                            </div>
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

            <EvaluateModal
                isOpen={showEvaluateModal}
                onClose={() => setShowEvaluateModal(false)}
                selectedVariant={selectedVariant}
                onSubmit={handleSubmitEvaluate}
                evaluateForm={evaluateForm}
                setEvaluateForm={setEvaluateForm}
            />

            <AdditionalEvaluateModal
                isOpen={showAdditionalModal}
                onClose={() => setShowAdditionalModal(false)}
                selectedVariant={selectedVariant}
                onSubmit={handleSubmitAdditional}
                additionalForm={additionalForm}
                setAdditionalForm={setAdditionalForm}
            />

            <ViewEvaluationModal
                isOpen={showViewModal}
                onClose={() => setShowViewModal(false)}
                evaluationData={evaluationData}
            />

            <CancelOrderModal
                isOpen={showCancelModal}
                onClose={() => setShowCancelModal(false)}
                selectedOrder={selectedOrder}
                onSubmit={handleCancelOrder}
                cancelForm={cancelForm}
                setCancelForm={setCancelForm}
            />

            <ReturnModal
                isOpen={showReturnModal}
                onClose={() => setShowReturnModal(false)}
                selectedOrder={selectedOrder}
                onSubmit={handleSubmitReturn}
                returnForm={returnForm}
                setReturnForm={setReturnForm}
            />
        </div>
    );
};

export default Orders