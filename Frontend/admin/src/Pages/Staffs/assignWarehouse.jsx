import React, { useState, useEffect, useContext } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, FormControl, Select, MenuItem, Grid, Card, CardContent, Typography, Chip } from '@mui/material';
import { MyContext } from '../../App';
import { getDataApi, postDataApi, putDataApi } from '../../utils/api';

const WAREHOUSE_ROLES = [
    { value: 'manager', label: 'Quản lý kho' },
    { value: 'warehouse_keeper', label: 'Thủ kho' },
    { value: 'stock_clerk', label: 'Nhân viên kho' },
    { value: 'picker', label: 'Nhân viên lấy hàng' },
    { value: 'packer', label: 'Nhân viên đóng gói' }
];

const STAFF_ROLES = WAREHOUSE_ROLES.filter(role => role.value !== 'manager');

const AssignWarehouseDialog = ({ open, onClose, userId, onSuccess }) => {
    const [step, setStep] = useState(1);
    const [selectedRole, setSelectedRole] = useState('');
    const [warehouses, setWarehouses] = useState([]);
    const [selectedWarehouse, setSelectedWarehouse] = useState(null);
    const [newRoleForOldManager, setNewRoleForOldManager] = useState('');
    const [loading, setLoading] = useState(false);

    const context = useContext(MyContext);

    useEffect(() => {
        if (open) {
            fetchWarehouses();
            resetState();
        }
    }, [open]);

    const resetState = () => {
        setStep(1);
        setSelectedRole('');
        setSelectedWarehouse(null);
        setNewRoleForOldManager('');
    };

    const fetchWarehouses = async () => {
        setLoading(true);
        try {
            const response = await getDataApi('/admin/warehouse/all?limit=100');
            if (response.success) {
                setWarehouses(response.data.data || []);
            } else {
                context.openAlertBox('error', 'Không thể tải danh sách kho');
            }
        } catch (error) {
            context.openAlertBox('error', 'Lỗi khi tải danh sách kho');
        } finally {
            setLoading(false);
        }
    };

    const handleRoleSelect = () => {
        if (!selectedRole) {
            context.openAlertBox('warning', 'Vui lòng chọn vai trò');
            return;
        }
        setStep(2);
    };

    const handleWarehouseSelect = (warehouse) => {
        if (selectedRole === 'manager' && warehouse.manager_name) {
            context.openAlertBox('warning', 'Kho này đã có quản lý');
            return;
        }

        setSelectedWarehouse(warehouse);

        if (selectedRole === 'manager' && warehouse.manager_name) {
            setStep(3);
        } else {
            handleAssign(warehouse);
        }
    };

    const handleAssign = async (warehouse = selectedWarehouse) => {
        if (!warehouse) return;

        setLoading(true);
        try {
            if (selectedRole === 'manager') {
                if (!newRoleForOldManager && warehouse.manager_name) {
                    context.openAlertBox('warning', 'Vui lòng chọn vai trò mới cho quản lý cũ');
                    setLoading(false);
                    return;
                }

                const response = await putDataApi(`/admin/warehouse/${warehouse.id}/assign-manager`, {
                    user_id: userId,
                    new_role_for_old_manager: newRoleForOldManager || 'staff'
                });

                if (response.success) {
                    context.openAlertBox('success', 'Gán quản lý kho thành công');
                    onSuccess();
                    onClose();
                } else {
                    context.openAlertBox('error', response?.data?.detail?.message || 'Gán quản lý thất bại');
                }
            } else {
                const response = await postDataApi(`/admin/warehouse/${warehouse.id}/assign-staff`, {
                    user_id: userId,
                    warehouse_role: selectedRole
                });

                if (response.success) {
                    context.openAlertBox('success', 'Gán nhân viên kho thành công');
                    onSuccess();
                    onClose();
                } else {
                    context.openAlertBox('error', response?.data?.detail?.message || 'Gán nhân viên thất bại');
                }
            }
        } catch (error) {
            context.openAlertBox('error', 'Lỗi hệ thống khi gán nhân viên');
        } finally {
            setLoading(false);
        }
    };

    const handleBack = () => {
        if (step === 3) {
            setStep(2);
            setNewRoleForOldManager('');
        } else if (step === 2) {
            setStep(1);
            setSelectedWarehouse(null);
        }
    };

    const canSelectWarehouse = (warehouse) => {
        if (selectedRole === 'manager') {
            return !warehouse.manager_name;
        }
        return true;
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>
                {step === 1 && 'Bước 1: Chọn vai trò'}
                {step === 2 && 'Bước 2: Chọn kho'}
                {step === 3 && 'Bước 3: Chọn vai trò mới cho quản lý cũ'}
            </DialogTitle>

            <DialogContent>
                {step === 1 && (
                    <div className="py-4">
                        <FormControl fullWidth>
                            <Select
                                value={selectedRole}
                                onChange={(e) => setSelectedRole(e.target.value)}
                                displayEmpty
                            >
                                <MenuItem value="">-- Chọn vai trò --</MenuItem>
                                {WAREHOUSE_ROLES.map(role => (
                                    <MenuItem key={role.value} value={role.value}>
                                        {role.label}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </div>
                )}

                {step === 2 && (
                    <div className="py-4">
                        {loading ? (
                            <div className="text-center py-8">Đang tải danh sách kho...</div>
                        ) : (
                            <Grid container spacing={2}>
                                {warehouses.map(warehouse => {
                                    const canSelect = canSelectWarehouse(warehouse);
                                    return (
                                        <Grid item xs={12} sm={6} key={warehouse.id}>
                                            <Card
                                                className={`cursor-pointer transition-all ${canSelect
                                                        ? 'hover:shadow-lg hover:scale-105'
                                                        : 'opacity-50 cursor-not-allowed'
                                                    }`}
                                                onClick={() => canSelect && handleWarehouseSelect(warehouse)}
                                                sx={{
                                                    border: selectedWarehouse?.id === warehouse.id ? '2px solid #1976d2' : '1px solid #e0e0e0',
                                                    opacity: canSelect ? 1 : 0.5
                                                }}
                                            >
                                                <CardContent>
                                                    <Typography variant="h6" className="font-semibold mb-2">
                                                        {warehouse.name}
                                                    </Typography>
                                                    <Typography variant="body2" color="text.secondary" className="mb-1">
                                                        Mã kho: <span className="font-medium">{warehouse.code}</span>
                                                    </Typography>
                                                    <Typography variant="body2" color="text.secondary" className="mb-2">
                                                        Địa chỉ: {warehouse.address}
                                                    </Typography>
                                                    {warehouse.manager_name && (
                                                        <Chip
                                                            label={`Quản lý: ${warehouse.manager_name}`}
                                                            size="small"
                                                            color="primary"
                                                            className="mt-2"
                                                        />
                                                    )}
                                                    {!canSelect && (
                                                        <Chip
                                                            label="Không thể chọn"
                                                            size="small"
                                                            color="error"
                                                            className="mt-2"
                                                        />
                                                    )}
                                                </CardContent>
                                            </Card>
                                        </Grid>
                                    );
                                })}
                            </Grid>
                        )}
                    </div>
                )}

                {step === 3 && (
                    <div className="py-4">
                        <Typography variant="body1" className="mb-4">
                            Kho này đã có quản lý. Vui lòng chọn vai trò mới cho quản lý cũ:
                        </Typography>
                        <FormControl fullWidth>
                            <Select
                                value={newRoleForOldManager}
                                onChange={(e) => setNewRoleForOldManager(e.target.value)}
                                displayEmpty
                            >
                                <MenuItem value="">-- Chọn vai trò --</MenuItem>
                                {STAFF_ROLES.map(role => (
                                    <MenuItem key={role.value} value={role.value}>
                                        {role.label}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </div>
                )}
            </DialogContent>

            <DialogActions>
                <Button onClick={onClose} disabled={loading}>
                    Hủy
                </Button>
                {step > 1 && (
                    <Button onClick={handleBack} disabled={loading}>
                        Quay lại
                    </Button>
                )}
                {step === 1 && (
                    <Button
                        onClick={handleRoleSelect}
                        variant="contained"
                        disabled={!selectedRole || loading}
                    >
                        Tiếp tục
                    </Button>
                )}
                {step === 3 && (
                    <Button
                        onClick={() => handleAssign()}
                        variant="contained"
                        disabled={!newRoleForOldManager || loading}
                    >
                        {loading ? 'Đang xử lý...' : 'Xác nhận'}
                    </Button>
                )}
            </DialogActions>
        </Dialog>
    );
};

export default AssignWarehouseDialog;