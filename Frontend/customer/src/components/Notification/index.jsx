import React, { useState, useEffect } from 'react';
import { Menu, MenuItem, IconButton, Badge, Tooltip, Button } from '@mui/material';
import { FaChevronLeft, FaChevronRight, FaRegBell } from 'react-icons/fa';
import { Link } from 'react-router-dom';
import { getDataApi, postDataApi } from '../../utils/api';

const NotificationMenu = () => {
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [notificationAnchorEl, setNotificationAnchorEl] = useState(null);
    const [loadingNotifications, setLoadingNotifications] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [isMarkingAllRead, setIsMarkingAllRead] = useState(false);
    const notificationOpen = Boolean(notificationAnchorEl);
    const itemsPerPage = 10;

    const fetchUnreadCount = async () => {
        try {
            const res = await getDataApi("/customer/notification/unread-count");
            if (res.success) {
                setUnreadCount(res.data.unread_count);
            }
        } catch (error) {
            console.error("Error fetching unread count:", error);
        }
    };

    const fetchNotifications = async (page = 1, unreadOnly = false) => {
        try {
            setLoadingNotifications(true);
            const skip = (page - 1) * itemsPerPage;
            const res = await getDataApi(`/customer/notification/?unread_only=${unreadOnly}&skip=${skip}&limit=${itemsPerPage}`);
            if (res.success) {
                setNotifications(res.data.data || []);
                setTotalPages(Math.ceil((res.data.total || 0) / itemsPerPage));
                setCurrentPage(page);
            }
        } catch (error) {
            console.error("Error fetching notifications:", error);
        } finally {
            setLoadingNotifications(false);
        }
    };

    const markAsRead = async (notificationIds) => {
        try {
            const res = await postDataApi("/customer/notification/mark-read", {
                notification_ids: notificationIds
            });
            if (res.success) {
                await fetchUnreadCount();
                await fetchNotifications(currentPage);
            }
        } catch (error) {
            console.error("Error marking as read:", error);
        }
    };

    const markAllAsRead = async () => {
        try {
            setIsMarkingAllRead(true);
            const res = await postDataApi("/customer/notification/mark-all-read", {});

            if (res.success) {
                await fetchUnreadCount();
                await fetchNotifications(currentPage);
            }
        } catch (error) {
            console.error("Error marking all as read:", error);
        } finally {
            setIsMarkingAllRead(false);
        }
    };

    const handleNotificationClick = (event) => {
        setNotificationAnchorEl(event.currentTarget);
        if (notifications.length === 0) {
            fetchNotifications(1);
        }
    };

    const handleNotificationClose = () => {
        setNotificationAnchorEl(null);
        setCurrentPage(1);
    };

    const handlePageChange = (newPage) => {
        if (newPage >= 1 && newPage <= totalPages && !loadingNotifications) {
            fetchNotifications(newPage);
        }
    };

    const handleMarkAllAsRead = () => {
        if (unreadCount > 0 && !isMarkingAllRead) {
            markAllAsRead();
        }
    };

    useEffect(() => {
        fetchUnreadCount();

        const interval = setInterval(() => {
            fetchUnreadCount();
        }, 30000);

        return () => clearInterval(interval);
    }, []);

    return (
        <>
            <Tooltip title="Thông báo" placement="bottom">
                <IconButton
                    aria-label="notifications"
                    onClick={handleNotificationClick}
                    className="relative"
                >
                    <Badge badgeContent={unreadCount} color="secondary">
                        <FaRegBell />
                    </Badge>
                </IconButton>
            </Tooltip>

            <Menu
                anchorEl={notificationAnchorEl}
                open={notificationOpen}
                onClose={handleNotificationClose}
                slotProps={{
                    paper: {
                        elevation: 0,
                        sx: {
                            overflow: 'visible',
                            filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
                            mt: 1.5,
                            width: 350,
                            maxHeight: 400,
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
                <div className="p-3 border-b">
                    <div className="flex justify-between items-center">
                        <h6 className="text-sm font-medium">Thông báo</h6>
                        {unreadCount > 0 && (
                            <button
                                onClick={handleMarkAllAsRead}
                                disabled={isMarkingAllRead}
                                className={`text-xs text-blue-600 hover:underline ${isMarkingAllRead ? 'opacity-50 cursor-not-allowed' : ''}`}
                            >
                                {isMarkingAllRead ? 'Đang xử lý...' : 'Đánh dấu tất cả đã đọc'}
                            </button>
                        )}
                    </div>
                </div>

                <div className="max-h-80 overflow-y-auto">
                    {loadingNotifications ? (
                        <div className="p-4 text-center">
                            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                        </div>
                    ) : notifications.length === 0 ? (
                        <div className="p-4 text-center text-gray-500">
                            <p className="text-sm">Không có thông báo nào</p>
                        </div>
                    ) : (
                        notifications.map((notification) => (
                            <MenuItem
                                key={notification.id}
                                className={`!p-3 !border-b border-gray-100 !whitespace-normal ${!notification.is_read ? 'bg-blue-50' : ''}`}
                                onClick={() => {
                                    if (!notification.is_read) {
                                        markAsRead([notification.id]);
                                    }
                                    handleNotificationClose();
                                }}
                            >
                                <div className="w-full">
                                    <div className="flex items-start gap-2">
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-gray-900 mb-1">
                                                {notification.title}
                                            </p>
                                            <p className="text-xs text-gray-600 line-clamp-2">
                                                {notification.message}
                                            </p>
                                            <p className="text-xs text-gray-400 mt-1">
                                                {new Date(notification.created_at).toLocaleDateString('vi-VN')}
                                            </p>
                                        </div>
                                        {!notification.is_read && (
                                            <div className="w-2 h-2 bg-blue-600 rounded-full mt-1 flex-shrink-0"></div>
                                        )}
                                    </div>
                                </div>
                            </MenuItem>
                        ))
                    )}
                </div>

                <div className="border-t">
                    <div className="flex justify-between items-center">
                        <div className="flex items-center gap-2">
                            <Button
                                size="small"
                                onClick={() => handlePageChange(currentPage - 1)}
                                disabled={currentPage === 1 || loadingNotifications}
                                className="!min-w-0 !px-2"
                            >
                                <FaChevronLeft className="text-xs" />
                            </Button>

                            <span className="text-xs text-gray-600">
                                Trang {currentPage}/{totalPages}
                            </span>

                            <Button
                                size="small"
                                onClick={() => handlePageChange(currentPage + 1)}
                                disabled={currentPage === totalPages || loadingNotifications}
                                className="!min-w-0 !px-2"
                            >
                                <FaChevronRight className="text-xs" />
                            </Button>
                        </div>

                        <span className="text-xs text-gray-500">
                            Tổng: {unreadCount} chưa đọc
                        </span>
                    </div>
                </div>
            </Menu>
        </>
    );
};

export default NotificationMenu;