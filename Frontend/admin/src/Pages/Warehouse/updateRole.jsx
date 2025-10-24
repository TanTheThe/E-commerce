import React, { useState, useEffect } from 'react';
import { MdClose } from 'react-icons/md';
import { putDataApi } from '../../utils/api';

const UpdateRoleModal = ({ open, onClose, staff, warehouse, onSuccess, context }) => {
    const [role, setRole] = useState('');
    const [loading, setLoading] = useState(false);

    const roles = [
        { value: 'warehouse_keeper', label: 'Thủ kho' },
        { value: 'stock_clerk', label: 'Nhân viên kho' },
        { value: 'picker', label: 'Nhân viên lấy hàng' },
        { value: 'packer', label: 'Nhân viên đóng gói' }
    ];

    useEffect(() => {
        if (staff && staff.warehouse_role) {
            setRole(staff.warehouse_role);
        }
    }, [staff]);

    const getRoleLabel = (roleValue) => {
        const roleObj = roles.find(r => r.value === roleValue);
        return roleObj ? roleObj.label : roleValue;
    };

    const handleSubmit = async () => {
        if (!role) {
            context.openAlertBox('warning', 'Vui lòng chọn vai trò');
            return;
        }

        if (!warehouse || !warehouse.id) {
            context.openAlertBox('error', 'Không thể cập nhật: Thiếu thông tin kho');
            return;
        }

        setLoading(true);
        try {
            const response = await putDataApi(
                `/admin/warehouse/${warehouse.id}/staff/${staff.id}/role`,
                { warehouse_role: role }
            );

            if (response.success) {
                context.openAlertBox('success', response.message || 'Cập nhật vai trò thành công');
                onSuccess();
                onClose();
            } else {
                context.openAlertBox('error', response?.data?.detail?.message || 'Cập nhật vai trò thất bại');
            }
        } catch (error) {
            console.error('Error updating role:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi cập nhật vai trò');
        } finally {
            setLoading(false);
        }
    };

    if (!open) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}>
            <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-800">Cập nhật vai trò nhân viên</h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 transition-colors cursor-pointer"
                        disabled={loading}
                    >
                        <MdClose className="text-2xl" />
                    </button>
                </div>

                <div className="mb-4 bg-gray-50 p-4 rounded-md">
                    <p className="text-sm text-gray-600 mb-2">
                        <span className="font-medium text-gray-700">Nhân viên:</span>{' '}
                        <span className="font-semibold text-gray-800">
                            {staff?.first_name} {staff?.last_name}
                        </span>
                    </p>
                    <p className="text-sm text-gray-600 mb-2">
                        <span className="font-medium text-gray-700">Email:</span>{' '}
                        <span className="text-gray-800">{staff?.email}</span>
                    </p>
                    <p className="text-sm text-gray-600 mb-2">
                        <span className="font-medium text-gray-700">Kho:</span>{' '}
                        <span className="font-semibold text-gray-800">
                            {warehouse?.name} ({warehouse?.code})
                        </span>
                    </p>
                    <p className="text-sm text-gray-600">
                        <span className="font-medium text-gray-700">Vai trò hiện tại:</span>{' '}
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {getRoleLabel(staff?.warehouse_role)}
                        </span>
                    </p>
                </div>

                <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Chọn vai trò mới <span className="text-red-500">*</span>
                    </label>
                    <select
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                        disabled={loading}
                    >
                        {roles.map((r) => (
                            <option key={r.value} value={r.value}>
                                {r.label}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="flex gap-3 justify-end">
                    <button
                        onClick={onClose}
                        disabled={loading}
                        className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Hủy
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={loading}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Đang cập nhật...' : 'Cập nhật'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default UpdateRoleModal;