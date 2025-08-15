import { useState, useRef } from "react";
import { HexColorPicker } from "react-colorful";
import { Button, Popover, TextField } from "@mui/material";
import { MdColorLens } from "react-icons/md";

const ColorPicker = ({ color = "", onChange }) => {
    const [anchorEl, setAnchorEl] = useState(null);

    const handleOpen = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleColorChange = (newColor) => {
        if (onChange) {
            onChange(newColor);
        }
    };

    const handleClearColor = () => {
        if (onChange) onChange('');
    };

    const open = Boolean(anchorEl);

    return (
        <div className="col">
            <h3 className="text-[14px] font-[500] mb-0.5">Override màu</h3>
            <div className="flex items-center gap-2">
                <TextField
                    value={color ?? ''}
                    placeholder="None"
                    onChange={(e) => {
                        const val = e.target.value;
                        onChange(val === '' ? null : val);
                    }}
                    size="small"
                    style={{ width: "150px" }}
                    className="bg-white"
                />
                <Button
                    className="btn-color-picker"
                    size="medium"
                    onClick={handleOpen}
                    startIcon={<MdColorLens />}
                    style={{ backgroundColor: color || "#ddd", color: "#000" }}
                >
                    Chọn
                </Button>
                {color && (
                    <Button
                        className="btn-color-remove px-4"
                        onClick={handleClearColor}
                    >
                        Xóa màu
                    </Button>

                )}
            </div>

            <Popover
                open={open}
                anchorEl={anchorEl}
                onClose={handleClose}
                anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
            >
                <div style={{ padding: 16 }}>
                    <HexColorPicker
                        color={color ?? "#000000"}
                        onChange={(newColor) => onChange(newColor)}
                    />
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handleClose}
                        size="small"
                        style={{ marginTop: 10 }}
                    >
                        OK
                    </Button>
                </div>
            </Popover>
        </div>
    );
}

export default ColorPicker