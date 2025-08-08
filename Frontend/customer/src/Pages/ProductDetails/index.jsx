import Breadcrumbs from "@mui/material/Breadcrumbs";
import React, { useState } from "react";
import { Link } from "react-router-dom";
import ProductZoom from "../../components/ProductZoom";
import Rating from '@mui/material/Rating';
import { Button } from "@mui/material";
import TextField from '@mui/material/TextField';
import ProductsSlider from '../../components/ProductsSlider'
import ProductDetailsComponent from "../../components/ProductDetails";

const ProductDetails = () => {
    const [activeTab, setActiveTab] = useState(0)

    return (
        <>
            <div className="py-5">
                <div className="container">
                    <Breadcrumbs aria-label="breadcrumb">
                        <Link underline="hover" color="inherit" href="/" className="link transition !text-[14px]">
                            Home
                        </Link>
                        <Link
                            underline="hover"
                            color="inherit"
                            href="/"
                            className="link transition !text-[14px]"
                        >
                            Fashion
                        </Link>
                        <Link
                            underline="hover"
                            color="inherit"
                            className="link transition !text-[14px]"
                        >
                            Cropped Satin Bomber Jacket
                        </Link>
                    </Breadcrumbs>
                </div>
            </div>

            <section className="bg-white py-5">
                <div className="container flex gap-8">
                    <div className="productZoomContainer w-[40%]">
                        <ProductZoom />
                    </div>
                    <div className="productContent w-[60%] pr-10 pt-5">
                        <ProductDetailsComponent/>
                    </div>
                </div>

                <div className="container pt-10">
                    <div className="flex items-center gap-8 mb-5">
                        <span onClick={() => setActiveTab(0)} className={`link text-[17px] cursor-pointer font-[500] ${activeTab === 0 && 'text-[#ff5252]'}`}>Description</span>
                        <span onClick={() => setActiveTab(1)} className={`link text-[17px] cursor-pointer font-[500] ${activeTab === 1 && 'text-[#ff5252]'}`}>Product Details</span>
                        <span onClick={() => setActiveTab(2)} className={`link text-[17px] cursor-pointer font-[500] ${activeTab === 2 && 'text-[#ff5252]'}`}>Reviews (5)</span>
                    </div>

                    {
                        activeTab === 0 &&
                        <div className="shadow-md w-full py-5 px-8 rounded-md">
                            <p>In this single tutorial we will make a full stack eCommerce website using (MERN) React JS, MongoDB, Express and Node JS or Online Store using React JS.
                                We will make the e-commerce front-end website to display products, product cart and login registration page using React JS.</p>

                            <h4>Lightweight Design</h4>

                            <p>Then we will make the back-end of the website using express, node js, mongo db and react js. Where we will create the APIs to add product, display product,
                                update product, update cart items and login registration API. We will also make the admin panel of our eCommerce website to add product, update product on
                                our e-commerce website.</p>

                            <h4>Free Shipping & Return</h4>

                            <p>In this single tutorial we will make a full stack eCommerce website using (MERN) React JS, MongoDB, Express and Node JS or Online Store using React JS</p>

                            <h4>Money Back Guarantee</h4>

                            <p>Where we will create the APIs to add product, display product, update product, update cart items and login registration API. We will also make the admin
                                panel of our eCommerce website to add product, update product on our e-commerce website.</p>

                            <h4>Online Support</h4>

                            <p>We will make the e-commerce front-end website to display products, product cart and login registration page using React JS.</p>
                        </div>
                    }

                    {
                        activeTab === 1 &&
                        <div className="shadow-md w-full py-5 px-8 rounded-md">
                            <div class="relative overflow-x-auto">
                                <table class="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
                                    <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                                        <tr>
                                            <th scope="col" class="px-6 py-3">
                                                Stand Up
                                            </th>
                                            <th scope="col" class="px-6 py-3">
                                                Folded (w/o wheels)
                                            </th>
                                            <th scope="col" class="px-6 py-3">
                                                Folded (w/ wheels)
                                            </th>
                                            <th scope="col" class="px-6 py-3">
                                                Door Pass Through
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200">
                                            <td class="px-6 py-4 font-[500]">
                                                35″L x 24″W x 37-45″H(front to back wheel)
                                            </td>
                                            <td class="px-6 py-4 font-[500]">
                                                32.5″L x 18.5″W x 16.5″H
                                            </td>
                                            <td class="px-6 py-4 font-[500]">
                                                32.5″L x 24″W x 18.5″H
                                            </td>
                                            <td class="px-6 py-4 font-[500]">
                                                24
                                            </td>
                                        </tr>
                                        <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200">
                                            <td class="px-6 py-4 font-[500]">
                                                35″L x 24″W x 37-45″H(front to back wheel)
                                            </td>
                                            <td class="px-6 py-4 font-[500]">
                                                32.5″L x 18.5″W x 16.5″H
                                            </td>
                                            <td class="px-6 py-4 font-[500]">
                                                32.5″L x 24″W x 18.5″H
                                            </td>
                                            <td class="px-6 py-4 font-[500]">
                                                24
                                            </td>
                                        </tr>
                                        <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200">
                                            <td class="px-6 py-4 font-[500]">
                                                35″L x 24″W x 37-45″H(front to back wheel)
                                            </td>
                                            <td class="px-6 py-4 font-[500]">
                                                32.5″L x 18.5″W x 16.5″H
                                            </td>
                                            <td class="px-6 py-4 font-[500]">
                                                32.5″L x 24″W x 18.5″H
                                            </td>
                                            <td class="px-6 py-4 font-[500]">
                                                24
                                            </td>
                                        </tr>
                                        <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200">
                                            <td class="px-6 py-4 font-[500]">
                                                35″L x 24″W x 37-45″H(front to back wheel)
                                            </td>
                                            <td class="px-6 py-4 font-[500]">
                                                32.5″L x 18.5″W x 16.5″H
                                            </td>
                                            <td class="px-6 py-4 font-[500]">
                                                32.5″L x 24″W x 18.5″H
                                            </td>
                                            <td class="px-6 py-4 font-[500]">
                                                24
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    }

                    {
                        activeTab === 2 &&
                        <div className="shadow-md w-[80%] py-5 px-8 rounded-md">
                            <div className="w-full productReviewsContainer">
                                <h2 className="text-[18px]">Custom questions & answers</h2>

                                <div className="reviewScroll w-full max-h-[300px] overflow-y-scroll overflow-x-hidden mt-5 pr-5">
                                    <div className="review pb-5 border-b border-[rgba(0,0,0,0.1)] w-full flex items-center justify-between">
                                        <div className="info w-[60%] flex items-center gap-2">
                                            <div className="img w-[80px] h-[80px] overflow-hidden rounded-full">
                                                <img src="https://thethaovanhoa.mediacdn.vn/372676912336973824/2022/12/16/avatar3-1671164179193908857633.jpg" className="w-full" />
                                            </div>

                                            <div className="w-[80%]">
                                                <h4 className="text-[16px]">Rinku Verma</h4>
                                                <h5 className="text-[13px] mb-0">2024-12-01</h5>
                                                <p className="mt-0 mb-0">In this single tutorial we will make a full stack eCommerce website using (MERN) React JS, MongoDB, Express and
                                                    Node JS or Online Store using React JS. We will make the e-commerce front-end website to display products, product cart and login
                                                    registration page using React JS.</p>

                                            </div>
                                        </div>
                                        <Rating name="size-small" defaultValue={2} readOnly />
                                    </div>
                                    <div className="review pb-5 border-b border-[rgba(0,0,0,0.1)] w-full flex items-center justify-between">
                                        <div className="info w-[60%] flex items-center gap-2">
                                            <div className="img w-[80px] h-[80px] overflow-hidden rounded-full">
                                                <img src="https://thethaovanhoa.mediacdn.vn/372676912336973824/2022/12/16/avatar3-1671164179193908857633.jpg" className="w-full" />
                                            </div>

                                            <div className="w-[80%]">
                                                <h4 className="text-[16px]">Rinku Verma</h4>
                                                <h5 className="text-[13px] mb-0">2024-12-01</h5>
                                                <p className="mt-0 mb-0">In this single tutorial we will make a full stack eCommerce website using (MERN) React JS, MongoDB, Express and
                                                    Node JS or Online Store using React JS. We will make the e-commerce front-end website to display products, product cart and login
                                                    registration page using React JS.</p>

                                            </div>
                                        </div>
                                        <Rating name="size-small" defaultValue={2} readOnly />
                                    </div>
                                    <div className="review pb-5 border-b border-[rgba(0,0,0,0.1)] w-full flex items-center justify-between">
                                        <div className="info w-[60%] flex items-center gap-2">
                                            <div className="img w-[80px] h-[80px] overflow-hidden rounded-full">
                                                <img src="https://thethaovanhoa.mediacdn.vn/372676912336973824/2022/12/16/avatar3-1671164179193908857633.jpg" className="w-full" />
                                            </div>

                                            <div className="w-[80%]">
                                                <h4 className="text-[16px]">Rinku Verma</h4>
                                                <h5 className="text-[13px] mb-0">2024-12-01</h5>
                                                <p className="mt-0 mb-0">In this single tutorial we will make a full stack eCommerce website using (MERN) React JS, MongoDB, Express and
                                                    Node JS or Online Store using React JS. We will make the e-commerce front-end website to display products, product cart and login
                                                    registration page using React JS.</p>

                                            </div>
                                        </div>
                                        <Rating name="size-small" defaultValue={2} readOnly />
                                    </div>
                                    <div className="review pb-5 border-b border-[rgba(0,0,0,0.1)] w-full flex items-center justify-between">
                                        <div className="info w-[60%] flex items-center gap-2">
                                            <div className="img w-[80px] h-[80px] overflow-hidden rounded-full">
                                                <img src="https://thethaovanhoa.mediacdn.vn/372676912336973824/2022/12/16/avatar3-1671164179193908857633.jpg" className="w-full" />
                                            </div>

                                            <div className="w-[80%]">
                                                <h4 className="text-[16px]">Rinku Verma</h4>
                                                <h5 className="text-[13px] mb-0">2024-12-01</h5>
                                                <p className="mt-0 mb-0">In this single tutorial we will make a full stack eCommerce website using (MERN) React JS, MongoDB, Express and
                                                    Node JS or Online Store using React JS. We will make the e-commerce front-end website to display products, product cart and login
                                                    registration page using React JS.</p>

                                            </div>
                                        </div>
                                        <Rating name="size-small" defaultValue={2} readOnly />
                                    </div>
                                    <div className="review pb-5 border-b border-[rgba(0,0,0,0.1)] w-full flex items-center justify-between">
                                        <div className="info w-[60%] flex items-center gap-2">
                                            <div className="img w-[80px] h-[80px] overflow-hidden rounded-full">
                                                <img src="https://thethaovanhoa.mediacdn.vn/372676912336973824/2022/12/16/avatar3-1671164179193908857633.jpg" className="w-full" />
                                            </div>

                                            <div className="w-[80%]">
                                                <h4 className="text-[16px]">Rinku Verma</h4>
                                                <h5 className="text-[13px] mb-0">2024-12-01</h5>
                                                <p className="mt-0 mb-0">In this single tutorial we will make a full stack eCommerce website using (MERN) React JS, MongoDB, Express and
                                                    Node JS or Online Store using React JS. We will make the e-commerce front-end website to display products, product cart and login
                                                    registration page using React JS.</p>
                                            </div>
                                        </div>
                                        <Rating name="size-small" defaultValue={2} readOnly />
                                    </div>
                                </div>

                                <br />

                                <div className="reviewForm bg-[#fafafa] p-4 rounded-md">
                                    <h2 className="text-[18px]">Add a review</h2>

                                    <form className="w-full mt-5">
                                        <TextField
                                            id="outlined-multiline-flexible"
                                            label="Write a review"
                                            className="w-full"
                                            multiline
                                            rows={5}
                                        />

                                        <br/><br/>
                                        <Rating name="size-small" defaultValue={2}/>

                                        <div className="flex items-center mt-5">
                                            <Button className="btn-org">Submit Review</Button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    }
                </div>

                <div className="container pt-8">
                    <h2 className="text-[20px] font-[600]">Related Products</h2>
                    <ProductsSlider items={6} />
                    
                </div>
            </section>
        </>
    )
}

export default ProductDetails