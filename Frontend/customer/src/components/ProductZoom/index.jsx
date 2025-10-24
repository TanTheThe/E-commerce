import React, { useRef, useState } from "react";
import InnerImageZoom from 'react-inner-image-zoom';
import 'react-inner-image-zoom/lib/styles.min.css';
import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "swiper/css/navigation";
import { Navigation } from "swiper/modules";
import CustomImageZoom from "./customImageZoom";

const ProductZoom = ({ images = [] }) => {
    const [slideIndex, setSlideIndex] = useState(0);
    const zoomSliderBig = useRef();
    const zoomSliderSmall = useRef();

    const goto = (index) => {
        const previousIndex = slideIndex;
        setSlideIndex(index);

        zoomSliderSmall.current?.swiper.slideTo(index);
        zoomSliderBig.current?.swiper.slideTo(index);

        if (zoomSliderSmall.current?.swiper && displayImages.length > 4) {
            const swiper = zoomSliderSmall.current.swiper;
            const totalSlides = displayImages.length;
            const visibleSlides = 4;

            let scrollToIndex = index;

            if (index > previousIndex) {
                if (index >= Math.min(swiper.activeIndex + visibleSlides - 1, totalSlides - 1)) {
                    scrollToIndex = Math.min(index - visibleSlides + 2, totalSlides - visibleSlides);
                }
            } else if (index < previousIndex) {
                if (index <= swiper.activeIndex) {
                    scrollToIndex = Math.max(index - 1, 0);
                }
            }

            if (scrollToIndex !== swiper.activeIndex) {
                swiper.slideTo(scrollToIndex);
            }
        }
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
                        onSlideChange={(swiper) => {
                            if (swiper.activeIndex !== slideIndex) {
                                const visibleRange = {
                                    start: swiper.activeIndex,
                                    end: Math.min(swiper.activeIndex + swiper.params.slidesPerView - 1, displayImages.length - 1)
                                };

                                if (slideIndex < visibleRange.start || slideIndex > visibleRange.end) {
                                    setSlideIndex(visibleRange.start);
                                    zoomSliderBig.current?.swiper.slideTo(visibleRange.start);
                                }
                            }
                        }}
                    >
                        {displayImages.map((image, index) => (
                            <SwiperSlide key={index}>
                                <div
                                    className={`item rounded-md overflow-hidden cursor-pointer group transition-opacity duration-200 ${slideIndex === index ? 'opacity-100' : 'opacity-60 hover:opacity-80'
                                        }`}
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
                        allowTouchMove={false}
                    >
                        {displayImages.map((image, index) => (
                            <SwiperSlide key={index}>
                                <CustomImageZoom
                                    src={image}
                                    alt={`Product ${index + 1}`}
                                    className="w-full h-full object-cover"
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