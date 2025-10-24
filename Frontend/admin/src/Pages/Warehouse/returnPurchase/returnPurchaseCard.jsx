import React, { useState } from 'react';
import { Eye, FileText, CheckCircle, Edit, Trash2, Mail, X } from 'lucide-react';

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
    });
};

const ReturnPurchaseStatusBadge = ({ status }) => {
    const statusConfig = {
        draft: { label: 'Nháp', color: 'bg-gray-100 text-gray-700' },
        approved: { label: 'Đã duyệt', color: 'bg-green-100 text-green-700' },
        sent: { label: 'Đã gửi', color: 'bg-blue-100 text-blue-700' },
        confirmed: { label: 'Đã xác nhận', color: 'bg-indigo-100 text-indigo-700' },
        completed: { label: 'Hoàn thành', color: 'bg-purple-100 text-purple-700' }
    };

    const config = statusConfig[status] || statusConfig.draft;

    return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
            {config.label}
        </span>
    );
};

const ReturnPurchaseTypeBadge = ({ returnType }) => {
    const typeConfig = {
        return_to_supplier: { label: 'Trả về NCC', color: 'bg-orange-100 text-orange-700' },
        exchange: { label: 'Đổi hàng', color: 'bg-indigo-100 text-indigo-700' },
        refund: { label: 'Hoàn tiền', color: 'bg-yellow-100 text-yellow-700' }
    };

    const config = typeConfig[returnType] || typeConfig.return_to_supplier;

    return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
            {config.label}
        </span>
    );
};

