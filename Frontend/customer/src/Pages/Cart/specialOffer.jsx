import React, { useState, useEffect, useContext } from 'react';
import { toast } from 'react-toastify';
import { FiGift, FiX, FiPercent, FiDollarSign, FiShoppingCart, FiCalendar, FiSearch } from 'react-icons/fi';
import { getDataApi } from "../../utils/api";
import { MyContext } from '../../App';

const SpecialOffersOrder = () => {
    const { selectedVoucher, setSelectedVoucher } = useContext(MyContext);
    const [isPopupOpen, setIsPopupOpen] = useState(false);
    const [offers, setOffers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');

    const fetchOffers = async (search = '') => {
        try {
            setLoading(true);
            const queryParams = new URLSearchParams({
                skip: '0',
                limit: '50',
            });

            if (search) {
                queryParams.append('search', search);
            }

            const response = await getDataApi(`/customer/special-offer?${queryParams.toString()}`);

            if (response.success) {
                const offersData = response.data.content?.data || response.data.data || [];
                setOffers(offersData);
            } else {
                toast.error(response.data.detail.message || 'Không thể tải vouchers');
            }
        } catch (error) {
            console.error('Error fetching offers:', error);
            toast.error('Có lỗi xảy ra khi tải vouchers');
        } finally {
            setLoading(false);
        }
    };

    const handleOpenPopup = () => {
        setIsPopupOpen(true);
        fetchOffers();
    };

    const handleClosePopup = () => {
        setIsPopupOpen(false);
        setSearchTerm('');
        setOffers([]);
    };

    const handleSelectVoucher = (voucher) => {
        if (selectedVoucher?.id === voucher.id) {
            setSelectedVoucher(null);
            toast.success('Đã bỏ chọn voucher');
        } else {
            setSelectedVoucher(voucher);
            toast.success(`Đã chọn voucher: ${voucher.name}`);
        }
    };

    const handleSearch = (e) => {
        const value = e.target.value;
        setSearchTerm(value);

        const timeoutId = setTimeout(() => {
            fetchOffers(value);
        }, 300);

        return () => clearTimeout(timeoutId);
    };

    const formatDiscount = (offer) => {
        if (offer.type === 'percent') {
            return `${offer.discount}%`;
        } else if (offer.type === 'fixed') {
            return `${offer.discount.toLocaleString('vi-VN')}đ`;
        }
        return offer.discount;
    };

    const formatCondition = (condition) => {
        return `${condition.toLocaleString('vi-VN')}đ`;
    };

    const getUsagePercentage = (used, total) => {
        if (total === 0) return 0;
        return Math.min((used / total) * 100, 100);
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('vi-VN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    };

    return (
        <>
            <div className="mt-3">
                <button
                    onClick={handleOpenPopup}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#ff5252] to-[#ff8a80] text-white rounded-lg font-medium hover:from-[#e53e3e] hover:to-[#ff5252] transition-all duration-200 shadow-md hover:shadow-lg cursor-pointer"
                >
                    <FiGift className="text-lg" />
                    <span>Chọn voucher ưu đãi</span>
                    {selectedVoucher && (
                        <span className="ml-2 px-2 py-1 bg-white/20 rounded-full text-xs">
                            {selectedVoucher.code}
                        </span>
                    )}
                </button>
            </div>

            {isPopupOpen && (
                <div
                    className="fixed inset-0 flex items-center justify-center z-50 p-4"
                    style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}
                >
                    <div className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
                        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-[#ff5252] to-[#ff8a80] text-white">
                            <div className="flex items-center gap-3">
                                <FiGift className="text-2xl" />
                                <h2 className="text-xl font-bold">Chọn voucher ưu đãi</h2>
                            </div>
                            <button
                                onClick={handleClosePopup}
                                className="p-2 hover:bg-white/20 rounded-full transition-colors cursor-pointer"
                            >
                                <FiX className="text-xl" />
                            </button>
                        </div>

                        {/* Search */}
                        <div className="p-6 border-b border-gray-200">
                            <div className="relative">
                                <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder="Tìm kiếm voucher theo tên hoặc mã..."
                                    value={searchTerm}
                                    onChange={handleSearch}
                                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-[#ff5252] focus:ring-2 focus:ring-[#ff5252]/20"
                                />
                            </div>
                        </div>

                        <div className="p-6 overflow-y-auto max-h-[60vh]">
                            {loading ? (
                                <div className="text-center py-12">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#ff5252] mx-auto mb-4"></div>
                                    <div className="text-gray-500">Đang tải vouchers...</div>
                                </div>
                            ) : offers.length === 0 ? (
                                <div className="text-center py-12">
                                    <FiGift className="text-6xl text-gray-300 mx-auto mb-4" />
                                    <div className="text-gray-500 text-lg">
                                        {searchTerm ? 'Không tìm thấy voucher nào phù hợp' : 'Chưa có voucher nào khả dụng'}
                                    </div>
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {offers.map((offer) => {
                                        const usagePercentage = getUsagePercentage(offer.used_quantity, offer.total_quantity);
                                        const remainingQuantity = offer.total_quantity - offer.used_quantity;
                                        const isSelected = selectedVoucher?.id === offer.id;

                                        return (
                                            <div
                                                key={offer.id}
                                                className={`relative bg-white border-2 rounded-lg p-5 cursor-pointer transition-all duration-200 hover:shadow-lg ${isSelected
                                                        ? 'border-[#ff5252] bg-[#ff5252]/5 shadow-md'
                                                        : 'border-gray-200 hover:border-[#ff5252]/50'
                                                    }`}
                                                onClick={() => handleSelectVoucher(offer)}
                                            >
                                                {isSelected && (
                                                    <div className="absolute top-3 right-3 w-6 h-6 bg-[#ff5252] rounded-full flex items-center justify-center">
                                                        <div className="w-2 h-2 bg-white rounded-full"></div>
                                                    </div>
                                                )}

                                                <div className="flex items-start justify-between mb-3">
                                                    <div className="flex items-center gap-2">
                                                        {offer.type === 'percent' ? (
                                                            <FiPercent className="text-[#ff5252] text-lg" />
                                                        ) : (
                                                            <FiDollarSign className="text-[#ff5252] text-lg" />
                                                        )}
                                                        <span className="text-sm font-medium text-gray-600">#{offer.code}</span>
                                                    </div>
                                                    <span className="text-xs font-medium px-2 py-1 rounded-full bg-green-100 text-green-600">
                                                        Còn {remainingQuantity}
                                                    </span>
                                                </div>

                                                <h3 className="text-lg font-semibold text-gray-800 mb-2 line-clamp-2">
                                                    {offer.name}
                                                </h3>

                                                <div className="text-2xl font-bold text-[#ff5252] mb-3">
                                                    {formatDiscount(offer)}
                                                    <span className="text-sm font-normal text-gray-500 ml-1">giảm</span>
                                                </div>

                                                <div className="flex items-center gap-2 mb-3">
                                                    <FiShoppingCart className="text-gray-400 text-sm" />
                                                    <span className="text-sm text-gray-600">
                                                        Đơn hàng từ {formatCondition(offer.condition)}
                                                    </span>
                                                </div>

                                                <div className="mb-3">
                                                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                                                        <span>Đã sử dụng: {offer.used_quantity}/{offer.total_quantity}</span>
                                                        <span>{Math.round(usagePercentage)}%</span>
                                                    </div>
                                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                                        <div
                                                            className="bg-gradient-to-r from-[#ff5252] to-[#ff8a80] h-2 rounded-full transition-all duration-300"
                                                            style={{ width: `${usagePercentage}%` }}
                                                        ></div>
                                                    </div>
                                                </div>

                                                <div className="flex items-center gap-2 text-xs text-gray-500">
                                                    <FiCalendar className="text-gray-400" />
                                                    <span>HSD: {formatDate(offer.end_time)}</span>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>

                        <div className="p-6 border-t border-gray-200 bg-gray-50">
                            <div className="flex items-center justify-between">
                                <div className="text-sm text-gray-600">
                                    {offers.length > 0 && (
                                        <span>Tìm thấy <strong>{offers.length}</strong> voucher khả dụng</span>
                                    )}
                                </div>
                                <div className="flex gap-3">
                                    <button
                                        onClick={handleClosePopup}
                                        className="px-6 py-2 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition-colors cursor-pointer"
                                    >
                                        Đóng
                                    </button>

                                    {selectedVoucher && (
                                        <button
                                            onClick={() => {
                                                toast.success(`Đã áp dụng voucher: ${selectedVoucher.name}`);
                                                handleClosePopup();
                                            }}
                                            className="px-6 py-2 bg-[#ff5252] text-white rounded-lg font-medium hover:bg-[#e53e3e] transition-colors cursor-pointer"
                                        >
                                            Áp dụng voucher
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default SpecialOffersOrder;