import React, { useState, useContext } from 'react';
import {
    Dialog, DialogTitle, DialogContent, DialogActions,
    Box, Typography, IconButton, Tabs, Tab, List, ListItem,
    CircularProgress, Chip, Button, TextField, Card, CardContent,
    Grid, Avatar, Divider
} from '@mui/material';
import { FaTimes, FaCheck, FaUndo, FaExclamationTriangle, FaImage, FaCog, FaRedo } from 'react-icons/fa';
import { styled } from '@mui/material';
import { MyContext } from '../../App';
import { getDataApi, postDataApi, putDataApi } from '../../utils/api';

const ReturnDialog = styled(Dialog)(({ theme }) => ({
    '& .MuiDialog-paper': {
        width: '900px',
        maxWidth: '95vw',
        maxHeight: '90vh'
    }
}));

const StatusChip = styled(Chip)(({ status }) => ({
    fontWeight: 'bold',
    ...(status === 'pending' && {
        backgroundColor: '#fff3cd',
        color: '#856404',
        border: '1px solid #ffeaa7'
    }),
    ...(status === 'approved' && {
        backgroundColor: '#d4edda',
        color: '#155724',
        border: '1px solid #c3e6cb'
    }),
    ...(status === 'rejected' && {
        backgroundColor: '#f8d7da',
        color: '#721c24',
        border: '1px solid #f5c6cb'
    }),
}));

