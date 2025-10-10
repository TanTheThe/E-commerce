const SummaryCard = ({ icon, label, value, color, isLoading }) => {
    const colorClasses = {
        blue: 'bg-blue-50 text-blue-600',
        purple: 'bg-purple-50 text-purple-600',
        green: 'bg-green-50 text-green-600',
        orange: 'bg-orange-50 text-orange-600'
    };

    return (
        <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="flex items-center gap-3">
                <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
                    {icon}
                </div>
                <div className="flex-1">
                    <p className="text-sm text-gray-600 mb-1">{label}</p>
                    {isLoading ? (
                        <div className="h-6 bg-gray-200 rounded animate-pulse w-20"></div>
                    ) : (
                        <p className="text-xl font-bold text-gray-800">{value}</p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SummaryCard;