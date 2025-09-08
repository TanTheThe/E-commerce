import React, { useState, useEffect } from 'react';
import {
    FiCheck,
    FiX,
    FiClock,
    FiCreditCard,
    FiHome,
    FiFileText,
    FiRefreshCw,
    FiAlertCircle
} from 'react-icons/fi';
import { getDataApi } from "../../utils/api";

const PaymentReturn = () => {
    const [paymentResult, setPaymentResult] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [retryCount, setRetryCount] = useState(0);
    const maxRetries = 3;

    const fetchPaymentResult = async () => {
        try {
            setLoading(true);
            setError(null);

            const result = await getDataApi('/customer/vnpay/payment_return');

            if (result.success && result.data?.payment) {
                setPaymentResult(result.data.payment);
            } else {
                throw new Error(result.data?.message || result.message || 'Không thể lấy thông tin thanh toán');
            }
        } catch (error) {
            console.error('Payment return error:', error);
            setError(error.message || 'Có lỗi xảy ra khi xử lý kết quả thanh toán');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPaymentResult();
    }, []);

    const handleRetry = () => {
        if (retryCount < maxRetries) {
            setRetryCount(prev => prev + 1);
            fetchPaymentResult();
        }
    };

    const handleGoHome = () => {
        localStorage.removeItem('paymentData');
        localStorage.removeItem('currentPayment');

        window.location.href = '/';
    };

    const handleViewOrders = () => {
        // Redirect to orders page
        window.location.href = '/orders'; // Adjust as needed
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'success':
                return <FiCheck className="w-16 h-16 text-green-500" />;
            case 'failed':
                return <FiX className="w-16 h-16 text-red-500" />;
            default:
                return <FiClock className="w-16 h-16 text-yellow-500" />;
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'success':
                return {
                    bg: 'from-green-50 to-emerald-50',
                    border: 'border-green-200',
                    text: 'text-green-800',
                    button: 'from-green-600 to-green-700 hover:from-green-700 hover:to-green-800'
                };
            case 'failed':
                return {
                    bg: 'from-red-50 to-rose-50',
                    border: 'border-red-200',
                    text: 'text-red-800',
                    button: 'from-red-600 to-red-700 hover:from-red-700 hover:to-red-800'
                };
            default:
                return {
                    bg: 'from-yellow-50 to-amber-50',
                    border: 'border-yellow-200',
                    text: 'text-yellow-800',
                    button: 'from-yellow-600 to-yellow-700 hover:from-yellow-700 hover:to-yellow-800'
                };
        }
    };

    const getResponseCodeMessage = (responseCode) => {
        const codes = {
            '00': 'Giao dịch thành công',
            '07': 'Trừ tiền thành công. Giao dịch bị nghi ngờ (liên quan tới lừa đảo, giao dịch bất thường)',
            '09': 'Thẻ/Tài khoản của khách hàng chưa đăng ký dịch vụ InternetBanking tại ngân hàng',
            '10': 'Khách hàng xác thực thông tin thẻ/tài khoản không đúng quá 3 lần',
            '11': 'Đã hết hạn chờ thanh toán. Xin quý khách vui lòng thực hiện lại giao dịch',
            '12': 'Thẻ/Tài khoản của khách hàng bị khóa',
            '13': 'Quý khách nhập sai mật khẩu xác thực giao dịch (OTP)',
            '24': 'Khách hàng hủy giao dịch',
            '51': 'Tài khoản của quý khách không đủ số dư để thực hiện giao dịch',
            '65': 'Tài khoản của Quý khách đã vượt quá hạn mức giao dịch trong ngày',
            '75': 'Ngân hàng thanh toán đang bảo trì',
            '79': 'KH nhập sai mật khẩu thanh toán quá số lần quy định',
            '99': 'Lỗi không xác định'
        };

        return codes[responseCode] || `Mã lỗi: ${responseCode}`;
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
                <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full mx-4">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
                        <h2 className="text-2xl font-bold text-gray-800 mb-2">Đang xử lý kết quả</h2>
                        <p className="text-gray-600">Vui lòng chờ trong giây lát...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-red-50 to-rose-100 flex items-center justify-center">
                <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full mx-4">
                    <div className="text-center">
                        <FiAlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                        <h2 className="text-2xl font-bold text-gray-800 mb-2">Có lỗi xảy ra</h2>
                        <p className="text-gray-600 mb-6">{error}</p>

                        <div className="space-y-3">
                            {retryCount < maxRetries && (
                                <button
                                    onClick={handleRetry}
                                    className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-blue-800 transition-all duration-200 flex items-center justify-center gap-2"
                                >
                                    <FiRefreshCw className="w-5 h-5" />
                                    Thử lại ({retryCount + 1}/{maxRetries})
                                </button>
                            )}

                            <button
                                onClick={handleGoHome}
                                className="w-full bg-gradient-to-r from-gray-600 to-gray-700 text-white py-3 rounded-xl font-semibold hover:from-gray-700 hover:to-gray-800 transition-all duration-200 flex items-center justify-center gap-2"
                            >
                                <FiHome className="w-5 h-5" />
                                Về trang chủ
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (!paymentResult) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
                <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full mx-4">
                    <div className="text-center">
                        <FiAlertCircle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
                        <h2 className="text-2xl font-bold text-gray-800 mb-2">Không tìm thấy thông tin</h2>
                        <p className="text-gray-600 mb-6">Không tìm thấy thông tin thanh toán</p>

                        <button
                            onClick={handleGoHome}
                            className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-blue-800 transition-all duration-200 flex items-center justify-center gap-2"
                        >
                            <FiHome className="w-5 h-5" />
                            Về trang chủ
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    const statusConfig = getStatusColor(paymentResult.status);
    const isSuccess = paymentResult.status === 'success';

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
            <div className="container mx-auto max-w-2xl px-4">
                <div className={`bg-gradient-to-br ${statusConfig.bg} rounded-2xl shadow-xl p-8 mb-8 border ${statusConfig.border}`}>
                    <div className="text-center">
                        <div className="mb-6">
                            {getStatusIcon(paymentResult.status)}
                        </div>

                        <h1 className={`text-3xl font-bold ${statusConfig.text} mb-2`}>
                            {isSuccess ? '✅ Thanh toán thành công!' : '❌ Thanh toán thất bại'}
                        </h1>

                        <p className="text-lg text-gray-600 mb-6">
                            {isSuccess
                                ? 'Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi'
                                : getResponseCodeMessage(paymentResult.response_code)
                            }
                        </p>

                        {paymentResult.already_processed && (
                            <div className="bg-blue-100 border border-blue-300 rounded-lg p-3 mb-4">
                                <p className="text-blue-800 text-sm">
                                    ℹ️ Giao dịch này đã được xử lý trước đó
                                </p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
                    <div className="flex items-center gap-3 mb-6 pb-4 border-b">
                        <FiFileText className="text-2xl text-blue-600" />
                        <h2 className="text-xl font-semibold text-gray-800">Chi tiết giao dịch</h2>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-600 mb-1">
                                    Mã đơn hàng
                                </label>
                                <p className="text-lg font-mono bg-gray-50 px-3 py-2 rounded-lg">
                                    {paymentResult.order_code}
                                </p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-600 mb-1">
                                    Số tiền
                                </label>
                                <p className="text-2xl font-bold text-blue-600">
                                    {parseInt(paymentResult.amount || 0).toLocaleString('vi-VN')} VNĐ
                                </p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-600 mb-1">
                                    Trạng thái
                                </label>
                                <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-semibold
                                    ${isSuccess
                                        ? 'bg-green-100 text-green-800'
                                        : 'bg-red-100 text-red-800'
                                    }`}>
                                    {isSuccess ? <FiCheck className="w-4 h-4" /> : <FiX className="w-4 h-4" />}
                                    {isSuccess ? 'Thành công' : 'Thất bại'}
                                </span>
                            </div>
                        </div>

                        <div className="space-y-4">
                            {paymentResult.transaction_no && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-600 mb-1">
                                        Mã giao dịch VNPay
                                    </label>
                                    <p className="text-lg font-mono bg-gray-50 px-3 py-2 rounded-lg">
                                        {paymentResult.transaction_no}
                                    </p>
                                </div>
                            )}

                            <div>
                                <label className="block text-sm font-medium text-gray-600 mb-1">
                                    Mã phản hồi
                                </label>
                                <p className="text-lg font-mono bg-gray-50 px-3 py-2 rounded-lg">
                                    {paymentResult.response_code}
                                </p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-600 mb-1">
                                    Thời gian
                                </label>
                                <p className="text-lg bg-gray-50 px-3 py-2 rounded-lg">
                                    {new Date().toLocaleString('vi-VN')}
                                </p>
                            </div>
                        </div>
                    </div>

                    {paymentResult.order_info && (
                        <div className="mt-6 pt-4 border-t">
                            <label className="block text-sm font-medium text-gray-600 mb-2">
                                Nội dung thanh toán
                            </label>
                            <p className="text-gray-800 bg-gray-50 px-4 py-3 rounded-lg">
                                {paymentResult.order_info}
                            </p>
                        </div>
                    )}
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                    <button
                        onClick={handleViewOrders}
                        className="bg-gradient-to-r from-blue-600 to-blue-700 text-white py-4 rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 flex items-center justify-center gap-3"
                    >
                        <FiFileText className="text-xl" />
                        Xem đơn hàng
                    </button>

                    <button
                        onClick={handleGoHome}
                        className="bg-gradient-to-r from-gray-600 to-gray-700 text-white py-4 rounded-xl font-semibold text-lg hover:from-gray-700 hover:to-gray-800 transition-all duration-200 flex items-center justify-center gap-3"
                    >
                        <FiHome className="text-xl" />
                        Về trang chủ
                    </button>
                </div>

                <div className="mt-8 bg-gray-50 rounded-2xl p-6">
                    <h3 className="font-semibold text-gray-800 mb-3">Cần hỗ trợ?</h3>
                    <div className="grid md:grid-cols-2 gap-4 text-sm">
                        <div>
                            <p className="text-gray-600 mb-2">Liên hệ hỗ trợ khách hàng:</p>
                            <p><strong>Hotline:</strong> 1900 1234</p>
                            <p><strong>Email:</strong> support@yourstore.com</p>
                        </div>
                        <div>
                            <p className="text-gray-600 mb-2">Hỗ trợ VNPay:</p>
                            <p><strong>Hotline VNPay:</strong> 1900 555 577</p>
                            <p><strong>Website:</strong> vnpay.vn</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PaymentReturn;

