import React, { useState, useContext, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
    Button,
    IconButton,
    Badge,
    Menu,
    MenuItem,
    Divider,
    Box,
    Typography,
    List,
    ListItem,
    ListItemText,
    ListItemSecondaryAction,
    Chip,
    Tooltip,
    CircularProgress,
    Pagination,
    Dialog,
    DialogTitle,
    DialogContent,
    Tabs,
    Tab,
    TextField,
    DialogActions
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
    FaRegBell,
    FaRegUser,
    FaBell,
    FaCheck,
    FaCheckDouble,
    FaExclamationTriangle,
    FaShoppingCart,
    FaUser,
    FaCog,
    FaTimes,
    FaEye
} from 'react-icons/fa';
import { IoMdLogOut } from 'react-icons/io';
import { RiMenu2Fill, RiMenu3Fill } from 'react-icons/ri';
import { MdMarkAsUnread, MdDone, MdDoneAll } from 'react-icons/md';
import { fetchWithAutoRefresh, getDataApi, postDataApi } from '../../utils/api';
import { MyContext } from "../../App";


const StyledBadge = styled(Badge)(({ theme }) => ({
    '& .MuiBadge-badge': {
        right: -3,
        top: 13,
        border: `2px solid ${theme.palette.background.paper}`,
        padding: '0 4px',
        backgroundColor: '#ff4444',
        color: 'white',
        fontWeight: 'bold'
    },
}));

const NotificationMenu = styled(Menu)(({ theme }) => ({
    '& .MuiPaper-root': {
        width: '420px',
        maxWidth: '90vw',
        maxHeight: '600px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
        borderRadius: '12px',
        border: '1px solid #e0e0e0'
    }
}));

const NotificationItem = styled(ListItem)(({ theme, isread }) => ({
    padding: '16px',
    borderBottom: '1px solid #f0f0f0',
    backgroundColor: isread === 'false' ? '#f8f9ff' : 'white',
    '&:hover': {
        backgroundColor: '#f5f5f5'
    },
    '&:last-child': {
        borderBottom: 'none'
    }
}));

const NotificationHeader = styled(Box)(({ theme }) => ({
    padding: '16px',
    borderBottom: '1px solid #e0e0e0',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fafafa'
}));

const CancellationDialog = styled(Dialog)(({ theme }) => ({
    '& .MuiDialog-paper': {
        width: '800px',
        maxWidth: '90vw',
        maxHeight: '80vh'
    }
}));

const getNotificationIcon = (type, actionType) => {
    if (actionType) {
        return <FaExclamationTriangle className="text-orange-500" />;
    }

    switch (type) {
        case 'order':
            return <FaShoppingCart className="text-blue-500" />;
        case 'user':
            return <FaUser className="text-green-500" />;
        case 'system':
            return <FaCog className="text-gray-500" />;
        default:
            return <FaBell className="text-blue-500" />;
    }
};

