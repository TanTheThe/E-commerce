const ProductsListSkeleton = () => {
    return (
        <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="bg-white rounded-lg shadow-sm p-4">
                    <div className="flex items-start gap-4">
                        <div className="w-20 h-20 bg-gray-200 rounded-md animate-pulse"></div>
                        <div className="flex-1 space-y-3">
                            <div className="h-5 bg-gray-200 rounded animate-pulse w-2/3"></div>
                            <div className="h-4 bg-gray-200 rounded animate-pulse w-1/3"></div>
                            <div className="flex gap-2">
                                <div className="h-6 bg-gray-200 rounded-full animate-pulse w-20"></div>
                                <div className="h-6 bg-gray-200 rounded-full animate-pulse w-20"></div>
                            </div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default ProductsListSkeleton;