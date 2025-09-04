import React, { useEffect, useRef, useState } from "react";
import '../Search/style.css'
import Button from '@mui/material/Button'
import { IoSearch } from "react-icons/io5"
import { getDataApi } from "../../utils/api";
import { Link, useNavigate } from "react-router-dom";

const Search = () => {
    const navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [showResults, setShowResults] = useState(false);
    const [selectedIndex, setSelectedIndex] = useState(-1);
    const searchTimeoutRef = useRef(null);
    const searchContainerRef = useRef(null);

    const performSearch = async (query) => {
        if (!query.trim()) {
            setSearchResults(null);
            setShowResults(false);
            setSelectedIndex(-1);
            return;
        }

        setIsLoading(true);
        try {
            const response = await getDataApi(`/customer/product/search?search=${encodeURIComponent(query)}`);
            console.log(response);
            if (response.success) {
                setSearchResults(response.data);
                setShowResults(true);
                setSelectedIndex(-1);
            }
        } catch (error) {
            console.error('Search error:', error);
            setSearchResults(null);
        } finally {
            setIsLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const value = e.target.value;
        setSearchQuery(value);
        setSelectedIndex(-1);

        if (searchTimeoutRef.current) {
            clearTimeout(searchTimeoutRef.current);
        }

        searchTimeoutRef.current = setTimeout(() => {
            performSearch(value);
        }, 300);
    };

    const handleSearchClick = () => {
        if (searchTimeoutRef.current) {
            clearTimeout(searchTimeoutRef.current);
        }

        if (selectedIndex >= 0) {
            handleSelectItem();
        } else {
            performSearch(searchQuery);
        }
    };

    const getDisplayItems = () => {
        if (!searchResults) return [];

        const items = [];

        searchResults.categories.slice(0, 5).forEach(category => {
            items.push({
                type: 'category',
                data: category,
                isParent: true
            });

            if (category.type === "parent_from_child_match" && category.matched_children?.length > 0) {
                category.matched_children.forEach(childName => {
                    const childCategory = category.children?.find(child => child.name === childName);
                    if (childCategory) {
                        items.push({
                            type: 'category',
                            data: childCategory,
                            isParent: false,
                            parentId: category.id
                        });
                    }
                });
            }
        });

        searchResults.products.slice(0, 8).forEach(product => {
            items.push({
                type: 'product',
                data: product
            });
        });

        if (searchResults.categories.length > 5 || searchResults.products.length > 8) {
            items.push({
                type: 'viewall',
                data: null
            });
        }

        return items;
    };

    const getTotalItems = () => {
        return getDisplayItems().length;
    };

    const getItemByIndex = (index) => {
        const items = getDisplayItems();
        return items[index] || null;
    };

    const handleCategoryNavigation = (category, parentId = null) => {
        console.log('Category clicked:', category, 'Parent ID:', parentId);

        if (parentId) {
            navigate(`/category/${parentId}?selected_categories=${category.id}`);
        } else {
            switch (category.type) {
                case "parent_direct_match":
                case "parent":
                case "parent_from_child_match":
                    navigate(`/category/${category.id}`);
                    break;

                default:
                    if (category.children_count === 0) {
                        const parentCategory = findParentCategory(category);
                        if (parentCategory) {
                            navigate(`/category/${parentCategory.id}?selected_categories=${category.id}`);
                        } else {
                            navigate(`/category/${category.id}`);
                        }
                    } else {
                        navigate(`/category/${category.id}`);
                    }
                    break;
            }
        }
    };

    const findParentCategory = (childCategory) => {
        if (!searchResults?.categories) return null;

        return searchResults.categories.find(cat =>
            cat.children && cat.children.some(child => child.id === childCategory.id)
        );
    };

    const handleSelectItem = () => {
        const item = getItemByIndex(selectedIndex);
        if (!item) return;

        setShowResults(false);
        setSelectedIndex(-1);

        switch (item.type) {
            case 'category':
                handleCategoryNavigation(item.data, item.parentId);
                break;
            case 'product':
                navigate(`/product/${item.data.id}`);
                break;
            case 'viewall':
                navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
                break;
        }
    };

    const handleKeyPress = (e) => {
        if (!showResults || !searchResults) return;

        const totalItems = getTotalItems();

        switch (e.key) {
            case 'Enter':
                e.preventDefault();
                if (searchTimeoutRef.current) {
                    clearTimeout(searchTimeoutRef.current);
                }

                if (selectedIndex >= 0) {
                    handleSelectItem();
                } else {
                    performSearch(searchQuery);
                }
                break;

            case 'ArrowDown':
                e.preventDefault();
                setSelectedIndex(prev => {
                    const nextIndex = prev + 1;
                    return nextIndex >= totalItems ? 0 : nextIndex;
                });
                break;

            case 'ArrowUp':
                e.preventDefault();
                setSelectedIndex(prev => {
                    const nextIndex = prev - 1;
                    return nextIndex < 0 ? totalItems - 1 : nextIndex;
                });
                break;

            case 'Escape':
                e.preventDefault();
                setShowResults(false);
                setSelectedIndex(-1);
                break;
        }
    };

    const handleCategoryClick = (category, parentId = null) => {
        setShowResults(false);
        setSelectedIndex(-1);
        handleCategoryNavigation(category, parentId);
    };

    const handleProductClick = (product) => {
        setShowResults(false);
        setSelectedIndex(-1);
        navigate(`/product/${product.id}`);
    };

    const handleViewAllClick = () => {
        setShowResults(false);
        setSelectedIndex(-1);
        navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    };

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (searchContainerRef.current && !searchContainerRef.current.contains(event.target)) {
                setShowResults(false);
                setSelectedIndex(-1);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    useEffect(() => {
        return () => {
            if (searchTimeoutRef.current) {
                clearTimeout(searchTimeoutRef.current);
            }
        };
    }, []);

    const isItemSelected = (index) => {
        return selectedIndex === index;
    };

    // Phân nhóm các items để hiển thị
    const getCategoryItems = () => {
        return getDisplayItems().filter(item => item.type === 'category');
    };

    const getProductItems = () => {
        return getDisplayItems().filter(item => item.type === 'product');
    };

    const getViewAllItem = () => {
        return getDisplayItems().find(item => item.type === 'viewall');
    };

    return (
        <div className="relative w-full" ref={searchContainerRef}>
            <div className="w-full h-[55px] bg-white border-2 border-gray-300 rounded-xl relative shadow-sm hover:border-blue-400 focus-within:border-blue-500 transition-all duration-300">
                <input
                    type="text"
                    placeholder="Tìm kiếm sản phẩm, danh mục..."
                    className="w-full h-full focus:outline-none bg-transparent pl-5 pr-14 text-[15px] placeholder-gray-500 font-medium"
                    value={searchQuery}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyPress}
                    onFocus={() => searchResults && setShowResults(true)}
                />
                <Button
                    className="!absolute top-1 right-1 !w-[42px] !min-w-[42px] h-[42px] !rounded-lg !bg-gradient-to-r !from-blue-500 !to-blue-600 hover:!from-blue-600 hover:!to-blue-700 !shadow-md hover:!shadow-lg !transition-all !duration-200"
                    onClick={handleSearchClick}
                    disabled={isLoading}
                >
                    <IoSearch className="text-white text-[18px]" />
                </Button>
            </div>

            {showResults && searchResults && (
                <div className="absolute top-[56px] left-0 right-0 bg-white border border-gray-200 rounded-2xl shadow-2xl z-50 max-h-[450px] overflow-y-auto backdrop-blur-sm">

                    {isLoading && (
                        <div className="p-6 text-center text-gray-500 font-medium">
                            <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mb-2"></div>
                            <div>Đang tìm kiếm...</div>
                        </div>
                    )}

                    {!isLoading && searchResults.categories.length === 0 && searchResults.products.length === 0 && (
                        <div className="p-6 text-center text-gray-500 font-medium">
                            <div className="text-2xl mb-2">🔍</div>
                            Không tìm thấy kết quả nào
                        </div>
                    )}

                    {getCategoryItems().length > 0 && (
                        <div className="border-b border-gray-100">
                            <div className="px-5 py-3 bg-gradient-to-r from-gray-50 to-gray-100 font-semibold text-sm text-gray-700 rounded-t-2xl">
                                📂 Danh mục
                            </div>
                            {getDisplayItems().map((item, index) => {
                                if (item.type !== 'category') return null;

                                const category = item.data;
                                const isParent = item.isParent;
                                const parentId = item.parentId;

                                return (
                                    <div
                                        key={`${category.id}-${isParent ? 'parent' : 'child'}`}
                                        className={`block px-5 py-4 cursor-pointer transition-all duration-200 border-b border-gray-50 last:border-b-0 group ${isItemSelected(index)
                                            ? 'bg-gradient-to-r from-blue-100 to-blue-200'
                                            : 'hover:bg-gradient-to-r hover:from-blue-50 hover:to-blue-100'
                                            }`}
                                        onClick={() => handleCategoryClick(category, parentId)}
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className={`flex-1 ${!isParent ? 'ml-6' : ''}`}>
                                                <div className="flex items-center">
                                                    {!isParent && (
                                                        <span className="text-gray-400 mr-2">└─</span>
                                                    )}
                                                    <span className={`text-sm font-semibold transition-colors ${isItemSelected(index)
                                                        ? 'text-blue-800'
                                                        : 'text-gray-800 group-hover:text-blue-700'
                                                        }`}>
                                                        {category.name}
                                                    </span>
                                                    {!isParent && (
                                                        <span className="ml-2 text-xs bg-green-100 text-green-600 px-2 py-0.5 rounded-full">
                                                            con
                                                        </span>
                                                    )}
                                                </div>
                                            </div>

                                            <div className="flex items-center space-x-2">
                                                {isParent && category.children_count > 0 && (
                                                    <span className="text-xs text-white bg-blue-500 px-2 py-1 rounded-full font-medium">
                                                        {category.children_count}
                                                    </span>
                                                )}

                                                {isParent && category.type === "parent_from_child_match" && (
                                                    <span className="text-xs text-orange-500" title="Mở rộng từ kết quả con">
                                                        ↗️
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}

                    {getProductItems().length > 0 && (
                        <div>
                            <div className="px-5 py-3 bg-gradient-to-r from-gray-50 to-gray-100 font-semibold text-sm text-gray-700">
                                🛍️ Sản phẩm
                            </div>
                            {getDisplayItems().map((item, index) => {
                                if (item.type !== 'product') return null;

                                const product = item.data;
                                const productIndex = getDisplayItems()
                                    .slice(0, index)
                                    .filter(i => i.type === 'product').length;

                                return (
                                    <div
                                        key={product.id}
                                        className={`block px-5 py-4 cursor-pointer transition-all duration-200 border-b border-gray-50 last:border-b-0 group ${isItemSelected(index)
                                            ? 'bg-gradient-to-r from-blue-100 to-blue-200'
                                            : 'hover:bg-gradient-to-r hover:from-blue-50 hover:to-blue-100'
                                            }`}
                                        onClick={() => handleProductClick(product)}
                                    >
                                        <div className="flex items-center">
                                            <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm mr-3">
                                                {productIndex + 1}
                                            </div>
                                            <div className="flex-1">
                                                <span className={`text-sm font-semibold transition-colors ${isItemSelected(index)
                                                    ? 'text-blue-800'
                                                    : 'text-gray-800 group-hover:text-blue-700'
                                                    }`}>
                                                    {product.name}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}

                    {getViewAllItem() && (
                        <div className="border-t border-gray-100">
                            {getDisplayItems().map((item, index) => {
                                if (item.type !== 'viewall') return null;

                                return (
                                    <div
                                        key="viewall"
                                        className={`block px-5 py-4 text-center text-sm font-bold cursor-pointer transition-all duration-200 rounded-b-2xl ${isItemSelected(index)
                                            ? 'bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800'
                                            : 'text-blue-600 hover:bg-gradient-to-r hover:from-blue-50 hover:to-blue-100'
                                            }`}
                                        onClick={handleViewAllClick}
                                    >
                                        ✨ Xem tất cả kết quả
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Search