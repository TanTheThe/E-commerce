import { useContext, useEffect, useState } from "react";
import { MyContext } from "../../../App";
import { getDataApi, postDataApi, putDataApi } from "../../../utils/api";
import { Upload, X } from "lucide-react";

const UpdatePurchaseOrderAfterNegotiationModal = ({ isOpen, onClose, onSuccess, poId, openAlertBox }) => {
    const [formData, setFormData] = useState({
        expected_delivery_date: '',
        discount_amount: 0,
        shipping_cost: 0,
        supplier_invoice_urls: [],
        notes: '',
        items: []
    });
    const [suppliers, setSuppliers] = useState([]);
    const [warehouses, setWarehouses] = useState([]);
    const [categories, setCategories] = useState([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [errors, setErrors] = useState({});
    const [uploadingImages, setUploadingImages] = useState(false);
    const [selectedImage, setSelectedImage] = useState(null);
    const context = useContext(MyContext);

    useEffect(() => {
        if (isOpen && poId) {
            fetchSuppliers();
            fetchWarehouses();
            fetchCategories();
            fetchPurchaseOrder();
        }
    }, [isOpen, poId]);

    const fetchPurchaseOrder = async () => {
        setIsLoading(true);
        try {
            const response = await getDataApi(`/admin/purchase-orders/${poId}`);
            if (response.success) {
                const order = response.data;

                let formattedDate = '';
                if (order.expected_delivery_date) {
                    formattedDate = order.expected_delivery_date.split(' ')[0];
                }

                setFormData({
                    supplier_id: order.supplier_id || '',
                    warehouse_id: order.warehouse_id || '',
                    expected_delivery_date: formattedDate,
                    discount_amount: order.discount_amount || 0,
                    shipping_cost: order.shipping_cost || 0,
                    supplier_invoice_urls: order.supplier_invoice_urls || [],
                    notes: order.notes || '',
                    items: []
                });

                if (order.items && order.items.length > 0) {
                    const itemsWithData = await Promise.all(
                        order.items.map(async (item, index) => {
                            const newItem = {
                                id: item.id,
                                category_id: item.product?.category_id || '',
                                product_id: item.product_id || '',
                                product_variant_id: item.product_variant_id || '',
                                quantity: item.quantity || 1,
                                unit_cost: item.unit_cost || 0,
                                notes: item.notes || '',
                                products: [],
                                variants: [],
                                isLoadingProducts: false,
                                isLoadingVariants: false
                            };

                            if (newItem.category_id) {
                                await fetchProductsByCategoryForItem(index, newItem.category_id, newItem);
                            } else {
                                await fetchAllProductsForItem(index, newItem);
                            }

                            if (newItem.product_id) {
                                await fetchVariantsByProductForItem(index, newItem.product_id, newItem);
                            }

                            return newItem;
                        })
                    );

                    setFormData(prev => ({
                        ...prev,
                        items: itemsWithData
                    }));
                }
            }
        } catch (error) {
            console.error('Error fetching purchase order:', error);
            openAlertBox?.("error", "Có lỗi xảy ra khi tải thông tin đơn hàng");
        } finally {
            setIsLoading(false);
        }
    };

    const fetchProductsByCategoryForItem = async (index, categoryId, item) => {
        try {
            const response = await getDataApi(`/admin/product/all/select-box?category_id=${categoryId}`);
            if (response.success) {
                item.products = response.data || [];
            }
        } catch (error) {
            console.error('Error fetching products:', error);
        }
    };

    const fetchAllProductsForItem = async (index, item) => {
        try {
            const response = await getDataApi('/admin/product/all/select-box');
            if (response.success) {
                item.products = response.data || [];
            }
        } catch (error) {
            console.error('Error fetching products:', error);
        }
    };

    const fetchVariantsByProductForItem = async (index, productId, item) => {
        try {
            const response = await getDataApi(`/admin/product/variants/all/select-box?product_id=${productId}`);
            if (response.success) {
                item.variants = response.data || [];
            }
        } catch (error) {
            console.error('Error fetching variants:', error);
        }
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

    const updateItem = (index, field, value) => {
        setFormData(prev => ({
            ...prev,
            items: prev.items.map((item, i) =>
                i === index ? { ...item, [field]: value } : item
            )
        }));
    };

    const handleImageUpload = (e) => {
        const files = Array.from(e.target.files);
        if (files.length === 0) return;

        setUploadingImages(true);

        const readPromises = files.map((file) => {
            return new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = () => {
                    resolve(reader.result);
                };
                reader.readAsDataURL(file);
            });
        });

        Promise.all(readPromises)
            .then((base64Urls) => {
                setFormData(prev => ({
                    ...prev,
                    supplier_invoice_urls: [...prev.supplier_invoice_urls, ...base64Urls]
                }));
                openAlertBox?.("success", `Đã thêm ${base64Urls.length} ảnh`);
            })
            .catch((error) => {
                console.error('Error reading images:', error);
                openAlertBox?.("error", "Có lỗi xảy ra khi đọc ảnh");
            })
            .finally(() => {
                setUploadingImages(false);
            });
    };

    const removeImage = (index) => {
        setFormData(prev => ({
            ...prev,
            supplier_invoice_urls: prev.supplier_invoice_urls.filter((_, i) => i !== index)
        }));
    };

    const ImagePreviewModal = ({ imageUrl, onClose }) => {
        if (!imageUrl) return null;

        return (
            <div
                className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-[60]"
                style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}
                onClick={onClose}
            >
                <div className="relative max-w-7xl max-h-[90vh] p-4">
                    <button
                        onClick={onClose}
                        className="absolute top-2 right-2 p-2 bg-white rounded-full text-gray-800 hover:bg-gray-200 transition-colors z-10"
                    >
                        <X className="w-6 h-6" />
                    </button>
                    <img
                        src={imageUrl}
                        alt="Preview"
                        className="max-w-full max-h-[85vh] object-contain rounded-lg"
                        onClick={(e) => e.stopPropagation()}
                    />
                </div>
            </div>
        );
    };

    const validateForm = () => {
        const newErrors = {};

        if (String(formData.expected_delivery_date) == 'None') {
            newErrors.expected_delivery_date = 'Vui lòng chọn ngày giao hàng dự kiến';
        }

        if (formData.supplier_invoice_urls.length === 0) {
            newErrors.supplier_invoice_urls = 'Vui lòng tải lên ít nhất 1 ảnh hóa đơn từ nhà cung cấp';
        }

        if (formData.items.length === 0) {
            newErrors.items = 'Vui lòng có ít nhất 1 sản phẩm';
        } else {
            formData.items.forEach((item, index) => {
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
                expected_delivery_date: formData.expected_delivery_date,
                discount_amount: parseInt(formData.discount_amount) || null,
                shipping_cost: parseInt(formData.shipping_cost) || null,
                supplier_invoice_urls: formData.supplier_invoice_urls,
                notes: formData.notes || null,
                items: formData.items.map(item => ({
                    product_variant_id: item.product_variant_id,
                    quantity: parseInt(item.quantity),
                    notes: item.notes || null
                }))
            };

            const response = await putDataApi(`/admin/purchase-orders/${poId}/after-negotiation`, submitData);

            console.log(response);

            if (response.success) {
                openAlertBox?.("success", response.message || 'Cập nhật đơn hàng sau thương lượng thành công');
                onSuccess?.();
                handleClose();
            } else {
                openAlertBox?.("error", response?.data?.detail?.message || "Có lỗi xảy ra khi cập nhật đơn");
            }
        } catch (error) {
            console.error('Error updating purchase order after negotiation:', error);
            openAlertBox?.("error", "Có lỗi xảy ra khi cập nhật đơn");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleClose = () => {
        setFormData({
            expected_delivery_date: '',
            discount_amount: 0,
            shipping_cost: 0,
            supplier_invoice_urls: [],
            notes: '',
            items: []
        });
        setErrors({});
        onClose();
    };

    const calculateSubtotal = () => {
        return formData.items.reduce((sum, item) =>
            sum + (parseInt(item.quantity) || 0) * (parseInt(item.unit_cost) || 0), 0
        );
    };

    const calculateTotal = () => {
        const subtotal = calculateSubtotal();
        const discount = parseInt(formData.discount_amount) || 0;
        const shipping = parseInt(formData.shipping_cost) || 0;
        return subtotal - discount + shipping;
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(amount);
    };

    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 bg-opacity-50 flex items-center justify-center z-50 p-4"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}
        >
            <div className="bg-white rounded-lg shadow-xl w-full max-w-5xl max-h-[90vh] flex flex-col">
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <h2 className="text-2xl font-bold text-gray-800">Cập nhật sau thương lượng</h2>
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
                                            Nhà cung cấp
                                        </label>
                                        <input
                                            type="text"
                                            value={suppliers.find(s => s.id == formData.supplier_id)?.name || ''}
                                            disabled
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 cursor-not-allowed"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Kho nhận hàng
                                        </label>
                                        <input
                                            type="text"
                                            value={warehouses.find(w => w.id == formData.warehouse_id)?.name || ''}
                                            disabled
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 cursor-not-allowed"
                                        />
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Ngày giao hàng dự kiến <span className="text-red-500">*</span>
                                        </label>
                                        <input
                                            type="date"
                                            value={formData.expected_delivery_date}
                                            onChange={(e) => {
                                                setFormData({ ...formData, expected_delivery_date: e.target.value });
                                                if (errors.expected_delivery_date) {
                                                    setErrors({ ...errors, expected_delivery_date: '' });
                                                }
                                            }}
                                            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.expected_delivery_date ? 'border-red-500' : 'border-gray-300'
                                                }`}
                                        />
                                        {errors.expected_delivery_date && (
                                            <p className="mt-1 text-sm text-red-500">{errors.expected_delivery_date}</p>
                                        )}
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Giảm giá (VND)
                                        </label>
                                        <input
                                            type="number"
                                            min="0"
                                            value={formData.discount_amount}
                                            onChange={(e) => setFormData({ ...formData, discount_amount: e.target.value })}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Phí vận chuyển (VND)
                                        </label>
                                        <input
                                            type="number"
                                            min="0"
                                            value={formData.shipping_cost}
                                            onChange={(e) => setFormData({ ...formData, shipping_cost: e.target.value })}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Hóa đơn từ nhà cung cấp <span className="text-red-500">*</span>
                                    </label>
                                    <div className="space-y-3">
                                        <div className="flex items-center gap-3">
                                            <label className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors cursor-pointer">
                                                <Upload className="w-4 h-4" />
                                                <span>{uploadingImages ? 'Đang tải lên...' : 'Tải ảnh lên'}</span>
                                                <input
                                                    type="file"
                                                    multiple
                                                    accept="image/*"
                                                    onChange={handleImageUpload}
                                                    disabled={uploadingImages}
                                                    className="hidden"
                                                />
                                            </label>
                                            {formData.supplier_invoice_urls.length > 0 && (
                                                <span className="text-sm text-gray-600">
                                                    {formData.supplier_invoice_urls.length} ảnh đã tải lên
                                                </span>
                                            )}
                                        </div>

                                        {errors.supplier_invoice_urls && (
                                            <p className="text-sm text-red-500">{errors.supplier_invoice_urls}</p>
                                        )}

                                        {formData.supplier_invoice_urls.length > 0 && (
                                            <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
                                                {formData.supplier_invoice_urls.map((url, index) => (
                                                    <div key={index} className="relative group">
                                                        <img
                                                            src={url}
                                                            alt={`Invoice ${index + 1}`}
                                                            className="w-full h-24 object-cover rounded-md border border-gray-200 cursor-pointer hover:opacity-80 transition-opacity"
                                                            onClick={() => setSelectedImage(url)}
                                                        />
                                                        <button
                                                            type="button"
                                                            onClick={() => removeImage(index)}
                                                            className="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                                                        >
                                                            <X className="w-3 h-3" />
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Ghi chú đơn hàng
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
                                    <label className="block text-sm font-medium text-gray-700 mb-4">
                                        Danh sách sản phẩm <span className="text-red-500">*</span>
                                    </label>

                                    {errors.items && (
                                        <p className="mb-3 text-sm text-red-500">{errors.items}</p>
                                    )}

                                    <div className="space-y-4">
                                        {formData.items.map((item, index) => (
                                            <div key={index} className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                                                <div className="mb-3">
                                                    <span className="text-sm font-medium text-gray-700">
                                                        Sản phẩm #{index + 1}
                                                    </span>
                                                </div>

                                                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                                            Danh mục
                                                        </label>
                                                        <input
                                                            type="text"
                                                            value={categories.find(c => c.id == item.category_id)?.name || ''}
                                                            disabled
                                                            className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 cursor-not-allowed"
                                                        />
                                                    </div>

                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                                            Sản phẩm
                                                        </label>
                                                        <input
                                                            type="text"
                                                            value={item.products.find(p => p.id == item.product_id)?.name || ''}
                                                            disabled
                                                            className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 cursor-not-allowed"
                                                        />
                                                    </div>

                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                                            Biến thể
                                                        </label>
                                                        <input
                                                            type="text"
                                                            value={item.variants.find(v => v.id == item.product_variant_id)?.name || ''}
                                                            disabled
                                                            className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 cursor-not-allowed"
                                                        />
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
                                                            Đơn giá (VND)
                                                        </label>
                                                        <input
                                                            type="number"
                                                            value={item.unit_cost}
                                                            disabled
                                                            className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 cursor-not-allowed"
                                                        />
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
                                        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg space-y-2">
                                            <div className="flex justify-between items-center text-sm">
                                                <span className="text-gray-700">Tạm tính:</span>
                                                <span className="font-medium text-gray-900">
                                                    {formatCurrency(calculateSubtotal())}
                                                </span>
                                            </div>
                                            <div className="flex justify-between items-center text-sm">
                                                <span className="text-gray-700">Giảm giá:</span>
                                                <span className="font-medium text-red-600">
                                                    - {formatCurrency(parseInt(formData.discount_amount) || 0)}
                                                </span>
                                            </div>
                                            <div className="flex justify-between items-center text-sm">
                                                <span className="text-gray-700">Phí vận chuyển:</span>
                                                <span className="font-medium text-gray-900">
                                                    + {formatCurrency(parseInt(formData.shipping_cost) || 0)}
                                                </span>
                                            </div>
                                            <div className="pt-2 border-t border-blue-300">
                                                <div className="flex justify-between items-center">
                                                    <span className="text-base font-medium text-gray-700">Tổng giá trị đơn hàng:</span>
                                                    <span className="text-xl font-bold text-blue-600">
                                                        {formatCurrency(calculateTotal())}
                                                    </span>
                                                </div>
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
                                className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isSubmitting ? 'Đang cập nhật...' : 'Cập nhật sau thương lượng'}
                            </button>
                        </div>
                    </>
                )}
            </div>

            {selectedImage && (
                <ImagePreviewModal
                    imageUrl={selectedImage}
                    onClose={() => setSelectedImage(null)}
                />
            )}

        </div>
    )
}

export default UpdatePurchaseOrderAfterNegotiationModal;