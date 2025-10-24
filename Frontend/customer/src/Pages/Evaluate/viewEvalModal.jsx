import { FiX, FiStar, FiMessageSquare } from 'react-icons/fi';

const ViewEvaluationModal = ({ isOpen, onClose, evaluationData }) => {
    if (!isOpen || !evaluationData) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.4)' }}>
            <div className="bg-white rounded-lg p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-gray-800">Chi tiết đánh giá</h3>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700 cursor-pointer">
                        <FiX className="text-xl" />
                    </button>
                </div>

                <div className="space-y-4">
                    <div className="flex gap-3 p-3 bg-gray-50 rounded-lg">
                        <div className="w-16 h-16 bg-gray-200 rounded-lg overflow-hidden">
                            <img
                                src={evaluationData.product.variant_image}
                                alt={evaluationData.product.name}
                                className="w-full h-full object-cover"
                            />
                        </div>
                        <div className="flex-1">
                            <h4 className="font-medium text-gray-800">{evaluationData.product.name}</h4>
                            <p className="text-sm text-gray-600">
                                Size: {evaluationData.product.size} • Màu: {evaluationData.product.color_name}
                            </p>
                        </div>
                    </div>

                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <div className="flex">
                                {[1, 2, 3, 4, 5].map(star => (
                                    <FiStar
                                        key={star}
                                        className={`text-lg ${star <= evaluationData.rate ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
                                    />
                                ))}
                            </div>
                            <span className="text-sm text-gray-600">
                                {new Date(evaluationData.created_at).toLocaleDateString('vi-VN')}
                            </span>
                        </div>

                        {evaluationData.comment && (
                            <p className="text-gray-700 mb-2">{evaluationData.comment}</p>
                        )}

                        {evaluationData.image && (
                            <img
                                src={evaluationData.image}
                                alt="Evaluation"
                                className="w-full max-w-xs rounded-lg"
                            />
                        )}
                    </div>

                    {evaluationData.additional_evaluation.has_additional && (
                        <div className="border-t pt-4">
                            <div className="flex items-center gap-2 mb-2">
                                <FiMessageSquare className="text-green-500" />
                                <span className="text-sm font-medium text-green-600">Đánh giá bổ sung</span>
                                <span className="text-sm text-gray-600">
                                    {new Date(evaluationData.additional_evaluation.created_at).toLocaleDateString('vi-VN')}
                                </span>
                            </div>

                            {evaluationData.additional_evaluation.comment && (
                                <p className="text-gray-700 mb-2">{evaluationData.additional_evaluation.comment}</p>
                            )}

                            {evaluationData.additional_evaluation.image && (
                                <img
                                    src={evaluationData.additional_evaluation.image}
                                    alt="Additional Evaluation"
                                    className="w-full max-w-xs rounded-lg"
                                />
                            )}
                        </div>
                    )}

                    {evaluationData.seller_reply.has_reply && (
                        <div className="border-t pt-4">
                            <div className="flex items-center gap-2 mb-2">
                                <span className="text-sm font-medium text-blue-600">Phản hồi từ người bán</span>
                                <span className="text-sm text-gray-600">
                                    {new Date(evaluationData.seller_reply.replied_at).toLocaleDateString('vi-VN')}
                                </span>
                            </div>
                            <p className="text-gray-700 bg-blue-50 p-3 rounded-lg">{evaluationData.seller_reply.content}</p>
                        </div>
                    )}
                </div>

                <div className="mt-6">
                    <button
                        onClick={onClose}
                        className="w-full py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors cursor-pointer"
                    >
                        Đóng
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ViewEvaluationModal;