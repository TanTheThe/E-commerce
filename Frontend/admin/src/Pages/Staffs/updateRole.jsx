import { useContext, useEffect, useState } from "react";
import { MyContext } from "../../App";
import { putDataApi } from "../../utils/api";
import { Button, Dialog, MenuItem, Select } from "@mui/material";

const UpdateRoleDialog = ({ open, onClose, user, onSuccess, formatWarehouseRole }) => {
    const [role, setRole] = useState('');
    const [loading, setLoading] = useState(false);

    const context = useContext(MyContext);
    
    const roles = [
        { value: 'warehouse_keeper', label: 'Thủ kho' },
        { value: 'stock_clerk', label: 'Nhân viên kho' },
        { value: 'picker', label: 'Nhân viên lấy hàng' },
        { value: 'packer', label: 'Nhân viên đóng gói' }
    ];

    useEffect(() => {
        if (user && user.warehouse_role) {
            setRole(user.warehouse_role);
        }
    }, [user]);

    const handleSubmit = async () => {
        if (!role) {
            context.openAlertBox('warning', 'Vui lòng chọn vai trò');
            return;
        }

        if (!user.warehouse_id) {
            context.openAlertBox('error', 'Không thể cập nhật: Nhân viên chưa thuộc kho nào');
            return;
        }

        setLoading(true);
        try {
            const response = await putDataApi(
                `/admin/warehouse/${user.warehouse_id}/staff/${user.id}/role`,
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
            context.openAlertBox('error', 'Lỗi hệ thống khi cập nhật vai trò');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <div className="p-6">
                <h2 className="text-xl font-semibold mb-4">Cập nhật vai trò nhân viên</h2>
                
                <div className="mb-4">
                    <p className="text-sm text-gray-600 mb-2">
                        Nhân viên: <span className="font-medium">{user?.first_name} {user?.last_name}</span>
                    </p>
                    <p className="text-sm text-gray-600 mb-2">
                        Mã kho: <span className="font-medium">{user?.warehouse_code || 'Chưa có'}</span>
                    </p>
                    <p className="text-sm text-gray-600 mb-4">
                        Vai trò hiện tại: <span className="font-medium">{formatWarehouseRole(user?.warehouse_role)}</span>
                    </p>
                </div>

                <div className="mb-6">
                    <label className="block text-sm font-medium mb-2">Chọn vai trò mới</label>
                    <Select
                        fullWidth
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                        size="small"
                    >
                        {roles.map((r) => (
                            <MenuItem key={r.value} value={r.value}>
                                {r.label}
                            </MenuItem>
                        ))}
                    </Select>
                </div>

                <div className="flex gap-3 justify-end">
                    <Button
                        onClick={onClose}
                        disabled={loading}
                        className="!text-gray-600"
                    >
                        Hủy
                    </Button>
                    <Button
                        onClick={handleSubmit}
                        disabled={loading}
                        className="!bg-blue-600 hover:!bg-blue-700 !text-white"
                    >
                        {loading ? 'Đang cập nhật...' : 'Cập nhật'}
                    </Button>
                </div>
            </div>
        </Dialog>
    );
};

export default UpdateRoleDialog;