import React, { useState, useEffect, useContext } from 'react';
import { Plus, Package } from 'lucide-react';
import { MyContext } from '../../../App';
import useAuth from '../../Verify/auth';
import { deleteDataApi, getDataApi, postDataApi } from '../../../utils/api';
import CreateGoodsReceiptModal from './createGoodsReceipt';
import PurchaseOrderCard from './purchaseOrderCard';
import GoodsReceiptsTreeModal from './goodsReceiptTree';

const GoodsReceiptsManagement = ({ warehouse }) => {
    const [total, setTotal] = useState(0);
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoading, setIsLoading] = useState(false);
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

    const [purchaseOrders, setPurchaseOrders] = useState([]);
    const [selectedPoId, setSelectedPoId] = useState(null);
    const [showGrTreeModal, setShowGrTreeModal] = useState(false);

    const { userRole } = useAuth();
    const context = useContext(MyContext);

    const limit = 12;

    const fetchPurchaseOrders = async () => {
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

            const response = await getDataApi(`/admin/purchase-orders/purchase-orders-with-receipts?${queryParams.toString()}`);

            if (response.success) {
                setPurchaseOrders(response.data.data || []);
                setTotal(response.data.total || 0);
            }
        } catch (error) {
            console.error('Error fetching purchase orders:', error);
            context.openAlertBox("error", "Lỗi khi tải danh sách đơn nhập hàng");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchPurchaseOrders();
    }, [currentPage, warehouse?.id]);

    const totalPages = Math.ceil(total / limit);

    const handleViewReceipts = (poId) => {
        setSelectedPoId(poId);
        setShowGrTreeModal(true);
    };

    const handleCreateNew = () => {
        setIsCreateModalOpen(true);
    };

    return (
        <div className="h-full flex flex-col bg-gray-50">
            <div className="bg-white border-b border-gray-200">
                <div className="flex items-center justify-between px-6 py-4">
                    <h2 className="text-xl font-semibold text-gray-800">Đơn nhập hàng có phiếu nhập kho</h2>
                    <button
                        onClick={handleCreateNew}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                    >
                        <Plus className="w-4 h-4" />
                        <span>Tạo phiếu nhập kho</span>
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
                        <p className="text-gray-500 text-lg">Không có đơn nhập hàng nào</p>
                    </div>
                ) : (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                            {purchaseOrders.map((po) => (
                                <PurchaseOrderCard
                                    key={po.id}
                                    po={po}
                                    onViewReceipts={handleViewReceipts}
                                />
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

            {showGrTreeModal && selectedPoId && (
                <GoodsReceiptsTreeModal
                    isOpen={showGrTreeModal}
                    purchaseOrderId={selectedPoId}
                    warehouseId={warehouse?.id}
                    onClose={() => {
                        setShowGrTreeModal(false);
                        setSelectedPoId(null);
                    }}
                    onSuccess={fetchPurchaseOrders}
                    userRole={userRole}
                    context={context}
                />
            )}

            <CreateGoodsReceiptModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onSuccess={fetchPurchaseOrders}
                warehouseId={warehouse?.id}
                purchaseOrderId={null}
                openAlertBox={context.openAlertBox}
            />
        </div>
    );
}

export default GoodsReceiptsManagement;

