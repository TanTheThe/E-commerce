import React, { useContext } from "react";
import "../ProductItem/style.css"
import { Link } from "react-router-dom";
import Rating from '@mui/material/Rating';
import {FaRegHeart} from "react-icons/fa"
import {IoGitCompareOutline} from "react-icons/io5"
import {MdZoomOutMap} from "react-icons/md"
import Button from "@mui/material/Button";
import { MyContext } from "../../App";

const ProductItem = () => {
    const context = useContext(MyContext)

    return (
        <div className="productItem shadow-lg rounded-md overflow-hidden border-1 border-[rgba(0,0,0,0.1)]">
            <div className="group imgWrapper w-[100%] overflow-hidden rounded-md relative">
                <Link to="/">
                    <div className="img h-[250px] overflow-hidden">
                        <img className="w-full" src="https://api.spicezgold.com/download/file_1734690981297_011618e4-4682-4123-be80-1fb7737d34ad1714702040213RARERABBITMenComfortOpaqueCasualShirt1.jpg"/>
                        <img className="w-full transition-all duration-700 absolute top-0 left-0 opacity-0 group-hover:opacity-100 group-hover:scale-105" src="https://api.spicezgold.com/download/file_1734690981297_23990e6b-d01e-40fd-bb6b-98198db544c01714702040162RARERABBITMenComfortOpaqueCasualShirt2.jpg"/>    
                    </div>
                </Link>

                <span className="discount flex items-center absolute top-[10px] left-[10px] z-50 bg-[#ff5252] text-white rounded-lg p-1 text-[12px] font-[500]">10%</span>

                <div className="actions absolute top-[-200px] right-[5px] z-50 flex items-center gap-2 flex-col w-[50px] transition-all duration-300 group-hover:top-[15px] opacity-0
                group-hover:opacity-100">
                    <Button className="!w-[35px] !h-[35px] !min-w-[35px] !rounded-full !bg-white text-black hover:!bg-[#ff5252] hover:text-white group"
                    onClick={() => context.setOpenProductDetailsModal(true)}>
                        <MdZoomOutMap className="text-[18px] !text-black group-hover:text-white hover:!text-white"/>
                    </Button>

                    <Button className="!w-[35px] !h-[35px] !min-w-[35px] !rounded-full !bg-white text-black hover:!bg-[#ff5252] hover:text-white group">
                        <IoGitCompareOutline className="text-[18px] !text-black group-hover:text-white hover:!text-white"/>
                    </Button>

                    <Button className="!w-[35px] !h-[35px] !min-w-[35px] !rounded-full !bg-white text-black hover:!bg-[#ff5252] hover:text-white group">
                        <FaRegHeart className="text-[18px] !text-black group-hover:text-white hover:!text-white"/>
                    </Button>
                </div>
            </div>

            <div className="info p-3 py-5">
                <h6 className="text-[13px] !font-[400]">
                    <Link to="/" className="link">
                        Soylent Green
                    </Link>
                </h6>
                <h3 className="text-[13px] title mt-1 font-[500] mb-1 text-[#000]">
                    <Link to="/" className="link transition-all">
                        Siril Georgette Pink Color Saree with Blouse Piece
                    </Link>
                </h3>
                <Rating name="size-small" defaultValue={2} size="small" readOnly />

                <div className="flex items-center gap-4">
                    <span className="oldPrice line-through text-gray-500 text-[15px] font-[500]">$58.00</span>
                    <span className="oldPrice text-[#ff5252] font-[600]">$58.00</span>
                </div>
            </div>
        </div>
    )
}

export default ProductItem