const ReturnPurchaseCard = ({
    returnPurchase,
    onViewDetail,
    onUpdate,
    onDelete,
    onSendEmail,
    onApprove,
    onConfirm,
    onComplete,
    userRole,
    openAlertBox
}) => {
    const [isSending, setIsSending] = useState(false);
    const [showEmailModal, setShowEmailModal] = useState(false);
    const [supplierEmail, setSupplierEmail] = useState('');
    const isAdmin = userRole === 'admin';

    const handleOpenEmailModal = () => {
        setSupplierEmail(returnPurchase.supplier?.email || '');
        setShowEmailModal(true);
    };

    const handleSendEmail = async () => {
        if (isSending) return;

        if (supplierEmail.trim()) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(supplierEmail.trim())) {
                openAlertBox?.("error", "Email không hợp lệ");
                return;
            }
        }

        setIsSending(true);
        try {
            const requestData = {
                supplier_email: supplierEmail.trim() || null,
            };
            await onSendEmail(returnPurchase.id, requestData);
            setShowEmailModal(false);
        } catch (error) {
            console.error("Error sending return purchase email:", error);
        } finally {
            setIsSending(false);
        }
    };

    return (
        <>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                        <h3 className="font-semibold text-lg text-gray-900">{returnPurchase.return_number}</h3>
                        {returnPurchase.purchase_order?.po_number && (
                            <p className="text-xs text-blue-600 mt-1">
                                PO: {returnPurchase.purchase_order.po_number}
                            </p>
                        )}
                        {returnPurchase.goods_receipt && (
                            <p className="text-xs text-purple-600 mt-1">
                                GR: {returnPurchase.goods_receipt.receipt_number}
                            </p>
                        )}
                    </div>
                    <div className="text-right space-y-1">
                        <ReturnPurchaseStatusBadge status={returnPurchase.status} />
                        <ReturnPurchaseTypeBadge returnType={returnPurchase.return_type} />
                    </div>
                </div>

                <div className="space-y-2 mb-3 text-sm">
                    <div className="flex justify-between">
                        <span className="text-gray-500">NCC:</span>
                        <span className="font-medium text-gray-900">{returnPurchase.supplier?.name || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-500">Kho:</span>
                        <span className="font-medium text-gray-900">{returnPurchase.warehouse?.name || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-500">Ngày trả:</span>
                        <span className="font-medium text-gray-900">{formatDate(returnPurchase.return_date)}</span>
                    </div>
                    {returnPurchase.shipped_date && (
                        <div className="flex justify-between">
                            <span className="text-gray-500">Đã gửi:</span>
                            <span className="font-medium text-gray-900">{formatDate(returnPurchase.shipped_date)}</span>
                        </div>
                    )}
                </div>

                <div className="border-t pt-3 mb-3">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-gray-600">Số lượng SP:</span>
                        <span className="font-semibold text-gray-900">{returnPurchase.total_items || 0} mặt hàng</span>
                    </div>
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-gray-600">Tổng tiền trả:</span>
                        <span className="font-bold text-lg text-orange-600">
                            {formatCurrency(returnPurchase.total_return_amount || 0)}
                        </span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span className="text-gray-600">Số tiền hoàn:</span>
                        <span className="font-bold text-lg text-green-600">
                            {formatCurrency(returnPurchase.refund_amount || 0)}
                        </span>
                    </div>
                </div>

                {returnPurchase.approved_at && (
                    <div className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded mb-3">
                        ✓ Đã duyệt: {formatDate(returnPurchase.approved_at)}
                    </div>
                )}

                {returnPurchase.confirmed_at && (
                    <div className="text-xs text-purple-600 bg-purple-50 px-2 py-1 rounded mb-3">
                        ✓ Nhận hàng: {formatDate(returnPurchase.confirmed_at)}
                    </div>
                )}

                <div className="flex gap-2 flex-wrap">
                    <button
                        onClick={() => onViewDetail(returnPurchase.id)}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                        <Eye className="w-4 h-4" />
                        <span>Xem chi tiết</span>
                    </button>

                    {returnPurchase.status === 'draft' && (
                        <>
                            {isAdmin && (
                                <>
                                    <button
                                        onClick={() => onApprove(returnPurchase.id)}
                                        className="flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                                        title="Duyệt phiếu"
                                    >
                                        <CheckCircle className="w-4 h-4" />
                                    </button>
                                </>
                            )}

                            <button
                                onClick={() => onUpdate(returnPurchase.id)}
                                className="flex items-center justify-center px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors"
                                title="Cập nhật"
                            >
                                <Edit className="w-4 h-4" />
                            </button>

                            <button
                                onClick={() => onDelete(returnPurchase.id)}
                                className="flex items-center justify-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                                title="Xóa"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </>
                    )}

                    {returnPurchase.status === 'approved' && isAdmin && (
                        <button
                            onClick={handleOpenEmailModal}
                            className="flex items-center justify-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
                            title="Gửi email cho NCC"
                        >
                            <Mail className="w-4 h-4" />
                        </button>
                    )}

                    {returnPurchase.status === 'sent' && isAdmin && (
                        <button
                            onClick={() => onConfirm(returnPurchase.id)}
                            className="flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                            title="Xác nhận nhận hàng"
                        >
                            <CheckCircle className="w-4 h-4" />
                        </button>
                    )}

                    {returnPurchase.status === 'confirmed' && isAdmin && (
                        <button
                            onClick={() => onComplete(returnPurchase.id)}
                            className="flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                            title="Hoàn thành"
                        >
                            <CheckCircle className="w-4 h-4" />
                        </button>
                    )}
                </div>
            </div>

            {showEmailModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                    style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.5)' }}>
                    <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-800">Gửi email thông báo hoàn trả</h3>
                            <button
                                onClick={() => setShowEmailModal(false)}
                                disabled={isSending}
                                className="text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Email nhà cung cấp
                            </label>
                            <input
                                type="email"
                                value={supplierEmail}
                                onChange={(e) => setSupplierEmail(e.target.value)}
                                placeholder={returnPurchase.supplier?.email || "Nhập email khác (nếu có)..."}
                                disabled={isSending}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-100"
                            />
                            <p className="mt-1 text-xs text-gray-500">
                                {returnPurchase.supplier?.email
                                    ? `Để trống để sử dụng email mặc định: ${returnPurchase.supplier.email}`
                                    : "Để trống để sử dụng email mặc định của nhà cung cấp"
                                }
                            </p>
                        </div>

                        {isSending && (
                            <div className="mb-4 flex items-center gap-2 text-indigo-600 bg-indigo-50 px-3 py-2 rounded-md">
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
                                <span className="text-sm">Đang gửi email...</span>
                            </div>
                        )}

                        <div className="flex justify-end gap-3">
                            <button
                                onClick={() => setShowEmailModal(false)}
                                disabled={isSending}
                                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                Hủy
                            </button>
                            <button
                                onClick={handleSendEmail}
                                disabled={isSending}
                                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                            >
                                {isSending ? (
                                    <>
                                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                        <span>Đang gửi...</span>
                                    </>
                                ) : (
                                    <>
                                        <Mail className="w-4 h-4" />
                                        <span>Gửi email</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default ReturnPurchaseCard;