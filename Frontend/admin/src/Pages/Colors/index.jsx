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
import AddColorModal from "./addColor";
import { AiOutlineEdit } from "react-icons/ai";
import { GoTrash } from "react-icons/go";
import EditColorModal from "./editColor";


const label = { inputProps: { 'aria-label': 'Checkbox demo' } };

const columns = [
    { id: 'colorName', label: 'COLOR NAME', minWidth: 180 },
    { id: 'colorCode', label: 'COLOR CODE', minWidth: 140 },
    { id: 'colorDisplay', label: 'COLOR PREVIEW', minWidth: 120 },
    { id: 'actions', label: 'ACTIONS', minWidth: 150 },
];

const Colors = () => {
    const [searchVal, setSearchVal] = useState('');
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [page, setPage] = useState(0);
    const [colors, setColors] = useState([]);
    const [totalColors, setTotalColors] = useState(0);
    const [selectedColorIds, setSelectedColorIds] = useState([]);
    const [loading, setLoading] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [colorToEdit, setColorToEdit] = useState(null);
    const [deleting, setDeleting] = useState(false);
    const [showAddModal, setShowAddModal] = useState(false);

    const context = useContext(MyContext);

    const fetchColors = async () => {
        setLoading(true);
        try {
            const skip = page * rowsPerPage;
            const limit = rowsPerPage;

            const queryParams = new URLSearchParams({
                skip: skip.toString(),
                limit: limit.toString(),
            });

            if (searchVal) queryParams.append('search', searchVal);

            const response = await getDataApi(`/admin/color?${queryParams.toString()}`);
            console.log(response);

            if (response.success === true) {
                setColors(response.data.data || []);
                setTotalColors(response.data.total || 0);
            } else {
                context.openAlertBox("error", response.message);
            }
        } catch (error) {
            console.error('Error fetching colors:', error);
            context.openAlertBox("error", "Lỗi khi tải danh sách màu sắc");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchColors();
    }, [page, rowsPerPage, searchVal]);

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(+event.target.value);
        setPage(0);
    };

    const handleDeleteColor = async (colorId) => {
        if (!window.confirm("Bạn có chắc muốn xóa màu sắc này?")) return;

        setDeleting(true);
        try {
            const response = await deleteDataApi(`/admin/color/${colorId}`);
            if (response.success) {
                context.openAlertBox('success', response.message);
                fetchColors();
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || 'Xóa màu sắc thất bại');
            }
        } catch (error) {
            context.openAlertBox('error', 'Lỗi hệ thống khi xóa màu sắc');
        } finally {
            setDeleting(false);
        }
    };

    const openDeleteDialog = (color) => {
        handleDeleteColor(color.id);
    };

    const debouncedSearch = useCallback(
        debounce((searchTerm) => {
            setSearchVal(searchTerm);
        }, 500),
        []
    );

    useEffect(() => {
        setPage(0);
    }, [searchVal]);

    const isValidHexColor = (hex) => {
        return /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(hex);
    };

    return (
        <>
            <div className="flex items-center justify-between px-2 py-0 mt-3">
                <h2 className="text-[18px] font-[600]">Danh sách màu sắc</h2>

                <div className="col w-[18%] ml-auto flex items-center justify-end gap-3">
                    <Button className="btn-blue !text-white btn-sm"
                        onClick={() => setShowAddModal(true)}>
                        Thêm màu mới
                    </Button>

                    <AddColorModal
                        open={showAddModal}
                        onClose={() => setShowAddModal(false)}
                        onColorAdded={fetchColors}
                        context={context}
                    />
                </div>
            </div>

            <div className="card my-4 pt-5 shadow-md sm:rounded-lg bg-white">
                <div className="flex items-center w-full px-5 mb-6 justify-between">
                    <div className="flex items-center gap-4 w-[60%]">
                        <h4 className="font-[600] text-[14px]">Tìm kiếm màu sắc</h4>
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
                            <Table stickyHeader aria-label="colors table">
                                <TableHead className="bg-[#f1f1f1]">
                                    <TableRow>
                                        <TableCell>
                                            <Checkbox {...label} size="small"
                                                checked={selectedColorIds.length === colors.length && colors.length > 0}
                                                indeterminate={selectedColorIds.length > 0 && selectedColorIds.length < colors.length}
                                                onChange={(e) => {
                                                    if (e.target.checked) {
                                                        const allIds = colors.map(color => color.id);
                                                        setSelectedColorIds(allIds);
                                                    } else {
                                                        setSelectedColorIds([]);
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
                                    {colors.map((color) => {
                                        return (
                                            <TableRow key={color.id}>
                                                <TableCell>
                                                    <Checkbox {...label} size="small"
                                                        checked={selectedColorIds.includes(color.id)}
                                                        onChange={(e) => {
                                                            if (e.target.checked) {
                                                                setSelectedColorIds(prev => [...prev, color.id]);
                                                            } else {
                                                                setSelectedColorIds(prev => prev.filter(id => id !== color.id));
                                                            }
                                                        }}
                                                    />
                                                </TableCell>

                                                <TableCell>
                                                    <span className="font-[Montserrat] text-gray-700 font-medium">
                                                        {color.name}
                                                    </span>
                                                </TableCell>

                                                <TableCell>
                                                    <span className="font-[Montserrat] text-gray-600 text-sm bg-gray-100 px-2 py-1 rounded">
                                                        {color.code}
                                                    </span>
                                                </TableCell>

                                                <TableCell>
                                                    <div className="flex items-center gap-3">
                                                        <div
                                                            className="w-8 h-8 rounded-full border border-gray-300 shadow-sm"
                                                            style={{
                                                                backgroundColor: isValidHexColor(color.code) ? color.code : '#cccccc'
                                                            }}
                                                            title={`Màu: ${color.code}`}
                                                        ></div>
                                                        {!isValidHexColor(color.code) && (
                                                            <span className="text-xs text-red-500">Mã màu không hợp lệ</span>
                                                        )}
                                                    </div>
                                                </TableCell>

                                                <TableCell>
                                                    <div className="flex items-center gap-2">
                                                        <Button
                                                            className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-[#e1e1e1] !min-w-[35px]"
                                                            onClick={() => {
                                                                setColorToEdit(color);
                                                                setEditDialogOpen(true);
                                                            }}
                                                            title="Chỉnh sửa"
                                                        >
                                                            <AiOutlineEdit className="text-[rgba(0,0,0,0.7)] text-[20px]" />
                                                        </Button>

                                                        <Button
                                                            className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-red-100 !min-w-[35px]"
                                                            onClick={() => openDeleteDialog(color)}
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
                            count={totalColors}
                            rowsPerPage={rowsPerPage}
                            page={page}
                            onPageChange={handleChangePage}
                            onRowsPerPageChange={handleChangeRowsPerPage}
                        />
                    </>
                )}
            </div>

            {selectedColorIds.length > 0 && (
                <div className="px-2 mt-2">
                    <Button
                        className="!bg-red-700 hover:!bg-red-600 btn-sm !text-white"
                        onClick={handleDeleteMultipleColors}
                        disabled={deleting}
                    >
                        Xóa {selectedColorIds.length} màu sắc
                    </Button>
                </div>
            )}

            <EditColorModal
                open={editDialogOpen}
                onClose={() => {
                    setEditDialogOpen(false);
                    setColorToEdit(null);
                }}
                onColorUpdated={fetchColors}
                context={context}
                colorToEdit={colorToEdit}
            />
        </>
    );
}

export default Colors