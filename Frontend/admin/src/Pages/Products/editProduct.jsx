import { useContext, useEffect, useState } from "react";
import { MyContext } from "../../App";
import { fetchWithAutoRefresh, getDataApi, putDataApi } from "../../utils/api";
import { Button, Checkbox, ListItemText, MenuItem, Select } from "@mui/material";
import { IoMdClose } from "react-icons/io";
import { LazyLoadImage } from "react-lazy-load-image-component";
import { FaCloudUploadAlt, FaCopy, FaPlus } from "react-icons/fa";
import ColorPicker from "../../Components/ColorPicker";
import { v4 as uuidv4 } from 'uuid';
import HierarchicalCategorySelect from "./categoriesSelect";
import { FaChevronDown, FaChevronUp } from 'react-icons/fa';


const EditProduct = ({ productId, onClose, onProductUpdated }) => {
    const [variantGroups, setVariantGroups] = useState([]);
    const [deletedVariantIds, setDeletedVariantIds] = useState([]);
    const [collapsedGroups, setCollapsedGroups] = useState({});
    const [images, setImages] = useState([]);
    const [formData, setFormData] = useState({
        name: '',
        short_description: '',
        description: ''
    });
    const [loading, setLoading] = useState(false);
    const [categories, setCategories] = useState([]);
    const [selectedCategories, setSelectedCategories] = useState([]);
    const [colors, setColors] = useState([]);
    const [initialLoading, setInitialLoading] = useState(true);

    const [availableSizes, setAvailableSizes] = useState({
        hasMultipleTypes: false,
        groups: [],
        sizes: []
    });
    const [collapsedVariants, setCollapsedVariants] = useState({});

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
        const fetchSizes = async () => {
            if (selectedCategories.length === 0) {
                setAvailableSizes({
                    hasMultipleTypes: false,
                    groups: [],
                    sizes: []
                });
                return;
            }

            const selectedCategoryObjects = categories.filter(cat =>
                selectedCategories.includes(cat.id)
            );

            const typeSizes = selectedCategoryObjects.map(cat => cat.type_size);
            const uniqueTypes = [...new Set(typeSizes)];

            try {
                const queryParams = new URLSearchParams();
                uniqueTypes.forEach(type => {
                    queryParams.append('type_sizes', type);
                });

                const res = await getDataApi(`/admin/size/?${queryParams.toString()}`);

                if (res.success === true) {
                    const sizesArray = res.data || [];

                    if (uniqueTypes.length === 1) {
                        const singleType = uniqueTypes[0];
                        const sizes = sizesArray.filter(size => size.type === singleType);

                        setAvailableSizes({
                            hasMultipleTypes: false,
                            groups: [],
                            sizes: sizes
                        });
                    } else {
                        const groups = uniqueTypes.map(type => {
                            const sizesOfType = sizesArray.filter(size => size.type === type);
                            return {
                                type: type,
                                label: getTypeLabel(type),
                                sizes: sizesOfType
                            };
                        });

                        setAvailableSizes({
                            hasMultipleTypes: true,
                            groups: groups,
                            sizes: []
                        });
                    }
                } else {
                    console.error("Failed to fetch sizes:", res.message);
                    setAvailableSizes({
                        hasMultipleTypes: false,
                        groups: [],
                        sizes: []
                    });
                }
            } catch (error) {
                console.error("Error fetching sizes:", error);
                setAvailableSizes({
                    hasMultipleTypes: false,
                    groups: [],
                    sizes: []
                });
            }
        };

        fetchSizes();
    }, [selectedCategories, categories]);

    const getTypeLabel = (type) => {
        const typeLabels = {
            'clothing': 'Quần áo',
            'shoe': 'Giày dép',
            'hat': 'Mũ nón',
            'accessory': 'Phụ kiện'
        };
        return typeLabels[type] || type;
    };

    useEffect(() => {
        const fetchColors = async () => {
            try {
                const queryParams = new URLSearchParams({
                    skip: "0",
                    limit: "1000",
                });

                const res = await getDataApi(`/admin/color?${queryParams.toString()}`);
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
                        short_description: product.short_description || '',
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

                    const variantGroups = {};
                    product.product_variant?.forEach(variant => {
                        let colorKey, colorType;

                        if (variant.color_id) {
                            colorKey = `available_${variant.color_id}`;
                            colorType = 'available';
                        } else if (variant.color_name || variant.color_code) {
                            colorKey = `custom_${variant.color_name || ''}_${variant.color_code || ''}`;
                            colorType = 'custom';
                        } else {
                            colorKey = 'none';
                            colorType = 'none';
                        }

                        if (!variantGroups[colorKey]) {
                            variantGroups[colorKey] = {
                                id: `group_${Date.now()}_${Math.random()}`,
                                color_type: colorType,
                                color_id: variant.color_id || null,
                                color_name: variant.color_name || null,
                                color_code: variant.color_code || null,
                                selectedSizes: [],
                                variants: []
                            };
                        }

                        variantGroups[colorKey].selectedSizes.push(variant.size || '');
                        variantGroups[colorKey].variants.push({
                            size: variant.size || '',
                            price: variant.original_price || '',
                            quantity: variant.quantity || '',
                            sku: variant.sku || '',
                            image: variant.image || null,
                            id: variant.id
                        });
                    });

                    setVariantGroups(Object.values(variantGroups));

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

    const handleAddVariantGroup = () => {
        const newGroupId = `group_${Date.now()}`;
        const newGroup = {
            id: newGroupId,
            color_type: 'none',
            color_id: null,
            color_name: null,
            color_code: null,
            selectedSizes: [],
            variants: []
        };
        setVariantGroups(prev => [...prev, newGroup]);
    };

    const handleRemoveVariantGroup = (groupId) => {
        const groupToRemove = variantGroups.find(group => group.id === groupId);

        if (groupToRemove) {
            const existingVariantIds = groupToRemove.variants
                .filter(v => v.id && typeof v.id === 'string' && v.id.length > 10)
                .map(v => v.id);
            if (existingVariantIds.length > 0) {
                setDeletedVariantIds(prev => [...prev, ...existingVariantIds]);
            }
        }

        setVariantGroups(prev => prev.filter(group => group.id !== groupId));
    };

    const toggleGroupCollapse = (groupId) => {
        setCollapsedGroups(prev => ({
            ...prev,
            [groupId]: !prev[groupId]
        }));
    };

    const handleColorChange = (groupId, field, value) => {
        setVariantGroups(prev =>
            prev.map(group => {
                if (group.id !== groupId) return group;

                if (field === 'color_type') {
                    return {
                        ...group,
                        color_type: value,
                        color_id: null,
                        color_name: null,
                        color_code: null,
                        selectedSizes: [],
                        variants: []
                    };
                }

                if (field === 'color_id') {
                    return {
                        ...group,
                        color_id: value || null,
                        color_name: null,
                        color_code: null
                    };
                }

                if (field === 'color_name' || field === 'color_code') {
                    return {
                        ...group,
                        color_id: null,
                        [field]: value
                    };
                }

                return group;
            })
        );
    };

    const handleSizeToggle = (groupId, sizeName) => {
        setVariantGroups(prev =>
            prev.map(group => {
                if (group.id !== groupId) return group;

                const isSelected = group.selectedSizes.includes(sizeName);
                let newSelectedSizes;
                let newVariants;

                if (isSelected) {
                    newSelectedSizes = group.selectedSizes.filter(size => size !== sizeName);
                    const removedVariant = group.variants.find(variant => variant.size === sizeName);
                    if (removedVariant && removedVariant.id && typeof removedVariant.id === 'string' && removedVariant.id.length > 10) {
                        setDeletedVariantIds(prev => [...prev, removedVariant.id]);
                    }
                    newVariants = group.variants.filter(variant => variant.size !== sizeName);
                } else {
                    newSelectedSizes = [...group.selectedSizes, sizeName];
                    newVariants = [...group.variants, {
                        size: sizeName,
                        price: '',
                        quantity: '',
                        sku: '',
                        image: null,
                        id: null
                    }];
                }

                return {
                    ...group,
                    selectedSizes: newSelectedSizes,
                    variants: newVariants
                };
            })
        );
    };

    const handleVariantUpdate = (groupId, size, field, value) => {
        setVariantGroups(prev =>
            prev.map(group => {
                if (group.id !== groupId) return group;

                return {
                    ...group,
                    variants: group.variants.map(variant => {
                        if (variant.size !== size) return variant;
                        return { ...variant, [field]: value };
                    })
                };
            })
        );
    };

    const handleVariantImageUpload = async (groupId, size, file) => {
        if (!file) return;

        const base64 = await convertToBase64(file);
        handleVariantUpdate(groupId, size, 'image', base64);
    };

    const copyFirstVariantToAll = (groupId) => {
        setVariantGroups(prev =>
            prev.map(group => {
                if (group.id !== groupId || group.variants.length === 0) return group;

                const firstVariant = group.variants[0];
                const updatedVariants = group.variants.map(variant => ({
                    ...variant,
                    price: firstVariant.price,
                    quantity: firstVariant.quantity,
                    image: firstVariant.image
                }));

                return {
                    ...group,
                    variants: updatedVariants
                };
            })
        );
    };

    const isColorSelected = (group) => {
        if (group.color_type === 'none') return true;
        if (group.color_type === 'available') return !!group.color_id;
        if (group.color_type === 'custom') return !!(group.color_name && group.color_code);
        return false;
    };

    const getAvailableSizesList = () => {
        if (!availableSizes.hasMultipleTypes) {
            return availableSizes.sizes || [];
        } else {
            return availableSizes.groups.flatMap(group => group.sizes) || [];
        }
    };

    const handleFormDataChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleCategorySelectionChange = (selectedIds) => {
        setSelectedCategories(selectedIds);
    };

    const renderSizeSelection = (group) => {
        const availableSizesList = getAvailableSizesList();
        const isColorChosen = isColorSelected(group);

        if (availableSizesList.length === 0) {
            return (
                <div className="text-sm text-gray-500 italic">
                    Chọn danh mục trước để hiển thị kích cỡ
                </div>
            );
        }

        if (!isColorChosen) {
            return (
                <div className="text-sm text-gray-500 italic">
                    Vui lòng chọn loại màu trước
                </div>
            );
        }

        if (!availableSizes.hasMultipleTypes) {
            return (
                <div className="grid grid-cols-4 gap-2">
                    {availableSizesList.map((size) => (
                        <label key={size.id} className="flex items-center cursor-pointer p-2 border rounded-md hover:bg-gray-50">
                            <input
                                type="checkbox"
                                checked={group.selectedSizes.includes(size.name)}
                                onChange={() => handleSizeToggle(group.id, size.name)}
                                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                            />
                            <span className="ml-2 text-sm">{size.name}</span>
                        </label>
                    ))}
                </div>
            );
        } else {
            return (
                <div className="space-y-4">
                    {availableSizes.groups.map((group_type) => (
                        <div key={group_type.type}>
                            <h5 className="text-sm font-medium text-gray-700 mb-2">{group_type.label}</h5>
                            <div className="grid grid-cols-4 gap-2">
                                {group_type.sizes.map((size) => (
                                    <label key={size.id} className="flex items-center cursor-pointer p-2 border rounded-md hover:bg-gray-50">
                                        <input
                                            type="checkbox"
                                            checked={group.selectedSizes.includes(size.name)}
                                            onChange={() => handleSizeToggle(group.id, size.name)}
                                            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                        />
                                        <span className="ml-2 text-sm">{size.name}</span>
                                    </label>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            );
        }
    };

    const renderColorSelection = (group) => {
        return (
            <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Chọn loại màu</h4>
                <div className="flex gap-4 mb-3">
                    <label className="flex items-center cursor-pointer">
                        <input
                            type="radio"
                            name={`color_type_${group.id}`}
                            value="available"
                            checked={group.color_type === 'available'}
                            onChange={(e) => handleColorChange(group.id, 'color_type', e.target.value)}
                            className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                        />
                        <span className="ml-2 text-sm text-gray-700">Màu có sẵn</span>
                    </label>
                    <label className="flex items-center cursor-pointer">
                        <input
                            type="radio"
                            name={`color_type_${group.id}`}
                            value="custom"
                            checked={group.color_type === 'custom'}
                            onChange={(e) => handleColorChange(group.id, 'color_type', e.target.value)}
                            className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                        />
                        <span className="ml-2 text-sm text-gray-700">Màu tùy chỉnh</span>
                    </label>
                    <label className="flex items-center cursor-pointer">
                        <input
                            type="radio"
                            name={`color_type_${group.id}`}
                            value="none"
                            checked={group.color_type === 'none'}
                            onChange={(e) => handleColorChange(group.id, 'color_type', e.target.value)}
                            className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                        />
                        <span className="ml-2 text-sm text-gray-700">Không màu</span>
                    </label>
                </div>

                {group.color_type === 'available' && (
                    <div>
                        <Select
                            size="small"
                            className="w-full"
                            value={group.color_id || ""}
                            onChange={(e) => handleColorChange(group.id, 'color_id', e.target.value)}
                        >
                            <MenuItem value="">Chọn màu</MenuItem>
                            {colors.map((c) => (
                                <MenuItem key={c.id} value={c.id}>
                                    <div className="flex items-center gap-2">
                                        <div
                                            className="w-4 h-4 rounded-full border border-gray-300"
                                            style={{ backgroundColor: c.code }}
                                        ></div>
                                        {c.name} ({c.code})
                                    </div>
                                </MenuItem>
                            ))}
                        </Select>
                    </div>
                )}

                {group.color_type === 'custom' && (
                    <div className="space-y-3">
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Tên màu tùy chỉnh</label>
                            <input
                                type="text"
                                value={group.color_name || ''}
                                onChange={(e) => handleColorChange(group.id, 'color_name', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="Ví dụ: Xanh Navy"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Chọn màu</label>
                            <div className="flex items-center gap-3">
                                <ColorPicker
                                    color={group.color_code || "#000000"}
                                    onChange={(newCode) => handleColorChange(group.id, 'color_code', newCode)}
                                />
                                <div className="flex items-center gap-2">
                                    <div
                                        className="w-8 h-8 rounded-lg border-2 border-gray-300 shadow-sm"
                                        style={{ backgroundColor: group.color_code || "#000000" }}
                                    ></div>
                                    <span className="text-xs text-gray-500 font-mono">
                                        {group.color_code || "#000000"}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        );
    };

    const validateForm = () => {
        if (!formData.name.trim()) {
            context.openAlertBox("error", 'Tên sản phẩm không được để trống');
            return false;
        }

        if (!formData.short_description.trim()) {
            context.openAlertBox("error", 'Mô tả ngắn không được để trống');
            return false;
        }

        if (images.length === 0) {
            context.openAlertBox("error", 'Vui lòng thêm ít nhất một ảnh chính cho sản phẩm');
            return false;
        }

        if (selectedCategories.length === 0) {
            context.openAlertBox("error", 'Vui lòng chọn ít nhất một danh mục');
            return false;
        }

        if (variantGroups.length === 0) {
            context.openAlertBox("error", 'Vui lòng thêm ít nhất một biến thể');
            return false;
        }

        for (let group of variantGroups) {
            if (group.variants.length === 0) {
                context.openAlertBox("error", 'Vui lòng chọn ít nhất một kích cỡ cho mỗi nhóm biến thể');
                return false;
            }

            for (let variant of group.variants) {
                if (!variant.price || variant.price <= 0) {
                    context.openAlertBox("error", `Giá phải lớn hơn 0 cho biến thể ${variant.size || 'không xác định'}`);
                    return false;
                }
                if (!variant.quantity || variant.quantity < 0) {
                    context.openAlertBox("error", `Số lượng không được âm cho biến thể ${variant.size || 'không xác định'}`);
                    return false;
                }
                if (!variant.image) {
                    context.openAlertBox("error", `Vui lòng thêm ảnh phụ cho biến thể ${variant.size || 'không xác định'}`);
                    return false;
                }
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

            const allVariants = variantGroups.flatMap(group =>
                group.variants.map(variant => {
                    const variantData = {
                        size: variant.size || null,
                        image: variant.image,
                        price: parseInt(variant.price),
                        quantity: parseInt(variant.quantity),
                        sku: variant.sku?.trim() || null
                    };

                    if (variant.id) {
                        variantData.id = variant.id;
                    }

                    if (group.color_type === 'available' && group.color_id) {
                        variantData.color_id = group.color_id;
                    } else if (group.color_type === 'custom' && (group.color_name || group.color_code)) {
                        variantData.color_name = group.color_name;
                        variantData.color_code = group.color_code;
                    }

                    return variantData;
                })
            );

            const submitData = {
                name: formData.name.trim(),
                description: formData.description?.trim() || null,
                short_description: formData.short_description.trim(),
                images: images.map(img => img.base64),
                categories_id: validCategoryIds,
                product_variant: allVariants,
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
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
            <div className="max-w-6xl mx-auto p-6">
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6 p-6">
                    <h1 className="text-2xl font-bold text-gray-800 mb-2">Cập nhật sản phẩm</h1>
                    <p className="text-gray-600">Cập nhật sản phẩm mới với thông tin chi tiết và biến thể</p>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-2 space-y-6">
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                    <div className="w-2 h-6 bg-blue-500 rounded-full mr-3"></div>
                                    Thông tin cơ bản
                                </h2>

                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Tên sản phẩm <span className="text-red-500">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            value={formData.name}
                                            onChange={(e) => handleFormDataChange('name', e.target.value)}
                                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-white"
                                            placeholder="Nhập tên sản phẩm..."
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Mô tả ngắn <span className="text-red-500">*</span>
                                        </label>
                                        <textarea
                                            value={formData.short_description}
                                            onChange={(e) => handleFormDataChange('short_description', e.target.value)}
                                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-white resize-none"
                                            rows="3"
                                            placeholder="Mô tả ngắn gọn về sản phẩm..."
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Mô tả chi tiết
                                        </label>
                                        <textarea
                                            value={formData.description}
                                            onChange={(e) => handleFormDataChange('description', e.target.value)}
                                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-white resize-none"
                                            rows="5"
                                            placeholder="Mô tả chi tiết về sản phẩm..."
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                    <div className="w-2 h-6 bg-green-500 rounded-full mr-3"></div>
                                    Hình ảnh sản phẩm
                                </h2>

                                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                                    {images.map((img) => (
                                        <div key={img.id} className="relative group">
                                            <div className="aspect-square border-2 border-dashed border-gray-200 rounded-lg overflow-hidden bg-gray-50 hover:border-blue-300 transition-colors">
                                                <LazyLoadImage
                                                    src={img.url}
                                                    alt="Product image"
                                                    className="w-full h-full object-cover"
                                                    effect="blur"
                                                />
                                            </div>
                                            <button
                                                type="button"
                                                onClick={() => removeImage(img.id)}
                                                className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 hover:bg-red-600 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                                            >
                                                <IoMdClose className="text-white text-sm" />
                                            </button>
                                        </div>
                                    ))}

                                    <div className="aspect-square border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center bg-gray-50 hover:border-blue-400 hover:bg-blue-50 transition-all cursor-pointer relative group">
                                        <input
                                            type="file"
                                            accept="image/*"
                                            multiple
                                            onChange={handleImageUpload}
                                            className="absolute inset-0 opacity-0 cursor-pointer"
                                            id="imageUpload"
                                        />
                                        <FaPlus className="text-gray-400 text-xl mb-2 group-hover:text-blue-500 transition-colors" />
                                        <span className="text-sm text-gray-500 group-hover:text-blue-600 font-medium">Thêm ảnh</span>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <h2 className="text-lg font-semibold text-gray-800 flex items-center">
                                        <div className="w-2 h-6 bg-purple-500 rounded-full mr-3"></div>
                                        Biến thể sản phẩm
                                    </h2>
                                    <Button
                                        type="button"
                                        className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg flex items-center gap-2 transition-colors"
                                        onClick={handleAddVariantGroup}
                                    >
                                        <FaPlus className="text-sm" />
                                        Thêm nhóm biến thể
                                    </Button>
                                </div>

                                <div className="space-y-6">
                                    {variantGroups.length === 0 ? (
                                        <div className="text-center py-12 text-gray-500">
                                            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                                <FaPlus className="text-2xl text-gray-400" />
                                            </div>
                                            <p className="text-lg font-medium">Chưa có biến thể nào</p>
                                            <p className="text-sm">Nhấn "Thêm biến thể" để bắt đầu</p>
                                        </div>
                                    ) : (
                                        variantGroups.map((group, index) => (
                                            <div key={group.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                                                <div className="flex items-center justify-between mb-4">
                                                    <div className="flex items-center gap-3">
                                                        <span className="text-sm font-medium text-gray-700">Nhóm biến thể #{index + 1}</span>
                                                        <button
                                                            type="button"
                                                            onClick={() => toggleGroupCollapse(group.id)}
                                                            className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-200 hover:bg-gray-300 rounded transition-colors"
                                                        >
                                                            {collapsedGroups[group.id] ? (
                                                                <>
                                                                    <FaChevronDown size={10} />
                                                                    Mở rộng
                                                                </>
                                                            ) : (
                                                                <>
                                                                    <FaChevronUp size={10} />
                                                                    Thu gọn
                                                                </>
                                                            )}
                                                        </button>
                                                    </div>
                                                    <button
                                                        type="button"
                                                        onClick={() => handleRemoveVariantGroup(group.id)}
                                                        className="text-red-500 hover:text-red-700 transition-colors"
                                                    >
                                                        <IoMdClose size={20} />
                                                    </button>
                                                </div>
                                                {!collapsedGroups[group.id] && (
                                                    <>
                                                        {renderColorSelection(group)}

                                                        <div className="mb-4">
                                                            <h4 className="text-sm font-medium text-gray-700 mb-2">Chọn kích cỡ</h4>
                                                            {renderSizeSelection(group)}
                                                        </div>

                                                        {group.variants.length > 0 && (
                                                            <div className="space-y-4">
                                                                <div className="flex items-center justify-between">
                                                                    <h4 className="text-sm font-medium text-gray-700">Chi tiết biến thể</h4>
                                                                    {group.variants.length > 1 && (
                                                                        <button
                                                                            type="button"
                                                                            onClick={() => copyFirstVariantToAll(group.id)}
                                                                            className="px-3 py-1 bg-green-500 hover:bg-green-600 text-white text-xs rounded-md transition-colors flex items-center gap-1"
                                                                        >
                                                                            <FaCopy size={10} />
                                                                            Sao chép từ đầu tiên
                                                                        </button>
                                                                    )}
                                                                </div>
                                                                {group.variants.map((variant) => (
                                                                    <div key={variant.size} className="bg-white p-4 rounded-lg border">
                                                                        <div className="mb-3">
                                                                            <span className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm font-medium">
                                                                                Kích cỡ: {variant.size}
                                                                            </span>
                                                                        </div>

                                                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                                                            <div>
                                                                                <label className="block text-xs font-medium text-gray-600 mb-1">Giá (VNĐ)</label>
                                                                                <input
                                                                                    type="number"
                                                                                    value={variant.price}
                                                                                    onChange={(e) => handleVariantUpdate(group.id, variant.size, 'price', e.target.value)}
                                                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                                                    placeholder="0"
                                                                                />
                                                                            </div>

                                                                            <div>
                                                                                <label className="block text-xs font-medium text-gray-600 mb-1">Số lượng</label>
                                                                                <input
                                                                                    type="number"
                                                                                    value={variant.quantity}
                                                                                    onChange={(e) => handleVariantUpdate(group.id, variant.size, 'quantity', e.target.value)}
                                                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                                                    placeholder="0"
                                                                                />
                                                                            </div>

                                                                            <div>
                                                                                <label className="block text-xs font-medium text-gray-600 mb-1">SKU</label>
                                                                                <input
                                                                                    type="text"
                                                                                    value={variant.sku}
                                                                                    onChange={(e) => handleVariantUpdate(group.id, variant.size, 'sku', e.target.value)}
                                                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                                                    placeholder="SKU-001"
                                                                                />
                                                                            </div>

                                                                            <div>
                                                                                <label className="block text-xs font-medium text-gray-600 mb-1">Ảnh phụ</label>
                                                                                <div className="flex items-center gap-2">
                                                                                    <input
                                                                                        type="file"
                                                                                        accept="image/*"
                                                                                        onChange={(e) => handleVariantImageUpload(group.id, variant.size, e.target.files[0])}
                                                                                        className="hidden"
                                                                                        id={`image-${group.id}-${variant.size}`}
                                                                                    />
                                                                                    <label
                                                                                        htmlFor={`image-${group.id}-${variant.size}`}
                                                                                        className="flex-1 px-3 py-2 border border-dashed border-gray-300 rounded-md text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors text-sm"
                                                                                    >
                                                                                        {variant.image ? '✓ Đã chọn' : 'Chọn ảnh'}
                                                                                    </label>
                                                                                    {variant.image && (
                                                                                        <div className="w-10 h-10 border rounded overflow-hidden">
                                                                                            <img
                                                                                                src={variant.image}
                                                                                                alt="Preview"
                                                                                                className="w-full h-full object-cover"
                                                                                            />
                                                                                        </div>
                                                                                    )}
                                                                                </div>
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </>
                                                )}
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                    <div className="w-2 h-6 bg-orange-500 rounded-full mr-3"></div>
                                    Danh mục
                                </h2>

                                <HierarchicalCategorySelect
                                    categories={categories}
                                    selectedCategoryIds={selectedCategories}
                                    onSelectionChange={handleCategorySelectionChange}
                                    label=""
                                    placeholder="Chọn danh mục sản phẩm"
                                />

                                {availableSizes.hasMultipleTypes && (
                                    <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                                        <div className="flex items-start">
                                            <span className="text-amber-600 mr-2 mt-0.5">⚠️</span>
                                            <div>
                                                <p className="text-sm font-medium text-amber-800 mb-1">Lưu ý về kích cỡ</p>
                                                <p className="text-xs text-amber-700">
                                                    Bạn đã chọn các danh mục với hệ thống kích cỡ khác nhau: {availableSizes.groups.map(g => g.label).join(', ')}.
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <Button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white py-3 px-6 rounded-lg font-medium flex items-center justify-center gap-3 transition-all duration-200 shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    <FaCloudUploadAlt className="text-xl text-white" />
                                    <p className="text-white">{loading ? 'Đang cập nhật sản phẩm...' : 'Cập nhật sản phẩm'}</p>
                                </Button>

                                {loading && (
                                    <div className="mt-3 text-center">
                                        <div className="inline-block w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mr-2"></div>
                                        <span className="text-sm text-gray-600">Đang xử lý...</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default EditProduct;