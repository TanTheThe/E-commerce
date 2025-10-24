import React, { useState, useEffect, useContext } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import { getDataApi, putDataApi } from '../../../utils/api';
import { MyContext } from "../../../App";

const formatDateForInput = (dateString) => {
    if (!dateString) return '';

    try {
        if (typeof dateString === 'string') {
            const match = dateString.match(/(\d{4})-(\d{2})-(\d{2})/);
            if (match) {
                return match[0];
            }
        }

        const date = new Date(dateString);
        if (isNaN(date.getTime())) return '';

        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');

        return `${year}-${month}-${day}`;
    } catch (e) {
        console.error('Error formatting date:', dateString, e);
        return '';
    }
};

const UpdateGoodsReceiptModal = ({ isOpen, onClose, onSuccess, grId }) => {
    const [formData, setFormData] = useState({
        receipt_date: '',
        delivery_note_number: '',
        has_discrepancy: false,
        discrepancy_notes: '',
        notes: '',
        receipt_details: []
    });
    const [originalData, setOriginalData] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [errors, setErrors] = useState({});
    const context = useContext(MyContext);

    useEffect(() => {
        if (isOpen && grId) {
            fetchGoodsReceipt();
        }
    }, [isOpen, grId]);

    const fetchGoodsReceipt = async () => {
        setIsLoading(true);
        try {
            const response = await getDataApi(`/admin/goods-receipt/${grId}`);
            if (response.success) {
                const gr = response.data;
                setOriginalData(gr);

                setFormData({
                    receipt_date: gr.receipt_date ? formatDateForInput(gr.receipt_date) : '',
                    delivery_note_number: gr.delivery_note_number || '',
                    has_discrepancy: gr.has_discrepancy || false,
                    discrepancy_notes: gr.discrepancy_notes || '',
                    notes: gr.notes || '',
                    receipt_details: gr.items?.map(item => ({
                        id: item.id,
                        product_variant_id: item.product_variant_id,
                        po_detail_id: item.po_detail_id,
                        ordered_quantity: item.ordered_quantity,
                        received_quantity: item.received_quantity,
                        accepted_quantity: item.accepted_quantity,
                        rejected_quantity: item.rejected_quantity,
                        unit_cost: item.unit_cost,
                        rejection_reason: item.rejection_reason || '',
                        notes: item.notes || '',
                        product_name: item.product_name,
                        variant_sku: item.variant_sku,
                        variant_size: item.variant_size,
                        variant_color_name: item.variant_color_name,
                        variant_image: item.variant_image
                    })) || []
                });
            }
        } catch (error) {
            console.error('Error fetching goods receipt:', error);
            context.openAlertBox("error", "Có lỗi xảy ra khi tải thông tin phiếu nhập kho");
        } finally {
            setIsLoading(false);
        }
    };

    const updateDetail = (index, field, value) => {
        setFormData(prev => ({
            ...prev,
            receipt_details: prev.receipt_details.map((detail, i) => {
                if (i === index) {
                    const updated = { ...detail, [field]: value };

                    if (field === 'received_quantity' || field === 'accepted_quantity') {
                        const received = field === 'received_quantity' ? parseInt(value) || 0 : parseInt(updated.received_quantity) || 0;
                        const accepted = field === 'accepted_quantity' ? parseInt(value) || 0 : parseInt(updated.accepted_quantity) || 0;
                        updated.rejected_quantity = Math.max(0, received - accepted);
                    }

                    return updated;
                }
                return detail;
            })
        }));
    };

    const validateForm = () => {
        const newErrors = {};

        if (!formData.receipt_date) {
            newErrors.receipt_date = 'Vui lòng chọn ngày nhận hàng';
        }

        if (formData.has_discrepancy && !formData.discrepancy_notes?.trim()) {
            newErrors.discrepancy_notes = 'Vui lòng nhập ghi chú về sai lệch';
        }

        formData.receipt_details.forEach((detail, index) => {
            if (detail.received_quantity < 0) {
                newErrors[`detail_${index}_received`] = 'Số lượng nhận phải >= 0';
            }
            if (detail.accepted_quantity < 0) {
                newErrors[`detail_${index}_accepted`] = 'Số lượng chấp nhận phải >= 0';
            }
            if (detail.accepted_quantity > detail.received_quantity) {
                newErrors[`detail_${index}_accepted`] = 'Số lượng chấp nhận không được lớn hơn số lượng nhận';
            }
            if (detail.rejected_quantity > 0 && !detail.rejection_reason?.trim()) {
                newErrors[`detail_${index}_rejection`] = 'Vui lòng nhập lý do từ chối';
            }
            if (detail.unit_cost <= 0) {
                newErrors[`detail_${index}_cost`] = 'Đơn giá phải > 0';
            }
        });

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async () => {
        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);
        try {
            const [year, month, day] = formData.receipt_date.split('-');
            const dateObj = new Date(year, parseInt(month) - 1, day);

            const submitData = {
                receipt_date: dateObj.toISOString(),
                delivery_note_number: formData.delivery_note_number || null,
                has_discrepancy: formData.has_discrepancy,
                discrepancy_notes: formData.discrepancy_notes || null,
                notes: formData.notes || null,
                receipt_details: formData.receipt_details.map(detail => ({
                    id: detail.id || null,
                    product_variant_id: detail.product_variant_id,
                    po_detail_id: detail.po_detail_id,
                    ordered_quantity: parseInt(detail.ordered_quantity),
                    received_quantity: parseInt(detail.received_quantity),
                    accepted_quantity: parseInt(detail.accepted_quantity),
                    rejected_quantity: parseInt(detail.rejected_quantity),
                    unit_cost: parseInt(detail.unit_cost),
                    rejection_reason: detail.rejection_reason || null,
                    notes: detail.notes || null
                }))
            };

            const response = await putDataApi(`/admin/goods-receipt/${grId}`, submitData);

            if (response.success) {
                context.openAlertBox("success", response.message || 'Cập nhật phiếu nhập kho thành công');
                onSuccess?.();
                handleClose();
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || "Có lỗi xảy ra khi cập nhật phiếu");
            }
        } catch (error) {
            console.error('Error updating goods receipt:', error);
            context.openAlertBox("error", "Có lỗi xảy ra khi cập nhật phiếu");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleClose = () => {
        setFormData({
            receipt_date: '',
            delivery_note_number: '',
            has_discrepancy: false,
            discrepancy_notes: '',
            notes: '',
            receipt_details: []
        });
        setOriginalData(null);
        setErrors({});
        onClose();
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(amount);
    };

    const calculateTotal = () => {
        return formData.receipt_details.reduce((sum, detail) =>
            sum + (parseInt(detail.accepted_quantity) || 0) * (parseInt(detail.unit_cost) || 0), 0
        );
    };

    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 bg-opacity-50 flex items-center justify-center z-50 p-4"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}
        >
            <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[85vh] flex flex-col">
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-800">Cập nhật phiếu nhập kho</h2>
                        {originalData && (
                            <p className="text-sm text-gray-600 mt-1">
                                Phiếu: {originalData.receipt_number} | PO: {originalData.purchase_order_number}
                            </p>
                        )}
                    </div>
                    <button
                        onClick={handleClose}
                        className="text-gray-400 hover:text-gray-600 transition-colors"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {isLoading ? (
                    <div className="flex-1 flex items-center justify-center p-6">
                        <div className="text-center">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                            <p className="text-gray-600">Đang tải dữ liệu...</p>
                        </div>
                    </div>
                ) : (
                    <>
                        <div className="flex-1 overflow-y-auto p-6">
                            <div className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Ngày nhận hàng <span className="text-red-500">*</span>
                                        </label>
                                        <input
                                            type="date"
                                            value={formData.receipt_date}
                                            onChange={(e) => setFormData({ ...formData, receipt_date: e.target.value })}
                                            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.receipt_date ? 'border-red-500' : 'border-gray-300'
                                                }`}
                                        />
                                        {errors.receipt_date && (
                                            <p className="mt-1 text-sm text-red-500">{errors.receipt_date}</p>
                                        )}
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Số phiếu giao hàng
                                        </label>
                                        <input
                                            type="text"
                                            value={formData.delivery_note_number}
                                            onChange={(e) => setFormData({ ...formData, delivery_note_number: e.target.value })}
                                            placeholder="Số phiếu của nhà cung cấp"
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={formData.has_discrepancy}
                                            onChange={(e) => setFormData({ ...formData, has_discrepancy: e.target.checked })}
                                            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                        />
                                        <span className="text-sm font-medium text-gray-700">Có sai lệch</span>
                                    </label>
                                </div>

                                {formData.has_discrepancy && (
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Ghi chú về sai lệch <span className="text-red-500">*</span>
                                        </label>
                                        <textarea
                                            value={formData.discrepancy_notes}
                                            onChange={(e) => setFormData({ ...formData, discrepancy_notes: e.target.value })}
                                            rows={3}
                                            placeholder="Mô tả chi tiết về sai lệch..."
                                            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none ${errors.discrepancy_notes ? 'border-red-500' : 'border-gray-300'
                                                }`}
                                        />
                                        {errors.discrepancy_notes && (
                                            <p className="mt-1 text-sm text-red-500">{errors.discrepancy_notes}</p>
                                        )}
                                    </div>
                                )}

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Ghi chú chung
                                    </label>
                                    <textarea
                                        value={formData.notes}
                                        onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                                        rows={3}
                                        placeholder="Ghi chú cho phiếu nhập kho..."
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-4">
                                        Chi tiết nhập kho <span className="text-red-500">*</span>
                                    </label>

                                    <div className="space-y-4">
                                        {formData.receipt_details.map((detail, index) => (
                                            <div key={index} className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                                                <div className="flex items-start gap-4 mb-3">
                                                    {detail.variant_image && (
                                                        <img
                                                            src={detail.variant_image}
                                                            alt={detail.product_name}
                                                            className="w-16 h-16 object-cover rounded border"
                                                        />
                                                    )}
                                                    <div className="flex-1">
                                                        <h4 className="font-semibold text-gray-900">{detail.product_name}</h4>
                                                        <p className="text-sm text-gray-600">
                                                            SKU: {detail.variant_sku} | Size: {detail.variant_size} | Màu: {detail.variant_color_name}
                                                        </p>
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                                    <div>
                                                        <label className="block text-xs font-medium text-gray-600 mb-1">
                                                            Đã đặt
                                                        </label>
                                                        <input
                                                            type="number"
                                                            value={detail.ordered_quantity}
                                                            disabled
                                                            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-gray-100 text-gray-700"
                                                        />
                                                    </div>

                                                    <div>
                                                        <label className="block text-xs font-medium text-gray-600 mb-1">
                                                            Đã nhận <span className="text-red-500">*</span>
                                                        </label>
                                                        <input
                                                            type="number"
                                                            min="0"
                                                            value={detail.received_quantity}
                                                            onChange={(e) => updateDetail(index, 'received_quantity', e.target.value)}
                                                            className={`w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors[`detail_${index}_received`] ? 'border-red-500' : 'border-gray-300'
                                                                }`}
                                                        />
                                                        {errors[`detail_${index}_received`] && (
                                                            <p className="mt-1 text-xs text-red-500">{errors[`detail_${index}_received`]}</p>
                                                        )}
                                                    </div>

                                                    <div>
                                                        <label className="block text-xs font-medium text-gray-600 mb-1">
                                                            Chấp nhận <span className="text-red-500">*</span>
                                                        </label>
                                                        <input
                                                            type="number"
                                                            min="0"
                                                            value={detail.accepted_quantity}
                                                            onChange={(e) => updateDetail(index, 'accepted_quantity', e.target.value)}
                                                            className={`w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors[`detail_${index}_accepted`] ? 'border-red-500' : 'border-gray-300'
                                                                }`}
                                                        />
                                                        {errors[`detail_${index}_accepted`] && (
                                                            <p className="mt-1 text-xs text-red-500">{errors[`detail_${index}_accepted`]}</p>
                                                        )}
                                                    </div>

                                                    <div>
                                                        <label className="block text-xs font-medium text-gray-600 mb-1">
                                                            Từ chối
                                                        </label>
                                                        <input
                                                            type="number"
                                                            value={detail.rejected_quantity}
                                                            disabled
                                                            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-red-50 text-red-700 font-medium"
                                                        />
                                                    </div>
                                                </div>

                                                {detail.rejected_quantity > 0 && (
                                                    <div className="mt-3">
                                                        <label className="block text-xs font-medium text-gray-600 mb-1">
                                                            Lý do từ chối <span className="text-red-500">*</span>
                                                        </label>
                                                        <input
                                                            type="text"
                                                            value={detail.rejection_reason}
                                                            onChange={(e) => updateDetail(index, 'rejection_reason', e.target.value)}
                                                            placeholder="Nhập lý do từ chối..."
                                                            className={`w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors[`detail_${index}_rejection`] ? 'border-red-500' : 'border-gray-300'
                                                                }`}
                                                        />
                                                        {errors[`detail_${index}_rejection`] && (
                                                            <p className="mt-1 text-xs text-red-500">{errors[`detail_${index}_rejection`]}</p>
                                                        )}
                                                    </div>
                                                )}

                                                <div className="grid grid-cols-2 gap-3 mt-3">
                                                    <div>
                                                        <label className="block text-xs font-medium text-gray-600 mb-1">
                                                            Đơn giá <span className="text-red-500">*</span>
                                                        </label>
                                                        <input
                                                            type="number"
                                                            min="0"
                                                            value={detail.unit_cost}
                                                            onChange={(e) => updateDetail(index, 'unit_cost', e.target.value)}
                                                            className={`w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors[`detail_${index}_cost`] ? 'border-red-500' : 'border-gray-300'
                                                                }`}
                                                        />
                                                        {errors[`detail_${index}_cost`] && (
                                                            <p className="mt-1 text-xs text-red-500">{errors[`detail_${index}_cost`]}</p>
                                                        )}
                                                    </div>

                                                    <div>
                                                        <label className="block text-xs font-medium text-gray-600 mb-1">
                                                            Thành tiền
                                                        </label>
                                                        <div className="w-full px-3 py-2 text-sm border border-gray-200 rounded-md bg-blue-50 text-blue-700 font-semibold">
                                                            {formatCurrency((detail.accepted_quantity || 0) * (detail.unit_cost || 0))}
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="mt-3">
                                                    <label className="block text-xs font-medium text-gray-600 mb-1">
                                                        Ghi chú
                                                    </label>
                                                    <input
                                                        type="text"
                                                        value={detail.notes}
                                                        onChange={(e) => updateDetail(index, 'notes', e.target.value)}
                                                        placeholder="Ghi chú cho sản phẩm này..."
                                                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                    />
                                                </div>
                                            </div>
                                        ))}
                                    </div>

                                    {formData.receipt_details.length > 0 && (
                                        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                            <div className="flex justify-between items-center">
                                                <span className="text-base font-medium text-gray-700">Tổng giá trị nhập kho:</span>
                                                <span className="text-xl font-bold text-blue-600">
                                                    {formatCurrency(calculateTotal())}
                                                </span>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
                            <button
                                type="button"
                                onClick={handleClose}
                                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
                            >
                                Hủy
                            </button>
                            <button
                                type="button"
                                onClick={handleSubmit}
                                disabled={isSubmitting}
                                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isSubmitting ? 'Đang cập nhật...' : 'Cập nhật phiếu nhập kho'}
                            </button>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default UpdateGoodsReceiptModal;