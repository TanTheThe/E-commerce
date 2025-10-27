import Button from "@mui/material/Button";
import React, { useContext, useState } from "react";
import { FaAngleDown, FaLock, FaRegImage, FaTag, FaUserTie, FaWarehouse } from "react-icons/fa";
import { FiUsers } from "react-icons/fi";
import { IoMdLogOut } from "react-icons/io";
import { IoBagCheckOutline } from "react-icons/io5";
import { RiProductHuntLine } from "react-icons/ri";
import { RxDashboard } from "react-icons/rx";
import { TbCategory } from "react-icons/tb";
import { RiDiscountPercentLine } from "react-icons/ri";
import { Link, useNavigate } from "react-router-dom";
import { Collapse } from 'react-collapse';
import { MyContext } from "../../App";
import AddCategory from "../../Pages/Category/addCategory";
import AddSpecialOffer from "../../Pages/SpecialOffer/addSpecialOffer";
import { MdBrandingWatermark, MdOutlinePreview } from "react-icons/md";
import { FaPeopleGroup } from "react-icons/fa6";
import { IoIosColorPalette } from "react-icons/io";
import { SiMaterialdesignicons } from "react-icons/si";
import useAuth from "../../Pages/Verify/auth";



const Sidebar = () => {
    const [submenuIndex, setSubmenuIndex] = useState(null)
    const [isOpen, setIsOpen] = useState(false);
    const { userRole } = useAuth();
    const isStaff = userRole === 'staff';

    const isOpenSubMenu = (index) => {
        if (isStaff) return;

        if (submenuIndex === index) {
            setSubmenuIndex(null);
        } else {
            setSubmenuIndex(index);
        }
    };

    const context = useContext(MyContext)
    const navigate = useNavigate()

    const checkLogin = () => {
        const token = localStorage.getItem("accesstoken");
        if (!token) {
            navigate("/login");
            return false;
        }
        return true;
    };

    const LockedMenuItem = ({ icon: Icon, label }) => (
        <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-gray-400 !font-[500] items-center !py-2 !bg-gray-50 cursor-not-allowed relative group">
            <Icon className="text-[18px]" />
            <span>{label}</span>
            <FaLock className="text-[12px] ml-auto text-gray-400" />
            <div className="absolute left-0 top-full mt-1 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
                Chỉ Admin mới truy cập được
            </div>
        </Button>
    );

    return (
        <>
            <div className={`sidebar fixed top-0 left-0 bg-[#fff] h-full border-r border-[rgba(0,0,0,0.1)] py-2 px-4 w-[${context.isSidebarOpen === true ? '15%' : '0px'}]`}>
                <div className="py-2 w-full">
                    <Link to="/">
                        <img src="https://ecme-react.themenate.net/img/logo/logo-light-full.png" className="w-[120px]" />
                    </Link>
                </div>

                <ul className="mt-4 ">
                    <li>
                        <Link to="/">
                            <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]">
                                <RxDashboard className="text-[18px]" /> <span>Dashboard</span>
                            </Button>
                        </Link>
                    </li>

                    <li>
                        {isStaff ? (
                            <LockedMenuItem icon={FaRegImage} label="Home Slides" />
                        ) : (
                            <>
                                <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]"
                                    onClick={() => isOpenSubMenu(1)}>
                                    <FaRegImage className="text-[18px]" /> <span>Home Slides</span>
                                    <span className="ml-auto w-[30px] h-[30px] flex items-center justify-center">
                                        <FaAngleDown className={`transition-all ${submenuIndex === 1 ? 'rotate-180' : ''}`} />
                                    </span>
                                </Button>

                                <Collapse isOpened={submenuIndex === 1 ? true : false}>
                                    <ul className="w-full">
                                        <li className="w-full">
                                            <Button className="!text-[rgba(0,0,0,0.8)] !capitalize !justify-start !w-full !text-[13px] !pl-9 flex gap-3">
                                                <span className="block w-[5px] h-[5px] rounded-full bg-[rgba(0,0,0,0.1)]"></span>
                                                Home Banner Slides List
                                            </Button>
                                        </li>
                                        <li className="w-full">
                                            <Button className="!text-[rgba(0,0,0,0.8)] !capitalize !justify-start !w-full !text-[13px] !pl-9 flex gap-3">
                                                <span className="block w-[5px] h-[5px] rounded-full bg-[rgba(0,0,0,0.1)]"></span>
                                                Add Home Banner Slide
                                            </Button>
                                        </li>
                                    </ul>
                                </Collapse>
                            </>
                        )}
                    </li>

                    <li>
                        {isStaff ? (
                            <LockedMenuItem icon={FaUserTie} label="Staffs" />
                        ) : (
                            <Link to="/staffs">
                                <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]">
                                    <FaUserTie className="text-[18px]" /> <span>Staffs</span>
                                </Button>
                            </Link>
                        )}
                    </li>

                    <li>
                        {isStaff ? (
                            <LockedMenuItem icon={FiUsers} label="Users" />
                        ) : (
                            <Link to="/users">
                                <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]">
                                    <FiUsers className="text-[18px]" /> <span>Users</span>
                                </Button>
                            </Link>
                        )}
                    </li>

                    <li>
                        {isStaff ? (
                            <LockedMenuItem icon={RiProductHuntLine} label="Products" />
                        ) : (
                            <Link to="/products">
                                <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]">
                                    <RiProductHuntLine className="text-[18px]" /> <span>Products</span>
                                </Button>
                            </Link>
                        )}
                    </li>

                    <li>
                        {isStaff ? (
                            <LockedMenuItem icon={TbCategory} label="Category" />
                        ) : (
                            <Link to="/category/list">
                                <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]">
                                    <TbCategory className="text-[18px]" /> <span>Category</span>
                                </Button>
                            </Link>
                        )}
                    </li>

                    <li>
                        {isStaff ? (
                            <LockedMenuItem icon={IoBagCheckOutline} label="Orders" />
                        ) : (
                            <Link to="/orders">
                                <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]">
                                    <IoBagCheckOutline className="text-[18px]" /> <span>Orders</span>
                                </Button>
                            </Link>
                        )}
                    </li>

                    {/* <li>
                        <Link to="/special-offer/list">
                            <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]">
                                <RiDiscountPercentLine className="text-[18px]" /> <span>Special Offers</span>
                            </Button>
                        </Link>
                        <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]"
                            onClick={() => isOpenSubMenu(6)}>
                            <RiDiscountPercentLine className="text-[18px]" /> <span>Special Offers</span>
                            <span className="ml-auto w-[30px] h-[30px] flex items-center justify-center"><FaAngleDown
                                className={`transition-all ${submenuIndex === 6 ? 'rotate-180' : ''}`} /></span>
                        </Button>

                        <Collapse isOpened={submenuIndex === 6 ? true : false}>
                            <ul className="w-full">
                                <li className="w-full">
                                    <Button className="!text-[rgba(0,0,0,0.8)] !capitalize !justify-start !w-full !text-[13px] !pl-9 flex gap-3"
                                        onClick={() => {
                                            if (checkLogin()) navigate("/special-offer/list");
                                        }}>
                                        <span className="block w-[5px] h-[5px] rounded-full bg-[rgba(0,0,0,0.1)]"></span>
                                        Danh sách mã khuyến mãi</Button>
                                </li>
                                <li className="w-full">
                                    <Button className="!text-[rgba(0,0,0,0.8)] !capitalize !justify-start !w-full !text-[13px] !pl-9 flex gap-3"
                                        onClick={() => {
                                            if (checkLogin()) setIsOpen(true);
                                        }}>
                                        <span className="block w-[5px] h-[5px] rounded-full bg-[rgba(0,0,0,0.1)]"></span>
                                        Tạo mã khuyến mãi</Button>
                                    <AddSpecialOffer open={isOpen} onClose={() => setIsOpen(false)} />
                                </li>
                            </ul>
                        </Collapse>
                    </li> */}

                    <li>
                        {isStaff ? (
                            <LockedMenuItem icon={RiDiscountPercentLine} label="Special Offers" />
                        ) : (
                            <Link to="/special-offer/list">
                                <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]">
                                    <RiDiscountPercentLine className="text-[18px]" /> <span>Special Offers</span>
                                </Button>
                            </Link>
                        )}
                    </li>

                    <li>
                        {isStaff ? (
                            <LockedMenuItem icon={MdOutlinePreview} label="Reviews" />
                        ) : (
                            <Link to="/reviews/list">
                                <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]">
                                    <MdOutlinePreview className="text-[18px]" /> <span>Reviews</span>
                                </Button>
                            </Link>
                        )}
                    </li>

                    <li>
                        {isStaff ? (
                            <LockedMenuItem icon={IoIosColorPalette} label="Colors" />
                        ) : (
                            <Link to="/colors/list">
                                <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]">
                                    <IoIosColorPalette className="text-[18px]" /> <span>Colors</span>
                                </Button>
                            </Link>
                        )}
                    </li>

                    <li>
                        {isStaff ? (
                            <LockedMenuItem icon={MdBrandingWatermark} label="Brands" />
                        ) : (
                            <Link to="/brands/list">
                                <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]">
                                    <MdBrandingWatermark className="text-[18px]" /> <span>Brands</span>
                                </Button>
                            </Link>
                        )}
                    </li>

                    <li>
                        {isStaff ? (
                            <LockedMenuItem icon={SiMaterialdesignicons} label="Materials" />
                        ) : (
                            <Link to="/materials/list">
                                <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]">
                                    <SiMaterialdesignicons className="text-[18px]" /> <span>Materials</span>
                                </Button>
                            </Link>
                        )}
                    </li>

                    <li>
                        {isStaff ? (
                            <LockedMenuItem icon={FaTag} label="Tags" />
                        ) : (
                            <Link to="/tags/list">
                                <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]">
                                    <FaTag className="text-[18px]" /> <span>Tags</span>
                                </Button>
                            </Link>
                        )}
                    </li>

                    <li>
                        {isStaff ? (
                            <LockedMenuItem icon={FaTag} label="Warehouses" />
                        ) : (
                            <Link to="/warehouses/list">
                                <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]">
                                    <FaWarehouse className="text-[18px]" /> <span>Warehouses</span>
                                </Button>
                            </Link>
                        )}
                    </li>

                    <li>
                        {isStaff ? (
                            <LockedMenuItem icon={FaTag} label="Suppliers" />
                        ) : (
                            <Link to="/suppliers/list">
                                <Button className="w-full !capitalize !justify-start flex gap-3 text-[14px] !text-[rgba(0,0,0,0.8)] !font-[500] items-center !py-2 hover:!bg-[#f1f1f1]">
                                    <FaPeopleGroup className="text-[18px]" /> <span>Suppliers</span>
                                </Button>
                            </Link>
                        )}
                    </li>
                </ul>
            </div >
        </>
    )
}

export default Sidebar