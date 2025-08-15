import React, { useCallback, useContext, useEffect, useState } from "react";
import Button from "@mui/material/Button";
import { FaAngleDown, FaAngleUp, FaRegEye } from "react-icons/fa";
import Badge from "../../Components/Badge"
import SearchBox from "../../Components/SearchBox";
import { GoTrash } from "react-icons/go";
import { AiOutlineEdit } from "react-icons/ai";
import { getDataApi, putDataApi } from "../../utils/api";
import OrderDetailOffcanvas from "./offcanvasOrderDetail";
import OrderStatusUpdateModal from "./updateStatusOrder";
import { MyContext } from "../../App";
import { debounce } from "lodash";
import { MenuItem, Select, Table, TableBody, TableCell, TableContainer, TableHead, TablePagination, TableRow } from "@mui/material";

const columns = [
    { id: 'code', label: 'ORDER CODE', minWidth: 120, align: 'center' },
    { id: 'customer_name', label: 'CUSTOMER NAME', minWidth: 200, align: 'center' },
    { id: 'total_price', label: 'TOTAL PRICE', minWidth: 150, align: 'center' },
    { id: 'status', label: 'STATUS', minWidth: 120, align: 'center' },
    { id: 'created_at', label: 'CREATED AT', minWidth: 150, align: 'center' },
    { id: 'action', label: 'ACTION', minWidth: 150, align: 'center' }
];

