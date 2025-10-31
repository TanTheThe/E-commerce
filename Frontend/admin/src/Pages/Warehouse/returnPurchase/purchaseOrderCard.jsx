import { Package } from "lucide-react";

const POStatusBadge = ({ status }) => {
    const statusConfig = {
        pending: { label: 'Đang xử lý', className: 'bg-yellow-100 text-yellow-800' },
        partial_received: { label: 'Nhận một phần', className: 'bg-blue-100 text-blue-800' },
        completed: { label: 'Hoàn thành', className: 'bg-green-100 text-green-800' }
    };

    const config = statusConfig[status] || { label: status, className: 'bg-gray-100 text-gray-800' };

    return (
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${config.className}`}>
            {config.label}
        </span>
    );
};

const PurchaseOrderCard = ({ po, onViewReturns }) => {
    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
                <div className="flex-1">
                    <h3 className="font-semibold text-lg text-gray-900">{po.po_number}</h3>
                    <p className="text-sm text-gray-500 mt-1">
                        Đặt hàng: {po.total_ordered} sản phẩm • {po.total_pr_count || 0} phiếu trả hàng
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <POStatusBadge status={po.status} />
                    <span className="text-sm text-gray-500">
                        {formatDate(po.created_at)}
                    </span>
                    <button
                        onClick={() => onViewReturns(po)}
                        className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors"
                    >
                        <Package className="w-4 h-4" />
                        <span>Xem phiếu trả hàng</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default PurchaseOrderCard;

