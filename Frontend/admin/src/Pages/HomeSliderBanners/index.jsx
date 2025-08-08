import React, { useContext, useState } from "react";
import { Button } from "@mui/material";
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


const label = { inputProps: { 'aria-label': 'Checkbox demo' } };

const columns = [
    { id: 'image', label: 'IMAGE', minWidth: 250 },
    { id: 'action', label: 'ACTION', minWidth: 100 }
];

const HomeSliderBanners = () => {
    const [categoryFilterVal, setCategoryFilterVal] = useState('')
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [page, setPage] = useState(0);

    const context = useContext(MyContext)

    const handleChangeCateFilter = (event) => {
        setCategoryFilterVal(event.target.value);
    };

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(+event.target.value);
        setPage(0);
    };

    return (
        <>
            <div className="flex items-center justify-between px-2 py-0 mt-3">
                <h2 className="text-[18px] font-[600]">
                    Home Slider Banners{" "}
                    <span className="font-[400] text-[14px]">(Table)</span>
                </h2>

                <div className="col w-[18%] ml-auto flex items-center justify-end gap-3">
                    <Button className="btn !bg-green-600 !text-white btn-sm flex items-center">Export</Button>
                    <Button className="btn-blue !text-white btn-sm" onClick={() => context.setIsOpenFullScreenPanel({
                        open: true,
                        model: 'Add Home Slide'
                    })}>Add Home Slide</Button>
                </div>
            </div>

            <div className="card my-4 pt-5 shadow-md sm:rounded-lg bg-white">
                <TableContainer sx={{ maxHeight: 440 }}>
                    <Table stickyHeader aria-label="sticky table">
                        <TableHead className="bg-[#f1f1f1]">
                            <TableRow>
                                <TableCell width={80}>
                                    <Checkbox {...label} size="small" />
                                </TableCell>
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
                            <TableRow>
                                <TableCell>
                                    <Checkbox {...label} size="small" />
                                </TableCell>

                                <TableCell width={300}>
                                    <div className="flex items-center gap-4 w-[300px]">
                                        <div className="img w-full rounded-md overflow-hidden group">
                                            <a href="/product/45745" data-discover="true">
                                                <img className="w-full group-hover:scale-105" src="https://api.spicezgold.com/download/file_1734524878924_1721277298204_banner.jpg" />
                                            </a>
                                        </div>
                                    </div>
                                </TableCell>

                                <TableCell width={100}>
                                    <div className="flex items-center gap-4">
                                        <Button className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-[#f1f1f1] !min-w-[35px]">
                                            <AiOutlineEdit className="text-[rgba(0,0,0,0.7)] text-[20px]" />
                                        </Button>

                                        <Button className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-[#f1f1f1] !min-w-[35px]">
                                            <FaRegEye className="text-[rgba(0,0,0,0.7)] text-[20px]" />
                                        </Button>

                                        <Button className="!w-[35px] !h-[35px] bg-[#f1f1f1] !border-[rgba(0,0,0,0.4)] !rounded-full hover:!bg-[#f1f1f1] !min-w-[35px]">
                                            <GoTrash className="text-[rgba(0,0,0,0.7)] text-[20px]" />
                                        </Button>
                                    </div>
                                </TableCell>
                            </TableRow>
                        </TableBody>
                    </Table>
                </TableContainer>

                <TablePagination
                    rowsPerPageOptions={[10, 25, 100]}
                    component="div"
                    count={10}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onPageChange={handleChangePage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                />
            </div>
        </>
    )
}

export default HomeSliderBanners