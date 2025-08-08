import React, { useState } from "react";
import { IoCloseSharp } from "react-icons/io5";
import { Link } from "react-router-dom";
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import { GoTriangleDown } from "react-icons/go";
import { Rating } from "@mui/material";
import Button from "@mui/material/Button";

const MyListItems = (props) => {
    

    return (
        <div className="cartItem w-full p-3 flex items-center gap-4 pb-5 border-b border-[rgba(0,0,0,0.1)]">
            <div className="img w-[15%] rounded-md overflow-hidden">
                <Link to="/product/7845" className="group">
                    <img src="https://api.spicezgold.com/download/file_1734690981297_011618e4-4682-4123-be80-1fb7737d34ad1714702040213RARERABBITMenComfortOpaqueCasualShirt1.jpg" className="w-full group-hover:scale-105 transition-all" />
                </Link>
            </div>

            <div className="info w-[85%] relative">
                <IoCloseSharp className="cursor-pointer absolute top-[0px] right-[0px] text-[22px] link transition-all" />
                <span className="text-[13px]">Sangria</span>
                <h3 className="text-[15px]">
                    <Link className="link">A-Line Kurti With Sharara & Dupatta</Link>
                </h3>

                <Rating name="size-small" defaultValue={4} size="small" readOnly />

                <div className="flex items-center gap-4 mt-2 mb-2">
                    <span className="oldPrice text-[14px] text-black font-[600]">$58.00</span>
                    <span className="oldPrice line-through text-gray-500 text-[14px] font-[500]">$58.00</span>
                    <span className="oldPrice text-[14px] text-[#ff5252] font-[600]">55% OFF</span>
                </div>

                <Button className="btn-org btn-sm">Add to Cart</Button>
            </div>
        </div>
    )
}

export default MyListItems