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

const Orders = () => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(false);
    const [openOrderDetail, setOpenOrderDetail] = useState(false);
    const [selectedOrder, setSelectedOrder] = useState(null);
    const [openStatusUpdate, setOpenStatusUpdate] = useState(false);
    const [searchInput, setSearchInput] = useState('');
    const [searchTerm, setSearchTerm] = useState('');

    const context = useContext(MyContext)

    const fetchOrders = async (search = '') => {
        setLoading(true);
        const res = await getDataApi(`/admin/order?skip=0&limit=10&search=${encodeURIComponent(search)}`);
        if (res.success) {
            setOrders(res.data);
        } else {
            context.openAlertBox("error", res?.data?.detail.message || "Xảy ra lỗi trong quá trình lấy danh sách sản phẩm")
        }
        setLoading(false);
    };

    const handleViewOrderDetail = async (orderId) => {
        const res = await getDataApi(`/admin/order/${orderId}`);
        console.log(res);
        if (res.success) {
            setSelectedOrder(res.data);
            setOpenOrderDetail(true);
        } else {
            context.openAlertBox("error", res?.data?.detail.message || "Xảy ra lỗi trong quá trình hiển thị sản phẩm")
        }
    };

    const handleUpdateOrderStatus = async (orderId, newStatus) => {
        try {
            const res = await putDataApi(`/admin/order/status/${orderId}`, {
                status: newStatus
            });
            console.log(res);
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

    const debouncedSearch = useCallback(
        debounce((value) => {
            setSearchTerm(value);
            fetchOrders(value);
        }, 500),
        []
    );

    useEffect(() => {
        debouncedSearch(searchInput);
    }, [searchInput]);

    useEffect(() => {
        fetchOrders();
    }, []);

    const formatDate = (isoDateStr) => {
        if (!isoDateStr) return "";
        return new Date(isoDateStr).toISOString().split("T")[0];
    };

    return (
        <>

            <div className="card my-4 shadow-md sm:rounded-lg bg-white">
                <div className="flex items-center justify-between px-5 py-5">
                    <h2 className="text-[18px] font-[600]">Recent Orders</h2>
                    <div className="w-[40%]"><SearchBox searchTerm={searchInput} setSearchTerm={setSearchInput} /></div>
                </div>
                <div className="relative overflow-x-auto mt-5 pb-5">
                    <table className="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
                        <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                            <tr>
                                <th scope="col" className="px-6 py-3 whitespace-nowrap">
                                    Order Code
                                </th>
                                <th scope="col" className="px-6 py-3 whitespace-nowrap">
                                    Customer Name
                                </th>
                                <th scope="col" className="px-6 py-3 whitespace-nowrap">
                                    Total Price
                                </th>
                                <th scope="col" className="px-6 py-3 whitespace-nowrap">
                                    Status
                                </th>
                                <th scope="col" className="px-6 py-3 whitespace-nowrap">
                                    Created At
                                </th>
                                <th scope="col" className="px-6 py-3 whitespace-nowrap">
                                    Actions
                                </th>
                            </tr>
                        </thead>

                        <tbody>
                            {loading ?
                                <tr>
                                    <td colSpan="6" className="text-center py-6 text-gray-500">Đang tải đơn hàng...</td>
                                </tr>
                                :
                                orders.map((order, index) => (
                                    <tr key={order.id} className="bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200">
                                        <td className="px-6 py-4 font-[500]">
                                            <span className="text-[#3872fa] font-[600]">{order.code}</span>
                                        </td>
                                        <td className="px-6 py-4 font-[500] whitespace-nowrap">
                                            {order.customer_name}
                                        </td>
                                        <td className="px-6 py-4 font-[500]">
                                            {order.total_price.toLocaleString()}₫
                                        </td>
                                        <td className="px-6 py-4 font-[500]">
                                            <Badge status={order.status} />
                                        </td>
                                        <td className="px-6 py-4 font-[500] whitespace-nowrap">
                                            {formatDate(order.created_at)}
                                        </td>
                                        <td className="px-6 py-4 font-[500]">
                                            <div className="flex items-center gap-2">
                                                <Button
                                                    onClick={() => handleOpenStatusUpdate(order)}
                                                    className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-[#f1f1f1] !min-w-[35px] !text-black">
                                                    <AiOutlineEdit className="text-[rgba(0,0,0,0.7)] text-[20px]" />
                                                </Button>
                                                <Button
                                                    className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-[#f1f1f1] !min-w-[35px]"
                                                    onClick={() => handleViewOrderDetail(order.id)}>
                                                    <FaRegEye className="text-[rgba(0,0,0,0.7)] text-[20px]" />
                                                </Button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            }
                        </tbody>
                    </table>
                </div>
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