import React, { useRef, useState } from "react";
import InnerImageZoom from 'react-inner-image-zoom';
import 'react-inner-image-zoom/lib/styles.min.css';
import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "swiper/css/navigation";
import { Navigation } from "swiper/modules";

const ProductZoom = ({ images = [] }) => {
    const [slideIndex, setSlideIndex] = useState(0);
    const zoomSliderBig = useRef();
    const zoomSliderSmall = useRef();

    const goto = (index) => {
        setSlideIndex(index);
        zoomSliderSmall.current?.swiper.slideTo(index);
        zoomSliderBig.current?.swiper.slideTo(index);
    };

    const displayImages = images && images.length > 0 ? images : ['/placeholder-image.jpg'];

    return (
        <>
            <div className="flex gap-3">
                <div className="slider w-[15%]">
                    <Swiper
                        ref={zoomSliderSmall}
                        direction="vertical"
                        slidesPerView={Math.min(4, displayImages.length)}
                        spaceBetween={10}
                        navigation={true}
                        modules={[Navigation]}
                        className="zoomProductSliderThumbs h-[500px] overflow-hidden"
                    >
                        {displayImages.map((image, index) => (
                            <SwiperSlide key={index}>
                                <div
                                    className={`item rounded-md overflow-hidden cursor-pointer group ${slideIndex === index ? 'opacity-100' : 'opacity-30'}`}
                                    onClick={() => goto(index)}
                                >
                                    <img
                                        src={image}
                                        className="w-full h-full object-cover transition-all group-hover:scale-105"
                                        alt={`Product thumbnail ${index + 1}`}
                                        onError={(e) => {
                                            e.target.src = '/placeholder-image.jpg';
                                        }}
                                    />
                                </div>
                            </SwiperSlide>
                        ))}
                    </Swiper>
                </div>

                <div className="zoomContainer w-[85%] h-[500px] overflow-hidden rounded-md">
                    <Swiper
                        ref={zoomSliderBig}
                        slidesPerView={1}
                        spaceBetween={0}
                        navigation={false}
                    >
                        {displayImages.map((image, index) => (
                            <SwiperSlide key={index}>
                                <InnerImageZoom
                                    zoomType="hover"
                                    zoomScale={1}
                                    src={image}
                                    className="w-full h-full object-cover"
                                    onError={(e) => {
                                        e.target.src = '/placeholder-image.jpg';
                                    }}
                                />
                            </SwiperSlide>
                        ))}
                    </Swiper>
                </div>
            </div>
        </>
    );
};

export default ProductZoom