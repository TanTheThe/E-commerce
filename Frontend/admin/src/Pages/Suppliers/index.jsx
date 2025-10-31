import React, { useCallback, useContext, useEffect, useState } from "react";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import Checkbox from '@mui/material/Checkbox';
import SearchBox from "../../Components/SearchBox";
import { MyContext } from "../../App";
import { MdDelete, MdLocalPhone, MdOutlineMarkEmailRead } from "react-icons/md";
import { Button, IconButton, MenuItem, Select } from "@mui/material";
import debounce from 'lodash/debounce';
import { deleteDataApi, getDataApi, postDataApi, putDataApi } from "../../utils/api";
import { AiOutlineEdit, AiOutlineEye } from "react-icons/ai";
import { GoTrash } from "react-icons/go";
import AddSupplierModal from "./addSupplier";
import EditSupplierModal from "./editSupplier";
import SupplierDetailOffcanvas from "./supplierDetail";


const label = { inputProps: { 'aria-label': 'Checkbox demo' } };

const columns = [
    { id: 'code', label: 'MÃ NCC', minWidth: 100 },
    { id: 'name', label: 'TÊN NCC', minWidth: 180 },
    { id: 'contact_person', label: 'NGƯỜI LIÊN HỆ', minWidth: 140 },
    { id: 'phone', label: 'SĐT', minWidth: 120 },
    { id: 'email', label: 'EMAIL', minWidth: 180 },
    { id: 'product_count', label: 'SL SẢN PHẨM', minWidth: 100 },
    { id: 'is_active', label: 'TRẠNG THÁI', minWidth: 120 },
    { id: 'created_at', label: 'NGÀY TẠO', minWidth: 150 },
    { id: 'actions', label: 'THAO TÁC', minWidth: 150 },
];

