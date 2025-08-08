import React, { useContext, useEffect, useState } from "react";
import { Button, DialogActions, DialogContent, DialogContentText, DialogTitle, TextField } from "@mui/material";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import { MenuItem, Select } from "@mui/material";
import { AiOutlineEdit } from "react-icons/ai";
import { FaRegEye } from "react-icons/fa";
import { GoTrash } from "react-icons/go";
import Checkbox from '@mui/material/Checkbox';
import SearchBox from "../../Components/SearchBox";
import Dialog from '@mui/material/Dialog';
import { MyContext } from "../../App";
import { deleteDataApi, getDataApi, postDataApi } from "../../utils/api";
import ProductDetailOffcanvas from "./offcanvasProductDetail";
import debounce from 'lodash/debounce';
import { useCallback } from 'react';


const label = { inputProps: { 'aria-label': 'Checkbox demo' } };

const columns = [
    { id: 'product', label: 'PRODUCT', minWidth: 200 },
    { id: 'category', label: 'CATEGORY', minWidth: 150 },
    {
        id: 'variants',
        label: 'VARIANTS',
        minWidth: 100
    },
    {
        id: 'priceRange',
        label: 'PRICE RANGE',
        minWidth: 150,
    },
    {
        id: 'createdAt',
        label: 'CREATED AT',
        minWidth: 150,
    },
    {
        id: 'actions',
        label: 'ACTIONS',
        minWidth: 150,
    },
];

