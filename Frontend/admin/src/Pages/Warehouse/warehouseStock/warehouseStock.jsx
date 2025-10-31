import React, { useState, useEffect, useCallback, useContext } from 'react';
import {
    ChevronDown,
    ChevronRight,
    Search,
    Package,
    Layers,
    TrendingUp,
    DollarSign,
    AlertCircle,
    X,
    ArrowUpDown
} from 'lucide-react';
import SummaryCard from './summaryCard';
import HierarchicalCategorySelect from './hierarchicalCategorySelect';
import ProductsListSkeleton from './productListSkeleton';
import ProductCard from './productCard';
import { getDataApi } from '../../../utils/api';
import PurchaseOrdersManagement from '../purchaseOrder/purchaseOrderManagement';
import GoodsReceiptsManagement from '../goodsReceipt/goodsReceiptManagement';
import ReturnPurchaseManagement from '../returnPurchase/returnPurchaseManagement';


function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatCurrency(value) {
    if (!value) return '-';
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(value);
}

const WarehouseStock = ({ warehouse, onClose }) => {
    const [activeTab, setActiveTab] = useState('stock');

    const [filtersData, setFiltersData] = useState({
        categories: [],
        brands: [],
        stock_statuses: []
    });
    const [allCategories, setAllCategories] = useState([]);

    const [selectedCategoryIds, setSelectedCategoryIds] = useState([]);
    const [selectedBrandIds, setSelectedBrandIds] = useState([]);
    const [stockStatus, setStockStatus] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [sortBy, setSortBy] = useState('name');
    const [sortOrder, setSortOrder] = useState('asc');

    const [products, setProducts] = useState([]);
    const [totalProducts, setTotalProducts] = useState(0);
    const [currentPage, setCurrentPage] = useState(1);
    const limit = 10;

    const [summary, setSummary] = useState(null);

    const [isLoading, setIsLoading] = useState(false);
    const [isLoadingSummary, setIsLoadingSummary] = useState(false);
    const [expandedProductIds, setExpandedProductIds] = useState(new Set());
    const [variantsCache, setVariantsCache] = useState(new Map());
    const [loadingVariants, setLoadingVariants] = useState(new Set());

    const fetchFilters = async () => {
        try {
            const response = await getDataApi(`/admin/stock/warehouse/${warehouse.id}/filters`);
            if (response.success) {
                setFiltersData(response.data);
            }
        } catch (error) {
            console.error('Error fetching filters:', error);
        }
    };

    const fetchSummary = async () => {
        setIsLoadingSummary(true);
        try {
            const response = await getDataApi(`/admin/stock/warehouse/${warehouse.id}/stocks/summary`);
            if (response.success) {
                setSummary(response.data.summary);
            }
        } catch (error) {
            console.error('Error fetching summary:', error);
        } finally {
            setIsLoadingSummary(false);
        }
    };

    const fetchProducts = async () => {
        setIsLoading(true);
        try {
            const skip = (currentPage - 1) * limit;
            const queryParams = new URLSearchParams({
                skip: skip.toString(),
                limit: limit.toString(),
                sort_by: sortBy,
                sort_order: sortOrder,
                stock_status: stockStatus
            });

            if (searchQuery) queryParams.append('search', searchQuery);
            if (selectedCategoryIds.length > 0) {
                selectedCategoryIds.forEach(id => queryParams.append('category_ids', id));
            }
            if (selectedBrandIds.length > 0) {
                selectedBrandIds.forEach(id => queryParams.append('brand_ids', id));
            }

            const response = await getDataApi(
                `/admin/stock/warehouse/${warehouse.id}/products?${queryParams.toString()}`
            );

            if (response.success) {
                setProducts(response.data.data || []);
                setTotalProducts(response.data.total || 0);
            }
        } catch (error) {
            console.error('Error fetching products:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const fetchVariants = async (productId) => {
        if (variantsCache.has(productId)) {
            return;
        }

        setLoadingVariants(prev => new Set([...prev, productId]));
        try {
            const response = await getDataApi(
                `/admin/stock/warehouse/${warehouse.id}/products/${productId}/variants`
            );

            if (response.success) {
                setVariantsCache(prev => new Map(prev).set(productId, response.data));
            }
        } catch (error) {
            console.error('Error fetching variants:', error);
        } finally {
            setLoadingVariants(prev => {
                const newSet = new Set(prev);
                newSet.delete(productId);
                return newSet;
            });
        }
    };

    const fetchCategories = async () => {
        try {
            const queryParams = new URLSearchParams({
                skip: "0",
                limit: "1000",
            });

            const res = await getDataApi(`/admin/categories/all?${queryParams.toString()}`);
            if (res.success === true) {
                setAllCategories(res.data.data || []);
            } else {
                console.error("Failed to fetch categories:", res.message);
                setAllCategories([]);
            }
        } catch (error) {
            console.error("Error fetching categories:", error);
            setAllCategories([]);
        }
    };

    useEffect(() => {
        Promise.all([fetchCategories(), fetchFilters(), fetchSummary(), fetchProducts()]);
    }, []);

    useEffect(() => {
        setCurrentPage(1);
    }, [selectedCategoryIds, selectedBrandIds, stockStatus, searchQuery, sortBy, sortOrder]);

    useEffect(() => {
        fetchProducts();
    }, [currentPage, selectedCategoryIds, selectedBrandIds, stockStatus, searchQuery, sortBy, sortOrder]);

    const debouncedSearch = useCallback(
        debounce((value) => {
            setSearchQuery(value);
        }, 300),
        []
    );

    const toggleProductExpansion = (productId) => {
        const newExpanded = new Set(expandedProductIds);
        if (newExpanded.has(productId)) {
            newExpanded.delete(productId);
        } else {
            newExpanded.add(productId);
            fetchVariants(productId);
        }
        setExpandedProductIds(newExpanded);
    };

    const toggleSortOrder = () => {
        setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
    };

    const totalPages = Math.ceil(totalProducts / limit);

    return (
        <div className="h-screen flex flex-col bg-gray-50">
            <div className="bg-white border-b border-gray-200">
                <div className="flex items-center px-6 py-3">
                    <button
                        className={`px-6 py-2 font-medium text-sm transition-colors ${activeTab === 'stock'
                            ? 'text-blue-600 border-b-2 border-blue-600'
                            : 'text-gray-500 hover:text-gray-700'
                            }`}
                        onClick={() => setActiveTab('stock')}
                    >
                        Tồn kho
                    </button>
                    <button
                        className={`px-6 py-2 font-medium text-sm transition-colors ${activeTab === 'orders'
                            ? 'text-blue-600 border-b-2 border-blue-600'
                            : 'text-gray-500 hover:text-gray-700'
                            }`}
                        onClick={() => setActiveTab('orders')}
                    >
                        Quản lý đơn đặt hàng
                    </button>
                    <button
                        className={`px-6 py-2 font-medium text-sm transition-colors ${activeTab === 'receipts'
                            ? 'text-blue-600 border-b-2 border-blue-600'
                            : 'text-gray-500 hover:text-gray-700'
                            }`}
                        onClick={() => setActiveTab('receipts')}
                    >
                        Quản lý phiếu nhập kho
                    </button>
                    <button
                        className={`px-6 py-2 font-medium text-sm transition-colors ${activeTab === 'returns'
                                ? 'text-blue-600 border-b-2 border-blue-600'
                                : 'text-gray-500 hover:text-gray-700'
                            }`}
                        onClick={() => setActiveTab('returns')}
                    >
                        Quản lý phiếu trả hàng
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-auto">
                {activeTab === 'stock' ? (
                    <div className="p-6">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                            <SummaryCard
                                icon={<Package className="w-6 h-6" />}
                                label="Tổng sản phẩm"
                                value={summary?.total_products || 0}
                                color="blue"
                                isLoading={isLoadingSummary}
                            />
                            <SummaryCard
                                icon={<Layers className="w-6 h-6" />}
                                label="Tổng variants"
                                value={summary?.total_variants || 0}
                                color="purple"
                                isLoading={isLoadingSummary}
                            />
                            <SummaryCard
                                icon={<TrendingUp className="w-6 h-6" />}
                                label="Tổng số lượng"
                                value={summary?.total_quantity || 0}
                                color="green"
                                isLoading={isLoadingSummary}
                            />
                            <SummaryCard
                                icon={<DollarSign className="w-6 h-6" />}
                                label="Giá trị kho"
                                value={formatCurrency(summary?.total_value || 0)}
                                color="orange"
                                isLoading={isLoadingSummary}
                            />
                        </div>

                        <div className="bg-white rounded-lg shadow-sm p-4 mb-4">
                            <div className="flex items-center gap-4">
                                <div className="flex-1 relative">
                                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                                    <input
                                        type="text"
                                        placeholder="Tìm kiếm sản phẩm..."
                                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        onChange={(e) => debouncedSearch(e.target.value)}
                                    />
                                </div>

                                <select
                                    value={sortBy}
                                    onChange={(e) => setSortBy(e.target.value)}
                                    className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="name">Tên sản phẩm</option>
                                    <option value="total_quantity">Số lượng</option>
                                    <option value="updated_at">Cập nhật gần đây</option>
                                </select>

                                <button
                                    onClick={toggleSortOrder}
                                    className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                                    title={sortOrder === 'asc' ? 'Tăng dần' : 'Giảm dần'}
                                >
                                    <ArrowUpDown className="w-4 h-4" />
                                </button>
                            </div>
                        </div>

                        <div className="flex gap-6">
                            <div className="w-1/4">
                                <div className="bg-white rounded-lg shadow-sm p-4 sticky top-4">
                                    <h3 className="font-semibold text-gray-800 mb-4">Bộ lọc</h3>

                                    <div className="mb-6">
                                        <HierarchicalCategorySelect
                                            categories={allCategories}
                                            selectedCategoryIds={selectedCategoryIds}
                                            onSelectionChange={setSelectedCategoryIds}
                                            label="Danh mục"
                                            placeholder="Tất cả danh mục"
                                        />
                                    </div>

                                    <div className="mb-6">
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Thương hiệu
                                        </label>
                                        <div className="max-h-48 overflow-y-auto border border-gray-200 rounded-md">
                                            {filtersData.brands.map((brand) => (
                                                <label
                                                    key={brand.id}
                                                    className="flex items-center px-3 py-2 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
                                                >
                                                    <input
                                                        type="checkbox"
                                                        checked={selectedBrandIds.includes(brand.id)}
                                                        onChange={(e) => {
                                                            if (e.target.checked) {
                                                                setSelectedBrandIds([...selectedBrandIds, brand.id]);
                                                            } else {
                                                                setSelectedBrandIds(selectedBrandIds.filter(id => id !== brand.id));
                                                            }
                                                        }}
                                                        className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                                    />
                                                    <span className="text-sm text-gray-700 flex-1">{brand.name}</span>
                                                    <span className="text-xs text-gray-500">({brand.product_count})</span>
                                                </label>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="mb-4">
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Trạng thái tồn kho
                                        </label>
                                        <div className="space-y-2">
                                            {filtersData.stock_statuses.map((status) => (
                                                <label
                                                    key={status.value}
                                                    className="flex items-center cursor-pointer hover:bg-gray-50 p-2 rounded"
                                                >
                                                    <input
                                                        type="radio"
                                                        name="stockStatus"
                                                        value={status.value}
                                                        checked={stockStatus === status.value}
                                                        onChange={(e) => setStockStatus(e.target.value)}
                                                        className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                    />
                                                    <span className="text-sm text-gray-700 flex-1">{status.label}</span>
                                                    <span className="text-xs text-gray-500">({status.count})</span>
                                                </label>
                                            ))}
                                            <label className="flex items-center cursor-pointer hover:bg-gray-50 p-2 rounded">
                                                <input
                                                    type="radio"
                                                    name="stockStatus"
                                                    value="all"
                                                    checked={stockStatus === 'all'}
                                                    onChange={(e) => setStockStatus(e.target.value)}
                                                    className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                />
                                                <span className="text-sm text-gray-700 flex-1">Tất cả</span>
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex-1">
                                {isLoading ? (
                                    <ProductsListSkeleton />
                                ) : products.length === 0 ? (
                                    <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                                        <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                                        <p className="text-gray-500 text-lg">Không tìm thấy sản phẩm nào</p>
                                    </div>
                                ) : (
                                    <>
                                        <div className="space-y-4 mb-6">
                                            {products.map((product) => (
                                                <ProductCard
                                                    key={product.id}
                                                    product={product}
                                                    isExpanded={expandedProductIds.has(product.id)}
                                                    onToggle={() => toggleProductExpansion(product.id)}
                                                    variants={variantsCache.get(product.id)}
                                                    isLoadingVariants={loadingVariants.has(product.id)}
                                                />
                                            ))}
                                        </div>

                                        {totalPages > 1 && (
                                            <div className="flex items-center justify-between bg-white rounded-lg shadow-sm p-4">
                                                <div className="text-sm text-gray-600">
                                                    Trang {currentPage} / {totalPages} · Tổng: {totalProducts} sản phẩm
                                                </div>
                                                <div className="flex gap-2">
                                                    <button
                                                        onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                                                        disabled={currentPage === 1}
                                                        className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                                    >
                                                        Trước
                                                    </button>
                                                    <button
                                                        onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
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
                        </div>
                    </div>
                ) : activeTab === 'orders' ? (
                    <PurchaseOrdersManagement warehouse={warehouse} />
                ) : activeTab === 'receipts' ? (
                    <GoodsReceiptsManagement warehouse={warehouse} />
                ) : activeTab === 'returns' ? (
                    <ReturnPurchaseManagement warehouse={warehouse} />
                ) : null}
            </div>
        </div>
    );
};

export default WarehouseStock;