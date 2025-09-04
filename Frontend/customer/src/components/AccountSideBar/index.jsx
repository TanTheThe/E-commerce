import Button from "@mui/material/Button";
import React, { useContext, useState } from "react";
import { FaCloudUploadAlt, FaRegUser } from "react-icons/fa";
import { IoIosLogOut, IoMdHeartEmpty } from "react-icons/io";
import { IoBagCheckOutline } from "react-icons/io5";
import { NavLink, useLocation, useNavigate } from "react-router";
import { MyContext } from "../../App";

const AccountSideBar = () => {
    const context = useContext(MyContext)
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        try {
            localStorage.removeItem("accesstoken");
            context?.setIsLogin(false);
            context?.setUserData(null);
            navigate('/login');
            context?.openAlertBox("success", "Logged out successfully!");
        } catch (error) {
            console.error("Error during logout:", error);
            context?.openAlertBox("error", "An error occurred during logout");
        }
    }

    const menuItems = [
        {
            path: "/my-account",
            icon: <FaRegUser className="text-[18px]" />,
            label: "My Profile",
            description: "Manage your personal information"
        },
        {
            path: "/my-list",
            icon: <IoMdHeartEmpty className="text-[18px]" />,
            label: "My List",
            description: "Your saved favorite items"
        },
        {
            path: "/my-orders",
            icon: <IoBagCheckOutline className="text-[18px]" />,
            label: "My Orders",
            description: "Track your order history"
        }
    ];

    if (context?.isLoading || !context?.userData) {
        return (
            <div className="card bg-white shadow-lg rounded-xl sticky top-[20px] overflow-hidden border border-gray-100">
                <div className="w-full p-6 flex items-center justify-center flex-col bg-gradient-to-br from-blue-50 to-indigo-50">
                    <div className="w-[80px] h-[80px] rounded-full bg-gray-200 animate-pulse flex items-center justify-center">
                        <FaRegUser className="text-gray-400 text-[28px]" />
                    </div>
                    <div className="h-6 bg-gray-200 rounded-lg w-32 mt-4 animate-pulse"></div>
                    <div className="h-4 bg-gray-200 rounded w-24 mt-2 animate-pulse"></div>
                </div>

                <div className="bg-white">
                    {[1, 2, 3, 4].map(item => (
                        <div key={item} className="px-6 py-3">
                            <div className="h-12 bg-gray-100 animate-pulse rounded-lg"></div>
                        </div>
                    ))}
                </div>
            </div>
        )
    }

    return (
        <div className="card bg-white shadow-lg rounded-xl sticky top-[20px] overflow-hidden border border-gray-100">
            <div className="w-full p-6 flex items-center justify-center flex-col bg-gradient-to-br from-blue-50 to-indigo-50">
                <div className="w-[100px] h-[100px] rounded-full overflow-hidden relative group shadow-lg ring-4 ring-white">
                    <img
                        className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                        src={context?.userData?.avatar || 'avatar.png'}
                        alt="Profile Avatar"
                        onError={(e) => {
                            e.target.src = 'avatar.png';
                        }}
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-opacity duration-300 flex items-center justify-center">
                        <FaRegUser className="text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    </div>
                </div>

                <h3 className="text-lg font-bold text-gray-800 mt-4 text-center">
                    {context?.userData?.content?.first_name || context?.userData?.first_name} {context?.userData?.content?.last_name || context?.userData?.last_name}
                </h3>

                <p className="text-sm text-gray-600 text-center break-all">
                    {context?.userData?.content?.email || context?.userData?.email}
                </p>

                {context?.userData?.content?.phone && (
                    <p className="text-xs text-gray-500 mt-1">
                        {context.userData.content.phone}
                    </p>
                )}
            </div>

            <div className="bg-white">
                <nav className="py-2">
                    {menuItems.map((item) => {
                        const isActive = location.pathname === item.path;
                        return (
                            <div key={item.path} className="px-3 py-1">
                                <NavLink
                                    to={item.path}
                                    className={`block rounded-lg transition-all duration-200 ${isActive
                                            ? 'bg-blue-50 border-l-4 border-blue-500'
                                            : 'hover:bg-gray-50'
                                        }`}
                                >
                                    <div className="flex items-center px-4 py-3 gap-3">
                                        <div className={`flex-shrink-0 ${isActive ? 'text-blue-600' : 'text-gray-500'}`}>
                                            {item.icon}
                                        </div>
                                        <div className="flex-grow">
                                            <div className={`font-medium ${isActive ? 'text-blue-800' : 'text-gray-700'}`}>
                                                {item.label}
                                            </div>
                                            <div className="text-xs text-gray-500 mt-0.5">
                                                {item.description}
                                            </div>
                                        </div>
                                        {isActive && (
                                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                        )}
                                    </div>
                                </NavLink>
                            </div>
                        );
                    })}

                    <div className="px-3 py-1 mt-4 border-t border-gray-100">
                        <button
                            onClick={handleLogout}
                            className="w-full flex items-center px-4 py-3 gap-3 text-left rounded-lg transition-all duration-200 hover:bg-red-50 group"
                        >
                            <div className="flex-shrink-0 text-gray-500 group-hover:text-red-600">
                                <IoIosLogOut className="text-[18px]" />
                            </div>
                            <div className="flex-grow">
                                <div className="font-medium text-gray-700 group-hover:text-red-700">
                                    Logout
                                </div>
                                <div className="text-xs text-gray-500">
                                    Sign out of your account
                                </div>
                            </div>
                        </button>
                    </div>
                </nav>
            </div>
        </div>
    )
}

export default AccountSideBar