const Products = () => {
    const [categoryFilterVal, setCategoryFilterVal] = useState('');
    const [minPrice, setMinPrice] = useState('');
    const [maxPrice, setMaxPrice] = useState('');
    const [debouncedMinPrice, setDebouncedMinPrice] = useState('');
    const [debouncedMaxPrice, setDebouncedMaxPrice] = useState('');
    const [minPriceError, setMinPriceError] = useState('');
    const [maxPriceError, setMaxPriceError] = useState('');
    const [searchVal, setSearchVal] = useState('');
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [page, setPage] = useState(0);
    const [isOffcanvasOpen, setIsOffcanvasOpen] = useState(false);
    const [selectedProduct, setSelectedProduct] = useState(null);
    const [selectedProductIds, setSelectedProductIds] = useState([]);

    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [totalProducts, setTotalProducts] = useState(0);
    const [categories, setCategories] = useState([]);

    const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
    const [productToDelete, setProductToDelete] = useState(null);

    const context = useContext(MyContext);

    const fetchCategories = async () => {
        try {
            const res = await getDataApi(`/admin/categories`);
            if (res.success === true) {
                setCategories(res.data || []);
            } else {
                console.error("Failed to fetch categories:", res.message);
                setCategories([]);
            }
        } catch (error) {
            console.error("Error fetching categories:", error);
            setCategories([]);
        }
    };

    const buildFilterData = () => {
        const filterData = {};

        if (searchVal && searchVal.trim()) {
            filterData.search = searchVal.trim();
        }

        if (categoryFilterVal) {
            filterData.category_ids = [categoryFilterVal];
        }

        if (debouncedMinPrice && !minPriceError && Number.isInteger(parseFloat(debouncedMinPrice)) && parseFloat(debouncedMinPrice) > 0) {
            filterData.min_price = parseInt(debouncedMinPrice);
        }

        if (debouncedMaxPrice && !maxPriceError && Number.isInteger(parseFloat(debouncedMaxPrice)) && parseFloat(debouncedMaxPrice) > 0) {
            filterData.max_price = parseInt(debouncedMaxPrice);
        }

        return filterData;
    };

    const fetchProducts = async () => {
        setLoading(true);
        try {
            const skip = page * rowsPerPage;
            const limit = rowsPerPage;
            const filterData = buildFilterData();

            const response = await postDataApi(`/admin/product/all?skip=${skip}&limit=${limit}`, filterData);

            if (response.success === true) {
                setProducts(response.data.data || []);
                setTotalProducts(response.data.total || 0);
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

    const fetchProductDetail = async (productId) => {
        try {
            const response = await getDataApi(`/admin/product/${productId}`);

            if (response.success === true) {
                return response.data;
            } else {
                console.error('Failed to fetch product detail:', response.message);
                return null;
            }
        } catch (error) {
            console.error('Error fetching product detail:', error);
            return null;
        }
    };

    const handleProductUpdated = () => {
        setPage(0);
        fetchProducts();
    };

    useEffect(() => {
        fetchProducts();
    }, [page, rowsPerPage, searchVal, categoryFilterVal, debouncedMinPrice, debouncedMaxPrice]);

    useEffect(() => {
        fetchCategories();
    }, []);

    const handleChangeCateFilter = (event) => {
        setCategoryFilterVal(event.target.value);
        setPage(0);
    };

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(+event.target.value);
        setPage(0);
    };

    const validatePriceInput = (value, setError) => {
        if (value === '') {
            setError('');
            return true;
        }

        if (!/^\d+$/.test(value)) {
            setError('Vui lòng chỉ nhập số nguyên');
            return false;
        }

        const numValue = parseInt(value);
        if (numValue <= 0) {
            setError('Giá phải lớn hơn 0');
            return false;
        }

        if (numValue > 1000000000) {
            setError('Giá không được vượt quá 1 tỷ');
            return false;
        }

        setError('');
        return true;
    };

    const handleMinPriceChange = (event) => {
        const value = event.target.value;
        if (value === '' || /^\d+$/.test(value)) {
            setMinPrice(value);
            validatePriceInput(value, setMinPriceError);
        }
    };

    const handleMaxPriceChange = (event) => {
        const value = event.target.value;
        if (value === '' || /^\d+$/.test(value)) {
            setMaxPrice(value);
            validatePriceInput(value, setMaxPriceError);
        }
    };

    const clearPriceFilter = () => {
        setMinPrice('');
        setMaxPrice('');
        setDebouncedMinPrice('');
        setDebouncedMaxPrice('');
        setMinPriceError('');
        setMaxPriceError('');
        setPage(0);
    };

    const handleDeleteProduct = async (productId) => {
        try {
            const response = await deleteDataApi(`/admin/product/${productId}`);
            if (response.success) {
                context.openAlertBox('success', response.message);
                fetchProducts();
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || 'Xóa sản phẩm thất bại')
            }
        } catch (error) {
            console.error('Lỗi khi xóa sản phẩm:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi xóa sản phẩm');
        }
    };

    const handleDeleteMultipleProducts = async () => {
        try {
            console.log(selectedProductIds);
            const response = await postDataApi(`/admin/product/delete`, {
                product_ids: selectedProductIds
            });
            if (response.success) {
                context.openAlertBox('success', `Đã xóa ${selectedProductIds.length} sản phẩm thành công.`);
                setSelectedProductIds([]);
                fetchProducts();
            } else {
                context.openAlertBox("error", response?.data?.detail || "Xóa thất bại");
            }
        } catch (error) {
            console.error(error);
            context.openAlertBox('error', 'Lỗi hệ thống khi xóa sản phẩm');
        } finally {
            setDeleteConfirmOpen(false);
        }
    };

    const formatPriceRange = (priceRange) => {
        if (!priceRange) return 'N/A';
        if (priceRange.min === priceRange.max) {
            return `${priceRange.min.toLocaleString('vi-VN')}đ`;
        }
        return `${priceRange.min.toLocaleString('vi-VN')}đ - ${priceRange.max.toLocaleString('vi-VN')}đ`;;
    };

    const handleViewProduct = async (product) => {
        setLoading(true);
        const productDetail = await fetchProductDetail(product.id);

        if (productDetail) {
            setSelectedProduct(productDetail);
            setIsOffcanvasOpen(true);
        }
        setLoading(false);
    };

    const handleCloseOffcanvas = () => {
        setIsOffcanvasOpen(false);
        setSelectedProduct(null);
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString("vi-VN", {
            day: "2-digit", month: "2-digit", year: "numeric"
        });
    };

    const debouncedSearch = useCallback(
        debounce((searchTerm) => {
            console.log('Search value changed:', searchTerm); // Debug log
            setSearchVal(searchTerm);
            setPage(0);
        }, 500),
        []
    );

    const debouncedPriceFilter = useCallback(
        debounce((minPrice, maxPrice, minError, maxError) => {
            if (!minError) {
                setDebouncedMinPrice(minPrice);
            }
            if (!maxError) {
                setDebouncedMaxPrice(maxPrice);
            }
            setPage(0);
        }, 800),
        []
    );

    useEffect(() => {
        debouncedPriceFilter(minPrice, maxPrice, minPriceError, maxPriceError);
    }, [minPrice, maxPrice, minPriceError, maxPriceError]);

    return (
        <>
            <div className="flex items-center justify-between px-2 py-0 mt-3">
                <h2 className="text-[18px] font-[600]">
                    Danh sách sản phẩm{" "}
                </h2>

                <div className="col w-[18%] ml-auto flex items-center justify-end gap-3">
                    <Button className="btn !bg-green-600 !text-white btn-sm flex items-center">Export</Button>
                    <Button className="btn-blue !text-white btn-sm"
                        onClick={() => context.setIsOpenFullScreenPanel({
                            open: true,
                            model: 'Add Product',
                            onUpdated: handleProductUpdated
                        })}>Add Product</Button>
                </div>
            </div>

            <div className="card my-4 pt-5 shadow-md sm:rounded-lg bg-white">
                <div className="flex items-center w-full px-5 justify-between">
                    <div className="flex items-center gap-4 w-[60%]">
                        <div className="col w-[30%]">
                            <h4 className="font-[600] text-[13px] mb-3">Sắp xếp theo danh mục</h4>
                            <Select
                                className="w-full mb-5"
                                size="small"
                                labelId="demo-simple-select-standard-label"
                                id="demo-simple-select-standard"
                                value={categoryFilterVal}
                                onChange={handleChangeCateFilter}
                                label="Category"
                            >
                                <MenuItem value="">
                                    <em>All Categories</em>
                                </MenuItem>
                                {categories.map((category) => (
                                    <MenuItem key={category.id} value={category.id}>
                                        {category.name}
                                    </MenuItem>
                                ))}
                            </Select>
                        </div>

                        <div className="col w-[30%]">
                            <h4 className="font-[600] text-[13px] mb-3">Lọc theo giá</h4>
                            <div className="flex flex-col gap-2 mb-5">
                                <div className="flex gap-2 items-start">
                                    <div className="flex-1">
                                        <TextField
                                            size="small"
                                            type="text"
                                            placeholder="Giá từ"
                                            value={minPrice}
                                            onChange={handleMinPriceChange}
                                            error={!!minPriceError}
                                            helperText={minPriceError}
                                            InputProps={{
                                                endAdornment: <span className="text-sm text-gray-500">đ</span>
                                            }}
                                            FormHelperTextProps={{
                                                style: { fontSize: '10px', marginTop: '4px' }
                                            }}
                                        />
                                    </div>
                                    <span className="text-gray-400 mt-2">-</span>
                                    <div className="flex-1">
                                        <TextField
                                            size="small"
                                            type="text"
                                            placeholder="Giá đến"
                                            value={maxPrice}
                                            onChange={handleMaxPriceChange}
                                            error={!!maxPriceError}
                                            helperText={maxPriceError}
                                            InputProps={{
                                                endAdornment: <span className="text-sm text-gray-500">đ</span>
                                            }}
                                            FormHelperTextProps={{
                                                style: { fontSize: '10px', marginTop: '4px' }
                                            }}
                                        />
                                    </div>
                                </div>
                                {(minPrice || maxPrice) && (
                                    <Button
                                        size="small"
                                        onClick={clearPriceFilter}
                                        className="!text-xs !text-red-500 !p-1 !min-w-0 self-start"
                                    >
                                        Xóa bộ lọc giá
                                    </Button>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="col w-[20%] ml-auto">
                        <SearchBox onSearch={debouncedSearch} />
                    </div>
                </div>

                {loading ? (
                    <div className="flex justify-center items-center h-64">
                        <div className="text-lg">Đang tải...</div>
                    </div>
                ) :
                    <>
                        <TableContainer sx={{ maxHeight: 440 }}>
                            <Table stickyHeader aria-label="sticky table">
                                <TableHead className="bg-[#f1f1f1]">
                                    <TableRow>
                                        <TableCell>
                                            <Checkbox {...label} size="small"
                                                checked={selectedProductIds.length === products.length && products.length > 0}
                                                indeterminate={selectedProductIds.length > 0 && selectedProductIds.length < products.length}
                                                onChange={(e) => {
                                                    if (e.target.checked) {
                                                        const allIds = products.map(p => p.id);
                                                        setSelectedProductIds(allIds);
                                                    } else {
                                                        setSelectedProductIds([]);
                                                    }
                                                }} />
                                        </TableCell>
                                        {columns.map((column) => (
                                            <TableCell
                                                key={column.id}
                                                align={column.align}
                                                style={{ minWidth: column.minWidth }}
                                            >
                                                {column.label}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {products.map((product) => {
                                        return (
                                            <TableRow key={product.id}>
                                                <TableCell>
                                                    <Checkbox {...label} size="small"
                                                        checked={selectedProductIds.includes(product.id)}
                                                        onChange={(e) => {
                                                            if (e.target.checked) {
                                                                setSelectedProductIds(prev => [...prev, product.id]);
                                                            } else {
                                                                setSelectedProductIds(prev => prev.filter(id => id !== product.id));
                                                            }
                                                        }} />
                                                </TableCell>

                                                <TableCell style={{ minWidth: 200 }}>
                                                    <div className="flex items-center gap-4 w-[350px]">
                                                        <div className="img w-[65px] h-[65px] rounded-md overflow-hidden group">
                                                            <a href={`/product/${product.id}`} data-discover="true">
                                                                <img className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                                                                    src={product.images?.[0] || '/placeholder-image.jpg'}
                                                                    alt={product.name} />
                                                            </a>
                                                        </div>
                                                        <div className="info w-[75%]">
                                                            <h3 className="font-[700] text-[14px] leading-4 hover:text-[#3872fa] font-[Montserrat] text-gray-500">
                                                                <a href={`/product/${product.id}`} data-discover="true">
                                                                    {product.name}
                                                                </a>
                                                            </h3>
                                                        </div>
                                                    </div>
                                                </TableCell>

                                                <TableCell style={{ minWidth: 150 }}>
                                                    <div className="flex flex-wrap gap-1">
                                                        {product.categories?.map((category, index) => (
                                                            <span key={index}
                                                                className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded font-[Montserrat]">
                                                                {category.name}
                                                            </span>
                                                        )) || <span className="text-gray-400">No category</span>}
                                                    </div>
                                                </TableCell>

                                                <TableCell style={{ minWidth: 100 }}>
                                                    <div className="flex items-center gap-2">
                                                        <span className="bg-gray-100 text-gray-800 text-sm font-medium px-2.5 py-1 rounded-full font-[Montserrat]">
                                                            {typeof product.variant_count === 'number' ? product.variant_count : 0}
                                                        </span>
                                                    </div>
                                                </TableCell>

                                                <TableCell style={{ minWidth: 150 }}>
                                                    <div className="flex flex-col gap-1">
                                                        <span className="text-[14px] font-[500] font-[Montserrat] text-gray-600">
                                                            {formatPriceRange(product.price_range)}
                                                        </span>
                                                    </div>
                                                </TableCell>

                                                <TableCell style={{ minWidth: 150 }}>
                                                    <div className="flex flex-col gap-1">
                                                        <span className="text-[14px] font-[500] font-[Montserrat] text-gray-600">
                                                            {formatDate(product.created_at)}
                                                        </span>
                                                    </div>
                                                </TableCell>

                                                <TableCell style={{ minWidth: 150 }}>
                                                    <div className="flex items-center gap-2">
                                                        <Button
                                                            className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-[#f1f1f1] !min-w-[35px] !text-black"
                                                            onClick={() => context.setIsOpenFullScreenPanel({
                                                                open: true,
                                                                model: 'Update Product',
                                                                productId: product.id,
                                                                onUpdated: handleProductUpdated
                                                            })}>
                                                            <AiOutlineEdit />
                                                        </Button>

                                                        <Button
                                                            className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-[#f1f1f1] !min-w-[35px]"
                                                            onClick={() => handleViewProduct(product)}
                                                            disabled={loading}
                                                        >
                                                            <FaRegEye className="text-[rgba(0,0,0,0.7)] text-[20px]" />
                                                        </Button>

                                                        <Button className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-[#f1f1f1] !min-w-[35px]"
                                                            onClick={() => {
                                                                setProductToDelete(product);
                                                                setDeleteConfirmOpen(true);
                                                            }}>
                                                            <GoTrash className="text-[rgba(0,0,0,0.7)] text-[20px]" />
                                                        </Button>
                                                    </div>
                                                </TableCell>
                                            </TableRow>
                                        );
                                    })}
                                </TableBody>
                            </Table>
                        </TableContainer>

                        <TablePagination
                            rowsPerPageOptions={[10, 25, 100]}
                            component="div"
                            count={totalProducts}
                            rowsPerPage={rowsPerPage}
                            page={page}
                            onPageChange={handleChangePage}
                            onRowsPerPageChange={handleChangeRowsPerPage}
                        />
                    </>
                }
            </div>

            {selectedProductIds.length > 0 && (
                <Button
                    className="!bg-red-600 !text-white btn-sm ml-4"
                    onClick={() => setDeleteConfirmOpen(true)}
                >
                    Xóa {selectedProductIds.length} sản phẩm
                </Button>
            )}

            <ProductDetailOffcanvas
                open={isOffcanvasOpen}
                onClose={handleCloseOffcanvas}
                product={selectedProduct} />

            <Dialog open={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)}>
                <DialogTitle>Xác nhận xóa sản phẩm</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        {productToDelete
                            ? <>Bạn có chắc chắn muốn xóa sản phẩm <strong>{productToDelete.name}</strong> không?</>
                            : <>Bạn có chắc chắn muốn xóa <strong>{selectedProductIds.length}</strong> sản phẩm đã chọn không?</>
                        }
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => {
                        setDeleteConfirmOpen(false);
                        setProductToDelete(null);
                    }}>
                        Hủy
                    </Button>

                    <Button
                        color="error"
                        onClick={async () => {
                            if (productToDelete) {
                                await handleDeleteProduct(productToDelete.id);
                                setProductToDelete(null);
                                setDeleteConfirmOpen(false);
                            } else {
                                await handleDeleteMultipleProducts();
                            }
                        }}
                    >
                        Xóa
                    </Button>
                </DialogActions>
            </Dialog>

        </>
    )
}

export default Products