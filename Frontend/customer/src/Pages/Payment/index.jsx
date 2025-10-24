import React, { useState, useEffect } from 'react';
import { FiCreditCard, FiShield, FiArrowLeft, FiLock } from 'react-icons/fi';
import { getDataApi, postDataApi } from "../../utils/api";

const VNPayPayment = () => {
    const [formData, setFormData] = useState({
        order_type: 'billpayment',
        order_code: '',
        amount: '',
        order_desc: '',
        bank_code: '',
        language: 'vn'
    });

    const [isProcessing, setIsProcessing] = useState(false);
    const [validationError, setValidationError] = useState('');

    useEffect(() => {
        const paymentData = JSON.parse(localStorage.getItem('paymentData') || '{}');
        const currentTime = new Date().toLocaleString('vi-VN');

        setFormData(prev => ({
            ...prev,
            order_code: paymentData.orderCode,
            amount: paymentData.amount || '10000',
            order_desc: `Thanh toan don hang thoi gian: ${currentTime}`
        }));
    }, []);

    const handleInputChange = (field, value) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const validateForm = () => {
        if (!formData.order_code) {
            setValidationError('Mã đơn hàng không hợp lệ');
            return false;
        }

        if (!formData.amount || parseInt(formData.amount) < 5000) {
            setValidationError('Số tiền phải từ 5,000 VND trở lên');
            return false;
        }

        if (parseInt(formData.amount) > 1000000000) {
            setValidationError('Số tiền không được vượt quá 1,000,000,000 VND');
            return false;
        }

        if (!formData.bank_code) {
            setValidationError('Vui lòng chọn phương thức thanh toán');
            return false;
        }

        return true;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsProcessing(true);
        setValidationError('');

        if (!validateForm()) {
            setIsProcessing(false);
            return;
        }

        try {
            const result = await postDataApi('/customer/vnpay/payment', formData);
            console.log(result)

            if (result.success && result.data.payment_url) {
                window.location.href = result.data.payment_url;
            } else {
                throw new Error(result.message || 'Payment initiation failed');
            }
        } catch (error) {
            let errorMessage = 'Có lỗi xảy ra khi khởi tạo thanh toán. Vui lòng thử lại.';

            if (error.response?.status === 400) {
                errorMessage = error.response.data?.message || 'Thông tin thanh toán không hợp lệ';
            } else if (error.response?.status === 404) {
                errorMessage = 'Không tìm thấy đơn hàng';
            } else if (error.response?.status === 500) {
                errorMessage = 'Lỗi hệ thống. Vui lòng thử lại sau';
            }

            setValidationError(errorMessage);
        } finally {
            setIsProcessing(false);
        }
    };

    const handleGoBack = () => {
        window.history.back();
    };

    const bankOptions = [
        { value: '', label: 'Chọn phương thức thanh toán' },
        { value: 'NCB', label: 'Ngân hàng NCB' },
        { value: 'AGRIBANK', label: 'Ngân hàng Agribank' },
        { value: 'SCB', label: 'Ngân hàng SCB' },
        { value: 'SACOMBANK', label: 'Ngân hàng Sacombank' },
        { value: 'EXIMBANK', label: 'Ngân hàng EximBank' },
        { value: 'MSBANK', label: 'Ngân hàng MSBANK' },
        { value: 'NAMABANK', label: 'Ngân hàng NamABank' },
        { value: 'VNMART', label: 'Ngân hàng VnMart' },
        { value: 'VIETINBANK', label: 'Ngân hàng VietinBank' },
        { value: 'VIETCOMBANK', label: 'Ngân hàng VCB' },
        { value: 'HDBANK', label: 'Ngân hàng HDBank' },
        { value: 'DONGABANK', label: 'Ngân hàng Dong A' },
        { value: 'TPBANK', label: 'Ngân hàng TPBank' },
        { value: 'OJB', label: 'Ngân hàng OceanBank' },
        { value: 'BIDV', label: 'Ngân hàng BIDV' },
        { value: 'TECHCOMBANK', label: 'Ngân hàng Techcombank' },
        { value: 'VPBANK', label: 'Ngân hàng VPBank' },
        { value: 'MBBANK', label: 'Ngân hàng MB Bank' },
        { value: 'ACB', label: 'Ngân hàng ACB' },
        { value: 'VISA', label: 'Thanh toán qua VISA/MASTER' },
    ];

    const formatAmount = (amount) => {
        if (!amount) return '';
        return parseInt(amount).toLocaleString('vi-VN');
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
            <div className="container mx-auto max-w-4xl px-4">
                <div className="mb-8">
                    <button
                        onClick={handleGoBack}
                        className="flex items-center gap-2 text-gray-600 hover:text-gray-800 mb-4 transition-colors cursor-pointer"
                    >
                        <FiArrowLeft />
                        Quay lại
                    </button>
                    <div className="text-center">
                        <div className="flex items-center justify-center gap-3 mb-2">
                            <FiCreditCard className="text-4xl text-blue-600" />
                            <h1 className="text-3xl font-bold text-gray-800">Thanh toán VNPay</h1>
                        </div>
                        <p className="text-gray-600">Thanh toán an toàn và bảo mật với VNPay</p>
                    </div>
                </div>

                <div className="grid lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2">
                        <div className="bg-white rounded-2xl shadow-xl p-8">
                            <div className="flex items-center gap-3 mb-6 pb-4 border-b">
                                <FiShield className="text-2xl text-green-500" />
                                <h2 className="text-xl font-semibold text-gray-800">Thông tin thanh toán</h2>
                            </div>

                            <div className="space-y-6">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Loại hàng hóa
                                    </label>
                                    <input
                                        type="text"
                                        value="Thanh toán hóa đơn"
                                        disabled
                                        className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-600 cursor-not-allowed"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Mã đơn hàng
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="text"
                                            value={formData.order_code}
                                            disabled
                                            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-800 font-mono cursor-not-allowed pr-10"
                                        />
                                        <FiLock className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Số tiền thanh toán
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="text"
                                            value={`${parseInt(formData.amount || 0).toLocaleString('vi-VN')} VNĐ`}
                                            disabled
                                            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-800 font-semibold text-lg cursor-not-allowed pr-10"
                                        />
                                        <FiLock className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Nội dung thanh toán
                                    </label>
                                    <textarea
                                        value={formData.order_desc}
                                        onChange={(e) => handleInputChange('order_desc', e.target.value)}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                                        rows="3"
                                        placeholder="Nhập mô tả đơn hàng..."
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Phương thức thanh toán
                                    </label>
                                    <select
                                        value={formData.bank_code}
                                        onChange={(e) => {
                                            handleInputChange('bank_code', e.target.value);
                                            setValidationError('');
                                        }}
                                        className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white cursor-pointer ${validationError ? 'border-red-500' : 'border-gray-300'
                                            }`}
                                    >
                                        {bankOptions.map(bank => (
                                            <option key={bank.value} value={bank.value}>
                                                {bank.label}
                                            </option>
                                        ))}
                                    </select>
                                    {validationError && (
                                        <p className="mt-2 text-sm text-red-600 flex items-center gap-1">
                                            <span>⚠️</span>
                                            {validationError}
                                        </p>
                                    )}
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Ngôn ngữ
                                    </label>
                                    <select
                                        value={formData.language}
                                        onChange={(e) => handleInputChange('language', e.target.value)}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                                    >
                                        <option value="vn">Tiếng Việt</option>
                                        <option value="en">English</option>
                                    </select>
                                </div>

                                <button
                                    type="button"
                                    onClick={handleSubmit}
                                    disabled={isProcessing || !formData.order_code || !formData.amount}
                                    className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-4 rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 cursor-pointer"
                                >
                                    {isProcessing ? (
                                        <>
                                            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                                            Đang chuyển hướng đến VNPay...
                                        </>
                                    ) : (
                                        <>
                                            <FiCreditCard className="text-xl" />
                                            Thanh toán ngay
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div className="bg-white rounded-2xl shadow-lg p-6">
                            <h3 className="text-lg font-semibold text-gray-800 mb-4">Thông tin đơn hàng</h3>
                            <div className="space-y-3">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Mã đơn hàng:</span>
                                    <span className="mt-0.5 font-mono text-sm">{formData.order_id}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Thời gian:</span>
                                    <span className="mt-0.5 text-sm">{new Date().toLocaleString('vi-VN')}</span>
                                </div>
                                <hr />
                                <div className="flex justify-between text-lg font-semibold">
                                    <span>Tổng tiền:</span>
                                    <span className="text-blue-600">
                                        {parseInt(formData.amount || 0).toLocaleString('vi-VN')} VNĐ
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 border border-green-200">
                            <div className="flex items-center gap-3 mb-3">
                                <FiShield className="text-2xl text-green-600" />
                                <h3 className="font-semibold text-green-800">Bảo mật thanh toán</h3>
                            </div>
                            <ul className="text-sm text-green-700 space-y-2">
                                <li className="flex items-center gap-2">
                                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                    Mã hóa SSL 256-bit
                                </li>
                                <li className="flex items-center gap-2">
                                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                    Được bảo vệ bởi VNPay
                                </li>
                                <li className="flex items-center gap-2">
                                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                    Tuân thủ chuẩn PCI DSS
                                </li>
                                <li className="flex items-center gap-2">
                                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                    Xác thực 3D Secure
                                </li>
                            </ul>
                        </div>

                        <div className="bg-gray-50 rounded-2xl p-6">
                            <h3 className="font-semibold text-gray-800 mb-3">Hỗ trợ khách hàng</h3>
                            <p className="text-sm text-gray-600 mb-3">
                                Nếu bạn gặp vấn đề trong quá trình thanh toán, vui lòng liên hệ:
                            </p>
                            <div className="text-sm space-y-1">
                                <p><strong>Hotline VNPay:</strong> 1900 555 577</p>
                                <p><strong>Hotline Shop:</strong> 1900 1234</p>
                                <p><strong>Email:</strong> support@yourstore.com</p>
                            </div>
                        </div>

                        {formData.bank_code === 'VISA' && (
                            <div className="bg-blue-50 rounded-2xl p-6 border border-blue-200">
                                <h3 className="font-semibold text-blue-800 mb-3">💳 Thanh toán thẻ quốc tế</h3>
                                <ul className="text-sm text-blue-700 space-y-1">
                                    <li>• Hỗ trợ VISA, Mastercard, JCB</li>
                                    <li>• Có thể yêu cầu xác thực OTP</li>
                                    <li>• Thời gian xử lý: 1-3 phút</li>
                                </ul>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default VNPayPayment;