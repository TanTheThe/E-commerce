import React, { useCallback, useContext, useEffect, useState } from "react";
import { Button, DialogActions, DialogContent, DialogContentText, DialogTitle, TextField } from "@mui/material";
import { IoMdAdd } from "react-icons/io";

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
import ProgressBar from "../../Components/ProgressBar";
import Checkbox from '@mui/material/Checkbox';
import SearchBox from "../../Components/SearchBox";

import Dialog from '@mui/material/Dialog';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Slide from '@mui/material/Slide';
import { MyContext } from "../../App";
import { deleteDataApi, getDataApi } from "../../utils/api";
import AddSpecialOffer from "./addSpecialOffer";
import EditSpecialOffer from "./editSpecialOffer";
import { debounce } from "lodash";

const columns = [
    { id: 'code', label: 'CODE', minWidth: 100, align: 'center' },
    { id: 'name', label: 'NAME', minWidth: 200, align: 'center' },
    { id: 'total_quantity', label: 'TOTAL QUANTITY', minWidth: 200, align: 'center' },
    { id: 'used_quantity', label: 'USED QUANTITY', minWidth: 200, align: 'center' },
    { id: 'discount', label: 'DISCOUNT', minWidth: 100, align: 'center' },
    { id: 'type', label: 'TYPE', minWidth: 100, align: 'center' },
    { id: 'condition', label: 'CONDITION', minWidth: 200, align: 'center' },
    { id: 'start_time', label: 'START', minWidth: 150, align: 'center' },
    { id: 'end_time', label: 'END', minWidth: 150, align: 'center' },
    { id: 'action', label: 'ACTION', minWidth: 150, align: 'center' }
];

