import React, { useState, useEffect, useContext } from 'react';
import { Plus, Package, FileText } from 'lucide-react';
import { MyContext } from '../../../App';
import useAuth from '../../Verify/auth';
import { deleteDataApi, getDataApi, postDataApi } from '../../../utils/api';
import ReturnPurchaseCard from './returnPurchaseCard';
import UpdateReturnPurchaseModal from './updateReturnPurchase';
import PurchaseReturnDetailModal from './returnPurchaseDetail';
import CreatePurchaseReturnModal from './createPurchaseReturn';
import ReturnPurchaseListModal from './purchaseOrderReturn';

const formatDate = (dateString) => {
    if (!dateString || isNaN(Date.parse(dateString))) {
        return null;
    }
    return new Date(dateString).toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
    });
};

const ReturnPurchaseManagement = ({ warehouse }) => {
    const [purchaseOrders, setPurchaseOrders] = useState([]);
    const [total, setTotal] = useState(0);
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoading, setIsLoading] = useState(false);
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [selectedPOId, setSelectedPOId] = useState(null);

    const { userRole } = useAuth();
    const context = useContext(MyContext);

    const limit = 12;

    const fetchPurchaseOrdersWithReturns = async () => {
        setIsLoading(true);
        try {
            const skip = (currentPage - 1) * limit;
            const queryParams = new URLSearchParams({
                skip: skip.toString(),
                limit: limit.toString()
            });

            if (warehouse?.id) {
                queryParams.append('warehouse_id', warehouse.id);
            }

            const response = await getDataApi(`/admin/purchase-orders/purchase-orders-with-returns?${queryParams.toString()}`);

            if (response.success) {
                setPurchaseOrders(response.data.data || []);
                setTotal(response.data.total || 0);
            }
        } catch (error) {
            console.error('Error fetching purchase orders with returns:', error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchPurchaseOrdersWithReturns();
    }, [currentPage, warehouse?.id]);

    const totalPages = Math.ceil(total / limit);

    const handleCreateNew = () => {
        setIsCreateModalOpen(true);
    };

    const handleViewReturns = (poId) => {
        setSelectedPOId(poId);
    };

    const getStatusBadge = (status) => {
        const statusConfig = {
            draft: { label: 'Nháp', color: 'bg-gray-100 text-gray-700' },
            approved: { label: 'Đã duyệt', color: 'bg-green-100 text-green-700' },
            ordered: { label: 'Đã đặt hàng', color: 'bg-blue-100 text-blue-700' },
            partial: { label: 'Nhập 1 phần', color: 'bg-yellow-100 text-yellow-700' },
            completed: { label: 'Hoàn thành', color: 'bg-purple-100 text-purple-700' }
        };

        const config = statusConfig[status] || statusConfig.draft;

        return (
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
                {config.label}
            </span>
        );
    };

    return (
        <div className="h-full flex flex-col bg-gray-50">
            <div className="bg-white border-b border-gray-200">
                <div className="flex items-center justify-between px-6 py-4">
                    <h2 className="text-xl font-semibold text-gray-800">Quản lý phiếu trả hàng nhập</h2>
                    <button
                        onClick={handleCreateNew}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                    >
                        <Plus className="w-4 h-4" />
                        <span>Tạo phiếu trả hàng</span>
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-auto p-6">
                {isLoading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {[...Array(6)].map((_, i) => (
                            <div key={i} className="bg-white rounded-lg shadow-sm p-4 animate-pulse">
                                <div className="h-6 bg-gray-200 rounded w-1/2 mb-3"></div>
                                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                                <div className="h-4 bg-gray-200 rounded w-2/3 mb-4"></div>
                                <div className="h-10 bg-gray-200 rounded"></div>
                            </div>
                        ))}
                    </div>
                ) : purchaseOrders.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                        <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                        <p className="text-gray-500 text-lg">Không có đơn nhập hàng nào có phiếu trả</p>
                    </div>
                ) : (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                            {purchaseOrders.map((po) => (
                                <div key={po.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                                    <div className="flex justify-between items-start mb-3">
                                        <div className="flex-1">
                                            <h3 className="font-semibold text-lg text-gray-900">{po.po_number}</h3>
                                        </div>
                                        {getStatusBadge(po.status)}
                                    </div>

                                    <div className="space-y-2 mb-3 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Tổng đã đặt:</span>
                                            <span className="font-medium text-gray-900">{po.total_ordered || 0} món</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Số phiếu hoàn:</span>
                                            <span className="font-semibold text-blue-600">{po.total_gr_count || 0} phiếu</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Ngày tạo:</span>
                                            <span className="font-medium text-gray-900">{formatDate(po.created_at)}</span>
                                        </div>
                                    </div>

                                    <button
                                        onClick={() => handleViewReturns(po.id)}
                                        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                                    >
                                        <FileText className="w-4 h-4" />
                                        <span>Xem phiếu trả hàng</span>
                                    </button>
                                </div>
                            ))}
                        </div>

                        {totalPages > 1 && (
                            <div className="flex items-center justify-between bg-white rounded-lg shadow-sm p-4">
                                <div className="text-sm text-gray-600">
                                    Trang {currentPage} / {totalPages} · Tổng: {total} đơn
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                                        disabled={currentPage === 1}
                                        className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                    >
                                        Trước
                                    </button>
                                    <button
                                        onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                                        disabled={currentPage === totalPages}
                                        className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                    >
                                        Sau
                                    </button>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>

            {selectedPOId && (
                <ReturnPurchaseListModal
                    poId={selectedPOId}
                    warehouseId={warehouse?.id}
                    onClose={() => setSelectedPOId(null)}
                    userRole={userRole}
                    openAlertBox={context.openAlertBox}
                />
            )}

            <CreatePurchaseReturnModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onSuccess={fetchPurchaseOrdersWithReturns}
                warehouseId={warehouse?.id}
                openAlertBox={context.openAlertBox}
            />
        </div>
    );
};

export default ReturnPurchaseManagement;

