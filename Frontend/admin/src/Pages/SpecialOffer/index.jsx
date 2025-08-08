import React, { useCallback, useContext, useEffect, useState } from "react";
import { Button, DialogActions, DialogContent, DialogContentText, DialogTitle } from "@mui/material";
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
    const [offerFilterVal, setOfferFilterVal] = useState('');
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [page, setPage] = useState(0);
    const [offers, setOffers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isOpen, setIsOpen] = useState(false);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [offerToDelete, setOfferToDelete] = useState(null);
    const [deleting, setDeleting] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [offerToEdit, setOfferToEdit] = useState(null);
    const [searchInput, setSearchInput] = useState('');
    const [searchTerm, setSearchTerm] = useState('');

    const context = useContext(MyContext);

    const fetchOffers = async (search = '') => {
        try {
            setLoading(true);
            const response = await getDataApi(`/admin/special-offer?skip=0&limit=10&search=${encodeURIComponent(search)}`);
            console.log(response);

            if (response.success) {
                setOffers(response.data || []);
            } else {
                context.openAlertBox("error", "Có lỗi trong quá trình tải danh sách voucher");
                setOffers([]);
            }
        } catch (error) {
            context.openAlertBox("error", "Lỗi hệ thống khi tải voucher");
            setOffers([]);
        } finally {
            setLoading(false);
        }
    };

    const handleChangeOfferFilter = (event) => {
        setOfferFilterVal(event.target.value)
    };

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(+event.target.value);
        setPage(0);
    };

    const filteredOffers = offers.filter(offer =>
        offer.name.toLowerCase().includes(offerFilterVal.toLowerCase())
    );

    const paginatedOffers = filteredOffers.slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage
    );

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

                setOffers(prev => prev.filter(off => off.id !== offerToDelete.id));

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
            fetchOffers(value);
        }, 500),
        []
    );

    useEffect(() => {
        debouncedSearch(searchInput);
    }, [searchInput]);


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
                            fetchOffers();
                        }}
                    />
                </div>
            </div>

            <div className="w-[40%] py-3"><SearchBox searchTerm={searchInput} setSearchTerm={setSearchInput} /></div>

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
                                    {paginatedOffers.length === 0 ? (
                                        <TableRow>
                                            <TableCell colSpan={3} align="center">
                                                <div className="py-8 text-gray-500">
                                                    {offers.length === 0 ? 'Chưa có mã khuyến mãi nào' : 'Không tìm thấy mã khuyến mãi phù hợp'}
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    ) : (
                                        paginatedOffers.map((offer) => {
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
                                                        <span className="font-medium">{offer.type === 'percent' ? offer.discount + '%' : offer.discount}</span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <span className="font-medium">{offer.type}</span>
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
                            count={filteredOffers.length}
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
                    fetchOffers();
                }}
            />
        </>
    )
}

export default SpecialOffer