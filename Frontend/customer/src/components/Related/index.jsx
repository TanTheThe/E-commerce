import React, { useState, useEffect } from 'react';
import { Tabs, Tab } from '@mui/material';
import ProductsSlider from '../ProductsSlider'
import { getDataApi } from '../../utils/api';

const RelatedSection = ({ productId }) => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchRelatedProducts = async () => {
            if (!productId) return;

            try {
                setLoading(true);
                const res = await getDataApi(`/customer/product/related?product_id=${productId}`);
                console.log(res);

                if (res.success) {
                    setProducts(res.data || []);
                }
            } catch (error) {
                console.error('Error fetching related products:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchRelatedProducts();
    }, [productId]);

    if (loading) {
        return (
            <div className="container pt-8">
                <div className="text-center">Đang tải sản phẩm liên quan...</div>
            </div>
        );
    }

    return (
        <div className="container pt-8">
            <h2 className="text-[20px] font-[600]">Sản phẩm liên quan</h2>
            <ProductsSlider items={6} products={products} />
        </div>
    );
};

export default RelatedSection;