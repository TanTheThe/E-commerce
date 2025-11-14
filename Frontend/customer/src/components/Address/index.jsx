import { useState, useEffect, useRef } from "react";
import { FiArrowLeft, FiCheck, FiEdit2, FiHome, FiMapPin, FiPlus, FiTrash2, FiX } from "react-icons/fi";
import toast from "react-hot-toast";
import { deleteDataApi, getDataApi, postDataApi, putDataApi } from "../../utils/api";

const AddressManager = ({ isOpen, onClose, selectedAddress, onSelectAddress }) => {
    const [addresses, setAddresses] = useState([]);
    const [loadingAddresses, setLoadingAddresses] = useState(false);
    const [showForm, setShowForm] = useState(false);
    const [isEditMode, setIsEditMode] = useState(false);
    const [editingAddressId, setEditingAddressId] = useState(null);

    const [provinces, setProvinces] = useState([]);
    const [wards, setWards] = useState([]);
    const [loadingProvinces, setLoadingProvinces] = useState(false);
    const [loadingWards, setLoadingWards] = useState(false);

    const [provinceSearchTerm, setProvinceSearchTerm] = useState('');
    const [wardSearchTerm, setWardSearchTerm] = useState('');
    const [showProvinceDropdown, setShowProvinceDropdown] = useState(false);
    const [showWardDropdown, setShowWardDropdown] = useState(false);
    const [allProvinces, setAllProvinces] = useState([]);
    const [allWards, setAllWards] = useState([]);

    const [formData, setFormData] = useState({
        line: '',
        ward_id: '',
        province_id: '',
        country: 'Việt Nam'
    });

    const [errors, setErrors] = useState({
        line: '',
        ward_id: '',
        province_id: ''
    });

    const [submitting, setSubmitting] = useState(false);
    const [deletingId, setDeletingId] = useState(null);

    const provinceSearchTimeout = useRef(null);
    const wardSearchTimeout = useRef(null);

    useEffect(() => {
        if (isOpen) {
            fetchAddresses();
        }
    }, [isOpen]);

    useEffect(() => {
        if (showForm) {
            fetchProvinces();
        }
    }, [showForm]);

    useEffect(() => {
        if (formData.province_id) {
            fetchWards(formData.province_id);
        } else {
            setWards([]);
        }
    }, [formData.province_id]);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (!event.target.closest('.province-searchable-select')) {
                setShowProvinceDropdown(false);
            }
            if (!event.target.closest('.ward-searchable-select')) {
                setShowWardDropdown(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    useEffect(() => {
        return () => {
            if (provinceSearchTimeout.current) {
                clearTimeout(provinceSearchTimeout.current);
            }
            if (wardSearchTimeout.current) {
                clearTimeout(wardSearchTimeout.current);
            }
        };
    }, []);

    const handleProvinceSearch = (searchValue) => {
        setProvinceSearchTerm(searchValue);

        if (provinceSearchTimeout.current) {
            clearTimeout(provinceSearchTimeout.current);
        }

        provinceSearchTimeout.current = setTimeout(() => {
            if (searchValue.trim()) {
                fetchProvinces(searchValue.trim());
            } else {
                setProvinces(allProvinces);
            }
        }, 600);
    };

    const handleWardSearch = (searchValue) => {
        setWardSearchTerm(searchValue);

        if (wardSearchTimeout.current) {
            clearTimeout(wardSearchTimeout.current);
        }

        wardSearchTimeout.current = setTimeout(() => {
            if (searchValue.trim() && formData.province_id) {
                fetchWards(formData.province_id, searchValue.trim());
            } else if (formData.province_id) {
                setWards(allWards);
            }
        }, 600);
    };

    const handleSelectProvince = (province) => {
        handleFormChange('province_id', province.id);
        setProvinceSearchTerm(province.name);
        setShowProvinceDropdown(false);
        clearError('province_id');
    };

    const handleSelectWard = (ward) => {
        handleFormChange('ward_id', ward.id);
        setWardSearchTerm(ward.name);
        setShowWardDropdown(false);
        clearError('ward_id');
    };

    const fetchProvinces = async (search = '') => {
        try {
            setLoadingProvinces(true);
            const url = search
                ? `/customer/address/provinces?search=${encodeURIComponent(search)}`
                : '/customer/address/provinces';
            const response = await getDataApi(url);

            if (response.success) {
                const provinceList = response.data || [];
                if (search) {
                    setProvinces(provinceList);
                } else {
                    setAllProvinces(provinceList);
                    setProvinces(provinceList);
                }
            } else {
                toast.error('Không thể tải danh sách tỉnh thành');
            }
        } catch (error) {
            console.error('Error fetching provinces:', error);
            toast.error('Có lỗi xảy ra khi tải tỉnh thành');
        } finally {
            setLoadingProvinces(false);
        }
    };

    const fetchWards = async (provinceId, search = '') => {
        if (!provinceId) {
            setWards([]);
            return;
        }

        try {
            setLoadingWards(true);
            const url = search
                ? `/customer/address/provinces/${provinceId}/wards?search=${encodeURIComponent(search)}`
                : `/customer/address/provinces/${provinceId}/wards`;
            const response = await getDataApi(url);

            if (response.success) {
                const wardList = response.data || [];
                if (search) {
                    setWards(wardList);
                } else {
                    setAllWards(wardList);
                    setWards(wardList);
                }
            } else {
                toast.error('Không thể tải danh sách phường/xã');
            }
        } catch (error) {
            console.error('Error fetching wards:', error);
            toast.error('Có lỗi xảy ra khi tải phường/xã');
        } finally {
            setLoadingWards(false);
        }
    };

    const fetchAddresses = async () => {
        try {
            setLoadingAddresses(true);
            const response = await getDataApi('/customer/address');

            if (response.success) {
                const addressList = response.data?.data || response.data || [];
                setAddresses(addressList);

                if (!selectedAddress && addressList.length > 0) {
                    const defaultAddress = addressList.find(addr => addr.is_default) || addressList[0];
                    onSelectAddress(defaultAddress);
                }
            } else {
                toast.error(response.data?.detail?.message || 'Không thể tải danh sách địa chỉ');
            }
        } catch (error) {
            console.error('Error fetching addresses:', error);
            toast.error('Có lỗi xảy ra khi tải địa chỉ');
        } finally {
            setLoadingAddresses(false);
        }
    };

    const handleCreateAddress = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            toast.error('Vui lòng điền đầy đủ thông tin bắt buộc!');
            return;
        }

        try {
            setSubmitting(true);

            const addressData = {
                line: formData.line.trim(),
                ward_id: formData.ward_id,
                province_id: formData.province_id,
                country: 'Việt Nam'
            };

            const response = await postDataApi('/customer/address', addressData);

            if (response.success) {
                toast.success('Tạo địa chỉ thành công!');

                const newAddressData = response.data?.data || response.data;
                setAddresses(prev => [...prev, newAddressData]);

                resetForm();

                if (addresses.length === 0) {
                    onSelectAddress(newAddressData);
                }
            } else {
                const rawMsg = response?.data?.detail?.message || response?.data?.detail?.[0]?.msg || "Không thể tạo địa chỉ mới";
                const cleanedMsg = rawMsg.replace(/^Value error,\s*/i, "");
                toast.error(cleanedMsg)
            }
        } catch (error) {
            console.error('Error creating address:', error);
            toast.error('Có lỗi xảy ra khi tạo địa chỉ');
        } finally {
            setSubmitting(false);
        }
    };

    const handleUpdateAddress = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            toast.error('Vui lòng điền đầy đủ thông tin bắt buộc!');
            return;
        }

        try {
            setSubmitting(true);

            const addressData = {
                line: formData.line.trim(),
                ward_id: formData.ward_id,
                province_id: formData.province_id,
                country: 'Việt Nam'
            };

            const response = await putDataApi(`/customer/address/${editingAddressId}`, addressData);

            if (response.success) {
                toast.success('Cập nhật địa chỉ thành công!');

                const updatedAddressData = response.data?.data || response.data;

                setAddresses(prev => prev.map(addr =>
                    addr.id === editingAddressId ? updatedAddressData : addr
                ));

                if (selectedAddress?.id === editingAddressId) {
                    onSelectAddress(updatedAddressData);
                }

                resetForm();
            } else {
                const rawMsg = response?.data?.detail?.message || response?.data?.detail?.[0]?.msg || "Không thể cập nhật địa chỉ";
                const cleanedMsg = rawMsg.replace(/^Value error,\s*/i, "");
                toast.error(cleanedMsg)
            }
        } catch (error) {
            console.error('Error updating address:', error);
            toast.error('Có lỗi xảy ra khi cập nhật địa chỉ');
        } finally {
            setSubmitting(false);
        }
    };

    const handleDeleteAddress = async (addressId) => {
        if (!window.confirm('Bạn có chắc chắn muốn xóa địa chỉ này?')) {
            return;
        }

        try {
            setDeletingId(addressId);

            const response = await deleteDataApi(`/customer/address/${addressId}`);

            if (response.success) {
                toast.success('Xóa địa chỉ thành công!');

                setAddresses(prev => prev.filter(addr => addr.id !== addressId));

                if (selectedAddress?.id === addressId) {
                    const remainingAddresses = addresses.filter(addr => addr.id !== addressId);
                    if (remainingAddresses.length > 0) {
                        onSelectAddress(remainingAddresses[0]);
                    } else {
                        onSelectAddress(null);
                    }
                }
            } else {
                toast.error(response.data?.detail?.message || 'Không thể xóa địa chỉ');
            }
        } catch (error) {
            console.error('Error deleting address:', error);
            toast.error('Có lỗi xảy ra khi xóa địa chỉ');
        } finally {
            setDeletingId(null);
        }
    };

    const validateForm = () => {
        const newErrors = {
            line: '',
            ward_id: '',
            province_id: ''
        };

        let isValid = true;

        if (!formData.line.trim()) {
            newErrors.line = 'Vui lòng nhập số nhà, tên đường';
            isValid = false;
        }

        if (!formData.province_id) {
            newErrors.province_id = 'Vui lòng chọn tỉnh/thành phố';
            isValid = false;
        }

        if (!formData.ward_id) {
            newErrors.ward_id = 'Vui lòng chọn phường/xã';
            isValid = false;
        }

        setErrors(newErrors);
        return isValid;
    };

    const clearError = (field) => {
        setErrors(prev => ({
            ...prev,
            [field]: ''
        }));
    };

    const handleEditClick = (address) => {
        setIsEditMode(true);
        setEditingAddressId(address.id);
        setFormData({
            line: address.line,
            ward_id: address.ward_info?.id || '',
            province_id: address.province_info?.id || '',
            country: address.country || 'Việt Nam'
        });
        setProvinceSearchTerm(address.province_info?.name || '');
        setWardSearchTerm(address.ward_info?.name || '');
        setShowForm(true);
    };

    const handleCreateClick = () => {
        setIsEditMode(false);
        setEditingAddressId(null);
        setFormData({
            line: '',
            ward_id: '',
            province_id: '',
            country: 'Việt Nam'
        });
        setShowForm(true);
    };

    const resetForm = () => {
        setShowForm(false);
        setIsEditMode(false);
        setEditingAddressId(null);
        setFormData({
            line: '',
            ward_id: '',
            province_id: '',
            country: 'Việt Nam'
        });
        setErrors({
            line: '',
            ward_id: '',
            province_id: ''
        });
        setWards([]);
        setAllWards([]);
        setProvinceSearchTerm('');
        setWardSearchTerm('');
        setShowProvinceDropdown(false);
        setShowWardDropdown(false);
    };

    const handleFormChange = (field, value) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));

        clearError(field);

        if (field === 'province_id') {
            setFormData(prev => ({
                ...prev,
                province_id: value,
                ward_id: ''
            }));
            clearError('ward_id');
        }
    };

    const handleClose = () => {
        resetForm();
        onClose();
    };

    const handleSelectAndClose = (address) => {
        onSelectAddress(address);
        toast.success('Đã chọn địa chỉ giao hàng');
        handleClose();
    };

    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 flex items-center justify-center z-50 p-4"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}
        >
            <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden">
                <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-[#ff5252] to-[#ff8a80] text-white">
                    <div className="flex items-center gap-3">
                        <FiMapPin className="text-2xl" />
                        <h2 className="text-xl font-bold">
                            {showForm
                                ? (isEditMode ? 'Sửa địa chỉ' : 'Thêm địa chỉ mới')
                                : 'Chọn địa chỉ giao hàng'
                            }
                        </h2>
                    </div>
                    <button
                        onClick={handleClose}
                        className="p-2 hover:bg-white/20 rounded-full transition-colors cursor-pointer"
                    >
                        <FiX className="text-xl" />
                    </button>
                </div>

                <div className="p-6 overflow-y-auto max-h-[calc(90vh-88px)]">
                    {!showForm ? (
                        <div>
                            <div className="flex justify-between items-center mb-4">
                                <h3 className="text-lg font-semibold">Địa chỉ của bạn</h3>
                                <button
                                    onClick={handleCreateClick}
                                    className="flex items-center gap-2 px-4 py-2 bg-[#ff5252] text-white rounded-lg font-medium hover:bg-[#e53e3e] transition-colors cursor-pointer"
                                >
                                    <FiPlus className="text-sm" />
                                    Thêm địa chỉ mới
                                </button>
                            </div>

                            {loadingAddresses ? (
                                <div className="text-center py-12">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#ff5252] mx-auto mb-4"></div>
                                    <div className="text-gray-500">Đang tải địa chỉ...</div>
                                </div>
                            ) : addresses.length === 0 ? (
                                <div className="text-center py-12">
                                    <FiMapPin className="text-6xl text-gray-300 mx-auto mb-4" />
                                    <div className="text-gray-500 text-lg mb-4">Chưa có địa chỉ nào</div>
                                    <button
                                        onClick={handleCreateClick}
                                        className="px-6 py-2 bg-[#ff5252] text-white rounded-lg font-medium hover:bg-[#e53e3e] transition-colors cursor-pointer"
                                    >
                                        Thêm địa chỉ đầu tiên
                                    </button>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {addresses.map((address) => {
                                        const isSelected = selectedAddress?.id === address.id;
                                        return (
                                            <div
                                                key={address.id}
                                                className={`relative border-2 rounded-lg p-4 transition-all duration-200 ${isSelected
                                                    ? 'border-[#ff5252] bg-[#ff5252]/5 shadow-md'
                                                    : 'border-gray-200 hover:border-[#ff5252]/50 hover:shadow-sm'
                                                    }`}
                                            >
                                                {isSelected && (
                                                    <div className="absolute top-3 right-3 w-6 h-6 bg-[#ff5252] rounded-full flex items-center justify-center">
                                                        <FiCheck className="text-white text-sm" />
                                                    </div>
                                                )}

                                                <div
                                                    className="pr-8 cursor-pointer"
                                                    onClick={() => handleSelectAndClose(address)}
                                                >
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <FiHome className="text-[#ff5252] text-lg" />
                                                        {address.is_default && (
                                                            <span className="text-xs font-medium px-2 py-1 rounded-full bg-green-100 text-green-600">
                                                                Mặc định
                                                            </span>
                                                        )}
                                                    </div>
                                                    <p className="font-semibold text-gray-800 mb-1">{address.line}</p>
                                                    <p className="text-gray-600 text-sm mb-1">
                                                        {address.ward_info?.name}, {address.province_info?.name}
                                                    </p>
                                                    <p className="text-gray-600 text-sm">
                                                        {address.country}
                                                    </p>
                                                </div>

                                                <div className="flex gap-2 mt-3 pt-3 border-t border-gray-200">
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            handleEditClick(address);
                                                        }}
                                                        className="flex items-center gap-1 px-3 py-1.5 text-sm bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 transition-colors cursor-pointer"
                                                    >
                                                        <FiEdit2 className="text-xs" />
                                                        Sửa
                                                    </button>
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            handleDeleteAddress(address.id);
                                                        }}
                                                        disabled={deletingId === address.id}
                                                        className="flex items-center gap-1 px-3 py-1.5 text-sm bg-red-50 text-red-600 rounded-md hover:bg-red-100 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                                                    >
                                                        {deletingId === address.id ? (
                                                            <>
                                                                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-red-600"></div>
                                                                Đang xóa...
                                                            </>
                                                        ) : (
                                                            <>
                                                                <FiTrash2 className="text-xs" />
                                                                Xóa
                                                            </>
                                                        )}
                                                    </button>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    ) : (
                        <div>
                            <button
                                onClick={resetForm}
                                className="flex items-center gap-2 text-gray-600 hover:text-[#ff5252] mb-4 cursor-pointer transition-colors"
                            >
                                <FiArrowLeft className="text-sm" />
                                Quay lại danh sách
                            </button>

                            <form onSubmit={isEditMode ? handleUpdateAddress : handleCreateAddress} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Số nhà, tên đường <span className="text-red-500">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.line}
                                        onChange={(e) => handleFormChange('line', e.target.value)}
                                        placeholder="Ví dụ: 123 Nguyễn Văn Linh"
                                        className={`w-full px-4 py-2.5 border rounded-lg focus:outline-none transition-all ${errors.line
                                            ? 'border-red-500 focus:border-red-500 focus:ring-2 focus:ring-red-200'
                                            : 'border-gray-300 focus:border-[#ff5252] focus:ring-2 focus:ring-[#ff5252]/20'
                                            }`}
                                    />
                                    {errors.line && (
                                        <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
                                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                            </svg>
                                            {errors.line}
                                        </p>
                                    )}
                                </div>

                                <div className="province-searchable-select relative">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Tỉnh/Thành phố <span className="text-red-500">*</span>
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="text"
                                            value={provinceSearchTerm}
                                            onChange={(e) => handleProvinceSearch(e.target.value)}
                                            onFocus={() => setShowProvinceDropdown(true)}
                                            placeholder="Tìm kiếm tỉnh/thành phố..."
                                            disabled={loadingProvinces}
                                            className={`w-full px-4 py-2.5 border rounded-lg focus:outline-none transition-all pr-10 ${errors.province_id
                                                ? 'border-red-500 focus:border-red-500 focus:ring-2 focus:ring-red-200'
                                                : 'border-gray-300 focus:border-[#ff5252] focus:ring-2 focus:ring-[#ff5252]/20'
                                                }`}
                                        />
                                        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                                            {loadingProvinces ? (
                                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-[#ff5252]"></div>
                                            ) : (
                                                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                                </svg>
                                            )}
                                        </div>
                                    </div>

                                    {showProvinceDropdown && !loadingProvinces && (
                                        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                                            {provinces.length > 0 ? (
                                                provinces.map((province) => (
                                                    <div
                                                        key={province.id}
                                                        onClick={() => handleSelectProvince(province)}
                                                        className={`px-4 py-2.5 cursor-pointer hover:bg-[#ff5252]/10 transition-colors ${formData.province_id === province.id ? 'bg-[#ff5252]/20 font-medium' : ''
                                                            }`}
                                                    >
                                                        <div className="flex items-center justify-between">
                                                            <span>{province.name}</span>
                                                            {formData.province_id === province.id && (
                                                                <FiCheck className="text-[#ff5252]" />
                                                            )}
                                                        </div>
                                                    </div>
                                                ))
                                            ) : (
                                                <div className="px-4 py-3 text-gray-500 text-center">
                                                    {provinceSearchTerm ? 'Không tìm thấy kết quả' : 'Không có dữ liệu'}
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {errors.province_id && (
                                        <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
                                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                            </svg>
                                            {errors.province_id}
                                        </p>
                                    )}
                                </div>

                                <div className="ward-searchable-select relative">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Phường/Xã <span className="text-red-500">*</span>
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="text"
                                            value={wardSearchTerm}
                                            onChange={(e) => handleWardSearch(e.target.value)}
                                            onFocus={() => setShowWardDropdown(true)}
                                            placeholder={!formData.province_id ? "Vui lòng chọn tỉnh/thành phố trước" : "Tìm kiếm phường/xã..."}
                                            disabled={!formData.province_id || loadingWards}
                                            className={`w-full px-4 py-2.5 border rounded-lg focus:outline-none transition-all pr-10 disabled:bg-gray-100 disabled:cursor-not-allowed ${errors.ward_id
                                                ? 'border-red-500 focus:border-red-500 focus:ring-2 focus:ring-red-200'
                                                : 'border-gray-300 focus:border-[#ff5252] focus:ring-2 focus:ring-[#ff5252]/20'
                                                }`}
                                        />
                                        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                                            {loadingWards ? (
                                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-[#ff5252]"></div>
                                            ) : (
                                                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                                </svg>
                                            )}
                                        </div>
                                    </div>

                                    {showWardDropdown && !loadingWards && formData.province_id && (
                                        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                                            {wards.length > 0 ? (
                                                wards.map((ward) => (
                                                    <div
                                                        key={ward.id}
                                                        onClick={() => handleSelectWard(ward)}
                                                        className={`px-4 py-2.5 cursor-pointer hover:bg-[#ff5252]/10 transition-colors ${formData.ward_id === ward.id ? 'bg-[#ff5252]/20 font-medium' : ''
                                                            }`}
                                                    >
                                                        <div className="flex items-center justify-between">
                                                            <span>{ward.name}</span>
                                                            {formData.ward_id === ward.id && (
                                                                <FiCheck className="text-[#ff5252]" />
                                                            )}
                                                        </div>
                                                    </div>
                                                ))
                                            ) : (
                                                <div className="px-4 py-3 text-gray-500 text-center">
                                                    {wardSearchTerm ? 'Không tìm thấy kết quả' : 'Không có dữ liệu'}
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {errors.ward_id && (
                                        <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
                                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                            </svg>
                                            {errors.ward_id}
                                        </p>
                                    )}
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Quốc gia
                                    </label>
                                    <input
                                        type="text"
                                        value="Việt Nam"
                                        disabled
                                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg bg-gray-100 text-gray-600 cursor-not-allowed"
                                    />
                                </div>

                                <div className="flex gap-3 pt-4 border-t border-gray-200">
                                    <button
                                        type="button"
                                        onClick={resetForm}
                                        className="flex-1 px-4 py-2.5 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors cursor-pointer"
                                    >
                                        Hủy
                                    </button>
                                    <button
                                        type="submit"
                                        disabled={submitting}
                                        className="flex-1 px-4 py-2.5 bg-gradient-to-r from-[#ff5252] to-[#ff8a80] text-white rounded-lg font-medium hover:shadow-lg transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {submitting ? (
                                            <div className="flex items-center justify-center gap-2">
                                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                                {isEditMode ? 'Đang cập nhật...' : 'Đang tạo...'}
                                            </div>
                                        ) : (
                                            isEditMode ? 'Cập nhật địa chỉ' : 'Tạo địa chỉ'
                                        )}
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AddressManager;