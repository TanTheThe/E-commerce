import React, { useState, useEffect, useCallback } from 'react';
import { Package, Search, Plus, Eye, Edit, Trash2, Calendar, DollarSign, User, Warehouse, TrendingUp, X, ChevronDown, ChevronUp } from 'lucide-react';
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
                        alt="Hóa đơn nhà cung cấp"
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

const PurchaseOrderDetailModal = ({ poId, onClose }) => {
    const [poDetail, setPoDetail] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [selectedImage, setSelectedImage] = useState(null);
    const [imageZoom, setImageZoom] = useState(1);

    useEffect(() => {
        const fetchDetail = async () => {
            setIsLoading(true);
            try {
                const response = await getDataApi(`/admin/purchase-orders/${poId}`);
                console.log(response);
                if (response.success) {
                    setPoDetail(response.data);
                }
            } catch (error) {
                console.error('Error fetching purchase order detail:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchDetail();
    }, [poId]);

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

    if (!poDetail) return null;

    const orderDate = formatDate(poDetail.order_date);
    const expectedDate = formatDate(poDetail.expected_delivery_date);
    const createdAt = formatDate(poDetail.created_at);
    const approvedAt = formatDate(poDetail.approved_at);

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
                <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-start">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">Chi tiết đơn nhập hàng</h2>
                        <div className="flex items-center gap-4">
                            <span className="text-lg font-semibold text-blue-600">{poDetail.po_number}</span>
                            <StatusBadge status={poDetail.status} />
                            <PaymentStatusBadge status={poDetail.payment_status} />
                        </div>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    <div className="grid grid-cols-2 gap-6">
                        <div className="bg-gray-50 rounded-lg p-4">
                            <h3 className="font-semibold text-gray-900 mb-3">Thông tin nhà cung cấp</h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Tên:</span>
                                    <span className="font-medium">{poDetail.supplier_name}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Mã:</span>
                                    <span className="font-medium">{poDetail.supplier_code}</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-gray-50 rounded-lg p-4">
                            <h3 className="font-semibold text-gray-900 mb-3">Thông tin kho</h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Tên:</span>
                                    <span className="font-medium">{poDetail.warehouse_name}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Mã:</span>
                                    <span className="font-medium">{poDetail.warehouse_code}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm text-gray-600">Ngày đặt hàng</label>
                            <p className={`font-medium ${!orderDate ? 'text-red-500' : ''}`}>
                                {orderDate || 'Chưa thống nhất với nhà cung cấp'}
                            </p>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm text-gray-600">Ngày giao dự kiến</label>
                            <p className={`font-medium ${!expectedDate ? 'text-red-500' : ''}`}>
                                {expectedDate || 'Chưa thống nhất với nhà cung cấp'}
                            </p>
                        </div>
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
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kích thước</th>
                                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">SL đặt</th>
                                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">SL nhận</th>
                                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Đơn giá</th>
                                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Thành tiền</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {poDetail.items.map((item) => (
                                        <tr key={item.id} className="hover:bg-gray-50">
                                            <td className="px-4 py-3">
                                                <div className="flex items-center gap-3">
                                                    {item.variant_image && (
                                                        <img
                                                            src={item.variant_image}
                                                            alt={item.product_name}
                                                            className="w-12 h-12 object-cover rounded"
                                                        />
                                                    )}
                                                    <span className="text-sm font-medium">{item.product_name}</span>
                                                </div>
                                            </td>
                                            <td className="px-4 py-3 text-sm">{item.variant_sku}</td>
                                            <td className="px-4 py-3 text-sm">{item.variant_color_name || '-'}</td>
                                            <td className="px-4 py-3 text-sm">{item.variant_size || '-'}</td>
                                            <td className="px-4 py-3 text-sm text-right">{item.quantity}</td>
                                            <td className="px-4 py-3 text-sm text-right font-medium">{item.received_quantity || 0}</td>
                                            <td className="px-4 py-3 text-sm text-right">{formatCurrency(item.unit_cost)}</td>
                                            <td className="px-4 py-3 text-sm text-right font-medium">{formatCurrency(item.total_cost)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div>
                        <h3 className="font-semibold text-gray-900 mb-3">Hóa đơn nhà cung cấp</h3>
                        {!poDetail.supplier_invoice_urls || poDetail.supplier_invoice_urls.length === 0 ? (
                            <p className="text-sm text-red-500 bg-red-50 p-3 rounded border border-red-200">
                                Chưa thống nhất với nhà cung cấp
                            </p>
                        ) : (
                            <div className="flex gap-3 flex-wrap">
                                {poDetail.supplier_invoice_urls.map((base64Image, index) => (
                                    <div
                                        key={index}
                                        className="relative cursor-pointer group"
                                        onClick={() => setSelectedImage(base64Image)}
                                    >
                                        <img
                                            src={base64Image}
                                            alt={`Hóa đơn ${index + 1}`}
                                            className="w-24 h-24 object-cover rounded border-2 border-gray-200 hover:border-blue-500 transition-all"
                                        />
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4">
                        <div className="max-w-md ml-auto space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Tạm tính:</span>
                                <span className="font-medium">{formatCurrency(poDetail.sub_total)}</span>
                            </div>

                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Giảm giá:</span>
                                {poDetail.discount_amount === 0 ? (
                                    <span className="font-medium text-red-500">
                                        Chưa thống nhất ý kiến với nhà cung cấp
                                    </span>
                                ) : (
                                    <span className="font-medium text-red-600">
                                        -{formatCurrency(poDetail.discount_amount)}
                                    </span>
                                )}
                            </div>

                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Phí vận chuyển:</span>
                                {poDetail.shipping_cost === 0 ? (
                                    <span className="font-medium text-red-500">
                                        Chưa thống nhất ý kiến với nhà cung cấp
                                    </span>
                                ) : (
                                    <span className="font-medium">{formatCurrency(poDetail.shipping_cost)}</span>
                                )}
                            </div>

                            <div className="border-t pt-2 flex justify-between">
                                <span className="font-semibold text-gray-900">Tổng cộng:</span>
                                <span className="font-bold text-lg text-blue-600">{formatCurrency(poDetail.total_amount)}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Đã thanh toán:</span>
                                <span className="font-medium text-green-600">{formatCurrency(poDetail.paid_amount || 0)}</span>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm text-gray-600">Người tạo</label>
                            <p className="font-medium">{poDetail.created_by_name}</p>
                            <p className={`text-xs ${!createdAt ? 'text-red-500' : 'text-gray-500'}`}>
                                {createdAt || 'Chưa thống nhất với nhà cung cấp'}
                            </p>
                        </div>
                        {poDetail.approved_by_name && (
                            <div className="space-y-2">
                                <label className="text-sm text-gray-600">Người duyệt</label>
                                <p className="font-medium">{poDetail.approved_by_name}</p>
                                <p className={`text-xs ${!approvedAt ? 'text-red-500' : 'text-gray-500'}`}>
                                    {approvedAt || 'Chưa thống nhất với nhà cung cấp'}
                                </p>
                            </div>
                        )}
                    </div>

                    {poDetail.notes && (
                        <div className="space-y-2">
                            <label className="text-sm text-gray-600">Ghi chú</label>
                            <p className="text-sm bg-yellow-50 p-3 rounded border border-yellow-200">{poDetail.notes}</p>
                        </div>
                    )}

                    {poDetail.cancellation_reason && (
                        <div className="space-y-2">
                            <label className="text-sm text-gray-600">Lý do hủy</label>
                            <p className="text-sm bg-red-50 p-3 rounded border border-red-200">{poDetail.cancellation_reason}</p>
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

export default PurchaseOrderDetailModal