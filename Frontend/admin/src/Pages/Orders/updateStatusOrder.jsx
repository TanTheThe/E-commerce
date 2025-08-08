import React, { useState } from "react";
import Button from "@mui/material/Button";
import { FaCheck, FaTimes } from "react-icons/fa";

const OrderStatusUpdateModal = ({ open, onClose, order, onUpdateStatus }) => {
    const [selectedStatus, setSelectedStatus] = useState(order?.status || "");
    const [isUpdating, setIsUpdating] = useState(false);

    const statusOptions = [
        { value: "Pending", label: "Pending", color: "bg-red-500", description: "Đơn hàng đang chờ xử lý" },
        { value: "Confirm", label: "Confirmed", color: "bg-yellow-500", description: "Đơn hàng đã được xác nhận" },
        { value: "Processing", label: "Processing", color: "bg-blue-500", description: "Đơn hàng đang được xử lý" },
        { value: "Shipped", label: "Shipped", color: "bg-purple-500", description: "Đơn hàng đã được giao cho đơn vị vận chuyển" },
        { value: "Delivered", label: "Delivered", color: "bg-green-700", description: "Đơn hàng đã được giao thành công" },
        { value: "Cancelled", label: "Cancelled", color: "bg-gray-500", description: "Đơn hàng đã bị hủy" }
    ];

    const handleUpdateStatus = async () => {
        if (!selectedStatus || selectedStatus === order?.status) {
            return;
        }

        setIsUpdating(true);
        try {
            await onUpdateStatus(order.id, selectedStatus);
            onClose();
        } catch (error) {
            console.error("Lỗi cập nhật trạng thái:", error);
        } finally {
            setIsUpdating(false);
        }
    };

    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/50 backdrop-blur-sm"
                onClick={onClose}
            ></div>

            {/* Modal */}
            <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 transform transition-all">
                {/* Header */}
                <div className="bg-gradient-to-r from-white-600 to-gray-500 p-6 rounded-t-xl text-white">
                    <h3 className="text-xl font-bold text-gray-700">Update Order Status</h3>
                    <p className="text-sm mt-1 text-black">Order Code: {order?.code}</p>
                </div>

                {/* Content */}
                <div className="p-6">
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-3">
                            Select New Status
                        </label>
                        <div className="space-y-3">
                            {statusOptions.map((status) => (
                                <div
                                    key={status.value}
                                    className={`relative flex items-center p-3 rounded-lg border-2 cursor-pointer transition-all ${selectedStatus === status.value
                                            ? 'border-blue-500 bg-blue-50'
                                            : 'border-gray-200 hover:border-gray-300'
                                        }`}
                                    onClick={() => setSelectedStatus(status.value)}
                                >
                                    <input
                                        type="radio"
                                        name="status"
                                        value={status.value}
                                        checked={selectedStatus === status.value}
                                        onChange={() => setSelectedStatus(status.value)}
                                        className="sr-only"
                                    />

                                    <div className="flex items-center flex-1">
                                        <div className={`w-4 h-4 rounded-full ${status.color} mr-3`}></div>
                                        <div>
                                            <div className="font-medium text-gray-900">{status.label}</div>
                                            <div className="text-xs text-gray-500">{status.description}</div>
                                        </div>
                                    </div>

                                    {selectedStatus === status.value && (
                                        <FaCheck className="text-blue-500 ml-2" />
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Current Status Info */}
                    <div className="bg-gray-50 p-3 rounded-lg mb-4">
                        <div className="text-xs text-gray-500 mb-1">Current Status</div>
                        <div className="flex items-center">
                            <div className={`w-3 h-3 rounded-full mr-2 ${statusOptions.find(s => s.value === order?.status)?.color || 'bg-gray-400'
                                }`}></div>
                            <span className="text-sm font-medium">{order?.status}</span>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="flex justify-end gap-3 p-6 border-t border-gray-200">
                    <Button
                        onClick={onClose}
                        className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                        disabled={isUpdating}
                    >
                        <FaTimes className="mr-2" />
                        Cancel
                    </Button>
                    <Button
                        onClick={handleUpdateStatus}
                        disabled={isUpdating || !selectedStatus || selectedStatus === order?.status}
                        className={`px-4 py-2 text-white rounded-lg transition-colors ${isUpdating || !selectedStatus || selectedStatus === order?.status
                                ? 'bg-gray-400 cursor-not-allowed'
                                : 'bg-blue-600 hover:bg-blue-700'
                            }`}
                    >
                        <FaCheck className="mr-2" />
                        {isUpdating ? 'Updating...' : 'Update Status'}
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default OrderStatusUpdateModal