const Orders = () => {
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [page, setPage] = useState(0);
    const [orders, setOrders] = useState([]);
    const [totalCount, setTotalCount] = useState(0);
    const [loading, setLoading] = useState(true);
    const [openOrderDetail, setOpenOrderDetail] = useState(false);
    const [selectedOrder, setSelectedOrder] = useState(null);
    const [openStatusUpdate, setOpenStatusUpdate] = useState(false);

    const [searchInput, setSearchInput] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [sortByTotalPrice, setSortByTotalPrice] = useState('');
    const [sortByCreatedAt, setSortByCreatedAt] = useState('newest');
    const [statusFilter, setStatusFilter] = useState('');

    const context = useContext(MyContext)

    const buildQueryParams = useCallback((customPage = page, customRowsPerPage = rowsPerPage, customSearch = searchTerm) => {
        const params = new URLSearchParams();
        const skip = customPage * customRowsPerPage;

        params.append('skip', skip.toString());
        params.append('limit', customRowsPerPage.toString());

        if (customSearch) params.append('search', customSearch);
        if (sortByTotalPrice) params.append('sort_by_total_price', sortByTotalPrice);
        if (sortByCreatedAt) params.append('sort_by_created_at', sortByCreatedAt);
        if (statusFilter) params.append('status_filter', statusFilter);

        return params.toString();
    }, [page, rowsPerPage, searchTerm, sortByTotalPrice, sortByCreatedAt, statusFilter]);

    const fetchOrders = useCallback(async (customPage = page, customRowsPerPage = rowsPerPage, customSearch = searchTerm) => {
        try {
            setLoading(true);
            const queryParams = buildQueryParams(customPage, customRowsPerPage, customSearch);
            const response = await getDataApi(`/admin/order?${queryParams}`);

            if (response.success) {
                const responseData = response.data?.content || response.data;
                setOrders(responseData.data || []);
                setTotalCount(responseData.total || 0);
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || "Có lỗi trong quá trình tải danh sách đơn hàng");
                setOrders([]);
                setTotalCount(0);
            }
        } catch (error) {
            context.openAlertBox("error", "Lỗi hệ thống khi tải đơn hàng");
            setOrders([]);
            setTotalCount(0);
        } finally {
            setLoading(false);
        }
    }, [buildQueryParams, page, rowsPerPage, searchTerm, context]);

    useEffect(() => {
        fetchOrders(page, rowsPerPage, searchTerm);
    }, [page, rowsPerPage, searchTerm, sortByTotalPrice, sortByCreatedAt, statusFilter, fetchOrders]);

    const debouncedSearch = useCallback(
        debounce((value) => {
            setSearchTerm(value);
            setPage(0);
        }, 500),
        []
    );

    useEffect(() => {
        debouncedSearch(searchInput);
        return () => {
            debouncedSearch.cancel();
        };
    }, [searchInput, debouncedSearch]);

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        const newRowsPerPage = +event.target.value;
        setRowsPerPage(newRowsPerPage);
        setPage(0);
    };

    const handleSortByTotalPriceChange = (event) => {
        setSortByTotalPrice(event.target.value);
        setPage(0);
    };

    const handleSortByCreatedAtChange = (event) => {
        setSortByCreatedAt(event.target.value);
        setPage(0);
    };

    const handleStatusFilterChange = (event) => {
        setStatusFilter(event.target.value);
        setPage(0);
    };

    const clearFilters = () => {
        setSearchInput('');
        setSearchTerm('');
        setSortByTotalPrice('');
        setSortByCreatedAt('newest');
        setStatusFilter('');
        setPage(0);
    };

    const handleViewOrderDetail = async (orderId) => {
        try {
            const res = await getDataApi(`/admin/order/${orderId}`);
            if (res.success) {
                setSelectedOrder(res.data);
                setOpenOrderDetail(true);
            } else {
                context.openAlertBox("error", res?.data?.detail?.message || "Xảy ra lỗi trong quá trình hiển thị đơn hàng");
            }
        } catch (error) {
            context.openAlertBox("error", "Lỗi hệ thống khi tải chi tiết đơn hàng");
        }
    };

    const handleUpdateOrderStatus = async (orderId, newStatus) => {
        try {
            const res = await putDataApi(`/admin/order/status/${orderId}`, {
                status: newStatus
            });

            if (res.success) {
                setOrders(prevOrders =>
                    prevOrders.map(order =>
                        order.id === orderId
                            ? { ...order, status: newStatus }
                            : order
                    )
                );
                context.openAlertBox("success", res.message)
            } else {
                context.openAlertBox("error", res?.data?.detail.message || "Xảy ra lỗi trong quá trình cập nhật trạng thái")
            }
        } catch (error) {
            console.error('Lỗi:', error);
            context.openAlertBox("error", res?.data?.detail.message || "Xảy ra lỗi trong quá trình cập nhật trạng thái")
        }
    };

    const handleOpenStatusUpdate = (order) => {
        setSelectedOrder(order);
        setOpenStatusUpdate(true);
    };

    const formatDate = (isoDateStr) => {
        if (!isoDateStr) return "";
        return new Date(isoDateStr).toLocaleDateString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    };

    const formatPrice = (price) => {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(price);
    };

    return (
        <>
            <div className="flex items-center justify-between px-2 py-0 mt-3">
                <h2 className="text-[18px] font-[600]">
                    Danh sách đơn hàng
                </h2>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm my-4">
                <h3 className="text-lg font-semibold text-gray-700 mb-4">Bộ lọc tìm kiếm</h3>

                <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Tìm kiếm</label>
                    <SearchBox searchTerm={searchInput} setSearchTerm={setSearchInput} />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    <div className="flex flex-col">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Trạng thái đơn hàng</label>
                        <Select value={statusFilter} onChange={handleStatusFilterChange} className="w-full h-11">
                            <MenuItem value="">-- Tất cả trạng thái --</MenuItem>
                            <MenuItem value="Pending">Chờ xử lý</MenuItem>
                            <MenuItem value="Confirmed">Đã xác nhận</MenuItem>
                            <MenuItem value="Shipping">Đang giao</MenuItem>
                            <MenuItem value="Delivered">Đã giao</MenuItem>
                            <MenuItem value="Cancelled">Đã hủy</MenuItem>
                        </Select>
                    </div>

                    <div className="flex flex-col">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Sắp xếp theo giá</label>
                        <Select value={sortByTotalPrice} onChange={handleSortByTotalPriceChange} className="w-full h-11">
                            <MenuItem value="">-- Không sắp xếp --</MenuItem>
                            <MenuItem value="cheapest">Giá thấp nhất</MenuItem>
                            <MenuItem value="expensive">Giá cao nhất</MenuItem>
                        </Select>
                    </div>

                    <div className="flex flex-col">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Sắp xếp theo ngày</label>
                        <Select value={sortByCreatedAt} onChange={handleSortByCreatedAtChange} className="w-full h-11">
                            <MenuItem value="newest">Mới nhất</MenuItem>
                            <MenuItem value="oldest">Cũ nhất</MenuItem>
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

                {(searchTerm || statusFilter || sortByTotalPrice || sortByCreatedAt !== 'newest') && (
                    <div className="mt-6 pt-4 border-t border-gray-200">
                        <p className="text-sm text-gray-600 mb-2">Bộ lọc hiện tại:</p>
                        <div className="flex flex-wrap gap-2">
                            {searchTerm && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                    Tìm kiếm: "{searchTerm}"
                                </span>
                            )}
                            {statusFilter && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                    Trạng thái: {
                                        statusFilter === 'Pending' ? 'Chờ xử lý' :
                                            statusFilter === 'Confirmed' ? 'Đã xác nhận' :
                                                statusFilter === 'Shipping' ? 'Đang giao' :
                                                    statusFilter === 'Delivered' ? 'Đã giao' : 'Đã hủy'
                                    }
                                </span>
                            )}
                            {sortByTotalPrice && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                    Sắp xếp giá: {sortByTotalPrice === 'cheapest' ? 'Thấp nhất' : 'Cao nhất'}
                                </span>
                            )}
                            {sortByCreatedAt !== 'newest' && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                    Sắp xếp ngày: {sortByCreatedAt === 'oldest' ? 'Cũ nhất' : 'Mới nhất'}
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
                                    {orders.length === 0 ? (
                                        <TableRow>
                                            <TableCell colSpan={columns.length} align="center">
                                                <div className="py-8 text-gray-500">
                                                    Không tìm thấy đơn hàng nào
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    ) : (
                                        orders.map((order) => {
                                            return (
                                                <TableRow key={order.id} hover>
                                                    <TableCell align="center">
                                                        <span className="text-[#3872fa] font-[600]">{order.code}</span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <span className="font-medium">{order.customer_name}</span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <span className="font-medium">{formatPrice(order.total_price)}</span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <Badge status={order.status} />
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <span className="font-medium">{formatDate(order.created_at)}</span>
                                                    </TableCell>

                                                    <TableCell align="center">
                                                        <div className="flex items-center justify-center gap-4">
                                                            <Button
                                                                className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-[#e1e1e1] !min-w-[35px]"
                                                                onClick={() => handleOpenStatusUpdate(order)}
                                                                title="Cập nhật trạng thái"
                                                            >
                                                                <AiOutlineEdit className="text-[rgba(0,0,0,0.7)] text-[20px]" />
                                                            </Button>

                                                            <Button
                                                                className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-[#e1e1e1] !min-w-[35px]"
                                                                onClick={() => handleViewOrderDetail(order.id)}
                                                                title="Xem chi tiết"
                                                            >
                                                                <FaRegEye className="text-[rgba(0,0,0,0.7)] text-[20px]" />
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

            <OrderDetailOffcanvas
                open={openOrderDetail}
                onClose={() => setOpenOrderDetail(false)}
                order={selectedOrder}
            />
            <OrderStatusUpdateModal
                open={openStatusUpdate}
                onClose={() => setOpenStatusUpdate(false)}
                order={selectedOrder}
                onUpdateStatus={handleUpdateOrderStatus}
            />
        </>
    )
}

export default Orders