import React from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import 'swiper/css'
import 'swiper/css/navigation'
import { Navigation } from "swiper/modules";
import BannerBox from "../BannerBox";


const AdsBannerSlider = (props) => {
    return (
        <div className="py-5 w-full">
            <Swiper slidesPerView={props.items} spaceBetween={10} navigation={true} modules={[Navigation]} className="smlBtn">
                <SwiperSlide>
                    <BannerBox img='https://serviceapi.spicezgold.com/download/1741669012402_banner1.webp'/>
                </SwiperSlide>
                <SwiperSlide>
                    <BannerBox img='https://serviceapi.spicezgold.com/download/1741669037986_banner2.webp'/>
                </SwiperSlide>
                <SwiperSlide>
                    <BannerBox img='https://serviceapi.spicezgold.com/download/1741669057847_banner5.webp'/>
                </SwiperSlide>
                <SwiperSlide>
                    <BannerBox img='https://serviceapi.spicezgold.com/download/1742453755529_1741669087880_banner6.webp'/>
                </SwiperSlide>
                <SwiperSlide>
                    <BannerBox img='https://serviceapi.spicezgold.com/download/1747977151416_adBanner1.jpg'/>
                </SwiperSlide>
            </Swiper>
        </div>
    )
}

export default AdsBannerSlider