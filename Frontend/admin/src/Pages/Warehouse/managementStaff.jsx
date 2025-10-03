import React, { useState, useEffect } from 'react';
import { MdClose, MdEdit, MdDelete, MdPeople } from 'react-icons/md';
import { deleteDataApi, getDataApi, putDataApi } from '../../utils/api';
import UpdateRoleModal from './updateRole';

const WarehouseStaffModal = ({ open, onClose, warehouse, context }) => {
    const [staffs, setStaffs] = useState([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(false);
    const [selectedStaffIds, setSelectedStaffIds] = useState([]);
    const [page, setPage] = useState(0);
    const limit = 10;
    const [showUpdateRoleModal, setShowUpdateRoleModal] = useState(false);
    const [selectedStaff, setSelectedStaff] = useState(null);
    const [showConfirmModal, setShowConfirmModal] = useState(false);
    const [confirmAction, setConfirmAction] = useState(null);

    useEffect(() => {
        if (open && warehouse) {
            fetchStaffs();
        }
    }, [open, warehouse, page]);

    const fetchStaffs = async () => {
        setLoading(true);
        try {
            const skip = page * limit;
            const response = await getDataApi(
                `/admin/user/warehouse/${warehouse.id}/staffs?skip=${skip}&limit=${limit}`
            );

            if (response.success === true) {
                setStaffs(response.data.data || []);
                setTotal(response.data.total || 0);
            } else {
                context.openAlertBox("error", "Lỗi khi tải danh sách nhân viên");
            }
        } catch (error) {
            console.error('Error fetching warehouse staffs:', error);
            context.openAlertBox("error", "Lỗi khi tải danh sách nhân viên");
        } finally {
            setLoading(false);
        }
    };

    const handleStaffSelection = (staffId) => {
        setSelectedStaffIds(prev => {
            if (prev.includes(staffId)) {
                return prev.filter(id => id !== staffId);
            } else {
                return [...prev, staffId];
            }
        });
    };

    const handleSelectAll = (e) => {
        if (e.target.checked) {
            setSelectedStaffIds(staffs.map(staff => staff.id));
        } else {
            setSelectedStaffIds([]);
        }
    };

    const handleRemoveStaff = (staffId) => {
        setConfirmAction({
            type: 'single',
            staffId: staffId,
            message: 'Bạn có chắc muốn gỡ nhân viên này khỏi kho?'
        });
        setShowConfirmModal(true);
    };

    const handleRemoveMultipleStaffs = () => {
        setConfirmAction({
            type: 'multiple',
            staffIds: selectedStaffIds,
            message: `Bạn có chắc muốn gỡ ${selectedStaffIds.length} nhân viên khỏi kho?`
        });
        setShowConfirmModal(true);
    };

    const executeRemoveAction = async () => {
        setShowConfirmModal(false);

        try {
            let response;

            if (confirmAction.type === 'single') {
                response = await deleteDataApi(
                    `/admin/warehouse/${warehouse.id}/staff/${confirmAction.staffId}`
                );
            } else {
                response = await putDataApi(
                    `/admin/warehouse/${warehouse.id}/staff/batch`,
                    { user_ids: confirmAction.staffIds }
                );
            }

            if (response.success || response.message) {
                const successMessage = confirmAction.type === 'single'
                    ? 'Gỡ nhân viên khỏi kho thành công'
                    : `Gỡ ${confirmAction.staffIds.length} nhân viên khỏi kho thành công`;

                context.openAlertBox('success', successMessage);
                setSelectedStaffIds([]);
                fetchStaffs();
            } else {
                context.openAlertBox('error', response?.data?.detail?.message || 'Gỡ nhân viên thất bại');
            }
        } catch (error) {
            console.error('Error removing staff:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi gỡ nhân viên');
        } finally {
            setConfirmAction(null);
        }
    };

    const handleUpdateRole = (staff) => {
        setSelectedStaff(staff);
        setShowUpdateRoleModal(true);
    };

    const handleUpdateRoleSuccess = () => {
        fetchStaffs();
    };

    const getRoleLabel = (role) => {
        const roles = {
            'warehouse_keeper': 'Thủ kho',
            'stock_clerk': 'Nhân viên kho',
            'picker': 'Nhân viên lấy hàng',
            'packer': 'Nhân viên đóng gói'
        };
        return roles[role] || role;
    };

    const getStatusBadge = (status) => {
        const statuses = {
            'active': { label: 'Đang làm', color: 'bg-green-100 text-green-800' },
            'inactive': { label: 'Tạm nghỉ', color: 'bg-gray-100 text-gray-800' },
            'on_leave': { label: 'Nghỉ phép', color: 'bg-yellow-100 text-yellow-800' }
        };
        return statuses[status] || { label: status, color: 'bg-gray-100 text-gray-800' };
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleDateString('vi-VN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch {
            return 'N/A';
        }
    };

    if (!open) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}>
            <div className="bg-white rounded-lg shadow-xl w-full max-w-5xl mx-4 max-h-[90vh] flex flex-col">
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <div className="flex items-center gap-3">
                        <MdPeople className="text-3xl text-blue-600" />
                        <div>
                            <h3 className="text-xl font-semibold text-gray-800">
                                Nhân viên trong kho
                            </h3>
                            <p className="text-sm text-gray-500 mt-1">
                                {warehouse?.name} - Mã: {warehouse?.code}
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 transition-colors cursor-pointer"
                    >
                        <MdClose className="text-2xl" />
                    </button>
                </div>

                {selectedStaffIds.length > 0 && (
                    <div className="px-6 py-3 bg-blue-50 border-b border-blue-200 flex items-center justify-between">
                        <span className="text-sm font-medium text-blue-800">
                            Đã chọn {selectedStaffIds.length} nhân viên
                        </span>
                        <button
                            onClick={handleRemoveMultipleStaffs}
                            className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors flex items-center gap-2 text-sm cursor-pointer"
                        >
                            <MdDelete /> Xóa nhiều
                        </button>
                    </div>
                )}

                <div className="flex-1 overflow-y-auto p-6">
                    {loading ? (
                        <div className="flex justify-center items-center h-64">
                            <div className="text-lg text-gray-600">Đang tải...</div>
                        </div>
                    ) : staffs.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-64 text-gray-500">
                            <MdPeople className="text-6xl mb-4 text-gray-300" />
                            <p className="text-lg">Chưa có nhân viên nào trong kho này</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-md border border-gray-200">
                                <input
                                    type="checkbox"
                                    checked={selectedStaffIds.length === staffs.length && staffs.length > 0}
                                    onChange={handleSelectAll}
                                    className="w-4 h-4 text-blue-600 cursor-pointer"
                                />
                                <span className="font-medium text-gray-700">Chọn tất cả</span>
                            </div>

                            {staffs.map((staff) => (
                                <div
                                    key={staff.id}
                                    className={`border rounded-lg p-4 transition-all ${selectedStaffIds.includes(staff.id)
                                            ? 'bg-blue-50 border-blue-300'
                                            : 'bg-white border-gray-200 hover:border-gray-300'
                                        }`}
                                >
                                    <div className="flex items-start gap-4">
                                        <input
                                            type="checkbox"
                                            checked={selectedStaffIds.includes(staff.id)}
                                            onChange={() => handleStaffSelection(staff.id)}
                                            className="w-5 h-5 text-blue-600 mt-1 cursor-pointer"
                                        />

                                        <div className="flex-1">
                                            <div className="flex items-start justify-between mb-3">
                                                <div>
                                                    <h4 className="text-lg font-semibold text-gray-800">
                                                        {staff.first_name} {staff.last_name}
                                                    </h4>
                                                    <div className="flex items-center gap-2 mt-1">
                                                        <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                            {getRoleLabel(staff.warehouse_role)}
                                                        </span>
                                                        {staff.staff_status && (
                                                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(staff.staff_status).color
                                                                }`}>
                                                                {getStatusBadge(staff.staff_status).label}
                                                            </span>
                                                        )}
                                                        {staff.is_verified && (
                                                            <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                                                ✓ Đã xác thực
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>

                                                <div className="flex items-center gap-2">
                                                    <button
                                                        onClick={() => handleUpdateRole(staff)}
                                                        className="px-3 py-1.5 bg-yellow-500 text-white rounded-md hover:bg-yellow-600 transition-colors flex items-center gap-1 text-sm cursor-pointer"
                                                        title="Cập nhật vai trò"
                                                    >
                                                        <MdEdit className="text-base" /> Đổi vai trò
                                                    </button>
                                                    <button
                                                        onClick={() => handleRemoveStaff(staff.id)}
                                                        className="px-3 py-1.5 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors flex items-center gap-1 text-sm cursor-pointer"
                                                        title="Xóa khỏi kho"
                                                    >
                                                        <MdDelete className="text-base" /> Xóa
                                                    </button>
                                                </div>
                                            </div>

                                            <div className="grid grid-cols-2 gap-3 text-sm">
                                                <div>
                                                    <span className="text-gray-500">Email:</span>
                                                    <span className="ml-2 text-gray-700">{staff.email}</span>
                                                </div>
                                                <div>
                                                    <span className="text-gray-500">SĐT:</span>
                                                    <span className="ml-2 text-gray-700">{staff.phone || 'N/A'}</span>
                                                </div>
                                                <div>
                                                    <span className="text-gray-500">Ngày tham gia:</span>
                                                    <span className="ml-2 text-gray-700">{formatDate(staff.created_at)}</span>
                                                </div>
                                                <div>
                                                    <span className="text-gray-500">Cập nhật:</span>
                                                    <span className="ml-2 text-gray-700">{formatDate(staff.updated_at)}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="p-6 border-t border-gray-200 bg-gray-50">
                    <div className="flex items-center justify-between">
                        <div className="text-sm text-gray-600">
                            Hiển thị <strong>{staffs.length}</strong> / <strong>{total}</strong> nhân viên
                        </div>
                        <div className="flex gap-3">
                            {total > (page + 1) * limit && (
                                <button
                                    onClick={() => setPage(prev => prev + 1)}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors cursor-pointer"
                                >
                                    Xem thêm
                                </button>
                            )}
                            <button
                                onClick={onClose}
                                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors cursor-pointer"
                            >
                                Đóng
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {showConfirmModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]"
                    style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}>
                    <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
                        <h3 className="text-lg font-semibold text-gray-800 mb-4">Xác nhận</h3>
                        <p className="text-gray-600 mb-6">{confirmAction?.message}</p>
                        <div className="flex justify-end gap-3">
                            <button
                                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors cursor-pointer"
                                onClick={() => {
                                    setShowConfirmModal(false);
                                    setConfirmAction(null);
                                }}
                            >
                                Hủy
                            </button>
                            <button
                                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors cursor-pointer"
                                onClick={executeRemoveAction}
                            >
                                Xác nhận
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <UpdateRoleModal
                open={showUpdateRoleModal}
                onClose={() => {
                    setShowUpdateRoleModal(false);
                    setSelectedStaff(null);
                }}
                staff={selectedStaff}
                warehouse={warehouse}
                onSuccess={handleUpdateRoleSuccess}
                context={context}
            />
        </div>
    );
};

export default WarehouseStaffModal;