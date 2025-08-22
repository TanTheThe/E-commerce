import React, { useState, useEffect  } from "react";
import Sidebar from "../../components/Sidebar";
import Typography from '@mui/material/Typography';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Link from '@mui/material/Link';
import ProductItem from "../../components/ProductItem";
import ProductItemListView from "../../components/ProductItemListView";
import { IoGridSharp } from "react-icons/io5";
import { IoIosMenu } from "react-icons/io";
import Button from "@mui/material/Button";
import { LuMenu } from "react-icons/lu";
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Pagination from "@mui/material/Pagination";
import { useParams } from "react-router-dom";
import { getDataApi } from "../../utils/api";


function handleClick(event) {
    event.preventDefault();
    console.info('You clicked a breadcrumb.');
}

const ProductListing = () => {
    const { categoryId } = useParams();

    const [itemView, setItemView] = useState('grid');
    const [anchorEl, setAnchorEl] = useState(null);

    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [totalProducts, setTotalProducts] = useState(0);
    const [categoryName, setCategoryName] = useState('');

    const [currentPage, setCurrentPage] = useState(1);
    const [rowsPerPage] = useState(16); 
    const [sortBy, setSortBy] = useState('Newest First');

    const [searchVal, setSearchVal] = useState('');
    const [categoryFilterIds, setCategoryFilterIds] = useState([]);
    const [minPrice, setMinPrice] = useState(null);
    const [maxPrice, setMaxPrice] = useState(null);
    const [colors, setColors] = useState([]);
    const [sizes, setSizes] = useState([]);
    const [rating, setRating] = useState([]);

    const open = Boolean(anchorEl);

    const sortMapping = {
        'Newest First': 'newest',
        'Price, Low to High': 'price_asc',
        'Price, High to Low': 'price_desc',
        'Name, A to Z': 'name_asc',
        'Name, Z to A': 'name_desc',
        'Best Seller': 'best_seller',
        'Sale, High to Low': 'sale_desc'
    };

    const buildFilterData = () => {
        const filterData = {};

        if (searchVal?.trim()) filterData.search = searchVal.trim();
        if (categoryFilterIds?.length) filterData.category_ids = categoryFilterIds;
        if (minPrice) filterData.min_price = minPrice;
        if (maxPrice) filterData.max_price = maxPrice;
        if (sortBy && sortMapping[sortBy]) filterData.sort_by = sortMapping[sortBy];
        if (colors?.length) filterData.colors = colors;
        if (sizes?.length) filterData.sizes = sizes;
        if (rating?.length) filterData.rating = rating;

        return filterData;
    };

    const fetchProducts = async () => {
        setLoading(true);
        try {
            const skip = (currentPage - 1) * rowsPerPage;
            const filterData = buildFilterData();

            const queryParams = new URLSearchParams({
                skip: skip.toString(),
                limit: rowsPerPage.toString(),
            });

            if (categoryId) queryParams.append('category_id', categoryId);
            if (filterData.search) queryParams.append('search', filterData.search);
            if (filterData.category_ids?.length) {
                filterData.category_ids.forEach(id => queryParams.append('category_ids', id.toString()));
            }
            if (filterData.min_price) queryParams.append('min_price', filterData.min_price.toString());
            if (filterData.max_price) queryParams.append('max_price', filterData.max_price.toString());
            if (filterData.sort_by) queryParams.append('sort_by', filterData.sort_by);
            if (filterData.colors?.length) {
                filterData.colors.forEach(c => queryParams.append('colors', c));
            }
            if (filterData.sizes?.length) {
                filterData.sizes.forEach(s => queryParams.append('sizes', s));
            }
            if (filterData.rating?.length) {
                filterData.rating.forEach(r => queryParams.append('rating', r.toString()));
            }

            const response = await getDataApi(`/customer/product/category?${queryParams.toString()}`);

            if (response.success === true) {
                setProducts(response.data?.data || []);
                setTotalProducts(response.data?.data?.length || 0);
            } else {
                console.error('Failed to fetch products:', response.message);
                setProducts([]);
                setTotalProducts(0);
            }
        } catch (error) {
            console.error('Error fetching products:', error);
            setProducts([]);
            setTotalProducts(0);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (categoryId) {
            fetchProducts();
        }
    }, [categoryId, currentPage, sortBy, searchVal, categoryFilterIds, minPrice, maxPrice, colors, sizes, rating]);

    const handleSortChange = (option) => {
        setSortBy(option);
        setCurrentPage(1);
        setAnchorEl(null);
    };

    const handlePageChange = (event, page) => {
        setCurrentPage(page);
    };

    const updateFilters = (newFilters) => {
        if (newFilters.search !== undefined) setSearchVal(newFilters.search);
        if (newFilters.category_ids !== undefined) setCategoryFilterIds(newFilters.category_ids);
        if (newFilters.min_price !== undefined) setMinPrice(newFilters.min_price);
        if (newFilters.max_price !== undefined) setMaxPrice(newFilters.max_price);
        if (newFilters.colors !== undefined) setColors(newFilters.colors);
        if (newFilters.sizes !== undefined) setSizes(newFilters.sizes);
        if (newFilters.rating !== undefined) setRating(newFilters.rating);

        setCurrentPage(1);
    };

    const totalPages = Math.ceil(totalProducts / rowsPerPage);

    return (
        <section className="py-5 pb-0">
            <div className="container">
                <Breadcrumbs aria-label="breadcrumb">
                    <Link underline="hover" color="inherit" href="/" className="link transition">
                        Home
                    </Link>
                    <Link underline="hover" color="inherit" href="/" className="link transition">
                        {categoryName || 'Category'}
                    </Link>
                </Breadcrumbs>
            </div>

            <div className="bg-white p-2 mt-4">
                <div className="container flex gap-3">
                    <div className="sidebarWrapper w-[20%] h-full bg-white">
                        <Sidebar
                            filters={{
                                search: searchVal,
                                category_ids: categoryFilterIds,
                                min_price: minPrice,
                                max_price: maxPrice,
                                colors,
                                sizes,
                                rating
                            }}
                            onFiltersChange={updateFilters}
                            loading={loading}
                        />
                    </div>

                    <div className="rightContent w-[80%] py-3">
                        <div className="bg-[#f1f1f1] p-2 w-full mb-4 rounded-md flex items-center justify-between">
                            <div className="col1 flex items-center gap-3 itemViewActions">
                                <Button
                                    className={`!w-[40px] !h-[40px] !min-w-[40px] !rounded-full !text-[#000] ${itemView === "list" && "active"}`}
                                    onClick={() => setItemView('list')}
                                >
                                    <LuMenu className="text-[rgba(0,0,0,0.7)]" />
                                </Button>
                                <Button
                                    className={`!w-[40px] !h-[40px] !min-w-[40px] !rounded-full !text-[#000] ${itemView === "grid" && "active"}`}
                                    onClick={() => setItemView('grid')}
                                >
                                    <IoGridSharp className="text-[rgba(0,0,0,0.7)]" />
                                </Button>

                                <span className="text-[14px] font-[500] pl-3 text-[rgba(0,0,0,0.7)]">
                                    {loading ? 'Loading...' : `There are ${totalProducts} products.`}
                                </span>
                            </div>

                            <div className="col2 ml-auto flex items-center justify-end">
                                <span className="text-[14px] font-[500] pl-3 text-[rgba(0,0,0,0.7)]">Sort By</span>

                                <Button
                                    id="basic-button"
                                    aria-controls={open ? 'basic-menu' : undefined}
                                    aria-haspopup="true"
                                    aria-expanded={open ? 'true' : undefined}
                                    onClick={(e) => setAnchorEl(e.currentTarget)}
                                    className="!bg-white !text-[12px] !text-[#000] !capitalize"
                                >
                                    {sortBy}
                                </Button>
                                <Menu
                                    id="basic-menu"
                                    anchorEl={anchorEl}
                                    open={open}
                                    onClose={() => setAnchorEl(null)}
                                    slotProps={{
                                        list: { 'aria-labelledby': 'basic-button' },
                                    }}
                                >
                                    {Object.keys(sortMapping).map((option) => (
                                        <MenuItem
                                            key={option}
                                            onClick={() => handleSortChange(option)}
                                            className="!text-[13px] !text-[#000] !capitalize"
                                        >
                                            {option}
                                        </MenuItem>
                                    ))}
                                </Menu>
                            </div>
                        </div>

                        {loading ? (
                            <div className="text-center py-10">
                                <span>Đang tải sản phẩm...</span>
                            </div>
                        ) : (
                            <div className={`grid ${itemView === 'grid' ? 'grid-cols-4 md:grid-cols-4' : 'grid-cols-1 md:grid-cols-1'} gap-4`}>
                                {products.length > 0 ? (
                                    products.map((product) => (
                                        itemView === 'grid'
                                            ? <ProductItem key={product.id} product={product} />
                                            : <ProductItemListView key={product.id} product={product} />
                                    ))
                                ) : (
                                    <div className="col-span-full text-center py-10">
                                        <span>Không có sản phẩm nào được tìm thấy</span>
                                    </div>
                                )}
                            </div>
                        )}

                        {totalPages > 1 && (
                            <div className="flex items-center justify-center mt-10">
                                <Pagination
                                    count={totalPages}
                                    page={currentPage}
                                    onChange={handlePageChange}
                                    showFirstButton
                                    showLastButton
                                />
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </section>
    );
};

export default ProductListing