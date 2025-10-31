import { useEffect, useState } from "react";
import { deleteDataApi, getDataApi, postDataApi } from "../../../utils/api";
import { Package, X } from "lucide-react";
import UpdateGoodsReceiptModal from "./updateGoodsReceipt";
import GoodsReceiptDetailModal from "./goodsReceiptDetail";
import ApprovalPreviewModal from "./approvalPreview";
import GoodsReceiptTreeNode from "./goodsReceiptTreeNode";



const GoodsReceiptsTreeModal = ({ isOpen, purchaseOrderId, warehouseId, onClose, onSuccess, userRole, context }) => {
    const [activeTab, setActiveTab] = useState('all');
    const [receiptsTree, setReceiptsTree] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedGrId, setSelectedGrId] = useState(null);
    const [grToUpdateId, setGrToUpdateId] = useState(null);
    const [showConfirmModal, setShowConfirmModal] = useState(false);
    const [confirmAction, setConfirmAction] = useState(null);
    const [approvalPreviewGrId, setApprovalPreviewGrId] = useState(null);

    const tabs = [
        { key: 'all', label: 'Tất cả', status: null },
        { key: 'pending', label: 'Chờ duyệt', status: 'pending' },
        { key: 'approved', label: 'Đã duyệt', status: 'approved' },
        { key: 'completed', label: 'Hoàn thành', status: 'completed' },
        { key: 'has_issue', label: 'Đang có vấn đề', status: 'has_issue' }
    ];

    const fetchGrTree = async () => {
        setIsLoading(true);
        try {
            const queryParams = new URLSearchParams({
                warehouse_id: warehouseId
            });

            const response = await getDataApi(`/admin/goods-receipt/${purchaseOrderId}/receipts-tree?${queryParams.toString()}`);

            if (response.success) {
                setReceiptsTree(response.data.receipts_tree || []);
            }
        } catch (error) {
            console.error('Error fetching GR tree:', error);
            context.openAlertBox("error", "Lỗi khi tải danh sách phiếu nhập kho");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (isOpen && purchaseOrderId) {
            fetchGrTree();
        }
    }, [isOpen, purchaseOrderId]);

    const filterReceipts = (receipts) => {
        return receipts.filter(gr => {
            const matchesTab = !tabs.find(t => t.key === activeTab)?.status || gr.status === tabs.find(t => t.key === activeTab).status;
            const matchesSearch = !searchQuery.trim() || gr.receipt_number.toLowerCase().includes(searchQuery.toLowerCase());
            return matchesTab && matchesSearch;
        }).map(gr => ({
            ...gr,
            children: gr.children ? filterReceipts(gr.children) : []
        }));
    };

    const filteredReceipts = filterReceipts(receiptsTree);

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
                    fetchGrTree();
                    onSuccess();
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
                    fetchGrTree();
                    onSuccess();
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

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.3)' }}>
            <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[85vh] flex flex-col m-4">
                <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
                    <h2 className="text-xl font-semibold text-gray-800">Phiếu nhập kho của đơn hàng</h2>
                    <button
                        onClick={onClose}
                        className="text-gray-500 hover:text-gray-700 transition-colors"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="bg-white border-b border-gray-200 px-6 py-3">
                    <div className="flex items-center justify-between">
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
                        <input
                            type="text"
                            placeholder="Tìm theo số phiếu..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                </div>

                <div className="flex-1 overflow-auto p-6">
                    {isLoading ? (
                        <div className="flex items-center justify-center py-12">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                        </div>
                    ) : filteredReceipts.length === 0 ? (
                        <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                            <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                            <p className="text-gray-500 text-lg">Không có phiếu nhập kho nào</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {filteredReceipts.map((gr) => (
                                <GoodsReceiptTreeNode
                                    key={gr.id}
                                    gr={gr}
                                    level={0}
                                    onViewDetail={handleViewDetail}
                                    onUpdate={handleUpdate}
                                    onDelete={handleDelete}
                                    onApprove={handleApprove}
                                    onViewApprovalPreview={handleViewApprovalPreview}
                                    userRole={userRole}
                                />
                            ))}
                        </div>
                    )}
                </div>

                {grToUpdateId && (
                    <UpdateGoodsReceiptModal
                        isOpen={!!grToUpdateId}
                        grId={grToUpdateId}
                        onClose={() => setGrToUpdateId(null)}
                        onSuccess={() => {
                            setGrToUpdateId(null);
                            fetchGrTree();
                            onSuccess();
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
            </div>
        </div>
    );
};

export default GoodsReceiptsTreeModal;