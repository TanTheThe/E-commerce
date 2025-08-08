import React from "react";
import Button from "@mui/material/Button";
import Badge from "../../Components/Badge";

const OrderDetailOffcanvas = ({ open, onClose, order }) => {
    const { order: orderInfo, customer, address, order_detail } = order || {};

    return (
        <div className={`fixed inset-0 z-50 ${open ? 'visible' : 'invisible'}`}>
            {/* Backdrop với hiệu ứng blur */}
            <div
                className={`fixed inset-0 bg-black/40 backdrop-blur-sm transition-all duration-300 ${open ? 'opacity-100' : 'opacity-0'}`}
                onClick={onClose}
            ></div>

            {/* Main Panel */}
            <div
                className={`fixed right-0 top-0 h-full w-[650px] bg-white shadow-2xl transform transition-transform duration-300 ${open ? 'translate-x-0' : 'translate-x-full'}`}
            >
                {/* Header với gradient */}
                <div className="bg-gradient-to-r from-white-600 to-gray-500 p-6 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-2xl font-bold text-gray-700">Order Details</h2>
                            <p className="text-sm mt-1 text-black">Complete order information</p>
                        </div>
                        <Button 
                            className="!w-10 !h-10 !min-w-10 !p-0 !text-white hover:!bg-white/20 !rounded-full" 
                            onClick={onClose}
                        >
                            <span className="text-xl">&times;</span>
                        </Button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 h-full overflow-y-auto pb-24 bg-gray-50">
                    {orderInfo && (
                        <>
                            {/* Order Summary Card */}
                            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-lg font-semibold text-gray-800">Order Summary</h3>
                                    <Badge status={orderInfo.status} />
                                </div>
                                
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-3">
                                        <div>
                                            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Order Code</span>
                                            <p className="text-sm font-semibold text-gray-800 mt-1">{orderInfo.code}</p>
                                        </div>
                                        <div>
                                            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Created Date</span>
                                            <p className="text-sm text-gray-800 mt-1">{orderInfo.created_at?.slice(0, 10)}</p>
                                        </div>
                                    </div>
                                    
                                    <div className="space-y-3">
                                        <div>
                                            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Subtotal</span>
                                            <p className="text-sm font-semibold text-gray-800 mt-1">{orderInfo.sub_total}</p>
                                        </div>
                                        <div>
                                            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Discount</span>
                                            <p className="text-sm text-red-600 font-semibold mt-1">-{orderInfo.discount}</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="border-t border-gray-100 pt-4 mt-4">
                                    <div className="flex justify-between items-center">
                                        <span className="text-lg font-semibold text-gray-800">Total Amount</span>
                                        <span className="text-2xl font-bold text-green-600">{orderInfo.total_price}</span>
                                    </div>
                                </div>
                                
                                {orderInfo.note && (
                                    <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                                        <span className="text-xs font-medium text-yellow-700 uppercase tracking-wider">Note</span>
                                        <p className="text-sm text-yellow-800 mt-1">{orderInfo.note}</p>
                                    </div>
                                )}
                            </div>

                            {/* Customer Info Card */}
                            {customer && (
                                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
                                    <div className="flex items-center mb-4">
                                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                                            <span className="text-blue-600 font-semibold">👤</span>
                                        </div>
                                        <h3 className="text-lg font-semibold text-gray-800">Customer Information</h3>
                                    </div>
                                    
                                    <div className="grid grid-cols-1 gap-3">
                                        <div className="flex items-center">
                                            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider w-16">Name</span>
                                            <span className="text-sm font-medium text-gray-800 ml-4">{customer.first_name} {customer.last_name}</span>
                                        </div>
                                        <div className="flex items-center">
                                            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider w-16">Email</span>
                                            <span className="text-sm text-blue-600 ml-4">{customer.email}</span>
                                        </div>
                                        <div className="flex items-center">
                                            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider w-16">Phone</span>
                                            <span className="text-sm text-gray-800 ml-4">{customer.phone}</span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Address Info Card */}
                            {address && (
                                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
                                    <div className="flex items-center mb-4">
                                        <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center mr-3">
                                            <span className="text-green-600 font-semibold">📍</span>
                                        </div>
                                        <h3 className="text-lg font-semibold text-gray-800">Shipping Address</h3>
                                    </div>
                                    
                                    <div className="bg-gray-50 rounded-lg p-4">
                                        <p className="text-sm text-gray-700 leading-relaxed">
                                            {[address.line, address.street, address.ward, address.district, address.city, address.country]
                                                .filter(Boolean)
                                                .join(", ")}
                                        </p>
                                    </div>
                                </div>
                            )}

                            {/* Products Card */}
                            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
                                <div className="flex items-center justify-between mb-6">
                                    <div className="flex items-center">
                                        <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center mr-3">
                                            <span className="text-purple-600 font-semibold">📦</span>
                                        </div>
                                        <h3 className="text-lg font-semibold text-gray-800">Products</h3>
                                    </div>
                                    <div className="bg-gray-100 px-3 py-1 rounded-full">
                                        <span className="text-xs font-medium text-gray-600">{order_detail?.length || 0} items</span>
                                    </div>
                                </div>
                                
                                {order_detail && order_detail.length > 0 ? (
                                    <div className="max-h-96 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
                                        <div className="space-y-4">
                                            {order_detail.map((item, index) => (
                                                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200">
                                                    <div className="flex gap-4">
                                                        <div className="relative">
                                                            <img
                                                                src={item.images?.[0] || "/placeholder-image.jpg"}
                                                                className="w-20 h-20 object-cover rounded-lg shadow-sm"
                                                                alt="Product"
                                                            />
                                                        </div>
                                                        
                                                        <div className="flex-1">
                                                            <h5 className="font-semibold text-gray-800 mb-2">{item.name}</h5>
                                                            
                                                            <div className="flex gap-4 mb-3">
                                                                <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                                                                    Size: {item.size || 'None'}
                                                                </span>
                                                                <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                                                                    Color: {item.color || 'None'}
                                                                </span>
                                                            </div>
                                                            
                                                            <div className="flex justify-between items-center">
                                                                <div>
                                                                    <span className="text-xs text-gray-500">Price</span>
                                                                    <p className="text-sm font-semibold text-gray-800">{item.price}</p>
                                                                </div>
                                                                <div className="text-right">
                                                                    <span className="text-xs text-gray-500">Quantity</span>
                                                                    <p className="text-sm font-semibold text-gray-800">x{item.quantity}</p>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ) : (
                                    <div className="text-center py-12">
                                        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                            <span className="text-gray-400 text-2xl">📦</span>
                                        </div>
                                        <p className="text-gray-500">No products in this order</p>
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default OrderDetailOffcanvas;