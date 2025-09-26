import React, { useContext, useEffect, useState } from "react";
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import { LazyLoadImage } from "react-lazy-load-image-component";
import 'react-lazy-load-image-component/src/effects/blur.css';
import { IoMdClose } from "react-icons/io";
import Button from "@mui/material/Button";
import { FaChevronDown, FaChevronUp, FaCloudUploadAlt, FaCopy, FaPlus } from "react-icons/fa";
import ColorPicker from "../../Components/ColorPicker";
import { Checkbox, FormControl, ListItemText } from "@mui/material";
import { MyContext } from "../../App";
import { fetchWithAutoRefresh, getDataApi, postDataApi } from "../../utils/api";
import HierarchicalCategorySelect from "./categoriesSelect";


const AddProduct = () => {
    const [variantGroups, setVariantGroups] = useState([]);
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
    const [availableSizes, setAvailableSizes] = useState({
        hasMultipleTypes: false,
        groups: [],
        sizes: []
    });
    const [collapsedGroups, setCollapsedGroups] = useState({});

    const [brands, setBrands] = useState([]);
    const [selectedBrand, setSelectedBrand] = useState('');
    const [materials, setMaterials] = useState([]);
    const [selectedMaterials, setSelectedMaterials] = useState([]);
    const [tags, setTags] = useState([]);
    const [selectedTags, setSelectedTags] = useState([]);

    const context = useContext(MyContext);
    const { onUpdated } = context?.isOpenFullScreenPanel || {};

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
                }
            } catch (error) {
                console.error("Error fetching categories:", error);
                setCategories([]);
            }
        };
        fetchCategories();
    }, []);

    useEffect(() => {
        const fetchBrands = async () => {
            try {
                const response = await getDataApi('/admin/brand/all');
                if (response.success === true) {
                    setBrands(response.data.data || []);
                }
            } catch (error) {
                console.error('Error fetching brands:', error);
            }
        };

        const fetchMaterials = async () => {
            try {
                const response = await getDataApi('/admin/material/all');
                if (response.success === true) {
                    setMaterials(response.data.data || []);
                }
            } catch (error) {
                console.error('Error fetching materials:', error);
            }
        };

        const fetchTags = async () => {
            try {
                const response = await getDataApi('/admin/tag/all');
                if (response.success === true) {
                    setTags(response.data.data || []);
                }
            } catch (error) {
                console.error('Error fetching tags:', error);
            }
        };

        fetchBrands();
        fetchMaterials();
        fetchTags();
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

    const convertToBase64 = (file) => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
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
        setVariantGroups(prev => prev.filter(group => group.id !== groupId));
    };

    const handleMaterialChange = (materialId, field, value) => {
        setSelectedMaterials(prev => {
            const existing = prev.find(m => m.material_id === materialId);
            if (existing) {
                return prev.map(m =>
                    m.material_id === materialId
                        ? { ...m, [field]: value }
                        : m
                );
            } else {
                return [...prev, { material_id: materialId, percentage: field === 'percentage' ? value : 0 }];
            }
        });
    };

    const handleMaterialToggle = (materialId) => {
        setSelectedMaterials(prev => {
            const exists = prev.find(m => m.material_id === materialId);
            if (exists) {
                return prev.filter(m => m.material_id !== materialId);
            } else {
                return [...prev, { material_id: materialId, percentage: 0 }];
            }
        });
    };

    const handleTagToggle = (tagId) => {
        setSelectedTags(prev => {
            if (prev.includes(tagId)) {
                return prev.filter(id => id !== tagId);
            } else {
                return [...prev, tagId];
            }
        });
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
                    newVariants = group.variants.filter(variant => variant.size !== sizeName);
                } else {
                    newSelectedSizes = [...group.selectedSizes, sizeName];
                    newVariants = [...group.variants, {
                        size: sizeName,
                        price: '',
                        quantity: '',
                        sku: '',
                        image: null
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

    const handleFormDataChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleCategorySelectionChange = (selectedIds) => {
        setSelectedCategories(selectedIds);
    };

    const isColorSelected = (group) => {
        if (group.color_type === 'none') return true;
        if (group.color_type === 'available') return !!group.color_id;
        if (group.color_type === 'custom') return !!(group.color_name && group.color_code);
        return false;
    };

    const handleImageUpload = async (e) => {
        const files = Array.from(e.target.files);
        const newImages = await Promise.all(files.map(async (file) => {
            const base64 = await convertToBase64(file);
            return {
                id: Date.now() + Math.random(),
                url: URL.createObjectURL(file),
                name: file.name,
                base64
            };
        }));
        setImages(prev => [...prev, ...newImages]);
    };

    const removeImage = (id) => {
        const removed = images.find(img => img.id === id);
        if (removed) URL.revokeObjectURL(removed.url);
        setImages(prev => prev.filter(img => img.id !== id));
    };

    const getAvailableSizesList = () => {
        if (!availableSizes.hasMultipleTypes) {
            return availableSizes.sizes || [];
        } else {
            return availableSizes.groups.flatMap(group => group.sizes) || [];
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

    const renderMaterialsSelection = () => {
        const totalPercentage = selectedMaterials.reduce((sum, material) => sum + (material.percentage || 0), 0);

        return (
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-gray-700">Chọn chất liệu</h4>
                    {selectedMaterials.length > 0 && (
                        <span className={`text-sm font-medium ${totalPercentage > 100 ? 'text-red-600' : 'text-green-600'}`}>
                            Tổng: {totalPercentage}%
                        </span>
                    )}
                </div>

                <div className="grid grid-cols-2 gap-3">
                    {materials.map(material => {
                        const selected = selectedMaterials.find(m => m.material_id === material.id);
                        return (
                            <div key={material.id} className={`p-3 border rounded-lg transition-all ${selected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="flex items-center cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={!!selected}
                                            onChange={() => handleMaterialToggle(material.id)}
                                            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer"
                                        />
                                        <span className="ml-2 text-sm font-medium text-gray-700">{material.name}</span>
                                    </label>
                                </div>

                                {selected && (
                                    <div>
                                        <label className="block text-xs text-gray-600 mb-1">Phần trăm (%)</label>
                                        <input
                                            type="number"
                                            min="0"
                                            max="100"
                                            value={selected.percentage || ''}
                                            onChange={(e) => handleMaterialChange(material.id, 'percentage', parseFloat(e.target.value) || 0)}
                                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                            placeholder="0"
                                        />
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
        );
    };

    const renderTagsSelection = () => {
        return (
            <div className="space-y-4">
                <h4 className="text-sm font-medium text-gray-700">Chọn tags</h4>
                <div className="grid grid-cols-3 gap-2">
                    {tags.map(tag => (
                        <label key={tag.id} className="flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={selectedTags.includes(tag.id)}
                                onChange={() => handleTagToggle(tag.id)}
                                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer"
                            />
                            <span className="ml-2 text-sm text-gray-700">{tag.name}</span>
                        </label>
                    ))}
                </div>

                {selectedTags.length > 0 && (
                    <div className="mt-3">
                        <p className="text-xs text-gray-600 mb-2">Tags đã chọn:</p>
                        <div className="flex flex-wrap gap-2">
                            {selectedTags.map(tagId => {
                                const tag = tags.find(t => t.id === tagId);
                                return tag ? (
                                    <span key={tagId} className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded">
                                        {tag.name}
                                    </span>
                                ) : null;
                            })}
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

        if (selectedMaterials.length > 0) {
            const totalPercentage = selectedMaterials.reduce((sum, material) => sum + (material.percentage || 0), 0);
            if (totalPercentage > 100) {
                context.openAlertBox("error", 'Tổng phần trăm chất liệu không được vượt quá 100%');
                return false;
            }

            for (let material of selectedMaterials) {
                if (!material.percentage || material.percentage <= 0) {
                    context.openAlertBox("error", 'Phần trăm chất liệu phải lớn hơn 0');
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
                short_description: formData.short_description.trim(),
                description: formData.description?.trim() || null,
                images: images.map(img => img.base64),
                categories_id: selectedCategories,
                product_variant: allVariants,
                brand_id: selectedBrand || null,
                materials: selectedMaterials.length > 0 ? selectedMaterials : null,
                tags_id: selectedTags.length > 0 ? selectedTags : null
            };

            const result = await postDataApi('/admin/product/', submitData);

            if (!result.success) {
                context.openAlertBox("error", result?.data?.detail.message || 'Có lỗi xảy ra khi tạo sản phẩm');
                return;
            }

            context.openAlertBox("success", result?.message);
            if (onUpdated) {
                onUpdated();
            }
            context.setIsOpenFullScreenPanel({ open: false });
            setFormData({ name: '', short_description: '', description: '' });
            setVariantGroups([]);
            setSelectedCategories([]);
            images.forEach(img => URL.revokeObjectURL(img.url));
            setImages([]);
        } catch (err) {
            console.error('Submit error:', err);
            context.openAlertBox("error", 'Có lỗi xảy ra khi tạo sản phẩm');
        } finally {
            setLoading(false);
        }
    };

    const toggleGroupCollapse = (groupId) => {
        setCollapsedGroups(prev => ({
            ...prev,
            [groupId]: !prev[groupId]
        }));
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

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
            <div className="max-w-6xl mx-auto p-6">
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6 p-6">
                    <h1 className="text-2xl font-bold text-gray-800 mb-2">Thêm sản phẩm mới</h1>
                    <p className="text-gray-600">Tạo sản phẩm mới với thông tin chi tiết và biến thể</p>
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
                                    <div className="w-2 h-6 bg-purple-500 rounded-full mr-3"></div>
                                    Thương hiệu
                                </h2>

                                <FormControl fullWidth size="small">
                                    <Select
                                        value={selectedBrand}
                                        onChange={(e) => setSelectedBrand(e.target.value)}
                                        displayEmpty
                                        className="!text-sm"
                                    >
                                        <MenuItem value="">Không chọn thương hiệu</MenuItem>
                                        {brands.map((brand) => (
                                            <MenuItem key={brand.id} value={brand.id}>
                                                {brand.name}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            </div>

                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                    <div className="w-2 h-6 bg-green-500 rounded-full mr-3"></div>
                                    Chất liệu
                                </h2>

                                {renderMaterialsSelection()}
                            </div>

                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                    <div className="w-2 h-6 bg-yellow-500 rounded-full mr-3"></div>
                                    Tags
                                </h2>

                                {renderTagsSelection()}
                            </div>

                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                    <div className="w-2 h-6 bg-green-500 rounded-full mr-3"></div>
                                    Ảnh chính sản phẩm
                                </h2>

                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Thêm ảnh chính <span className="text-red-500">*</span>
                                        </label>
                                        <input
                                            type="file"
                                            accept="image/*"
                                            multiple
                                            onChange={handleImageUpload}
                                            className="hidden"
                                            id="main-images-upload"
                                        />
                                        <label
                                            htmlFor="main-images-upload"
                                            className="w-full px-4 py-8 border-2 border-dashed border-gray-300 rounded-lg text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors block"
                                        >
                                            <div className="flex flex-col items-center">
                                                <FaCloudUploadAlt className="text-3xl text-gray-400 mb-2" />
                                                <p className="text-sm font-medium text-gray-700">Nhấp để chọn ảnh</p>
                                                <p className="text-xs text-gray-500">Hỗ trợ nhiều ảnh cùng lúc</p>
                                            </div>
                                        </label>
                                    </div>

                                    {images.length > 0 && (
                                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                                            {images.map((image) => (
                                                <div key={image.id} className="relative group">
                                                    <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                                                        <img
                                                            src={image.url}
                                                            alt={image.name}
                                                            className="w-full h-full object-cover"
                                                        />
                                                    </div>
                                                    <button
                                                        type="button"
                                                        onClick={() => removeImage(image.id)}
                                                        className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                                                    >
                                                        <IoMdClose />
                                                    </button>
                                                    <p className="text-xs text-gray-500 mt-1 truncate">{image.name}</p>
                                                </div>
                                            ))}
                                        </div>
                                    )}
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
                                        className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg flex items-center gap-2 transition-colors cursor-pointer"
                                        onClick={handleAddVariantGroup}
                                    >
                                        <FaPlus className="text-sm" />
                                        Thêm biến thể
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
                                                            className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-200 hover:bg-gray-300 rounded transition-colors cursor-pointer"
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
                                                        className="text-red-500 hover:text-red-700 transition-colors cursor-pointer"
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
                                                                            className="px-3 py-1 bg-green-500 hover:bg-green-600 text-white text-xs rounded-md transition-colors flex items-center gap-1 cursor-pointer"
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
                                    <p className="text-white">{loading ? 'Đang tạo sản phẩm...' : 'Tạo sản phẩm'}</p>
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

export default AddProduct