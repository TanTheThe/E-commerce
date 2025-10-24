const CancelOrderModal = ({ isOpen, onClose, selectedOrder, onSubmit, cancelForm, setCancelForm }) => {
    const cancelReasons = [
        { key: 'change_mind', label: 'Đổi ý không muốn mua nữa' },
        { key: 'found_better_price', label: 'Tìm được nơi bán giá tốt hơn' },
        { key: 'wrong_order', label: 'Đặt nhầm sản phẩm' },
        { key: 'payment_issue', label: 'Vấn đề về thanh toán' },
        { key: 'delivery_time', label: 'Thời gian giao hàng quá lâu' },
        { key: 'other', label: 'Lý do khác' }
    ];

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}>
            <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
                <div className="p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-bold text-gray-800">Hủy đơn hàng</h3>
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-gray-600 text-2xl cursor-pointer"
                        >
                            ×
                        </button>
                    </div>

                    {selectedOrder && (
                        <div className="mb-6">
                            <div className="bg-gray-50 p-4 rounded-lg">
                                <p className="text-sm text-gray-600">Mã đơn hàng</p>
                                <p className="font-bold text-[#ff5252]">#{selectedOrder.order.code}</p>
                                <p className="text-sm text-gray-600 mt-2">Tổng tiền</p>
                                <p className="font-bold">{selectedOrder.order.total_price?.toLocaleString('vi-VN')}đ</p>
                            </div>
                        </div>
                    )}

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Lý do hủy đơn hàng *
                            </label>
                            <select
                                value={cancelForm.reason}
                                onChange={(e) => setCancelForm({ ...cancelForm, reason: e.target.value, reason_detail: '' })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#ff5252] focus:border-[#ff5252]"
                                required
                            >
                                <option value="">-- Chọn lý do --</option>
                                {cancelReasons.map(reason => (
                                    <option key={reason.key} value={reason.key}>
                                        {reason.label}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {cancelForm.reason === 'other' && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Chi tiết lý do *
                                </label>
                                <textarea
                                    value={cancelForm.reason_detail}
                                    onChange={(e) => setCancelForm({ ...cancelForm, reason_detail: e.target.value })}
                                    placeholder="Vui lòng mô tả chi tiết lý do hủy đơn hàng..."
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#ff5252] focus:border-[#ff5252] resize-none"
                                    rows={4}
                                    required
                                />
                            </div>
                        )}

                        {selectedOrder?.order.status === 'confirmed' && (
                            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                                <div className="flex items-start">
                                    <div className="text-yellow-600 mr-2">ℹ️</div>
                                    <div>
                                        <p className="text-sm font-medium text-yellow-800">Lưu ý</p>
                                        <p className="text-sm text-yellow-700 mt-1">
                                            Đơn hàng đã được xác nhận. Yêu cầu hủy sẽ được gửi đến admin để xem xét và phê duyệt.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="flex gap-3 mt-8">
                        <button
                            onClick={onClose}
                            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                        >
                            Hủy bỏ
                        </button>
                        <button
                            onClick={onSubmit}
                            disabled={!cancelForm.reason || (cancelForm.reason === 'other' && !cancelForm.reason_detail)}
                            className="flex-1 px-4 py-2 bg-[#ff5252] text-white rounded-lg hover:bg-[#e53e3e] transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed cursor-pointer"
                        >
                            Xác nhận hủy
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CancelOrderModal