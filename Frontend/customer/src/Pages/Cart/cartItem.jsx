import React, { useContext, useState } from "react";
import { MyContext } from "../../App";
import { MdOutlineDeleteOutline } from 'react-icons/md';

const CartItems = () => {
    const {
        checkoutItems,
    } = useContext(MyContext);

    if (!checkoutItems || checkoutItems.length === 0) {
        return (
            <div className="py-8 px-4 text-center text-gray-500">
                Chưa có sản phẩm nào được chọn để thanh toán
            </div>
        );
    }

    return (
        <div className="py-3 px-4">
            {checkoutItems.map((item, index) => (
                <div
                    key={item.cart_item_id}
                    className={`cartItem w-full flex items-center gap-4 pb-4 mb-4 ${index < checkoutItems.length - 1 ? 'border-b border-gray-100' : ''
                        }`}
                >
                    <div className="img w-[25%] overflow-hidden h-[80px] rounded-md">
                        <img
                            src={item.image || '/default-product.jpg'}
                            alt={`${item.product_name} - ${item.size} ${item.color_name}`}
                            className='w-full h-full object-cover'
                        />
                    </div>

                    <div className='info w-[75%] pr-5'>
                        <h4 className="text-[14px] font-[600] text-gray-800 mb-1">
                            {item.product_name}
                        </h4>

                        <div className="text-[13px] text-gray-600 mb-2 flex gap-3">
                            {item.size && <span>Size: <strong>{item.size}</strong></span>}
                            {item.color_name && <span>Màu: <strong>{item.color_name}</strong></span>}
                        </div>

                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                                <span className="text-[12px] text-gray-500">Số lượng:</span>
                                <span className="mx-2 min-w-[30px] text-center font-semibold">{item.quantity}</span>
                            </div>
                            <div className="text-right">
                                <div className="text-[14px] text-[#ff5252] font-bold">
                                    {item.unit_price?.toLocaleString('vi-VN')}đ
                                </div>
                                <div className="text-[12px] text-gray-500">
                                    Tổng: {(item.unit_price * item.quantity)?.toLocaleString('vi-VN')}đ
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default CartItems;