import React, { useContext, useEffect, useState } from "react";
import { Dialog, DialogTitle, DialogContent, Button, IconButton } from "@mui/material";
import { IoMdClose } from "react-icons/io";
import { FaPlus } from "react-icons/fa";
import { LazyLoadImage } from "react-lazy-load-image-component";
import dayjs from "dayjs"
import { putDataApi } from "../../utils/api";
import { MyContext } from "../../App";

const EditSpecialOffer = ({ open, onClose, offer, onSuccess }) => {
    const [formFields, setFormFields] = useState({
        name: "",
        total_quantity: "",
        discount: "",
        condition: "",
        type: "",
        scope: "",
        start_time: "",
        end_time: ""
    });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isLocked, setIsLocked] = useState(false);
    const context = useContext(MyContext)

    useEffect(() => {
        if (offer) {
            const formatTime = (timeStr) => dayjs(timeStr).format("YYYY-MM-DDTHH:mm");

            setFormFields({
                name: offer.name,
                total_quantity: offer.total_quantity,
                discount: offer.discount,
                condition: offer.condition,
                type: offer.type,
                scope: offer.scope,
                start_time: formatTime(offer.start_time),
                end_time: formatTime(offer.end_time)
            });

            setIsLocked(offer.used_quantity > 0);
        }
    }, [offer]);

    const onChangeInput = (e) => {
        const { name, value } = e.target;
        setFormFields((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setIsSubmitting(true);
            const payload = {
                ...formFields,
                start_time: new Date(formFields.start_time).toISOString(),
                end_time: new Date(formFields.end_time).toISOString(),
            };
            const response = await putDataApi(`/admin/special-offer/${offer.id}`, payload);
            if (response.success) {
                context.openAlertBox("success", response.message);
                onSuccess?.();
                onClose();
            } else {
                context.openAlertBox("error", response.data.detail.message || "Có lỗi xảy ra khi cập nhật khuyến mãi");
            }
        } catch (err) {
            console.error(err);
            context.openAlertBox("error", "Có lỗi xảy ra khi cập nhật khuyến mãi");
        } finally {
            setIsSubmitting(false);
        }
    };

    const renderInput = (label, name, placeholder, type = "text") => {
        const isEditable = !isLocked || name === "name" || name === "end_time";
        return (
            <div className="mb-4">
                <label className="block text-sm font-medium mb-1">{label}</label>
                <input
                    type={type}
                    name={name}
                    value={formFields[name]}
                    onChange={onChangeInput}
                    className={`w-full border p-2 rounded transition-all duration-200 ${isEditable ? "" : "bg-gray-100 opacity-70 cursor-not-allowed"
                        }`}
                    placeholder={placeholder}
                    disabled={!isEditable}
                />
            </div>
        );
    };

    const renderSelect = (label, name, options, isEditable = true) => {
        const canEdit = !isLocked || name === "name" || name === "end_time";
        const finalEditable = isEditable && canEdit;

        return (
            <div className="mb-4">
                <label className="block text-sm font-medium mb-1">{label}</label>
                <select
                    name={name}
                    value={formFields[name]}
                    onChange={onChangeInput}
                    className={`w-full border p-2 rounded transition-all duration-200 ${finalEditable ? "" : "bg-gray-100 opacity-70 cursor-not-allowed"}`}
                    disabled={!finalEditable}
                >
                    {options.map(option => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </select>
            </div>
        );
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle>
                Cập nhật khuyến mãi
                <IconButton onClick={onClose} style={{ float: 'right' }}>
                    <IoMdClose />
                </IconButton>
            </DialogTitle>
            <DialogContent>
                <form onSubmit={handleSubmit}>
                    {renderInput("Tên", "name", "Nhập tên khuyến mãi...")}
                    {renderInput("Tổng số lượng", "total_quantity", "Nhập tổng số lượng...")}
                    {renderInput("Mức giảm giá", "discount", "Nhập mức giảm giá...")}

                    {renderSelect("Loại", "type", [
                        { value: "percent", label: "Phần trăm" },
                        { value: "fixed", label: "Giảm tiền cố định" }
                    ])}

                    {renderSelect("Phạm vi áp dụng", "scope", [
                        { value: "order", label: "Đơn hàng" },
                        { value: "product", label: "Sản phẩm" }
                    ])}

                    {formFields.scope === 'order' && renderInput("Điều kiện", "condition", "Nhập điều kiện giảm giá...")}

                    {renderInput("Thời gian bắt đầu", "start_time", "Chọn thời gian bắt đầu...", "datetime-local")}
                    {renderInput("Thời gian kết thúc", "end_time", "Chọn thời gian kết thúc...", "datetime-local")}

                    <br />

                    <Button type="submit" disabled={isSubmitting} variant="contained" fullWidth>
                        {isSubmitting ? "Đang cập nhật..." : "Cập nhật khuyến mãi"}
                    </Button>
                </form>
            </DialogContent>
        </Dialog>
    );
};

export default EditSpecialOffer;
