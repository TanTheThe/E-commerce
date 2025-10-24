import React, { useState, useEffect, useContext } from 'react';
import { X, Plus, Trash2, AlertTriangle } from 'lucide-react';
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

const UpdateReturnPurchaseModal = ({ isOpen, onClose, onSuccess, prId, openAlertBox }) => {
    const [formData, setFormData] = useState({
        goods_receipt_id: '',
        return_reason: '',
        return_type: 'exchange',
        notes: '',
        return_items: []
    });

    const [originalData, setOriginalData] = useState(null);
    const [grDetails, setGrDetails] = useState([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [errors, setErrors] = useState({});
    const [warnings, setWarnings] = useState({});

    const returnTypeOptions = [
        { value: 'return_to_supplier', label: 'Trả hàng về NCC' },
        { value: 'exchange', label: 'Đổi hàng' },
        { value: 'refund', label: 'Hoàn tiền' }
    ];

    const conditionOptions = [
        { value: 'damaged', label: 'Hư hỏng' },
        { value: 'defective', label: 'Lỗi sản xuất' },
        { value: 'expired', label: 'Hết hạn' },
        { value: 'wrong_item', label: 'Sai hàng' }
    ];

    useEffect(() => {
        if (isOpen && prId) {
            fetchPurchaseReturn();
        }
    }, [isOpen, prId]);

    const fetchPurchaseReturn = async () => {
        setIsLoading(true);
        try {
            const response = await getDataApi(`/admin/return-purchase/${prId}`);
            if (response.success) {
                const pr = response.data;
                setOriginalData(pr);

                if (pr.goods_receipt_id) {
                    await fetchGrDetails(pr.goods_receipt_id);
                }

                setFormData({
                    goods_receipt_id: pr.goods_receipt_id || '',
                    return_reason: pr.return_reason || '',
                    return_type: pr.return_type || 'exchange',
                    notes: pr.notes || '',
                    return_items: pr.items?.map(item => ({
                        id: item.id,
                        gr_detail_id: item.goods_receipt_detail_id,
                        return_quantity: item.return_quantity,
                        condition: item.condition || 'damaged',
                        rejection_evidence: item.rejection_evidence || [],
                        notes: item.notes || '',
                        product_variant_id: item.product_variant_id,
                        product_name: item.product_name,
                        variant_sku: item.variant_sku,
                        variant_name: `${item.variant_color_name || ''} - ${item.variant_size || ''}`.trim(),
                        variant_image: item.variant_image
                    })) || []
                });
            } else {
                openAlertBox?.("error", response?.data?.detail?.message || "Có lỗi xảy ra");
            }
        } catch (error) {
            console.error('Error fetching purchase return:', error);
            openAlertBox?.("error", "Có lỗi xảy ra khi tải thông tin phiếu trả hàng");
        } finally {
            setIsLoading(false);
        }
    };

    const fetchGrDetails = async (grId) => {
        try {
            const response = await getDataApi(`/admin/goods-receipt/${grId}`);
            if (response.success) {
                const details = response.data.items.map(item => ({
                    gr_detail_id: item.id,
                    product_variant_id: item.product_variant_id,
                    product_name: item.product_name,
                    variant_name: `${item.variant_color_name || ''} - ${item.variant_size || ''}`.trim(),
                    accepted_quantity: item.accepted_quantity,
                    received_quantity: item.received_quantity,
                    rejected_quantity: item.rejected_quantity || 0,
                    returned_quantity: item.returned_quantity || 0,
                    unit_cost: item.unit_cost,
                    variant_sku: item.variant_sku,
                    variant_image: item.variant_image
                }));
                setGrDetails(details);
            }
        } catch (error) {
            console.error('Error fetching GR details:', error);
        }
    };

    const addItem = () => {
        const newItem = {
            gr_detail_id: '',
            return_quantity: 0,
            condition: 'damaged',
            rejection_evidence: [],
            notes: ''
        };

        setFormData(prev => ({
            ...prev,
            return_items: [...prev.return_items, newItem]
        }));
    };

    const removeItem = (index) => {
        setFormData(prev => ({
            ...prev,
            return_items: prev.return_items.filter((_, i) => i !== index)
        }));
    };

    const updateItem = (index, field, value) => {
        setFormData(prev => ({
            ...prev,
            return_items: prev.return_items.map((item, i) => {
                if (i === index) {
                    const updated = { ...item, [field]: value };

                    if (field === 'gr_detail_id' && value) {
                        const detail = grDetails.find(d => d.gr_detail_id === value);
                        if (detail) {
                            updated.product_variant_id = detail.product_variant_id;
                            updated.product_name = detail.product_name;
                            updated.variant_name = detail.variant_name;
                            updated.variant_sku = detail.variant_sku;
                            updated.variant_image = detail.variant_image;
                            updated.accepted_quantity = detail.accepted_quantity;
                            updated.received_quantity = detail.received_quantity;
                            updated.returned_quantity = detail.returned_quantity;
                        }
                    }

                    if (field === 'return_quantity' || field === 'gr_detail_id') {
                        const detail = field === 'gr_detail_id'
                            ? grDetails.find(d => d.gr_detail_id === value)
                            : grDetails.find(d => d.gr_detail_id === item.gr_detail_id);

                        if (detail) {
                            const returnQty = field === 'return_quantity' ? parseInt(value) || 0 : parseInt(item.return_quantity) || 0;

                            const currentItemOldQty = item.id
                                ? (originalData?.items?.find(origItem => origItem.id === item.id)?.return_quantity || 0)
                                : 0;

                            const otherPRsReturned = (detail.returned_quantity || 0) - currentItemOldQty;

                            const totalReturned = otherPRsReturned + returnQty;

                            const needToReturn = detail.rejected_quantity || 0;

                            setErrors(prev => {
                                const newErrors = { ...prev };

                                if (totalReturned > needToReturn) {
                                    newErrors[`item_${index}_quantity`] = `Số lượng trả (${totalReturned}) không được vượt quá số lượng cần hoàn trả (${needToReturn})`;
                                } else {
                                    delete newErrors[`item_${index}_quantity`];
                                }

                                return newErrors;
                            });

                            setWarnings(prev => {
                                const newWarnings = { ...prev };

                                if (totalReturned > needToReturn) {
                                    delete newWarnings[`item_${index}_quantity`];
                                }
                                else if (totalReturned < needToReturn) {
                                    newWarnings[`item_${index}_quantity`] = `Số lượng trả về chưa đủ so với số lượng cần hoàn trả (${needToReturn})`;
                                }
                                else {
                                    delete newWarnings[`item_${index}_quantity`];
                                }

                                return newWarnings;
                            });
                        }
                    }

                    return updated;
                }
                return item;
            })
        }));
    };

    const validateForm = () => {
        const newErrors = {};

        if (!formData.goods_receipt_id) {
            newErrors.goods_receipt_id = 'Vui lòng chọn phiếu nhập kho';
        }

        if (!formData.return_reason) {
            newErrors.return_reason = 'Vui lòng nhập lý do trả hàng';
        }

        if (formData.return_items.length === 0) {
            newErrors.return_items = 'Vui lòng thêm ít nhất 1 sản phẩm trả hàng';
        } else {
            formData.return_items.forEach((item, index) => {
                if (!item.gr_detail_id) {
                    newErrors[`item_${index}_gr`] = 'Vui lòng chọn chi tiết GR';
                }
                if (item.return_quantity <= 0) {
                    newErrors[`item_${index}_quantity`] = 'Số lượng trả phải lớn hơn 0';
                }
                const detail = grDetails.find(d => d.gr_detail_id === item.gr_detail_id);
                if (detail) {
                    const returnQty = parseInt(item.return_quantity) || 0;

                    const currentItemOldQty = item.id
                        ? (originalData?.items?.find(origItem => origItem.id === item.id)?.return_quantity || 0)
                        : 0;

                    const otherPRsReturned = (detail.returned_quantity || 0) - currentItemOldQty;

                    const totalReturned = otherPRsReturned + returnQty;

                    const needToReturn = detail.rejected_quantity || 0;

                    if (totalReturned > needToReturn) {
                        newErrors[`item_${index}_quantity`] = `Số lượng trả (${totalReturned}) không được vượt quá số lượng cần hoàn trả (${needToReturn})`;
                    }
                }
            });
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async () => {
        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);

        try {
            const submitData = {
                return_reason: formData.return_reason,
                return_type: formData.return_type,
                notes: formData.notes || null,
                return_details: formData.return_items.map(item => {
                    const detail = grDetails.find(d => d.gr_detail_id === item.gr_detail_id);
                    return {
                        id: item.id || undefined,
                        product_variant_id: item.product_variant_id,
                        goods_receipt_detail_id: item.gr_detail_id,
                        return_quantity: parseInt(item.return_quantity),
                        unit_cost: detail?.unit_cost || 0,
                        condition: item.condition,
                        rejection_evidence: item.rejection_evidence.length > 0 ? item.rejection_evidence : undefined,
                        notes: item.notes || undefined
                    };
                })
            };

            const response = await putDataApi(`/admin/return-purchase/${prId}`, submitData);

            if (response.success) {
                openAlertBox?.("success", response.message || 'Cập nhật phiếu trả hàng thành công');
                onSuccess?.();
                handleClose();
            } else {
                openAlertBox?.("error", response?.data?.detail?.message);
            }
        } catch (error) {
            console.error('Error updating purchase return:', error);
            openAlertBox?.("error", "Có lỗi xảy ra khi cập nhật đơn trả hàng");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleClose = () => {
        setFormData({
            goods_receipt_id: '',
            return_reason: '',
            return_type: 'exchange',
            notes: '',
            return_items: []
        });
        setOriginalData(null);
        setGrDetails([]);
        setErrors({});
        setWarnings({});
        onClose();
    };

    const getGrDetailDisplay = (grDetailId) => {
        const detail = grDetails.find(d => d.gr_detail_id === grDetailId);
        return detail ? `${detail.product_name} - ${detail.variant_name}` : '';
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-opacity-50 flex items-center justify-center z-50 p-4"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}>
            <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] flex flex-col">
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-800">Cập nhật đơn trả hàng cho NCC</h2>
                        {originalData && (
                            <p className="text-sm text-gray-600 mt-1">
                                Phiếu: {originalData.return_number} | PO: {originalData.purchase_order_number} | NCC: {originalData.supplier_name}
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
                                            Phiếu nhập kho <span className="text-red-500">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            value={originalData?.goods_receipt_number || ''}
                                            disabled
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-600 cursor-not-allowed"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Loại trả hàng <span className="text-red-500">*</span>
                                        </label>
                                        <select
                                            value={formData.return_type}
                                            onChange={(e) => setFormData({ ...formData, return_type: e.target.value })}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        >
                                            {returnTypeOptions.map(option => (
                                                <option key={option.value} value={option.value}>{option.label}</option>
                                            ))}
                                        </select>
                                    </div>

                                    <div className="md:col-span-2">
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Lý do trả hàng <span className="text-red-500">*</span>
                                        </label>
                                        <textarea
                                            value={formData.return_reason}
                                            onChange={(e) => setFormData({ ...formData, return_reason: e.target.value })}
                                            rows={3}
                                            placeholder="Nhập lý do trả hàng cho nhà cung cấp..."
                                            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.return_reason ? 'border-red-500' : 'border-gray-300'}`}
                                        />
                                        {errors.return_reason && <p className="mt-1 text-sm text-red-500">{errors.return_reason}</p>}
                                    </div>

                                    <div className="md:col-span-2">
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Ghi chú chung
                                        </label>
                                        <textarea
                                            value={formData.notes}
                                            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                                            rows={2}
                                            placeholder="Ghi chú thêm về đơn trả hàng..."
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <div className="flex items-center justify-between mb-4">
                                        <label className="block text-sm font-medium text-gray-700">
                                            Chi tiết sản phẩm trả hàng <span className="text-red-500">*</span>
                                        </label>
                                        <button
                                            type="button"
                                            onClick={addItem}
                                            className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
                                        >
                                            <Plus className="w-4 h-4" />
                                            Thêm sản phẩm
                                        </button>
                                    </div>

                                    {errors.return_items && <p className="mb-3 text-sm text-red-500">{errors.return_items}</p>}

                                    <div className="space-y-4">
                                        {formData.return_items.map((item, index) => (
                                            <div key={index} className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                                                <div className="flex items-start justify-between mb-3">
                                                    <span className="text-sm font-medium text-gray-700">
                                                        Sản phẩm #{index + 1}
                                                    </span>
                                                    <button
                                                        type="button"
                                                        onClick={() => removeItem(index)}
                                                        className="text-red-500 hover:text-red-700 transition-colors"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>

                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                                    <div className="md:col-span-2">
                                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                                            Chi tiết GR <span className="text-red-500">*</span>
                                                        </label>
                                                        <select
                                                            value={item.gr_detail_id}
                                                            onChange={(e) => updateItem(index, 'gr_detail_id', e.target.value)}
                                                            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors[`item_${index}_gr`] ? 'border-red-500' : 'border-gray-300'}`}
                                                        >
                                                            <option value="">Chọn sản phẩm từ GR</option>
                                                            {grDetails.map(detail => (
                                                                <option key={detail.gr_detail_id} value={detail.gr_detail_id}>
                                                                    {detail.product_name} - {detail.variant_name} (Đã nhận: {detail.accepted_quantity})
                                                                </option>
                                                            ))}
                                                        </select>
                                                        {errors[`item_${index}_gr`] && <p className="mt-1 text-sm text-red-500">{errors[`item_${index}_gr`]}</p>}
                                                    </div>

                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                                            Số lượng trả <span className="text-red-500">*</span>
                                                        </label>
                                                        <input
                                                            type="number"
                                                            min="0"
                                                            value={item.return_quantity}
                                                            onChange={(e) => updateItem(index, 'return_quantity', e.target.value)}
                                                            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors[`item_${index}_quantity`] ? 'border-red-500' : 'border-gray-300'}`}
                                                        />
                                                        {errors[`item_${index}_quantity`] && <p className="mt-1 text-sm text-red-500">{errors[`item_${index}_quantity`]}</p>}
                                                        {!errors[`item_${index}_quantity`] && warnings[`item_${index}_quantity`] && (
                                                            <p className="mt-1 text-sm text-yellow-600 flex items-center gap-1">
                                                                <AlertTriangle className="w-4 h-4" />
                                                                {warnings[`item_${index}_quantity`]}
                                                            </p>
                                                        )}
                                                    </div>

                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                                            Tình trạng hàng <span className="text-red-500">*</span>
                                                        </label>
                                                        <select
                                                            value={item.condition}
                                                            onChange={(e) => updateItem(index, 'condition', e.target.value)}
                                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                        >
                                                            {conditionOptions.map(option => (
                                                                <option key={option.value} value={option.value}>{option.label}</option>
                                                            ))}
                                                        </select>
                                                    </div>

                                                    <div className="md:col-span-2">
                                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                                            Ghi chú
                                                        </label>
                                                        <input
                                                            type="text"
                                                            value={item.notes}
                                                            onChange={(e) => updateItem(index, 'notes', e.target.value)}
                                                            placeholder="Ghi chú cho sản phẩm này..."
                                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                        />
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
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
                                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isSubmitting ? 'Đang cập nhật...' : 'Cập nhật đơn trả hàng'}
                            </button>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default UpdateReturnPurchaseModal;