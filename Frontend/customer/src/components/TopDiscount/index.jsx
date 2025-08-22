import React, { useState, useEffect } from 'react';
import { Tabs, Tab } from '@mui/material';
import ProductsSlider from '../ProductsSlider'
import { getDataApi } from '../../utils/api';

const TopDiscountSection = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchLatest = async () => {
            try {
                setLoading(true);
                const res = await getDataApi("/customer/product/top-discount");
                console.log(res);

                if (res.success) {
                    setProducts(res.data || []);
                }
            } catch (error) {
                console.error('Error fetching best sellers:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchLatest();
    }, []);

    if (loading) {
        return (
            <section className="bg-white py-8">
                <div className="container">
                    <div className="text-center">Đang tải...</div>
                </div>
            </section>
        );
    }

    return (
        <section className="bg-white py-2">
            <div className="container">
                <div className="leftSec mb-3">
                    <h2 className="text-[20px] font-[600]">Sản phẩm giảm giá sâu nhất</h2>
                    <p className="text-[14px] font-[400]">Những sản phẩm đang có chương trình giảm giá tốt nhất.</p>
                </div>

                <ProductsSlider
                    items={6}
                    products={products}
                />
            </div>
        </section>
    );
};

export default TopDiscountSection;