const ReturnRequestHandler = ({ open, onClose, onProcessed, onMarkAsProcessed, notifications }) => {
    const [returnRequests, setReturnRequests] = useState([]);
    const [loadingReturns, setLoadingReturns] = useState(false);
    const [returnTab, setReturnTab] = useState(0);
    const [selectedReturn, setSelectedReturn] = useState(null);
    const [returnDetail, setReturnDetail] = useState(null);
    const [actionDialog, setActionDialog] = useState(false);
    const [actionType, setActionType] = useState('');
    const [adminNote, setAdminNote] = useState('');
    const [rejectReason, setRejectReason] = useState('');
    const [processingAction, setProcessingAction] = useState(false);
    const [detailDialog, setDetailDialog] = useState(false);
    const [loadingDetail, setLoadingDetail] = useState(false);
    const [processingRefund, setProcessingRefund] = useState(false);
    const [completingReturn, setCompletingReturn] = useState(false);

    const context = useContext(MyContext);

    const fetchReturnRequests = async (statusFilter = 'pending') => {
        setLoadingReturns(true);
        try {
            const response = await getDataApi(`/admin/return-order/requests?status_return=${statusFilter}&limit=50`);
            if (response.success) {
                setReturnRequests(response.data.data);
            }
        } catch (error) {
            console.error('Error fetching return requests:', error);
            context.openAlertBox("error", "Không thể tải danh sách yêu cầu hoàn trả");
        } finally {
            setLoadingReturns(false);
        }
    };

    const fetchReturnDetail = async (returnId) => {
        setLoadingDetail(true);
        try {
            const response = await getDataApi(`/admin/return-order/${returnId}`);
            if (response.success) {
                setReturnDetail(response.data);
            }
        } catch (error) {
            console.error('Error fetching return detail:', error);
            context.openAlertBox("error", "Không thể tải chi tiết yêu cầu hoàn trả");
        } finally {
            setLoadingDetail(false);
        }
    };

    const processReturnRequest = async (returnId, action, note = '', reason = '') => {
        setProcessingAction(true);
        try {
            const requestData = {
                action: action,
                admin_note: note,
                reject_reason: reason
            };

            const response = await postDataApi(`/admin/return-order/process/${returnId}`, requestData);

            if (response.success) {
                context.openAlertBox("success", response.message);

                const currentStatusFilter = getStatusFilter();
                await fetchReturnRequests(currentStatusFilter);
                await autoMarkNotificationProcessed(returnId);
                await onProcessed();

                setActionDialog(false);
                setSelectedReturn(null);
                setAdminNote('');
                setRejectReason('');
            } else {
                context.openAlertBox("error", response.data.detail.message || "Không thể xử lý yêu cầu hoàn trả");
            }
        } catch (error) {
            console.error('Error processing return:', error);
            context.openAlertBox("error", "Lỗi khi xử lý yêu cầu hoàn trả");
        } finally {
            setProcessingAction(false);
        }
    };

    const completeReturnOrder = async (returnId, restoreStock = true) => {
        setCompletingReturn(true);
        try {
            const response = await postDataApi(`/admin/return-order/complete/${returnId}`, {
                restore_stock: restoreStock
            });

            if (response.success) {
                context.openAlertBox("success", response.message);

                const currentStatusFilter = getStatusFilter();
                await fetchReturnRequests(currentStatusFilter);

                if (returnDetail && selectedReturn?.id === returnId) {
                    await fetchReturnDetail(returnId);
                }
            } else {
                context.openAlertBox("error", response.data.detail.message || "Không thể hoàn thành xử lý hoàn trả");
            }
        } catch (error) {
            console.error('Error completing return:', error);
            context.openAlertBox("error", "Lỗi khi hoàn thành xử lý hoàn trả");
        } finally {
            setCompletingReturn(false);
        }
    };

    const retryRefund = async (refundId) => {
        setProcessingRefund(true);
        try {
            const response = await postDataApi(`/admin/return-order/retry-refund/${refundId}`, {});

            if (response.success) {
                const result = response.data;

                if (result.status === 'success') {
                    context.openAlertBox("success", result.message);
                } else if (result.status === 'manual_required') {
                    context.openAlertBox("warning", result.message);
                } else {
                    context.openAlertBox("error", result.data.detail.message);
                }

                if (returnDetail && selectedReturn) {
                    await fetchReturnDetail(selectedReturn.id);
                }
            }
        } catch (error) {
            console.error('Error retrying refund:', error);
            context.openAlertBox("error", "Lỗi khi thử lại hoàn tiền");
        } finally {
            setProcessingRefund(false);
        }
    };

    const updateRefundStatus = async (refundId, status) => {
        try {
            const response = await putDataApi(`/admin/return-order/refund/${refundId}/status`, { status });
            if (response.success) {
                context.openAlertBox("success", response.message);
                if (returnDetail) {
                    await fetchReturnDetail(selectedReturn.id);
                }
            }
        } catch (error) {
            console.error('Error updating refund status:', error);
            context.openAlertBox("error", "Không thể cập nhật trạng thái hoàn tiền");
        }
    };

    const autoMarkNotificationProcessed = async (returnId) => {
        try {
            const relatedNotification = notifications.find(n =>
                n.return_order_id === returnId &&
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

    const getStatusFilter = (tabValue = returnTab) => {
        switch (tabValue) {
            case 0: return 'pending';
            case 1: return 'approved';
            case 2: return 'completed';
            case 3: return 'rejected';
            default: return 'pending';
        }
    };

    const handleReturnTabChange = (event, newValue) => {
        setReturnTab(newValue);
        const statusFilter = getStatusFilter(newValue);
        fetchReturnRequests(statusFilter);
    };

    const openActionDialog = (returnRequest, type) => {
        setSelectedReturn(returnRequest);
        setActionType(type);
        setActionDialog(true);
    };

    const openDetailDialog = async (returnRequest) => {
        setSelectedReturn(returnRequest);
        setDetailDialog(true);
        await fetchReturnDetail(returnRequest.id);
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'pending': return 'warning';
            case 'approved': return 'success';
            case 'rejected': return 'error';
            default: return 'default';
        }
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(amount);
    };

    React.useEffect(() => {
        if (open) {
            setReturnTab(0);
            fetchReturnRequests('pending');
        }
    }, [open]);

    return (
        <>
            <ReturnDialog
                open={open}
                onClose={onClose}
                maxWidth={false}
            >
                <DialogTitle>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="h6">Yêu cầu hoàn trả đơn hàng</Typography>
                        <IconButton onClick={onClose}>
                            <FaTimes />
                        </IconButton>
                    </Box>
                </DialogTitle>

                <DialogContent>
                    <Tabs value={returnTab} onChange={handleReturnTabChange} sx={{ mb: 2 }}>
                        <Tab label="Chờ xử lý" />
                        <Tab label="Đã chấp nhận" />
                        <Tab label="Đã hoàn thành" />
                        <Tab label="Đã từ chối" />
                    </Tabs>

                    {loadingReturns ? (
                        <Box display="flex" justifyContent="center" py={4}>
                            <CircularProgress />
                        </Box>
                    ) : returnRequests.length === 0 ? (
                        <Box textAlign="center" py={4}>
                            <FaUndo className="text-gray-400 text-2xl mb-2" />
                            <Typography variant="body2" color="textSecondary">
                                {returnTab === 0 && 'Không có yêu cầu hoàn trả nào đang chờ xử lý'}
                                {returnTab === 1 && 'Không có yêu cầu hoàn trả nào đã được chấp nhận'}
                                {returnTab === 2 && 'Không có yêu cầu hoàn trả nào đã hoàn thành'}
                                {returnTab === 3 && 'Không có yêu cầu hoàn trả nào đã bị từ chối'}
                            </Typography>
                        </Box>
                    ) : (
                        <List sx={{ maxHeight: '500px', overflowY: 'auto' }}>
                            {returnRequests.map((returnRequest) => (
                                <ListItem key={returnRequest.id} sx={{ border: '1px solid #e0e0e0', mb: 2, borderRadius: '8px', p: 0 }}>
                                    <Card sx={{ width: '100%' }}>
                                        <CardContent>
                                            <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                                                <Box>
                                                    <Typography variant="h6" gutterBottom>
                                                        Đơn hàng #{returnRequest.order?.code}
                                                    </Typography>
                                                    <Typography variant="body2" color="textSecondary">
                                                        Khách hàng: {returnRequest.user?.first_name} {returnRequest.user?.last_name}
                                                    </Typography>
                                                    <Typography variant="body2" color="textSecondary">
                                                        Email: {returnRequest.user?.email}
                                                    </Typography>
                                                </Box>
                                                <Box display="flex" flexDirection="column" alignItems="flex-end" gap={1}>
                                                    <StatusChip
                                                        status={returnRequest.status}
                                                        label={returnRequest.status}
                                                        size="small"
                                                    />
                                                    <Typography variant="caption" color="textSecondary">
                                                        {new Date(returnRequest.created_at).toLocaleString('vi-VN')}
                                                    </Typography>
                                                </Box>
                                            </Box>

                                            <Divider sx={{ my: 2 }} />

                                            <Grid container spacing={2}>
                                                <Grid item xs={12} sm={6}>
                                                    <Typography variant="body2" gutterBottom>
                                                        <strong>Tổng tiền đơn hàng:</strong> {formatCurrency(returnRequest.order?.total_price)}
                                                    </Typography>
                                                    <Typography variant="body2" gutterBottom>
                                                        <strong>Số sản phẩm hoàn trả:</strong> {returnRequest.return_items_count}
                                                    </Typography>
                                                    <Typography variant="body2" gutterBottom>
                                                        <strong>Tổng tiền hoàn trả:</strong> {formatCurrency(returnRequest.total_refund)}
                                                    </Typography>
                                                </Grid>
                                                <Grid item xs={12} sm={6}>
                                                    <Typography variant="body2" gutterBottom>
                                                        <strong>Phương thức thanh toán:</strong> {returnRequest.order?.payment_method?.toUpperCase()}
                                                    </Typography>
                                                    <Typography variant="body2" gutterBottom>
                                                        <strong>Trạng thái thanh toán:</strong> {returnRequest.order?.payment_status}
                                                    </Typography>
                                                </Grid>
                                            </Grid>

                                            <Box mt={2}>
                                                <Typography variant="body2" gutterBottom>
                                                    <strong>Lý do hoàn trả:</strong>
                                                </Typography>
                                                <Typography variant="body2" color="textSecondary" sx={{
                                                    backgroundColor: '#f5f5f5',
                                                    p: 1,
                                                    borderRadius: 1,
                                                    fontStyle: 'italic'
                                                }}>
                                                    {returnRequest.reason}
                                                </Typography>
                                            </Box>

                                            {returnRequest.note && (
                                                <Box mt={1}>
                                                    <Typography variant="body2" gutterBottom>
                                                        <strong>Ghi chú:</strong>
                                                    </Typography>
                                                    <Typography variant="body2" color="textSecondary" sx={{
                                                        backgroundColor: '#f0f8ff',
                                                        p: 1,
                                                        borderRadius: 1
                                                    }}>
                                                        {returnRequest.note}
                                                    </Typography>
                                                </Box>
                                            )}

                                            <Box display="flex" gap={1} mt={3} justifyContent="space-between">
                                                <Button
                                                    variant="outlined"
                                                    size="small"
                                                    startIcon={<FaImage />}
                                                    onClick={() => openDetailDialog(returnRequest)}
                                                >
                                                    Xem chi tiết
                                                </Button>

                                                {returnTab === 0 && returnRequest.status === 'pending' && (
                                                    <Box display="flex" gap={1}>
                                                        <Button
                                                            variant="contained"
                                                            color="success"
                                                            size="small"
                                                            startIcon={<FaCheck />}
                                                            onClick={() => openActionDialog(returnRequest, 'approve')}
                                                            disabled={processingAction}
                                                        >
                                                            Chấp nhận
                                                        </Button>
                                                        <Button
                                                            variant="contained"
                                                            color="error"
                                                            size="small"
                                                            startIcon={<FaTimes />}
                                                            onClick={() => openActionDialog(returnRequest, 'reject')}
                                                            disabled={processingAction}
                                                        >
                                                            Từ chối
                                                        </Button>
                                                    </Box>
                                                )}
                                                {returnTab === 1 && returnRequest.status === 'approved' && (
                                                    <Box display="flex" gap={1}>
                                                        <Button
                                                            variant="contained"
                                                            color="primary"
                                                            size="small"
                                                            startIcon={<FaCheck />}
                                                            onClick={() => completeReturnOrder(returnRequest.id, true)}
                                                            disabled={completingReturn}
                                                        >
                                                            {completingReturn ? 'Đang xử lý...' : 'Xác nhận đã nhận hàng'}
                                                        </Button>
                                                    </Box>
                                                )}
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </ListItem>
                            ))}
                        </List>
                    )}
                </DialogContent>
            </ReturnDialog>

            <Dialog open={actionDialog} onClose={() => setActionDialog(false)} maxWidth="sm" fullWidth>
                <DialogTitle>
                    {actionType === 'approve' ? 'Chấp nhận yêu cầu hoàn trả' : 'Từ chối yêu cầu hoàn trả'}
                </DialogTitle>
                <DialogContent>
                    {selectedReturn && (
                        <Box mb={2}>
                            <Typography variant="body2" gutterBottom>
                                <strong>Đơn hàng:</strong> #{selectedReturn.order?.code}
                            </Typography>
                            <Typography variant="body2" gutterBottom>
                                <strong>Khách hàng:</strong> {selectedReturn.user?.full_name}
                            </Typography>
                            <Typography variant="body2" gutterBottom>
                                <strong>Tổng tiền hoàn trả:</strong> {formatCurrency(selectedReturn.total_refund)}
                            </Typography>
                            <Typography variant="body2" gutterBottom>
                                <strong>Lý do hoàn trả:</strong> {selectedReturn.reason}
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
                            placeholder="Ghi chú về việc chấp nhận hoàn trả..."
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
                            placeholder="Nhập lý do từ chối yêu cầu hoàn trả..."
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
                            processReturnRequest(
                                selectedReturn.id,
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

            <Dialog open={detailDialog} onClose={() => setDetailDialog(false)} maxWidth="md" fullWidth>
                <DialogTitle>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="h6">Chi tiết yêu cầu hoàn trả</Typography>
                        <IconButton onClick={() => setDetailDialog(false)}>
                            <FaTimes />
                        </IconButton>
                    </Box>
                </DialogTitle>
                <DialogContent>
                    {loadingDetail ? (
                        <Box display="flex" justifyContent="center" py={4}>
                            <CircularProgress />
                        </Box>
                    ) : returnDetail ? (
                        <Box>
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={6}>
                                    <Card>
                                        <CardContent>
                                            <Typography variant="h6" gutterBottom>
                                                Thông tin đơn hàng
                                            </Typography>
                                            <Typography variant="body2" gutterBottom>
                                                <strong>Mã đơn hàng:</strong> #{returnDetail.return_order.order?.code}
                                            </Typography>
                                            <Typography variant="body2" gutterBottom>
                                                <strong>Tổng tiền:</strong> {formatCurrency(returnDetail.return_order.order?.total_price)}
                                            </Typography>
                                            <Typography variant="body2" gutterBottom>
                                                <strong>Phương thức thanh toán:</strong> {returnDetail.return_order.order?.payment_method?.toUpperCase()}
                                            </Typography>
                                            <Typography variant="body2" gutterBottom>
                                                <strong>Trạng thái thanh toán:</strong> {returnDetail.return_order.order?.payment_status}
                                            </Typography>
                                            <Typography variant="body2" gutterBottom>
                                                <strong>Ngày giao hàng:</strong> {returnDetail.return_order.order?.delivered_at ?
                                                    new Date(returnDetail.return_order.order.delivered_at).toLocaleString('vi-VN') : 'Chưa giao'}
                                            </Typography>
                                        </CardContent>
                                    </Card>
                                </Grid>

                                <Grid item xs={12} md={6}>
                                    <Card>
                                        <CardContent>
                                            <Typography variant="h6" gutterBottom>
                                                Thông tin khách hàng
                                            </Typography>
                                            <Typography variant="body2" gutterBottom>
                                                <strong>Họ tên:</strong> {returnDetail.return_order.user?.full_name}
                                            </Typography>
                                            <Typography variant="body2" gutterBottom>
                                                <strong>Email:</strong> {returnDetail.return_order.user?.email}
                                            </Typography>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            </Grid>

                            <Card sx={{ mt: 3 }}>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Thông tin hoàn trả
                                    </Typography>
                                    <Grid container spacing={2}>
                                        <Grid item xs={12} sm={6}>
                                            <Typography variant="body2" gutterBottom>
                                                <strong>Trạng thái:</strong>
                                                <StatusChip
                                                    status={returnDetail.return_order.status}
                                                    label={returnDetail.return_order.status}
                                                    size="small"
                                                    sx={{ ml: 1 }}
                                                />
                                            </Typography>
                                            <Typography variant="body2" gutterBottom>
                                                <strong>Ngày tạo:</strong> {new Date(returnDetail.return_order.created_at).toLocaleString('vi-VN')}
                                            </Typography>
                                            {returnDetail.return_order.approved_at && (
                                                <Typography variant="body2" gutterBottom>
                                                    <strong>Ngày chấp nhận:</strong> {new Date(returnDetail.return_order.approved_at).toLocaleString('vi-VN')}
                                                </Typography>
                                            )}
                                            {returnDetail.return_order.rejected_at && (
                                                <Typography variant="body2" gutterBottom>
                                                    <strong>Ngày từ chối:</strong> {new Date(returnDetail.return_order.rejected_at).toLocaleString('vi-VN')}
                                                </Typography>
                                            )}
                                            {returnDetail.return_order.refunded_at && (
                                                <Typography variant="body2" gutterBottom>
                                                    <strong>Ngày hoàn tiền:</strong> {new Date(returnDetail.return_order.refunded_at).toLocaleString('vi-VN')}
                                                </Typography>
                                            )}
                                        </Grid>
                                        <Grid item xs={12} sm={6}>
                                            <Typography variant="body2" gutterBottom>
                                                <strong>Số sản phẩm hoàn trả:</strong> {returnDetail.return_order.return_items?.length || 0}
                                            </Typography>
                                            <Typography variant="body2" gutterBottom>
                                                <strong>Tổng tiền hoàn trả:</strong> {formatCurrency(
                                                    returnDetail.return_order.return_items?.reduce((sum, item) => sum + item.refund_amount, 0) || 0
                                                )}
                                            </Typography>
                                        </Grid>
                                    </Grid>

                                    <Box mt={2}>
                                        <Typography variant="body2" gutterBottom>
                                            <strong>Lý do hoàn trả:</strong>
                                        </Typography>
                                        <Typography variant="body2" sx={{
                                            backgroundColor: '#f5f5f5',
                                            p: 2,
                                            borderRadius: 1,
                                            fontStyle: 'italic'
                                        }}>
                                            {returnDetail.return_order.reason}
                                        </Typography>
                                    </Box>

                                    {returnDetail.return_order.note && (
                                        <Box mt={2}>
                                            <Typography variant="body2" gutterBottom>
                                                <strong>Ghi chú:</strong>
                                            </Typography>
                                            <Typography variant="body2" sx={{
                                                backgroundColor: '#f0f8ff',
                                                p: 2,
                                                borderRadius: 1
                                            }}>
                                                {returnDetail.return_order.note}
                                            </Typography>
                                        </Box>
                                    )}
                                </CardContent>
                            </Card>

                            {/* Return Items */}
                            <Card sx={{ mt: 3 }}>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Sản phẩm hoàn trả
                                    </Typography>
                                    {returnDetail.return_order.return_items?.map((item, index) => (
                                        <Card key={item.id} sx={{ mb: 2, border: '1px solid #e0e0e0' }}>
                                            <CardContent>
                                                <Grid container spacing={2}>
                                                    <Grid item xs={12} sm={8}>
                                                        <Typography variant="body2" gutterBottom>
                                                            <strong>Sản phẩm #{index + 1}</strong>
                                                        </Typography>
                                                        <Typography variant="body2" gutterBottom>
                                                            <strong>Số lượng:</strong> {item.quantity}
                                                        </Typography>
                                                        <Typography variant="body2" gutterBottom>
                                                            <strong>Số tiền hoàn:</strong> {formatCurrency(item.refund_amount)}
                                                        </Typography>
                                                        <Typography variant="body2" gutterBottom>
                                                            <strong>Ngày tạo:</strong> {new Date(item.created_at).toLocaleString('vi-VN')}
                                                        </Typography>
                                                    </Grid>
                                                    <Grid item xs={12} sm={4}>
                                                        {item.images && item.images.length > 0 && (
                                                            <Box>
                                                                <Typography variant="body2" gutterBottom>
                                                                    <strong>Hình ảnh:</strong>
                                                                </Typography>
                                                                <Box display="flex" flexWrap="wrap" gap={1}>
                                                                    {item.images.map((image, imgIndex) => (
                                                                        <Avatar
                                                                            key={imgIndex}
                                                                            src={image}
                                                                            sx={{ width: 60, height: 60 }}
                                                                            variant="rounded"
                                                                        />
                                                                    ))}
                                                                </Box>
                                                            </Box>
                                                        )}
                                                    </Grid>
                                                </Grid>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </CardContent>
                            </Card>

                            {returnDetail.refund_info && (
                                <Card sx={{ mt: 3 }}>
                                    <CardContent>
                                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                                            <Typography variant="h6">
                                                Thông tin hoàn tiền
                                            </Typography>
                                            <Box display="flex" gap={1}>
                                                {(returnDetail.refund_info.status === 'failed' || returnDetail.refund_info.status === 'pending') && (
                                                    <Button
                                                        variant="contained"
                                                        color="warning"
                                                        size="small"
                                                        onClick={() => retryRefund(returnDetail.refund_info.refund_id)}
                                                        disabled={processingRefund}
                                                        startIcon={processingRefund ? <CircularProgress size={16} /> : <FaRedo />}
                                                    >
                                                        {processingRefund ? 'Đang thử lại...' :
                                                            `Thử lại (${returnDetail.refund_info.attempt_count || 1}/5)`}
                                                    </Button>
                                                )}
                                                {(returnDetail.refund_info.status === 'manual_required' ||
                                                    (returnDetail.refund_info.status === 'failed' && returnDetail.refund_info.attempt_count >= 5)) && (
                                                        <>
                                                            <Button
                                                                variant="contained"
                                                                color="success"
                                                                size="small"
                                                                onClick={() => updateRefundStatus(returnDetail.refund_info.refund_id, 'success')}
                                                            >
                                                                Đánh dấu đã hoàn tiền
                                                            </Button>
                                                            <Button
                                                                variant="contained"
                                                                color="error"
                                                                size="small"
                                                                onClick={() => updateRefundStatus(returnDetail.refund_info.refund_id, 'failed')}
                                                            >
                                                                Đánh dấu thất bại
                                                            </Button>
                                                        </>
                                                    )}
                                            </Box>
                                        </Box>

                                        <Grid container spacing={2}>
                                            <Grid item xs={12} sm={6}>
                                                <Typography variant="body2" gutterBottom>
                                                    <strong>Trạng thái hoàn tiền:</strong>
                                                    <Chip
                                                        label={returnDetail.refund_info.status}
                                                        size="small"
                                                        color={
                                                            returnDetail.refund_info.status === 'success' ? 'success' :
                                                                returnDetail.refund_info.status === 'failed' ? 'error' :
                                                                    returnDetail.refund_info.status === 'manual_required' ? 'warning' :
                                                                        'default'
                                                        }
                                                        sx={{ ml: 1 }}
                                                    />
                                                </Typography>
                                                <Typography variant="body2" gutterBottom>
                                                    <strong>Số tiền hoàn:</strong> {formatCurrency(returnDetail.refund_info.amount)}
                                                </Typography>
                                                <Typography variant="body2" gutterBottom>
                                                    <strong>Số lần thử:</strong> {returnDetail.refund_info.attempt_count || 1}/5
                                                </Typography>
                                                <Typography variant="body2" gutterBottom>
                                                    <strong>Ngày tạo:</strong> {new Date(returnDetail.refund_info.created_at).toLocaleString('vi-VN')}
                                                </Typography>
                                            </Grid>
                                            <Grid item xs={12} sm={6}>
                                                {returnDetail.refund_info.response_code && (
                                                    <Typography variant="body2" gutterBottom>
                                                        <strong>Mã phản hồi:</strong> {returnDetail.refund_info.response_code}
                                                    </Typography>
                                                )}
                                            </Grid>
                                        </Grid>

                                        {(returnDetail.refund_info.status === 'manual_required' ||
                                            (returnDetail.refund_info.status === 'failed' && returnDetail.refund_info.attempt_count >= 5)) && (
                                                <Box mt={2} p={2} sx={{ backgroundColor: '#fff3cd', borderRadius: 1, border: '1px solid #ffeaa7' }}>
                                                    <Box display="flex" alignItems="center" gap={1}>
                                                        <FaExclamationTriangle className="text-orange-500" />
                                                        <Typography variant="body2" color="warning.dark" fontWeight="bold">
                                                            Yêu cầu xử lý thủ công
                                                        </Typography>
                                                    </Box>
                                                    <Typography variant="body2" color="warning.dark" mt={1}>
                                                        Hệ thống không thể tự động hoàn tiền sau {returnDetail.refund_info.attempt_count || 1} lần thử.
                                                        Vui lòng xử lý hoàn tiền thủ công và cập nhật trạng thái.
                                                    </Typography>
                                                </Box>
                                            )}
                                    </CardContent>
                                </Card>
                            )}
                        </Box>
                    ) : (
                        <Box textAlign="center" py={4}>
                            <Typography variant="body2" color="textSecondary">
                                Không thể tải chi tiết yêu cầu hoàn trả
                            </Typography>
                        </Box>
                    )}
                </DialogContent>
            </Dialog>
        </>
    );
};

export default ReturnRequestHandler;