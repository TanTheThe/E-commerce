import { ChevronDown, ChevronRight, AlertCircle } from 'lucide-react';

const StatusBadge = ({ status }) => {
    const statusConfig = {
        available: { label: 'Đủ hàng', className: 'bg-green-100 text-green-800' },
        low: { label: 'Sắp hết', className: 'bg-orange-100 text-orange-800' },
        out: { label: 'Hết hàng', className: 'bg-red-100 text-red-800' }
    };

    const config = statusConfig[status] || statusConfig.available;

    return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.className}`}>
            {config.label}
        </span>
    );
};

function formatCurrency(value) {
    if (!value) return '-';
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(value);
}

const ProductCard = ({ product, isExpanded, onToggle, variants, isLoadingVariants }) => {
    const stockSummary = product.stock_summary;

    return (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div
                className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={onToggle}
            >
                <div className="flex items-start gap-4">
                    <img
                        src={product.thumbnail || '/placeholder.png'}
                        alt={product.name}
                        className="w-20 h-20 object-cover rounded-md flex-shrink-0"
                    />

                    <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-800 mb-1 truncate">
                            {product.name}
                        </h3>

                        {product.brand && (
                            <p className="text-sm text-gray-600 mb-2">{product.brand.name}</p>
                        )}

                        {product.categories && product.categories.length > 0 && (
                            <div className="flex flex-wrap gap-1 mb-2">
                                {product.categories.map((cat) => (
                                    <span
                                        key={cat.id}
                                        className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full"
                                    >
                                        {cat.name}
                                    </span>
                                ))}
                            </div>
                        )}

                        <div className="flex items-center gap-4 text-sm">
                            <span className="text-gray-600">
                                Tổng tồn: <strong>{stockSummary.total_quantity}</strong>
                            </span>
                            <span className="text-gray-600">
                                Variants: <strong>{stockSummary.variants_in_stock}/{stockSummary.total_variants}</strong> có hàng
                            </span>
                            {stockSummary.variants_low_stock > 0 && (
                                <span className="text-orange-600 flex items-center gap-1">
                                    <AlertCircle className="w-4 h-4" />
                                    {stockSummary.variants_low_stock} sắp hết
                                </span>
                            )}
                            {stockSummary.variants_out_of_stock > 0 && (
                                <span className="text-red-600 flex items-center gap-1">
                                    <AlertCircle className="w-4 h-4" />
                                    {stockSummary.variants_out_of_stock} hết hàng
                                </span>
                            )}
                        </div>
                    </div>

                    <div className="flex-shrink-0">
                        {isExpanded ? (
                            <ChevronDown className="w-5 h-5 text-gray-400" />
                        ) : (
                            <ChevronRight className="w-5 h-5 text-gray-400" />
                        )}
                    </div>
                </div>
            </div>

            {isExpanded && (
                <div className="border-t border-gray-200 bg-gray-50">
                    {isLoadingVariants ? (
                        <div className="p-8 text-center">
                            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                            <p className="text-sm text-gray-600 mt-2">Đang tải variants...</p>
                        </div>
                    ) : variants && variants.variants ? (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-gray-100 border-b border-gray-200">
                                    <tr>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">Hình ảnh</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">SKU</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">Thuộc tính</th>
                                        <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700">Tồn</th>
                                        <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700">Giữ</th>
                                        <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700">Sẵn</th>
                                        <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700">Min</th>
                                        <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700">Giá vốn</th>
                                        <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700">Giá bán</th>
                                        <th className="px-4 py-3 text-center text-xs font-semibold text-gray-700">Trạng thái</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {variants.variants.map((variant) => (
                                        <tr key={variant.id} className="hover:bg-gray-50">
                                            <td className="px-4 py-3">
                                                <img
                                                    src={variant.image || '/placeholder.png'}
                                                    alt={`${variant.size} - ${variant.color_name}`}
                                                    className="w-12 h-12 object-cover rounded"
                                                />
                                            </td>
                                            <td className="px-4 py-3 text-sm text-gray-900 font-mono">
                                                {variant.sku}
                                            </td>
                                            <td className="px-4 py-3">
                                                <div className="text-sm">
                                                    <div className="font-medium text-gray-900">{variant.size}</div>
                                                    <div className="flex items-center gap-2 mt-1">
                                                        {variant.color_code && (
                                                            <div
                                                                className="w-4 h-4 rounded-full border border-gray-300"
                                                                style={{ backgroundColor: variant.color_code }}
                                                            ></div>
                                                        )}
                                                        <span className="text-gray-600">{variant.color_name}</span>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-4 py-3 text-right text-sm font-semibold text-gray-900">
                                                {variant.stock.quantity}
                                            </td>
                                            <td className="px-4 py-3 text-right text-sm text-gray-600">
                                                {variant.stock.reserved_quantity}
                                            </td>
                                            <td className="px-4 py-3 text-right text-sm font-semibold text-green-600">
                                                {variant.stock.available_quantity}
                                            </td>
                                            <td className="px-4 py-3 text-right text-sm text-gray-500">
                                                {variant.stock.min_stock_level || '-'}
                                            </td>
                                            <td className="px-4 py-3 text-right text-sm text-gray-700">
                                                {formatCurrency(variant.stock.cost_price)}
                                            </td>
                                            <td className="px-4 py-3 text-right text-sm font-medium text-gray-900">
                                                {formatCurrency(variant.price)}
                                            </td>
                                            <td className="px-4 py-3 text-center">
                                                <StatusBadge status={variant.stock.status} />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div className="p-8 text-center text-gray-500">
                            Không có variants
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default ProductCard;