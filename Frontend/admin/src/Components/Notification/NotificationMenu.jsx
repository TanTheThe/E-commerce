import React from 'react';
import {
    Menu, Box, Typography, List, ListItem, CircularProgress,
    IconButton, Chip, Pagination, Tooltip
} from '@mui/material';
import { FaBell, FaShoppingCart, FaUser, FaCog, FaEye, FaExclamationTriangle } from 'react-icons/fa';
import { MdDoneAll, MdDone } from 'react-icons/md';
import { styled } from '@mui/material';

const StyledNotificationMenu = styled(Menu)(({ theme }) => ({
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

const NotificationMenu = ({
    anchorEl,
    open,
    onClose,
    notifications,
    loading,
    markingAsRead,
    filters,
    currentPage,
    totalNotifications,
    itemsPerPage,
    onMarkAllAsRead,
    onFilterChange,
    onPageChange,
    onMarkAsRead,
    onNotificationAction
}) => {
    return (
        <StyledNotificationMenu
            anchorEl={anchorEl}
            open={open}
            onClose={onClose}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
            <NotificationHeader>
                <Typography variant="h6" sx={{ fontSize: '16px', fontWeight: 600 }}>
                    Thông báo
                </Typography>
                <Box display="flex" gap={1}>
                    <Tooltip title="Đánh dấu tất cả đã đọc">
                        <IconButton size="small" onClick={onMarkAllAsRead} disabled={markingAsRead}>
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
                        onClick={() => onFilterChange({ unread_only: false, action_required: false })}
                        sx={{ fontSize: '12px' }}
                    />
                    <Chip
                        label="Chưa đọc"
                        size="small"
                        variant={filters.unread_only ? "filled" : "outlined"}
                        onClick={() => onFilterChange({ unread_only: true, action_required: false })}
                        sx={{ fontSize: '12px' }}
                    />
                    <Chip
                        label="Cần xử lý"
                        size="small"
                        variant={filters.action_required ? "filled" : "outlined"}
                        onClick={() => onFilterChange({ unread_only: false, action_required: true })}
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
                                                            onClick={() => onMarkAsRead([notification.id])}
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
                                                            onClick={() => onNotificationAction(notification)}
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
                        onChange={onPageChange}
                        size="small"
                        color="primary"
                    />
                </Box>
            )}
        </StyledNotificationMenu>
    );
};

export default NotificationMenu;