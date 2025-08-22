import React from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import 'swiper/css'
import 'swiper/css/navigation'
import { Navigation } from "swiper/modules";
import ProductItem from "../ProductItem";

const ProductsSlider = ({ items = 6, products = [] }) => {
    return (
        <div className="productsSlider py-3">
            <Swiper
                slidesPerView={items}
                spaceBetween={10}
                navigation={true}
                modules={[Navigation]}
                className="mySwiper"
                breakpoints={{
                    320: {
                        slidesPerView: 1,
                    },
                    640: {
                        slidesPerView: 2,
                    },
                    768: {
                        slidesPerView: 3,
                    },
                    1024: {
                        slidesPerView: 4,
                    },
                    1280: {
                        slidesPerView: items,
                    },
                }}
            >
                {products.length > 0 ? (
                    products.map((product) => (
                        <SwiperSlide key={product.id}>
                            <ProductItem product={product} />
                        </SwiperSlide>
                    ))
                ) : (
                    Array.from({ length: items }).map((_, index) => (
                        <SwiperSlide key={index}>
                            <ProductItem />
                        </SwiperSlide>
                    ))
                )}
            </Swiper>
        </div>
    );
}

export default ProductsSlider