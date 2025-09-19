import React, { useState, useContext, useEffect } from 'react';
import {
    IconButton, Box, Typography, List, CircularProgress,
    Tooltip, Chip, Pagination
} from '@mui/material';
import { FaRegBell, FaBell, FaEye } from 'react-icons/fa';
import { MdDoneAll, MdDone } from 'react-icons/md';
import { styled, Badge } from '@mui/material';
import { MyContext } from '../../App';
import { getDataApi, postDataApi } from '../../utils/api';
import NotificationMenu from './NotificationMenu';
import CancellationHandler from './CancellationHandler';
import ReturnRequestHandler from './ReturnRequestHandler';

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

const NotificationDropdown = () => {
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
    const [returnRequestDialog, setReturnRequestDialog] = useState(false);

    const openNotification = Boolean(anchorNotification);
    const context = useContext(MyContext);
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

    const handleNotificationAction = async (notification) => {
        if (notification.action_type && notification.order_id) {
            if (notification.action_type === 'handle_cancellation') {
                setCancellationDialog(true);
            } else if (notification.action_type === 'handle_return') {
                setReturnRequestDialog(true);
            }
        } else {
            console.log('Condition not met - missing action_type or order_id');
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

    // Auto refresh counts
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

    const totalBadgeCount = unreadCount;

    return (
        <>
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
                notifications={notifications}
                loading={loading}
                markingAsRead={markingAsRead}
                filters={filters}
                currentPage={currentPage}
                totalNotifications={totalNotifications}
                itemsPerPage={itemsPerPage}
                onMarkAllAsRead={markAllAsRead}
                onFilterChange={handleFilterChange}
                onPageChange={handlePageChange}
                onMarkAsRead={markAsRead}
                onNotificationAction={handleNotificationAction}
            />

            <CancellationHandler
                open={cancellationDialog}
                onClose={() => setCancellationDialog(false)}
                onProcessed={async () => {
                    await fetchPendingActionsCount();
                    await fetchNotifications(currentPage, filters);
                }}
                onMarkAsProcessed={markAsProcessed}
                notifications={notifications}
            />
            <ReturnRequestHandler
                open={returnRequestDialog}
                onClose={() => setReturnRequestDialog(false)}
                onProcessed={async () => {
                    await fetchPendingActionsCount();
                    await fetchNotifications(currentPage, filters);
                }}
                onMarkAsProcessed={markAsProcessed}
                notifications={notifications}
            />
        </>
    );
};

export default NotificationDropdown;