import { BsFillBagCheckFill } from "react-icons/bs";
import Button from "@mui/material/Button";
import CartItems from "./cartItem";
import { useContext, useEffect, useState } from "react";
import { MyContext } from "../../App";
import SpecialOffersOrder from "./specialOffer";
import { FiArrowLeft, FiCheck, FiHome, FiMapPin, FiPlus, FiTag, FiX } from "react-icons/fi";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { getDataApi, postDataApi } from "../../utils/api";
import AddressManager from "../../components/Address";

const CartPage = () => {
    const {
        checkoutItems,
        checkoutTotal,
        selectedVoucher,
        setSelectedVoucher,
        selectedAddress,
        setSelectedAddress
    } = useContext(MyContext);

    const [isCheckingOut, setIsCheckingOut] = useState(false);
    const [orderNote, setOrderNote] = useState('');
    const [paymentMethod, setPaymentMethod] = useState('cod');
    const [onlinePaymentMethod, setOnlinePaymentMethod] = useState('vnpay');

    const [isAddressManagerOpen, setIsAddressManagerOpen] = useState(false);

    const navigate = useNavigate();

    const shippingFee = 0;
    const subtotal = checkoutTotal || 0;

    const calculateDiscount = (subtotal, voucher) => {
        if (!voucher || subtotal < voucher.condition) return 0;

        if (voucher.type === 'percent') {
            return Math.min((subtotal * voucher.discount) / 100, voucher.max_discount || Infinity);
        } else if (voucher.type === 'fixed') {
            return Math.min(voucher.discount, subtotal);
        }
        return 0;
    };

    const discount = calculateDiscount(subtotal, selectedVoucher);
    const finalTotal = subtotal - discount + shippingFee;

    const isVoucherValid = selectedVoucher && subtotal >= selectedVoucher.condition;

    const removeVoucher = () => {
        setSelectedVoucher(null);
        toast.success('Đã gỡ voucher');
    };

    const handleOpenAddressManager = () => {
        setIsAddressManagerOpen(true);
    };

    const handleCloseAddressManager = () => {
        setIsAddressManagerOpen(false);
    };

    const handleSelectAddress = (address) => {
        setSelectedAddress(address);
    };

    const handleCheckout = async () => {
        try {
            if (!checkoutItems || checkoutItems.length === 0) {
                toast.error('Giỏ hàng trống!');
                return;
            }

            if (!selectedAddress) {
                toast.error('Vui lòng chọn địa chỉ giao hàng!');
                return;
            }

            setIsCheckingOut(true);

            const orderDetail = checkoutItems.map(item => ({
                quantity: item.quantity,
                product_variant_id: item.product_variant_id || item.variant_id
            }));

            let paymentMethodValue;
            if (paymentMethod === 'cod') {
                paymentMethodValue = 'direct';
            } else if (paymentMethod === 'online') {
                paymentMethodValue = 'vnpay';
            }

            const orderData = {
                special_offer_id: selectedVoucher?.id || null,
                note: orderNote.trim() || null,
                payment_method: paymentMethodValue,
                order_detail: orderDetail,
                address_id: selectedAddress.id
            };

            const response = await postDataApi('/customer/order', orderData);

            if (response.success) {
                const orderCode = response.data.order_code;

                const paymentData = {
                    orderCode: orderCode,
                    amount: finalTotal.toString(),
                    orderItems: checkoutItems,
                    address: selectedAddress,
                    voucher: selectedVoucher,
                    note: orderNote
                };

                localStorage.setItem('paymentData', JSON.stringify(paymentData));

                toast.success('Đặt hàng thành công! Đang chuyển đến trang thanh toán...');

                if (paymentMethod === 'cod') {
                    navigate(`/order-success/${response.data.order_id}`);
                } else {
                    navigate(`/payment/${orderCode}`);
                }
            } else {
                toast.error(response.data.detail.message || 'Đặt hàng thất bại!');
            }

        } catch (error) {
            console.error('Checkout error:', error);
            toast.error('Có lỗi xảy ra khi đặt hàng!');
        } finally {
            setIsCheckingOut(false);
        }
    };

    return (
        <section className="section py-10 pb-10">
            <div className="container w-[80%] max-w-[80%] flex gap-5">
                <div className="leftPart w-[70%]">
                    <div className="shadow-md rounded-md bg-white">
                        <div className="py-2 px-3 border-b border-[rgba(0,0,0,0.1)]">
                            <h2>Your Cart</h2>
                            <p className="mt-0">There are
                                <span className="font-bold text-[#ff5252]"> {checkoutItems.length} </span>
                                products in your cart
                            </p>
                            <SpecialOffersOrder />
                        </div>
                        <CartItems />

                        <div className="py-4 px-3 border-t border-[rgba(0,0,0,0.1)]">
                            <div className="flex items-center gap-2 mb-3">
                                <h3 className="text-lg font-semibold">Ghi chú đơn hàng</h3>
                                <p className="text-xs text-gray-500">(không bắt buộc)</p>
                            </div>
                            <textarea
                                value={orderNote}
                                onChange={(e) => setOrderNote(e.target.value)}
                                placeholder=""
                                className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:border-[#ff5252] focus:ring-2 focus:ring-[#ff5252]/20 resize-none"
                                rows="3"
                                maxLength="500"
                            />
                            <div className="text-xs text-gray-500 mt-1 text-right">
                                {orderNote.length}/500 ký tự
                            </div>
                        </div>
                    </div>
                </div>

                <div className="rightPart w-[30%]">
                    <div className="shadow-md rounded-md bg-white p-5">
                        <h3 className="pb-3 border-b border-[rgba(0,0,0,0.1)]">Cart Totals</h3>

                        <p className="flex items-center justify-between">
                            <span className="text-[14px] font-[500]">Subtotal</span>
                            <span className="text-[#ff5252] font-bold">
                                {subtotal?.toLocaleString('vi-VN')}đ
                            </span>
                        </p>

                        <p className="flex items-center justify-between">
                            <span className="text-[14px] font-[500]">Shipping</span>
                            <span className="font-bold">Free</span>
                        </p>

                        {selectedVoucher && (
                            <div className="border-t border-[rgba(0,0,0,0.1)] pt-3 mt-3">
                                <div className="mb-2">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-[14px] font-[500] text-green-600">Voucher Applied</span>
                                        <button
                                            onClick={removeVoucher}
                                            className="text-gray-400 hover:text-red-500 transition-colors cursor-pointer"
                                            title="Remove voucher"
                                        >
                                            <FiX size={16} />
                                        </button>
                                    </div>

                                    <div className={`${isVoucherValid ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'} border rounded-lg p-3`}>
                                        <div className="flex items-center gap-2 mb-1">
                                            <FiTag className={`${isVoucherValid ? 'text-green-600' : 'text-red-600'} text-sm`} />
                                            <span className={`text-sm font-medium ${isVoucherValid ? 'text-green-800' : 'text-red-800'}`}>
                                                #{selectedVoucher.code}
                                            </span>
                                        </div>
                                        <p className={`text-xs ${isVoucherValid ? 'text-green-700' : 'text-red-700'} mb-1`}>
                                            {selectedVoucher.name}
                                        </p>

                                        {!isVoucherValid && (
                                            <p className="text-xs text-red-600">
                                                Cần mua thêm {(selectedVoucher.condition - subtotal).toLocaleString('vi-VN')}đ để áp dụng
                                            </p>
                                        )}
                                    </div>
                                </div>

                                <p className="flex items-center justify-between">
                                    <span className="text-[14px] font-[500]">Discount</span>
                                    <span className="text-green-600 font-bold">
                                        -{discount?.toLocaleString('vi-VN')}đ
                                    </span>
                                </p>
                            </div>
                        )}

                        <p className="flex items-center justify-between">
                            <span className="text-[14px] font-[500]">Estimate for</span>
                            <span className="font-bold">Việt Nam</span>
                        </p>

                        {selectedAddress ? (
                            <div className="border-t border-[rgba(0,0,0,0.1)] pt-3 mt-3">
                                <p className="flex items-center justify-between mb-2">
                                    <span className="text-[14px] font-[500]">Giao đến</span>
                                    <button
                                        className="text-[#ff5252] text-sm underline cursor-pointer hover:text-[#e53e3e] transition-colors"
                                        onClick={handleOpenAddressManager}
                                    >
                                        Thay đổi
                                    </button>
                                </p>
                                <div className="text-sm text-gray-600 bg-gradient-to-br from-gray-50 to-gray-100 p-3 rounded-lg border border-gray-200">
                                    <p className="font-semibold text-gray-800 mb-1">{selectedAddress.line}</p>
                                    <p className="text-gray-600">
                                        {selectedAddress.ward_info?.name}, {selectedAddress.province_info?.name}
                                    </p>
                                    <p className="text-gray-500 text-xs mt-1">{selectedAddress.country}</p>
                                </div>
                            </div>
                        ) : (
                            <div className="border-t border-[rgba(0,0,0,0.1)] pt-3 mt-3">
                                <button
                                    className="w-full text-[#ff5252] text-sm border border-[#ff5252] rounded py-2 cursor-pointer hover:bg-[#ff5252] hover:text-white transition-colors"
                                    onClick={handleOpenAddressManager}
                                >
                                    Chọn địa chỉ giao hàng
                                </button>
                            </div>
                        )}

                        <div className="border-t border-[rgba(0,0,0,0.1)] pt-3 mt-3">
                            <h4 className="text-[14px] font-[500] mb-3">Phương thức thanh toán</h4>

                            <div className="flex gap-2 mb-3">
                                <button
                                    type="button"
                                    onClick={() => setPaymentMethod('cod')}
                                    className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors cursor-pointer ${paymentMethod === 'cod'
                                        ? 'bg-[#ff5252] text-white'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                        }`}
                                >
                                    💵 Thanh toán trực tiếp
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setPaymentMethod('online')}
                                    className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors cursor-pointer ${paymentMethod === 'online'
                                        ? 'bg-[#ff5252] text-white'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                        }`}
                                >
                                    🏧 Thanh toán online
                                </button>
                            </div>

                            {paymentMethod === 'cod' && (
                                <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                                    <p className="text-sm text-orange-800">Trả tiền mặt khi nhận được hàng</p>
                                </div>
                            )}

                            {paymentMethod === 'online' && (
                                <div className="space-y-2">
                                    <label className="flex items-center gap-3 cursor-pointer p-3 border border-blue-200 bg-blue-50 rounded-lg">
                                        <input
                                            type="radio"
                                            name="onlinePaymentMethod"
                                            value="vnpay"
                                            checked={onlinePaymentMethod === 'vnpay'}
                                            onChange={(e) => setOnlinePaymentMethod(e.target.value)}
                                            className="w-4 h-4 text-blue-600 focus:ring-blue-500 focus:ring-2"
                                        />
                                        <div>
                                            <p className="font-medium text-sm text-blue-800">VNPay</p>
                                        </div>
                                    </label>
                                </div>
                            )}
                        </div>

                        <div className="border-t border-[rgba(0,0,0,0.1)] pt-3 mt-3">
                            <p className="flex items-center justify-between text-lg">
                                <span className="font-bold">Total</span>
                                <span className="text-[#ff5252] font-bold text-xl">
                                    {finalTotal?.toLocaleString('vi-VN')}đ
                                </span>
                            </p>

                            {discount > 0 && (
                                <p className="text-sm text-green-600 text-right mt-1">
                                    Bạn đã tiết kiệm {discount?.toLocaleString('vi-VN')}đ
                                </p>
                            )}
                        </div>

                        <Button
                            className="btn-org btn-lg w-full flex gap-2"
                            disabled={checkoutItems.length === 0 || isCheckingOut || !selectedAddress}
                            onClick={handleCheckout}
                        >
                            {isCheckingOut ? (
                                <>
                                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                    Đang xử lý...
                                </>
                            ) : (
                                <>
                                    <BsFillBagCheckFill className="text-[20px]" />
                                    Checkout ({checkoutItems.length} items)
                                </>
                            )}
                        </Button>

                        {!selectedAddress && (
                            <p className="text-xs text-red-500 text-center mt-2">
                                * Vui lòng chọn địa chỉ giao hàng
                            </p>
                        )}
                    </div>
                </div>
            </div>

            <AddressManager
                isOpen={isAddressManagerOpen}
                onClose={handleCloseAddressManager}
                selectedAddress={selectedAddress}
                onSelectAddress={handleSelectAddress}
            />
        </section>
    );
};

export default CartPage;