const formatRelativeTime = (dateString) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));

    if (diffInMinutes < 1) return 'Vừa xong';
    if (diffInMinutes < 60) return `${diffInMinutes} phút trước`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} giờ trước`;
    return `${Math.floor(diffInMinutes / 1440)} ngày trước`;
};

const Header = () => {
    const [anchorMyAcc, setAnchorMyAcc] = useState(null);
    const [anchorNotification, setAnchorNotification] = useState(null);
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [pendingActionsCount, setPendingActionsCount] = useState(0);
    const [loading, setLoading] = useState(false);
    const [markingAsRead, setMarkingAsRead] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalNotifications, setTotalNotifications] = useState(0);
    const [filters, setFilters] = useState({
        unread_only: false,
        action_required: false
    });

    const [cancellationDialog, setCancellationDialog] = useState(false);
    const [cancellationRequests, setCancellationRequests] = useState([]);
    const [loadingCancellations, setLoadingCancellations] = useState(false);
    const [cancellationTab, setCancellationTab] = useState(0);
    const [selectedOrder, setSelectedOrder] = useState(null);
    const [actionDialog, setActionDialog] = useState(false);
    const [actionType, setActionType] = useState('');
    const [adminNote, setAdminNote] = useState('');
    const [rejectReason, setRejectReason] = useState('');
    const [processingAction, setProcessingAction] = useState(false);

    const openMyAcc = Boolean(anchorMyAcc);
    const openNotification = Boolean(anchorNotification);
    const context = useContext(MyContext);
    const navigate = useNavigate();

    const itemsPerPage = 10;

    const fetchNotifications = async (page = 1, filterOptions = filters) => {
        setLoading(true);
        try {
            const skip = (page - 1) * itemsPerPage;
            const queryParams = new URLSearchParams({
                skip,
                limit: itemsPerPage,
                ...filterOptions
            });

            const response = await getDataApi(`/admin/notification/?${queryParams}`);
            if (response.success) {
                setNotifications(response.data.data);
                setTotalNotifications(response.data.total);
            }
        } catch (error) {
            console.error('Error fetching notifications:', error);
            context.openAlertBox("error", "Không thể tải thông báo");
        } finally {
            setLoading(false);
        }
    };

    const fetchUnreadCount = async () => {
        try {
            const response = await getDataApi('/admin/notification/unread-count');
            if (response.success) {
                setUnreadCount(response.data.unread_count);
            }
        } catch (error) {
            console.error('Error fetching unread count:', error);
        }
    };

    const fetchPendingActionsCount = async () => {
        try {
            const response = await getDataApi('/admin/notification/pending-actions-count');
            if (response.success) {
                setPendingActionsCount(response.data.pending_actions_count);
            }
        } catch (error) {
            console.error('Error fetching pending actions count:', error);
        }
    };

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

    const markAsRead = async (notificationIds) => {
        setMarkingAsRead(true);
        try {
            const response = await postDataApi('/admin/notification/mark-read', {
                notification_ids: notificationIds
            });

            if (response.success) {
                setNotifications(prev =>
                    prev.map(notif =>
                        notificationIds.includes(notif.id)
                            ? { ...notif, is_read: true, read_at: new Date().toISOString() }
                            : notif
                    )
                );

                await fetchUnreadCount();
                context.openAlertBox("success", response.message);
            }
        } catch (error) {
            console.error('Error marking as read:', error);
            context.openAlertBox("error", "Không thể đánh dấu đã đọc");
        } finally {
            setMarkingAsRead(false);
        }
    };

    const markAsProcessed = async (notificationId) => {
        try {
            const response = await postDataApi('/admin/notification/mark-processed', {
                notification_id: notificationId
            });

            if (response.success) {
                setNotifications(prev =>
                    prev.map(notif =>
                        notif.id === notificationId
                            ? { ...notif, is_processed: true, processed_at: new Date().toISOString() }
                            : notif
                    )
                );

                await fetchPendingActionsCount();
            }
        } catch (error) {
            console.error('Error marking as processed:', error);
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

                await fetchPendingActionsCount();
                await fetchNotifications(currentPage, filters);

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
                await markAsProcessed(relatedNotification.id);
            }
        } catch (error) {
            console.error('Error auto-marking notification:', error);
        }
    };

    const handleNotificationAction = async (notification) => {
        if (notification.action_type && notification.order_id) {
            setCancellationDialog(true);
            setCancellationTab(0); 
            await fetchCancellationRequests('pending');
        }
    };

    const handleClickNotification = (event) => {
        setAnchorNotification(event.currentTarget);
        if (notifications.length === 0) {
            fetchNotifications(1, filters);
        }
    };

    const handleCloseNotification = () => {
        setAnchorNotification(null);
    };

    const handleClickMyAcc = (event) => {
        setAnchorMyAcc(event.currentTarget);
    };

    const handleCloseMyAcc = () => {
        setAnchorMyAcc(null);
    };

    const markAllAsRead = async () => {
        const unreadIds = notifications.filter(n => !n.is_read).map(n => n.id);
        if (unreadIds.length > 0) {
            await markAsRead(unreadIds);
        }
    };

    const handleFilterChange = (newFilters) => {
        setFilters(newFilters);
        setCurrentPage(1);
        fetchNotifications(1, newFilters);
    };

    const handlePageChange = (event, page) => {
        setCurrentPage(page);
        fetchNotifications(page, filters);
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

    useEffect(() => {
        if (context.isLogin) {
            fetchUnreadCount();
            fetchPendingActionsCount();

            const interval = setInterval(() => {
                fetchUnreadCount();
                fetchPendingActionsCount();
            }, 30000); 

            return () => clearInterval(interval);
        }
    }, [context.isLogin]);

    const logout = async () => {
        setAnchorMyAcc(null);

        const response = await fetchWithAutoRefresh("/admin/auth/logout", "GET");

        if (response?.success === true) {
            localStorage.clear();
            sessionStorage.clear();
            context.setIsLogin(false);
            context.setUserData(null);
            navigate("/login");
        } else {
            context.openAlertBox("error", response?.data?.detail.message);
            localStorage.clear();
            sessionStorage.clear();
            context.setIsLogin(false);
            context.setUserData(null);
            navigate("/login");
        }
    };

    const totalBadgeCount = unreadCount;

    return (
        <>
            <header className={`w-full h-[auto] py-2 ${context.isSidebarOpen === true ? 'pl-72' : 'pl-5'} pr-5 shadow-md bg-[#fff] flex items-center justify-between transition-all`}>
                <div className="part1">
                    <Button className="!w-[40px] !h-[40px] !rounded-full !min-w-[40px] !text-[rgba(0,0,0,0.8)]" onClick={() => context.setIsSidebarOpen(!context.isSidebarOpen)}>
                        {context.isSidebarOpen === true ?
                            <RiMenu2Fill className="text-[18px] text-[rgba(0,0,0,0.8)]" />
                            :
                            <RiMenu3Fill className="text-[18px] text-[rgba(0,0,0,0.8)]" />
                        }
                    </Button>
                </div>

                <div className="part2 w-[40%] flex items-center justify-end gap-5">
                    <Tooltip title="Thông báo">
                        <IconButton aria-label="notifications" onClick={handleClickNotification}>
                            <StyledBadge badgeContent={totalBadgeCount > 0 ? totalBadgeCount : null} color="error">
                                <FaRegBell className="text-[18px]" />
                            </StyledBadge>
                        </IconButton>
                    </Tooltip>

                    <NotificationMenu
                        anchorEl={anchorNotification}
                        open={openNotification}
                        onClose={handleCloseNotification}
                        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                    >
                        <NotificationHeader>
                            <Typography variant="h6" sx={{ fontSize: '16px', fontWeight: 600 }}>
                                Thông báo
                            </Typography>
                            <Box display="flex" gap={1}>
                                <Tooltip title="Đánh dấu tất cả đã đọc">
                                    <IconButton size="small" onClick={markAllAsRead} disabled={markingAsRead}>
                                        {markingAsRead ? <CircularProgress size={16} /> : <MdDoneAll />}
                                    </IconButton>
                                </Tooltip>
                            </Box>
                        </NotificationHeader>

                        <Box sx={{ px: 2, py: 1, borderBottom: '1px solid #e0e0e0' }}>
                            <Box display="flex" gap={1}>
                                <Chip
                                    label="Tất cả"
                                    size="small"
                                    variant={!filters.unread_only && !filters.action_required ? "filled" : "outlined"}
                                    onClick={() => handleFilterChange({ unread_only: false, action_required: false })}
                                    sx={{ fontSize: '12px' }}
                                />
                                <Chip
                                    label="Chưa đọc"
                                    size="small"
                                    variant={filters.unread_only ? "filled" : "outlined"}
                                    onClick={() => handleFilterChange({ unread_only: true, action_required: false })}
                                    sx={{ fontSize: '12px' }}
                                />
                                <Chip
                                    label="Cần xử lý"
                                    size="small"
                                    variant={filters.action_required ? "filled" : "outlined"}
                                    onClick={() => handleFilterChange({ unread_only: false, action_required: true })}
                                    sx={{ fontSize: '12px' }}
                                    color="warning"
                                />
                            </Box>
                        </Box>

                        <Box sx={{ maxHeight: '400px', overflowY: 'auto' }}>
                            {loading ? (
                                <Box display="flex" justifyContent="center" alignItems="center" py={4}>
                                    <CircularProgress />
                                </Box>
                            ) : notifications.length === 0 ? (
                                <Box textAlign="center" py={4}>
                                    <FaBell className="text-gray-400 text-2xl mb-2" />
                                    <Typography variant="body2" color="textSecondary">
                                        Không có thông báo nào
                                    </Typography>
                                </Box>
                            ) : (
                                <List sx={{ p: 0 }}>
                                    {notifications.map((notification) => (
                                        <NotificationItem
                                            key={notification.id}
                                            isread={notification.is_read.toString()}
                                        >
                                            <Box display="flex" alignItems="flex-start" gap={2} width="100%">
                                                <Box sx={{ mt: 0.5 }}>
                                                    {getNotificationIcon(notification.type, notification.action_type)}
                                                </Box>

                                                <Box flex={1}>
                                                    <Box display="flex" justifyContent="between" alignItems="flex-start" mb={0.5}>
                                                        <Typography
                                                            variant="subtitle2"
                                                            sx={{
                                                                fontWeight: notification.is_read ? 400 : 600,
                                                                fontSize: '14px',
                                                                flex: 1
                                                            }}
                                                        >
                                                            {notification.title}
                                                        </Typography>
                                                        <Typography variant="caption" color="textSecondary" sx={{ fontSize: '11px', ml: 1 }}>
                                                            {formatRelativeTime(notification.created_at)}
                                                        </Typography>
                                                    </Box>

                                                    <Typography
                                                        variant="body2"
                                                        color="textSecondary"
                                                        sx={{ fontSize: '13px', mb: 1 }}
                                                    >
                                                        {notification.message}
                                                    </Typography>

                                                    <Box display="flex" justifyContent="between" alignItems="center">
                                                        <Box display="flex" gap={0.5}>
                                                            {notification.action_type && !notification.is_processed && (
                                                                <Chip
                                                                    label={notification.action_type}
                                                                    size="small"
                                                                    color="warning"
                                                                    sx={{ fontSize: '10px', height: '20px' }}
                                                                />
                                                            )}
                                                            {notification.is_processed && (
                                                                <Chip
                                                                    label="Đã xử lý"
                                                                    size="small"
                                                                    color="success"
                                                                    sx={{ fontSize: '10px', height: '20px' }}
                                                                />
                                                            )}
                                                        </Box>

                                                        <Box display="flex" gap={0.5}>
                                                            {!notification.is_read && (
                                                                <Tooltip title="Đánh dấu đã đọc">
                                                                    <IconButton
                                                                        size="small"
                                                                        onClick={() => markAsRead([notification.id])}
                                                                        sx={{ padding: '2px' }}
                                                                    >
                                                                        <MdDone fontSize="14px" />
                                                                    </IconButton>
                                                                </Tooltip>
                                                            )}
                                                            {notification.action_type && !notification.is_processed && (
                                                                <Tooltip title="Xem chi tiết">
                                                                    <IconButton
                                                                        size="small"
                                                                        onClick={() => handleNotificationAction(notification)}
                                                                        sx={{ padding: '2px' }}
                                                                    >
                                                                        <FaEye fontSize="12px" />
                                                                    </IconButton>
                                                                </Tooltip>
                                                            )}
                                                        </Box>
                                                    </Box>
                                                </Box>
                                            </Box>
                                        </NotificationItem>
                                    ))}
                                </List>
                            )}
                        </Box>

                        {notifications.length > 0 && Math.ceil(totalNotifications / itemsPerPage) > 1 && (
                            <Box display="flex" justifyContent="center" p={2} borderTop="1px solid #e0e0e0">
                                <Pagination
                                    count={Math.ceil(totalNotifications / itemsPerPage)}
                                    page={currentPage}
                                    onChange={handlePageChange}
                                    size="small"
                                    color="primary"
                                />
                            </Box>
                        )}
                    </NotificationMenu>

                    {context.isLogin === true ? (
                        <div className="relative">
                            <div className="rounded-full w-[35px] h-[35px] overflow-hidden cursor-pointer" onClick={handleClickMyAcc}>
                                <img src="https://thethaovanhoa.mediacdn.vn/372676912336973824/2022/12/16/avatar3-1671164179193908857633.jpg" className="w-full h-full object-cover" />
                            </div>

                            <Menu
                                anchorEl={anchorMyAcc}
                                id="account-menu"
                                open={openMyAcc}
                                onClose={handleCloseMyAcc}
                                onClick={handleCloseMyAcc}
                                slotProps={{
                                    paper: {
                                        elevation: 0,
                                        sx: {
                                            overflow: 'visible',
                                            filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
                                            mt: 1.5,
                                            '& .MuiAvatar-root': {
                                                width: 32,
                                                height: 32,
                                                ml: -0.5,
                                                mr: 1,
                                            },
                                            '&::before': {
                                                content: '""',
                                                display: 'block',
                                                position: 'absolute',
                                                top: 0,
                                                right: 14,
                                                width: 10,
                                                height: 10,
                                                bgcolor: 'background.paper',
                                                transform: 'translateY(-50%) rotate(45deg)',
                                                zIndex: 0,
                                            },
                                        },
                                    },
                                }}
                                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                            >
                                <MenuItem onClick={handleCloseMyAcc} className="!bg-white">
                                    <div className="flex items-center gap-3">
                                        <div className="rounded-full w-[35px] h-[35px] overflow-hidden cursor-pointer">
                                            <img src="https://thethaovanhoa.mediacdn.vn/372676912336973824/2022/12/16/avatar3-1671164179193908857633.jpg" className="w-full h-full object-cover" />
                                        </div>
                                        <div className="info">
                                            <h3 className="text-[15px] font-[500] leading-5">
                                                {context?.userData?.content?.first_name || context?.userData?.first_name} {context?.userData?.content?.last_name || context?.userData?.last_name}
                                            </h3>
                                            <p className="text-[12px] font-[400] opacity-70">
                                                {context?.userData?.content?.email || context?.userData?.email}
                                            </p>
                                        </div>
                                    </div>
                                </MenuItem>
                                <Divider />
                                <Link to="/profile">
                                    <MenuItem onClick={handleCloseMyAcc} className="flex items-center gap-3">
                                        <FaRegUser className="text-[16px]" />
                                        <span className="text-[14px]">Profile</span>
                                    </MenuItem>
                                </Link>
                                <MenuItem onClick={logout} className="flex items-center gap-3">
                                    <IoMdLogOut className="text-[18px]" />
                                    <span className="text-[14px]">Sign Out</span>
                                </MenuItem>
                            </Menu>
                        </div>
                    ) : (
                        <Button className="btn-blue btn-sm !rounded-full" onClick={() => navigate("/login")}>
                            Sign In
                        </Button>
                    )}
                </div>
            </header>

            <CancellationDialog
                open={cancellationDialog}
                onClose={() => setCancellationDialog(false)}
                maxWidth={false}
            >
                <DialogTitle>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="h6">Yêu cầu hủy đơn hàng</Typography>
                        <IconButton onClick={() => setCancellationDialog(false)}>
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

export default Header;