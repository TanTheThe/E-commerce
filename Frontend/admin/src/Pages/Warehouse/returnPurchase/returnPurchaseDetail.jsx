import React, { useState, useEffect, useContext } from 'react';
import { X } from 'lucide-react';
import { getDataApi } from '../../../utils/api';
import { MyContext } from '../../../App';

const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
};

const formatDate = (dateString) => {
    if (!dateString || isNaN(Date.parse(dateString))) return null;
    return new Date(dateString).toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
    });
};

const formatDateTime = (dateString) => {
    if (!dateString || isNaN(Date.parse(dateString))) return null;
    return new Date(dateString).toLocaleString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
};

const StatusBadge = ({ status }) => {
    const statusConfig = {
        draft: { label: 'Nháp', color: 'bg-gray-100 text-gray-700' },
        sent: { label: 'Đã gửi', color: 'bg-blue-100 text-blue-700' },
        approved: { label: 'Đã duyệt', color: 'bg-green-100 text-green-700' },
        completed: { label: 'Hoàn thành', color: 'bg-purple-100 text-purple-700' },
        rejected: { label: 'Đã từ chối', color: 'bg-red-100 text-red-700' }
    };

    const config = statusConfig[status] || { label: status, color: 'bg-gray-100 text-gray-700' };

    return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
            {config.label}
        </span>
    );
};

const ReturnTypeBadge = ({ type }) => {
    const typeConfig = {
        return_to_supplier: { label: 'Trả về NCC', color: 'bg-purple-100 text-purple-700' },
        exchange: { label: 'Đổi hàng', color: 'bg-orange-100 text-orange-700' },
        refund: { label: 'Hoàn tiền', color: 'bg-green-100 text-green-700' }
    };

    const config = typeConfig[type] || { label: type, color: 'bg-gray-100 text-gray-700' };

    return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
            {config.label}
        </span>
    );
};

const ConditionBadge = ({ condition }) => {
    if (!condition) return <span className="text-gray-400">-</span>;

    const conditionConfig = {
        damaged: { label: 'Hư hỏng', color: 'bg-red-100 text-red-700' },
        defective: { label: 'Lỗi', color: 'bg-orange-100 text-orange-700' },
        expired: { label: 'Hết hạn', color: 'bg-yellow-100 text-yellow-700' },
        wrong_item: { label: 'Sai hàng', color: 'bg-purple-100 text-purple-700' }
    };

    const config = conditionConfig[condition] || { label: condition, color: 'bg-gray-100 text-gray-700' };

    return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
            {config.label}
        </span>
    );
};

