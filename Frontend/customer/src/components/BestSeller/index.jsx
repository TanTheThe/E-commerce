import React, { useState, useEffect, useContext } from 'react';
import { Tabs, Tab } from '@mui/material';
import ProductsSlider from '../ProductsSlider'
import { getDataApi } from '../../utils/api';
import { MyContext } from '../../App';

const BestSellerSection = () => {
    const context = useContext(MyContext);
    const [value, setValue] = useState(0);
    const [bestSellerData, setBestSellerData] = useState({});
    const [parentCategories, setParentCategories] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (context?.categories && context.categories.length > 0) {
            const parents = context.categories.filter(cat => cat.parent_id === null);
            setParentCategories(parents);

            if (parents.length > 0 && !bestSellerData[parents[0].id]) {
                fetchBestSellersForCategory(parents[0].id);
            }
        }
    }, [context?.categories]);

    const fetchBestSellersForCategory = async (parentCategoryId) => {
        try {
            const res = await getDataApi(`/customer/product/popular/${parentCategoryId}`);
            console.log(res);

            if (res.success) {
                setBestSellerData(prev => ({
                    ...prev,
                    [parentCategoryId]: res.data[parentCategoryId] || []
                }));
            }
        } catch (error) {
            console.error('Error fetching best sellers:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleChange = async (event, newValue) => {
        setValue(newValue);

        const selectedParentId = parentCategories[newValue]?.id;

        if (selectedParentId && !bestSellerData[selectedParentId]) {
            await fetchBestSellersForCategory(selectedParentId);
        }
    };

    const getCurrentCategoryProducts = () => {
        if (parentCategories.length === 0) return [];
        const currentParentId = parentCategories[value]?.id;
        return bestSellerData[currentParentId] || [];
    };

    if (loading && parentCategories.length === 0) {
        return (
            <section className="bg-white py-8">
                <div className="container">
                    <div className="text-center">Đang tải...</div>
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

                <ProductsSlider
                    items={6}
                    products={getCurrentCategoryProducts()}
                />
            </div>
        </section>
    );
};

export default BestSellerSection;