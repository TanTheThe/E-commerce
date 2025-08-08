import React, { useContext, useEffect, useState } from "react";
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';
import 'swiper/css/navigation';
import { Navigation } from 'swiper/modules';
import { AiTwotoneGift, AiTwotonePieChart } from "react-icons/ai";
import { IoStatsChartSharp } from "react-icons/io5";
import { BsBank } from "react-icons/bs";
import { RiProductHuntLine } from "react-icons/ri";
import { MyContext } from "../../App";
import { getDataApi } from "../../utils/api";

const DashBoardBoxes = () => {
    const [newOrders, setNewOrders] = useState(0);
    const [totalSales, setTotalSales] = useState(0);
    const [totalRevenue, setTotalRevenue] = useState(0);
    const [countProducts, setCountProducts] = useState(0);
    const context = useContext(MyContext)

    useEffect(() => {
        const fetchNewOrders = async () => {
            try {
                const res = await getDataApi(`/admin/order/statistics/count-orders`);
                if (res.success) {
                    setNewOrders(res.data.count_orders);
                }else{
                    context.openAlertBox("error", res?.data?.detail.message || "Xảy ra lỗi trong quá trình tính tổng sản phẩm")
                }
            } catch (error) {
                context.openAlertBox("error", res?.data?.detail.message || "Xảy ra lỗi trong quá trình tính tổng sản phẩm")
                console.error("Failed to fetch new orders", error);
            }
        };

        const fetchTotalSales = async () => {
            try {
                const res = await getDataApi(`/admin/order/statistics/sales`);
                if (res.success) {
                    setTotalSales(res.data.total_sales || 0);
                } else {
                    context.openAlertBox("error", res?.data?.detail.message || "Xảy ra lỗi khi lấy doanh thu");
                }
            } catch (error) {
                context.openAlertBox("error", "Xảy ra lỗi khi lấy doanh thu");
                console.error("Failed to fetch total sales", error);
            }
        };

        const fetchTotalRevenue = async () => {
            try {
                const res = await getDataApi(`/admin/order/statistics/revenue`);
                if (res.success) {
                    setTotalRevenue(res.data.total_revenue || 0);
                } else {
                    context.openAlertBox("error", res?.data?.detail.message || "Xảy ra lỗi khi lấy doanh thu");
                }
            } catch (error) {
                context.openAlertBox("error", "Xảy ra lỗi khi lấy doanh thu");
                console.error("Failed to fetch total revenue", error);
            }
        };

        const fetchCountProducts = async () => {
            try {
                const res = await getDataApi(`/admin/product/statistics/count-products`);
                if (res.success) {
                    setCountProducts(res.data.count_products || 0);
                } else {
                    context.openAlertBox("error", res?.data?.detail.message || "Xảy ra lỗi khi lấy doanh thu");
                }
            } catch (error) {
                context.openAlertBox("error", "Xảy ra lỗi khi lấy doanh thu");
                console.error("Failed to fetch total revenue", error);
            }
        };

        fetchNewOrders();
        fetchTotalSales();
        fetchTotalRevenue();
        fetchCountProducts();
    }, []);

    return (
        <>
            <Swiper
                slidesPerView={4}
                spaceBetween={30}
                navigation={true}
                modules={[Navigation]}
                className="dashboardBoxesSlider"
            >
                <SwiperSlide>
                    <div className="box bg-white p-5 cursor-pointer hover:bg-[#f1f1f1] rounded-md border border-[rgba(0,0,0,0.1)] flex items-center gap-4">
                        <AiTwotoneGift className="text-[40px] text-[#3872fa]" />
                        <div className="info w-[70%]">
                            <h3>New Orders</h3>
                            <b>{newOrders}</b>
                        </div>
                        <IoStatsChartSharp className="text-[50px] text-[#3872fa]" />
                    </div>
                </SwiperSlide>
                <SwiperSlide>
                    <div className="box bg-white p-5 cursor-pointer hover:bg-[#f1f1f1] rounded-md border border-[rgba(0,0,0,0.1)] flex items-center gap-4">
                        <AiTwotonePieChart className="text-[40px] text-[#10b981]" />
                        <div className="info w-[70%]">
                            <h3>Sales</h3>
                            <b>{totalSales.toLocaleString('vi-VN')} ₫</b>
                        </div>
                        <IoStatsChartSharp className="text-[50px] text-[#10b981]" />
                    </div>
                </SwiperSlide>
                <SwiperSlide>
                    <div className="box bg-white p-5 cursor-pointer hover:bg-[#f1f1f1] rounded-md border border-[rgba(0,0,0,0.1)] flex items-center gap-4">
                        <BsBank className="text-[40px] text-[#7928ca]" />
                        <div className="info w-[70%]">
                            <h3>Revenue</h3>
                            <b>{totalRevenue.toLocaleString('vi-VN')} ₫</b>
                        </div>
                        <IoStatsChartSharp className="text-[50px] text-[#7928ca]" />
                    </div>
                </SwiperSlide>
                <SwiperSlide>
                    <div className="box bg-white p-5 cursor-pointer hover:bg-[#f1f1f1] rounded-md border border-[rgba(0,0,0,0.1)] flex items-center gap-4">
                        <RiProductHuntLine className="text-[40px] text-[#ca7e28]" />
                        <div className="info w-[70%]">
                            <h3>Total Products</h3>
                            <b>{countProducts}</b>
                        </div>
                        <IoStatsChartSharp className="text-[50px] text-[#ca7e28]" />
                    </div>
                </SwiperSlide>
            </Swiper>
        </>
    )
}

export default DashBoardBoxes