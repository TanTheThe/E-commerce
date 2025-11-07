import React from 'react';
import { FaShoppingCart, FaUser, FaCog, FaBell, FaExclamationTriangle, FaEye } from 'react-icons/fa';
import { MdDone, MdDoneAll } from 'react-icons/md';

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
    if (!open) return null;

    const totalPages = Math.ceil(totalNotifications / itemsPerPage);

    return (
        <>
            <div
                className="fixed inset-0 z-40"
                onClick={onClose}
            />

            <div className="fixed top-16 right-4 w-[420px] max-w-[90vw] bg-white rounded-2xl shadow-2xl border border-gray-100 z-50 overflow-hidden">
                <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-5 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                                <FaBell className="text-white text-sm" />
                            </div>
                            <h3 className="text-white font-semibold text-lg">Thông báo</h3>
                        </div>
                        <button
                            onClick={onMarkAllAsRead}
                            disabled={markingAsRead}
                            className="text-white/90 hover:text-white hover:bg-white/10 p-2 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            title="Đánh dấu tất cả đã đọc"
                        >
                            {markingAsRead ? (
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <MdDoneAll className="text-lg" />
                            )}
                        </button>
                    </div>
                </div>

                <div className="px-5 py-3 bg-gray-50 border-b border-gray-200">
                    <div className="flex gap-2">
                        <button
                            onClick={() => onFilterChange({ unread_only: false, action_required: false })}
                            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${!filters.unread_only && !filters.action_required
                                    ? 'bg-blue-600 text-white shadow-sm'
                                    : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
                                }`}
                        >
                            Tất cả
                        </button>
                        <button
                            onClick={() => onFilterChange({ unread_only: true, action_required: false })}
                            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${filters.unread_only
                                    ? 'bg-blue-600 text-white shadow-sm'
                                    : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
                                }`}
                        >
                            Chưa đọc
                        </button>
                        <button
                            onClick={() => onFilterChange({ unread_only: false, action_required: true })}
                            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${filters.action_required
                                    ? 'bg-orange-500 text-white shadow-sm'
                                    : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
                                }`}
                        >
                            Cần xử lý
                        </button>
                    </div>
                </div>

                <div className="max-h-[400px] overflow-y-auto">
                    {loading ? (
                        <div className="flex justify-center items-center py-12">
                            <div className="w-8 h-8 border-3 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
                        </div>
                    ) : notifications.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-12 text-center">
                            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-3">
                                <FaBell className="text-gray-400 text-2xl" />
                            </div>
                            <p className="text-gray-500 text-sm">Không có thông báo nào</p>
                        </div>
                    ) : (
                        <div className="divide-y divide-gray-100">
                            {notifications.map((notification) => (
                                <div
                                    key={notification.id}
                                    className={`p-4 transition-colors hover:bg-gray-50 ${!notification.is_read ? 'bg-blue-50/50' : 'bg-white'
                                        }`}
                                >
                                    <div className="flex gap-3">
                                        <div className="flex-shrink-0 mt-0.5">
                                            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${notification.action_type ? 'bg-orange-100' :
                                                    notification.type === 'order' ? 'bg-blue-100' :
                                                        notification.type === 'user' ? 'bg-green-100' :
                                                            'bg-gray-100'
                                                }`}>
                                                {getNotificationIcon(notification.type, notification.action_type)}
                                            </div>
                                        </div>

                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-start justify-between gap-2 mb-1">
                                                <h4 className={`text-sm flex-1 ${notification.is_read ? 'text-gray-700 font-normal' : 'text-gray-900 font-semibold'
                                                    }`}>
                                                    {notification.title}
                                                </h4>
                                                <span className="text-xs text-gray-500 whitespace-nowrap">
                                                    {formatRelativeTime(notification.created_at)}
                                                </span>
                                            </div>

                                            <p className="text-xs text-gray-600 mb-2 line-clamp-2">
                                                {notification.message}
                                            </p>

                                            <div className="flex items-center justify-between">
                                                <div className="flex gap-1.5">
                                                    {notification.action_type && !notification.is_processed && (
                                                        <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-orange-100 text-orange-700">
                                                            {notification.action_type}
                                                        </span>
                                                    )}
                                                    {notification.is_processed && (
                                                        <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-green-100 text-green-700">
                                                            Đã xử lý
                                                        </span>
                                                    )}
                                                </div>

                                                <div className="flex gap-1">
                                                    {!notification.is_read && (
                                                        <button
                                                            onClick={() => onMarkAsRead([notification.id])}
                                                            className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
                                                            title="Đánh dấu đã đọc"
                                                        >
                                                            <MdDone className="text-sm" />
                                                        </button>
                                                    )}
                                                    {notification.action_type && !notification.is_processed && (
                                                        <button
                                                            onClick={() => onNotificationAction(notification)}
                                                            className="p-1.5 text-gray-500 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-all"
                                                            title="Xem chi tiết"
                                                        >
                                                            <FaEye className="text-xs" />
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {notifications.length > 0 && totalPages > 1 && (
                    <div className="px-5 py-3 bg-gray-50 border-t border-gray-200">
                        <div className="flex items-center justify-center gap-1">
                            <button
                                onClick={(e) => onPageChange(e, Math.max(1, currentPage - 1))}
                                disabled={currentPage === 1}
                                className="px-3 py-1.5 rounded-lg text-sm font-medium text-gray-700 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                            >
                                ‹
                            </button>

                            {[...Array(totalPages)].map((_, i) => {
                                const page = i + 1;
                                if (
                                    page === 1 ||
                                    page === totalPages ||
                                    (page >= currentPage - 1 && page <= currentPage + 1)
                                ) {
                                    return (
                                        <button
                                            key={page}
                                            onClick={(e) => onPageChange(e, page)}
                                            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${currentPage === page
                                                    ? 'bg-blue-600 text-white shadow-sm'
                                                    : 'text-gray-700 hover:bg-white'
                                                }`}
                                        >
                                            {page}
                                        </button>
                                    );
                                } else if (
                                    page === currentPage - 2 ||
                                    page === currentPage + 2
                                ) {
                                    return <span key={page} className="px-1 text-gray-400">...</span>;
                                }
                                return null;
                            })}

                            <button
                                onClick={(e) => onPageChange(e, Math.min(totalPages, currentPage + 1))}
                                disabled={currentPage === totalPages}
                                className="px-3 py-1.5 rounded-lg text-sm font-medium text-gray-700 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                            >
                                ›
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </>
    );
};

export default NotificationMenu;