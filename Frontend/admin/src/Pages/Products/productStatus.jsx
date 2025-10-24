// ProductStatusManager.jsx
import React, { useState, useContext } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Typography,
    Box,
    Chip
} from '@mui/material';
import { MyContext } from '../../App';
import { putDataApi, postDataApi } from '../../utils/api';

const ProductStatusManager = ({
    open,
    onClose,
    selectedProducts,
    mode,
    onStatusUpdated
}) => {
    const [selectedStatus, setSelectedStatus] = useState('');
    const [loading, setLoading] = useState(false);
    const context = useContext(MyContext);

    const statusOptions = [
        { value: 'active', label: 'Hoạt động', color: 'success' },
        { value: 'inactive', label: 'Không hoạt động', color: 'error' },
    ];

    const getStatusChip = (status) => {
        const statusConfig = statusOptions.find(s => s.value === status);
        return (
            <Chip
                label={statusConfig?.label || status}
                color={statusConfig?.color || 'default'}
                size="small"
            />
        );
    };

    const handleUpdateStatus = async () => {
        if (!selectedStatus) {
            context.openAlertBox('error', 'Vui lòng chọn trạng thái');
            return;
        }

        setLoading(true);
        try {
            let response;

            if (mode === 'single' && selectedProducts.length === 1) {
                response = await putDataApi(`/admin/product/${selectedProducts[0].id}/status`, {
                    status: selectedStatus
                });
            } else {
                response = await postDataApi('/admin/product/status/bulk', {
                    product_ids: selectedProducts.map(p => p.id),
                    status: selectedStatus
                });
            }

            if (response.success) {
                const message = mode === 'single'
                    ? 'Cập nhật trạng thái sản phẩm thành công'
                    : `Cập nhật trạng thái thành công cho ${selectedProducts.length} sản phẩm`;

                context.openAlertBox('success', message);
                onStatusUpdated();
                handleClose();
            } else {
                context.openAlertBox('error', response.message || 'Cập nhật thất bại');
            }
        } catch (error) {
            console.error('Error updating product status:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi cập nhật trạng thái');
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setSelectedStatus('');
        onClose();
    };

    const getDialogTitle = () => {
        if (mode === 'single' && selectedProducts.length === 1) {
            return 'Cập nhật trạng thái sản phẩm';
        }
        return `Cập nhật trạng thái ${selectedProducts.length} sản phẩm`;
    };

    return (
        <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
            <DialogTitle>{getDialogTitle()}</DialogTitle>

            <DialogContent>
                {mode === 'single' && selectedProducts.length === 1 ? (
                    <Box sx={{ mb: 3 }}>
                        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                            <img
                                src={selectedProducts[0].images?.[0] || '/placeholder-image.jpg'}
                                alt={selectedProducts[0].name}
                                style={{ width: 60, height: 60, objectFit: 'cover', borderRadius: 8 }}
                            />
                            <Box>
                                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                                    {selectedProducts[0].name}
                                </Typography>
                                <Box sx={{ mt: 1 }}>
                                    <Typography variant="body2" color="text.secondary" component="span">
                                        Trạng thái hiện tại:
                                    </Typography>
                                    {getStatusChip(selectedProducts[0].status)}
                                </Box>
                            </Box>
                        </Box>
                    </Box>
                ) : (
                    <Box sx={{ mb: 3 }}>
                        <Typography variant="body1" sx={{ mb: 2 }}>
                            Bạn đang cập nhật trạng thái cho {selectedProducts.length} sản phẩm:
                        </Typography>
                        <Box sx={{ maxHeight: 200, overflowY: 'auto' }}>
                            {selectedProducts.map((product, index) => (
                                <Box key={product.id} sx={{
                                    display: 'flex',
                                    gap: 2,
                                    alignItems: 'center',
                                    mb: 1,
                                    p: 1,
                                    border: '1px solid #e0e0e0',
                                    borderRadius: 1
                                }}>
                                    <img
                                        src={product.images?.[0] || '/placeholder-image.jpg'}
                                        alt={product.name}
                                        style={{ width: 40, height: 40, objectFit: 'cover', borderRadius: 4 }}
                                    />
                                    <Box sx={{ flex: 1 }}>
                                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                            {product.name}
                                        </Typography>
                                        <Box sx={{ mt: 0.5 }}>
                                            {getStatusChip(product.status)}
                                        </Box>
                                    </Box>
                                </Box>
                            ))}
                        </Box>
                    </Box>
                )}

                <FormControl fullWidth>
                    <InputLabel>Trạng thái mới</InputLabel>
                    <Select
                        value={selectedStatus}
                        label="Trạng thái mới"
                        onChange={(e) => setSelectedStatus(e.target.value)}
                    >
                        {statusOptions.map((status) => (
                            <MenuItem key={status.value} value={status.value}>
                                <Chip
                                    label={status.label}
                                    color={status.color}
                                    size="small"
                                />
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </DialogContent>

            <DialogActions>
                <Button onClick={handleClose} disabled={loading}>
                    Hủy
                </Button>
                <Button
                    onClick={handleUpdateStatus}
                    variant="contained"
                    disabled={loading || !selectedStatus}
                >
                    {loading ? 'Đang cập nhật...' : 'Cập nhật'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default ProductStatusManager;