const Suppliers = () => {
    const [searchVal, setSearchVal] = useState('');
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [page, setPage] = useState(0);
    const [suppliers, setSuppliers] = useState([]);
    const [totalSuppliers, setTotalSuppliers] = useState(0);
    const [loading, setLoading] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [supplierToEdit, setSupplierToEdit] = useState(null);
    const [deleting, setDeleting] = useState(false);
    const [showAddModal, setShowAddModal] = useState(false);
    const [isActiveFilter, setIsActiveFilter] = useState(null);
    const [detailDialogOpen, setDetailDialogOpen] = useState(false);
    const [supplierToView, setSupplierToView] = useState(null);

    const context = useContext(MyContext);

    const fetchSuppliers = async () => {
        setLoading(true);
        try {
            const skip = page * rowsPerPage;
            const limit = rowsPerPage;

            const queryParams = new URLSearchParams({
                skip: skip.toString(),
                limit: limit.toString(),
            });

            if (searchVal) queryParams.append('search', searchVal);
            if (isActiveFilter !== null) queryParams.append('is_active', isActiveFilter.toString());

            const response = await getDataApi(`/admin/suppliers?${queryParams.toString()}`);

            if (response.success === true) {
                setSuppliers(response.data.data || []);
                setTotalSuppliers(response.data.total || 0);
            } else {
                context.openAlertBox("error", response.data.detail.message);
            }
        } catch (error) {
            console.error('Error fetching suppliers:', error);
            context.openAlertBox("error", "Lỗi khi tải danh sách nhà cung cấp");
        } finally {
            setLoading(false);
        }
    };

    const handleDeactivateSupplier = async (supplierId) => {
        if (!window.confirm("Bạn có chắc muốn VÔ HIỆU HÓA nhà cung cấp này? (Điều này sẽ đặt trạng thái thành Không hoạt động)")) return;

        setDeleting(true);
        try {
            const response = await deleteDataApi(`/admin/suppliers/${supplierId}`);

            if (response.success) {
                context.openAlertBox('success', response.message);
                fetchSuppliers();
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || 'Vô hiệu hóa nhà cung cấp thất bại');
            }
        } catch (error) {
            context.openAlertBox('error', 'Lỗi hệ thống khi vô hiệu hóa nhà cung cấp');
        } finally {
            setDeleting(false);
        }
    };

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(+event.target.value);
        setPage(0);
    };

    const openDeactivateDialog = (supplier) => {
        handleDeactivateSupplier(supplier.id);
    };

    const openDetailDialog = (supplier) => {
        setSupplierToView(supplier);
        setDetailDialogOpen(true);
    };

    const closeDetailDialog = () => {
        setDetailDialogOpen(false);
        setSupplierToView(null);
    };

    const debouncedSearch = useCallback(
        debounce((searchTerm) => {
            setSearchVal(searchTerm);
        }, 500),
        []
    );

    useEffect(() => {
        fetchSuppliers();
    }, [page, rowsPerPage, searchVal, isActiveFilter]);

    useEffect(() => {
        setPage(0);
    }, [searchVal, isActiveFilter]);

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleDateString('vi-VN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            });
        } catch {
            return 'N/A';
        }
    };

    return (
        <>
            <div className="flex items-center justify-between px-2 py-0 mt-3">
                <h2 className="text-[18px] font-[600]">Danh sách Nhà Cung Cấp</h2>

                <div className="col w-[18%] ml-auto flex items-center justify-end gap-3">
                    <Button className="btn-blue !text-white btn-sm"
                        onClick={() => setShowAddModal(true)}>
                        Tạo Nhà Cung Cấp
                    </Button>

                    <AddSupplierModal
                        open={showAddModal}
                        onClose={() => setShowAddModal(false)}
                        onSupplierAdded={fetchSuppliers}
                        context={context}
                    />
                </div>
            </div>

            <div className="card my-4 pt-5 shadow-md sm:rounded-lg bg-white">
                <div className="flex items-center w-full px-5 mb-6 justify-between">
                    <div className="flex items-center gap-4 w-[60%]">
                        <h4 className="font-[600] text-[14px]">Tìm kiếm Nhà Cung Cấp</h4>

                        <select
                            className="px-3 py-1 border border-gray-300 rounded-md text-sm"
                            value={isActiveFilter === null ? '' : isActiveFilter.toString()}
                            onChange={(e) => {
                                const value = e.target.value;
                                setIsActiveFilter(value === '' ? null : value === 'true');
                            }}
                        >
                            <option value="">Tất cả trạng thái</option>
                            <option value="true">Đang hoạt động</option>
                            <option value="false">Không hoạt động</option>
                        </select>

                    </div>

                    <div className="col w-[30%] ml-auto">
                        <SearchBox onSearch={debouncedSearch} />
                    </div>
                </div>

                {loading ? (
                    <div className="flex justify-center items-center h-64">
                        <div className="text-lg">Đang tải...</div>
                    </div>
                ) : (
                    <>
                        <TableContainer sx={{ maxHeight: 440 }}>
                            <Table stickyHeader aria-label="suppliers table">
                                <TableHead className="bg-[#f1f1f1]">
                                    <TableRow>
                                        {columns.map((column) => (
                                            <TableCell
                                                key={column.id}
                                                style={{ minWidth: column.minWidth }}
                                            >
                                                {column.label}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                </TableHead>

                                <TableBody>
                                    {suppliers.map((supplier) => {
                                        return (
                                            <TableRow key={supplier.id}>
                                                <TableCell>
                                                    <span className="font-[Montserrat] text-gray-700 font-medium">
                                                        {supplier.code}
                                                    </span>
                                                </TableCell>
                                                <TableCell>
                                                    <span className="font-[Montserrat] text-gray-700 font-medium">
                                                        {supplier.name}
                                                    </span>
                                                </TableCell>
                                                <TableCell>
                                                    <span className="font-[Montserrat] text-gray-500 text-sm">
                                                        {supplier.contact_person}
                                                    </span>
                                                </TableCell>
                                                <TableCell>
                                                    <span className="font-[Montserrat] text-gray-500 text-sm">
                                                        {supplier.phone}
                                                    </span>
                                                </TableCell>
                                                <TableCell>
                                                    <span className="font-[Montserrat] text-gray-500 text-sm">
                                                        {supplier.email}
                                                    </span>
                                                </TableCell>
                                                <TableCell>
                                                    <span className="font-[Montserrat] text-gray-500 text-sm">
                                                        {supplier.product_count || 0}
                                                    </span>
                                                </TableCell>
                                                <TableCell>
                                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${supplier.is_active
                                                        ? 'bg-green-100 text-green-800'
                                                        : 'bg-red-100 text-red-800'
                                                        }`}>
                                                        {supplier.is_active ? 'Hoạt động' : 'Không hoạt động'}
                                                    </span>
                                                </TableCell>
                                                <TableCell>
                                                    <span className="font-[Montserrat] text-gray-600 text-sm">
                                                        {formatDate(supplier.created_at)}
                                                    </span>
                                                </TableCell>

                                                <TableCell>
                                                    <div className="flex items-center gap-2">
                                                        <Button
                                                            className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-blue-100 !min-w-[35px]"
                                                            onClick={() => openDetailDialog(supplier)}
                                                            title="Xem chi tiết"
                                                        >
                                                            <AiOutlineEye className="text-[rgba(0,0,0,0.7)] text-[20px] hover:text-blue-600" />
                                                        </Button>

                                                        <Button
                                                            className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-[#e1e1e1] !min-w-[35px]"
                                                            onClick={() => {
                                                                setSupplierToEdit(supplier);
                                                                setEditDialogOpen(true);
                                                            }}
                                                            title="Chỉnh sửa"
                                                        >
                                                            <AiOutlineEdit className="text-[rgba(0,0,0,0.7)] text-[20px]" />
                                                        </Button>

                                                        <Button
                                                            className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-red-100 !min-w-[35px]"
                                                            onClick={() => openDeactivateDialog(supplier)}
                                                            title="Vô hiệu hóa"
                                                            disabled={deleting || !supplier.is_active}
                                                        >
                                                            <GoTrash className="text-[rgba(0,0,0,0.7)] text-[20px] hover:text-red-600" />
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
                            count={totalSuppliers}
                            rowsPerPage={rowsPerPage}
                            page={page}
                            onPageChange={handleChangePage}
                            onRowsPerPageChange={handleChangeRowsPerPage}
                        />
                    </>
                )}
            </div>

            <EditSupplierModal
                open={editDialogOpen}
                onClose={() => {
                    setEditDialogOpen(false);
                    setSupplierToEdit(null);
                }}
                onSupplierUpdated={fetchSuppliers}
                context={context}
                supplierToEdit={supplierToEdit}
            />

            <SupplierDetailOffcanvas
                open={detailDialogOpen}
                onClose={closeDetailDialog}
                supplier={supplierToView}
                context={context}
            />
        </>
    );
};

export default Suppliers