import { BsFillBagCheckFill } from "react-icons/bs";
import Button from "@mui/material/Button";
import CartItems from "./cartItem";
import { useContext, useState } from "react";
import { MyContext } from "../../App";
import SpecialOffersOrder from "./specialOffer";
import { FiArrowLeft, FiCheck, FiHome, FiMapPin, FiPlus, FiTag, FiX } from "react-icons/fi";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { getDataApi, postDataApi } from "../../utils/api";

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
    const [isAddressPopupOpen, setIsAddressPopupOpen] = useState(false);
    const [addresses, setAddresses] = useState([]);
    const [loadingAddresses, setLoadingAddresses] = useState(false);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [newAddress, setNewAddress] = useState({
        line: '',
        street: '',
        ward: '',
        district: '',
        city: '',
        country: 'Việt Nam'
    });
    const [creatingAddress, setCreatingAddress] = useState(false);
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

    const fetchAddresses = async () => {
        try {
            setLoadingAddresses(true);
            const response = await getDataApi('/customer/address');

            if (response.success) {
                const addressList = response.data?.data || response.data || [];
                setAddresses(addressList);

                if (setSelectedAddress && typeof setSelectedAddress === 'function' && !selectedAddress && addressList.length > 0) {
                    const defaultAddress = addressList.find(addr => addr.is_default) || addressList[0];
                    setSelectedAddress(defaultAddress);
                }
            } else {
                toast.error(response.message || 'Không thể tải danh sách địa chỉ');
            }
        } catch (error) {
            console.error('Error fetching addresses:', error);
            toast.error('Có lỗi xảy ra khi tải địa chỉ');
        } finally {
            setLoadingAddresses(false);
        }
    };

    const handleCreateAddress = async (e) => {
        e.preventDefault();

        if (!newAddress.line.trim() || !newAddress.ward.trim() ||
            !newAddress.district.trim() || !newAddress.city.trim()) {
            toast.error('Vui lòng điền đầy đủ thông tin bắt buộc!');
            return;
        }

        try {
            setCreatingAddress(true);

            const addressData = {
                line: newAddress.line.trim(),
                street: newAddress.street.trim() || '',
                ward: newAddress.ward.trim(),
                district: newAddress.district.trim(),
                city: newAddress.city.trim(),
                country: newAddress.country.trim() || 'Việt Nam'
            };

            const response = await postDataApi('/customer/address', addressData);

            if (response.success) {
                toast.success('Tạo địa chỉ thành công!');

                setNewAddress({
                    line: '',
                    street: '',
                    ward: '',
                    district: '',
                    city: '',
                    country: 'Việt Nam'
                });

                setShowCreateForm(false);

                await fetchAddresses();

                if (setSelectedAddress && typeof setSelectedAddress === 'function' && addresses.length === 0 && response.data) {
                    setSelectedAddress(response.data);
                }
            } else {
                toast.error(response.data?.message || 'Không thể tạo địa chỉ mới');
            }
        } catch (error) {
            console.error('Error creating address:', error);
            toast.error('Có lỗi xảy ra khi tạo địa chỉ');
        } finally {
            setCreatingAddress(false);
        }
    };

    const handleOpenAddressPopup = () => {
        setIsAddressPopupOpen(true);
        fetchAddresses();
    };

    const handleCloseAddressPopup = () => {
        setIsAddressPopupOpen(false);
        setShowCreateForm(false);
        setNewAddress({
            line: '',
            street: '',
            ward: '',
            district: '',
            city: '',
            country: 'Việt Nam'
        });
    };

    const handleSelectAddress = (address) => {
        setSelectedAddress(address);
        toast.success('Đã chọn địa chỉ giao hàng');
        handleCloseAddressPopup();
    };

    const handleNewAddressChange = (field, value) => {
        setNewAddress(prev => ({
            ...prev,
            [field]: value
        }));
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

            const orderData = {
                special_offer_id: selectedVoucher?.id || null,
                note: orderNote.trim() || null,
                order_detail: orderDetail,
                address_id: selectedAddress.id
            };

            console.log('Order data:', orderData);

            const response = await postDataApi('/customer/order', orderData);

            if (response.success) {
                const orderInfo = {
                    ...response.data,
                    created_at: new Date().toISOString()
                };

                localStorage.setItem('latest_order', JSON.stringify(orderInfo));

                toast.success('Đặt hàng thành công!');

                navigate(`/order-success/${response.data.order_id}`);
            } else {
                toast.error(response.data?.message || 'Đặt hàng thất bại!');
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
                                <p className="text-xs text-gray-500">(không bắt buộc)</p>
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
                            <span className="font-bold">Việt Nam</span>
                        </p>

                        {selectedAddress ? (
                            <div className="border-t border-[rgba(0,0,0,0.1)] pt-3 mt-3">
                                <p className="flex items-center justify-between mb-2">
                                    <span className="text-[14px] font-[500]">Giao đến</span>
                                    <button
                                        className="text-[#ff5252] text-sm underline cursor-pointer"
                                        onClick={handleOpenAddressPopup}
                                    >
                                        Thay đổi
                                    </button>
                                </p>
                                <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                                    <p className="font-medium">{selectedAddress.line}</p>
                                    <p>{selectedAddress.street}, {selectedAddress.ward}</p>
                                    <p>{selectedAddress.district}, {selectedAddress.city}</p>
                                </div>
                            </div>
                        ) : (
                            <div className="border-t border-[rgba(0,0,0,0.1)] pt-3 mt-3">
                                <button
                                    className="w-full text-[#ff5252] text-sm border border-[#ff5252] rounded py-2 cursor-pointer hover:bg-[#ff5252] hover:text-white transition-colors"
                                    onClick={handleOpenAddressPopup}
                                >
                                    Chọn địa chỉ giao hàng
                                </button>
                            </div>
                        )}

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

                        <br />
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

            {isAddressPopupOpen && (
                <div
                    className="fixed inset-0 flex items-center justify-center z-50 p-4"
                    style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}
                >
                    <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
                        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-[#ff5252] to-[#ff8a80] text-white">
                            <div className="flex items-center gap-3">
                                <FiMapPin className="text-2xl" />
                                <h2 className="text-xl font-bold">
                                    {showCreateForm ? 'Thêm địa chỉ mới' : 'Chọn địa chỉ giao hàng'}
                                </h2>
                            </div>
                            <button
                                onClick={handleCloseAddressPopup}
                                className="p-2 hover:bg-white/20 rounded-full transition-colors cursor-pointer"
                            >
                                <FiX className="text-xl" />
                            </button>
                        </div>

                        <div className="p-6 overflow-y-auto max-h-[70vh]">
                            {!showCreateForm ? (
                                <div>
                                    <div className="flex justify-between items-center mb-4">
                                        <h3 className="text-lg font-semibold">Địa chỉ của bạn</h3>
                                        <button
                                            onClick={() => setShowCreateForm(true)}
                                            className="flex items-center gap-2 px-4 py-2 bg-[#ff5252] text-white rounded-lg font-medium hover:bg-[#e53e3e] transition-colors cursor-pointer"
                                        >
                                            <FiPlus className="text-sm" />
                                            Thêm địa chỉ mới
                                        </button>
                                    </div>

                                    {loadingAddresses ? (
                                        <div className="text-center py-12">
                                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#ff5252] mx-auto mb-4"></div>
                                            <div className="text-gray-500">Đang tải địa chỉ...</div>
                                        </div>
                                    ) : addresses.length === 0 ? (
                                        <div className="text-center py-12">
                                            <FiMapPin className="text-6xl text-gray-300 mx-auto mb-4" />
                                            <div className="text-gray-500 text-lg mb-4">Chưa có địa chỉ nào</div>
                                            <button
                                                onClick={() => setShowCreateForm(true)}
                                                className="px-6 py-2 bg-[#ff5252] text-white rounded-lg font-medium hover:bg-[#e53e3e] transition-colors cursor-pointer"
                                            >
                                                Thêm địa chỉ đầu tiên
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="space-y-3">
                                            {addresses.map((address) => {
                                                const isSelected = selectedAddress?.id === address.id;
                                                return (
                                                    <div
                                                        key={address.id}
                                                        className={`relative border-2 rounded-lg p-4 cursor-pointer transition-all duration-200 hover:shadow-md ${isSelected
                                                            ? 'border-[#ff5252] bg-[#ff5252]/5 shadow-md'
                                                            : 'border-gray-200 hover:border-[#ff5252]/50'
                                                            }`}
                                                        onClick={() => handleSelectAddress(address)}
                                                    >
                                                        {isSelected && (
                                                            <div className="absolute top-3 right-3 w-6 h-6 bg-[#ff5252] rounded-full flex items-center justify-center">
                                                                <FiCheck className="text-white text-sm" />
                                                            </div>
                                                        )}

                                                        <div className="pr-8">
                                                            <div className="flex items-center gap-2 mb-2">
                                                                <FiHome className="text-[#ff5252] text-lg" />
                                                                {address.is_default && (
                                                                    <span className="text-xs font-medium px-2 py-1 rounded-full bg-green-100 text-green-600">
                                                                        Mặc định
                                                                    </span>
                                                                )}
                                                            </div>
                                                            <p className="font-semibold text-gray-800 mb-1">{address.line}</p>
                                                            <p className="text-gray-600 text-sm mb-1">
                                                                {address.street}, {address.ward}
                                                            </p>
                                                            <p className="text-gray-600 text-sm">
                                                                {address.district}, {address.city}, {address.country}
                                                            </p>
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div>
                                    <button
                                        onClick={() => setShowCreateForm(false)}
                                        className="flex items-center gap-2 text-gray-600 hover:text-[#ff5252] mb-4 cursor-pointer"
                                    >
                                        <FiArrowLeft className="text-sm" />
                                        Quay lại danh sách
                                    </button>

                                    <form onSubmit={handleCreateAddress} className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Số nhà, tên đường...
                                            </label>
                                            <input
                                                type="text"
                                                value={newAddress.line}
                                                onChange={(e) => handleNewAddressChange('line', e.target.value)}
                                                placeholder=""
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-[#ff5252] focus:ring-2 focus:ring-[#ff5252]/20"
                                                required
                                            />
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Phường/Xã *
                                            </label>
                                            <input
                                                type="text"
                                                value={newAddress.ward}
                                                onChange={(e) => handleNewAddressChange('ward', e.target.value)}
                                                placeholder=""
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-[#ff5252] focus:ring-2 focus:ring-[#ff5252]/20"
                                                required
                                            />
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Quận/Huyện *
                                                </label>
                                                <input
                                                    type="text"
                                                    value={newAddress.district}
                                                    onChange={(e) => handleNewAddressChange('district', e.target.value)}
                                                    placeholder=""
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-[#ff5252] focus:ring-2 focus:ring-[#ff5252]/20"
                                                    required
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Tỉnh/Thành phố *
                                                </label>
                                                <input
                                                    type="text"
                                                    value={newAddress.city}
                                                    onChange={(e) => handleNewAddressChange('city', e.target.value)}
                                                    placeholder=""
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-[#ff5252] focus:ring-2 focus:ring-[#ff5252]/20"
                                                    required
                                                />
                                            </div>
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Đường/Khu vực
                                            </label>
                                            <input
                                                type="text"
                                                value={newAddress.street}
                                                onChange={(e) => handleNewAddressChange('street', e.target.value)}
                                                placeholder=""
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-[#ff5252] focus:ring-2 focus:ring-[#ff5252]/20"
                                            />
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Quốc gia
                                            </label>
                                            <input
                                                type="text"
                                                value={newAddress.country}
                                                onChange={(e) => handleNewAddressChange('country', e.target.value)}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-[#ff5252] focus:ring-2 focus:ring-[#ff5252]/20"
                                            />
                                        </div>

                                        <div className="flex gap-3 pt-4">
                                            <button
                                                type="button"
                                                onClick={() => setShowCreateForm(false)}
                                                className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition-colors cursor-pointer"
                                            >
                                                Hủy
                                            </button>
                                            <button
                                                type="submit"
                                                disabled={creatingAddress}
                                                className="flex-1 px-4 py-2 bg-[#ff5252] text-white rounded-lg font-medium hover:bg-[#e53e3e] transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                                            >
                                                {creatingAddress ? (
                                                    <div className="flex items-center justify-center gap-2">
                                                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                                        Đang tạo...
                                                    </div>
                                                ) : (
                                                    'Tạo địa chỉ'
                                                )}
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </section>
    );
};

export default CartPage;