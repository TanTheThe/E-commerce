import React from "react";
import {IoIosArrowForward, IoMdTime} from "react-icons/io"
import { Link } from "react-router-dom";


const BlogItem = () => {
    return (
        <div className="blogItem group">
            <div className="imgWrapper w-full overflow-hidden rounded-md cursor-pointer">
                <img src="banner_5.png" className="w-full transition-all group-hover:scale-105 group-hover:rotate-1"/>

                <span className="flex items-center justify-center text-white absolute bottom-[15px] right-[15px] z-50 bg-[#ff5252] rounded-md p-1 text-[11px] font-[500] gap-1">
                    <IoMdTime className="text-[16px]"/> 5 APRIL, 2023
                </span>
            </div>

            <div className="info py-4">
                <h2 className="text-[16px] font-[600] text-black">
                    <Link to="/" className="link">Learn How To Create Full Stack</Link>
                </h2>
                <p className="text-[13px] font-[400] text-[rgba(0,0,0,0.8)] mb-4">In this single tutorial we will make a full stack eCommerce website using ....</p>

                <Link className="link font-[500] text-[14px] flex items-center gap-1">Read More <IoIosArrowForward/></Link>
            </div>
        </div>
    )
}

export default BlogItem