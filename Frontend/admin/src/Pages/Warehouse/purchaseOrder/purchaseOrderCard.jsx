import { Edit, Eye, Send, Trash2 } from "lucide-react";
import useAuth from "../../Verify/auth";
import { useState } from "react";

const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
};

const formatDate = (dateString) => {
    if (!dateString || isNaN(Date.parse(dateString))) {
        return null;
    }
    return new Date(dateString).toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
    });
};

const StatusBadge = ({ status }) => {
    const statusConfig = {
        draft: { label: 'Nháp', color: 'bg-gray-100 text-gray-700' },
        sent: { label: 'Đã gửi', color: 'bg-blue-100 text-blue-700' },
        confirmed: { label: 'Đã xác nhận', color: 'bg-yellow-100 text-yellow-700' },
        completed: { label: 'Hoàn thành', color: 'bg-green-100 text-green-700' },
        cancelled: { label: 'Đã hủy', color: 'bg-red-100 text-red-700' }
    };

    const config = statusConfig[status] || statusConfig.draft;

    return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
            {config.label}
        </span>
    );
};

const PaymentStatusBadge = ({ status }) => {
    const statusConfig = {
        unpaid: { label: 'Chưa thanh toán', color: 'bg-red-100 text-red-700' },
        partially_paid: { label: 'Thanh toán 1 phần', color: 'bg-orange-100 text-orange-700' },
        paid: { label: 'Đã thanh toán', color: 'bg-green-100 text-green-700' }
    };

    const config = statusConfig[status] || statusConfig.unpaid;

    return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
            {config.label}
        </span>
    );
};

const SendPurchaseOrderModal = ({ isOpen, onClose, onConfirm, isLoading }) => {
    const [notes, setNotes] = useState('');
    const [supplierEmail, setSupplierEmail] = useState('');

    if (!isOpen) return null;

    const handleSubmit = () => {
        const data = {};
        if (notes.trim()) data.notes = notes.trim();
        if (supplierEmail.trim()) data.supplier_email = supplierEmail.trim();
        onConfirm(data);
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}>
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
                <div className="p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        Gửi đơn đặt hàng cho nhà cung cấp
                    </h3>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Email nhà cung cấp (tùy chọn)
                            </label>
                            <input
                                type="email"
                                value={supplierEmail}
                                onChange={(e) => setSupplierEmail(e.target.value)}
                                placeholder="Để trống nếu dùng email mặc định"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Ghi chú (tùy chọn)
                            </label>
                            <textarea
                                value={notes}
                                onChange={(e) => setNotes(e.target.value)}
                                placeholder="Nhập ghi chú khi gửi..."
                                rows={3}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                            />
                        </div>
                    </div>

                    <div className="flex gap-3 mt-6">
                        <button
                            onClick={onClose}
                            disabled={isLoading}
                            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50"
                        >
                            Hủy
                        </button>
                        <button
                            onClick={handleSubmit}
                            disabled={isLoading}
                            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                        >
                            {isLoading ? (
                                <span>Đang gửi...</span>
                            ) : (
                                <>
                                    <Send className="w-4 h-4" />
                                    <span>Gửi</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

const PurchaseOrderCard = ({ po, onViewDetail, onUpdate, onDelete, onSend, userRole }) => {
    const [showSendModal, setShowSendModal] = useState(false);
    const [isSending, setIsSending] = useState(false);

    const isAdmin = userRole === 'admin';

    const handleSendClick = () => {
        setShowSendModal(true);
    };

    const handleConfirmSend = async (data) => {
        setIsSending(true);
        try {
            await onSend(po.id, data);
            setShowSendModal(false);
        } catch (error) {
            console.error('Error sending PO:', error);
        } finally {
            setIsSending(false);
        }
    };

    return (
        <>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-3">
                    <div>
                        <h3 className="font-semibold text-lg text-gray-900">{po.po_number}</h3>
                        <p className="text-sm text-gray-600 mt-1">Nhà cung cấp: {po.supplier_name}</p>
                        <p className="text-sm text-gray-600">Kho: {po.warehouse_name}</p>
                    </div>
                    <div className="text-right">
                        <StatusBadge status={po.status} />
                        <div className="mt-2">
                            <PaymentStatusBadge status={po.payment_status} />
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
                    <div>
                        <span className="text-gray-600">Ngày đặt:</span>
                        <p className="font-medium">{formatDate(po.order_date)}</p>
                    </div>
                    <div>
                        <span className="text-gray-600">Giao dự kiến:</span>
                        <p
                            className={`font-medium ${!formatDate(po.expected_delivery_date) ? 'text-red-500' : ''
                                }`}
                        >
                            {formatDate(po.expected_delivery_date) ||
                                'Chưa thống nhất với nhà cung cấp'}
                        </p>
                    </div>
                </div>

                <div className="border-t pt-3 mb-3">
                    <div className="flex justify-between items-center">
                        <span className="text-gray-600">Tổng tiền:</span>
                        <span className="font-bold text-lg text-blue-600">{formatCurrency(po.total_amount)}</span>
                    </div>
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={() => onViewDetail(po.id)}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                        <Eye className="w-4 h-4" />
                        <span>Xem chi tiết</span>
                    </button>

                    {isAdmin && po.status === 'draft' && (
                        <button
                            onClick={handleSendClick}
                            className="flex items-center justify-center px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
                            title="Gửi cho nhà cung cấp"
                        >
                            <Send className="w-4 h-4" />
                        </button>
                    )}

                    {po.status === 'draft' && (
                        <>
                            <button
                                onClick={() => onUpdate(po.id)}
                                className="flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                            >
                                <Edit className="w-4 h-4" />
                            </button>
                            <button
                                onClick={() => onDelete(po.id)}
                                className="flex items-center justify-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </>
                    )}
                </div>
            </div>

            <SendPurchaseOrderModal
                isOpen={showSendModal}
                onClose={() => setShowSendModal(false)}
                onConfirm={handleConfirmSend}
                isLoading={isSending}
            />
        </>
    );
};

export default PurchaseOrderCard;