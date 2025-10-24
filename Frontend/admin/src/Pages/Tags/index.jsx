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
import AddTagModal from "./addTag";
import EditTagModal from "./editTag";


const label = { inputProps: { 'aria-label': 'Checkbox demo' } };

const columns = [
    { id: 'tagName', label: 'TÊN TAG', minWidth: 180 },
    { id: 'slug', label: 'SLUG', minWidth: 140 },
    { id: 'productCount', label: 'SỐ LƯỢNG SẢN PHẨM', minWidth: 120 },
    { id: 'status', label: 'TRẠNG THÁI', minWidth: 120 },
    { id: 'createdAt', label: 'NGÀY TẠO', minWidth: 150 },
    { id: 'actions', label: 'THAO TÁC', minWidth: 150 },
];

const Tags = () => {
    const [searchVal, setSearchVal] = useState('');
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [page, setPage] = useState(0);
    const [tags, setTags] = useState([]);
    const [totalTags, setTotalTags] = useState(0);
    const [selectedTagIds, setSelectedTagIds] = useState([]);
    const [loading, setLoading] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [tagToEdit, setTagToEdit] = useState(null);
    const [deleting, setDeleting] = useState(false);
    const [showAddModal, setShowAddModal] = useState(false);
    const [isActiveFilter, setIsActiveFilter] = useState(null);
    const [sortBy, setSortBy] = useState('created_desc');

    const context = useContext(MyContext);

    const fetchTags = async () => {
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

            const response = await getDataApi(`/admin/tag/all?${queryParams.toString()}`);

            if (response.success === true) {
                setTags(response.data.data || []);
                setTotalTags(response.data.total || 0);
            } else {
                context.openAlertBox("error", response.data.detail.message);
            }
        } catch (error) {
            console.error('Error fetching tags:', error);
            context.openAlertBox("error", "Lỗi khi tải danh sách tag");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTags();
    }, [page, rowsPerPage, searchVal, isActiveFilter, sortBy]);

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(+event.target.value);
        setPage(0);
    };

    const handleDeleteTag = async (tagId) => {
        if (!window.confirm("Bạn có chắc muốn xóa tag này?")) return;

        setDeleting(true);
        try {
            const response = await deleteDataApi(`/admin/tag/${tagId}`);
            if (response.success) {
                context.openAlertBox('success', response.message);
                fetchTags();
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || 'Xóa tag thất bại');
            }
        } catch (error) {
            context.openAlertBox('error', 'Lỗi hệ thống khi xóa tag');
        } finally {
            setDeleting(false);
        }
    };

    const handleDeleteMultipleTags = async () => {
        if (selectedTagIds.length === 0) return;

        if (!window.confirm(`Bạn có chắc muốn xóa ${selectedTagIds.length} tag đã chọn?`)) return;

        setDeleting(true);
        try {
            const response = await postDataApi('/admin/tag/delete', {
                tag_ids: selectedTagIds
            });

            if (response.success) {
                context.openAlertBox('success', response.message);
                setSelectedTagIds([]);
                fetchTags();
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || 'Xóa tag thất bại');
            }
        } catch (error) {
            context.openAlertBox('error', 'Lỗi hệ thống khi xóa tag');
        } finally {
            setDeleting(false);
        }
    };

    const openDeleteDialog = (tag) => {
        handleDeleteTag(tag.id);
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
                <h2 className="text-[18px] font-[600]">Danh sách tag</h2>

                <div className="col w-[18%] ml-auto flex items-center justify-end gap-3">
                    <Button className="btn-blue !text-white btn-sm"
                        onClick={() => setShowAddModal(true)}>
                        Thêm tag
                    </Button>

                    <AddTagModal
                        open={showAddModal}
                        onClose={() => setShowAddModal(false)}
                        onTagAdded={fetchTags}
                        context={context}
                    />
                </div>
            </div>

            <div className="card my-4 pt-5 shadow-md sm:rounded-lg bg-white">
                <div className="flex items-center w-full px-5 mb-6 justify-between">
                    <div className="flex items-center gap-4 w-[60%]">
                        <h4 className="font-[600] text-[14px]">Tìm kiếm tag</h4>

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
                            <Table stickyHeader aria-label="tags table">
                                <TableHead className="bg-[#f1f1f1]">
                                    <TableRow>
                                        <TableCell>
                                            <Checkbox {...label} size="small"
                                                checked={selectedTagIds.length === tags.length && tags.length > 0}
                                                indeterminate={selectedTagIds.length > 0 && selectedTagIds.length < tags.length}
                                                onChange={(e) => {
                                                    if (e.target.checked) {
                                                        const allIds = tags.map(tag => tag.id);
                                                        setSelectedTagIds(allIds);
                                                    } else {
                                                        setSelectedTagIds([]);
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
                                    {tags.map((tag) => {
                                        return (
                                            <TableRow key={tag.id}>
                                                <TableCell>
                                                    <Checkbox {...label} size="small"
                                                        checked={selectedTagIds.includes(tag.id)}
                                                        onChange={(e) => {
                                                            if (e.target.checked) {
                                                                setSelectedTagIds(prev => [...prev, tag.id]);
                                                            } else {
                                                                setSelectedTagIds(prev => prev.filter(id => id !== tag.id));
                                                            }
                                                        }}
                                                    />
                                                </TableCell>

                                                <TableCell>
                                                    <div className="flex flex-col">
                                                        <span className="font-[Montserrat] text-gray-700 font-medium">
                                                            {tag.name}
                                                        </span>
                                                    </div>
                                                </TableCell>

                                                <TableCell>
                                                    <span className="font-[Montserrat] text-gray-500 text-sm">
                                                        {tag.slug}
                                                    </span>
                                                </TableCell>

                                                <TableCell>
                                                    <span className="font-[Montserrat] text-gray-600 text-sm bg-blue-100 px-2 py-1 rounded">
                                                        {tag.product_count || 0}
                                                    </span>
                                                </TableCell>

                                                <TableCell>
                                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${tag.is_active
                                                        ? 'bg-green-100 text-green-800'
                                                        : 'bg-red-100 text-red-800'
                                                        }`}>
                                                        {tag.is_active ? 'Hoạt động' : 'Không hoạt động'}
                                                    </span>
                                                </TableCell>

                                                <TableCell>
                                                    <span className="font-[Montserrat] text-gray-600 text-sm">
                                                        {formatDate(tag.created_at)}
                                                    </span>
                                                </TableCell>

                                                <TableCell>
                                                    <div className="flex items-center gap-2">
                                                        <Button
                                                            className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-[#e1e1e1] !min-w-[35px]"
                                                            onClick={() => {
                                                                setTagToEdit(tag);
                                                                setEditDialogOpen(true);
                                                            }}
                                                            title="Chỉnh sửa"
                                                        >
                                                            <AiOutlineEdit className="text-[rgba(0,0,0,0.7)] text-[20px]" />
                                                        </Button>

                                                        <Button
                                                            className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-red-100 !min-w-[35px]"
                                                            onClick={() => openDeleteDialog(tag)}
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
                            count={totalTags}
                            rowsPerPage={rowsPerPage}
                            page={page}
                            onPageChange={handleChangePage}
                            onRowsPerPageChange={handleChangeRowsPerPage}
                        />
                    </>
                )}
            </div>

            {selectedTagIds.length > 0 && (
                <div className="px-2 mt-2">
                    <Button
                        className="!bg-red-700 hover:!bg-red-600 btn-sm !text-white"
                        onClick={handleDeleteMultipleTags}
                        disabled={deleting}
                    >
                        Xóa {selectedTagIds.length} tag
                    </Button>
                </div>
            )}

            <EditTagModal
                open={editDialogOpen}
                onClose={() => {
                    setEditDialogOpen(false);
                    setTagToEdit(null);
                }}
                onTagUpdated={fetchTags}
                context={context}
                tagToEdit={tagToEdit}
            />
        </>
    );
};

export default Tags