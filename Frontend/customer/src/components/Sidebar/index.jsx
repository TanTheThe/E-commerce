import React, { useEffect, useState } from "react";
import CategoryCollapse from "../CategoryCollapse";
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import "../Sidebar/style.css"
import { Collapse } from 'react-collapse';
import Button from "@mui/material/Button";
import { FaAngleDown, FaAngleUp } from "react-icons/fa6";
import RangeSlider from 'react-range-slider-input';
import 'react-range-slider-input/dist/style.css';
import Rating from "@mui/material/Rating";
import { getDataApi } from "../../utils/api";

const Sidebar = ({ categoryId,
    onFilterChange,
    selectedCategoryIds = [],
    selectedSizes = [],
    selectedColors = [],
    selectedRatings = [],
    minPrice,
    maxPrice }) => {
    const [isOpenCategoryFilter, setIsOpenCategoryFilter] = useState(true);
    const [isOpenSizeFilter, setIsOpenSizeFilter] = useState(true);
    const [isOpenColorFilter, setIsOpenColorFilter] = useState(true);

    const [filterData, setFilterData] = useState({ categories: [], sizes: [], colors: [] });
    const [showAllSizes, setShowAllSizes] = useState(false);
    const [showAllColors, setShowAllColors] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [tempMinPrice, setTempMinPrice] = useState('');
    const [tempMaxPrice, setTempMaxPrice] = useState('');

    useEffect(() => {
        const fetchFilters = async () => {
            if (!categoryId) return;

            setLoading(true);
            setError(null);

            try {
                const response = await getDataApi(`/customer/product/filter-info?category_id=${categoryId}`);
                setFilterData(response.content || response.data || { categories: [], sizes: [], colors: [] });
            } catch (err) {
                console.error("Failed to fetch filters:", err);
                setError("Không thể tải dữ liệu bộ lọc");
            } finally {
                setLoading(false);
            }
        };

        fetchFilters();
    }, [categoryId]);

    useEffect(() => {
        setTempMinPrice(minPrice || '');
        setTempMaxPrice(maxPrice || '');
    }, [minPrice, maxPrice]);

    const handleCategoryChange = (categoryId, checked) => {
        let newSelected;
        if (checked) {
            newSelected = [...selectedCategoryIds, categoryId];
        } else {
            newSelected = selectedCategoryIds.filter(id => id !== categoryId);
        }
        onFilterChange('categories', newSelected);
    };

    const handleSizeChange = (size, checked) => {
        let newSelected;
        if (checked) {
            newSelected = [...selectedSizes, size];
        } else {
            newSelected = selectedSizes.filter(s => s !== size);
        }
        onFilterChange('sizes', newSelected);
    };

    const handleColorChange = (color, checked) => {
        let newSelected;
        if (checked) {
            newSelected = [...selectedColors, color];
        } else {
            newSelected = selectedColors.filter(c => c !== color);
        }
        onFilterChange('colors', newSelected);
    };

    const handleRatingChange = (rating, checked) => {
        let newSelected;
        if (checked) {
            newSelected = [...selectedRatings, rating];
        } else {
            newSelected = selectedRatings.filter(r => r !== rating);
        }
        onFilterChange('rating', newSelected);
    };

    const handlePriceFilter = () => {
        const min = tempMinPrice ? parseFloat(tempMinPrice) : null;
        const max = tempMaxPrice ? parseFloat(tempMaxPrice) : null;

        if (min !== null && min < 0) {
            alert('Giá tối thiểu không được âm');
            return;
        }
        if (max !== null && max < 0) {
            alert('Giá tối đa không được âm');
            return;
        }
        if (min !== null && max !== null && min > max) {
            alert('Giá tối thiểu không được lớn hơn giá tối đa');
            return;
        }

        onFilterChange('price', { min, max });
    };

    const handleClearPrice = () => {
        setTempMinPrice('');
        setTempMaxPrice('');
        onFilterChange('price', { min: null, max: null });
    };

    const renderLimitedList = (items, showAll, setShowAll, type) => {
        const limit = 7;
        const visibleItems = showAll ? items : items.slice(0, limit);

        return (
            <>
                {visibleItems.map((item) => (
                    <FormControlLabel
                        key={item.id || item.name}
                        control={
                            <Checkbox
                                size="small"
                                checked={
                                    type === 'categories' ? selectedCategoryIds.includes(item.id) :
                                        type === 'sizes' ? selectedSizes.includes(item.name) :
                                            type === 'colors' ? selectedColors.includes(item.name) : false
                                }
                                onChange={(e) => {
                                    if (type === 'categories') {
                                        handleCategoryChange(item.id, e.target.checked);
                                    } else if (type === 'sizes') {
                                        handleSizeChange(item.name, e.target.checked);
                                    } else if (type === 'colors') {
                                        handleColorChange(item.name, e.target.checked);
                                    }
                                }}
                            />
                        }
                        label={item.name}
                        className="w-full"
                    />
                ))}
                {items.length > limit && (
                    <Button
                        variant="text"
                        className="!text-[#ff5252] text-[13px] mt-1 !normal-case"
                        onClick={() => setShowAll(!showAll)}
                    >
                        {showAll ? "Thu gọn" : "Xem thêm..."}
                    </Button>
                )}
            </>
        );
    };

    if (loading) {
        return (
            <aside className="sidebar py-5">
                <div className="box p-4 text-center">
                    <span>Đang tải...</span>
                </div>
            </aside>
        );
    }

    if (error) {
        return (
            <aside className="sidebar py-5">
                <div className="box p-4 text-center text-red-500">
                    <span>{error}</span>
                </div>
            </aside>
        );
    }

    return (
        <aside className="sidebar py-5">
            <div className="box">
                <h3 className="w-full text-[16px] font-[600] flex items-center pr-5">
                    Shop by Category
                    <Button
                        className="!w-[30px] !h-[30px] !min-w-[30px] !rounded-full !ml-auto !text-[#000]"
                        onClick={() => setIsOpenCategoryFilter(!isOpenCategoryFilter)}
                    >
                        {isOpenCategoryFilter ? <FaAngleDown /> : <FaAngleUp />}
                    </Button>
                </h3>
                <Collapse isOpened={isOpenCategoryFilter}>
                    <div className="px-3 relative -left-[13px]">
                        {filterData.categories && filterData.categories.length > 0 ? (
                            filterData.categories.map((cat) => (
                                <FormControlLabel
                                    key={cat.id}
                                    control={
                                        <Checkbox
                                            size="small"
                                            checked={selectedCategoryIds.includes(cat.id)}
                                            onChange={(e) => handleCategoryChange(cat.id, e.target.checked)}
                                        />
                                    }
                                    label={cat.name}
                                    className="w-full"
                                />
                            ))
                        ) : (
                            <span className="text-gray-500 text-sm">Không có danh mục con</span>
                        )}
                    </div>
                </Collapse>
            </div>

            <div className="box mt-5">
                <h3 className="w-full text-[16px] font-[600] flex items-center pr-5">
                    Size
                    <Button
                        className="!w-[30px] !h-[30px] !min-w-[30px] !rounded-full !ml-auto !text-[#000]"
                        onClick={() => setIsOpenSizeFilter(!isOpenSizeFilter)}
                    >
                        {isOpenSizeFilter ? <FaAngleDown /> : <FaAngleUp />}
                    </Button>
                </h3>
                <Collapse isOpened={isOpenSizeFilter}>
                    <div className="px-3 relative -left-[13px]">
                        {filterData.sizes && filterData.sizes.length > 0 ? (
                            renderLimitedList(filterData.sizes, showAllSizes, setShowAllSizes, 'sizes')
                        ) : (
                            <span className="text-gray-500 text-sm">Không có size</span>
                        )}
                    </div>
                </Collapse>
            </div>

            <div className="box mt-5">
                <h3 className="w-full text-[16px] font-[600] flex items-center pr-5">
                    Color
                    <Button
                        className="!w-[30px] !h-[30px] !min-w-[30px] !rounded-full !ml-auto !text-[#000]"
                        onClick={() => setIsOpenColorFilter(!isOpenColorFilter)}
                    >
                        {isOpenColorFilter ? <FaAngleDown /> : <FaAngleUp />}
                    </Button>
                </h3>
                <Collapse isOpened={isOpenColorFilter}>
                    <div className="px-3 relative -left-[13px]">
                        {filterData.colors && filterData.colors.length > 0 ? (
                            renderLimitedList(filterData.colors, showAllColors, setShowAllColors, 'colors')
                        ) : (
                            <span className="text-gray-500 text-sm">Không có màu sắc</span>
                        )}
                    </div>
                </Collapse>
            </div>

            <div className="box mt-5">
                <h3 className="w-full mb-3 text-[16px] font-[600] flex items-center pr-5">
                    Filter By Price
                </h3>

                <div className="px-3 space-y-3">
                    <div className="flex gap-2 items-center">
                        <input
                            type="number"
                            placeholder="Giá tối thiểu"
                            value={tempMinPrice}
                            onChange={(e) => setTempMinPrice(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            min="0"
                        />
                        <span className="text-gray-500">-</span>
                        <input
                            type="number"
                            placeholder="Giá tối đa"
                            value={tempMaxPrice}
                            onChange={(e) => setTempMaxPrice(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            min="0"
                        />
                    </div>

                    <div className="flex gap-2">
                        <Button
                            onClick={handlePriceFilter}
                            className="!bg-blue-500 !text-white !text-xs !py-2 !px-4 !normal-case !rounded-md hover:!bg-blue-600"
                        >
                            Filter
                        </Button>
                        <Button
                            onClick={handleClearPrice}
                            className="!bg-gray-200 !text-gray-700 !text-xs !py-2 !px-4 !normal-case !rounded-md hover:!bg-gray-300"
                        >
                            Clear
                        </Button>
                    </div>

                    {(minPrice !== null && minPrice !== undefined) || (maxPrice !== null && maxPrice !== undefined) ? (
                        <div className="text-xs text-gray-600 mt-2">
                            Đang lọc: {minPrice || 0} - {maxPrice || '∞'}
                        </div>
                    ) : null}
                </div>
            </div>

            <div className="box mt-5">
                <h3 className="w-full mb-3 text-[16px] font-[600] flex items-center pr-5">
                    Filter By Rating
                </h3>
                {[5, 4, 3, 2, 1].map((star) => (
                    <div className="w-full flex items-center" key={star}>
                        <Checkbox
                            size="small"
                            checked={selectedRatings.includes(star)}
                            onChange={(e) => handleRatingChange(star, e.target.checked)}
                        />
                        <Rating
                            name={`rating-${star}`}
                            value={star}
                            size="small"
                            readOnly
                        />
                        <span className="ml-2 text-sm">& up</span>
                    </div>
                ))}
            </div>
        </aside>
    );
};

export default Sidebar