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
import { AiOutlineEdit } from "react-icons/ai";
import { GoTrash } from "react-icons/go";
import EditBrandModal from "./editBrand";
import AddBrandModal from "./addBrand";


const label = { inputProps: { 'aria-label': 'Checkbox demo' } };

const columns = [
    { id: 'brandName', label: 'BRAND NAME', minWidth: 180 },
    { id: 'logo', label: 'LOGO', minWidth: 120 },
    { id: 'productCount', label: 'PRODUCTS COUNT', minWidth: 100 },
    { id: 'status', label: 'STATUS', minWidth: 120 },
    { id: 'createdAt', label: 'CREATED AT', minWidth: 150 },
    { id: 'actions', label: 'ACTIONS', minWidth: 150 },
];

const Brands = () => {
    const [searchVal, setSearchVal] = useState('');
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [page, setPage] = useState(0);
    const [brands, setBrands] = useState([]);
    const [totalBrands, setTotalBrands] = useState(0);
    const [selectedBrandIds, setSelectedBrandIds] = useState([]);
    const [loading, setLoading] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [brandToEdit, setBrandToEdit] = useState(null);
    const [deleting, setDeleting] = useState(false);
    const [showAddModal, setShowAddModal] = useState(false);
    const [isActiveFilter, setIsActiveFilter] = useState(null);
    const [sortBy, setSortBy] = useState('created_desc');

    const context = useContext(MyContext);

    const fetchBrands = async () => {
        setLoading(true);
        try {
            const skip = page * rowsPerPage;
            const limit = rowsPerPage;

            const queryParams = new URLSearchParams({
                skip: skip.toString(),
                limit: limit.toString(),
                sort_by: sortBy
            });

            if (searchVal) queryParams.append('search', searchVal);
            if (isActiveFilter !== null) queryParams.append('is_active', isActiveFilter.toString());

            const response = await getDataApi(`/admin/brand/all?${queryParams.toString()}`);

            if (response.success === true) {
                setBrands(response.data.data || []);
                setTotalBrands(response.data.total || 0);
            } else {
                context.openAlertBox("error", response.data.detail.message);
            }
        } catch (error) {
            console.error('Error fetching colors:', error);
            context.openAlertBox("error", "Lỗi khi tải danh sách màu sắc");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchBrands();
    }, [page, rowsPerPage, searchVal, isActiveFilter, sortBy]);

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(+event.target.value);
        setPage(0);
    };

    const handleDeleteBrand = async (brandId) => {
        if (!window.confirm("Bạn có chắc muốn xóa thương hiệu này?")) return;

        setDeleting(true);
        try {
            const response = await deleteDataApi(`/admin/brand/${brandId}`);
            if (response.success) {
                context.openAlertBox('success', response.message);
                fetchBrands();
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || 'Xóa màu sắc thất bại');
            }
        } catch (error) {
            context.openAlertBox('error', 'Lỗi hệ thống khi xóa màu sắc');
        } finally {
            setDeleting(false);
        }
    };

    const handleDeleteMultipleBrands = async () => {
        if (selectedBrandIds.length === 0) return;

        if (!window.confirm(`Bạn có chắc muốn xóa ${selectedBrandIds.length} thương hiệu đã chọn?`)) return;

        setDeleting(true);
        try {
            const response = await postDataApi('/admin/brand/delete', {
                brand_ids: selectedBrandIds
            });

            if (response.success) {
                context.openAlertBox('success', response.message);
                setSelectedBrandIds([]);
                fetchBrands();
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || 'Xóa thương hiệu thất bại');
            }
        } catch (error) {
            context.openAlertBox('error', 'Lỗi hệ thống khi xóa thương hiệu');
        } finally {
            setDeleting(false);
        }
    };

    const handleBrandUpdated = (updatedBrand) => {
        setBrands(prevBrands =>
            prevBrands.map(brand =>
                brand.id === updatedBrand.id
                    ? { ...brand, ...updatedBrand }
                    : brand
            )
        );
    };

    const openDeleteDialog = (brand) => {
        handleDeleteBrand(brand.id);
    };

    const debouncedSearch = useCallback(
        debounce((searchTerm) => {
            setSearchVal(searchTerm);
        }, 500),
        []
    );

    useEffect(() => {
        setPage(0);
    }, [searchVal, isActiveFilter, sortBy]);

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
                <h2 className="text-[18px] font-[600]">Danh sách thương hiệu</h2>

                <div className="col w-[18%] ml-auto flex items-center justify-end gap-3">
                    <Button className="btn-blue !text-white btn-sm"
                        onClick={() => setShowAddModal(true)}>
                        Thêm thương hiệu
                    </Button>

                    <AddBrandModal
                        open={showAddModal}
                        onClose={() => setShowAddModal(false)}
                        onBrandAdded={fetchBrands}
                        context={context}
                    />
                </div>
            </div>

            <div className="card my-4 pt-5 shadow-md sm:rounded-lg bg-white">
                <div className="flex items-center w-full px-5 mb-6 justify-between">
                    <div className="flex items-center gap-4 w-[60%]">
                        <h4 className="font-[600] text-[14px]">Tìm kiếm thương hiệu</h4>

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

                        <select
                            className="px-3 py-1 border border-gray-300 rounded-md text-sm"
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value)}
                        >
                            <option value="created_desc">Mới nhất</option>
                            <option value="created_asc">Cũ nhất</option>
                            <option value="name_asc">Tên A-Z</option>
                            <option value="name_desc">Tên Z-A</option>
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
                            <Table stickyHeader aria-label="brands table">
                                <TableHead className="bg-[#f1f1f1]">
                                    <TableRow>
                                        <TableCell>
                                            <Checkbox {...label} size="small"
                                                checked={selectedBrandIds.length === brands.length && brands.length > 0}
                                                indeterminate={selectedBrandIds.length > 0 && selectedBrandIds.length < brands.length}
                                                onChange={(e) => {
                                                    if (e.target.checked) {
                                                        const allIds = brands.map(brand => brand.id);
                                                        setSelectedBrandIds(allIds);
                                                    } else {
                                                        setSelectedBrandIds([]);
                                                    }
                                                }}
                                            />
                                        </TableCell>
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
                                    {brands.map((brand) => {
                                        return (
                                            <TableRow key={brand.id}>
                                                <TableCell>
                                                    <Checkbox {...label} size="small"
                                                        checked={selectedBrandIds.includes(brand.id)}
                                                        onChange={(e) => {
                                                            if (e.target.checked) {
                                                                setSelectedBrandIds(prev => [...prev, brand.id]);
                                                            } else {
                                                                setSelectedBrandIds(prev => prev.filter(id => id !== brand.id));
                                                            }
                                                        }}
                                                    />
                                                </TableCell>

                                                <TableCell>
                                                    <div className="flex flex-col">
                                                        <span className="font-[Montserrat] text-gray-700 font-medium">
                                                            {brand.name}
                                                        </span>
                                                        <span className="text-xs text-gray-500">
                                                            {brand.slug}
                                                        </span>
                                                    </div>
                                                </TableCell>

                                                <TableCell>
                                                    <div>
                                                        {brand.logo ? (
                                                            <img
                                                                src={brand.logo}
                                                                alt={brand.name}
                                                                className="w-12 h-12 object-contain rounded border border-gray-200"
                                                                onError={(e) => {
                                                                    e.target.style.display = 'none';
                                                                    e.target.nextSibling.style.display = 'flex';
                                                                }}
                                                            />
                                                        ) : null}
                                                        <div className="w-12 h-12 bg-gray-100 rounded border border-gray-200 flex items-center justify-center text-gray-400 text-xs"
                                                            style={{ display: brand.logo ? 'none' : 'flex' }}>
                                                            No Logo
                                                        </div>
                                                    </div>
                                                </TableCell>

                                                <TableCell>
                                                    <span className="font-[Montserrat] text-gray-600 text-sm bg-blue-100 px-2 py-1 rounded">
                                                        {brand.product_count || 0}
                                                    </span>
                                                </TableCell>

                                                <TableCell>
                                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${brand.is_active
                                                        ? 'bg-green-100 text-green-800'
                                                        : 'bg-red-100 text-red-800'
                                                        }`}>
                                                        {brand.is_active ? 'Hoạt động' : 'Không hoạt động'}
                                                    </span>
                                                </TableCell>

                                                <TableCell>
                                                    <span className="font-[Montserrat] text-gray-600 text-sm">
                                                        {formatDate(brand.created_at)}
                                                    </span>
                                                </TableCell>

                                                <TableCell>
                                                    <div className="flex items-center gap-2">
                                                        <Button
                                                            className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-[#e1e1e1] !min-w-[35px]"
                                                            onClick={() => {
                                                                setBrandToEdit(brand);
                                                                setEditDialogOpen(true);
                                                            }}
                                                            title="Chỉnh sửa"
                                                        >
                                                            <AiOutlineEdit className="text-[rgba(0,0,0,0.7)] text-[20px]" />
                                                        </Button>

                                                        <Button
                                                            className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-red-100 !min-w-[35px]"
                                                            onClick={() => openDeleteDialog(brand)}
                                                            title="Xóa"
                                                            disabled={deleting}
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
                            count={totalBrands}
                            rowsPerPage={rowsPerPage}
                            page={page}
                            onPageChange={handleChangePage}
                            onRowsPerPageChange={handleChangeRowsPerPage}
                        />
                    </>
                )}
            </div>

            {selectedBrandIds.length > 0 && (
                <div className="px-2 mt-2">
                    <Button
                        className="!bg-red-700 hover:!bg-red-600 btn-sm !text-white"
                        onClick={handleDeleteMultipleBrands}
                        disabled={deleting}
                    >
                        Xóa {selectedBrandIds.length} thương hiệu
                    </Button>
                </div>
            )}

            <EditBrandModal
                open={editDialogOpen}
                onClose={() => {
                    setEditDialogOpen(false);
                    setBrandToEdit(null);
                }}
                onBrandUpdated={handleBrandUpdated}
                context={context}
                brandToEdit={brandToEdit}
            />
        </>
    );
}

export default Brands