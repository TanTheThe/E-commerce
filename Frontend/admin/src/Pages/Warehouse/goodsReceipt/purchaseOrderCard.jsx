import { FileText } from "lucide-react";

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

const PurchaseOrderCard = ({ po, onViewReceipts }) => {
    const statusConfig = {
        pending: { label: 'Chờ duyệt', color: 'bg-yellow-100 text-yellow-700' },
        approved: { label: 'Đã duyệt', color: 'bg-blue-100 text-blue-700' },
        completed: { label: 'Hoàn thành', color: 'bg-green-100 text-green-700' },
        cancelled: { label: 'Đã hủy', color: 'bg-red-100 text-red-700' }
    };

    const config = statusConfig[po.status] || statusConfig.pending;

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                    <h3 className="font-semibold text-lg text-gray-900">{po.po_number}</h3>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
                    {config.label}
                </span>
            </div>

            <div className="space-y-2 mb-3 text-sm">
                <div className="flex justify-between">
                    <span className="text-gray-500">Tổng đã đặt:</span>
                    <span className="font-medium text-gray-900">{po.total_ordered || 0} món</span>
                </div>
                <div className="flex justify-between">
                    <span className="text-gray-500">Số phiếu nhập:</span>
                    <span className="font-semibold text-blue-600">{po.total_gr_count || 0} phiếu</span>
                </div>
                <div className="flex justify-between">
                    <span className="text-gray-500">Ngày tạo:</span>
                    <span className="font-medium text-gray-900">{formatDate(po.created_at)}</span>
                </div>
            </div>

            <button
                onClick={() => onViewReceipts(po.id)}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
                <FileText className="w-4 h-4" />
                <span>Xem các phiếu nhập kho</span>
            </button>
        </div>
    );
};


export default PurchaseOrderCard;