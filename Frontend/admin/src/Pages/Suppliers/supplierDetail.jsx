import React, { useState, useEffect } from "react";
import { Drawer, CircularProgress, Button } from "@mui/material";
import {
    FaUserCircle,
    FaMapMarkerAlt,
    FaCheckCircle,
    FaTimesCircle,
    FaWallet,
    FaExclamationTriangle,
    FaUniversity,
    FaEnvelope,
    FaPhone,
    FaStickyNote,
    FaClock,
    FaCreditCard,
    FaBox,
} from "react-icons/fa";
import { getDataApi } from '../../utils/api';

const SupplierDetailOffcanvas = ({ open, onClose, supplier, context }) => {
    const [detail, setDetail] = useState(null);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState(0);

    const formatCurrency = (amount) =>
        amount == null
            ? "Chưa có"
            : new Intl.NumberFormat("vi-VN", {
                style: "currency",
                currency: "VND",
            }).format(amount);

    const formatDate = (dateString) => {
        if (!dateString) return "N/A";
        try {
            return new Date(dateString).toLocaleDateString("vi-VN", {
                year: "numeric",
                month: "2-digit",
                day: "2-digit",
                hour: "2-digit",
                minute: "2-digit",
            });
        } catch {
            return dateString;
        }
    };

    const fetchDetail = async (id) => {
        setLoading(true);
        setDetail(null);
        try {
            const response = await getDataApi(`/admin/suppliers/${id}`);

            if (response.success && response.data) {
                setDetail(response.data);
            } else {
                context.openAlertBox('error', response?.data?.detail?.message || 'Không tìm thấy chi tiết nhà cung cấp.');
            }
        } catch (error) {
            console.error('Error fetching supplier detail:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi tải chi tiết.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (open && supplier?.id) {
            fetchDetail(supplier.id);
            setActiveTab(0);
        } else if (!open) {
            setDetail(null);
        }
    }, [open, supplier?.id]);

    return (
        <Drawer
            anchor="right"
            open={open}
            onClose={onClose}
            PaperProps={{
                sx: {
                    width: { xs: '100%', sm: 520, md: 680 },
                    bgcolor: '#f8fafc',
                    fontFamily: "'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
                },
            }}
        >
            <div className="h-full flex flex-col" style={{ fontFamily: "'Montserrat', sans-serif" }}>
                <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
                    <h2 className="text-xl font-semibold text-gray-800">Thông tin nhà cung cấp</h2>
                    <Button
                        className="!w-8 !h-8 !min-w-8 !p-0 hover:bg-gray-100 !rounded-full"
                        onClick={onClose}
                    >
                        <span className="text-2xl text-gray-600">&times;</span>
                    </Button>
                </div>

                {loading ? (
                    <div className="flex-1 flex items-center justify-center">
                        <CircularProgress />
                    </div>
                ) : !detail ? (
                    <div className="flex-1 flex items-center justify-center px-4">
                        <p className="text-gray-500">Không có dữ liệu.</p>
                    </div>
                ) : (
                    <>
                        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-6">
                            <div className="flex items-center gap-4">
                                <div className="w-16 h-16 rounded-full bg-white/25 border-2 border-white/50 flex items-center justify-center text-white text-2xl font-bold">
                                    {detail.name?.[0] || 'N'}
                                </div>
                                <div className="flex-1">
                                    <h3 className="text-xl font-semibold text-white mb-1">{detail.name}</h3>
                                    <p className="text-white/90 text-sm">Mã: {detail.code}</p>
                                </div>
                                <span className={`px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1.5 ${detail.is_active
                                        ? 'bg-green-500/90 text-white'
                                        : 'bg-red-500/90 text-white'
                                    }`}>
                                    {detail.is_active ? <FaCheckCircle size={12} /> : <FaTimesCircle size={12} />}
                                    {detail.is_active ? 'Hoạt động' : 'Ngưng'}
                                </span>
                            </div>
                        </div>

                        {/* Tabs */}
                        <div className="bg-white border-b border-gray-200">
                            <div className="flex px-4">
                                <button
                                    className={`px-6 py-3 font-medium text-sm transition-colors relative ${activeTab === 0
                                            ? 'text-purple-600'
                                            : 'text-gray-600 hover:text-purple-600'
                                        }`}
                                    onClick={() => setActiveTab(0)}
                                >
                                    Thông tin
                                    {activeTab === 0 && (
                                        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-purple-600"></div>
                                    )}
                                </button>
                                <button
                                    className={`px-6 py-3 font-medium text-sm transition-colors relative flex items-center gap-2 ${activeTab === 1
                                            ? 'text-purple-600'
                                            : 'text-gray-600 hover:text-purple-600'
                                        }`}
                                    onClick={() => setActiveTab(1)}
                                >
                                    Sản phẩm
                                    {detail.total_products > 0 && (
                                        <span className="bg-purple-100 text-purple-600 px-2 py-0.5 rounded-full text-xs font-semibold">
                                            {detail.total_products}
                                        </span>
                                    )}
                                    {activeTab === 1 && (
                                        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-purple-600"></div>
                                    )}
                                </button>
                            </div>
                        </div>

                        <div className="flex-1 overflow-y-auto p-4 pb-24">
                            {activeTab === 0 && (
                                <div className="space-y-4">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="bg-gradient-to-br from-purple-600 to-indigo-600 p-4 rounded-lg text-white">
                                            <div className="flex items-center gap-2 mb-2 opacity-90">
                                                <FaWallet size={16} />
                                                <span className="text-sm">Hạn mức</span>
                                            </div>
                                            <p className="text-xl font-bold">{formatCurrency(detail.credit_limit)}</p>
                                        </div>
                                        <div className={`bg-gradient-to-br ${detail.current_debt > 0
                                                ? 'from-red-500 to-pink-500'
                                                : 'from-blue-500 to-cyan-500'
                                            } p-4 rounded-lg text-white`}>
                                            <div className="flex items-center gap-2 mb-2 opacity-90">
                                                <FaExclamationTriangle size={16} />
                                                <span className="text-sm">Công nợ</span>
                                            </div>
                                            <p className="text-xl font-bold">{formatCurrency(detail.current_debt)}</p>
                                        </div>
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                                        <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-200">
                                            <FaUserCircle className="text-purple-600" size={20} />
                                            <h4 className="font-semibold text-gray-800">Thông tin liên hệ</h4>
                                        </div>
                                        <div className="space-y-3">
                                            <InfoRow icon={<FaUserCircle />} label="Người liên hệ" value={detail.contact_person} />
                                            <InfoRow icon={<FaPhone />} label="Số điện thoại" value={detail.phone} />
                                            <InfoRow icon={<FaEnvelope />} label="Email" value={detail.email} />
                                            <InfoRow icon={<FaMapMarkerAlt />} label="Địa chỉ" value={detail.address} />
                                        </div>
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                                        <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-200">
                                            <FaUniversity className="text-purple-600" size={20} />
                                            <h4 className="font-semibold text-gray-800">Thông tin ngân hàng</h4>
                                        </div>
                                        <div className="space-y-3">
                                            <InfoRow icon={<FaCreditCard />} label="Số tài khoản" value={detail.bank_account} />
                                            <InfoRow icon={<FaUniversity />} label="Ngân hàng" value={detail.bank_name} />
                                        </div>
                                    </div>

                                    {detail.notes && (
                                        <div className="bg-white border border-gray-200 rounded-lg p-4">
                                            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-200">
                                                <FaStickyNote className="text-purple-600" size={20} />
                                                <h4 className="font-semibold text-gray-800">Ghi chú</h4>
                                            </div>
                                            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                                                <p className="text-gray-700 whitespace-pre-wrap text-sm">{detail.notes}</p>
                                            </div>
                                        </div>
                                    )}

                                    <div className="bg-white border border-gray-200 rounded-lg p-3">
                                        <div className="flex flex-col sm:flex-row gap-3 text-sm text-gray-600 justify-center">
                                            <div className="flex items-center gap-2">
                                                <FaClock size={14} className="text-gray-400" />
                                                <span>Tạo: {formatDate(detail.created_at)}</span>
                                            </div>
                                            {detail.updated_at && (
                                                <div className="flex items-center gap-2">
                                                    <FaClock size={14} className="text-gray-400" />
                                                    <span>Cập nhật: {formatDate(detail.updated_at)}</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeTab === 1 && (
                                <div>
                                    {detail.products && detail.products.length > 0 ? (
                                        <div className="space-y-3">
                                            {detail.products.map((product) => (
                                                <div
                                                    key={product.id}
                                                    className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow"
                                                >
                                                    <div className="flex gap-3 p-3">
                                                        <img
                                                            src={product.image || 'https://via.placeholder.com/100x100?text=No+Image'}
                                                            alt={product.name}
                                                            className="w-24 h-24 object-cover rounded-md flex-shrink-0"
                                                        />
                                                        <div className="flex-1 min-w-0">
                                                            <h5 className="font-semibold text-gray-800 mb-2 line-clamp-2">
                                                                {product.name}
                                                            </h5>
                                                            <div className="flex flex-wrap gap-2 mb-2">
                                                                <span className={`text-xs px-2 py-1 rounded font-medium ${product.status === 'active'
                                                                        ? 'bg-green-100 text-green-800'
                                                                        : 'bg-gray-100 text-gray-800'
                                                                    }`}>
                                                                    {product.status}
                                                                </span>
                                                                <span className={`text-xs px-2 py-1 rounded font-medium flex items-center gap-1 ${product.is_active
                                                                        ? 'bg-blue-100 text-blue-800'
                                                                        : 'bg-red-100 text-red-800'
                                                                    }`}>
                                                                    {product.is_active ? (
                                                                        <FaCheckCircle size={10} />
                                                                    ) : (
                                                                        <FaTimesCircle size={10} />
                                                                    )}
                                                                    {product.is_active ? 'Cung cấp' : 'Ngừng'}
                                                                </span>
                                                            </div>
                                                            {product.notes && (
                                                                <p className="text-xs text-gray-600 truncate">
                                                                    💬 {product.notes}
                                                                </p>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
                                            <FaBox size={48} className="text-gray-300 mx-auto mb-3" />
                                            <p className="text-gray-500">Chưa có sản phẩm nào</p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        <div className="absolute bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-3">
                            <div className="flex justify-end">
                                <Button
                                    className="!px-6 !py-2 !bg-gray-600 !text-white !rounded-md hover:!bg-gray-700 !normal-case"
                                    onClick={onClose}
                                >
                                    Đóng
                                </Button>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </Drawer>
    );
};

const InfoRow = ({ icon, label, value }) => (
    <div className="flex items-start gap-3">
        <div className="text-gray-400 mt-0.5 flex-shrink-0">
            {icon}
        </div>
        <div className="flex-1 min-w-0">
            <p className="text-xs text-gray-600 font-medium mb-1">{label}</p>
            <p className="text-sm text-gray-800 break-words">{value || 'N/A'}</p>
        </div>
    </div>
);

export default SupplierDetailOffcanvas;