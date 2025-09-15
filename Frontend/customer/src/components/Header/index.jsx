import React, { useCallback, useContext, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Search from "../Search";
import Button from "@mui/material/Button";
import Badge from "@mui/material/Badge";
import { styled } from "@mui/material/styles";
import IconButton from "@mui/material/IconButton";
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart"
import { MdOutlineShoppingCart } from "react-icons/md";
import { IoIosGitCompare, IoIosLogOut, IoMdHeartEmpty } from "react-icons/io";
import { FaRegBell, FaRegHeart, FaRegUser } from "react-icons/fa";
import { Tooltip } from "@mui/material";
import Navigation from "./Navigation";
import { MyContext } from "../../App";

import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import { IoBagCheckOutline, IoNotifications } from "react-icons/io5";
import { getDataApi, fetchWithAutoRefresh, postDataApi } from "../../utils/api";


const Header = () => {
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [notificationAnchorEl, setNotificationAnchorEl] = useState(null);
    const [loadingNotifications, setLoadingNotifications] = useState(false);
    const notificationOpen = Boolean(notificationAnchorEl);

    const context = useContext(MyContext)
    const [anchorEl, setAnchorEl] = useState(null);
    const open = Boolean(anchorEl);

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
        setAnchorEl(null)
    };

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

    const fetchCartItemsCount = async () => {
        try {
            const res = await getDataApi("/customer/cart/count");
            if (res.success) {
                context.setCartItemsCount(res.data.count_cart_items);
            }
        } catch (error) {
            console.error("Error fetching cart items count:", error);
            context.setCartItemsCount(0);
        }
    };

    const fetchNotifications = async (unreadOnly = false) => {
        try {
            setLoadingNotifications(true);
            const res = await getDataApi(`/customer/notification/?unread_only=${unreadOnly}&skip=0&limit=10`);
            if (res.success) {
                setNotifications(res.data.data || []);
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
                fetchUnreadCount();
                fetchNotifications();
            }
        } catch (error) {
            console.error("Error marking as read:", error);
        }
    };

    const handleNotificationClick = (event) => {
        setNotificationAnchorEl(event.currentTarget);
        if (notifications.length === 0) {
            fetchNotifications();
        }
    };

    const handleNotificationClose = () => {
        setNotificationAnchorEl(null);
    };

    const handleMarkAllAsRead = () => {
        const unreadIds = notifications.filter(n => !n.is_read).map(n => n.id);
        if (unreadIds.length > 0) {
            markAsRead(unreadIds);
        }
    };

    const logout = async () => {
        setAnchorEl(null)
        const response = await fetchWithAutoRefresh("/customer/auth/logout", "GET")

        if (response?.success === true) {
            context.setIsLogin(false)
            localStorage.removeItem("accesstoken")
            localStorage.removeItem("refreshtoken")
        }
    }

    const updateCartCount = useCallback(() => {
        if (context.isLogin) {
            fetchCartItemsCount();
        }
    }, [context.isLogin]);

    useEffect(() => {
        if (context.setUpdateCartCount) {
            context.setUpdateCartCount(updateCartCount);
        }
    }, [updateCartCount, context.setUpdateCartCount]);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const res = await getDataApi("/customer/categories/all");

                if (res.success) {
                    context.setCategories(res.data.data);
                }
            } catch (error) {
                console.error("Error fetching categories:", error);
            }
        };
        fetchCategories();

        if (context.isLogin) {
            fetchUnreadCount();
            fetchCartItemsCount();

            const interval = setInterval(() => {
                fetchUnreadCount();
                fetchCartItemsCount();
            }, 30000);

            return () => clearInterval(interval);
        }
    }, [context.isLogin]);

    return (
        <header className="bg-white">
            <div className="top-strip py-2 border-gray-250 border-b-[1px]">
                <div className="container">
                    <div className="flex items-center justify-between">
                        <div className="col1 w-[50%]">
                            <p className="text-[14px] font-[500]">Giảm giá tới 50% cho các kiểu dáng mùa mới, chỉ trong thời gian có hạn</p>
                        </div>

                        <div className="col2 flex items-center justify-end">
                            <ul className="flex items-center gap-3">
                                <li className="list-none">
                                    <Link to="/help-center" className="text-[14px] link font-[500] transition">Help Center</Link>
                                </li>
                                <li className="list-none">
                                    <Link to="/order-tracking" className="text-[14px] link font-[500] transition">Order Tracking</Link>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <div className="top-strip py-4 border-b-[1px] border-gray-250">
                <div className="container flex items-center justify-between">
                    <div className="col1 w-[25%]">
                        <Link to={"/"}><img src="/logo.jpg" /></Link>
                    </div>
                    <div className="col2 w-[40%]">
                        <Search />
                    </div>
                    <div className="col3 w-[35%] flex items-center pl-20">
                        <ul className="flex items-center justify-end gap-3">
                            {
                                context.isLogin === false ?
                                    <li className="list-none">
                                        <Link to="/login" className="link transition text-[16px] font-[500]">Login</Link> | &nbsp;
                                        <Link to="/signup" className="link transition text-[16px] font-[500]">Register</Link>
                                    </li>
                                    :
                                    <>
                                        <Button className="!text-[#000] myAccountWrap flex items-center gap-3 cursor-pointer"
                                            onClick={handleClick}>
                                            <Button className="!w-[40px] !h-[40px] !min-w-[40px] !rounded-full !bg-[#f1f1f1]">
                                                <FaRegUser className="text-[16px] text-[rgba(0,0,0,0.7)]" />
                                            </Button>

                                            <div className="info flex flex-col">
                                                <h4 className="leading-3 text-[14px] text-[rgba(0,0,0,0.6)] font-[500] mb-0 capitalize text-left justify-start">
                                                    {context?.userData.first_name} {context?.userData.last_name}
                                                </h4>
                                                <span className="text-[13px] text-[rgba(0,0,0,0.6)] font-[400] normal-case text-left justify-start">
                                                    {context?.userData.email}
                                                </span>
                                            </div>
                                        </Button>

                                        <Menu
                                            anchorEl={anchorEl}
                                            id="account-menu"
                                            open={open}
                                            onClose={handleClose}
                                            onClick={handleClose}
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
                                            <Link to='/my-account' className="w-full block">
                                                <MenuItem onClick={handleClose} className="flex gap-2 !py-2">
                                                    <FaRegUser className="text-[18px]" /> <span className="text-[14px]">My Account</span>
                                                </MenuItem>
                                            </Link>

                                            <Link to='/my-orders' className="w-full block">
                                                <MenuItem onClick={handleClose} className="flex gap-2 !py-2">
                                                    <IoBagCheckOutline className="text-[18px]" /> <span className="text-[14px]">Orders</span>
                                                </MenuItem>
                                            </Link>

                                            <Link to='/my-list' className="w-full block">
                                                <MenuItem onClick={handleClose} className="flex gap-2 !py-2">
                                                    <IoMdHeartEmpty className="text-[18px]" /> <span className="text-[14px]">My List</span>
                                                </MenuItem>
                                            </Link>

                                            <MenuItem onClick={logout} className="flex gap-2 !py-2">
                                                <IoIosLogOut className="text-[18px]" /> <span className="text-[14px]">Logout</span>
                                            </MenuItem>
                                        </Menu>
                                    </>

                            }

                            {context.isLogin && (
                                <li>
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
                                                        className="text-xs text-blue-600 hover:underline"
                                                    >
                                                        Đánh dấu tất cả đã đọc
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

                                        <div className="p-3 border-t">
                                            <Link
                                                to="/notifications"
                                                className="text-xs text-blue-600 hover:underline block text-center"
                                                onClick={handleNotificationClose}
                                            >
                                                Xem tất cả thông báo
                                            </Link>
                                        </div>
                                    </Menu>
                                </li>
                            )}

                            <li>
                                <Tooltip title="Wishlist">
                                    <IconButton aria-label="wishlist">
                                        <Badge badgeContent={4} color="secondary">
                                            <FaRegHeart />
                                        </Badge>
                                    </IconButton>
                                </Tooltip>
                            </li>
                            <li>
                                <Tooltip title="Cart">
                                    <IconButton aria-label="cart" onClick={() => context.setOpenCartPanel(true)}>
                                        <Badge badgeContent={context.cartItemsCount} color="secondary">
                                            <MdOutlineShoppingCart />
                                        </Badge>
                                    </IconButton>
                                </Tooltip>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            <Navigation categories={context.categories} />

        </header>
    )
}

export default Header