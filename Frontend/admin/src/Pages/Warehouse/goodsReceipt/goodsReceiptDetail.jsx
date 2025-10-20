import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { getDataApi } from '../../../utils/api';

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
        pending: { label: 'Chờ xử lý', color: 'bg-yellow-100 text-yellow-700' },
        received: { label: 'Đã nhận', color: 'bg-blue-100 text-blue-700' },
        inspected: { label: 'Đã kiểm tra', color: 'bg-purple-100 text-purple-700' },
        completed: { label: 'Hoàn thành', color: 'bg-green-100 text-green-700' },
        cancelled: { label: 'Đã hủy', color: 'bg-red-100 text-red-700' }
    };

    const config = statusConfig[status] || { label: status, color: 'bg-gray-100 text-gray-700' };

    return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
            {config.label}
        </span>
    );
};

const ImageViewer = ({ imageBase64, onClose }) => {
    const [zoom, setZoom] = useState(1);
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isDragging, setIsDragging] = useState(false);
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

    const handleWheel = (e) => {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        setZoom(prev => Math.min(Math.max(0.5, prev + delta), 3));
    };

    const handleMouseDown = (e) => {
        if (zoom > 1) {
            setIsDragging(true);
            setDragStart({
                x: e.clientX - position.x,
                y: e.clientY - position.y
            });
        }
    };

    const handleMouseMove = (e) => {
        if (isDragging && zoom > 1) {
            setPosition({
                x: e.clientX - dragStart.x,
                y: e.clientY - dragStart.y
            });
        }
    };

    const handleMouseUp = () => {
        setIsDragging(false);
    };

    useEffect(() => {
        if (isDragging) {
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
            return () => {
                document.removeEventListener('mousemove', handleMouseMove);
                document.removeEventListener('mouseup', handleMouseUp);
            };
        }
    }, [isDragging, dragStart, position]);

    return (
        <div
            className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-[60]"
            onClick={onClose}
        >
            <div className="relative w-full h-full flex items-center justify-center p-8">
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        onClose();
                    }}
                    className="absolute top-4 right-4 text-white hover:text-gray-300 bg-black bg-opacity-50 rounded-full p-2 z-10"
                >
                    <X className="w-8 h-8" />
                </button>
                <div className="text-white absolute top-4 left-4 bg-black bg-opacity-50 px-3 py-1 rounded">
                    Zoom: {Math.round(zoom * 100)}% {zoom > 1 && '- Kéo để di chuyển'}
                </div>
                <div
                    className="overflow-hidden max-w-full max-h-full flex items-center justify-center"
                    onWheel={handleWheel}
                    onClick={(e) => e.stopPropagation()}
                >
                    <img
                        src={imageBase64}
                        alt="Ảnh sản phẩm"
                        style={{
                            transform: `scale(${zoom}) translate(${position.x / zoom}px, ${position.y / zoom}px)`,
                            transition: isDragging ? 'none' : 'transform 0.1s',
                            cursor: zoom > 1 ? (isDragging ? 'grabbing' : 'grab') : 'default'
                        }}
                        className="max-w-none select-none"
                        onMouseDown={handleMouseDown}
                        draggable={false}
                    />
                </div>
            </div>
        </div>
    );
};

