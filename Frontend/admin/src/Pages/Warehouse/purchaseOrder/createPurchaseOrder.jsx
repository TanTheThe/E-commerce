import React, { useState, useEffect, useContext } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import { getDataApi, postDataApi } from '../../../utils/api';
import { MyContext } from '../../../App';

const CreatePurchaseOrderModal = ({ isOpen, onClose, onSuccess, warehouseId, openAlertBox }) => {
    const [formData, setFormData] = useState({
        supplier_id: '',
        warehouse_id: warehouseId || '',
        notes: '',
        items: []
    });

    const [suppliers, setSuppliers] = useState([]);
    const [warehouses, setWarehouses] = useState([]);
    const [categories, setCategories] = useState([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [errors, setErrors] = useState({});
    const [invalidProducts, setInvalidProducts] = useState(new Set());

    useEffect(() => {
        if (isOpen) {
            fetchSuppliers();
            fetchWarehouses();
            fetchCategories();
        }
    }, [isOpen]);

    useEffect(() => {
        if (warehouseId) {
            setFormData(prev => ({ ...prev, warehouse_id: warehouseId }));
        }
    }, [warehouseId]);

    const handleSupplierChange = async (supplierId) => {
        setFormData(prev => ({ ...prev, supplier_id: supplierId }));

        if (supplierId && formData.items.length > 0) {
            await refreshAllItemsProducts(supplierId);
        }
    };

    const refreshAllItemsProducts = async (supplierId) => {
        const invalidProductIds = new Set();

        const updatedItems = await Promise.all(
            formData.items.map(async (item, index) => {
                try {
                    let url = `/admin/product/all/select-box`;
                    if (item.category_id) {
                        url += `?category_id=${item.category_id}`;
                        if (supplierId) {
                            url += `&supplier_id=${supplierId}`;
                        }
                    } else if (supplierId) {
                        url += `?supplier_id=${supplierId}`;
                    }

                    const response = await getDataApi(url);
                    const newProducts = response.success ? response.data || [] : [];

                    const isProductValid = item.product_id &&
                        newProducts.some(p => p.id === item.product_id);

                    if (item.product_id && !isProductValid) {
                        invalidProductIds.add(index);
                    }

                    return {
                        ...item,
                        products: newProducts
                    };
                } catch (error) {
                    console.error('Error refreshing products:', error);
                    return item;
                }
            })
        );

        setFormData(prev => ({ ...prev, items: updatedItems }));
        setInvalidProducts(invalidProductIds);
    };

    const fetchSuppliers = async () => {
        try {
            const response = await getDataApi('/admin/suppliers?limit=1000');
            if (response.success) {
                setSuppliers(response.data.data || []);
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
            }
        } catch (error) {
            console.error('Error fetching warehouses:', error);
        }
    };

    const fetchCategories = async () => {
        try {
            const response = await getDataApi('/admin/categories/all/select-box');
            if (response.success) {
                setCategories(response.data || []);
            }
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    };

    const addItem = () => {
        const newItem = {
            category_id: '',
            product_id: '',
            product_variant_id: '',
            quantity: 1,
            unit_cost: 0,
            notes: '',
            products: [],
            variants: [],
            isLoadingProducts: false,
            isLoadingVariants: false
        };

        setFormData(prev => ({
            ...prev,
            items: [...prev.items, newItem]
        }));

        const newIndex = formData.items.length;
        fetchAllProducts(newIndex);
    };

    const removeItem = (index) => {
        setFormData(prev => ({
            ...prev,
            items: prev.items.filter((_, i) => i !== index)
        }));

        setInvalidProducts(prev => {
            const newSet = new Set(prev);
            newSet.delete(index);
            const adjustedSet = new Set();
            newSet.forEach(idx => {
                if (idx > index) adjustedSet.add(idx - 1);
                else if (idx < index) adjustedSet.add(idx);
            });
            return adjustedSet;
        });
    };

    const updateItem = (index, field, value) => {
        setFormData(prev => ({
            ...prev,
            items: prev.items.map((item, i) =>
                i === index ? { ...item, [field]: value } : item
            )
        }));
    };

    const handleCategoryChange = async (index, categoryId) => {
        updateItem(index, 'category_id', categoryId);
        updateItem(index, 'product_id', '');
        updateItem(index, 'product_variant_id', '');
        updateItem(index, 'variants', []);

        if (categoryId) {
            await fetchProductsByCategory(index, categoryId);
        } else {
            await fetchAllProducts(index);
        }
    };

    const isVariantDuplicate = (index, variantId) => {
        if (!variantId) return false;
        return formData.items.some((item, i) =>
            i !== index && item.product_variant_id == variantId
        );
    };

    const fetchProductsByCategory = async (index, categoryId) => {
        updateItem(index, 'isLoadingProducts', true);
        try {
            const supplierId = formData.supplier_id;
            let url = `/admin/product/all/select-box?category_id=${categoryId}`;

            if (supplierId) {
                url += `&supplier_id=${supplierId}`;
            }

            const response = await getDataApi(url);
            if (response.success) {
                updateItem(index, 'products', response.data || []);
            }
        } catch (error) {
            console.error('Error fetching products:', error);
        } finally {
            updateItem(index, 'isLoadingProducts', false);
        }
    };

    const fetchAllProducts = async (index) => {
        updateItem(index, 'isLoadingProducts', true);
        try {
            const supplierId = formData.supplier_id;
            let url = `/admin/product/all/select-box`;

            if (supplierId) {
                url += `?supplier_id=${supplierId}`;
            }

            const response = await getDataApi(url);
            if (response.success) {
                updateItem(index, 'products', response.data || []);
            }
        } catch (error) {
            console.error('Error fetching products:', error);
        } finally {
            updateItem(index, 'isLoadingProducts', false);
        }
    };

    const handleProductChange = async (index, productId) => {
        updateItem(index, 'product_id', productId);
        updateItem(index, 'product_variant_id', '');

        setInvalidProducts(prev => {
            const newSet = new Set(prev);
            newSet.delete(index);
            return newSet;
        });

        if (productId) {
            await fetchVariantsByProduct(index, productId);
        } else {
            updateItem(index, 'variants', []);
        }
    };

    const fetchVariantsByProduct = async (index, productId) => {
        updateItem(index, 'isLoadingVariants', true);
        try {
            const response = await getDataApi(`/admin/product/variants/all/select-box?product_id=${productId}`);
            if (response.success) {
                updateItem(index, 'variants', response.data || []);
                updateItem(index, 'product_variant_id', '');
                updateItem(index, 'unit_cost', 0);
            }
        } catch (error) {
            console.error('Error fetching variants:', error);
        } finally {
            updateItem(index, 'isLoadingVariants', false);
        }
    };

    const handleVariantChange = (index, variantId) => {
        if (isVariantDuplicate(index, variantId)) {
            openAlertBox?.("warning", "Biến thể này đã được chọn ở sản phẩm khác. Vui lòng quay lại chỉnh sửa hoặc chọn biến thể khác.");
            return;
        }

        updateItem(index, 'product_variant_id', variantId);

        const item = formData.items[index];
        const selectedVariant = item.variants.find(v => v.id == variantId);

        if (selectedVariant && selectedVariant.price) {
            updateItem(index, 'unit_cost', selectedVariant.price);
        } else {
            updateItem(index, 'unit_cost', 0);
        }
    };

    const validateForm = () => {
        const newErrors = {};

        if (!formData.supplier_id) {
            newErrors.supplier_id = 'Vui lòng chọn nhà cung cấp';
        }

        if (!formData.warehouse_id) {
            newErrors.warehouse_id = 'Vui lòng chọn kho nhận hàng';
        }

        if (formData.items.length === 0) {
            newErrors.items = 'Vui lòng thêm ít nhất 1 sản phẩm';
        } else {
            if (invalidProducts.size > 0) {
                newErrors.invalid_products = 'Có sản phẩm không thuộc nhà cung cấp đã chọn. Vui lòng chọn lại.';
            }

            formData.items.forEach((item, index) => {
                if (!item.product_variant_id) {
                    newErrors[`item_${index}_variant`] = 'Vui lòng chọn biến thể sản phẩm';
                }
                if (item.quantity <= 0) {
                    newErrors[`item_${index}_quantity`] = 'Số lượng phải lớn hơn 0';
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
                supplier_id: formData.supplier_id,
                warehouse_id: formData.warehouse_id,
                notes: formData.notes || null,
                items: formData.items.map(item => ({
                    product_variant_id: item.product_variant_id,
                    quantity: parseInt(item.quantity),
                    notes: item.notes || null
                }))
            };

            const response = await postDataApi('/admin/purchase-orders', submitData);

            if (response.success) {
                openAlertBox?.("success", response.message || 'Tạo đơn nhập hàng thành công');
                onSuccess?.();
                handleClose();
            } else {
                openAlertBox?.("error", response?.data?.detail.message || "Có lỗi xảy ra khi tạo đơn");
            }
        } catch (error) {
            console.error('Error creating purchase order:', error);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleClose = () => {
        setFormData({
            supplier_id: '',
            warehouse_id: warehouseId || '',
            notes: '',
            items: []
        });
        setErrors({});
        onClose();
    };

    const calculateTotal = () => {
        return formData.items.reduce((sum, item) =>
            sum + (parseInt(item.quantity) || 0) * (parseInt(item.unit_cost) || 0), 0
        );
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(amount);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-opacity-50 flex items-center justify-center z-50 p-4"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}>
            <div className="bg-white rounded-lg shadow-xl w-full max-w-5xl max-h-[90vh] flex flex-col">
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <h2 className="text-2xl font-bold text-gray-800">Tạo đơn đặt hàng</h2>
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
                                    Nhà cung cấp <span className="text-red-500">*</span>
                                </label>
                                <select
                                    value={formData.supplier_id}
                                    onChange={(e) => handleSupplierChange(e.target.value)}
                                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.supplier_id ? 'border-red-500' : 'border-gray-300'}`}
                                >
                                    <option value="">Chọn nhà cung cấp</option>
                                    {suppliers.map(supplier => (
                                        <option key={supplier.id} value={supplier.id}>
                                            {supplier.name}
                                        </option>
                                    ))}
                                </select>
                                {errors.supplier_id && (
                                    <p className="mt-1 text-sm text-red-500">{errors.supplier_id}</p>
                                )}
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
                                {errors.warehouse_id && (
                                    <p className="mt-1 text-sm text-red-500">{errors.warehouse_id}</p>
                                )}
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Ghi chú chung
                            </label>
                            <textarea
                                value={formData.notes}
                                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                                rows={3}
                                placeholder="Ghi chú cho đơn đặt hàng..."
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        <div>
                            <div className="flex items-center justify-between mb-4">
                                <label className="block text-sm font-medium text-gray-700">
                                    Danh sách sản phẩm <span className="text-red-500">*</span>
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

                            {errors.items && (
                                <p className="mb-3 text-sm text-red-500">{errors.items}</p>
                            )}

                            {errors.invalid_products && (
                                <div className="mb-3 p-3 bg-red-50 border border-red-300 rounded-md flex items-start gap-2">
                                    <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                                    <p className="text-sm text-red-800">{errors.invalid_products}</p>
                                </div>
                            )}

                            <div className="space-y-4">
                                {formData.items.map((item, index) => (
                                    <div key={index} className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                                        {invalidProducts.has(index) && (
                                            <div className="mb-3 p-3 bg-yellow-50 border border-yellow-300 rounded-md flex items-start gap-2">
                                                <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                                                <div className="text-sm text-yellow-800">
                                                    <p className="font-medium">Sản phẩm không thuộc nhà cung cấp đã chọn</p>
                                                    <p className="text-xs mt-1">Vui lòng chọn lại sản phẩm phù hợp với nhà cung cấp hiện tại</p>
                                                </div>
                                            </div>
                                        )}
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

                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Danh mục (tùy chọn)
                                                </label>
                                                <select
                                                    value={item.category_id}
                                                    onChange={(e) => handleCategoryChange(index, e.target.value)}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                >
                                                    <option value="">Tất cả danh mục</option>
                                                    {categories.map(cat => (
                                                        <option key={cat.id} value={cat.id}>
                                                            {cat.name}
                                                        </option>
                                                    ))}
                                                </select>
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Sản phẩm <span className="text-red-500">*</span>
                                                </label>
                                                <select
                                                    value={item.product_id}
                                                    onChange={(e) => handleProductChange(index, e.target.value)}
                                                    disabled={item.isLoadingProducts}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                                                >
                                                    <option value="">
                                                        {item.isLoadingProducts ? 'Đang tải...' : 'Chọn sản phẩm'}
                                                    </option>
                                                    {item.products?.map(product => (
                                                        <option key={product.id} value={product.id}>
                                                            {product.name}
                                                        </option>
                                                    ))}
                                                </select>
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Biến thể <span className="text-red-500">*</span>
                                                </label>
                                                <select
                                                    value={item.product_variant_id}
                                                    onChange={(e) => handleVariantChange(index, e.target.value)}
                                                    disabled={!item.product_id || item.isLoadingVariants}
                                                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 ${errors[`item_${index}_variant`] ? 'border-red-500' : 'border-gray-300'
                                                        }`}
                                                >
                                                    <option value="">
                                                        {item.isLoadingVariants ? 'Đang tải...' : 'Chọn biến thể'}
                                                    </option>
                                                    {item.variants?.map(variant => {
                                                        const isDuplicate = isVariantDuplicate(index, variant.id);
                                                        return (
                                                            <option
                                                                key={variant.id}
                                                                value={variant.id}
                                                                disabled={isDuplicate}
                                                                style={isDuplicate ? { color: '#999', fontStyle: 'italic' } : {}}
                                                            >
                                                                {variant.name} {isDuplicate ? '(Đã chọn)' : ''}
                                                            </option>
                                                        );
                                                    })}
                                                </select>
                                                {errors[`item_${index}_variant`] && (
                                                    <p className="mt-1 text-sm text-red-500">{errors[`item_${index}_variant`]}</p>
                                                )}
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Số lượng <span className="text-red-500">*</span>
                                                </label>
                                                <input
                                                    type="number"
                                                    min="1"
                                                    value={item.quantity}
                                                    onChange={(e) => updateItem(index, 'quantity', e.target.value)}
                                                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors[`item_${index}_quantity`] ? 'border-red-500' : 'border-gray-300'
                                                        }`}
                                                />
                                                {errors[`item_${index}_quantity`] && (
                                                    <p className="mt-1 text-sm text-red-500">{errors[`item_${index}_quantity`]}</p>
                                                )}
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Đơn giá (VND) <span className="text-red-500">*</span>
                                                </label>
                                                <input
                                                    type="number"
                                                    min="0"
                                                    value={item.unit_cost}
                                                    disabled
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 cursor-not-allowed"
                                                />
                                                {errors[`item_${index}_cost`] && (
                                                    <p className="mt-1 text-sm text-red-500">{errors[`item_${index}_cost`]}</p>
                                                )}
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Thành tiền
                                                </label>
                                                <div className="w-full px-3 py-2 border border-gray-200 rounded-md bg-gray-100 text-gray-700 font-semibold">
                                                    {formatCurrency((item.quantity || 0) * (item.unit_cost || 0))}
                                                </div>
                                            </div>

                                            <div className="md:col-span-3">
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

                            {formData.items.length > 0 && (
                                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                    <div className="flex justify-between items-center">
                                        <span className="text-base font-medium text-gray-700">Tổng giá trị đơn hàng:</span>
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
                        {isSubmitting ? 'Đang tạo...' : 'Tạo đơn đặt hàng'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CreatePurchaseOrderModal;