import React, { useState, useEffect, useCallback, useContext } from 'react';
import { Package, Search, Plus, Eye, Edit, Trash2, Calendar, DollarSign, User, Warehouse, TrendingUp, X, ChevronDown, ChevronUp } from 'lucide-react';
import { deleteDataApi, getDataApi, postDataApi, putDataApi } from "../../../utils/api";
import PurchaseOrderCard from "./purchaseOrderCard";
import PurchaseOrderDetailModal from './purchaseOrderDetail';
import CreatePurchaseOrderModal from './createPurchaseOrder';
import UpdatePurchaseOrderModal from './updatePurchaseOrder';
import useAuth from '../../Verify/auth';
import { MyContext } from '../../../App';
import UpdatePurchaseOrderAfterNegotiationModal from './updatePOAfterNegotiation';

const PurchaseOrdersManagement = ({ warehouse }) => {
    const [activeTab, setActiveTab] = useState('all');
    const [purchaseOrders, setPurchaseOrders] = useState([]);
    const [total, setTotal] = useState(0);
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedPoId, setSelectedPoId] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [poToUpdateId, setPoToUpdateId] = useState(null);
    const [showConfirmModal, setShowConfirmModal] = useState(false);
    const [confirmAction, setConfirmAction] = useState(null);

    const [poToUpdateAfterNegotiationId, setPoToUpdateAfterNegotiationId] = useState(null);

    const { userRole } = useAuth();
    const context = useContext(MyContext)

    const limit = 12;

    const tabs = [
        { key: 'all', label: 'Tất cả', status: null },
        { key: 'draft', label: 'Nháp', status: 'draft' },
        { key: 'sent', label: 'Đã gửi', status: 'sent' },
        { key: 'confirmed', label: 'Đã xác nhận', status: 'confirmed' },
        { key: 'completed', label: 'Hoàn thành', status: 'completed' },
        { key: 'cancelled', label: 'Đã hủy', status: 'cancelled' }
    ];

    const fetchPurchaseOrders = async () => {
        setIsLoading(true);
        try {
            const skip = (currentPage - 1) * limit;
            const queryParams = new URLSearchParams({
                skip: skip.toString(),
                limit: limit.toString()
            });

            const currentTab = tabs.find(t => t.key === activeTab);
            if (currentTab?.status) {
                queryParams.append('po_status', currentTab.status);
            }

            if (warehouse?.id) {
                queryParams.append('warehouse_id', warehouse.id);
            }

            const response = await getDataApi(`/admin/purchase-orders/all?${queryParams.toString()}`);

            if (response.success) {
                setPurchaseOrders(response.data.data || []);
                setTotal(response.data.total || 0);
            }
        } catch (error) {
            console.error('Error fetching purchase orders:', error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchPurchaseOrders();
    }, [activeTab, currentPage, warehouse?.id]);

    useEffect(() => {
        setCurrentPage(1);
    }, [activeTab]);

    const totalPages = Math.ceil(total / limit);

    const handleViewDetail = (poId) => {
        setSelectedPoId(poId);
    };

    const handleUpdate = (poId) => {
        setPoToUpdateId(poId);
    };

    const handleUpdateAfterNegotiation = (poId) => {
        setPoToUpdateAfterNegotiationId(poId);
    };

    const handleSend = async (poId, requestData) => {
        try {
            const response = await postDataApi(
                `/admin/purchase-orders/${poId}/send`,
                requestData
            );

            if (response.success) {
                fetchPurchaseOrders();
                context.openAlertBox("success", response.message || "Đã gửi đi yêu cầu đặt đơn hàng");
            }
        } catch (error) {
            console.error('Error sending purchase order:', error);
        }
    };

    const handleDelete = (poId) => {
        setConfirmAction({
            action: 'deletePo',
            poId,
            message: 'Bạn có chắc muốn xóa đơn đặt hàng này không?'
        });
        setShowConfirmModal(true);
    };

    const handleConfirm = (poId) => {
        setConfirmAction({
            action: 'confirmPo',
            poId,
            message: 'Bạn có chắc muốn xác nhận đơn đặt hàng này không?'
        });
        setShowConfirmModal(true);
    };

    const executeConfirmAction = async () => {
        if (!confirmAction) return;

        setShowConfirmModal(false);

        if (confirmAction.action === 'deletePo') {
            const poId = confirmAction.poId;
            try {
                const response = await deleteDataApi(`/admin/purchase-orders/${poId}`);

                if (response.success) {
                    context.openAlertBox("success", response.message || "Xóa đơn đặt hàng thành công");
                    fetchPurchaseOrders();
                } else {
                    context.openAlertBox("error", response?.data?.detail?.message || "Xóa đơn hàng thất bại");
                }
            } catch (error) {
                console.error('Error deleting purchase order:', error);
                context.openAlertBox("error", "Đã xảy ra lỗi khi xóa đơn hàng");
            }
        } else if (confirmAction.action === 'confirmPo') {
            const poId = confirmAction.poId;
            try {
                const response = await putDataApi(`/admin/purchase-orders/${poId}/confirm`, {});

                if (response.success) {
                    context.openAlertBox("success", response.message || "Xác nhận đơn hàng thành công");
                    fetchPurchaseOrders();
                } else {
                    context.openAlertBox("error", response?.data?.detail?.message || "Xác nhận đơn hàng thất bại");
                }
            } catch (error) {
                console.error('Error confirming purchase order:', error);
                context.openAlertBox("error", "Đã xảy ra lỗi khi xác nhận đơn hàng");
            }
        }

        setConfirmAction(null);
    };

    const handleCreateNew = () => {
        setIsCreateModalOpen(true);
    };

    return (
        <div className="h-full flex flex-col bg-gray-50">
            <div className="bg-white border-b border-gray-200">
                <div className="flex items-center justify-between px-6 py-4">
                    <div className="flex items-center gap-2">
                        {tabs.map((tab) => (
                            <button
                                key={tab.key}
                                className={`px-4 py-2 font-medium text-sm rounded-md transition-colors ${activeTab === tab.key
                                    ? 'bg-blue-600 text-white'
                                    : 'text-gray-600 hover:bg-gray-100'
                                    }`}
                                onClick={() => setActiveTab(tab.key)}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </div>
                    <button
                        onClick={handleCreateNew}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                    >
                        <Plus className="w-4 h-4" />
                        <span>Tạo đơn đặt hàng</span>
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
                        <p className="text-gray-500 text-lg">Không có đơn đặt hàng nào</p>
                    </div>
                ) : (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                            {purchaseOrders.map((po) => (
                                <PurchaseOrderCard
                                    key={po.id}
                                    po={po}
                                    onViewDetail={handleViewDetail}
                                    onUpdate={handleUpdate}
                                    onUpdateAfterNegotiation={handleUpdateAfterNegotiation}
                                    onDelete={handleDelete}
                                    onSend={handleSend}
                                    onConfirm={handleConfirm}
                                    userRole={userRole}
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

            {poToUpdateId && (
                <UpdatePurchaseOrderModal
                    isOpen={!!poToUpdateId}
                    poId={poToUpdateId}
                    onClose={() => setPoToUpdateId(null)}
                    onSuccess={() => {
                        setPoToUpdateId(null);
                        fetchPurchaseOrders();
                    }}
                />
            )}

            {selectedPoId && (
                <PurchaseOrderDetailModal
                    poId={selectedPoId}
                    onClose={() => setSelectedPoId(null)}
                />
            )}

            {showConfirmModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                    style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}>
                    <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
                        <h3 className="text-lg font-semibold text-gray-800 mb-4">Xác nhận</h3>
                        <p className="text-gray-600 mb-6">{confirmAction?.message}</p>
                        <div className="flex justify-end gap-3">
                            <button
                                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors cursor-pointer"
                                onClick={() => {
                                    setShowConfirmModal(false);
                                    setConfirmAction(null);
                                }}
                            >
                                Hủy
                            </button>
                            <button
                                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors cursor-pointer"
                                onClick={executeConfirmAction}
                            >
                                Xác nhận
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {poToUpdateAfterNegotiationId && (
                <UpdatePurchaseOrderAfterNegotiationModal
                    isOpen={!!poToUpdateAfterNegotiationId}
                    poId={poToUpdateAfterNegotiationId}
                    onClose={() => setPoToUpdateAfterNegotiationId(null)}
                    onSuccess={() => {
                        setPoToUpdateAfterNegotiationId(null);
                        fetchPurchaseOrders();
                    }}
                />
            )}

            <CreatePurchaseOrderModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onSuccess={fetchPurchaseOrders}
                warehouseId={warehouse?.id}
            />
        </div>
    );
};

export default PurchaseOrdersManagement;