const PurchaseReturnDetailModal = ({ prId, onClose }) => {
    const [prDetail, setPrDetail] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (!prId) return;

        const fetchDetail = async () => {
            setIsLoading(true);
            try {
                const response = await getDataApi(`/admin/return-purchase/${prId}`);

                if (response.success) {
                    setPrDetail(response.data);
                } else {
                    alert(response?.data?.detail?.message || "Lỗi khi tải dữ liệu");
                }
            } catch (error) {
                console.error('Error fetching purchase return detail:', error);
                alert("Lỗi khi tải chi tiết phiếu trả hàng");
            } finally {
                setIsLoading(false);
            }
        };

        fetchDetail();
    }, [prId]);

    if (isLoading) {
        return (
            <div
                className="fixed inset-0 bg-opacity-50 flex items-center justify-center z-50"
                onClick={onClose}
                style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}
            >
                <div
                    className="bg-white rounded-lg p-8 w-full max-w-6xl max-h-[90vh] overflow-auto"
                    onClick={(e) => e.stopPropagation()}
                >
                    <div className="animate-pulse space-y-4">
                        <div className="h-8 bg-gray-200 rounded w-1/3"></div>
                        <div className="space-y-3">
                            <div className="h-4 bg-gray-200 rounded"></div>
                            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                            <div className="h-4 bg-gray-200 rounded w-4/6"></div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (!prDetail) return null;

    const returnDate = formatDate(prDetail.return_date);
    const shippedDate = formatDate(prDetail.shipped_date);
    const createdAt = formatDateTime(prDetail.created_at);
    const approvedAt = formatDateTime(prDetail.approved_at);
    const completedAt = formatDateTime(prDetail.completed_at);

    return (
        <div
            className="fixed inset-0 bg-opacity-50 flex items-center justify-center z-50"
            onClick={onClose}
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}
        >
            <div
                className="bg-white rounded-lg w-full max-w-6xl max-h-[85vh] overflow-auto m-4"
                onClick={(e) => e.stopPropagation()}
            >
                <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-start z-10">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">Chi tiết phiếu trả hàng</h2>
                        <div className="flex items-center gap-4 flex-wrap">
                            <span className="text-lg font-semibold text-red-600">{prDetail.return_number}</span>
                            <StatusBadge status={prDetail.status} />
                            <ReturnTypeBadge type={prDetail.return_type} />
                        </div>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm text-gray-600">Đơn đặt hàng</label>
                            <p className="font-medium text-blue-600">{prDetail.purchase_order_number || 'N/A'}</p>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm text-gray-600">Phiếu nhập kho</label>
                            <p className="font-medium text-blue-600">{prDetail.goods_receipt_number || 'Không có'}</p>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm text-gray-600">Ngày tạo phiếu trả</label>
                            <p className="font-medium">{returnDate || 'N/A'}</p>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm text-gray-600">Ngày gửi hàng</label>
                            <p className="font-medium">{shippedDate || 'Chưa gửi'}</p>
                        </div>
                        {prDetail.delivery_note_number && (
                            <div className="space-y-2">
                                <label className="text-sm text-gray-600">Số phiếu giao nhận</label>
                                <p className="font-medium">{prDetail.delivery_note_number}</p>
                            </div>
                        )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-gray-50 rounded-lg p-4">
                            <h3 className="font-semibold text-gray-900 mb-3">Thông tin nhà cung cấp</h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Tên:</span>
                                    <span className="font-medium">{prDetail.supplier_name || 'N/A'}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Mã:</span>
                                    <span className="font-medium">{prDetail.supplier_code || 'N/A'}</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-gray-50 rounded-lg p-4">
                            <h3 className="font-semibold text-gray-900 mb-3">Thông tin kho xuất</h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Tên:</span>
                                    <span className="font-medium">{prDetail.warehouse_name || 'N/A'}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Mã:</span>
                                    <span className="font-medium">{prDetail.warehouse_code || 'N/A'}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {prDetail.return_reason && (
                        <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                            <h3 className="font-semibold text-gray-900 mb-2">Lý do trả hàng</h3>
                            <p className="text-sm text-gray-700">{prDetail.return_reason}</p>
                        </div>
                    )}

                    <div>
                        <h3 className="font-semibold text-gray-900 mb-3">Danh sách sản phẩm trả</h3>
                        <div className="overflow-x-auto border border-gray-200 rounded-lg">
                            <table className="w-full">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sản phẩm</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Màu sắc</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
                                        <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Tình trạng</th>
                                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">SL trả</th>
                                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Đơn giá</th>
                                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Thành tiền</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {prDetail.items && prDetail.items.length > 0 ? (
                                        prDetail.items.map((item) => (
                                            <React.Fragment key={item.id}>
                                                <tr className="hover:bg-gray-50">
                                                    <td className="px-4 py-3">
                                                        <div className="flex items-center gap-3">
                                                            {item.product_snapshot.variant_image && (
                                                                <img
                                                                    src={item.product_snapshot.variant_image}
                                                                    alt={item.product_snapshot.name}
                                                                    className="w-12 h-12 object-cover rounded border"
                                                                />
                                                            )}
                                                            <span className="text-sm font-medium">{item.product_snapshot.name}</span>
                                                        </div>
                                                    </td>
                                                    <td className="px-4 py-3 text-sm">{item.product_snapshot.sku}</td>
                                                    <td className="px-4 py-3 text-sm">{item.product_snapshot.color_name || '-'}</td>
                                                    <td className="px-4 py-3 text-sm">{item.product_snapshot.size || '-'}</td>
                                                    <td className="px-4 py-3 text-center">
                                                        <ConditionBadge condition={item.condition} />
                                                    </td>
                                                    <td className="px-4 py-3 text-sm text-right font-medium text-red-600">
                                                        {item.return_quantity}
                                                    </td>
                                                    <td className="px-4 py-3 text-sm text-right">{formatCurrency(item.unit_cost)}</td>
                                                    <td className="px-4 py-3 text-sm text-right font-medium">
                                                        {formatCurrency(item.total_cost)}
                                                    </td>
                                                </tr>
                                                {(item.rejection_evidence?.length > 0 || item.notes) && (
                                                    <tr>
                                                        <td colSpan="8" className="px-4 py-2 bg-gray-50">
                                                            {item.rejection_evidence?.length > 0 && (
                                                                <div className="mb-2">
                                                                    <span className="text-xs font-medium text-gray-600">Chứng từ: </span>
                                                                    <div className="flex gap-2 mt-1">
                                                                        {item.rejection_evidence.map((url, idx) => (
                                                                            <a
                                                                                key={idx}
                                                                                href={url}
                                                                                target="_blank"
                                                                                rel="noopener noreferrer"
                                                                                className="text-xs text-blue-600 hover:underline"
                                                                            >
                                                                                File {idx + 1}
                                                                            </a>
                                                                        ))}
                                                                    </div>
                                                                </div>
                                                            )}
                                                            {item.notes && (
                                                                <div className="text-xs text-gray-600">
                                                                    <span className="font-medium">Ghi chú: </span>
                                                                    {item.notes}
                                                                </div>
                                                            )}
                                                        </td>
                                                    </tr>
                                                )}
                                            </React.Fragment>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan="8" className="px-4 py-3 text-center text-gray-500">
                                                Không có sản phẩm nào
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="flex justify-between">
                                <span className="font-medium text-gray-700">Tổng giá trị trả hàng:</span>
                                <span className="font-bold text-lg text-red-600">
                                    {formatCurrency(prDetail.total_return_amount || 0)}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="font-medium text-gray-700">Số tiền NCC hoàn lại:</span>
                                <span className="font-bold text-lg text-green-600">
                                    {formatCurrency(prDetail.refund_amount || 0)}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div>
                        <h3 className="font-semibold text-gray-900 mb-3">Thông tin xử lý</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {prDetail.created_by_name && (
                                <div className="bg-blue-50 rounded-lg p-3">
                                    <label className="text-xs text-gray-600">Người tạo phiếu</label>
                                    <p className="font-medium text-sm">{prDetail.created_by_name}</p>
                                    {createdAt && (
                                        <p className="text-xs text-gray-500 mt-1">{createdAt}</p>
                                    )}
                                </div>
                            )}
                            {prDetail.approved_by_name && (
                                <div className="bg-green-50 rounded-lg p-3">
                                    <label className="text-xs text-gray-600">Người phê duyệt</label>
                                    <p className="font-medium text-sm">{prDetail.approved_by_name}</p>
                                    {approvedAt && (
                                        <p className="text-xs text-gray-500 mt-1">{approvedAt}</p>
                                    )}
                                </div>
                            )}
                            {completedAt && (
                                <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                                    <label className="text-xs text-gray-600">Thời gian hoàn thành</label>
                                    <p className="font-medium text-sm">{completedAt}</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {prDetail.notes && (
                        <div className="space-y-2">
                            <label className="text-sm text-gray-600 font-semibold">Ghi chú</label>
                            <p className="text-sm bg-yellow-50 p-3 rounded border border-yellow-200">
                                {prDetail.notes}
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default PurchaseReturnDetailModal;