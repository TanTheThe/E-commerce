import React, { useState, useEffect } from 'react';
import { X, CheckCircle, AlertTriangle, Package, TrendingUp, FileText } from 'lucide-react';
import { getDataApi } from '../../../utils/api';

const StatusBadge = ({ status, isPreview = false }) => {
    const statusConfig = {
        pending: { label: 'Chờ xử lý', color: 'bg-yellow-100 text-yellow-700' },
        approved: { label: 'Đã chấp nhận', color: 'bg-blue-100 text-blue-700' },
        completed: { label: 'Hoàn thành', color: 'bg-green-100 text-green-700' },
        cancelled: { label: 'Đã hủy', color: 'bg-red-100 text-red-700' },
        has_issue: { label: 'Có vấn đề', color: 'bg-orange-100 text-orange-700' },
        partial_received: { label: 'Nhận một nữa', color: 'bg-orange-100 text-orange-700' }
    };

    const config = statusConfig[status] || { label: status, color: 'bg-gray-100 text-gray-700' };

    return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color} ${isPreview ? 'border-2 border-dashed border-current' : ''}`}>
            {config.label}
        </span>
    );
};

const StatusTransition = ({ currentStatus, predictedStatus, label }) => {
    return (
        <div className="flex items-center gap-3 bg-gray-50 p-3 rounded-lg">
            <div className="flex-1">
                <p className="text-xs text-gray-500 mb-1">{label} hiện tại</p>
                <StatusBadge status={currentStatus} />
            </div>
            <div className="text-gray-400">
                <TrendingUp className="w-5 h-5" />
            </div>
            <div className="flex-1">
                <p className="text-xs text-gray-500 mb-1">{label} sau khi duyệt</p>
                <StatusBadge status={predictedStatus} isPreview={true} />
            </div>
        </div>
    );
};

const VariantComparisonCard = ({ variant }) => {
    const isComplete = variant.is_complete;
    const percentage = variant.ordered > 0
        ? Math.round((variant.total_accepted / variant.ordered) * 100)
        : 0;

    return (
        <div className={`border rounded-lg p-4 ${isComplete ? 'border-green-200 bg-green-50' : 'border-orange-200 bg-orange-50'}`}>
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                    {isComplete ? (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                        <AlertTriangle className="w-5 h-5 text-orange-600" />
                    )}
                    <span className="font-medium text-sm">
                        {isComplete ? 'Đủ số lượng' : 'Thiếu hàng'}
                    </span>
                </div>
                <span className={`text-xs font-medium px-2 py-1 rounded ${percentage === 100 ? 'bg-green-200 text-green-800' :
                    percentage >= 50 ? 'bg-orange-200 text-orange-800' :
                        'bg-red-200 text-red-800'
                    }`}>
                    {percentage}%
                </span>
            </div>

            <div className="grid grid-cols-3 gap-3 text-sm">
                <div>
                    <p className="text-gray-600 text-xs mb-1">Đã đặt</p>
                    <p className="font-semibold text-gray-900">{variant.ordered}</p>
                </div>
                <div>
                    <p className="text-gray-600 text-xs mb-1">Đã nhận đạt</p>
                    <p className={`font-semibold ${isComplete ? 'text-green-600' : 'text-orange-600'}`}>
                        {variant.total_accepted}
                    </p>
                </div>
                <div>
                    <p className="text-gray-600 text-xs mb-1">Còn thiếu</p>
                    <p className="font-semibold text-red-600">
                        {Math.max(0, variant.ordered - variant.total_accepted)}
                    </p>
                </div>
            </div>

            {!isComplete && (
                <div className="mt-3 pt-3 border-t border-orange-200">
                    <p className="text-xs text-orange-700">
                        <AlertTriangle className="w-3 h-3 inline mr-1" />
                        Cần tạo phiếu hoàn trả hoặc phiếu nhập bổ sung
                    </p>
                </div>
            )}
        </div>
    );
};

const ApprovalPreviewModal = ({ grId, onClose }) => {
    const [previewData, setPreviewData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!grId) return;

        const fetchPreview = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const response = await getDataApi(`/admin/goods-receipt/${grId}/approval-preview`);
                if (response.success) {
                    setPreviewData(response.data);
                } else {
                    setError('Không thể tải thông tin xem trước');
                }
            } catch (error) {
                console.error('Error fetching approval preview:', error);
                setError('Đã xảy ra lỗi khi tải dữ liệu');
            } finally {
                setIsLoading(false);
            }
        };

        fetchPreview();
    }, [grId]);

    if (isLoading) {
        return (
            <div
                className="fixed inset-0 bg-opacity-50 flex items-center justify-center z-50"
                onClick={onClose}
                style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}
            >
                <div
                    className="bg-white rounded-lg p-8 w-full max-w-5xl max-h-[90vh] overflow-auto"
                    onClick={(e) => e.stopPropagation()}
                >
                    <div className="animate-pulse space-y-4">
                        <div className="h-8 bg-gray-200 rounded w-1/3"></div>
                        <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                        <div className="h-32 bg-gray-200 rounded"></div>
                        <div className="h-32 bg-gray-200 rounded"></div>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div
                className="fixed inset-0 bg-opacity-50 flex items-center justify-center z-50"
                onClick={onClose}
                style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}
            >
                <div
                    className="bg-white rounded-lg p-6 w-full max-w-md"
                    onClick={(e) => e.stopPropagation()}
                >
                    <div className="flex items-center gap-3 mb-4">
                        <AlertTriangle className="w-8 h-8 text-red-500" />
                        <h3 className="text-lg font-semibold text-gray-900">Lỗi</h3>
                    </div>
                    <p className="text-gray-600 mb-4">{error}</p>
                    <button
                        onClick={onClose}
                        className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                    >
                        Đóng
                    </button>
                </div>
            </div>
        );
    }

    if (!previewData) return null;

    const { goods_receipt, purchase_order, summary, variant_details } = previewData;
    const completeVariants = variant_details.filter(v => v.is_complete).length;
    const incompleteVariants = variant_details.filter(v => !v.is_complete).length;

    return (
        <div
            className="fixed inset-0 bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={onClose}
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}
        >
            <div
                className="bg-white rounded-lg w-full max-w-5xl max-h-[85vh] overflow-auto"
                onClick={(e) => e.stopPropagation()}
            >
                <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-start z-10">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">
                            Xem trước kết quả phê duyệt
                        </h2>
                        <p className="text-sm text-gray-600">
                            Phiếu nhập hàng: <span className="font-semibold text-blue-600">{goods_receipt.receipt_number}</span>
                        </p>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    <div className={`rounded-lg p-4 flex items-start gap-3 ${summary.all_completed
                        ? 'bg-green-50 border border-green-200'
                        : 'bg-orange-50 border border-orange-200'
                        }`}>
                        {summary.all_completed ? (
                            <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
                        ) : (
                            <AlertTriangle className="w-6 h-6 text-orange-600 flex-shrink-0 mt-0.5" />
                        )}
                        <div className="flex-1">
                            <h3 className={`font-semibold mb-1 ${summary.all_completed ? 'text-green-900' : 'text-orange-900'
                                }`}>
                                {summary.all_completed ? 'Đơn hàng hoàn tất' : 'Đơn hàng chưa hoàn tất'}
                            </h3>
                            <p className={`text-sm ${summary.all_completed ? 'text-green-700' : 'text-orange-700'
                                }`}>
                                {summary.message}
                            </p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-white border border-gray-200 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-3">
                                <Package className="w-5 h-5 text-blue-600" />
                                <h3 className="font-semibold text-gray-900">Phiếu nhập hàng</h3>
                            </div>
                            <StatusTransition
                                currentStatus={goods_receipt.current_status}
                                predictedStatus={goods_receipt.predicted_status}
                                label="Trạng thái"
                            />
                            <div className="mt-3 text-sm text-gray-600">
                                <p>Kho: <span className="font-medium">{goods_receipt.warehouse.name}</span></p>
                            </div>
                        </div>

                        <div className="bg-white border border-gray-200 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-3">
                                <FileText className="w-5 h-5 text-purple-600" />
                                <h3 className="font-semibold text-gray-900">Đơn nhập hàng</h3>
                            </div>
                            <StatusTransition
                                currentStatus={purchase_order.current_status}
                                predictedStatus={purchase_order.predicted_status}
                                label="Trạng thái"
                            />
                            <div className="mt-3 text-sm text-gray-600">
                                <p>Mã đơn: <span className="font-medium">{purchase_order.po_number}</span></p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-200">
                        <h3 className="font-semibold text-gray-900 mb-3">Tổng quan</h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="text-center">
                                <p className="text-2xl font-bold text-blue-600">{summary.total_variants}</p>
                                <p className="text-xs text-gray-600 mt-1">Tổng biến thể</p>
                            </div>
                            <div className="text-center">
                                <p className="text-2xl font-bold text-green-600">{completeVariants}</p>
                                <p className="text-xs text-gray-600 mt-1">Đủ số lượng</p>
                            </div>
                            <div className="text-center">
                                <p className="text-2xl font-bold text-orange-600">{incompleteVariants}</p>
                                <p className="text-xs text-gray-600 mt-1">Còn thiếu</p>
                            </div>
                            <div className="text-center">
                                <p className="text-2xl font-bold text-purple-600">
                                    {summary.will_update_stock ? 'Có' : 'Không'}
                                </p>
                                <p className="text-xs text-gray-600 mt-1">Cập nhật kho</p>
                            </div>
                        </div>
                    </div>

                    <div>
                        <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                            <Package className="w-5 h-5" />
                            Chi tiết từng biến thể ({variant_details.length})
                        </h3>
                        <div className="space-y-3">
                            {variant_details && variant_details.length > 0 ? (
                                variant_details.map((variant, index) => (
                                    <VariantComparisonCard key={variant.variant_id || index} variant={variant} />
                                ))
                            ) : (
                                <p className="text-center text-gray-500 py-4">Không có biến thể nào</p>
                            )}
                        </div>
                    </div>

                    {!summary.all_completed && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                            <h4 className="font-semibold text-yellow-900 mb-2 flex items-center gap-2">
                                <AlertTriangle className="w-5 h-5" />
                                Hành động cần thực hiện sau khi duyệt
                            </h4>
                            <ul className="text-sm text-yellow-800 space-y-1 ml-7">
                                <li>• Tạo phiếu hoàn trả cho số lượng bị loại (nếu có)</li>
                                <li>• Hoặc tạo phiếu nhập bổ sung cho số lượng còn thiếu</li>
                                <li>• Liên hệ nhà cung cấp để xử lý chênh lệch</li>
                            </ul>
                        </div>
                    )}

                    {summary.will_update_stock && (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                                <CheckCircle className="w-5 h-5" />
                                Cập nhật tồn kho
                            </h4>
                            <p className="text-sm text-blue-800">
                                Tồn kho tại <span className="font-medium">{goods_receipt.warehouse.name}</span> sẽ được cập nhật tự động với số lượng đã nhận đạt yêu cầu.
                            </p>
                        </div>
                    )}
                </div>

                <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 p-4 flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                    >
                        Đóng
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ApprovalPreviewModal;