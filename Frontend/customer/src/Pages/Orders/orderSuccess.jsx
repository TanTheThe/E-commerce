import React, { useState, useEffect } from 'react';
import { getDataApi } from '../../utils/api';
import { useNavigate, useParams } from 'react-router-dom';
import { FaCalendarAlt } from 'react-icons/fa';
import { FiCalendar, FiCheck, FiClock, FiCopy, FiEye, FiMail, FiMapPin, FiPhone, FiTruck, FiUser } from 'react-icons/fi';
import toast from 'react-hot-toast'

const OrderSuccessPage = () => {
    const { orderId } = useParams();
    const navigate = useNavigate();
    const [orderData, setOrderData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchOrderDetails = async () => {
        try {
            setLoading(true);

            const response = await getDataApi(`/customer/order/${orderId}`)
            if (response.success) {
                setOrderData(response.data)
            }
        } catch (err) {
            setError('Không thể tải thông tin đơn hàng');
            console.error('Error fetching order:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (orderId) {
            fetchOrderDetails();
        }
    }, [orderId]);

    const copyOrderCode = () => {
        if (orderData?.order?.code) {
            navigator.clipboard.writeText(orderData.order.code)
                .then(() => {
                    toast.success('Copied to clipboard!', {
                        position: 'top-right',
                        autoClose: 2000,
                        hideProgressBar: false,
                        closeOnClick: true,
                        pauseOnHover: true,
                        draggable: true,
                    });
                })
                .catch((err) => {
                    toast.error('Failed to copy!', {
                        position: 'top-right',
                        autoClose: 3000,
                    });
                    console.error('Copy failed:', err);
                });
        }
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

    const getStatusInfo = (status) => {
        const statusMap = {
            'pending': {
                label: 'Chờ xác nhận',
                icon: FiClock,
                color: 'text-yellow-600',
                bgColor: 'bg-yellow-50',
                borderColor: 'border-yellow-200'
            },
            'confirmed': {
                label: 'Đã xác nhận',
                icon: FiCheck,
                color: 'text-blue-600',
                bgColor: 'bg-blue-50',
                borderColor: 'border-blue-200'
            },
            'shipping': {
                label: 'Đang giao hàng',
                icon: FiTruck,
                color: 'text-orange-600',
                bgColor: 'bg-orange-50',
                borderColor: 'border-orange-200'
            },
            'delivered': {
                label: 'Đã giao hàng',
                icon: FiCheck,
                color: 'text-green-600',
                bgColor: 'bg-green-50',
                borderColor: 'border-green-200'
            }
        };
        return statusMap[status?.toLowerCase()] || statusMap['pending'];
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[#ff5252] mx-auto mb-4"></div>
                    <p className="text-gray-600">Đang tải thông tin đơn hàng...</p>
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
                        onClick={() => navigate('/orders')}
                        className="px-6 py-2 bg-[#ff5252] text-white rounded-lg hover:bg-[#e53e3e] transition-colors cursor-pointer"
                    >
                        Xem đơn hàng của tôi
                    </button>
                </div>
            </div>
        );
    }

    if (!orderData) return null;

    const statusInfo = getStatusInfo(orderData.order.status);
    const StatusIcon = statusInfo.icon;

    const isFromSuccessRoute = window.location.pathname.includes('order-success');

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="container mx-auto px-4 max-w-6xl">
                {isFromSuccessRoute ? (
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-4">
                            <FiCheck className="text-4xl text-green-600" />
                        </div>
                        <h1 className="text-3xl font-bold text-gray-800 mb-2">Đặt hàng thành công!</h1>
                        <p className="text-gray-600">Cảm ơn bạn đã mua hàng. Đơn hàng của bạn đang được xử lý.</p>
                    </div>
                ) : (
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold text-gray-800 mb-2">Chi tiết đơn hàng</h1>
                        <p className="text-gray-600">Theo dõi tình trạng và thông tin chi tiết đơn hàng của bạn</p>
                    </div>
                )}

                <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-gray-600">Mã đơn hàng</p>
                            <div className="flex items-center gap-2">
                                <p className="text-2xl font-bold text-[#ff5252]">#{orderData.order.code}</p>
                                <button
                                    onClick={copyOrderCode}
                                    className="p-2 text-gray-400 hover:text-[#ff5252] transition-colors cursor-pointer"
                                    title="Sao chép mã đơn hàng"
                                >
                                    <FiCopy />
                                </button>
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="text-gray-600">Tổng tiền</p>
                            <p className="text-2xl font-bold text-[#ff5252]">
                                {orderData.order.total_price?.toLocaleString('vi-VN')}đ
                            </p>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm mb-6">
                    <div className="p-6">
                        <h2 className="text-xl font-bold text-gray-800 mb-4">Trạng thái hiện tại</h2>

                        <div className={`flex items-center gap-4 p-4 rounded-lg border-2 ${statusInfo.bgColor} ${statusInfo.borderColor}`}>
                            <div className={`w-12 h-12 rounded-full flex items-center justify-center ${statusInfo.bgColor} ${statusInfo.borderColor} border-2`}>
                                <StatusIcon className={`text-xl ${statusInfo.color}`} />
                            </div>
                            <div>
                                <p className={`font-bold ${statusInfo.color}`}>{statusInfo.label}</p>
                                <p className="text-gray-600 text-sm">
                                    {isFromSuccessRoute
                                        ? `Đặt hàng ${formatDate(orderData.order.created_at)}`
                                        : `Cập nhật ${formatDate(orderData.order.last_status_change?.changed_at || orderData.order.created_at)}`
                                    }
                                </p>
                            </div>
                        </div>

                        <div className="mt-4 text-center">
                            <button
                                onClick={() => navigate(`/order-detail/${orderId}`)}
                                className="px-6 py-3 bg-[#ff5252] text-white font-medium rounded-lg hover:bg-[#e53e3e] transition-colors cursor-pointer inline-flex items-center gap-2"
                            >
                                <FiEye />
                                Theo dõi đơn hàng chi tiết
                            </button>
                        </div>
                    </div>
                </div>

                <div className="grid lg:grid-cols-3 gap-6">
                    <div className="lg:col-span-2">
                        <div className="bg-white rounded-lg shadow-sm">
                            <div className="p-6 border-b border-gray-200">
                                <h3 className="text-lg font-bold text-gray-800">Chi tiết đơn hàng</h3>
                            </div>
                            <div className="p-6">
                                <div className="space-y-4">
                                    {orderData.order_detail.map((item, index) => (
                                        <div key={index} className="flex gap-4 p-4 border border-gray-200 rounded-lg">
                                            <div className="w-20 h-20 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                                                <img
                                                    src={item.variant_image || (item.product_image && item.product_image[0])}
                                                    alt={item.name}
                                                    className="w-full h-full object-cover"
                                                />
                                            </div>
                                            <div className="flex-1">
                                                <h4 className="font-semibold text-gray-800 mb-1">{item.name}</h4>
                                                <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
                                                    <span>Size: {item.size}</span>
                                                    <span>Màu: {item.color_name}</span>
                                                    <span>SL: {item.quantity}</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <span className="font-semibold text-[#ff5252]">
                                                        {item.price_after_discount?.toLocaleString('vi-VN')}đ
                                                    </span>
                                                    {item.price_before_discount && item.price_before_discount > item.price_after_discount && (
                                                        <span className="text-sm text-gray-500 line-through">
                                                            {item.price_before_discount?.toLocaleString('vi-VN')}đ
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {orderData.order.note && (
                                    <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                                        <h4 className="font-medium text-gray-800 mb-2">Ghi chú đơn hàng:</h4>
                                        <p className="text-gray-600">{orderData.order.note}</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div className="bg-white rounded-lg shadow-sm p-6">
                            <h3 className="text-lg font-bold text-gray-800 mb-4">Tóm tắt đơn hàng</h3>
                            <div className="space-y-3">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Tạm tính</span>
                                    <span className="font-medium">{orderData.order.sub_total?.toLocaleString('vi-VN')}đ</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Giảm giá</span>
                                    <span className="font-medium text-green-600">-{orderData.order.discount?.toLocaleString('vi-VN')}đ</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Phí vận chuyển</span>
                                    <span className="font-medium">Miễn phí</span>
                                </div>
                                <div className="border-t pt-3">
                                    <div className="flex justify-between text-lg font-bold">
                                        <span>Tổng cộng</span>
                                        <span className="text-[#ff5252]">{orderData.order.total_price?.toLocaleString('vi-VN')}đ</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm p-6">
                            <h3 className="text-lg font-bold text-gray-800 mb-4">Thông tin khách hàng</h3>
                            <div className="space-y-3">
                                <div className="flex items-center gap-3">
                                    <FiUser className="text-gray-500" />
                                    <span>{orderData.customer.first_name} {orderData.customer.last_name}</span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <FiMail className="text-gray-500" />
                                    <span>{orderData.customer.email}</span>
                                </div>
                                {orderData.customer.phone && (
                                    <div className="flex items-center gap-3">
                                        <FiPhone className="text-gray-500" />
                                        <span>{orderData.customer.phone}</span>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm p-6">
                            <h3 className="text-lg font-bold text-gray-800 mb-4">Địa chỉ giao hàng</h3>
                            <div className="flex items-start gap-3">
                                <FiMapPin className="text-gray-500 mt-1" />
                                <div>
                                    <p className="font-medium">{orderData.address.line}</p>
                                    <p className="text-gray-600">{orderData.address.street}, {orderData.address.ward}</p>
                                    <p className="text-gray-600">{orderData.address.district}, {orderData.address.city}</p>
                                    <p className="text-gray-600">{orderData.address.country}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
                    <button
                        onClick={() => navigate('/my-orders')}
                        className="px-8 py-3 bg-[#ff5252] text-white font-medium rounded-lg hover:bg-[#e53e3e] transition-colors cursor-pointer"
                    >
                        {isFromSuccessRoute ? 'Theo dõi đơn hàng' : 'Quay lại đơn hàng'}
                    </button>
                    <button
                        onClick={() => navigate('/')}
                        className="px-8 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 transition-colors cursor-pointer"
                    >
                        Tiếp tục mua sắm
                    </button>
                </div>
            </div>
        </div>
    );
};

export default OrderSuccessPage;