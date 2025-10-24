const EvaluationButtons = ({ item, onEvaluate, onViewEvaluation, onAdditionalEvaluation }) => {
    if (!item.has_evaluation) {
        return (
            <button
                onClick={() => onEvaluate(item)}
                className="px-3 py-1 text-xs bg-[#ff5252] text-white rounded-md hover:bg-[#e53e3e] transition-colors cursor-pointer"
            >
                Đánh giá
            </button>
        );
    }

    if (!item.has_additional_evaluation) {
        return (
            <>
                <button
                    onClick={() => onViewEvaluation(item)}
                    className="px-3 py-1 text-xs bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors cursor-pointer"
                >
                    Xem đánh giá
                </button>
                <button
                    onClick={() => onAdditionalEvaluation(item)}
                    className="px-3 py-1 text-xs bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors cursor-pointer"
                >
                    Đánh giá bổ sung
                </button>
            </>
        );
    }

    return (
        <>
            <button
                onClick={() => onViewEvaluation(item)}
                className="px-3 py-1 text-xs bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors cursor-pointer"
            >
                Xem đánh giá
            </button>
            <button
                onClick={() => onViewEvaluation(item, 'additional')}
                className="px-3 py-1 text-xs bg-purple-500 text-white rounded-md hover:bg-purple-600 transition-colors cursor-pointer"
            >
                Xem đánh giá bổ sung
            </button>
        </>
    );
};

export default EvaluationButtons;