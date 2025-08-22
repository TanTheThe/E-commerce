import React, { useContext, useEffect, useState } from "react";
import UploadBox from "../../Components/UploadBox";
import { LazyLoadImage } from "react-lazy-load-image-component";
import 'react-lazy-load-image-component/src/effects/blur.css';
import { IoMdClose } from "react-icons/io";
import Button from "@mui/material/Button";
import { FaCloudUploadAlt, FaPlus } from "react-icons/fa";
import { postDataApi } from "../../utils/api";
import { MyContext } from "../../App";
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import IconButton from '@mui/material/IconButton';

const AddSpecialOffer = ({ open, onClose, onSuccess }) => {
    const [formFields, setFormFields] = useState({
        name: "",
        total_quantity: "",
        discount: "",
        condition: "",
        type: "percent",
        scope: "order",
        start_time: "",
        end_time: ""
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const context = useContext(MyContext)

    const onChangeInput = (e) => {
        const { name, value } = e.target;
        setFormFields(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        try {
            const { name, total_quantity, discount, condition, type, scope, start_time, end_time } = formFields;

            const offerData = {
                name: name.trim(),
                total_quantity: parseInt(total_quantity),
                discount: parseFloat(discount),
                condition: parseFloat(condition),
                type: type,
                scope: scope,
                start_time: new Date(start_time).toISOString(),
                end_time: new Date(end_time).toISOString()
            };

            const response = await postDataApi('/admin/special-offer', offerData);

            if (response.success) {
                context.openAlertBox(
                    "success", response?.message
                )
                onSuccess && onSuccess();
                setFormFields({
                    name: "",
                    total_quantity: "",
                    discount: "",
                    condition: "",
                    type: "percent",
                    scope: "order",
                    start_time: "",
                    end_time: ""
                });
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || "Có lỗi trong quá trình tạo khuyến mãi")
            }
        } catch (error) {
            console.error("Error submitting form:", error);
            context.openAlertBox("error", "Có lỗi hệ thống khi tạo khuyến mãi!")
        }
        setIsSubmitting(false);
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle>
                Tạo ưu đãi mới
                <IconButton onClick={onClose} style={{ float: 'right' }}>
                    <IoMdClose />
                </IconButton>
            </DialogTitle>
            <DialogContent>
                <form onSubmit={handleSubmit}>
                    <div>
                        <label className="block text-sm font-medium mb-1">Tên ưu đãi</label>
                        <input
                            type="text"
                            name="name"
                            value={formFields.name}
                            onChange={onChangeInput}
                            className="w-full border p-2 rounded"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1 mt-4">Phạm vi áp dụng</label>
                        <select
                            name="scope"
                            value={formFields.scope}
                            onChange={onChangeInput}
                            className="w-full border p-2 rounded"
                        >
                            <option value="order">Đơn hàng</option>
                            <option value="product">Sản phẩm</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1 mt-4">Tổng số lượng</label>
                        <input
                            type="number"
                            name="total_quantity"
                            value={formFields.total_quantity}
                            onChange={onChangeInput}
                            className="w-full border p-2 rounded"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1 mt-4">Giảm giá</label>
                        <input
                            type="number"
                            step="0.01"
                            name="discount"
                            value={formFields.discount}
                            onChange={onChangeInput}
                            className="w-full border p-2 rounded"
                            required
                        />
                    </div>
                    {formFields.scope === 'order' && (
                        <div>
                            <label className="block text-sm font-medium mb-1 mt-4">Điều kiện áp dụng (tổng đơn hàng tối thiểu)</label>
                            <input
                                type="number"
                                step="0.01"
                                name="condition"
                                value={formFields.condition}
                                onChange={onChangeInput}
                                className="w-full border p-2 rounded"
                            />
                        </div>
                    )}
                    <div>
                        <label className="block text-sm font-medium mb-1 mt-4">Loại ưu đãi</label>
                        <select
                            name="type"
                            value={formFields.type}
                            onChange={onChangeInput}
                            className="w-full border p-2 rounded"
                        >
                            <option value="percent">Phần trăm</option>
                            <option value="fixed">Giảm tiền cố định</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1 mt-4">Thời gian bắt đầu</label>
                        <input
                            type="datetime-local"
                            name="start_time"
                            value={formFields.start_time}
                            onChange={onChangeInput}
                            className="w-full border p-2 rounded"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1 mt-4">Thời gian kết thúc</label>
                        <input
                            type="datetime-local"
                            name="end_time"
                            value={formFields.end_time}
                            onChange={onChangeInput}
                            className="w-full border p-2 rounded"
                            required
                        />
                    </div>

                    <div className="mt-8"></div>

                    <Button type="submit" disabled={isSubmitting} variant="contained" fullWidth>
                        {isSubmitting ? "Đang tạo..." : "Tạo ưu đãi"}
                    </Button>
                </form>
            </DialogContent>
        </Dialog>
    )
}

export default AddSpecialOffer