import React, { useEffect, useState } from "react";
import Button from "@mui/material/Button";
import { RiMenu2Fill } from "react-icons/ri";
import { LiaAngleDownSolid } from "react-icons/lia";
import { Link } from "react-router-dom";
import { GoRocket } from "react-icons/go";
import CategoryPanel from "./CategoryPanel";
import "../Navigation/style.css"
import { getDataApi } from "../../../utils/api";

const Navigation = ({ categories }) => {
    const parentCategories = categories.filter(category => category.parent_id === null);

    return (
        <>
            <nav className="py-2">
                <div className="container flex items-center justify-end">
                    <div className="w-[80%]">
                        <ul className="flex items-center gap-1 nav">
                            {
                                parentCategories.map((category) => (
                                    <li key={category.id} className="list-none">
                                        <Link to={`/category/${category.id}`} className="link transition text-[14px] font-[500] pr-3">
                                            <Button className="link transition !font-[600]">{category.name}</Button>
                                        </Link>
                                    </li>
                                ))
                            }
                        </ul>
                    </div>

                    <div className="col_3 w-[20%]">
                        <p className="text-[14px] font-[500] flex items-center gap-3 mb-0 mt-0 ml-5">
                            <GoRocket className="text-[18px]" />
                            Free International Delivery
                        </p>
                    </div>
                </div>
            </nav>
        </>
    )
}

export default Navigation