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

            console.log('Current URL:', window.location.href);
            console.log('Search params:', window.location.search);

            const urlParams = new URLSearchParams(window.location.search);
            const encodedData = urlParams.get('data');
            const errorParam = urlParams.get('error');
            const sessionId = urlParams.get('session_id');

            if (errorParam) {
                throw new Error(decodeURIComponent(errorParam));
            }

            if (encodedData) {
                try {
                    const decodedData = atob(encodedData);
                    const paymentData = JSON.parse(decodedData);
                    setPaymentResult(paymentData);
                    return;
                } catch (decodeError) {
                    console.error('Error decoding payment data:', decodeError);
                    throw new Error('Không thể giải mã thông tin thanh toán');
                }
            }

            if (sessionId) {
                const result = await getDataApi(`/customer/vnpay/payment_result/${sessionId}`);

                if (result.success && result.data?.payment) {
                    setPaymentResult(result.data.payment);
                    return;
                } else {
                    throw new Error(result.message || 'Không thể lấy thông tin thanh toán');
                }
            }

            if (urlParams.get('vnp_TxnRef')) {
                const directResult = {
                    order_code: urlParams.get('vnp_TxnRef'),
                    amount: parseInt(urlParams.get('vnp_Amount') || '0') / 100,
                    response_code: urlParams.get('vnp_ResponseCode'),
                    transaction_no: urlParams.get('vnp_TransactionNo'),
                    status: urlParams.get('vnp_ResponseCode') === '00' ? 'success' : 'failed',
                    order_info: urlParams.get('vnp_OrderInfo') || '',
                    already_processed: false
                };

                setPaymentResult(directResult);
                return;
            }

            throw new Error('Không tìm thấy thông tin thanh toán trong URL');
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
        window.location.href = '/my-orders';
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
                    button: 'from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 cursor-pointer'
                };
            case 'failed':
                return {
                    bg: 'from-red-50 to-rose-50',
                    border: 'border-red-200',
                    text: 'text-red-800',
                    button: 'from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 cursor-pointer'
                };
            default:
                return {
                    bg: 'from-yellow-50 to-amber-50',
                    border: 'border-yellow-200',
                    text: 'text-yellow-800',
                    button: 'from-yellow-600 to-yellow-700 hover:from-yellow-700 hover:to-yellow-800 cursor-pointer'
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

    const formatAmount = (amount) => {
        if (!amount) return '0';
        return parseInt(amount).toLocaleString('vi-VN') + ' VND';
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
                                    className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-blue-800 transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer"
                                >
                                    <FiRefreshCw className="w-5 h-5" />
                                    Thử lại ({retryCount + 1}/{maxRetries})
                                </button>
                            )}

                            <button
                                onClick={handleGoHome}
                                className="w-full bg-gradient-to-r from-gray-600 to-gray-700 text-white py-3 rounded-xl font-semibold hover:from-gray-700 hover:to-gray-800 transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer"
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
                            className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-blue-800 transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer"
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
        <div className={`min-h-screen bg-gradient-to-br ${statusConfig.bg} flex items-center justify-center`}>
            <div className={`bg-white rounded-2xl shadow-xl p-8 max-w-lg w-full mx-4 border-2 ${statusConfig.border}`}>
                <div className="text-center mb-8">
                    <div className='ml-47'>{getStatusIcon(paymentResult.status)}</div>

                    <h1 className={`text-3xl font-bold ${statusConfig.text} mt-4 mb-2`}>
                        {isSuccess ? 'Thanh toán thành công!' : 'Thanh toán không thành công'}
                    </h1>

                    <p className={`${statusConfig.text} text-lg`}>
                        {getResponseCodeMessage(paymentResult.response_code)}
                    </p>
                </div>

                <div className="bg-gray-50 rounded-xl p-6 mb-8 space-y-4">
                    <div className="flex justify-between items-center py-2 border-b border-gray-200">
                        <span className="text-gray-600 font-medium">Mã đơn hàng:</span>
                        <span className="font-semibold text-gray-800">{paymentResult.order_code}</span>
                    </div>

                    <div className="flex justify-between items-center py-2 border-b border-gray-200">
                        <span className="text-gray-600 font-medium">Số tiền:</span>
                        <span className="font-semibold text-gray-800">{formatAmount(paymentResult.amount)}</span>
                    </div>

                    <div className="flex justify-between items-center py-2 border-b border-gray-200">
                        <span className="text-gray-600 font-medium">Mã giao dịch:</span>
                        <span className="font-semibold text-gray-800">{paymentResult.transaction_no || 'N/A'}</span>
                    </div>

                    <div className="flex justify-between items-center py-2 border-b border-gray-200">
                        <span className="text-gray-600 font-medium">Mã phản hồi:</span>
                        <span className="font-semibold text-gray-800">{paymentResult.response_code}</span>
                    </div>

                    {paymentResult.order_info && (
                        <div className="flex justify-between items-start py-2">
                            <span className="text-gray-600 font-medium">Thông tin đơn hàng:</span>
                            <span className="font-semibold text-gray-800 text-right max-w-xs break-words">
                                {paymentResult.order_info}
                            </span>
                        </div>
                    )}

                    {paymentResult.already_processed && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mt-4">
                            <p className="text-yellow-800 text-sm font-medium">
                                ⚠️ Giao dịch này đã được xử lý trước đó
                            </p>
                        </div>
                    )}
                </div>

                <div className="space-y-3">
                    {isSuccess && (
                        <button
                            onClick={handleViewOrders}
                            className={`w-full bg-gradient-to-r ${statusConfig.button} text-white py-3 rounded-xl font-semibold transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer`}
                        >
                            Xem đơn hàng
                        </button>
                    )}

                    <button
                        onClick={handleGoHome}
                        className="w-full bg-gradient-to-r from-gray-600 to-gray-700 text-white py-3 rounded-xl font-semibold hover:from-gray-700 hover:to-gray-800 transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer"
                    >
                        <FiHome className="w-5 h-5" />
                        Về trang chủ
                    </button>
                </div>
            </div>
        </div>
    );
};

export default PaymentReturn;

