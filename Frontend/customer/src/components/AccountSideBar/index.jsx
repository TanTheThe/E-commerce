import Button from "@mui/material/Button";
import React, { useContext, useState } from "react";
import { FaCloudUploadAlt, FaRegUser } from "react-icons/fa";
import { IoIosLogOut, IoMdHeartEmpty } from "react-icons/io";
import { IoBagCheckOutline } from "react-icons/io5";
import { NavLink } from "react-router";
import { MyContext } from "../../App";

const AccountSideBar = () => {
    const context = useContext(MyContext)
    if (context?.isLoading || !context?.userData) {
        return (
            <div className="card bg-white shadow-md rounded-md sticky top-[10px]">
                <div className="w-full p-5 flex items-center justify-center flex-col">
                    <div className="w-[110px] h-[110px] rounded-full overflow-hidden relative group bg-gray-200 animate-pulse">
                        {/* Skeleton loader */}
                    </div>
                    <div className="h-6 bg-gray-200 rounded w-32 mt-3 animate-pulse"></div>
                    <div className="h-4 bg-gray-200 rounded w-24 mt-2 animate-pulse"></div>
                </div>
                <ul className="list-none pb-5 bg-[#faf9f9] myAccountTabs">
                    {/* Skeleton for menu items */}
                    {[1, 2, 3, 4].map(item => (
                        <li key={item} className="w-full">
                            <div className="w-full h-12 bg-gray-200 animate-pulse mx-5 my-2 rounded"></div>
                        </li>
                    ))}
                </ul>
            </div>
        )
    }

    return (
        <div className="card bg-white shadow-md rounded-md sticky top-[10px]">
            <div className="w-full p-5 flex items-center justify-center flex-col">
                <div className="w-[110px] h-[110px] rounded-full overflow-hidden relative group">
                    <img className="w-full h-full object-cover" src='avatar.png' />
                </div>

                <h3>{context?.userData?.first_name} {context?.userData?.last_name}</h3>
                <h6 className="text-[13px] font-[500]">{context?.userData?.email}</h6>
            </div>

            <ul className="list-none pb-5 bg-[#faf9f9] myAccountTabs">
                <li className="w-full">
                    <NavLink to="/my-account" exact={true} activeClassName="isActive">
                        <Button className="w-full !text-left !px-5 !justify-start !capitalize !text-[rgba(0,0,0,0.8)] !rounded-none flex items-center gap-2">
                            <FaRegUser className="text-[17px]" /> My Profile
                        </Button>
                    </NavLink>
                </li>

                <li className="w-full">
                    <NavLink to="/my-list" exact={true} activeClassName="isActive">
                        <Button className="w-full !text-left !px-5 !justify-start !capitalize !text-[rgba(0,0,0,0.8)] !rounded-none flex items-center gap-2">
                            <IoMdHeartEmpty className="text-[17px]" /> My List
                        </Button>
                    </NavLink>
                </li>

                <li className="w-full">
                    <NavLink to="/my-orders" exact={true} activeClassName="isActive">
                        <Button className="w-full !text-left !px-5 !justify-start !capitalize !text-[rgba(0,0,0,0.8)] !rounded-none flex items-center gap-2">
                            <IoBagCheckOutline className="text-[17px]" /> My Orders
                        </Button>
                    </NavLink>
                </li>

                <li className="w-full">
                    <Button className="w-full !text-left !px-5 !justify-start !capitalize !text-[rgba(0,0,0,0.8)] !rounded-none flex items-center gap-2">
                        <IoIosLogOut className="text-[17px]" /> Logout
                    </Button>
                </li>
            </ul>
        </div>
    )
}

export default AccountSideBar