const GoodsReceiptDetailModal = ({ grId, onClose }) => {
    const [grDetail, setGrDetail] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [selectedImage, setSelectedImage] = useState(null);

    useEffect(() => {
        const fetchDetail = async () => {
            setIsLoading(true);
            try {
                const response = await getDataApi(`/admin/goods-receipt/${grId}`);
                if (response.success) {
                    setGrDetail(response.data);
                }
            } catch (error) {
                console.error('Error fetching goods receipt detail:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchDetail();
    }, [grId]);

    if (isLoading) {
        return (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white rounded-lg p-6 w-full max-w-5xl max-h-[90vh] overflow-auto">
                    <div className="animate-pulse">
                        <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
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

    if (!grDetail) return null;

    const receiptDate = formatDate(grDetail.receipt_date);
    const receivedAt = formatDateTime(grDetail.received_at);
    const inspectedAt = formatDateTime(grDetail.inspected_at);
    const approvedAt = formatDateTime(grDetail.approved_at);
    const completedAt = formatDateTime(grDetail.completed_at);

    return (
        <div
            className="fixed inset-0 bg-opacity-50 flex items-center justify-center z-50 mt-15"
            onClick={onClose}
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}
        >
            <div
                className="bg-white rounded-lg w-full max-w-6xl max-h-[90vh] overflow-auto m-4"
                onClick={(e) => e.stopPropagation()}
            >
                <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-start z-10">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">Chi tiết phiếu nhập hàng</h2>
                        <div className="flex items-center gap-4">
                            <span className="text-lg font-semibold text-blue-600">{grDetail.receipt_number}</span>
                            <StatusBadge status={grDetail.status} />
                            {grDetail.has_discrepancy && (
                                <span className="px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-700">
                                    Có chênh lệch
                                </span>
                            )}
                        </div>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    <div className="grid grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm text-gray-600">Đơn nhập hàng liên quan</label>
                            <p className="font-medium text-blue-600">{grDetail.purchase_order_number || 'N/A'}</p>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm text-gray-600">Số phiếu giao hàng</label>
                            <p className="font-medium">{grDetail.delivery_note_number || 'Không có'}</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                        <div className="bg-gray-50 rounded-lg p-4">
                            <h3 className="font-semibold text-gray-900 mb-3">Thông tin nhà cung cấp</h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Tên:</span>
                                    <span className="font-medium">{grDetail.supplier_name}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Mã:</span>
                                    <span className="font-medium">{grDetail.supplier_code}</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-gray-50 rounded-lg p-4">
                            <h3 className="font-semibold text-gray-900 mb-3">Thông tin kho</h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Tên:</span>
                                    <span className="font-medium">{grDetail.warehouse_name}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Mã:</span>
                                    <span className="font-medium">{grDetail.warehouse_code}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm text-gray-600">Ngày nhập hàng</label>
                        <p className="font-medium">{receiptDate || 'N/A'}</p>
                    </div>

                    <div>
                        <h3 className="font-semibold text-gray-900 mb-3">Danh sách sản phẩm</h3>
                        <div className="overflow-x-auto border border-gray-200 rounded-lg">
                            <table className="w-full">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sản phẩm</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Màu sắc</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
                                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">SL đặt</th>
                                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">SL nhận</th>
                                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">SL đạt</th>
                                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">SL loại</th>
                                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Đơn giá</th>
                                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Thành tiền</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {grDetail.items.map((item) => (
                                        <React.Fragment key={item.id}>
                                            <tr className="hover:bg-gray-50">
                                                <td className="px-4 py-3">
                                                    <div className="flex items-center gap-3">
                                                        {item.variant_image && (
                                                            <img
                                                                src={item.variant_image}
                                                                alt={item.product_name}
                                                                className="w-12 h-12 object-cover rounded cursor-pointer hover:opacity-80"
                                                                onClick={() => setSelectedImage(item.variant_image)}
                                                            />
                                                        )}
                                                        <span className="text-sm font-medium">{item.product_name}</span>
                                                    </div>
                                                </td>
                                                <td className="px-4 py-3 text-sm">{item.variant_sku}</td>
                                                <td className="px-4 py-3 text-sm">{item.variant_color_name || '-'}</td>
                                                <td className="px-4 py-3 text-sm">{item.variant_size || '-'}</td>
                                                <td className="px-4 py-3 text-sm text-right">{item.ordered_quantity}</td>
                                                <td className="px-4 py-3 text-sm text-right font-medium text-blue-600">
                                                    {item.received_quantity}
                                                </td>
                                                <td className="px-4 py-3 text-sm text-right font-medium text-green-600">
                                                    {item.accepted_quantity}
                                                </td>
                                                <td className="px-4 py-3 text-sm text-right font-medium text-red-600">
                                                    {item.rejected_quantity}
                                                </td>
                                                <td className="px-4 py-3 text-sm text-right">{formatCurrency(item.unit_cost)}</td>
                                                <td className="px-4 py-3 text-sm text-right font-medium">
                                                    {formatCurrency(item.total_cost)}
                                                </td>
                                            </tr>
                                            {(item.rejection_reason || item.notes) && (
                                                <tr>
                                                    <td colSpan="10" className="px-4 py-2 bg-gray-50">
                                                        {item.rejection_reason && (
                                                            <div className="text-xs text-red-600 mb-1">
                                                                <span className="font-medium">Lý do loại: </span>
                                                                {item.rejection_reason}
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
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4">
                        <div className="max-w-md ml-auto">
                            <div className="flex justify-between">
                                <span className="font-semibold text-gray-900">Tổng giá trị nhập:</span>
                                <span className="font-bold text-lg text-blue-600">
                                    {formatCurrency(grDetail.total_received_amount)}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div>
                        <h3 className="font-semibold text-gray-900 mb-3">Thông tin xử lý</h3>
                        <div className="grid grid-cols-2 gap-4">
                            {grDetail.received_by_name && (
                                <div className="bg-blue-50 rounded-lg p-3">
                                    <label className="text-xs text-gray-600">Người nhận hàng</label>
                                    <p className="font-medium text-sm">{grDetail.received_by_name}</p>
                                    {receivedAt && (
                                        <p className="text-xs text-gray-500 mt-1">{receivedAt}</p>
                                    )}
                                </div>
                            )}
                            {grDetail.inspected_by_name && (
                                <div className="bg-purple-50 rounded-lg p-3">
                                    <label className="text-xs text-gray-600">Người kiểm tra</label>
                                    <p className="font-medium text-sm">{grDetail.inspected_by_name}</p>
                                    {inspectedAt && (
                                        <p className="text-xs text-gray-500 mt-1">{inspectedAt}</p>
                                    )}
                                </div>
                            )}
                            {grDetail.approved_by_name && (
                                <div className="bg-green-50 rounded-lg p-3">
                                    <label className="text-xs text-gray-600">Người phê duyệt</label>
                                    <p className="font-medium text-sm">{grDetail.approved_by_name}</p>
                                    {approvedAt && (
                                        <p className="text-xs text-gray-500 mt-1">{approvedAt}</p>
                                    )}
                                </div>
                            )}
                            {completedAt && (
                                <div className="bg-gray-50 rounded-lg p-3">
                                    <label className="text-xs text-gray-600">Thời gian hoàn thành</label>
                                    <p className="font-medium text-sm">{completedAt}</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {grDetail.has_discrepancy && grDetail.discrepancy_notes && (
                        <div className="space-y-2">
                            <label className="text-sm text-gray-600 font-semibold">Ghi chú chênh lệch</label>
                            <p className="text-sm bg-orange-50 p-3 rounded border border-orange-200">
                                {grDetail.discrepancy_notes}
                            </p>
                        </div>
                    )}

                    {grDetail.notes && (
                        <div className="space-y-2">
                            <label className="text-sm text-gray-600">Ghi chú</label>
                            <p className="text-sm bg-yellow-50 p-3 rounded border border-yellow-200">
                                {grDetail.notes}
                            </p>
                        </div>
                    )}
                </div>
            </div>

            {selectedImage && (
                <ImageViewer
                    imageBase64={selectedImage}
                    onClose={() => setSelectedImage(null)}
                />
            )}
        </div>
    );
};

export default GoodsReceiptDetailModal;