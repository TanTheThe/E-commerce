import React, { useState, useRef } from 'react';
import { FiX, FiUpload, FiTrash2, FiCheck } from 'react-icons/fi';
import { toast } from 'react-toastify';

const ReturnModal = ({
    isOpen,
    onClose,
    selectedOrder,
    onSubmit,
    returnForm,
    setReturnForm
}) => {
    const fileInputRef = useRef(null);

    if (!isOpen || !selectedOrder) return null;

    const handleImageUpload = (event, orderDetailId) => {
        const files = Array.from(event.target.files);

        files.forEach(file => {
            if (!file.type.startsWith('image/')) {
                toast.error('Vui lòng chỉ tải lên file ảnh');
                return;
            }

            if (file.size > 5 * 1024 * 1024) {
                toast.error('Kích thước ảnh không được vượt quá 5MB');
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                const imageData = {
                    url: URL.createObjectURL(file),
                    base64: e.target.result,
                    file: file,
                    name: file.name
                };

                setReturnForm(prev => ({
                    ...prev,
                    return_items: prev.return_items.map(item =>
                        item.order_detail_id === orderDetailId
                            ? {
                                ...item,
                                images: [...(item.images || []), imageData]
                            }
                            : item
                    )
                }));
            };
            reader.readAsDataURL(file);
        });

        event.target.value = '';
    };

    const handleRemoveImage = (orderDetailId, imageIndex) => {
        setReturnForm(prev => {
            const updatedItems = prev.return_items.map(item => {
                if (item.order_detail_id === orderDetailId) {
                    const imageToRemove = item.images[imageIndex];
                    if (imageToRemove?.url) {
                        URL.revokeObjectURL(imageToRemove.url);
                    }
                    return {
                        ...item,
                        images: item.images.filter((_, i) => i !== imageIndex)
                    };
                }
                return item;
            });

            return {
                ...prev,
                return_items: updatedItems
            };
        });
    };

    const handleItemToggle = (orderDetailId) => {
        setReturnForm(prev => ({
            ...prev,
            return_items: prev.return_items.map(item =>
                item.order_detail_id === orderDetailId
                    ? { ...item, selected: !item.selected }
                    : item
            )
        }));
    };

    const handleQuantityChange = (orderDetailId, newQuantity) => {
        setReturnForm(prev => ({
            ...prev,
            return_items: prev.return_items.map(item => {
                if (item.order_detail_id === orderDetailId) {
                    const originalQuantity = returnForm.return_items.find(ri => ri.order_detail_id === orderDetailId)?.quantity || item.quantity;

                    return {
                        ...item,
                        quantity: Math.max(1, Math.min(newQuantity, originalQuantity))
                    };
                }
                return item;
            })
        }));
    };

    const handleReasonChange = (reason) => {
        setReturnForm(prev => ({
            ...prev,
            reason
        }));
    };

    const handleNoteChange = (note) => {
        setReturnForm(prev => ({
            ...prev,
            note
        }));
    };

    const selectedItemsCount = returnForm.return_items.filter(item => item.selected).length;
    const allSelectedItemsHaveEnoughImages = returnForm.return_items
        .filter(item => item.selected)
        .every(item => item.images && item.images.length >= 5);
    const isFormValid = returnForm.reason && selectedItemsCount > 0 && allSelectedItemsHaveEnoughImages;

    const returnReasons = [
        'Sản phẩm bị lỗi/hỏng',
        'Sản phẩm không đúng mô tả',
        'Sản phẩm không đúng size',
        'Nhận được sản phẩm sai',
        'Chất lượng không như mong đợi',
        'Lý do khác'
    ];

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.6)' }}>
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <h2 className="text-2xl font-bold text-gray-800">Yêu cầu trả hàng</h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-100 rounded-full transition-colors cursor-pointer"
                    >
                        <FiX className="text-xl text-gray-600" />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    <div className="bg-gray-50 p-4 rounded-lg">
                        <h3 className="font-semibold text-gray-800 mb-2">Thông tin đơn hàng</h3>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <span className="text-gray-600">Mã đơn hàng:</span>
                                <span className="font-medium text-[#ff5252] ml-2">#{selectedOrder.order.code}</span>
                            </div>
                            <div>
                                <span className="text-gray-600">Ngày đặt:</span>
                                <span className="font-medium ml-2">
                                    {new Date(selectedOrder.order.created_at).toLocaleDateString('vi-VN')}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-3">
                            Lý do trả hàng <span className="text-red-500">*</span>
                        </label>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {returnReasons.map((reason) => (
                                <label key={reason} className="flex items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                                    <input
                                        type="radio"
                                        name="return_reason"
                                        value={reason}
                                        checked={returnForm.reason === reason}
                                        onChange={(e) => handleReasonChange(e.target.value)}
                                        className="mr-3 text-[#ff5252] focus:ring-[#ff5252]"
                                    />
                                    <span className="text-sm">{reason}</span>
                                </label>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Ghi chú thêm
                        </label>
                        <textarea
                            value={returnForm.note}
                            onChange={(e) => handleNoteChange(e.target.value)}
                            placeholder="Mô tả chi tiết về tình trạng sản phẩm..."
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#ff5252] focus:border-transparent"
                            rows={3}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-3">
                            Chọn sản phẩm cần trả <span className="text-red-500">*</span>
                        </label>
                        <div className="space-y-3">
                            {returnForm.return_items.map((returnItem) => {
                                return (
                                    <div key={returnItem.order_detail_id} className={`border rounded-lg p-4 ${returnItem.selected ? 'border-[#ff5252] bg-red-50' : 'border-gray-200'}`}>
                                        <div className="flex items-start gap-4">
                                            <div className="flex items-center">
                                                <input
                                                    type="checkbox"
                                                    checked={returnItem.selected}
                                                    onChange={() => handleItemToggle(returnItem.order_detail_id)}
                                                    className="w-4 h-4 text-[#ff5252] focus:ring-[#ff5252] border-gray-300 rounded cursor-pointer"
                                                />
                                            </div>

                                            <div className="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                                                <img
                                                    src={returnItem.product_image}
                                                    alt={returnItem.product_name}
                                                    className="w-full h-full object-cover"
                                                />
                                            </div>

                                            <div className="flex-1">
                                                <h4 className="font-medium text-gray-800 mb-1">{returnItem.product_name}</h4>
                                                <div className="text-sm text-gray-600 mb-2">
                                                    <span>Size: {returnItem.size}</span>
                                                    <span className="mx-2">•</span>
                                                    <span>Màu: {returnItem.color_name}</span>
                                                </div>
                                                <div className="flex items-center gap-4">
                                                    <span className="text-lg font-bold text-[#ff5252]">
                                                        {returnItem.price_after_discount?.toLocaleString('vi-VN')}đ
                                                    </span>
                                                    {returnItem.selected && (
                                                        <div className="mt-3 space-y-3">
                                                            <div className="flex items-center gap-2">
                                                                <span className="text-sm text-gray-600">Số lượng:</span>
                                                                <div className="flex items-center gap-1">
                                                                    <button
                                                                        onClick={() => handleQuantityChange(returnItem.order_detail_id, returnItem.quantity - 1)}
                                                                        className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100 cursor-pointer"
                                                                        disabled={returnItem.quantity <= 1}
                                                                    >
                                                                        -
                                                                    </button>
                                                                    <input
                                                                        type="number"
                                                                        value={returnItem.quantity}
                                                                        onChange={(e) => handleQuantityChange(returnItem.order_detail_id, parseInt(e.target.value) || 1)}
                                                                        className="w-16 text-center border border-gray-300 rounded px-2 py-1"
                                                                        min={1}
                                                                    />
                                                                    <button
                                                                        onClick={() => handleQuantityChange(returnItem.order_detail_id, returnItem.quantity + 1)}
                                                                        className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100 cursor-pointer"
                                                                    >
                                                                        +
                                                                    </button>
                                                                </div>
                                                            </div>

                                                            <div>
                                                                <label className="block text-xs font-medium text-gray-700 mb-2">
                                                                    Hình ảnh sản phẩm <span className="text-red-500">*</span>
                                                                    <span className="text-gray-500 font-normal"> (Tối thiểu 5 ảnh)</span>
                                                                </label>

                                                                <div className="border-2 border-dashed border-gray-300 rounded-lg p-3 text-center hover:border-[#ff5252] transition-colors">
                                                                    <input
                                                                        type="file"
                                                                        multiple
                                                                        accept="image/*"
                                                                        onChange={(e) => handleImageUpload(e, returnItem.order_detail_id)}
                                                                        className="hidden"
                                                                        id={`file-input-${returnItem.order_detail_id}`}
                                                                    />
                                                                    <FiUpload className="mx-auto text-lg text-gray-400 mb-1" />
                                                                    <button
                                                                        type="button"
                                                                        onClick={() => document.getElementById(`file-input-${returnItem.order_detail_id}`)?.click()}
                                                                        className="text-xs px-3 py-1 bg-[#ff5252] text-white rounded hover:bg-[#e53e3e] transition-colors cursor-pointer"
                                                                    >
                                                                        Chọn ảnh
                                                                    </button>
                                                                </div>

                                                                {returnItem.images && returnItem.images.length > 0 && (
                                                                    <div className="mt-2">
                                                                        <div className="grid grid-cols-5 gap-2">
                                                                            {returnItem.images.map((image, imageIndex) => (
                                                                                <div key={imageIndex} className="relative group">
                                                                                    <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                                                                                        <img
                                                                                            src={image.url}
                                                                                            alt={`Preview ${imageIndex + 1}`}
                                                                                            className="w-full h-full object-cover"
                                                                                        />
                                                                                    </div>
                                                                                    <button
                                                                                        onClick={() => handleRemoveImage(returnItem.order_detail_id, imageIndex)}
                                                                                        className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                                                                                    >
                                                                                        <FiX className="text-xs" />
                                                                                    </button>
                                                                                </div>
                                                                            ))}
                                                                        </div>
                                                                        <p className="text-xs text-gray-600 mt-1">
                                                                            {returnItem.images.length}/5 ảnh tối thiểu
                                                                        </p>
                                                                        {returnItem.images.length < 5 && (
                                                                            <p className="text-red-500 text-xs mt-1">
                                                                                Vui lòng tải lên ít nhất 5 ảnh cho sản phẩm này
                                                                            </p>
                                                                        )}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                        {selectedItemsCount === 0 && (
                            <p className="text-red-500 text-sm mt-2">Vui lòng chọn ít nhất một sản phẩm để trả hàng</p>
                        )}
                    </div>

                </div>

                <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
                    <div className="text-sm text-gray-600">
                        {selectedItemsCount > 0 && (
                            <span>Đã chọn {selectedItemsCount} sản phẩm</span>
                        )}
                    </div>

                    <div className="flex gap-3">
                        <button
                            onClick={onClose}
                            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                        >
                            Hủy bỏ
                        </button>
                        <button
                            onClick={onSubmit}
                            disabled={!isFormValid}
                            className={`px-6 py-2 rounded-lg transition-colors ${isFormValid
                                ? 'bg-[#ff5252] text-white hover:bg-[#e53e3e] cursor-pointer'
                                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                }`}
                        >
                            <div className="flex items-center gap-2">
                                <FiCheck className="text-sm" />
                                <span>Gửi yêu cầu</span>
                            </div>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ReturnModal;