import { useContext, useEffect, useState } from "react";
import { MyContext } from "../../App";
import { fetchWithAutoRefresh, getDataApi, putDataApi } from "../../utils/api";
import { Button, Checkbox, ListItemText, MenuItem, Select } from "@mui/material";
import { IoMdClose } from "react-icons/io";
import { LazyLoadImage } from "react-lazy-load-image-component";
import { FaCloudUploadAlt, FaPlus } from "react-icons/fa";
import ColorPicker from "../../Components/ColorPicker";
import { v4 as uuidv4 } from 'uuid';
import HierarchicalCategorySelect from "./categoriesSelect";


const EditProduct = ({ productId, onClose, onProductUpdated }) => {
    const [variants, setVariants] = useState([]);
    const [images, setImages] = useState([]);
    const [formData, setFormData] = useState({ name: '', description: '' });
    const [loading, setLoading] = useState(false);
    const [categories, setCategories] = useState([]);
    const [selectedCategories, setSelectedCategories] = useState([]);
    const [colors, setColors] = useState([]);
    const [initialLoading, setInitialLoading] = useState(true);
    const [deletedVariantIds, setDeletedVariantIds] = useState([]);

    const { isOpenFullScreenPanel, setIsOpenFullScreenPanel } = useContext(MyContext);
    const context = useContext(MyContext);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const queryParams = new URLSearchParams({
                    skip: "0",
                    limit: "1000",
                });

                const res = await getDataApi(`/admin/categories/all?${queryParams.toString()}`);
                if (res.success === true) {
                    setCategories(res.data.data || []);
                } else {
                    console.error("Failed to fetch categories:", res.message);
                    setCategories([]);
                    context.openAlertBox("error", "Không lấy được danh sách danh mục");
                }
            } catch (error) {
                console.error("Error fetching categories:", error);
                setCategories([]);
                context.openAlertBox("error", "Lỗi khi lấy danh mục");
            }
        };
        fetchCategories();
    }, []);

    useEffect(() => {
        const fetchColors = async () => {
            try {
                const queryParams = new URLSearchParams({
                    skip: "0",
                    limit: "1000",
                });

                const res = await getDataApi(`/admin/color?${queryParams.toString()}`);
                console.log(res);
                if (res.success === true) {
                    setColors(res.data.data || []);
                } else {
                    console.error("Failed to fetch colors:", res.message);
                    setColors([]);
                }
            } catch (error) {
                console.error("Error fetching colors:", error);
                setColors([]);
            }
        };
        fetchColors();
    }, []);

    useEffect(() => {
        const fetchProductDetail = async () => {
            if (!productId) return;

            setInitialLoading(true);
            try {
                const response = await getDataApi(`/admin/product/${productId}`);

                if (response.success === true) {
                    const product = response.data;

                    setFormData({
                        name: product.name || '',
                        description: product.description || ''
                    });

                    setSelectedCategories(product.categories?.map(cat => String(cat.id)) || []);

                    const productImages = product.images?.map((img, index) => ({
                        id: Date.now() + index,
                        url: img,
                        name: `image_${index}.jpg`,
                        base64: img,
                        isExisting: true
                    })) || [];
                    setImages(productImages);

                    const productVariants = product.product_variant?.map(variant => ({
                        id: variant.id,
                        size: variant.size || '',
                        quantity: variant.quantity || '',
                        price: variant.price || '',
                        sku: variant.sku || '',
                        color_id: variant.color_id || null,
                        color_name: variant.color_name || null,
                        color_code: variant.color_code || null,
                        isExisting: true
                    })) || [];
                    setVariants(productVariants);

                } else {
                    context.openAlertBox("error", "Không thể tải thông tin sản phẩm");
                }
            } catch (err) {
                console.error("Error fetching product detail:", err);
                context.openAlertBox("error", "Lỗi khi tải thông tin sản phẩm");
            } finally {
                setInitialLoading(false);
            }
        };

        fetchProductDetail();
    }, [productId]);

    const convertToBase64 = (file) => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    };

    const handleImageUpload = async (e) => {
        const files = Array.from(e.target.files);
        const newImages = await Promise.all(files.map(async (file) => {
            const base64 = await convertToBase64(file);
            return {
                id: Date.now() + Math.random(),
                url: URL.createObjectURL(file),
                name: file.name,
                base64,
                isExisting: false
            };
        }));
        setImages(prev => [...prev, ...newImages]);
    };

    const removeImage = (id) => {
        const removed = images.find(img => img.id === id);
        if (removed && !removed.isExisting) {
            URL.revokeObjectURL(removed.url);
        }
        setImages(prev => prev.filter(img => img.id !== id));
    };

    const handleAddVariant = () => {
        const tempId = `new_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        setVariants(prev => [
            ...prev,
            {
                id: tempId,
                size: '',
                quantity: '',
                price: '',
                sku: '',
                color_id: null,
                color_name: null,
                color_code: null,
                isExisting: false
            }
        ]);
    };

    const handleRemoveVariant = (variantId) => {
        const variantToRemove = variants.find(variant => variant.id === variantId);

        setVariants(prev => prev.filter(variant => variant.id !== variantId));

        if (variantToRemove && variantToRemove.isExisting) {
            setDeletedVariantIds(prev => {
                const newDeleted = [...prev, variantId];
                return newDeleted;
            });
        } else {
            console.log('NOT adding to deletedVariantIds - variant is new or not found');
        }
    };

    const handleVariantChange = (id, field, value) => {
        setVariants(prev =>
            prev.map(v => {
                if (v.id !== id) return v;

                if (field === 'color_id') {
                    return {
                        ...v,
                        color_id: value || null,
                        color_name: null,
                        color_code: null
                    };
                }

                if (field === 'color_override') {
                    return {
                        ...v,
                        color_id: null,
                        color_name: value?.name || null,
                        color_code: value?.code || null
                    };
                }

                return { ...v, [field]: value };
            })
        );
    };

    const handleFormDataChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleCategorySelectionChange = (selectedIds) => {
        setSelectedCategories(selectedIds);
    };

    const validateForm = () => {
        if (!formData.name.trim()) {
            context.openAlertBox("error", 'Tên sản phẩm không được để trống');
            return false;
        }

        if (selectedCategories.length === 0) {
            context.openAlertBox("error", 'Vui lòng chọn ít nhất một danh mục cho sản phẩm');
            return false;
        }

        if (images.length === 0) {
            context.openAlertBox("error", 'Vui lòng thêm ít nhất một hình ảnh');
            return false;
        }

        if (variants.length === 0) {
            context.openAlertBox("error", 'Vui lòng thêm ít nhất một variant');
            return false;
        }

        for (let variant of variants) {
            if (!variant.sku.trim()) {
                context.openAlertBox("error", 'SKU không được để trống');
                return false;
            }
            if (!variant.price || variant.price <= 0) {
                context.openAlertBox("error", 'Giá phải lớn hơn 0');
                return false;
            }
            if (!variant.quantity || variant.quantity < 0) {
                context.openAlertBox("error", 'Số lượng không được âm');
                return false;
            }
        }
        return true;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validateForm()) return;

        setLoading(true);
        try {
            const isUUID = (val) => typeof val === 'string' && /^[0-9a-fA-F\-]{36}$/.test(val);

            const validCategoryIds = selectedCategories.filter(id => isUUID(id));

            if (validCategoryIds.length === 0) {
                context.openAlertBox("error", 'Vui lòng chọn ít nhất một danh mục hợp lệ');
                return;
            }

            const submitData = {
                name: formData.name.trim(),
                description: formData.description?.trim() || null,
                images: images.map(img => img.base64),
                categories_id: validCategoryIds,
                product_variant: variants.map(variant => {
                    if (variant.color_id) {
                        return {
                            id: variant.isExisting ? variant.id : null,
                            size: variant.size || null,
                            color_id: variant.color_id,
                            price: parseInt(variant.price),
                            quantity: parseInt(variant.quantity),
                            sku: variant.sku.trim()
                        };
                    } else {
                        return {
                            id: variant.isExisting ? variant.id : null,
                            size: variant.size || null,
                            color_name: variant.color_name,
                            color_code: variant.color_code,
                            price: parseInt(variant.price),
                            quantity: parseInt(variant.quantity),
                            sku: variant.sku.trim()
                        };
                    }
                }),
                deleted_variant_ids: deletedVariantIds
            };

            const result = await putDataApi(`/admin/product/${productId}`, submitData);

            if (!result.success) {
                context.openAlertBox("error", result?.data?.detail?.message || result?.message || 'Có lỗi xảy ra khi cập nhật sản phẩm');
                return;
            }

            context.openAlertBox("success", result?.message || 'Cập nhật sản phẩm thành công');

            if (isOpenFullScreenPanel?.onUpdated && typeof isOpenFullScreenPanel.onUpdated === 'function') {
                isOpenFullScreenPanel.onUpdated();
            }

            onClose && onClose();
        } catch (err) {
            console.error('Submit error:', err);
            context.openAlertBox("error", 'Có lỗi xảy ra khi cập nhật sản phẩm');
        } finally {
            setLoading(false);
        }
    };

    if (initialLoading) {
        return (
            <section className="p-5 bg-gray-50">
                <div className="flex justify-center items-center h-64">
                    <div className="text-lg">Đang tải thông tin sản phẩm...</div>
                </div>
            </section>
        );
    }

    return (
        <section className="p-5 bg-gray-50">
            <form className="form py-3 p-8" onSubmit={handleSubmit}>
                <div className="flex-1 overflow-y-auto pr-4">
                    <div className="mb-3">
                        <h3 className="text-[14px] font-[500] mb-1">Tên sản phẩm</h3>
                        <input
                            type="text"
                            value={formData.name}
                            onChange={(e) => handleFormDataChange('name', e.target.value)}
                            className="w-full h-[40px] border border-[rgba(0,0,0,0.2)] rounded-sm p-3 bg-white text-sm"
                        />
                    </div>

                    <div className="mb-3">
                        <h3 className="text-[14px] font-[500] mb-1">Mô tả sản phẩm</h3>
                        <textarea
                            value={formData.description}
                            onChange={(e) => handleFormDataChange('description', e.target.value)}
                            className="w-full h-[100px] border border-[rgba(0,0,0,0.2)] rounded-sm p-3 bg-white text-sm"
                        />
                    </div>

                    <div className="mb-5">
                        <h3 className="text-[14px] font-[500] mb-1">Danh mục sản phẩm</h3>
                        <HierarchicalCategorySelect
                            categories={categories}
                            selectedCategoryIds={selectedCategories}
                            onSelectionChange={handleCategorySelectionChange}
                            label=""
                            placeholder="Chọn danh mục sản phẩm"
                        />
                    </div>

                    <div className="mb-4">
                        <h3 className="font-bold text-[16px] mb-3">Tải lên ảnh</h3>
                        <div className="grid grid-cols-7 gap-4">
                            {images.map((img) => (
                                <div key={img.id} className="relative">
                                    <span
                                        className="absolute w-[20px] h-[20px] rounded-full bg-red-700 -top-[10px] -right-[10px] flex items-center justify-center cursor-pointer z-10"
                                        onClick={() => removeImage(img.id)}
                                    >
                                        <IoMdClose className="text-white text-[14px]" />
                                    </span>
                                    <div className="border border-dashed h-[150px] bg-gray-100 rounded-md overflow-hidden">
                                        <LazyLoadImage
                                            src={img.url}
                                            alt="image"
                                            className="w-full h-full object-cover"
                                            effect="blur"
                                        />
                                    </div>
                                </div>
                            ))}
                            <div className="border-dashed border h-[150px] flex items-center justify-center bg-gray-100 rounded relative">
                                <input
                                    type="file"
                                    accept="image/*"
                                    multiple
                                    onChange={handleImageUpload}
                                    className="absolute inset-0 opacity-0 z-10 cursor-pointer"
                                    id="imageUploadEdit"
                                />
                                <label htmlFor="imageUploadEdit" className="text-center text-gray-500">
                                    <FaPlus className="mx-auto mb-2 text-xl" />
                                    Thêm ảnh
                                </label>
                            </div>
                        </div>
                    </div>

                    {variants.map((variant, index) => (
                        <div key={variant.id} className="border border-gray-300 p-4 mb-4 rounded-md bg-white relative">
                            <button
                                type="button"
                                onClick={() => handleRemoveVariant(variant.id)}
                                className="absolute top-2 right-2 text-red-600 cursor-pointer"
                            >
                                <IoMdClose size={20} />
                            </button>

                            <div className="grid grid-cols-6 gap-4 mb-3">
                                <div className="col-span-1">
                                    <h3 className="text-sm font-medium mb-1">Kích cỡ</h3>
                                    <Select
                                        size="small"
                                        className="w-full"
                                        value={variant.size}
                                        onChange={(e) =>
                                            handleVariantChange(variant.id, 'size', e.target.value)
                                        }
                                    >
                                        <MenuItem value="">None</MenuItem>
                                        <MenuItem value="S">S</MenuItem>
                                        <MenuItem value="M">M</MenuItem>
                                        <MenuItem value="L">L</MenuItem>
                                    </Select>
                                </div>
                                <div className="col-span-1">
                                    <h3 className="text-sm font-medium mb-1">Số lượng</h3>
                                    <input
                                        type="number"
                                        value={variant.quantity}
                                        onChange={(e) => handleVariantChange(variant.id, 'quantity', e.target.value)}
                                        className="w-full h-[40px] border border-gray-300 p-3 text-sm rounded-sm"
                                    />
                                </div>
                                <div className="col-span-1">
                                    <h3 className="text-sm font-medium mb-1">Đơn giá</h3>
                                    <input
                                        type="number"
                                        value={variant.price}
                                        onChange={(e) => handleVariantChange(variant.id, 'price', e.target.value)}
                                        className="w-full h-[40px] border border-gray-300 p-3 text-sm rounded-sm"
                                    />
                                </div>
                                <div className="col-span-1">
                                    <h3 className="text-sm font-medium mb-1">SKU</h3>
                                    <input
                                        type="text"
                                        value={variant.sku}
                                        onChange={(e) => handleVariantChange(variant.id, 'sku', e.target.value)}
                                        className="w-full h-[40px] border border-gray-300 p-3 text-sm rounded-sm"
                                    />
                                </div>
                                <div className="col-span-1">
                                    <h3 className="text-sm font-medium mb-1">Màu (có sẵn)</h3>
                                    <Select
                                        size="small"
                                        className="w-full"
                                        value={variant.color_id || ""}
                                        onChange={(e) =>
                                            handleVariantChange(variant.id, 'color_id', e.target.value)
                                        }
                                    >
                                        <MenuItem value="">None</MenuItem>
                                        {colors.map((c) => (
                                            <MenuItem key={c.id} value={c.id}>
                                                {c.name} ({c.code})
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </div>
                                <div className="col-span-2">
                                    <ColorPicker
                                        color={variant.color_code || ""}
                                        onChange={(newCode) =>
                                            handleVariantChange(variant.id, 'color_override', {
                                                name: `Custom-${variant.id}`,
                                                code: newCode
                                            })
                                        }
                                    />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
                <div className="mb-4">
                    <Button
                        type="button"
                        className="btn-outline-blue px-4"
                        onClick={handleAddVariant}
                    >
                        Thêm biến thể
                    </Button>
                </div>
                <div className="flex gap-3">
                    <Button
                        type="button"
                        onClick={onClose}
                        className="btn-outline btn-lg w-full"
                    >
                        Hủy
                    </Button>
                    <Button
                        type="submit"
                        disabled={loading}
                        className="btn-blue btn-lg w-full flex gap-2"
                    >
                        <FaCloudUploadAlt className="text-[25px] text-white" />
                        {loading ? 'Đang cập nhật...' : 'Cập nhật sản phẩm'}
                    </Button>
                </div>
            </form>
        </section>
    );
}

export default EditProduct;