import { Button } from "@mui/material";
import React, { useState } from "react";
import { FaAngleDown, FaAngleUp } from "react-icons/fa";

const QtyBox = ({ value, onChange, max, disabled }) => {
    const plusQty = () => {
        if (!disabled && value < max) {
            onChange(value + 1);
        }
    }

    const minusQty = () => {
        if (!disabled && value > 1) {
            onChange(value - 1);
        }
    }

    const handleInputChange = (e) => {
        if (!disabled) {
            const val = parseInt(e.target.value) || 1;
            const clampedVal = Math.min(max, Math.max(1, val));
            onChange(clampedVal);
        }
    }

    return (
        <div className="qtyBox flex items-center relative">
            <input
                type="number"
                className="w-full h-[45px] p-2 pl-5 text-[15px] focus:outline-none border border-[rgba(0,0,0,0.2)] rounded-md"
                value={value}
                onChange={handleInputChange}
                min="1"
                max={max}
                disabled={disabled}
            />

            <div className="flex items-center flex-col justify-between h-[40px] absolute top-0 right-0 z-50">
                <Button
                    className={`!min-w-[30px] !w-[30px] !h-[22px] !text-[#000] !rounded-none hover:!bg-[#f1f1f1] ${disabled ? '!opacity-50 !cursor-not-allowed' : ''}`}
                    onClick={plusQty}
                    disabled={disabled || value >= max}
                >
                    <FaAngleUp className="text-[12px] opacity-55" />
                </Button>
                <Button
                    className={`!min-w-[30px] !w-[30px] !h-[22px] !text-[#000] !rounded-none hover:!bg-[#f1f1f1] ${disabled ? '!opacity-50 !cursor-not-allowed' : ''}`}
                    onClick={minusQty}
                    disabled={disabled || value <= 1}
                >
                    <FaAngleDown className="text-[12px] opacity-55" />
                </Button>
            </div>
        </div>
    )
}

export default QtyBox