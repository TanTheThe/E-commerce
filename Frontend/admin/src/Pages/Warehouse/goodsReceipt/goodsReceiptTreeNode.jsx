import { CheckCircle, Edit, Eye, FileText, Trash2 } from "lucide-react";

const GoodsReceiptStatusBadge = ({ status }) => {
    const statusConfig = {
        pending: { label: 'Chờ duyệt', color: 'bg-yellow-100 text-yellow-700' },
        approved: { label: 'Đã duyệt', color: 'bg-blue-100 text-blue-700' },
        completed: { label: 'Hoàn thành', color: 'bg-green-100 text-green-700' },
        has_issue: { label: 'Đang có vấn đề', color: 'bg-orange-100 text-orange-700' },
        cancelled: { label: 'Đã hủy', color: 'bg-red-100 text-red-700' }
    };

    const config = statusConfig[status] || statusConfig.pending;

    return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
            {config.label}
        </span>
    );
};

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

const GoodsReceiptTreeNode = ({ gr, level, onViewDetail, onUpdate, onDelete, onApprove, onViewApprovalPreview, userRole }) => {
    const isAdmin = userRole === 'admin';
    const indentClass = level > 0 ? `ml-${level * 8} border-l-2 border-gray-300 pl-4` : '';

    return (
        <div className={indentClass}>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow mb-2">
                <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                        <h3 className="font-semibold text-lg text-gray-900">{gr.receipt_number}</h3>
                        {level > 0 && (
                            <p className="text-xs text-purple-600 mt-1">
                                ↳ Phiếu con (Level {level})
                            </p>
                        )}
                    </div>
                    <div className="text-right">
                        <GoodsReceiptStatusBadge status={gr.status} />
                        {gr.has_discrepancy && (
                            <div className="mt-1">
                                <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">
                                    Có sai lệch
                                </span>
                            </div>
                        )}
                    </div>
                </div>

                <div className="space-y-2 mb-3 text-sm">
                    <div className="flex justify-between">
                        <span className="text-gray-500">NCC:</span>
                        <span className="font-medium text-gray-900">{gr.supplier?.name || 'Không có'}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-500">Kho:</span>
                        <span className="font-medium text-gray-900">{gr.warehouse?.name || 'Không có'}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-500">Phiếu cha:</span>
                        <span className="font-medium text-gray-900">{gr.receipt_number_parent || 'Không có'}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-500">Ngày nhận:</span>
                        <span className="font-medium text-gray-900">{formatDate(gr.receipt_date)}</span>
                    </div>
                </div>

                <div className="border-t pt-3 mb-3">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-gray-600">Số lượng SP:</span>
                        <span className="font-semibold text-gray-900">{gr.total_items || 0} mặt hàng</span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span className="text-gray-600">Tổng tiền:</span>
                        <span className="font-bold text-lg text-blue-600">
                            {formatCurrency(gr.total_received_amount || 0)}
                        </span>
                    </div>
                </div>

                {gr.approved_at && (
                    <div className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded mb-3">
                        ✓ Đã duyệt: {formatDate(gr.approved_at)}
                    </div>
                )}

                <div className="flex gap-2">
                    <button
                        onClick={() => onViewDetail(gr.id)}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                        <Eye className="w-4 h-4" />
                        <span>Xem chi tiết</span>
                    </button>

                    {gr.status === 'pending' && (
                        <>
                            <button
                                onClick={() => onViewApprovalPreview(gr.id)}
                                className="flex items-center justify-center px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
                                title="Xem preview duyệt"
                            >
                                <FileText className="w-4 h-4" />
                            </button>

                            {isAdmin && (
                                <button
                                    onClick={() => onApprove(gr.id)}
                                    className="flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                                    title="Duyệt phiếu"
                                >
                                    <CheckCircle className="w-4 h-4" />
                                </button>
                            )}

                            <button
                                onClick={() => onUpdate(gr.id)}
                                className="flex items-center justify-center px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors"
                                title="Cập nhật"
                            >
                                <Edit className="w-4 h-4" />
                            </button>

                            <button
                                onClick={() => onDelete(gr.id)}
                                className="flex items-center justify-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                                title="Xóa"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </>
                    )}

                    {gr.status === 'approved' && (
                        <button
                            onClick={() => onUpdate(gr.id)}
                            className="flex items-center justify-center px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors"
                            title="Cập nhật"
                        >
                            <Edit className="w-4 h-4" />
                        </button>
                    )}
                </div>
            </div>

            {gr.children && gr.children.length > 0 && (
                <div className="mt-2">
                    {gr.children.map((child) => (
                        <GoodsReceiptTreeNode
                            key={child.id}
                            gr={child}
                            level={level + 1}
                            onViewDetail={onViewDetail}
                            onUpdate={onUpdate}
                            onDelete={onDelete}
                            onApprove={onApprove}
                            onViewApprovalPreview={onViewApprovalPreview}
                            userRole={userRole}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default GoodsReceiptTreeNode