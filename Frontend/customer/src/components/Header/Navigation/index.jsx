import React, { useEffect, useState } from "react";
import Button from "@mui/material/Button";
import { RiMenu2Fill } from "react-icons/ri";
import { LiaAngleDownSolid } from "react-icons/lia";
import { Link } from "react-router-dom";
import { GoRocket } from "react-icons/go";
import CategoryPanel from "./CategoryPanel";
import "../Navigation/style.css"
import { getDataApi } from "../../../utils/api";
import { ChevronDown } from "lucide-react";

const Navigation = ({ categories }) => {
    const [activeDropdown, setActiveDropdown] = useState(null);
    const [timeoutId, setTimeoutId] = useState(null);

    const parentCategories = categories.filter(category => category.parent_id === null);

    const getChildCategories = (parentId) => {
        return categories.filter(category => category.parent_id === parentId);
    };

    const handleMouseEnter = (categoryId) => {
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
        setActiveDropdown(categoryId);
    };

    const handleMouseLeave = () => {
        const id = setTimeout(() => {
            setActiveDropdown(null);
        }, 150);
        setTimeoutId(id);
    };

    return (
        <nav className="py-3 bg-white shadow-sm border-b border-gray-100">
            <div className="container mx-auto px-4">
                <div className="flex items-center justify-between">
                    <div className="flex-1">
                        <ul className="flex items-center gap-8">
                            {parentCategories.map((category) => {
                                const childCategories = getChildCategories(category.id);
                                const hasChildren = childCategories.length > 0;

                                return (
                                    <li
                                        key={category.id}
                                        className="relative group"
                                        onMouseEnter={() => hasChildren && handleMouseEnter(category.id)}
                                        onMouseLeave={() => hasChildren && handleMouseLeave()}
                                    >
                                        <Link
                                            to={`/category/${category.id}`}
                                            className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-blue-600 font-medium text-sm transition-colors duration-200 rounded-md hover:bg-gray-50"
                                        >
                                            {category.image && (
                                                <img
                                                    src={category.image}
                                                    alt={category.name}
                                                    className="w-5 h-5 object-cover rounded"
                                                />
                                            )}
                                            <span>{category.name}</span>
                                            {hasChildren && (
                                                <ChevronDown
                                                    className={`w-4 h-4 transition-transform duration-200 ${activeDropdown === category.id ? 'rotate-180' : ''
                                                        }`}
                                                />
                                            )}
                                        </Link>

                                        {hasChildren && (
                                            <div
                                                className={`absolute top-full left-0 mt-1 bg-white rounded-lg shadow-lg border border-gray-200 py-2 min-w-[200px] z-50 transition-all duration-200 ${activeDropdown === category.id
                                                        ? 'opacity-100 visible transform translate-y-0'
                                                        : 'opacity-0 invisible transform -translate-y-2'
                                                    }`}
                                                onMouseEnter={() => handleMouseEnter(category.id)}
                                                onMouseLeave={handleMouseLeave}
                                            >
                                                <div className="py-1">
                                                    <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide border-b border-gray-100">
                                                        {category.name}
                                                    </div>
                                                    {childCategories.map((childCategory) => (
                                                        <Link
                                                            key={childCategory.id}
                                                            to={`/category/${childCategory.id}`}
                                                            className="flex items-center gap-3 px-4 py-3 text-sm text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-colors duration-150"
                                                        >
                                                            {childCategory.image && (
                                                                <img
                                                                    src={childCategory.image}
                                                                    alt={childCategory.name}
                                                                    className="w-6 h-6 object-cover rounded-full"
                                                                />
                                                            )}
                                                            <div className="flex-1">
                                                                <div className="font-medium">{childCategory.name}</div>
                                                                {childCategory.type_size && (
                                                                    <div className="text-xs text-gray-500 capitalize">
                                                                        {childCategory.type_size}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </Link>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </li>
                                );
                            })}
                        </ul>
                    </div>

                    <div className="flex items-center gap-3 text-sm font-medium text-gray-600 bg-gradient-to-r from-blue-50 to-purple-50 px-4 py-2 rounded-full">
                        <GoRocket className="w-5 h-5 text-blue-600" />
                        <span>Free International Delivery</span>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navigation