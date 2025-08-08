import React, { useContext, useState } from "react";
import TextField from '@mui/material/TextField';
import Button from "@mui/material/Button";
import { BsFillBagCheckFill } from "react-icons/bs";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import CloseIcon from "@mui/icons-material/Close";
import IconButton from "@mui/material/IconButton";
import { deleteDataApi, getDataApi, postDataApi, putDataApi } from "../../utils/api";
import { MyContext } from "../../App";

const Checkout = () => {
    const [openAddressDialog, setOpenAddressDialog] = useState(false);
    const [addresses, setAddresses] = useState([]);
    const [selectedAddress, setSelectedAddress] = useState(null);
    const [addingNew, setAddingNew] = useState(false);
    const [newAddress, setNewAddress] = useState({
        line: "",
        street: "",
        ward: "",
        district: "",
        city: ""
    });
    const [editingId, setEditingId] = useState(null);

    const context = useContext(MyContext)

    const resetForm = () => {
        setNewAddress({
            line: "",
            street: "",
            ward: "",
            district: "",
            city: ""
        });
        setEditingId(null);
        setAddingNew(false);
    };

    const fetchAddresses = async () => {
        const res = await getDataApi("/customer/address");
        if (res.success) {
            setAddresses(res.data);
        }
    };

    const handleOpenDialog = () => {
        setOpenAddressDialog(true);
        fetchAddresses();
    };

    const handleCloseDialog = () => {
        setOpenAddressDialog(false);
        resetForm();
    };

    const handleSelectAddress = (addr) => {
        setSelectedAddress(addr);
        handleCloseDialog();
    };

    const handleDelete = async (id) => {
        const res = await deleteDataApi(`/customer/address/${id}`);
        if (res.success) {
            setAddresses((prev) => prev.filter((a) => a.id !== id));
            context.openAlertBox(
                "success", res?.message
            )
        } else {
            context.openAlertBox("error", res?.data?.detail?.message)
        }
    };

    const handleAddAddress = async () => {
        const res = await postDataApi("/customer/address", newAddress);
        console.log(res);
        if (res.success) {
            setAddresses([...addresses, res.data]);
            resetForm();
            context.openAlertBox(
                "success", res?.message
            )
        } else {
            context.openAlertBox("error", res?.data?.detail?.message)
        }
    };

    const handleUpdateAddress = async () => {
        const res = await putDataApi(`/customer/address/${editingId}`, newAddress);
        if (res.success) {
            const updated = res.data;

            setAddresses(prev => prev.map(addr => addr.id === editingId ? updated : addr));

            if (selectedAddress?.id === editingId) {
                setSelectedAddress(updated);
            }

            resetForm();
            context.openAlertBox("success", res?.message);
        } else {
            context.openAlertBox("error", res?.data?.detail?.message);
        }
    };

    const handleAddNewClick = () => {
        resetForm();
        setAddingNew(true);
    };

    const handleEditClick = (addr) => {
        console.log(addr);
        setEditingId(addr.id);
        setNewAddress({ ...addr });
        setAddingNew(true);
    };

    const handleCancelClick = () => {
        resetForm();
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
                            <div className="p-3 rounded text-sm">
                                {selectedAddress ? (
                                    <>
                                        <p>{selectedAddress.line}, {selectedAddress.street}</p>
                                        <p>{selectedAddress.ward}, {selectedAddress.district}, {selectedAddress.city}</p>
                                    </>
                                ) : (
                                    <p>Chưa chọn địa chỉ giao hàng</p>
                                )}
                            </div>

                            <div className="flex items-center justify-center p-5 border border-dashed border-[rgba(0,0,0,0.2)] bg-[#f1faff] cursor-pointer
                                hover:bg-[#e7f3f9]" onClick={handleOpenDialog}>
                                <span className="text-[14px] font-[500]">Choose Address</span>
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

            <Dialog open={openAddressDialog} onClose={handleCloseDialog} fullWidth maxWidth="md">
                <DialogTitle sx={{ m: 0, p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    {editingId ? 'Cập nhật địa chỉ' : addingNew ? 'Thêm địa chỉ mới' : 'Chọn địa chỉ'}
                    <IconButton onClick={handleCloseDialog} size="small">
                        <CloseIcon fontSize="small" />
                    </IconButton>
                </DialogTitle>
                <DialogContent dividers>
                    {!addingNew && (
                        <>
                            <div className="max-h-[300px] overflow-y-auto pr-2">
                                {addresses.map((addr) => (
                                    <div key={addr.id} className="border-b py-2">
                                        <div onClick={() => handleSelectAddress(addr)} className="cursor-pointer hover:bg-gray-100 p-2 rounded">
                                            <p>{addr.line}, {addr.street}</p>
                                            <p>{addr.ward}, {addr.district}, {addr.city}</p>
                                        </div>
                                        <div className="flex gap-3 mt-2 text-sm text-blue-600">
                                            <Button
                                                size="small"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleEditClick(addr);
                                                }}
                                            >
                                                Cập nhật
                                            </Button>
                                            <Button
                                                size="small"
                                                color="error"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleDelete(addr.id);
                                                }}
                                            >
                                                Xóa
                                            </Button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            <div className="mt-5">
                                <Button fullWidth className="btn-org btn-lg" onClick={handleAddNewClick}>
                                    + Thêm địa chỉ mới
                                </Button>
                            </div>
                        </>
                    )}
                    {addingNew && (
                        <div className="space-y-5 mt-2">
                            <div className="flex items-center gap-5">
                                <div className="col w-[100%]">
                                    <TextField className="w-full" label="Tỉnh/Thành phố" variant="outlined" size="small"
                                        value={newAddress.city}
                                        onChange={(e) => setNewAddress({ ...newAddress, city: e.target.value })} />
                                </div>
                            </div>
                            <div className="flex items-center gap-5">
                                <div className="col w-[100%]">
                                    <TextField
                                        className="w-full" label="Quận/Huyện" variant="outlined" size="small"
                                        value={newAddress.district}
                                        onChange={(e) => setNewAddress({ ...newAddress, district: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="flex items-center gap-5">
                                <div className="col w-[100%]">
                                    <TextField
                                        className="w-full" label="Phường/Xã" variant="outlined" size="small"
                                        value={newAddress.ward}
                                        onChange={(e) => setNewAddress({ ...newAddress, ward: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="flex items-center gap-5">
                                <div className="col w-[100%]">
                                    <TextField
                                        className="w-full" label="Tên đường" variant="outlined" size="small"
                                        value={newAddress.street}
                                        onChange={(e) => setNewAddress({ ...newAddress, street: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="flex items-center gap-5">
                                <div className="col w-[100%]">
                                    <TextField
                                        className="w-full" label="Chi tiết (Số nhà, Tòa nhà...)" variant="outlined" size="small"
                                        value={newAddress.line}
                                        onChange={(e) => setNewAddress({ ...newAddress, line: e.target.value })}
                                    />
                                </div>
                            </div>
                        </div>
                    )}
                </DialogContent>
                <DialogActions>
                    {addingNew && (
                        <>
                            <Button onClick={handleCancelClick} className="btn-org btn-border btn-lg">Hủy</Button>

                            {editingId ? (
                                <Button onClick={handleUpdateAddress} className="btn-org btn-lg">Cập nhật địa chỉ</Button>
                            ) : (
                                <Button onClick={handleAddAddress} className="btn-org btn-lg">Lưu địa chỉ</Button>
                            )}
                        </>
                    )}
                </DialogActions>
            </Dialog>
        </section>
    )
}

export default Checkout