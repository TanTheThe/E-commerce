import React, { useState, useEffect, useCallback, useContext } from 'react';
import { MdAdd, MdEdit, MdToggleOn, MdToggleOff, MdStar, MdInventory, MdPersonAdd, MdPeople } from 'react-icons/md';
import { FaWarehouse, FaPhone, FaEnvelope, FaMapMarkerAlt, FaUser } from 'react-icons/fa';
import AddWarehouseModal from './addWarehouse';
import EditWarehouseModal from './editWarehouse';
import { MyContext } from "../../App";
import { getDataApi, postDataApi, putDataApi } from '../../utils/api';
import WarehouseStaffModal from './managementStaff';
import WarehouseStock from './warehouseStock/warehouseStock';
import { AppBar, Dialog, IconButton, Slide, Toolbar, Typography } from '@mui/material';
import { IoMdClose } from 'react-icons/io';


const Transition = React.forwardRef(function Transition(props, ref) {
    return <Slide direction="up" ref={ref} {...props} />;
});

const Warehouse = () => {
    const [searchVal, setSearchVal] = useState('');
    const [warehouses, setWarehouses] = useState([]);
    const [totalWarehouses, setTotalWarehouses] = useState(0);
    const [loading, setLoading] = useState(false);
    const [isActiveFilter, setIsActiveFilter] = useState(null);
    const [sortBy, setSortBy] = useState('created_desc');
    const [page, setPage] = useState(0);
    const [rowsPerPage] = useState(12);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [showUpdateModal, setShowUpdateModal] = useState(false);
    const [selectedWarehouse, setSelectedWarehouse] = useState(null);
    const [showConfirmModal, setShowConfirmModal] = useState(false);
    const [confirmAction, setConfirmAction] = useState(null);

    const [showAssignStaffModal, setShowAssignStaffModal] = useState(false);
    const [selectedWarehouseForAssign, setSelectedWarehouseForAssign] = useState(null);
    const [availableStaffs, setAvailableStaffs] = useState([]);
    const [selectedRole, setSelectedRole] = useState('');
    const [selectedStaffIds, setSelectedStaffIds] = useState([]);
    const [loadingStaffs, setLoadingStaffs] = useState(false);

    const [showStaffModal, setShowStaffModal] = useState(false);
    const [selectedWarehouseForStaff, setSelectedWarehouseForStaff] = useState(null);

    const [showStockModal, setShowStockModal] = useState(false);
    const [selectedWarehouseForStock, setSelectedWarehouseForStock] = useState(null);

    const context = useContext(MyContext);

    const fetchWarehouses = async () => {
        setLoading(true);
        try {
            const skip = page * rowsPerPage;
            const limit = rowsPerPage;

            const queryParams = new URLSearchParams({
                skip: skip.toString(),
                limit: limit.toString(),
                sort_by: sortBy
            });

            if (searchVal) queryParams.append('search', searchVal);
            if (isActiveFilter !== null) queryParams.append('is_active', isActiveFilter.toString());

            const response = await getDataApi(`/admin/warehouse/all?${queryParams.toString()}`);

            console.log(response);

            if (response.success === true) {
                setWarehouses(response.data.data || []);
                setTotalWarehouses(response.data.total || 0);
            } else {
                context.openAlertBox("error", response.data.detail.message);
            }
        } catch (error) {
            console.error('Error fetching warehouses:', error);
            context.openAlertBox("error", "Lỗi khi tải danh sách kho");
        } finally {
            setLoading(false);
        }
    };

    const fetchAvailableStaffs = async () => {
        setLoadingStaffs(true);
        try {
            const response = await getDataApi('/admin/user/available-staffs?skip=0&limit=100');

            if (response.success === true) {
                setAvailableStaffs(response.data.data || []);
            } else {
                context.openAlertBox("error", "Lỗi khi tải danh sách nhân viên");
            }
        } catch (error) {
            console.error('Error fetching available staffs:', error);
            context.openAlertBox("error", "Lỗi khi tải danh sách nhân viên");
        } finally {
            setLoadingStaffs(false);
        }
    };

    const handleOpenAssignStaff = (warehouse) => {
        setSelectedWarehouseForAssign(warehouse);
        setSelectedRole('');
        setSelectedStaffIds([]);
        setShowAssignStaffModal(true);
        fetchAvailableStaffs();
    };

    const handleAssignStaff = async () => {
        if (!selectedRole) {
            context.openAlertBox("error", "Vui lòng chọn vai trò");
            return;
        }

        if (selectedStaffIds.length === 0) {
            context.openAlertBox("error", "Vui lòng chọn ít nhất một nhân viên");
            return;
        }

        try {
            const requestData = {
                staff_list: selectedStaffIds.map(staffId => ({
                    user_id: staffId,
                    warehouse_role: selectedRole
                }))
            };

            const response = await postDataApi(
                `/admin/warehouse/${selectedWarehouseForAssign.id}/assign-staff/batch`,
                requestData
            );

            if (response.success || response.message) {
                context.openAlertBox('success', `Gán ${selectedStaffIds.length} nhân viên thành công`);
                setShowAssignStaffModal(false);
                setSelectedWarehouseForAssign(null);
                setSelectedRole('');
                setSelectedStaffIds([]);
                fetchWarehouses();
            } else {
                context.openAlertBox('error', response?.data?.detail?.message || 'Gán nhân viên thất bại');
            }
        } catch (error) {
            console.error('Error assigning staff:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi gán nhân viên');
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

    const handleConfirm = (action, warehouseId, currentStatus = null) => {
        setConfirmAction({
            action,
            warehouseId,
            currentStatus,
            message: action === 'setDefault'
                ? 'Bạn có chắc muốn đặt kho này làm mặc định?'
                : `Bạn có chắc muốn ${currentStatus ? 'tắt' : 'bật'} kho này?`
        });
        setShowConfirmModal(true);
    };

    useEffect(() => {
        fetchWarehouses();
    }, [page, rowsPerPage, searchVal, isActiveFilter, sortBy]);

    const debounce = (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };

    const debouncedSearch = useCallback(
        debounce((searchTerm) => {
            setSearchVal(searchTerm);
            setPage(0);
        }, 500),
        []
    );

    useEffect(() => {
        setPage(0);
    }, [searchVal, isActiveFilter, sortBy]);

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

    const executeConfirmAction = async () => {
        if (!confirmAction) return;

        setShowConfirmModal(false);

        if (confirmAction.action === 'setDefault') {
            try {
                const response = await postDataApi(`/admin/warehouse/${confirmAction.warehouseId}/set-default`, {});

                if (response.success || response.message) {
                    context.openAlertBox('success', 'Đặt kho mặc định thành công');
                    fetchWarehouses();
                } else {
                    context.openAlertBox('error', response?.data?.detail?.message || 'Đặt kho mặc định thất bại');
                }
            } catch (error) {
                console.error('Error setting default warehouse:', error);
                context.openAlertBox('error', 'Lỗi hệ thống khi đặt kho mặc định');
            }
        } else if (confirmAction.action === 'toggleStatus') {
            try {
                const response = await putDataApi(`/admin/warehouse/${confirmAction.warehouseId}/change-status`, {});

                if (response.success || response.message) {
                    context.openAlertBox('success', 'Cập nhật trạng thái thành công');
                    fetchWarehouses();
                } else {
                    context.openAlertBox('error', response?.data?.detail?.message || 'Cập nhật trạng thái thất bại');
                }
            } catch (error) {
                console.error('Error toggling warehouse status:', error);
                context.openAlertBox('error', 'Lỗi hệ thống khi cập nhật trạng thái');
            }
        }

        setConfirmAction(null);
    };


    const handleUpdateWarehouse = (warehouse) => {
        setSelectedWarehouse(warehouse);
        setShowUpdateModal(true);
    };

    const handleViewInventory = (warehouse) => {
        setSelectedWarehouseForStock(warehouse);
        setShowStockModal(true);
    };

    const handleViewStaffs = (warehouse) => {
        setSelectedWarehouseForStaff(warehouse);
        setShowStaffModal(true);
    };

    const handleLoadMore = () => {
        setPage(prev => prev + 1);
    };

    return (
        <div className="p-4 bg-gray-50 min-h-screen">
            <div className="flex items-center justify-between px-2 py-0 mt-3 mb-4">
                <h2 className="text-[24px] font-[700] text-gray-800">Quản lý kho</h2>

                <button
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center gap-2 transition-colors cursor-pointer"
                    onClick={() => setShowCreateModal(true)}
                >
                    <MdAdd className="text-[20px]" /> Tạo kho mới
                </button>
            </div>

            <div className="bg-white rounded-lg shadow-md">
                <div className="flex items-center w-full px-5 py-4 border-b border-gray-200 justify-between">
                    <div className="flex items-center gap-4 w-[60%]">
                        <h4 className="font-[600] text-[14px] text-gray-700">Bộ lọc:</h4>

                        <select
                            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={isActiveFilter === null ? '' : isActiveFilter.toString()}
                            onChange={(e) => {
                                const value = e.target.value;
                                setIsActiveFilter(value === '' ? null : value === 'true');
                            }}
                        >
                            <option value="">Tất cả trạng thái</option>
                            <option value="true">Đang hoạt động</option>
                            <option value="false">Không hoạt động</option>
                        </select>

                        <select
                            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value)}
                        >
                            <option value="created_desc">Mới nhất</option>
                            <option value="created_asc">Cũ nhất</option>
                        </select>
                    </div>

                    <div className="w-[30%]">
                        <input
                            type="text"
                            placeholder="Tìm kiếm kho..."
                            className="w-full px-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            onChange={(e) => debouncedSearch(e.target.value)}
                        />
                    </div>
                </div>

                {loading ? (
                    <div className="flex justify-center items-center h-64">
                        <div className="text-lg text-gray-600">Đang tải...</div>
                    </div>
                ) : (
                    <>
                        {warehouses.length === 0 ? (
                            <div className="flex justify-center items-center h-64 flex-col">
                                <FaWarehouse className="text-6xl text-gray-300 mb-4" />
                                <p className="text-gray-500 text-lg">Không có kho nào</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6">
                                {warehouses.map((warehouse) => (
                                    <div
                                        key={warehouse.id}
                                        className="warehouseItem shadow-lg rounded-md overflow-hidden border border-gray-200 flex items-stretch hover:shadow-xl transition-all duration-300"
                                    >
                                        <div className="iconWrapper w-[28%] bg-gradient-to-br from-blue-500 to-blue-600 flex flex-col items-center justify-center p-5 relative">
                                            <FaWarehouse className="text-white text-6xl mb-3" />

                                            {warehouse.is_default && (
                                                <span className="absolute top-3 right-3 bg-yellow-400 text-white rounded-full p-2 shadow-lg" title="Kho mặc định">
                                                    <MdStar className="text-[18px]" />
                                                </span>
                                            )}

                                            <span className={`text-[12px] font-[600] px-3 py-1 rounded-full mt-3 ${warehouse.is_active
                                                ? 'bg-green-400 text-white'
                                                : 'bg-red-400 text-white'
                                                }`}>
                                                {warehouse.is_active ? 'Hoạt động' : 'Tạm dừng'}
                                            </span>
                                        </div>

                                        <div className="info p-5 w-[72%] flex flex-col justify-between">
                                            <div>
                                                <div className="flex items-start justify-between mb-4">
                                                    <div className="flex-1">
                                                        <h3 className="text-[20px] font-[700] mb-2 text-gray-800">
                                                            {warehouse.name}
                                                        </h3>
                                                        <span className="text-[13px] text-gray-600 font-[600] bg-gray-100 px-3 py-1 rounded-full">
                                                            Mã: {warehouse.code}
                                                        </span>
                                                    </div>
                                                </div>

                                                <div className="flex flex-col gap-3 mb-4">
                                                    <div className="flex items-start gap-3 text-[14px] text-gray-600">
                                                        <FaMapMarkerAlt className="mt-1 text-blue-500 flex-shrink-0" />
                                                        <span className="line-clamp-2">{warehouse.address || 'Chưa có địa chỉ'}</span>
                                                    </div>

                                                    <div className="flex items-center gap-3 text-[14px] text-gray-600">
                                                        <FaUser className="text-blue-500 flex-shrink-0" />
                                                        <span>Quản lý: <strong>{warehouse.manager_name || 'Chưa có thông tin'}</strong></span>
                                                    </div>

                                                    <div className="flex items-center gap-3 text-[14px] text-gray-600">
                                                        <FaPhone className="text-blue-500 flex-shrink-0" />
                                                        <span>{warehouse.phone || 'Chưa có số điện thoại'}</span>
                                                    </div>

                                                    <div className="flex items-center gap-3 text-[14px] text-gray-600">
                                                        <FaEnvelope className="text-blue-500 flex-shrink-0" />
                                                        <span className="truncate">{warehouse.email || 'Chưa có email'}</span>
                                                    </div>
                                                </div>

                                                <div className="text-[12px] text-gray-400 mb-4 pt-3 border-t border-gray-200">
                                                    <span>Tạo lúc: {formatDate(warehouse.created_at)}</span>
                                                </div>
                                            </div>

                                            <div className="flex items-center gap-2 flex-wrap">
                                                <button
                                                    className="text-[13px] px-3 py-2 bg-green-500 text-white hover:bg-green-600 rounded-md transition-colors flex items-center gap-1 cursor-pointer"
                                                    onClick={() => handleOpenAssignStaff(warehouse)}
                                                >
                                                    <MdPersonAdd /> Thêm nhân viên
                                                </button>

                                                <button
                                                    className="text-[13px] px-3 py-2 bg-indigo-500 text-white hover:bg-indigo-600 rounded-md transition-colors flex items-center gap-1 cursor-pointer"
                                                    onClick={() => handleViewStaffs(warehouse)}
                                                >
                                                    <MdPeople /> Theo dõi nhân viên
                                                </button>

                                                <button
                                                    className="text-[13px] px-3 py-2 bg-purple-500 text-white hover:bg-purple-600 rounded-md transition-colors flex items-center gap-1 cursor-pointer"
                                                    onClick={() => handleViewInventory(warehouse)}
                                                >
                                                    <MdInventory /> Xem nội dung
                                                </button>

                                                {!warehouse.is_default && (
                                                    <button
                                                        className="text-[13px] px-3 py-2 bg-yellow-500 text-white hover:bg-yellow-600 rounded-md transition-colors flex items-center gap-1 cursor-pointer"
                                                        onClick={() => handleConfirm('setDefault', warehouse.id)}
                                                    >
                                                        <MdStar /> Đặt mặc định
                                                    </button>
                                                )}

                                                <button
                                                    className="text-[13px] px-3 py-2 bg-blue-500 text-white hover:bg-blue-600 rounded-md transition-colors flex items-center gap-1 cursor-pointer"
                                                    onClick={() => handleUpdateWarehouse(warehouse)}
                                                >
                                                    <MdEdit /> Cập nhật
                                                </button>

                                                <button
                                                    className={`text-[13px] px-3 py-2 rounded-md transition-colors flex items-center gap-1 cursor-pointer ${warehouse.is_active
                                                        ? 'bg-red-500 text-white hover:bg-red-600'
                                                        : 'bg-green-500 text-white hover:bg-green-600'
                                                        }`}
                                                    onClick={() => handleConfirm('toggleStatus', warehouse.id, warehouse.is_active)}
                                                >
                                                    {warehouse.is_active ? (
                                                        <>
                                                            <MdToggleOff /> Tắt
                                                        </>
                                                    ) : (
                                                        <>
                                                            <MdToggleOn /> Bật
                                                        </>
                                                    )}
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {totalWarehouses > warehouses.length && (
                            <div className="flex justify-center items-center py-6 border-t border-gray-200">
                                <button
                                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md transition-colors cursor-pointer"
                                    onClick={handleLoadMore}
                                    disabled={loading}
                                >
                                    Xem thêm ({warehouses.length}/{totalWarehouses})
                                </button>
                            </div>
                        )}

                        {warehouses.length > 0 && (
                            <div className="text-center text-gray-500 text-sm py-4 border-t border-gray-200 bg-gray-50">
                                Hiển thị <strong>{warehouses.length}</strong> / <strong>{totalWarehouses}</strong> kho
                            </div>
                        )}
                    </>
                )}
            </div>

            {showConfirmModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
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
                                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors cursor-pointer"
                                onClick={executeConfirmAction}
                            >
                                Xác nhận
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {showAssignStaffModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                    style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}>
                    <div className="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                        <h3 className="text-xl font-semibold text-gray-800 mb-4">
                            Thêm nhân viên vào kho: {selectedWarehouseForAssign?.name}
                        </h3>

                        <div className="mb-6">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Chọn vai trò <span className="text-red-500">*</span>
                            </label>
                            <select
                                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                value={selectedRole}
                                onChange={(e) => {
                                    setSelectedRole(e.target.value);
                                    setSelectedStaffIds([]);
                                }}
                            >
                                <option value="">-- Chọn vai trò --</option>
                                <option value="warehouse_keeper">Thủ kho</option>
                                <option value="stock_clerk">Nhân viên kho</option>
                                <option value="picker">Nhân viên lấy hàng</option>
                                <option value="packer">Nhân viên đóng gói</option>
                            </select>
                        </div>

                        {selectedRole && (
                            <div className="mb-6">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Chọn nhân viên (có thể chọn nhiều)
                                </label>

                                {loadingStaffs ? (
                                    <div className="text-center py-8 text-gray-500">Đang tải danh sách nhân viên...</div>
                                ) : availableStaffs.length === 0 ? (
                                    <div className="text-center py-8 text-gray-500">Không có nhân viên khả dụng</div>
                                ) : (
                                    <div className="border border-gray-300 rounded-md max-h-[300px] overflow-y-auto">
                                        {availableStaffs.map((staff) => (
                                            <div
                                                key={staff.id}
                                                className={`p-3 border-b border-gray-200 hover:bg-gray-50 cursor-pointer transition-colors ${selectedStaffIds.includes(staff.id) ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                                                    }`}
                                                onClick={() => handleStaffSelection(staff.id)}
                                            >
                                                <div className="flex items-center gap-3">
                                                    <input
                                                        type="checkbox"
                                                        checked={selectedStaffIds.includes(staff.id)}
                                                        onChange={() => handleStaffSelection(staff.id)}
                                                        className="w-4 h-4 text-blue-600 cursor-pointer"
                                                    />
                                                    <div className="flex-1">
                                                        <div className="font-medium text-gray-800">
                                                            {staff.first_name} {staff.last_name}
                                                        </div>
                                                        <div className="text-sm text-gray-500 flex gap-4">
                                                            <span>Email: {staff.email}</span>
                                                            {staff.phone && <span>SĐT: {staff.phone}</span>}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {selectedStaffIds.length > 0 && (
                                    <div className="mt-2 text-sm text-blue-600">
                                        Đã chọn {selectedStaffIds.length} nhân viên
                                    </div>
                                )}
                            </div>
                        )}

                        <div className="flex justify-end gap-3 mt-6">
                            <button
                                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors cursor-pointer"
                                onClick={() => {
                                    setShowAssignStaffModal(false);
                                    setSelectedWarehouseForAssign(null);
                                    setSelectedRole('');
                                    setSelectedStaffIds([]);
                                }}
                            >
                                Hủy
                            </button>
                            <button
                                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors cursor-pointer disabled:bg-gray-400 disabled:cursor-not-allowed"
                                onClick={handleAssignStaff}
                                disabled={!selectedRole || selectedStaffIds.length === 0}
                            >
                                Gán nhân viên ({selectedStaffIds.length})
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <AddWarehouseModal
                open={showCreateModal}
                onClose={() => setShowCreateModal(false)}
                onWarehouseCreated={fetchWarehouses}
                context={context}
            />

            <EditWarehouseModal
                open={showUpdateModal}
                onClose={() => {
                    setShowUpdateModal(false);
                    setSelectedWarehouse(null);
                }}
                onWarehouseUpdated={fetchWarehouses}
                context={context}
                warehouse={selectedWarehouse}
            />

            <WarehouseStaffModal
                open={showStaffModal}
                onClose={() => {
                    setShowStaffModal(false);
                    setSelectedWarehouseForStaff(null);
                }}
                warehouse={selectedWarehouseForStaff}
                context={context}
            />

            {showStockModal && selectedWarehouseForStock && (
                <Dialog
                    fullScreen
                    open={showStockModal}
                    onClose={() => {
                        setShowStockModal(false);
                        setSelectedWarehouseForStock(null);
                    }}
                    TransitionComponent={Transition}
                >
                    <AppBar sx={{ position: 'relative' }}>
                        <Toolbar>
                            <IconButton
                                edge="start"
                                color="inherit"
                                onClick={() => {
                                    setShowStockModal(false);
                                    setSelectedWarehouseForStock(null);
                                }}
                                aria-label="close"
                            >
                                <IoMdClose className='text-gray-800' />
                            </IconButton>
                            <Typography sx={{ ml: 2, flex: 1 }} variant="h6" component="div">
                                <span className='text-gray-800'>{selectedWarehouseForStock.name}</span>
                            </Typography>
                        </Toolbar>
                    </AppBar>
                    <WarehouseStock
                        warehouse={selectedWarehouseForStock}
                        onClose={() => {
                            setShowStockModal(false);
                            setSelectedWarehouseForStock(null);
                        }}
                    />
                </Dialog>
            )}
        </div>
    );
};

export default Warehouse