const SpecialOffer = () => {
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [page, setPage] = useState(0);
    const [offers, setOffers] = useState([]);
    const [totalCount, setTotalCount] = useState(0);
    const [loading, setLoading] = useState(true);
    const [isOpen, setIsOpen] = useState(false);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [offerToDelete, setOfferToDelete] = useState(null);
    const [deleting, setDeleting] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [offerToEdit, setOfferToEdit] = useState(null);

    const [searchInput, setSearchInput] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [typeFilter, setTypeFilter] = useState('');
    const [discountMin, setDiscountMin] = useState('');
    const [discountMax, setDiscountMax] = useState('');
    const [quantityStatus, setQuantityStatus] = useState('');
    const [timeStatus, setTimeStatus] = useState('');

    const context = useContext(MyContext);

    const buildQueryParams = (customPage = page, customRowsPerPage = rowsPerPage, customSearch = searchTerm) => {
        const params = new URLSearchParams();
        params.append('skip', (customPage * customRowsPerPage).toString());
        params.append('limit', customRowsPerPage.toString());

        if (customSearch) params.append('search', customSearch);
        if (typeFilter) params.append('type', typeFilter);
        if (discountMin && discountMin !== '') params.append('discount_min', discountMin.toString());
        if (discountMax && discountMax !== '') params.append('discount_max', discountMax.toString());
        if (quantityStatus) params.append('quantity_status', quantityStatus);
        if (timeStatus) params.append('time_status', timeStatus);

        return params.toString();
    };

    const fetchOffers = async (customPage = page, customRowsPerPage = rowsPerPage, customSearch = searchTerm) => {
        try {
            setLoading(true);
            const queryParams = buildQueryParams(customPage, customRowsPerPage, customSearch);
            const response = await getDataApi(`/admin/special-offer?${queryParams}`);

            if (response.success) {
                const responseData = response.data || response.content;
                setOffers(responseData.data || []);
                setTotalCount(responseData.total || 0);
            } else {
                context.openAlertBox("error", "Có lỗi trong quá trình tải danh sách voucher");
                setOffers([]);
                setTotalCount(0);
            }
        } catch (error) {
            context.openAlertBox("error", "Lỗi hệ thống khi tải voucher");
            setOffers([]);
            setTotalCount(0);
        } finally {
            setLoading(false);
        }
    };

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
        fetchOffers(newPage, rowsPerPage, searchTerm);
    };

    const handleChangeRowsPerPage = (event) => {
        const newRowsPerPage = +event.target.value;
        setRowsPerPage(newRowsPerPage);
        setPage(0);
        fetchOffers(0, newRowsPerPage, searchTerm);
    };

    const handleTypeFilterChange = (event) => {
        setTypeFilter(event.target.value);
    };

    const handleDiscountMinChange = (event) => {
        setDiscountMin(event.target.value);
    };

    const handleDiscountMaxChange = (event) => {
        const value = event.target.value;
        setDiscountMax(value);
    };

    const debouncedDiscountFilter = useCallback(
        debounce(() => {
            setPage(0);
            fetchOffers(0, rowsPerPage, searchTerm);
        }, 500),
        []
    );

    const handleQuantityStatusChange = (event) => {
        setQuantityStatus(event.target.value);
    };

    const handleTimeStatusChange = (event) => {
        setTimeStatus(event.target.value);
    };

    const clearFilters = () => {
        setSearchInput('');
        setSearchTerm('');
        setTypeFilter('');
        setDiscountMin('');
        setDiscountMax('');
        setQuantityStatus('');
        setTimeStatus('');
        setPage(0);
    };

    const openDeleteDialog = (offer) => {
        setOfferToDelete(offer);
        setDeleteDialogOpen(true);
    };

    const closeDeleteDialog = () => {
        setDeleteDialogOpen(false);
        setOfferToDelete(null);
    };

    const handleDeleteOffer = async () => {
        if (!offerToDelete) return;

        try {
            setDeleting(true);

            const response = await deleteDataApi(`/admin/special-offer/${offerToDelete.id}`);

            if (response.success) {
                context.openAlertBox("success", response.message || "Xóa mã khuyến mãi thành công");
                fetchOffers(page, rowsPerPage, searchTerm);
                closeDeleteDialog();
            } else {
                context.openAlertBox("error", response.message || "Có lỗi trong quá trình xóa mã khuyến mãi");
            }
        } catch (error) {
            console.error('Error deleting offer:', error);
            context.openAlertBox("error", "Có lỗi hệ thống trong quá trình xóa mã khuyến mãi!");
        } finally {
            setDeleting(false);
        }
    };

    const formatDate = (dateStr) => {
        return new Date(dateStr).toLocaleDateString('vi-VN', {
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const debouncedSearch = useCallback(
        debounce((value) => {
            setSearchTerm(value);
            setPage(0);
            fetchOffers(0, rowsPerPage, value);
        }, 500),
        [rowsPerPage]
    );

    useEffect(() => {
        debouncedSearch(searchInput);
    }, [searchInput, debouncedSearch]);

    useEffect(() => {
        setPage(0);
        fetchOffers(0, rowsPerPage, searchTerm);
    }, [typeFilter, quantityStatus, timeStatus]);

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            setPage(0);
            fetchOffers(0, rowsPerPage, searchTerm);
        }, 500);

        return () => clearTimeout(timeoutId);
    }, [discountMin, discountMax]);

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            if (discountMin || discountMax) {
                setPage(0);
                fetchOffers(0, rowsPerPage, searchTerm);
            }
        }, 500);

        return () => clearTimeout(timeoutId);
    }, [discountMin, discountMax]);

    useEffect(() => {
        return () => {
            debouncedDiscountFilter.cancel && debouncedDiscountFilter.cancel();
        };
    }, []);

    useEffect(() => {
        fetchOffers();
    }, []);

    return (
        <>
            <div className="flex items-center justify-between px-2 py-0 mt-3">
                <h2 className="text-[18px] font-[600]">
                    Danh sách các mã khuyến mãi
                </h2>

                <div className="col w-[30%] ml-auto flex items-center justify-end gap-3">
                    <Button
                        className="btn-blue !text-white btn-sm"
                        onClick={() => setIsOpen(true)}
                    >
                        Tạo mã khuyến mãi
                    </Button>
                    <AddSpecialOffer
                        open={isOpen}
                        onClose={() => setIsOpen(false)}
                        onSuccess={() => {
                            fetchOffers(page, rowsPerPage, searchTerm);
                        }}
                    />
                </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm my-4">
                <h3 className="text-lg font-semibold text-gray-700 mb-4">Bộ lọc tìm kiếm</h3>

                <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Tìm kiếm</label>
                    <SearchBox searchTerm={searchInput} setSearchTerm={setSearchInput} />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    <div className="flex flex-col">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Loại khuyến mãi</label>
                        <Select value={typeFilter} onChange={handleTypeFilterChange} className="w-full h-11">
                            <MenuItem value="">-- Tất cả loại --</MenuItem>
                            <MenuItem value="percent">Phần trăm (%)</MenuItem>
                            <MenuItem value="fixed">Số tiền cố định</MenuItem>
                        </Select>
                    </div>

                    <div className="flex flex-col">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Trạng thái số lượng</label>
                        <Select value={quantityStatus} onChange={handleQuantityStatusChange} className="w-full h-11">
                            <MenuItem value="">-- Tất cả trạng thái --</MenuItem>
                            <MenuItem value="remaining"> Còn lại</MenuItem>
                            <MenuItem value="out"> Đã hết</MenuItem>
                        </Select>
                    </div>

                    <div className="flex flex-col">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Trạng thái thời gian</label>
                        <Select value={timeStatus} onChange={handleTimeStatusChange} className="w-full h-11">
                            <MenuItem value="">-- Tất cả thời gian --</MenuItem>
                            <MenuItem value="upcoming"> Sắp diễn ra</MenuItem>
                            <MenuItem value="active"> Đang hoạt động</MenuItem>
                            <MenuItem value="expired"> Đã hết hạn</MenuItem>
                        </Select>
                    </div>

                    <div className="col">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Lọc theo khoảng</label>
                        <div className="flex flex-col gap-2">
                            <div className="flex gap-2 items-start">
                                <div className="flex-1">
                                    <TextField
                                        type="text"
                                        size="small"
                                        placeholder="Giảm từ"
                                        value={discountMin}
                                        onChange={handleDiscountMinChange}
                                        minRows={0}
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
                                        placeholder="Giảm đến"
                                        value={discountMax}
                                        onChange={handleDiscountMaxChange}
                                        minRows={0}
                                        FormHelperTextProps={{
                                            style: { fontSize: '10px', marginTop: '4px' }
                                        }}
                                    />
                                </div>
                            </div>
                        </div>
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

                {(searchTerm || typeFilter || discountMin || discountMax || quantityStatus || timeStatus) && (
                    <div className="mt-6 pt-4 border-t border-gray-200">
                        <p className="text-sm text-gray-600 mb-2">Bộ lọc hiện tại:</p>
                        <div className="flex flex-wrap gap-2">
                            {searchTerm && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                    Tìm kiếm: "{searchTerm}"
                                </span>
                            )}
                            {typeFilter && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                    Loại: {typeFilter === 'percent' ? 'Phần trăm' : 'Số tiền cố định'}
                                </span>
                            )}
                            {discountMin && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                    Giảm từ: {discountMin}
                                </span>
                            )}
                            {discountMax && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                    Giảm đến: {discountMax}
                                </span>
                            )}
                            {quantityStatus && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                    Số lượng: {quantityStatus === 'remaining' ? 'Còn lại' : 'Đã hết'}
                                </span>
                            )}
                            {timeStatus && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                                    Thời gian: {
                                        timeStatus === 'upcoming' ? 'Sắp diễn ra' :
                                            timeStatus === 'active' ? 'Đang hoạt động' : 'Đã hết hạn'
                                    }
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
                        <TableContainer sx={{ maxHeight: 440 }}>
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
                                    {offers.length === 0 ? (
                                        <TableRow>
                                            <TableCell colSpan={columns.length} align="center">
                                                <div className="py-8 text-gray-500">
                                                    Không tìm thấy mã khuyến mãi nào
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    ) : (
                                        offers.map((offer) => {
                                            return (
                                                <TableRow key={offer.id} hover>
                                                    <TableCell align="center">
                                                        <span className="font-medium">{offer.code}</span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <span className="font-medium">{offer.name}</span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <span className="font-medium">{offer.total_quantity}</span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <span className="font-medium">{offer.used_quantity}</span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <span className="font-medium">
                                                            {offer.type === 'percent' ? offer.discount + '%' : offer.discount}
                                                        </span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <span className="font-medium">
                                                            {offer.type === 'percent' ? 'Phần trăm' : 'Số tiền cố định'}
                                                        </span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <span className="font-medium">≥ {offer.condition}</span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <span className="font-medium">{formatDate(offer.start_time)}</span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <span className="font-medium">{formatDate(offer.end_time)}</span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <div className="flex items-center justify-center gap-4">
                                                            <Button
                                                                className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-[#e1e1e1] !min-w-[35px]"
                                                                onClick={() => {
                                                                    setOfferToEdit(offer);
                                                                    setEditDialogOpen(true);
                                                                }}
                                                                title="Chỉnh sửa"
                                                            >
                                                                <AiOutlineEdit className="text-[rgba(0,0,0,0.7)] text-[20px]" />
                                                            </Button>

                                                            <Button
                                                                className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-red-100 !min-w-[35px]"
                                                                onClick={() => openDeleteDialog(offer)}
                                                                title="Xóa"
                                                                disabled={deleting}
                                                            >
                                                                <GoTrash className="text-[rgba(0,0,0,0.7)] text-[20px] hover:text-red-600" />
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
                            rowsPerPageOptions={[10, 25, 100]}
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
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">
                    Xác nhận xóa mã khuyến mãi
                </DialogTitle>
                <DialogContent>
                    <DialogContentText id="alert-dialog-description">
                        Bạn có chắc chắn muốn xóa mã khuyến mãi "{offerToDelete?.name}"?
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={closeDeleteDialog} disabled={deleting}>
                        Hủy
                    </Button>
                    <Button
                        onClick={handleDeleteOffer}
                        autoFocus
                        color="error"
                        disabled={deleting}
                    >
                        {deleting ? 'Đang xóa...' : 'Xóa'}
                    </Button>
                </DialogActions>
            </Dialog>

            <EditSpecialOffer
                open={editDialogOpen}
                onClose={() => {
                    setEditDialogOpen(false);
                    setOfferToEdit(null);
                }}
                offer={offerToEdit}
                onSuccess={() => {
                    fetchOffers(page, rowsPerPage, searchTerm);
                }}
            />
        </>
    )
}

export default SpecialOffer