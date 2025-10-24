import React, { useState, useContext } from 'react';
import {
    Dialog, DialogTitle, DialogContent, DialogActions,
    Box, Typography, IconButton, Tabs, Tab, List, ListItem,
    CircularProgress, Chip, Button, TextField
} from '@mui/material';
import { FaTimes, FaCheck } from 'react-icons/fa';
import { styled } from '@mui/material';
import { MyContext } from '../../App';
import { getDataApi, postDataApi } from '../../utils/api';

const CancellationDialog = styled(Dialog)(({ theme }) => ({
    '& .MuiDialog-paper': {
        width: '800px',
        maxWidth: '90vw',
        maxHeight: '80vh'
    }
}));

const CancellationHandler = ({ open, onClose, onProcessed, onMarkAsProcessed, notifications }) => {
    const [cancellationRequests, setCancellationRequests] = useState([]);
    const [loadingCancellations, setLoadingCancellations] = useState(false);
    const [cancellationTab, setCancellationTab] = useState(0);
    const [selectedOrder, setSelectedOrder] = useState(null);
    const [actionDialog, setActionDialog] = useState(false);
    const [actionType, setActionType] = useState('');
    const [adminNote, setAdminNote] = useState('');
    const [rejectReason, setRejectReason] = useState('');
    const [processingAction, setProcessingAction] = useState(false);

    const context = useContext(MyContext);

    const fetchCancellationRequests = async (statusFilter = 'pending') => {
        setLoadingCancellations(true);
        try {
            const response = await getDataApi(`/admin/order/cancellation-requests?status_filter=${statusFilter}&limit=50`);
            if (response.success) {
                setCancellationRequests(response.data.data);
            }
        } catch (error) {
            console.error('Error fetching cancellation requests:', error);
            context.openAlertBox("error", "Không thể tải danh sách yêu cầu hủy đơn");
        } finally {
            setLoadingCancellations(false);
        }
    };

    const processCancellationRequest = async (orderId, action, note = '', reason = '') => {
        setProcessingAction(true);
        try {
            const requestData = {
                action: action === 'approve' ? 'handle_cancellation' : 'reject',
                admin_note: note,
                reject_reason: reason
            };

            const response = await postDataApi(`/admin/order/${orderId}/process-cancellation`, requestData);

            if (response.success) {
                context.openAlertBox("success", response.message);

                const currentStatusFilter = cancellationTab === 0 ? 'pending' : 'cancelled';
                await fetchCancellationRequests(currentStatusFilter);

                await autoMarkNotificationProcessed(orderId);
                await onProcessed();

                setActionDialog(false);
                setSelectedOrder(null);
                setAdminNote('');
                setRejectReason('');
            } else {
                context.openAlertBox("error", "Không thể xử lý yêu cầu hủy đơn");
            }
        } catch (error) {
            console.error('Error processing cancellation:', error);
            context.openAlertBox("error", "Lỗi khi xử lý yêu cầu hủy đơn");
        } finally {
            setProcessingAction(false);
        }
    };

    const autoMarkNotificationProcessed = async (orderId) => {
        try {
            const relatedNotification = notifications.find(n =>
                n.order_id === orderId &&
                n.action_type &&
                !n.is_processed
            );

            if (relatedNotification) {
                const response = await postDataApi('/admin/notifications/mark-processed', {
                    notification_id: relatedNotification.id
                });

                if (response.success) {
                    console.log('Notification marked as processed:', relatedNotification.id);
                } else {
                    console.error('Error marking notification as processed:', response.message);
                }
            }
        } catch (error) {
            console.error('Error auto-marking notification:', error);
        }
    };

    const handleCancellationTabChange = (event, newValue) => {
        setCancellationTab(newValue);
        const statusFilter = newValue === 0 ? 'pending' : 'cancelled';
        fetchCancellationRequests(statusFilter);
    };

    const openActionDialog = (order, type) => {
        setSelectedOrder(order);
        setActionType(type);
        setActionDialog(true);
    };

    // Fetch data when dialog opens
    React.useEffect(() => {
        if (open) {
            setCancellationTab(0);
            fetchCancellationRequests('pending');
        }
    }, [open]);

    return (
        <>
            <CancellationDialog
                open={open}
                onClose={onClose}
                maxWidth={false}
            >
                <DialogTitle>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="h6">Yêu cầu hủy đơn hàng</Typography>
                        <IconButton onClick={onClose}>
                            <FaTimes />
                        </IconButton>
                    </Box>
                </DialogTitle>

                <DialogContent>
                    <Tabs value={cancellationTab} onChange={handleCancellationTabChange} sx={{ mb: 2 }}>
                        <Tab label="Chờ xử lý" />
                        <Tab label="Đã hủy" />
                    </Tabs>

                    {loadingCancellations ? (
                        <Box display="flex" justifyContent="center" py={4}>
                            <CircularProgress />
                        </Box>
                    ) : cancellationRequests.length === 0 ? (
                        <Box textAlign="center" py={4}>
                            <Typography variant="body2" color="textSecondary">
                                {cancellationTab === 0 ? 'Không có yêu cầu hủy nào đang chờ xử lý' : 'Không có đơn hàng nào đã bị hủy'}
                            </Typography>
                        </Box>
                    ) : (
                        <List sx={{ maxHeight: '400px', overflowY: 'auto' }}>
                            {cancellationRequests.map((order) => (
                                <ListItem key={order.id} sx={{ border: '1px solid #e0e0e0', mb: 1, borderRadius: '8px' }}>
                                    <Box width="100%">
                                        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                                            <Typography variant="subtitle1" fontWeight={600}>
                                                Đơn hàng #{order.code}
                                            </Typography>
                                            <Box display="flex" gap={1}>
                                                <Chip
                                                    label={order.status}
                                                    size="small"
                                                    color={order.status === 'cancelled' ? 'error' : 'primary'}
                                                />
                                                {order.cancellation_status && (
                                                    <Chip
                                                        label={order.cancellation_status}
                                                        size="small"
                                                        color={order.cancellation_status === 'requested' ? 'warning' : 'default'}
                                                    />
                                                )}
                                            </Box>
                                        </Box>

                                        <Typography variant="body2" color="textSecondary" gutterBottom>
                                            Khách hàng: {order.first_name} {order.last_name}
                                        </Typography>

                                        <Typography variant="body2" color="textSecondary" gutterBottom>
                                            Tổng tiền: {new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(order.total_price)}
                                        </Typography>

                                        <Typography variant="body2" color="textSecondary" gutterBottom>
                                            Lý do hủy: {order.cancellation_reason || 'Không có'}
                                        </Typography>

                                        <Typography variant="body2" color="textSecondary" gutterBottom>
                                            Yêu cầu hủy lúc: {new Date(order.cancellation_requested_at).toLocaleString('vi-VN')}
                                        </Typography>

                                        {cancellationTab === 0 && order.cancellation_status === 'requested' && (
                                            <Box display="flex" gap={1} mt={2}>
                                                <Button
                                                    variant="contained"
                                                    color="success"
                                                    size="small"
                                                    startIcon={<FaCheck />}
                                                    onClick={() => openActionDialog(order, 'approve')}
                                                    disabled={processingAction}
                                                >
                                                    Chấp nhận
                                                </Button>
                                                <Button
                                                    variant="contained"
                                                    color="error"
                                                    size="small"
                                                    startIcon={<FaTimes />}
                                                    onClick={() => openActionDialog(order, 'reject')}
                                                    disabled={processingAction}
                                                >
                                                    Từ chối
                                                </Button>
                                            </Box>
                                        )}
                                    </Box>
                                </ListItem>
                            ))}
                        </List>
                    )}
                </DialogContent>
            </CancellationDialog>

            <Dialog open={actionDialog} onClose={() => setActionDialog(false)} maxWidth="sm" fullWidth>
                <DialogTitle>
                    {actionType === 'approve' ? 'Chấp nhận hủy đơn hàng' : 'Từ chối hủy đơn hàng'}
                </DialogTitle>
                <DialogContent>
                    {selectedOrder && (
                        <Box mb={2}>
                            <Typography variant="body2" gutterBottom>
                                <strong>Đơn hàng:</strong> #{selectedOrder.code}
                            </Typography>
                            <Typography variant="body2" gutterBottom>
                                <strong>Khách hàng:</strong> {selectedOrder.first_name} {selectedOrder.last_name}
                            </Typography>
                            <Typography variant="body2" gutterBottom>
                                <strong>Lý do hủy:</strong> {selectedOrder.cancellation_reason}
                            </Typography>
                        </Box>
                    )}

                    {actionType === 'approve' ? (
                        <TextField
                            autoFocus
                            margin="dense"
                            label="Ghi chú của admin (tùy chọn)"
                            multiline
                            rows={3}
                            fullWidth
                            variant="outlined"
                            value={adminNote}
                            onChange={(e) => setAdminNote(e.target.value)}
                            placeholder="Ghi chú về việc chấp nhận hủy đơn..."
                        />
                    ) : (
                        <TextField
                            autoFocus
                            margin="dense"
                            label="Lý do từ chối *"
                            multiline
                            rows={3}
                            fullWidth
                            variant="outlined"
                            value={rejectReason}
                            onChange={(e) => setRejectReason(e.target.value)}
                            placeholder="Nhập lý do từ chối hủy đơn hàng..."
                            required
                        />
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setActionDialog(false)}>
                        Hủy
                    </Button>
                    <Button
                        variant="contained"
                        color={actionType === 'approve' ? 'success' : 'error'}
                        onClick={() => {
                            if (actionType === 'reject' && !rejectReason.trim()) {
                                context.openAlertBox("error", "Vui lòng nhập lý do từ chối");
                                return;
                            }
                            processCancellationRequest(
                                selectedOrder.id,
                                actionType,
                                adminNote,
                                rejectReason
                            );
                        }}
                        disabled={processingAction}
                        startIcon={processingAction ? <CircularProgress size={16} /> : (actionType === 'approve' ? <FaCheck /> : <FaTimes />)}
                    >
                        {processingAction ? 'Đang xử lý...' : (actionType === 'approve' ? 'Chấp nhận' : 'Từ chối')}
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
};

export default CancellationHandler;