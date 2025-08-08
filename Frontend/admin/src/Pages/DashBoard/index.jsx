import React, { useState, PureComponent, useContext } from "react";
import DashBoardBoxes from "../../Components/DashBoardBoxes";
import Button from "@mui/material/Button";
import { FaAngleDown, FaAngleUp, FaPlus, FaRegEye } from "react-icons/fa";
import Badge from "../../Components/Badge"
import Checkbox from '@mui/material/Checkbox';
import { Link } from "react-router-dom";
import ProgressBar from "../../Components/ProgressBar";
import { AiOutlineEdit } from "react-icons/ai";
import { GoTrash } from "react-icons/go";
import Pagination from '@mui/material/Pagination';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import { MenuItem, Select } from "@mui/material";
import { BiExport } from "react-icons/bi";
import { MyContext } from "../../App";
import Products from "../Products";
import Orders from "../Orders";

const DashBoard = () => {
    const [isOpenOrderedProduct, setIsOpenOrderedProduct] = useState(null)
    const isShowOrderedProduct = (index) => {
        if (isOpenOrderedProduct === index) {
            setIsOpenOrderedProduct(null)
        } else {
            setIsOpenOrderedProduct(index)
        }
    }

    const [chart1Data, setChart1Data] = useState(
        [
            {
                name: 'JAN',
                TotalUsers: 4000,
                TotalSales: 2400,
                amt: 2400,
            },
            {
                name: 'FEB',
                TotalUsers: 3000,
                TotalSales: 1398,
                amt: 2210,
            },
            {
                name: 'MARCH',
                TotalUsers: 2000,
                TotalSales: 9800,
                amt: 2290,
            },
            {
                name: 'APRIL',
                TotalUsers: 2780,
                TotalSales: 3908,
                amt: 2000,
            },
            {
                name: 'MAY',
                TotalUsers: 1890,
                TotalSales: 4800,
                amt: 2181,
            },
            {
                name: 'JUNE',
                TotalUsers: 2390,
                TotalSales: 3800,
                amt: 2500,
            },
            {
                name: 'JULY',
                TotalUsers: 3490,
                TotalSales: 4300,
                amt: 2100,
            },
            {
                name: 'AUG',
                TotalUsers: 4000,
                TotalSales: 2400,
                amt: 2400,
            },
            {
                name: 'SEP',
                TotalUsers: 2000,
                TotalSales: 9800,
                amt: 2290,
            },
            {
                name: 'OCT',
                TotalUsers: 3490,
                TotalSales: 4300,
                amt: 2100,
            },
            {
                name: 'NOV',
                TotalUsers: 2000,
                TotalSales: 9800,
                amt: 2290,
            },
            {
                name: 'DEC',
                TotalUsers: 3490,
                TotalSales: 4300,
                amt: 2100,
            },
        ]
    )

    const context = useContext(MyContext)

    return (
        <>
            <div className="w-full py-2 p-5 border bg-[#f1faff] border-[rgba(0,0,0,0.1)] flex items-center gap-8 mb-5 justify-between rounded-md">
                <div className="info">
                    <h1 className="text-[35px] font-[700] leading-10 mb-3">Good Morning,<br />
                        Cameron
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" class="inline-flex h-8 w-8 ml-2"><path fill="#fac036" d="M39.11 79.56c-1.1 1.03-2.21-.2-2.21-.2S18.42 59.78 17.22 58.9c-1.69-1.23-5.31-3.16-8.93.57-1.51 1.55-3.97 5 .6 10.56.99 1.2 29.78 31.54 31.46 33.18 0 0 13.3 12.94 21.35 17.81 2.23 1.35 4.74 2.78 7.67 3.78 2.92 1 6.22 1.69 9.7 1.69 3.48.04 7.09-.63 10.5-1.88 3.41-1.26 6.59-3.09 9.48-5.2.71-.54 1.43-1.08 2.1-1.66l1.94-1.6a58.67 58.67 0 0 0 3.82-3.53c2.43-2.42 4.62-5.01 6.55-7.66 1.92-2.66 3.55-5.41 4.85-8.15 1.3-2.74 2.21-5.49 2.76-8.09.58-2.59.74-5.04.65-7.18-.02-2.14-.45-3.97-.8-5.43-.4-1.46-.83-2.55-1.17-3.27-.33-.72-.51-1.1-.51-1.1-.46-1.29-.9-2.52-1.29-3.63a889.622 889.622 0 0 0-4.51-12.47l.01.03c-4.85-13.17-10.06-26.74-10.06-26.74-.79-2.39-3.7-3.22-5.84-1.68-6.18 4.44-8.07 10.92-5.89 17.83l5.59 15.32c.79 1.71-1.39 3.69-2.85 2.5-4.59-3.74-14.3-14.05-14.3-14.05-4.34-4.16-28.83-29.27-30.47-30.8-3.3-3.07-7.46-4.65-10.63-2.32-3.24 2.38-4.14 6.06-1.01 10.08.85 1.09 25.6 27.24 25.6 27.24 1.44 1.51-.26 3.65-1.85 2.18 0 0-30.79-32.12-32.18-33.62-3.15-3.42-8.21-4.17-11.21-1.35-2.93 2.75-2.86 7.26.34 10.8 1.02 1.12 22.71 24.02 31.39 33.4.58.63 1.03 1.47.17 2.26-.01.01-.88.95-2-.25-2.36-2.52-25.93-27.08-27.24-28.41-3.01-3.06-7.05-4.51-10.3-1.53-2.96 2.71-3.44 7.44-.04 10.78l28.55 30.18s.93 1.1-.11 2.07z"></path><path fill="#e48c15" d="m85.46 54.4 2.41 2.58s-13.79 13.31-4.39 33.75c0 0 1.22 2.59-.38 3.02 0 0-1.4.78-3-3.2 0-.01-9.49-19.42 5.36-36.15z"></path><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-miterlimit="10" stroke-width="4" opacity="0.5" d="M63.28 10.2s5.81.88 11.19 6.64c5.38 5.77 7.87 13.18 7.87 13.18M77.44 3.5s4.87 2.45 8.63 8.5c3.76 6.05 4.67 13.05 4.67 13.05m-55.03 85.68s-5.86.39-12.35-4.09-10.52-11.18-10.52-11.18m18.69 25.1s-5.44.23-11.68-3.22-10.44-9.12-10.44-9.12"></path></svg>
                    </h1>
                    <p>Here’s What happening on your store today. See the statistics at once.</p>

                    <br />

                    <Button className="btn-blue !capitalize" onClick={() => context.setIsOpenFullScreenPanel({
                        open: true,
                        model: "Add Product"
                    })}>
                        <FaPlus className="mr-1" /> Add Product
                    </Button>
                </div>

                <img src="shop-illustration.webp" className="w-[250px]" />
            </div>
            <DashBoardBoxes />

            <div className="pt-5">
                <Products />
            </div>

            <div className="card my-4 shadow-md sm:rounded-lg bg-white">
                <Orders />
            </div>

            <div className="card my-4 shadow-md sm:rounded-lg bg-white">
                <div className="flex items-center justify-between px-5 py-5">
                    <h2 className="text-[18px] font-[600]">Total Users & Total Sales</h2>
                </div>

                <div className="flex items-center gap-5 px-5 py-5 pt-1">
                    <span className="flex items-center gap-1 text-[15px]">
                        <span className="block w-[8px] h-[8px] rounded-full bg-green-600">
                        </span>
                        Total Sales
                    </span>

                    <span className="flex items-center gap-1 text-[15px]">
                        <span className="block w-[8px] h-[8px] rounded-full bg-[#3872fa]">
                        </span>
                        Total Users
                    </span>
                </div>

                <ResponsiveContainer width={1000} height={400}>
                    <LineChart
                        width={1000}
                        height={500}
                        data={chart1Data}
                        margin={{
                            top: 5,
                            right: 30,
                            left: 20,
                            bottom: 5,
                        }}
                    >
                        <CartesianGrid strokeDasharray="3 3" stroke="none" />
                        <XAxis dataKey="name" tick={{ fontSize: 14 }} />
                        <YAxis tick={{ fontSize: 14 }} />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="TotalUsers" stroke="#8884d8" activeDot={{ r: 8 }} strokeWidth={3} />
                        <Line type="monotone" dataKey="TotalSales" stroke="#82ca9d" strokeWidth={3} />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </>
    )
}

export default DashBoard