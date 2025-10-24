import React, { useState, useEffect, useContext } from 'react';
import { Plus, Package } from 'lucide-react';
import { MyContext } from '../../../App';
import useAuth from '../../Verify/auth';
import { deleteDataApi, getDataApi, postDataApi } from '../../../utils/api';
import GoodsReceiptCard from './goodsReceiptCard';
import UpdateGoodsReceiptModal from './updateGoodsReceipt';
import GoodsReceiptDetailModal from './goodsReceiptDetail';
import ApprovalPreviewModal from './approvalPreview';
import CreateGoodsReceiptModal from './createGoodsReceipt';

const GoodsReceiptsManagement = ({ warehouse }) => {
    const [activeTab, setActiveTab] = useState('all');
    const [goodsReceipts, setGoodsReceipts] = useState([]);
    const [total, setTotal] = useState(0);
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedGrId, setSelectedGrId] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [grToUpdateId, setGrToUpdateId] = useState(null);
    const [showConfirmModal, setShowConfirmModal] = useState(false);
    const [confirmAction, setConfirmAction] = useState(null);
    const [approvalPreviewGrId, setApprovalPreviewGrId] = useState(null);

    const { userRole } = useAuth();
    const context = useContext(MyContext);

    const limit = 12;

    const tabs = [
        { key: 'all', label: 'Tất cả', status: null },
        { key: 'pending', label: 'Chờ duyệt', status: 'pending' },
        { key: 'approved', label: 'Đã duyệt', status: 'approved' },
        { key: 'completed', label: 'Hoàn thành', status: 'completed' },
        { key: 'has_issue', label: 'Đang có vấn đề', status: 'has_issue' }
    ];

    const fetchGoodsReceipts = async () => {
        setIsLoading(true);
        try {
            const skip = (currentPage - 1) * limit;
            const queryParams = new URLSearchParams({
                skip: skip.toString(),
                limit: limit.toString()
            });

            const currentTab = tabs.find(t => t.key === activeTab);
            if (currentTab?.status) {
                queryParams.append('status_gr', currentTab.status);
            }

            if (warehouse?.id) {
                queryParams.append('warehouse_id', warehouse.id);
            }

            if (searchQuery.trim()) {
                queryParams.append('search', searchQuery.trim());
            }

            const response = await getDataApi(`/admin/goods-receipt?${queryParams.toString()}`);

            if (response.success) {
                setGoodsReceipts(response.data.data || []);
                setTotal(response.data.total || 0);
            }
        } catch (error) {
            console.error('Error fetching goods receipts:', error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchGoodsReceipts();
    }, [activeTab, currentPage, warehouse?.id, searchQuery]);

    useEffect(() => {
        setCurrentPage(1);
    }, [activeTab, searchQuery]);

    const totalPages = Math.ceil(total / limit);

    const handleViewDetail = (grId) => {
        setSelectedGrId(grId);
    };

    const handleUpdate = (grId) => {
        setGrToUpdateId(grId);
    };

    const handleViewApprovalPreview = (grId) => {
        setApprovalPreviewGrId(grId);
    };

    const handleApprove = (grId) => {
        setConfirmAction({
            action: 'approveGr',
            grId,
            message: 'Bạn có chắc muốn duyệt phiếu nhập kho này không?'
        });
        setShowConfirmModal(true);
    };

    const handleDelete = (grId) => {
        setConfirmAction({
            action: 'deleteGr',
            grId,
            message: 'Bạn có chắc muốn xóa phiếu nhập kho này không?'
        });
        setShowConfirmModal(true);
    };

    const executeConfirmAction = async () => {
        if (!confirmAction) return;

        setShowConfirmModal(false);

        if (confirmAction.action === 'deleteGr') {
            const grId = confirmAction.grId;
            try {
                const response = await deleteDataApi(`/admin/goods-receipt/${grId}`);

                if (response.success) {
                    context.openAlertBox("success", response.message || "Xóa phiếu nhập kho thành công");
                    fetchGoodsReceipts();
                } else {
                    context.openAlertBox("error", response?.data?.detail?.message || "Xóa phiếu nhập kho thất bại");
                }
            } catch (error) {
                console.error('Error deleting goods receipt:', error);
                context.openAlertBox("error", "Đã xảy ra lỗi khi xóa phiếu nhập kho");
            }
        } else if (confirmAction.action === 'approveGr') {
            const grId = confirmAction.grId;
            try {
                const response = await postDataApi(`/admin/goods-receipt/${grId}/approve`, {});

                if (response.success) {
                    context.openAlertBox("success", response.message || "Duyệt phiếu nhập kho thành công");
                    fetchGoodsReceipts();
                } else {
                    context.openAlertBox("error", response?.data?.detail?.message || "Duyệt phiếu nhập kho thất bại");
                }
            } catch (error) {
                console.error('Error approving goods receipt:', error);
                context.openAlertBox("error", "Đã xảy ra lỗi khi duyệt phiếu nhập kho");
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
                    <div className="flex items-center gap-3">
                        <input
                            type="text"
                            placeholder="Tìm theo số phiếu..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button
                            onClick={handleCreateNew}
                            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                        >
                            <Plus className="w-4 h-4" />
                            <span>Tạo phiếu nhập kho</span>
                        </button>
                    </div>
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
                ) : goodsReceipts.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                        <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                        <p className="text-gray-500 text-lg">Không có phiếu nhập kho nào</p>
                    </div>
                ) : (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                            {goodsReceipts.map((gr) => (
                                <GoodsReceiptCard
                                    key={gr.id}
                                    gr={gr}
                                    onViewDetail={handleViewDetail}
                                    onUpdate={handleUpdate}
                                    onDelete={handleDelete}
                                    onApprove={handleApprove}
                                    onViewApprovalPreview={handleViewApprovalPreview}
                                    userRole={userRole}
                                />
                            ))}
                        </div>

                        {totalPages > 1 && (
                            <div className="flex items-center justify-between bg-white rounded-lg shadow-sm p-4">
                                <div className="text-sm text-gray-600">
                                    Trang {currentPage} / {totalPages} · Tổng: {total} phiếu
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

            {grToUpdateId && (
                <UpdateGoodsReceiptModal
                    isOpen={!!grToUpdateId}
                    grId={grToUpdateId}
                    onClose={() => setGrToUpdateId(null)}
                    onSuccess={() => {
                        setGrToUpdateId(null);
                        fetchGoodsReceipts();
                    }}
                />
            )}

            {selectedGrId && (
                <GoodsReceiptDetailModal
                    grId={selectedGrId}
                    onClose={() => setSelectedGrId(null)}
                />
            )}

            {approvalPreviewGrId && (
                <ApprovalPreviewModal
                    grId={approvalPreviewGrId}
                    onClose={() => setApprovalPreviewGrId(null)}
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

            <CreateGoodsReceiptModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onSuccess={fetchGoodsReceipts}
                warehouseId={warehouse?.id}
                purchaseOrderId={null}
                openAlertBox={context.openAlertBox}
            />
        </div>
    );
}

export default GoodsReceiptsManagement;

