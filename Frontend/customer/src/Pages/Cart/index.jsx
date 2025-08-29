import { BsFillBagCheckFill } from "react-icons/bs";
import Button from "@mui/material/Button";
import CartItems from "./cartItem";
import { useContext } from "react";
import { MyContext } from "../../App";

const CartPage = () => {
    const { checkoutItems, checkoutTotal } = useContext(MyContext);

    const shippingFee = 0;
    const finalTotal = checkoutTotal + shippingFee;

    return (
        <section className="section py-10 pb-10">
            <div className="container w-[80%] max-w-[80%] flex gap-5">
                <div className="leftPart w-[70%]">
                    <div className="shadow-md rounded-md bg-white">
                        <div className="py-2 px-3 border-b border-[rgba(0,0,0,0.1)]">
                            <h2>Your Cart</h2>
                            <p className="mt-0">There are
                                <span className="font-bold text-[#ff5252]"> {checkoutItems.length} </span>
                                products in your cart
                            </p>
                        </div>

                        <CartItems />
                    </div>
                </div>

                <div className="rightPart w-[30%]">
                    <div className="shadow-md rounded-md bg-white p-5">
                        <h3 className="pb-3 border-b border-[rgba(0,0,0,0.1)]">Cart Totals</h3>

                        <p className="flex items-center justify-between">
                            <span className="text-[14px] font-[500]">Subtotal</span>
                            <span className="text-[#ff5252] font-bold">
                                {checkoutTotal?.toLocaleString('vi-VN')}đ
                            </span>
                        </p>
                        <p className="flex items-center justify-between">
                            <span className="text-[14px] font-[500]">Shipping</span>
                            <span className="font-bold">Free</span>
                        </p>
                        <p className="flex items-center justify-between">
                            <span className="text-[14px] font-[500]">Estimate for</span>
                            <span className="font-bold">Vietnam</span>
                        </p>
                        <p className="flex items-center justify-between">
                            <span className="text-[14px] font-[500]">Total</span>
                            <span className="text-[#ff5252] font-bold">
                                {finalTotal?.toLocaleString('vi-VN')}đ
                            </span>
                        </p>

                        <br />

                        <Button
                            className="btn-org btn-lg w-full flex gap-2"
                            disabled={checkoutItems.length === 0}
                        >
                            <BsFillBagCheckFill className="text-[20px]" />
                            Checkout ({checkoutItems.length} items)
                        </Button>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default CartPage;