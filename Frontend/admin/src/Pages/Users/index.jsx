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


const label = { inputProps: { 'aria-label': 'Checkbox demo' } };

const columns = [
    { id: 'userName', label: 'USER NAME', minWidth: 120 },
    { id: 'userEmail', label: 'USER EMAIL', minWidth: 180 },
    { id: 'userPhone', label: 'USER PHONE', minWidth: 140 },
    { id: 'status', label: 'STATUS', minWidth: 120 },
    { id: 'createdAt', label: 'CREATED AT', minWidth: 160 },
    { id: 'actions', label: 'ACTIONS', minWidth: 100 },
];

const Users = () => {
    const [statusFilterVal, setStatusFilterVal] = useState('');
    const [searchVal, setSearchVal] = useState('');
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [page, setPage] = useState(0);
    const [users, setUsers] = useState([]);
    const [totalUsers, setTotalUsers] = useState(0);
    const [selectedUserIds, setSelectedUserIds] = useState([]);
    const [loading, setLoading] = useState(false);

    const context = useContext(MyContext);

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const skip = page * rowsPerPage;
            const limit = rowsPerPage;

            const body = {
                search: searchVal,
                customer_status: statusFilterVal,
            };

            const response = await postDataApi(`/admin/user/all?skip=${skip}&limit=${limit}`, body);
            console.log(response);

            if (response.success === true) {
                setUsers(response.data.data || []);
                setTotalUsers(response.data.total || 0);
            } else {
                context.openAlertBox("error", response.message);
            }
        } catch (error) {
            console.error('Error fetching users:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, [page, rowsPerPage, statusFilterVal, searchVal]);

    const handleChangeStatusFilter = (event) => {
        setStatusFilterVal(event.target.value);
    };

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(+event.target.value);
        setPage(0);
    };

    const handleBlockUser = async (userId) => {
        try {
            const response = await putDataApi(`/admin/user/${userId}/change-status`);
            if (response.success) {
                context.openAlertBox('success', response.message);
                fetchUsers();
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || 'Thay đổi trạng thái thất bại');
            }
        } catch (error) {
            context.openAlertBox('error', 'Lỗi hệ thống khi đổi trạng thái người dùng');
        }
    };

    const handleDeleteUser = async (userId) => {
        if (!window.confirm("Bạn có chắc muốn xóa người dùng này?")) return;
        try {
            const response = await deleteDataApi(`/admin/user/${userId}`);
            if (response.success) {
                context.openAlertBox('success', response.message);
                fetchUsers();
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || 'Xóa người dùng thất bại');
            }
        } catch (error) {
            context.openAlertBox('error', 'Lỗi hệ thống khi xóa người dùng');
        }
    };

    const handleDeleteMultipleUser = async () => {
        if (!window.confirm(`Bạn có chắc muốn xóa ${selectedUserIds.length} người dùng không?`)) return;

        try {
            const response = await postDataApi('/admin/user/delete', {
                user_ids: selectedUserIds
            });

            if (response.success) {
                context.openAlertBox('success', response.message);
                setSelectedUserIds([]);
                fetchUsers();
            } else {
                context.openAlertBox('error', response?.data?.detail || 'Xóa nhiều người dùng thất bại');
            }
        } catch (error) {
            context.openAlertBox('error', 'Lỗi hệ thống khi xóa nhiều người dùng');
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString("vi-VN", {
            day: "2-digit", month: "2-digit", year: "numeric"
        });
    };

    const debouncedSearch = useCallback(
        debounce((searchTerm) => {
            setSearchVal(searchTerm);
        }, 500),
        []
    );

    useEffect(() => {
        setPage(0);  // reset page
    }, [statusFilterVal, searchVal]);

    return (
        <>
            <div className="flex items-center justify-between px-2 py-0 mt-3">
                <h2 className="text-[18px] font-[600]">Danh sách khách hàng</h2>
            </div>

            <div className="card my-4 pt-5 shadow-md sm:rounded-lg bg-white">
                <div className="flex items-center w-full px-5 justify-between">
                    <div className="flex items-center gap-4 w-[60%]">
                        <div className="col w-[30%]">
                            <h4 className="font-[600] text-[13px] mb-3">Sắp xếp theo trạng thái</h4>
                            <Select
                                className="w-full mb-5"
                                size="small"
                                value={statusFilterVal}
                                onChange={handleChangeStatusFilter}
                            >
                                <MenuItem value="">Tất cả trạng thái</MenuItem>
                                <MenuItem value="active">Hoạt động</MenuItem>
                                <MenuItem value="inactive">Bị khóa</MenuItem>
                            </Select>
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
                ) : (
                    <>
                        <TableContainer sx={{ maxHeight: 440 }}>
                            <Table stickyHeader aria-label="user table">
                                <TableHead className="bg-[#f1f1f1]">
                                    <TableRow>
                                        <TableCell>
                                            <Checkbox {...label} size="small"
                                                checked={selectedUserIds.length === users.length && users.length > 0}
                                                indeterminate={selectedUserIds.length > 0 && selectedUserIds.length < users.length}
                                                onChange={(e) => {
                                                    if (e.target.checked) {
                                                        const allIds = users.map(u => u.id);
                                                        setSelectedUserIds(allIds);
                                                    } else {
                                                        setSelectedUserIds([]);
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
                                    {users.map((user) => {
                                        const isActive = user.customer_status === "active";
                                        return (
                                            <TableRow key={user.id}>
                                                <TableCell>
                                                    <Checkbox {...label} size="small"
                                                        checked={selectedUserIds.includes(user.id)}
                                                        onChange={(e) => {
                                                            if (e.target.checked) {
                                                                setSelectedUserIds(prev => [...prev, user.id]);
                                                            } else {
                                                                setSelectedUserIds(prev => prev.filter(id => id !== user.id));
                                                            }
                                                        }}
                                                    />
                                                </TableCell>

                                                <TableCell>
                                                    <span className="font-[Montserrat] text-gray-600">{user.first_name} {user.last_name}</span>
                                                </TableCell>

                                                <TableCell>
                                                    <span className="flex gap-2 font-[Montserrat] text-gray-600">
                                                        <MdOutlineMarkEmailRead className="mt-1" />
                                                        {user.email}
                                                    </span>
                                                </TableCell>

                                                <TableCell>
                                                    <span className="flex gap-2 font-[Montserrat] text-gray-600">
                                                        {user.phone ? <MdLocalPhone className="mt-1" /> : null}
                                                        {user.phone || "Không có"}
                                                    </span>
                                                </TableCell>

                                                <TableCell>
                                                    <span className={`text-sm font-medium px-5 py-2 rounded-full
                                                        ${isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                        {isActive ? 'Hoạt động' : 'Bị khóa'}
                                                    </span>
                                                </TableCell>

                                                <TableCell>
                                                    <span className="text-[13px] text-gray-500 font-[Montserrat]">
                                                        {formatDate(user.created_at)}
                                                    </span>
                                                </TableCell>

                                                <TableCell className="flex gap-2">
                                                    <Button
                                                        className={`!text-white btn-sm ${isActive ? '!bg-red-700 hover:!bg-red-600' : '!bg-green-600 hover:!bg-green-500'}`}
                                                        onClick={() => handleBlockUser(user.id)}
                                                    >
                                                        {isActive ? 'Khóa' : 'Mở khóa'}
                                                    </Button>

                                                    <IconButton
                                                        onClick={() => handleDeleteUser(user.id)}
                                                        className="!text-red-600 hover:!text-red-800"
                                                    >
                                                        <MdDelete />
                                                    </IconButton>
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
                            count={totalUsers}
                            rowsPerPage={rowsPerPage}
                            page={page}
                            onPageChange={handleChangePage}
                            onRowsPerPageChange={handleChangeRowsPerPage}
                        />
                    </>
                )}
            </div>
            {selectedUserIds.length > 0 && (
                <div className="px-2 mt-2">
                    <Button
                        className="!bg-red-700 hover:!bg-red-600 btn-sm !text-white"
                        onClick={handleDeleteMultipleUser}
                    >
                        Xóa {selectedUserIds.length} người dùng
                    </Button>
                </div>
            )}
        </>
    );
}

export default Users