import React, { useState, useEffect, useContext } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, FormControl, Select, MenuItem, Grid, Card, CardContent, Typography, Chip } from '@mui/material';
import { MyContext } from '../../App';
import CloseIcon from '@mui/icons-material/Close';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { CircularProgress, Alert, IconButton } from '@mui/material';
import { getDataApi, postDataApi, putDataApi } from '../../utils/api';
import InfoIcon from '@mui/icons-material/Info';

const WAREHOUSE_ROLES = [
    { value: 'manager', label: 'Quản lý kho' },
    { value: 'warehouse_keeper', label: 'Thủ kho' },
    { value: 'stock_clerk', label: 'Nhân viên kho' },
    { value: 'picker', label: 'Nhân viên lấy hàng' },
    { value: 'packer', label: 'Nhân viên đóng gói' }
];

const STAFF_ROLES = WAREHOUSE_ROLES.filter(role => role.value !== 'manager');

const AssignWarehouseDialog = ({ open, onClose, userId, onSuccess }) => {
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
    };

    const handleWarehouseSelect = (warehouse) => {
        setSelectedWarehouse(warehouse);
        if (selectedRole === 'manager' && warehouse.manager_name) {

        } else {
            handleAssign(warehouse);
        }
    };

    const handleAssign = async (warehouse = selectedWarehouse) => {
        if (!warehouse) return;

        setLoading(true);
        try {
            if (selectedRole === 'manager') {
                if (warehouse.manager_name && !newRoleForOldManager) {
                    context.openAlertBox('warning', 'Vui lòng chọn vai trò mới cho quản lý cũ');
                    setLoading(false);
                    return;
                }

                const response = await putDataApi(`/admin/warehouse/${warehouse.id}/assign-manager`, {
                    user_id: userId,
                    new_role_for_old_manager: warehouse.manager_name ? newRoleForOldManager : null
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

    const canSelectWarehouse = (warehouse) => {
        return true;
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>
                <div className="flex items-center justify-between">
                    <span>Gán nhân viên vào kho</span>
                    <IconButton onClick={onClose} size="small">
                        <CloseIcon />
                    </IconButton>
                </div>
            </DialogTitle>

            <DialogContent dividers sx={{ minHeight: '400px' }}>
                {/* Bước 1: Chọn vai trò */}
                <div className="mb-6">
                    <div className="flex items-center gap-2 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-bold shadow-md">
                            1
                        </div>
                        <Typography variant="h6" className="font-bold text-gray-800">
                            Chọn vai trò
                        </Typography>
                    </div>
                    <div className="ml-12">
                        <FormControl fullWidth disabled={selectedRole && selectedWarehouse}>
                            <Select
                                value={selectedRole}
                                onChange={(e) => setSelectedRole(e.target.value)}
                                displayEmpty
                                sx={{
                                    backgroundColor: (selectedRole && selectedWarehouse) ? '#f5f5f5' : 'white',
                                    borderRadius: '8px',
                                    '& .MuiOutlinedInput-notchedOutline': {
                                        borderColor: selectedRole ? '#1976d2' : '#e0e0e0',
                                        borderWidth: selectedRole ? '2px' : '1px',
                                    },
                                }}
                            >
                                <MenuItem value="">-- Chọn vai trò --</MenuItem>
                                {WAREHOUSE_ROLES.map(role => (
                                    <MenuItem key={role.value} value={role.value}>
                                        <div className="flex items-center gap-2">
                                            <span>{role.label}</span>
                                            {role.value === 'manager' && (
                                                <Chip label="Quản lý" size="small" color="primary" sx={{ height: '20px' }} />
                                            )}
                                        </div>
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                        {selectedRole && selectedWarehouse && (
                            <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200 flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <CheckCircleIcon sx={{ color: '#1976d2' }} />
                                    <Chip
                                        label={WAREHOUSE_ROLES.find(r => r.value === selectedRole)?.label}
                                        color="primary"
                                        size="small"
                                    />
                                </div>
                                <Button
                                    size="small"
                                    variant="outlined"
                                    onClick={() => {
                                        setSelectedRole('');
                                        setSelectedWarehouse(null);
                                        setNewRoleForOldManager('');
                                    }}
                                >
                                    Thay đổi
                                </Button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Bước 2: Chọn kho - Chỉ hiển thị khi đã chọn role */}
                {selectedRole && !selectedWarehouse && (
                    <div className="mb-6">
                        <div className="flex items-center gap-2 mb-3">
                            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center text-white font-bold shadow-md">
                                2
                            </div>
                            <Typography variant="h6" className="font-bold text-gray-800">
                                Chọn kho
                            </Typography>
                        </div>
                        <div className="ml-12">
                            {loading ? (
                                <div className="text-center py-12">
                                    <CircularProgress size={50} thickness={4} />
                                    <Typography className="mt-4 text-gray-600 font-medium">
                                        Đang tải danh sách kho...
                                    </Typography>
                                </div>
                            ) : warehouses.length === 0 ? (
                                <Alert severity="info" sx={{ borderRadius: '8px' }}>
                                    Không có kho nào trong hệ thống
                                </Alert>
                            ) : (
                                <Grid container spacing={2}>
                                    {warehouses.map(warehouse => (
                                        <Grid item xs={12} sm={6} key={warehouse.id}>
                                            <Card
                                                className="cursor-pointer transition-all duration-300"
                                                onClick={() => handleWarehouseSelect(warehouse)}
                                                sx={{
                                                    border: '2px solid #e0e0e0',
                                                    borderRadius: '12px',
                                                    '&:hover': {
                                                        transform: 'translateY(-4px)',
                                                        boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
                                                        borderColor: '#1976d2',
                                                    }
                                                }}
                                            >
                                                <CardContent>
                                                    <div className="flex items-start justify-between mb-2">
                                                        <Typography variant="h6" className="font-bold text-gray-800 flex-1">
                                                            {warehouse.name}
                                                        </Typography>
                                                        {selectedRole === 'manager' && warehouse.manager_name && (
                                                            <Chip
                                                                label="Có quản lý"
                                                                size="small"
                                                                color="warning"
                                                                sx={{ height: '24px', fontWeight: 600 }}
                                                            />
                                                        )}
                                                    </div>
                                                    <div className="space-y-1 mb-3">
                                                        <Typography variant="body2" className="text-gray-600">
                                                            <strong className="text-gray-700">Mã kho:</strong> {warehouse.code}
                                                        </Typography>
                                                        <Typography variant="body2" className="text-gray-600">
                                                            <strong className="text-gray-700">Địa chỉ:</strong> {warehouse.address}
                                                        </Typography>
                                                    </div>
                                                    {warehouse.manager_name && (
                                                        <div className="mt-3 pt-3 border-t border-gray-200">
                                                            <div className="flex items-center gap-2">
                                                                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                                                                    <span className="text-blue-600 font-bold text-sm">
                                                                        {warehouse.manager_name.charAt(0).toUpperCase()}
                                                                    </span>
                                                                </div>
                                                                <div>
                                                                    <Typography variant="caption" className="text-gray-500 block">
                                                                        Quản lý hiện tại
                                                                    </Typography>
                                                                    <Typography variant="body2" className="font-semibold text-gray-800">
                                                                        {warehouse.manager_name}
                                                                    </Typography>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    )}
                                                </CardContent>
                                            </Card>
                                        </Grid>
                                    ))}
                                </Grid>
                            )}
                        </div>
                    </div>
                )}

                {/* Hiển thị kho đã chọn (cho trường hợp không cần chọn role mới) */}
                {selectedWarehouse && !(selectedRole === 'manager' && selectedWarehouse.manager_name) && (
                    <div className="mb-6">
                        <div className="flex items-center gap-2 mb-3">
                            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center text-white font-bold shadow-md">
                                <CheckCircleIcon />
                            </div>
                            <Typography variant="h6" className="font-bold text-gray-800">
                                Kho đã chọn
                            </Typography>
                        </div>
                        <div className="ml-12">
                            <div className="p-4 bg-green-50 rounded-lg border-2 border-green-200 flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-12 h-12 rounded-lg bg-green-500 flex items-center justify-center text-white font-bold shadow-md">
                                        {selectedWarehouse?.name.charAt(0).toUpperCase()}
                                    </div>
                                    <div>
                                        <Typography variant="body1" className="font-bold text-gray-800">
                                            {selectedWarehouse?.name}
                                        </Typography>
                                        <Typography variant="caption" className="text-gray-600">
                                            {selectedWarehouse?.code}
                                        </Typography>
                                    </div>
                                </div>
                                <Button
                                    size="small"
                                    variant="outlined"
                                    color="success"
                                    onClick={() => {
                                        setSelectedWarehouse(null);
                                        setNewRoleForOldManager('');
                                    }}
                                >
                                    Thay đổi
                                </Button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Bước 3: Chọn vai trò mới cho quản lý cũ - Chỉ hiển thị khi assign manager vào kho đã có manager */}
                {selectedRole === 'manager' && selectedWarehouse?.manager_name && (
                    <div className="mb-4">
                        <div className="flex items-center gap-2 mb-3">
                            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center text-white font-bold shadow-md">
                                3
                            </div>
                            <Typography variant="h6" className="font-bold text-gray-800">
                                Vai trò mới cho quản lý cũ
                            </Typography>
                        </div>
                        <div className="ml-12">
                            <Alert
                                severity="warning"
                                icon={<InfoIcon />}
                                sx={{
                                    mb: 3,
                                    borderRadius: '8px',
                                    border: '1px solid #ed6c02',
                                    '& .MuiAlert-message': {
                                        width: '100%'
                                    }
                                }}
                            >
                                <div className="space-y-2">
                                    <Typography variant="body2" className="font-semibold">
                                        Kho <strong className="text-orange-700">{selectedWarehouse?.name}</strong> đã có quản lý
                                    </Typography>
                                    <div className="flex items-center gap-2 p-2 bg-white rounded border border-orange-200">
                                        <div className="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center">
                                            <span className="text-orange-600 font-bold text-sm">
                                                {selectedWarehouse?.manager_name.charAt(0).toUpperCase()}
                                            </span>
                                        </div>
                                        <div>
                                            <Typography variant="caption" className="text-gray-600">
                                                Quản lý hiện tại
                                            </Typography>
                                            <Typography variant="body2" className="font-semibold">
                                                {selectedWarehouse?.manager_name}
                                            </Typography>
                                        </div>
                                    </div>
                                    <Typography variant="body2" className="text-gray-700">
                                        Vui lòng chọn vai trò mới cho quản lý cũ sau khi thay thế
                                    </Typography>
                                </div>
                            </Alert>

                            <FormControl fullWidth sx={{ mb: 3 }}>
                                <Select
                                    value={newRoleForOldManager}
                                    onChange={(e) => setNewRoleForOldManager(e.target.value)}
                                    displayEmpty
                                    sx={{
                                        borderRadius: '8px',
                                        '& .MuiOutlinedInput-notchedOutline': {
                                            borderColor: newRoleForOldManager ? '#ed6c02' : '#e0e0e0',
                                            borderWidth: newRoleForOldManager ? '2px' : '1px',
                                        },
                                    }}
                                >
                                    <MenuItem value="">-- Chọn vai trò mới --</MenuItem>
                                    {STAFF_ROLES.map(role => (
                                        <MenuItem key={role.value} value={role.value}>
                                            {role.label}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>

                            <Button
                                onClick={() => handleAssign()}
                                variant="contained"
                                disabled={!newRoleForOldManager || loading}
                                fullWidth
                                size="large"
                                sx={{
                                    borderRadius: '8px',
                                    py: 1.5,
                                    fontSize: '16px',
                                    fontWeight: 600,
                                    textTransform: 'none',
                                    background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
                                    '&:hover': {
                                        background: 'linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)',
                                    }
                                }}
                                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <CheckCircleIcon />}
                            >
                                {loading ? 'Đang xử lý...' : 'Xác nhận gán kho'}
                            </Button>

                            <Button
                                size="small"
                                variant="text"
                                fullWidth
                                sx={{ mt: 1 }}
                                onClick={() => {
                                    setSelectedWarehouse(null);
                                    setNewRoleForOldManager('');
                                }}
                            >
                                Chọn lại kho
                            </Button>
                        </div>
                    </div>
                )}
            </DialogContent>
        </Dialog>
    );
};

export default AssignWarehouseDialog;