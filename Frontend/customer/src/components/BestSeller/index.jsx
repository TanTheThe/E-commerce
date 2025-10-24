import React, { useState, useEffect, useContext } from 'react';
import { Tabs, Tab } from '@mui/material';
import ProductsSlider from '../ProductsSlider'
import { getDataApi } from '../../utils/api';
import { MyContext } from '../../App';

const BestSellerSection = () => {
    const [value, setValue] = useState(0);
    const [bestSellerData, setBestSellerData] = useState({});
    const [parentCategories, setParentCategories] = useState([]);

    const [loadingCategories, setLoadingCategories] = useState(true);
    const [loadingProducts, setLoadingProducts] = useState(false);
    const [fetchingCategories, setFetchingCategories] = useState(new Set());

    const fetchCategories = async () => {
        try {
            const res = await getDataApi("/customer/categories/all");
            if (res.success) {
                const categories = res.data.data;
                const parents = categories.filter(cat => cat.parent_id === null);
                setParentCategories(parents);
                setLoadingCategories(false);

                if (parents.length > 0 && parents[0]?.id && !bestSellerData[parents[0].id] && !fetchingCategories.has(parents[0].id)) {
                    fetchBestSellersForCategory(parents[0].id);
                }
            } else {
                setParentCategories([]);
                setLoadingCategories(false);
            }
        } catch (error) {
            console.error("Error fetching categories:", error);
            setParentCategories([]);
            setLoadingCategories(false);
        }
    };

    useEffect(() => {
        fetchCategories();
    }, []);

    const fetchBestSellersForCategory = async (parentCategoryId) => {
        if (!parentCategoryId || fetchingCategories.has(parentCategoryId)) {
            return;
        }

        setFetchingCategories(prev => new Set([...prev, parentCategoryId]));
        setLoadingProducts(true);

        try {
            const timeoutPromise = new Promise((_, reject) => {
                setTimeout(() => reject(new Error('Request timeout')), 10000);
            });

            const apiPromise = getDataApi(`/customer/product/popular/${parentCategoryId}`);

            const res = await Promise.race([apiPromise, timeoutPromise]);

            if (res && res.success) {
                setBestSellerData(prev => ({
                    ...prev,
                    [parentCategoryId]: res.data[parentCategoryId] || []
                }));
            } else {
                console.warn("API returned unsuccessful response:", res);
                setBestSellerData(prev => ({
                    ...prev,
                    [parentCategoryId]: []
                }));
            }
        } catch (error) {
            console.error("Error fetching best sellers:", error);
            setBestSellerData(prev => ({
                ...prev,
                [parentCategoryId]: []
            }));
        } finally {
            setLoadingProducts(false);
            setFetchingCategories(prev => {
                const newSet = new Set(prev);
                newSet.delete(parentCategoryId);
                return newSet;
            });
        }
    };

    const handleChange = async (event, newValue) => {
        setValue(newValue);

        const selectedParentId = parentCategories[newValue]?.id;
        if (selectedParentId &&
            !bestSellerData[selectedParentId] &&
            !fetchingCategories.has(selectedParentId)) {
            await fetchBestSellersForCategory(selectedParentId);
        }
    };

    const getCurrentCategoryProducts = () => {
        if (parentCategories.length === 0) return [];
        const currentParentId = parentCategories[value]?.id;
        return bestSellerData[currentParentId] || [];
    };

    if (loadingCategories) {
        return (
            <section className="bg-white py-8">
                <div className="container">
                    <div className="text-center">Đang tải danh mục...</div>
                </div>
            </section>
        );
    }

    if (!loadingCategories && parentCategories.length === 0) {
        return (
            <section className="bg-white py-8">
                <div className="container">
                    <div className="text-center">Không có danh mục nào.</div>
                </div>
            </section>
        );
    }

    return (
        <section className="bg-white py-8">
            <div className="container">
                <div className="flex items-center justify-between">
                    <div className="leftSec">
                        <h2 className="text-[20px] font-[600]">Sản phẩm phổ biến</h2>
                        <p className="text-[14px] font-[400]">Những sản phẩm bán chạy nhất trong tháng vừa rồi.</p>
                    </div>
                    <div className="rightSec w-[65%]">
                        <Tabs
                            value={value}
                            onChange={handleChange}
                            variant="scrollable"
                            scrollButtons="auto"
                            aria-label="best seller categories"
                        >
                            {parentCategories.map((category, index) => (
                                <Tab key={category.id} label={category.name} />
                            ))}
                        </Tabs>
                    </div>
                </div>

                {loadingProducts ? (
                    <div className="text-center py-6">Đang tải sản phẩm...</div>
                ) : (
                    <ProductsSlider items={6} products={getCurrentCategoryProducts()} />
                )}
            </div>
        </section>
    );
};

export default BestSellerSection;