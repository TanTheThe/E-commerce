import React, { useState, useContext, useEffect } from 'react';
import { X, Plus, Trash2, AlertTriangle } from 'lucide-react';
import { MyContext } from '../../../App';
import { getDataApi, postDataApi } from '../../../utils/api';

const CreatePurchaseReturnModal = ({ isOpen, onClose, onSuccess, warehouseId, goodsReceiptId, openAlertBox }) => {
    const [formData, setFormData] = useState({
        goods_receipt_id: goodsReceiptId || '',
        return_reason: '',
        return_type: 'exchange',
        notes: '',
        return_items: []
    });

    const [warehouses, setWarehouses] = useState([]);
    const [goodsReceipts, setGoodsReceipts] = useState([]);
    const [grDetails, setGrDetails] = useState([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
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
        if (isOpen) {
            fetchWarehouses();
            fetchGoodsReceipts();
        }
    }, [isOpen]);

    useEffect(() => {
        if (goodsReceiptId) {
            setFormData(prev => ({ ...prev, goods_receipt_id: goodsReceiptId }));
            fetchGrDetails(goodsReceiptId);
        }
    }, [goodsReceiptId]);

    const fetchWarehouses = async () => {
        try {
            const response = await getDataApi('/admin/warehouse/all?limit=1000');
            if (response.success) {
                setWarehouses(response.data.data || []);
            } else {
                openAlertBox?.("error", response.data.detail.message);
            }
        } catch (error) {
            console.error('Error fetching warehouses:', error);
        }
    };

    const fetchGoodsReceipts = async () => {
        try {
            const response = await getDataApi(
                `/admin/goods-receipt?warehouse_id=${warehouseId}&status_gr=has_issue&limit=1000`
            );
            if (response.success) {
                setGoodsReceipts(response.data.data || []);
            } else {
                openAlertBox?.("error", response.data.detail.message);
            }
        } catch (error) {
            console.error('Error fetching goods receipts:', error);
        }
    };

    const fetchGrDetails = async (grId) => {
        try {
            const response = await getDataApi(`/admin/goods-receipt/${grId}`);
            if (response.success) {
                const details = response.data.items
                    .filter(item => {
                        const hasRejected = (item.rejected_quantity || 0) > 0;
                        const hasShortage = item.ordered_quantity > item.accepted_quantity;
                        return hasRejected || hasShortage;
                    })
                    .map(item => ({
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
                        variant_image: item.variant_image,
                        ordered_quantity: item.ordered_quantity
                    }));
                setGrDetails(details);
            } else {
                openAlertBox?.("error", response.data.detail.message);
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

        setErrors(prev => {
            const newErrors = { ...prev };
            delete newErrors[`item_${index}_gr`];
            delete newErrors[`item_${index}_quantity`];
            return newErrors;
        });

        setWarnings(prev => {
            const newWarnings = { ...prev };
            delete newWarnings[`item_${index}_gr`];
            delete newWarnings[`item_${index}_quantity`];
            return newWarnings;
        });
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
                            updated.accepted_quantity = detail.accepted_quantity;
                            updated.received_quantity = detail.received_quantity;
                            updated.returned_quantity = detail.returned_quantity;

                            const alreadyReturned = detail.returned_quantity || 0;
                            const needToReturn = detail.rejected_quantity || 0;

                            if (alreadyReturned >= needToReturn && needToReturn > 0) {
                                setWarnings(prev => ({
                                    ...prev,
                                    [`item_${index}_gr`]: `Sản phẩm này đã tạo đủ số lượng hoàn trả (${alreadyReturned}/${needToReturn})`
                                }));
                            } else {
                                setWarnings(prev => {
                                    const newWarnings = { ...prev };
                                    delete newWarnings[`item_${index}_gr`];
                                    return newWarnings;
                                });
                            }
                        }
                    }

                    if (field === 'return_quantity' || field === 'gr_detail_id') {
                        const detail = field === 'gr_detail_id'
                            ? grDetails.find(d => d.gr_detail_id === value)
                            : grDetails.find(d => d.gr_detail_id === item.gr_detail_id);

                        if (detail) {
                            const returnQty = field === 'return_quantity' ? parseInt(value) || 0 : parseInt(item.return_quantity) || 0;

                            const totalReturned = (detail.returned_quantity || 0) + returnQty;
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
                    const totalReturned = (detail.returned_quantity || 0) + returnQty;
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
                goods_receipt_id: formData.goods_receipt_id,
                return_items: formData.return_items.map(item => ({
                    gr_detail_id: item.gr_detail_id,
                    return_quantity: parseInt(item.return_quantity),
                    condition: item.condition,
                    rejection_evidence: item.rejection_evidence.length > 0 ? item.rejection_evidence : null,
                    notes: item.notes || null
                })),
                return_reason: formData.return_reason,
                return_type: formData.return_type,
                notes: formData.notes || null
            };

            const response = await postDataApi('/admin/return-purchase', submitData);

            if (response.success) {
                openAlertBox?.("success", response.message);
                onSuccess?.();
                handleClose();
            } else {
                openAlertBox?.("error", response?.data?.detail.message);
            }
        } catch (error) {
            console.error('Error creating purchase return:', error);
            openAlertBox?.("error", "Có lỗi xảy ra khi tạo đơn trả hàng");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleClose = () => {
        setFormData({
            goods_receipt_id: goodsReceiptId || '',
            return_reason: '',
            return_type: 'exchange',
            notes: '',
            return_items: []
        });
        setErrors({});
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
                    <h2 className="text-2xl font-bold text-gray-800">Tạo đơn trả hàng cho NCC</h2>
                    <button
                        onClick={handleClose}
                        className="text-gray-400 hover:text-gray-600 transition-colors"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-6">
                    <div className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Phiếu nhập kho <span className="text-red-500">*</span>
                                </label>
                                <select
                                    value={formData.goods_receipt_id}
                                    onChange={(e) => {
                                        setFormData({ ...formData, goods_receipt_id: e.target.value });
                                        if (e.target.value) fetchGrDetails(e.target.value);
                                    }}
                                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.goods_receipt_id ? 'border-red-500' : 'border-gray-300'}`}
                                >
                                    <option value="">Chọn phiếu nhập kho</option>
                                    {goodsReceipts.map(gr => (
                                        <option key={gr.id} value={gr.id}>{gr.receipt_number}</option>
                                    ))}
                                </select>
                                {errors.goods_receipt_id && <p className="mt-1 text-sm text-red-500">{errors.goods_receipt_id}</p>}
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
                                                            {detail.product_name} - {detail.variant_name} (Cần trả: {detail.rejected_quantity}, Đã nhận: {detail.accepted_quantity}/{detail.ordered_quantity})
                                                        </option>
                                                    ))}
                                                </select>
                                                {errors[`item_${index}_gr`] && <p className="mt-1 text-sm text-red-500">{errors[`item_${index}_gr`]}</p>}
                                                {!errors[`item_${index}_gr`] && warnings[`item_${index}_gr`] && (
                                                    <p className="mt-1 text-sm text-yellow-600 flex items-center gap-1">
                                                        <AlertTriangle className="w-4 h-4" />
                                                        {warnings[`item_${index}_gr`]}
                                                    </p>
                                                )}
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
                        {isSubmitting ? 'Đang tạo...' : 'Tạo đơn trả hàng'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CreatePurchaseReturnModal;