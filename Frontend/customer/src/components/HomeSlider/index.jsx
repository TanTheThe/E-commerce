import React from "react";
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Autoplay } from 'swiper/modules'
import 'swiper/css';
import 'swiper/css/navigation';

const HomeSlider = () => {
    return (
        <div className="homeSlider py-4">
            <div className="container">
                <Swiper loop={true} spaceBetween={10} navigation={true} modules={[Navigation, Autoplay]} autoplay={{delay:2500, disableOnInteraction:false}} className="sliderHome">
                    <SwiperSlide>
                        <div className="item rounded-[20px] overflow-hidden">
                            <img src="https://api.spicezgold.com/download/file_1734524930884_NewProject(6).jpg" className="w-full"/>
                        </div>
                    </SwiperSlide>
                    <SwiperSlide>
                        <div className="item rounded-[20px] overflow-hidden">
                            <img src="https://api.spicezgold.com/download/file_1734524971122_NewProject(8).jpg" className="w-full"/>
                        </div>
                    </SwiperSlide>
                    <SwiperSlide>
                        <div className="item rounded-[20px] overflow-hidden">
                            <img src="https://api.spicezgold.com/download/file_1734524985581_NewProject(11).jpg" className="w-full"  />
                        </div>
                    </SwiperSlide>
                    <SwiperSlide>
                        <div className="item rounded-[20px] overflow-hidden">
                            <img src="https://api.spicezgold.com/download/file_1734525002307_1723967638078_slideBanner1.6bbeed1a0c8ffb494f7c.jpg" className="w-full"/>
                        </div>
                    </SwiperSlide>
                    <SwiperSlide>
                        <div className="item rounded-[20px] overflow-hidden">
                            <img src="https://api.spicezgold.com/download/file_1734525014348_NewProject(7).jpg" className="w-full"/>
                        </div>
                    </SwiperSlide>
                </Swiper>
            </div>
        </div>

    )
}

export default HomeSlider