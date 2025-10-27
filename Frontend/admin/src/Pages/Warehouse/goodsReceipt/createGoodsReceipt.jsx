import React, { useState, useContext, useEffect } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import { getDataApi, postDataApi } from '../../../utils/api';

const CreateGoodsReceiptModal = ({ isOpen, onClose, onSuccess, warehouseId, purchaseOrderId, openAlertBox }) => {
    const [formData, setFormData] = useState({
        purchase_order_id: purchaseOrderId || '',
        warehouse_id: warehouseId || '',
        supplier_id: '',
        receipt_date: new Date().toISOString().split('T')[0],
        delivery_note_number: '',
        parent_receipt_id: '',
        notes: '',
        items: []
    });

    const [suppliers, setSuppliers] = useState([]);
    const [warehouses, setWarehouses] = useState([]);
    const [purchaseOrders, setPurchaseOrders] = useState([]);
    const [parentReceipts, setParentReceipts] = useState([]);
    const [poDetails, setPoDetails] = useState([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [errors, setErrors] = useState({});
    const [parentReceiptDetails, setParentReceiptDetails] = useState(null);

    useEffect(() => {
        if (isOpen) {
            fetchSuppliers();
            fetchWarehouses();
            fetchPurchaseOrders();
        }
    }, [isOpen]);

    useEffect(() => {
        if (warehouseId) {
            setFormData(prev => ({ ...prev, warehouse_id: warehouseId }));
        }
    }, [warehouseId]);

    useEffect(() => {
        if (purchaseOrderId) {
            setFormData(prev => ({ ...prev, purchase_order_id: purchaseOrderId }));
            fetchPoDetails(purchaseOrderId);
        }
    }, [purchaseOrderId]);

    useEffect(() => {
        if (formData.parent_receipt_id) {
            fetchParentReceiptDetails(formData.parent_receipt_id);
        } else {
            setParentReceiptDetails(null);
            setFormData(prev => ({
                ...prev,
                items: prev.items.map(item => {
                    const poDetail = poDetails.find(d => d.po_detail_id === item.po_detail_id);
                    if (poDetail) {
                        return { ...item, ordered_quantity: poDetail.ordered_quantity };
                    }
                    return item;
                })
            }));
        }
    }, [formData.parent_receipt_id]);

    useEffect(() => {
        if (formData.purchase_order_id && formData.warehouse_id) {
            fetchParentReceipts();
        } else {
            setParentReceipts([]);
        }
    }, [formData.purchase_order_id, formData.warehouse_id]);

    const fetchSuppliers = async () => {
        try {
            const response = await getDataApi('/admin/suppliers?limit=1000');
            if (response.success) {
                setSuppliers(response.data.data || []);
            } else {
                openAlertBox?.("error", response.data.detail.message)
            }
        } catch (error) {
            console.error('Error fetching suppliers:', error);
        }
    };

    const fetchWarehouses = async () => {
        try {
            const response = await getDataApi('/admin/warehouse/all?limit=1000');
            if (response.success) {
                setWarehouses(response.data.data || []);
            } else {
                openAlertBox?.("error", response.data.detail.message)
            }
        } catch (error) {
            console.error('Error fetching warehouses:', error);
        }
    };

    const fetchPurchaseOrders = async () => {
        try {
            const response = await getDataApi('/admin/purchase-orders/all?po_status=confirmed,partial_received&limit=1000');
            if (response.success) {
                setPurchaseOrders(response.data.data || []);
            } else {
                openAlertBox?.("error", response.data.detail.message)
            }
        } catch (error) {
            console.error('Error fetching purchase orders:', error);
        }
    };

    const fetchParentReceipts = async () => {
        try {
            const response = await getDataApi(
                `/admin/goods-receipt?warehouse_id=${formData.warehouse_id}&status_gr=has_issue&purchase_order_id=${formData.purchase_order_id}&limit=1000`
            );
            if (response.success) {
                setParentReceipts(response.data.data || []);
            } else {
                openAlertBox?.("error", response.data.detail.message)
            }
        } catch (error) {
            console.error('Error fetching parent receipts:', error);
        }
    };

    const fetchPoDetails = async (poId) => {
        try {
            const response = await getDataApi(`/admin/purchase-orders/${poId}`);
            if (response.success) {
                const details = response.data.items.map(item => ({
                    po_detail_id: item.id,
                    product_variant_id: item.product_variant_id,
                    product_name: item.product_name,
                    variant_name: `${item.variant_color_name || ''} - ${item.variant_size || ''}`.trim(),
                    ordered_quantity: item.quantity,
                    variant_sku: item.variant_sku,
                    variant_image: item.variant_image
                }));
                setPoDetails(details);
            } else {
                openAlertBox?.("error", response.data.detail.message)
            }
        } catch (error) {
            console.error('Error fetching PO details:', error);
        }
    };

    const fetchParentReceiptDetails = async (parentId) => {
        try {
            const response = await getDataApi(`/admin/goods-receipt/create-info/${parentId}`);
            if (response.success) {
                setParentReceiptDetails(response.data);

                const newItems = response.data.items.map(item => ({
                    po_detail_id: '', 
                    product_variant_id: item.product_variant_id,
                    ordered_quantity: item.ordered_quantity,
                    received_quantity: 0,
                    accepted_quantity: 0,
                    rejected_quantity: 0,
                    rejection_reason: '',
                    notes: ''
                }));

                setFormData(prev => ({
                    ...prev,
                    items: newItems
                }));
            } else {
                openAlertBox?.("error", response.data.detail.message);
            }
        } catch (error) {
            console.error('Error fetching parent receipt details:', error);
            openAlertBox?.("error", "Không thể tải thông tin GR cha");
        }
    };

    const addItem = () => {
        const newItem = {
            po_detail_id: '',
            product_variant_id: '',
            ordered_quantity: 0,
            received_quantity: 0,
            accepted_quantity: 0,
            rejected_quantity: 0,
            rejection_reason: '',
            notes: ''
        };

        setFormData(prev => ({
            ...prev,
            items: [...prev.items, newItem]
        }));
    };

    const removeItem = (index) => {
        setFormData(prev => ({
            ...prev,
            items: prev.items.filter((_, i) => i !== index)
        }));
    };

    const updateItem = (index, field, value) => {
        setFormData(prev => ({
            ...prev,
            items: prev.items.map((item, i) => {
                if (i === index) {
                    const updated = { ...item, [field]: value };

                    if (field === 'po_detail_id' && value) {
                        if (parentReceiptDetails) {
                            const parentItem = parentReceiptDetails.items.find(
                                pi => pi.product_variant_id === updated.product_variant_id
                            );

                            if (parentItem) {
                                updated.ordered_quantity = parentItem.ordered_quantity;
                            } else {
                                openAlertBox?.("warning", "Sản phẩm này không có trong GR cha");
                                return item;
                            }
                        } else {
                            const detail = poDetails.find(d => d.po_detail_id === value);
                            if (detail) {
                                updated.product_variant_id = detail.product_variant_id;
                                updated.ordered_quantity = detail.ordered_quantity;
                            }
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

        if (!formData.purchase_order_id) {
            newErrors.purchase_order_id = 'Vui lòng chọn đơn đặt hàng';
        }

        if (!formData.warehouse_id) {
            newErrors.warehouse_id = 'Vui lòng chọn kho nhận hàng';
        }

        if (!formData.supplier_id) {
            newErrors.supplier_id = 'Vui lòng chọn nhà cung cấp';
        }

        if (formData.items.length === 0) {
            newErrors.items = 'Vui lòng thêm ít nhất 1 sản phẩm';
        } else {
            formData.items.forEach((item, index) => {
                if (!item.po_detail_id) {
                    newErrors[`item_${index}_po`] = 'Vui lòng chọn chi tiết PO';
                }
                if (item.received_quantity < 0) {
                    newErrors[`item_${index}_received`] = 'Số lượng nhận không thể âm';
                }
                if (item.accepted_quantity < 0) {
                    newErrors[`item_${index}_accepted`] = 'Số lượng chấp nhận không thể âm';
                }
                if (item.rejected_quantity < 0) {
                    newErrors[`item_${index}_rejected`] = 'Số lượng từ chối không thể âm';
                }

                if (parentReceiptDetails) {
                    const parentItem = parentReceiptDetails.items.find(
                        pi => pi.product_variant_id === item.product_variant_id
                    );

                    if (parentItem) {
                        const maxAcceptable = parentItem.ordered_quantity;

                        if (item.accepted_quantity > maxAcceptable) {
                            newErrors[`item_${index}_accepted`] =
                                `Số lượng chấp nhận không được vượt quá ${maxAcceptable} (số lượng còn lại từ GR cha)`;
                        }

                        if (item.ordered_quantity !== maxAcceptable) {
                            newErrors[`item_${index}_ordered`] =
                                `Số lượng đặt phải bằng ${maxAcceptable} (từ GR cha)`;
                        }
                    }
                }

                if (
                    item.received_quantity > 0 &&
                    (Number(item.accepted_quantity) + Number(item.rejected_quantity)) !== Number(item.received_quantity)
                ) {
                    newErrors[`item_${index}_total`] = 'Tổng chấp nhận + từ chối phải bằng số lượng nhận';
                }
                if (item.rejected_quantity > 0 && !item.rejection_reason) {
                    newErrors[`item_${index}_reason`] = 'Vui lòng nhập lý do từ chối';
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
                purchase_order_id: formData.purchase_order_id,
                warehouse_id: formData.warehouse_id,
                supplier_id: formData.supplier_id,
                receipt_date: new Date(formData.receipt_date).toISOString(),
                delivery_note_number: formData.delivery_note_number || null,
                parent_receipt_id: formData.parent_receipt_id || null,
                notes: formData.notes || null,
                items: formData.items.map(item => ({
                    po_detail_id: item.po_detail_id,
                    product_variant_id: item.product_variant_id,
                    ordered_quantity: parseInt(item.ordered_quantity),
                    received_quantity: parseInt(item.received_quantity),
                    accepted_quantity: parseInt(item.accepted_quantity),
                    rejected_quantity: parseInt(item.rejected_quantity),
                    rejection_reason: item.rejection_reason || null,
                    notes: item.notes || null
                }))
            };

            const response = await postDataApi('/admin/goods-receipt', submitData);

            if (response.success) {
                openAlertBox?.("success", response.message);
                onSuccess?.();
                handleClose();
            } else {
                openAlertBox?.("error", response?.data?.detail.message);
            }
        } catch (error) {
            console.error('Error creating goods receipt:', error);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleClose = () => {
        setFormData({
            purchase_order_id: purchaseOrderId || '',
            warehouse_id: warehouseId || '',
            supplier_id: '',
            receipt_date: new Date().toISOString().split('T')[0],
            delivery_note_number: '',
            parent_receipt_id: '',
            notes: '',
            items: []
        });
        setErrors({});
        onClose();
    };

    const getPoDetailDisplay = (poDetailId) => {
        const detail = poDetails.find(d => d.po_detail_id === poDetailId);
        return detail ? `${detail.product_name} - ${detail.variant_name}` : '';
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-opacity-50 flex items-center justify-center z-50 p-4"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}>
            <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] flex flex-col">
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <h2 className="text-2xl font-bold text-gray-800">Tạo đơn nhập kho</h2>
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
                                    Đơn đặt hàng <span className="text-red-500">*</span>
                                </label>
                                <select
                                    value={formData.purchase_order_id}
                                    onChange={(e) => {
                                        setFormData({ ...formData, purchase_order_id: e.target.value });
                                        if (e.target.value) fetchPoDetails(e.target.value);
                                    }}
                                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.purchase_order_id ? 'border-red-500' : 'border-gray-300'}`}
                                >
                                    <option value="">Chọn đơn đặt hàng</option>
                                    {purchaseOrders.map(po => (
                                        <option key={po.id} value={po.id}>{po.po_number}</option>
                                    ))}
                                </select>
                                {errors.purchase_order_id && <p className="mt-1 text-sm text-red-500">{errors.purchase_order_id}</p>}
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Nhà cung cấp <span className="text-red-500">*</span>
                                </label>
                                <select
                                    value={formData.supplier_id}
                                    onChange={(e) => setFormData({ ...formData, supplier_id: e.target.value })}
                                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.supplier_id ? 'border-red-500' : 'border-gray-300'}`}
                                >
                                    <option value="">Chọn nhà cung cấp</option>
                                    {suppliers.map(supplier => (
                                        <option key={supplier.id} value={supplier.id}>{supplier.name}</option>
                                    ))}
                                </select>
                                {errors.supplier_id && <p className="mt-1 text-sm text-red-500">{errors.supplier_id}</p>}
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Kho nhận hàng <span className="text-red-500">*</span>
                                </label>
                                <input
                                    type="text"
                                    value={warehouses.find(w => w.id == formData.warehouse_id)?.name || ''}
                                    disabled
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 cursor-not-allowed"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Ngày nhập kho
                                </label>
                                <input
                                    type="date"
                                    value={formData.receipt_date}
                                    onChange={(e) => setFormData({ ...formData, receipt_date: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Số phiếu giao hàng
                                </label>
                                <input
                                    type="text"
                                    value={formData.delivery_note_number}
                                    onChange={(e) => setFormData({ ...formData, delivery_note_number: e.target.value })}
                                    placeholder="Nhập số phiếu giao hàng..."
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Chọn GR cha (nếu có)
                                </label>
                                <select
                                    value={formData.parent_receipt_id}
                                    onChange={(e) => setFormData({ ...formData, parent_receipt_id: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="">
                                        {parentReceipts.length === 0
                                            ? 'Không có GR cha khả dụng'
                                            : 'Chọn GR cha (tùy chọn)'}
                                    </option>
                                    {parentReceipts.map(gr => (
                                        <option key={gr.id} value={gr.id}>{gr.receipt_number}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Ghi chú chung
                            </label>
                            <textarea
                                value={formData.notes}
                                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                                rows={2}
                                placeholder="Ghi chú cho đơn nhập kho..."
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        <div>
                            <div className="flex items-center justify-between mb-4">
                                <label className="block text-sm font-medium text-gray-700">
                                    Chi tiết nhập kho <span className="text-red-500">*</span>
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

                            {errors.items && <p className="mb-3 text-sm text-red-500">{errors.items}</p>}

                            <div className="space-y-4">
                                {formData.items.map((item, index) => (
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
                                                    Chi tiết PO <span className="text-red-500">*</span>
                                                </label>
                                                <select
                                                    value={item.po_detail_id}
                                                    onChange={(e) => updateItem(index, 'po_detail_id', e.target.value)}
                                                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors[`item_${index}_po`] ? 'border-red-500' : 'border-gray-300'}`}
                                                >
                                                    <option value="">Chọn sản phẩm từ PO</option>
                                                    {poDetails
                                                        .filter(detail => {
                                                            if (parentReceiptDetails) {
                                                                const parentItem = parentReceiptDetails.items.find(
                                                                    pi => pi.product_variant_id === detail.product_variant_id
                                                                );
                                                                return parentItem && parentItem.ordered_quantity > 0;
                                                            }
                                                            return true;
                                                        })
                                                        .map(detail => {
                                                            let displayQty = detail.ordered_quantity;
                                                            if (parentReceiptDetails) {
                                                                const parentItem = parentReceiptDetails.items.find(
                                                                    pi => pi.product_variant_id === detail.product_variant_id
                                                                );
                                                                if (parentItem) {
                                                                    displayQty = parentItem.ordered_quantity;
                                                                }
                                                            }

                                                            return (
                                                                <option key={detail.po_detail_id} value={detail.po_detail_id}>
                                                                    {detail.product_name} - {detail.variant_name}
                                                                    {parentReceiptDetails
                                                                        ? ` (Còn lại từ GR cha: ${displayQty})`
                                                                        : ` (Đặt: ${displayQty})`
                                                                    }
                                                                </option>
                                                            );
                                                        })
                                                    }
                                                </select>
                                                {errors[`item_${index}_po`] && <p className="mt-1 text-sm text-red-500">{errors[`item_${index}_po`]}</p>}
                                            </div>

                                            {formData.parent_receipt_id && (
                                                <div className="md:col-span-2 p-3 bg-blue-50 border border-blue-200 rounded-md">
                                                    <p className="text-sm text-blue-800">
                                                        <strong>💡 Lưu ý:</strong> Bạn đang tạo GR con. Số lượng đặt được tính từ số lượng từ chối của GR cha.
                                                        Số lượng chấp nhận không được vượt quá số lượng từ chối của GR cha.
                                                    </p>
                                                </div>
                                            )}

                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Số lượng đặt
                                                </label>
                                                <input
                                                    type="number"
                                                    value={item.ordered_quantity}
                                                    disabled
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 cursor-not-allowed"
                                                />
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Số lượng nhận được <span className="text-red-500">*</span>
                                                </label>
                                                <input
                                                    type="number"
                                                    min="0"
                                                    value={item.received_quantity}
                                                    onChange={(e) => updateItem(index, 'received_quantity', e.target.value)}
                                                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors[`item_${index}_received`] ? 'border-red-500' : 'border-gray-300'}`}
                                                />
                                                {errors[`item_${index}_received`] && <p className="mt-1 text-sm text-red-500">{errors[`item_${index}_received`]}</p>}
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Số lượng chấp nhận <span className="text-red-500">*</span>
                                                </label>
                                                <input
                                                    type="number"
                                                    min="0"
                                                    value={item.accepted_quantity}
                                                    onChange={(e) => updateItem(index, 'accepted_quantity', e.target.value)}
                                                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors[`item_${index}_accepted`] ? 'border-red-500' : 'border-gray-300'}`}
                                                />
                                                {errors[`item_${index}_accepted`] && <p className="mt-1 text-sm text-red-500">{errors[`item_${index}_accepted`]}</p>}
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Số lượng từ chối <span className="text-red-500">*</span>
                                                </label>
                                                <input
                                                    type="number"
                                                    min="0"
                                                    value={item.rejected_quantity}
                                                    onChange={(e) => updateItem(index, 'rejected_quantity', e.target.value)}
                                                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors[`item_${index}_rejected`] ? 'border-red-500' : 'border-gray-300'}`}
                                                />
                                                {errors[`item_${index}_rejected`] && <p className="mt-1 text-sm text-red-500">{errors[`item_${index}_rejected`]}</p>}
                                            </div>

                                            {item.rejected_quantity > 0 && (
                                                <div className="md:col-span-2">
                                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                                        Lý do từ chối <span className="text-red-500">*</span>
                                                    </label>
                                                    <input
                                                        type="text"
                                                        value={item.rejection_reason}
                                                        onChange={(e) => updateItem(index, 'rejection_reason', e.target.value)}
                                                        placeholder="Nhập lý do từ chối..."
                                                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors[`item_${index}_reason`] ? 'border-red-500' : 'border-gray-300'}`}
                                                    />
                                                    {errors[`item_${index}_reason`] && <p className="mt-1 text-sm text-red-500">{errors[`item_${index}_reason`]}</p>}
                                                </div>
                                            )}

                                            {errors[`item_${index}_total`] && (
                                                <div className="md:col-span-2">
                                                    <p className="text-sm text-red-500">{errors[`item_${index}_total`]}</p>
                                                </div>
                                            )}

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
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isSubmitting ? 'Đang tạo...' : 'Tạo đơn nhập kho'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CreateGoodsReceiptModal;