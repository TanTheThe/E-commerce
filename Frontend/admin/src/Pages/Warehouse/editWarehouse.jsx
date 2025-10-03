import React, { useState, useEffect, useRef, useContext } from 'react';
import { IoMdClose } from "react-icons/io";
import { IoClose, IoCopyOutline } from "react-icons/io5";
import { getDataApi, putDataApi } from '../../utils/api';

const EditWarehouseModal = ({ open, onClose, onWarehouseUpdated, context, warehouse }) => {
    const [formData, setFormData] = useState({
        name: '',
        address: '',
        phone: '',
        email: '',
        manager_id: '',
    });
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});
    const [staffs, setStaffs] = useState([]);
    const [loadingStaffs, setLoadingStaffs] = useState(false);

    const fetchStaffs = async () => {
        setLoadingStaffs(true);
        try {
            const response = await getDataApi('/admin/user/all-staffs?limit=100&staff_status=active');
            if (response.success) {
                setStaffs(response.data.data);
            }
        } catch (error) {
            console.error('Error fetching staffs:', error);
            context.openAlertBox('error', 'Lỗi khi tải danh sách nhân viên');
        } finally {
            setLoadingStaffs(false);
        }
    };

    const fetchWarehouseDetail = async () => {
        try {
            const response = await getDataApi(`/admin/warehouse/${warehouse.id}`);
            if (response.success) {
                setFormData({
                    name: response.data.name || '',
                    address: response.data.address || '',
                    phone: response.data.phone || '',
                    email: response.data.email || '',
                    manager_id: response.data.manager_id || '',
                });
            }
        } catch (error) {
            console.error('Error fetching warehouse detail:', error);
        }
    };

    useEffect(() => {
        if (open && warehouse) {
            fetchStaffs();
            fetchWarehouseDetail();
        }
    }, [open, warehouse]);

    const validateForm = () => {
        const newErrors = {};

        if (!formData.name.trim()) {
            newErrors.name = 'Tên kho là bắt buộc';
        } else if (formData.name.length > 255) {
            newErrors.name = 'Tên kho không được quá 255 ký tự';
        }

        if (!formData.address.trim()) {
            newErrors.address = 'Địa chỉ là bắt buộc';
        }

        if (formData.phone) {
            const phoneRegex = /^(09\d{8}|02\d{9})$/;
            if (!phoneRegex.test(formData.phone)) {
                newErrors.phone = 'Số điện thoại phải là 10 số (bắt đầu 09) hoặc 11 số (bắt đầu 02)';
            }
        }

        if (formData.email && !/^[\w\.-]+@[\w\.-]+\.\w+$/.test(formData.email)) {
            newErrors.email = 'Email không hợp lệ';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setLoading(true);
        try {
            const submitData = {
                ...formData,
                phone: formData.phone?.trim() || null,
                email: formData.email?.trim() || null,
                manager_id: formData.manager_id === '' ? null : formData.manager_id
            };

            const response = await putDataApi(`/admin/warehouse/${warehouse.id}`, submitData);

            if (response.success || response.message) {
                context.openAlertBox('success', 'Cập nhật kho thành công');
                onWarehouseUpdated();
                handleClose();
            } else {
                context.openAlertBox('error', response?.data?.detail?.message || 'Cập nhật kho thất bại');
            }
        } catch (error) {
            console.error('Error updating warehouse:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi cập nhật kho');
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setErrors({});
        onClose();
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    if (!open) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}>
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                    <h2 className="text-xl font-bold text-gray-800">Cập nhật kho</h2>
                    <button
                        onClick={handleClose}
                        className="text-gray-400 hover:text-gray-600 transition-colors cursor-pointer"
                    >
                        <IoClose className="text-2xl" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6">
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Tên kho <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.name ? 'border-red-500' : 'border-gray-300'
                                    }`}
                                placeholder="Nhập tên kho"
                            />
                            {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Địa chỉ <span className="text-red-500">*</span>
                            </label>
                            <textarea
                                name="address"
                                value={formData.address}
                                onChange={handleChange}
                                rows="3"
                                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.address ? 'border-red-500' : 'border-gray-300'
                                    }`}
                                placeholder="Nhập địa chỉ kho"
                            />
                            {errors.address && <p className="text-red-500 text-xs mt-1">{errors.address}</p>}
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Quản lý kho
                            </label>
                            <select
                                name="manager_id"
                                value={formData.manager_id}
                                onChange={handleChange}
                                disabled={loadingStaffs}
                                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.manager_id ? 'border-red-500' : 'border-gray-300'
                                    }`}
                            >
                                <option value="">-- Không chọn quản lý --</option>
                                {staffs.map(staff => (
                                    <option key={staff.id} value={staff.id}>
                                        {staff.first_name} {staff.last_name} ({staff.email})
                                    </option>
                                ))}
                            </select>
                            {loadingStaffs && (
                                <p className="text-gray-500 text-xs mt-1">Đang tải danh sách nhân viên...</p>
                            )}
                            {errors.manager_id && (
                                <p className="text-red-500 text-xs mt-1">{errors.manager_id}</p>
                            )}
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Số điện thoại
                                </label>
                                <input
                                    type="text"
                                    name="phone"
                                    value={formData.phone}
                                    onChange={handleChange}
                                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.phone ? 'border-red-500' : 'border-gray-300'
                                        }`}
                                    placeholder="VD: 0912345678 hoặc 02812345678"
                                />
                                {errors.phone && <p className="text-red-500 text-xs mt-1">{errors.phone}</p>}
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Email
                                </label>
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.email ? 'border-red-500' : 'border-gray-300'
                                        }`}
                                    placeholder="email@example.com"
                                />
                                {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center justify-end gap-3 mt-6 pt-4 border-t border-gray-200">
                        <button
                            type="button"
                            onClick={handleClose}
                            className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors cursor-pointer"
                        >
                            Hủy
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-300 cursor-pointer"
                        >
                            {loading ? 'Đang cập nhật...' : 'Cập nhật'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default EditWarehouseModal;