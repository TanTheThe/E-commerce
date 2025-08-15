import React, { useCallback, useContext, useEffect, useState } from "react";
import { Avatar, Button, DialogActions, DialogContent, DialogContentText, DialogTitle, Rating, TextField } from "@mui/material";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import { MenuItem, Select } from "@mui/material";
import { GoTrash } from "react-icons/go";
import SearchBox from "../../Components/SearchBox";

import Dialog from '@mui/material/Dialog';
import { MyContext } from "../../App";
import { deleteDataApi, getDataApi } from "../../utils/api";
import { debounce } from "lodash";
import { AiOutlineEye } from "react-icons/ai";
import ReviewDetailDialog from "./reviewDetail";

const columns = [
    { id: 'customer', label: 'CUSTOMER', minWidth: 200, align: 'left' },
    { id: 'product', label: 'PRODUCT', minWidth: 250, align: 'left' },
    { id: 'order_code', label: 'ORDER CODE', minWidth: 150, align: 'center' },
    { id: 'rating', label: 'RATING', minWidth: 120, align: 'center' },
    { id: 'created_at', label: 'CREATED AT', minWidth: 160, align: 'center' },
    { id: 'action', label: 'ACTION', minWidth: 120, align: 'center' }
];

const Reviews = () => {
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [page, setPage] = useState(0);
    const [reviews, setReviews] = useState([]);
    const [totalCount, setTotalCount] = useState(0);
    const [loading, setLoading] = useState(true);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [reviewToDelete, setReviewToDelete] = useState(null);
    const [deleting, setDeleting] = useState(false);
    const [detailDialogOpen, setDetailDialogOpen] = useState(false);
    const [reviewIdToView, setReviewIdToView] = useState(null);

    const [searchInput, setSearchInput] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [rateFilter, setRateFilter] = useState('');
    const [sortByCreatedAt, setSortByCreatedAt] = useState('');
    const [sortByRate, setSortByRate] = useState('');

    const context = useContext(MyContext);

    const buildQueryParams = (customPage = page, customRowsPerPage = rowsPerPage, customSearch = searchTerm) => {
        const params = new URLSearchParams();
        params.append('skip', (customPage * customRowsPerPage).toString());
        params.append('limit', customRowsPerPage.toString());

        if (customSearch) params.append('search', customSearch);
        if (rateFilter) params.append('rate', rateFilter);
        if (sortByCreatedAt) params.append('sort_by_created_at', sortByCreatedAt);
        if (sortByRate) params.append('sort_by_rate', sortByRate);

        return params.toString();
    };

    const fetchReviews = async (customPage = page, customRowsPerPage = rowsPerPage, customSearch = searchTerm) => {
        try {
            setLoading(true);
            const queryParams = buildQueryParams(customPage, customRowsPerPage, customSearch);
            const response = await getDataApi(`/admin/evaluate?${queryParams}`);

            if (response.success) {
                const responseData = response.data || response.content;
                setReviews(responseData.data || []);
                setTotalCount(responseData.total || 0);
            } else {
                context.openAlertBox("error", "Có lỗi trong quá trình tải danh sách đánh giá");
                setReviews([]);
                setTotalCount(0);
            }
        } catch (error) {
            context.openAlertBox("error", "Lỗi hệ thống khi tải đánh giá");
            setReviews([]);
            setTotalCount(0);
        } finally {
            setLoading(false);
        }
    };

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
        fetchReviews(newPage, rowsPerPage, searchTerm);
    };

    const handleChangeRowsPerPage = (event) => {
        const newRowsPerPage = +event.target.value;
        setRowsPerPage(newRowsPerPage);
        setPage(0);
        fetchReviews(0, newRowsPerPage, searchTerm);
    };

    const handleRateFilterChange = (event) => {
        setRateFilter(event.target.value);
    };

    const handleSortByCreatedAtChange = (event) => {
        setSortByCreatedAt(event.target.value);
    };

    const handleSortByRateChange = (event) => {
        setSortByRate(event.target.value);
    };

    const clearFilters = () => {
        setSearchInput('');
        setSearchTerm('');
        setRateFilter('');
        setSortByCreatedAt('');
        setSortByRate('');
        setPage(0);
    };

    const openDeleteDialog = (review) => {
        setReviewToDelete(review);
        setDeleteDialogOpen(true);
    };

    const closeDeleteDialog = () => {
        setDeleteDialogOpen(false);
        setReviewToDelete(null);
    };

    const openDetailDialog = (review) => {
        setReviewIdToView(review.id);
        setDetailDialogOpen(true);
    };

    const closeDetailDialog = () => {
        setDetailDialogOpen(false);
        setReviewIdToView(null);
    };

    const handleDeleteReview = async () => {
        if (!reviewToDelete) return;

        try {
            setDeleting(true);
            const response = await deleteDataApi(`/admin/evaluate/${reviewToDelete.id}`);

            if (response.success) {
                context.openAlertBox("success", response.message || "Xóa đánh giá thành công");
                fetchReviews(page, rowsPerPage, searchTerm);
                closeDeleteDialog();
            } else {
                context.openAlertBox("error", response.message || "Có lỗi trong quá trình xóa đánh giá");
            }
        } catch (error) {
            console.error('Error deleting review:', error);
            context.openAlertBox("error", "Có lỗi hệ thống trong quá trình xóa đánh giá!");
        } finally {
            setDeleting(false);
        }
    };

    const formatDate = (dateStr) => {
        return new Date(dateStr).toLocaleDateString('vi-VN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const truncateText = (text, maxLength = 50) => {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    };

    const debouncedSearch = useCallback(
        debounce((value) => {
            setSearchTerm(value);
            setPage(0);
            fetchReviews(0, rowsPerPage, value);
        }, 500),
        [rowsPerPage]
    );

    useEffect(() => {
        debouncedSearch(searchInput);
    }, [searchInput, debouncedSearch]);

    useEffect(() => {
        setPage(0);
        fetchReviews(0, rowsPerPage, searchTerm);
    }, [rateFilter, sortByCreatedAt, sortByRate]);

    useEffect(() => {
        fetchReviews();
    }, []);

    return (
        <>
            <div className="flex items-center justify-between px-2 py-0 mt-3">
                <h2 className="text-[18px] font-[600]">
                    Quản lý đánh giá sản phẩm
                </h2>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm my-4">
                <h3 className="text-lg font-semibold text-gray-700 mb-4">Bộ lọc tìm kiếm</h3>

                <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Tìm kiếm (tên khách hàng, sản phẩm, mã đơn hàng)
                    </label>
                    <SearchBox searchTerm={searchInput} setSearchTerm={setSearchInput} />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div className="flex flex-col">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Lọc theo điểm</label>
                        <Select value={rateFilter} onChange={handleRateFilterChange} className="w-full h-11">
                            <MenuItem value="">-- Tất cả điểm --</MenuItem>
                            <MenuItem value="5">5 sao</MenuItem>
                            <MenuItem value="4">4 sao</MenuItem>
                            <MenuItem value="3">3 sao</MenuItem>
                            <MenuItem value="2">2 sao</MenuItem>
                            <MenuItem value="1">1 sao</MenuItem>
                        </Select>
                    </div>

                    <div className="flex flex-col">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Sắp xếp theo thời gian</label>
                        <Select value={sortByCreatedAt} onChange={handleSortByCreatedAtChange} className="w-full h-11">
                            <MenuItem value="">-- Mặc định --</MenuItem>
                            <MenuItem value="newest">Mới nhất</MenuItem>
                            <MenuItem value="oldest">Cũ nhất</MenuItem>
                        </Select>
                    </div>

                    <div className="flex flex-col">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Sắp xếp theo điểm</label>
                        <Select value={sortByRate} onChange={handleSortByRateChange} className="w-full h-11">
                            <MenuItem value="">-- Mặc định --</MenuItem>
                            <MenuItem value="highest">Cao nhất</MenuItem>
                            <MenuItem value="lowest">Thấp nhất</MenuItem>
                        </Select>
                    </div>

                    <div className="flex flex-col justify-end">
                        <Button
                            onClick={clearFilters}
                            className="h-12 bg-gray-50 hover:bg-gray-100 text-gray-700 border-2 border-gray-300 hover:border-gray-400 rounded-md font-medium transition-all duration-200 flex items-center justify-center gap-2"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                            Xóa bộ lọc
                        </Button>
                    </div>
                </div>

                {(searchTerm || rateFilter || sortByCreatedAt || sortByRate) && (
                    <div className="mt-6 pt-4 border-t border-gray-200">
                        <p className="text-sm text-gray-600 mb-2">Bộ lọc hiện tại:</p>
                        <div className="flex flex-wrap gap-2">
                            {searchTerm && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                    Tìm kiếm: "{searchTerm}"
                                </span>
                            )}
                            {rateFilter && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                    Điểm: {rateFilter} sao
                                </span>
                            )}
                            {sortByCreatedAt && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                    Thời gian: {sortByCreatedAt === 'newest' ? 'Mới nhất' : 'Cũ nhất'}
                                </span>
                            )}
                            {sortByRate && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                    Điểm: {sortByRate === 'highest' ? 'Cao nhất' : 'Thấp nhất'}
                                </span>
                            )}
                        </div>
                    </div>
                )}
            </div>

            <div className="card my-4 pt-5 shadow-md sm:rounded-lg bg-white">
                {loading ? (
                    <div className="flex justify-center items-center py-8">
                        <div className="text-gray-500">Đang tải dữ liệu...</div>
                    </div>
                ) : (
                    <>
                        <TableContainer sx={{ maxHeight: 600 }}>
                            <Table stickyHeader aria-label="sticky table">
                                <TableHead className="bg-[#f1f1f1]">
                                    <TableRow>
                                        {columns.map((column) => (
                                            <TableCell
                                                width={column.minWidth}
                                                key={column.id}
                                                align={column.align}
                                            >
                                                {column.label}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {reviews.length === 0 ? (
                                        <TableRow>
                                            <TableCell colSpan={columns.length} align="center">
                                                <div className="py-8 text-gray-500">
                                                    Không tìm thấy đánh giá nào
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    ) : (
                                        reviews.map((review) => {
                                            return (
                                                <TableRow key={review.id} hover>
                                                    <TableCell align="left">
                                                        <div className="flex items-center gap-3">
                                                            <div>
                                                                <div className="font-medium text-sm">
                                                                    {review.customer?.full_name ||
                                                                        `${review.customer?.first_name || ''} ${review.customer?.last_name || ''}`.trim() ||
                                                                        'N/A'}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </TableCell>

                                                    <TableCell align="left">
                                                        <div>
                                                            <div className="font-medium text-sm">
                                                                {review.product?.name || 'N/A'}
                                                            </div>
                                                            {(review.product?.size || review.product?.color_name) && (
                                                                <div className="text-xs text-gray-500 mt-1">
                                                                    {review.product.size && `Size: ${review.product.size}`}
                                                                    {review.product.size && review.product.color_name && ' | '}
                                                                    {review.product.color_name && `Color: ${review.product.color_name}`}
                                                                </div>
                                                            )}
                                                        </div>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">
                                                            {review.code || 'N/A'}
                                                        </span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <Rating
                                                            value={review.rate}
                                                            readOnly
                                                            size="small"
                                                        />
                                                        <div className="text-xs text-gray-500 mt-1">
                                                            {review.rate}/5
                                                        </div>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <span className="text-sm">
                                                            {formatDate(review.created_at)}
                                                        </span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <div className="flex items-center justify-center gap-2">
                                                            <Button
                                                                className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-blue-100 !min-w-[35px]"
                                                                onClick={() => openDetailDialog(review)}
                                                                title="Xem chi tiết"
                                                            >
                                                                <AiOutlineEye className="text-[rgba(0,0,0,0.7)] text-[18px]" />
                                                            </Button>

                                                            <Button
                                                                className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-red-100 !min-w-[35px]"
                                                                onClick={() => openDeleteDialog(review)}
                                                                title="Xóa"
                                                                disabled={deleting}
                                                            >
                                                                <GoTrash className="text-[rgba(0,0,0,0.7)] text-[18px] hover:text-red-600" />
                                                            </Button>
                                                        </div>
                                                    </TableCell>
                                                </TableRow>
                                            );
                                        })
                                    )}
                                </TableBody>
                            </Table>
                        </TableContainer>

                        <TablePagination
                            rowsPerPageOptions={[10, 25, 50, 100]}
                            component="div"
                            count={totalCount}
                            rowsPerPage={rowsPerPage}
                            page={page}
                            onPageChange={handleChangePage}
                            onRowsPerPageChange={handleChangeRowsPerPage}
                            labelRowsPerPage="Số hàng mỗi trang:"
                            labelDisplayedRows={({ from, to, count }) =>
                                `${from}-${to} trong tổng số ${count !== -1 ? count : `hơn ${to}`}`
                            }
                        />
                    </>
                )}
            </div>

            <Dialog
                open={deleteDialogOpen}
                onClose={closeDeleteDialog}
                aria-labelledby="delete-dialog-title"
                aria-describedby="delete-dialog-description"
            >
                <DialogTitle id="delete-dialog-title">
                    Xác nhận xóa đánh giá
                </DialogTitle>
                <DialogContent>
                    <DialogContentText id="delete-dialog-description">
                        Bạn có chắc chắn muốn xóa đánh giá của khách hàng "{reviewToDelete?.customer?.full_name || `${reviewToDelete?.customer?.first_name || ''} ${reviewToDelete?.customer?.last_name || ''}`.trim()}"?
                        <br />
                        <strong>Hành động này không thể hoàn tác!</strong>
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={closeDeleteDialog} disabled={deleting}>
                        Hủy
                    </Button>
                    <Button
                        onClick={handleDeleteReview}
                        autoFocus
                        color="error"
                        disabled={deleting}
                    >
                        {deleting ? 'Đang xóa...' : 'Xóa'}
                    </Button>
                </DialogActions>
            </Dialog>

            <ReviewDetailDialog
                open={detailDialogOpen}
                onClose={closeDetailDialog}
                reviewId={reviewIdToView}
            />
        </>
    )
}

export default Reviews