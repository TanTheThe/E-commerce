import React, { useContext, useState } from "react";
import TextField from '@mui/material/TextField';
import Button from "@mui/material/Button";
import { BsFillBagCheckFill } from "react-icons/bs";
import { MyContext } from "../../App";
import AddressManager from "../../components/Address";

const Checkout = () => {
    const [openAddressDialog, setOpenAddressDialog] = useState(false);
    const [selectedAddress, setSelectedAddress] = useState(null);

    const context = useContext(MyContext);

    const handleOpenDialog = () => {
        setOpenAddressDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenAddressDialog(false);
    };

    const handleSelectAddress = (addr) => {
        setSelectedAddress(addr);
        context.openAlertBox("success", "Đã chọn địa chỉ giao hàng");
    };

    return (
        <section className="py-10">
            <div className="container flex gap-5">
                <div className="leftCol w-[70%]">
                    <div className="card bg-white shadow-md p-5 rounded-md w-full">
                        <h1>Billing Details</h1>

                        <form className="w-full mt-5">
                            <div className="flex items-center gap-5 pb-5">
                                <div className="col w-[50%]">
                                    <TextField className="w-full" label="Full Name" variant="outlined" size="small" />
                                </div>
                                <div className="col w-[50%]">
                                    <TextField type="email" className="w-full" label="Email" variant="outlined" size="small" />
                                </div>
                            </div>

                            <h6 className="text-[14px] font-[500]">Địa chỉ được chọn</h6>
                            <div className="p-3 rounded text-sm bg-gray-50">
                                {selectedAddress ? (
                                    <>
                                        <p className="font-medium">{selectedAddress.line}</p>
                                        <p>{selectedAddress.ward_info?.name}, {selectedAddress.province_info?.name}</p>
                                        <p>{selectedAddress.country}</p>
                                    </>
                                ) : (
                                    <p className="text-gray-500">Chưa chọn địa chỉ giao hàng</p>
                                )}
                            </div>

                            <div className="flex items-center justify-center p-5 border border-dashed border-[rgba(0,0,0,0.2)] bg-[#f1faff] cursor-pointer
                                hover:bg-[#e7f3f9] mt-3" onClick={handleOpenDialog}>
                                <span className="text-[14px] font-[500]">Chọn địa chỉ giao hàng</span>
                            </div>
                        </form>
                    </div>
                </div>

                <div className="rightCol w-[30%]">
                    <div className="card shadow-md bg-white p-5 rounded-md">
                        <h2 className="mb-4">Your Order</h2>

                        <div className="flex items-center justify-between py-3 border-t border-b border-[rgba(0,0,0,0.1)]">
                            <span className="text-[14px] font-[600]">Product</span>
                            <span className="text-[14px] font-[600]">Subtotal</span>
                        </div>

                        <div className="mb-5 scroll max-h-[250px] overflow-y-scroll overflow-x-hidden pr-2">
                            <div className="flex items-center justify-between py-2">
                                <div className="part1 flex items-center gap-3">
                                    <div className="img w-[60px] h-[60px] object-cover overflow-hidden rounded-md group cursor-pointer">
                                        <img className="w-full transition-all group-hover:scale-105" src="https://api.spicezgold.com/download/file_1734690981297_011618e4-4682-4123-be80-1fb7737d34ad1714702040213RARERABBITMenComfortOpaqueCasualShirt1.jpg" />
                                    </div>

                                    <div className="info">
                                        <h4 className="text-[14px]">A-Line Kurti With Sh... </h4>
                                        <span className="text-[13px]">Qty: 1</span>
                                    </div>
                                </div>

                                <span className="text-[14px] font-[500]">$1,300.00</span>
                            </div>

                            <div className="flex items-center justify-between py-2">
                                <div className="part1 flex items-center gap-3">
                                    <div className="img w-[60px] h-[60px] object-cover overflow-hidden rounded-md group cursor-pointer">
                                        <img className="w-full transition-all group-hover:scale-105" src="https://api.spicezgold.com/download/file_1734690981297_011618e4-4682-4123-be80-1fb7737d34ad1714702040213RARERABBITMenComfortOpaqueCasualShirt1.jpg" />
                                    </div>

                                    <div className="info">
                                        <h4 className="text-[14px]">A-Line Kurti With Sh... </h4>
                                        <span className="text-[13px]">Qty: 1</span>
                                    </div>
                                </div>

                                <span className="text-[14px] font-[500]">$1,300.00</span>
                            </div>

                            <div className="flex items-center justify-between py-2">
                                <div className="part1 flex items-center gap-3">
                                    <div className="img w-[60px] h-[60px] object-cover overflow-hidden rounded-md group cursor-pointer">
                                        <img className="w-full transition-all group-hover:scale-105" src="https://api.spicezgold.com/download/file_1734690981297_011618e4-4682-4123-be80-1fb7737d34ad1714702040213RARERABBITMenComfortOpaqueCasualShirt1.jpg" />
                                    </div>

                                    <div className="info">
                                        <h4 className="text-[14px]">A-Line Kurti With Sh... </h4>
                                        <span className="text-[13px]">Qty: 1</span>
                                    </div>
                                </div>

                                <span className="text-[14px] font-[500]">$1,300.00</span>
                            </div>

                            <div className="flex items-center justify-between py-2">
                                <div className="part1 flex items-center gap-3">
                                    <div className="img w-[60px] h-[60px] object-cover overflow-hidden rounded-md group cursor-pointer">
                                        <img className="w-full transition-all group-hover:scale-105" src="https://api.spicezgold.com/download/file_1734690981297_011618e4-4682-4123-be80-1fb7737d34ad1714702040213RARERABBITMenComfortOpaqueCasualShirt1.jpg" />
                                    </div>

                                    <div className="info">
                                        <h4 className="text-[14px]">A-Line Kurti With Sh... </h4>
                                        <span className="text-[13px]">Qty: 1</span>
                                    </div>
                                </div>

                                <span className="text-[14px] font-[500]">$1,300.00</span>
                            </div>
                        </div>

                        <Button className="btn-org btn-lg w-full flex gap-2">
                            <BsFillBagCheckFill className="text-[20px]" />Checkout
                        </Button>
                    </div>
                </div>
            </div>

            <AddressManager
                isOpen={openAddressDialog}
                onClose={handleCloseDialog}
                selectedAddress={selectedAddress}
                onSelectAddress={handleSelectAddress}
            />
        </section>
    )
}

export default Checkout