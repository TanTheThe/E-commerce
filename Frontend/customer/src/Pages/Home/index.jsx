import React, { useContext, useState } from "react";
import HomeSlider from "../../components/HomeSlider";
import HomeCatSlider from "../../components/CatSlider";
import { LiaShippingFastSolid } from "react-icons/lia"
import AdsBannerSlider from "../../components/AdsBannerSlider";
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import ProductsSlider from "../../components/ProductsSlider";
import { Swiper, SwiperSlide } from "swiper/react";
import 'swiper/css'
import 'swiper/css/navigation'
import { Navigation } from "swiper/modules";
import BlogItem from "../../components/BlogItem";
import Footer from "../../components/Footer";
import HomeBannerV2 from "../../components/HomeSliderV2";
import BannerBoxV2 from "../../components/BannerBoxV2";
import AdsBannerSliderV2 from "../../components/AdsBannerSliderV2";
import { MyContext } from "../../App";
import BestSellerSection from "../../components/BestSeller";
import LatestSection from "../../components/Latest";
import TopDiscountSection from "../../components/TopDiscount";

const Home = () => {
    const [value, setValue] = useState(0);
    const context = useContext(MyContext)
    const parentCategories = context.categories.filter(category => category.parent_id === null);

    const handleChange = (event, newValue) => {
        setValue(newValue);
    };

    return (
        <>
            <HomeSlider />

            <section className="py-6">
                <div className="container flex gap-5">
                    <div className="part1 w-[65%]">
                        <HomeBannerV2/>
                    </div>
                    <div className="part2 w-[35%] flex items-center gap-5 justify-between flex-col">
                        <BannerBoxV2 info='right' images={'https://serviceapi.spicezgold.com/download/1741664665391_1741497254110_New_Project_50.jpg'}/>
                        <BannerBoxV2 info='left' images={'https://serviceapi.spicezgold.com/download/1741664496923_1737020250515_New_Project_47.jpg'}/>
                    </div>
                </div>
            </section>
            {/* <HomeCatSlider /> */}

            <BestSellerSection/>

            <section className="py-8 pt-2 bg-white">
                <div className="container">
                    <div className="freeShipping w-[80%] m-auto py-4 p-4 border-2 border-[#ff5252] flex items-center justify-between rounded-md mb-7">
                        <div className="col1 flex items-center gap-4">
                            <LiaShippingFastSolid className="text-[50px]" />
                            <span className="text-[20px] font-[600] uppercase">Free Shipping</span>
                        </div>

                        <div className="col2">
                            <p className="mb-0 font-[500]">Free Delivery Now On Your First Order and over $200</p>
                        </div>

                        <p className="font-bold text-[25px]">- Only $200*</p>
                    </div>

                    <AdsBannerSliderV2 items={4} />
                </div>
            </section>

            <LatestSection/>

            <TopDiscountSection/>

            <section className="py-5 pb-8 pt-0 bg-white blogSection">
                <div className="container">
                    <h2 className="text-[20px] font-[600] mb-4">From The Blog</h2>
                    <Swiper slidesPerView={4} spaceBetween={20} navigation={true} modules={[Navigation]} observer={true} observeParents={true} className="blogSlider">
                        <SwiperSlide>
                            <BlogItem/>
                        </SwiperSlide>
                        <SwiperSlide>
                            <BlogItem/>
                        </SwiperSlide>
                        <SwiperSlide>
                            <BlogItem/>
                        </SwiperSlide>
                        <SwiperSlide>
                            <BlogItem/>
                        </SwiperSlide>
                        <SwiperSlide>
                            <BlogItem/>
                        </SwiperSlide>
                        <SwiperSlide>
                            <BlogItem/>
                        </SwiperSlide>
                    </Swiper>
                </div>
            </section>
        </>
    )
}

export default Home