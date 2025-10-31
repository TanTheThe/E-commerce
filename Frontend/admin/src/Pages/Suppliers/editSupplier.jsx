import React, { useState, useEffect } from "react";
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Grid,
    Box,
    Typography,
    IconButton,
    InputAdornment,
    Backdrop,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Switch,
    FormControlLabel,
    Chip,
    CircularProgress,
} from "@mui/material";
import { IoMdClose } from "react-icons/io";
import {
    MdPerson,
    MdPhone,
    MdEmail,
    MdLocationOn,
    MdAccountBalance,
    MdCreditCard,
    MdNote,
    MdInventory,
    MdCategory,
    MdDelete,
    MdArrowForward,
    MdSearch,
} from "react-icons/md";
import { getDataApi, putDataApi } from '../../utils/api';

const EditSupplierModal = ({ open, onClose, onSupplierUpdated, context, supplierToEdit }) => {
    const [supplierName, setSupplierName] = useState('');
    const [contactPerson, setContactPerson] = useState('');
    const [phone, setPhone] = useState('');
    const [email, setEmail] = useState('');
    const [address, setAddress] = useState('');
    const [bankAccount, setBankAccount] = useState('');
    const [bankName, setBankName] = useState('');
    const [creditLimit, setCreditLimit] = useState('');
    const [notes, setNotes] = useState('');
    const [isActive, setIsActive] = useState(true);

    const [categories, setCategories] = useState([]);
    const [products, setProducts] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [existingProducts, setExistingProducts] = useState([]);
    const [addedProducts, setAddedProducts] = useState([]);
    const [removedProductIds, setRemovedProductIds] = useState([]);
    const [updatedProducts, setUpdatedProducts] = useState([]);

    const [loading, setLoading] = useState(false);
    const [fetching, setFetching] = useState(false);
    const [loadingData, setLoadingData] = useState(false);
    const [nameError, setNameError] = useState('');

    const fetchSupplierDetail = async (supplierId) => {
        if (!supplierId) return;

        setFetching(true);
        try {
            const response = await getDataApi(`/admin/suppliers/${supplierId}`);

            if (response.success && response.data) {
                const data = response.data;
                setSupplierName(data.name || '');
                setContactPerson(data.contact_person || '');
                setPhone(data.phone || '');
                setEmail(data.email || '');
                setAddress(data.address || '');
                setBankAccount(data.bank_account || '');
                setBankName(data.bank_name || '');
                setCreditLimit(data.credit_limit !== undefined && data.credit_limit !== null ? data.credit_limit.toString() : '');
                setNotes(data.notes || '');
                setIsActive(data.is_active !== undefined ? data.is_active : true);

                if (data.products && Array.isArray(data.products)) {
                    setExistingProducts(data.products.map(p => ({
                        product_id: p.id,
                        product_name: p.name,
                        product_image: p.image,
                        product_status: p.status,
                        is_active: p.is_active !== undefined ? p.is_active : true,
                        notes: p.notes || ''
                    })));
                }
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || "Lỗi khi tải chi tiết nhà cung cấp.");
            }
        } catch (error) {
            console.error('Error fetching supplier detail:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi tải chi tiết nhà cung cấp.');
        } finally {
            setFetching(false);
        }
    };

    useEffect(() => {
        if (open) {
            fetchCategories();
        }
    }, [open]);

    useEffect(() => {
        if (supplierToEdit && open && supplierToEdit.id) {
            fetchSupplierDetail(supplierToEdit.id);
        }
    }, [supplierToEdit, open]);

    useEffect(() => {
        if (selectedCategory) {
            fetchProducts(selectedCategory);
        } else {
            setProducts([]);
        }
    }, [selectedCategory]);

    const fetchCategories = async () => {
        try {
            const response = await getDataApi('/admin/categories/all/select-box');
            if (response.success && response.data) {
                setCategories(response.data);
            }
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    };

    const fetchProducts = async (categoryId) => {
        setLoadingData(true);
        try {
            const url = `/admin/product/all/select-box?category_id=${categoryId}`;
            const response = await getDataApi(url);
            if (response.success && response.data) {
                setProducts(response.data);
            }
        } catch (error) {
            console.error('Error fetching products:', error);
        } finally {
            setLoadingData(false);
        }
    };

    const handleAddProduct = (product) => {
        if (!product) return;

        const existsInCurrent = existingProducts.find(p => p.product_id === product.id);
        const existsInAdded = addedProducts.find(p => p.product_id === product.id);

        if (!existsInCurrent && !existsInAdded) {
            setAddedProducts([...addedProducts, {
                product_id: product.id,
                product_name: product.name,
                is_active: true,
                notes: ''
            }]);
        }
    };

    const handleRemoveExistingProduct = (productId) => {
        setRemovedProductIds([...removedProductIds, productId]);
        setExistingProducts(existingProducts.filter(p => p.product_id !== productId));
        setUpdatedProducts(updatedProducts.filter(p => p.product_id !== productId));
    };

    const handleRemoveAddedProduct = (productId) => {
        setAddedProducts(addedProducts.filter(p => p.product_id !== productId));
    };

    const handleUpdateExistingProduct = (productId, field, value) => {
        setExistingProducts(existingProducts.map(p =>
            p.product_id === productId ? { ...p, [field]: value } : p
        ));

        const existingProduct = existingProducts.find(p => p.product_id === productId);
        if (existingProduct) {
            const updatedProduct = { ...existingProduct, [field]: value };
            const existingUpdateIndex = updatedProducts.findIndex(p => p.product_id === productId);

            if (existingUpdateIndex >= 0) {
                const newUpdated = [...updatedProducts];
                newUpdated[existingUpdateIndex] = updatedProduct;
                setUpdatedProducts(newUpdated);
            } else {
                setUpdatedProducts([...updatedProducts, updatedProduct]);
            }
        }
    };

    const handleUpdateAddedProduct = (productId, field, value) => {
        setAddedProducts(addedProducts.map(p =>
            p.product_id === productId ? { ...p, [field]: value } : p
        ));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!supplierName.trim()) {
            setNameError('Tên nhà cung cấp không được để trống');
            return;
        }

        if (!supplierToEdit?.id) {
            context.openAlertBox('error', 'Không tìm thấy ID nhà cung cấp cần cập nhật');
            return;
        }

        setLoading(true);
        try {
            const requestData = {
                name: supplierName.trim(),
                contact_person: contactPerson.trim() || null,
                phone: phone.trim() || null,
                email: email.trim() || null,
                address: address.trim() || null,
                bank_account: bankAccount.trim() || null,
                bank_name: bankName.trim() || null,
                credit_limit: creditLimit !== '' ? parseInt(creditLimit) : null,
                notes: notes.trim() || null,
                is_active: isActive
            };

            if (addedProducts.length > 0) {
                requestData.add_products = addedProducts.map(p => ({
                    product_id: p.product_id,
                    is_active: p.is_active,
                    notes: p.notes || null
                }));
            }

            if (removedProductIds.length > 0) {
                requestData.remove_product_ids = removedProductIds;
            }

            if (updatedProducts.length > 0) {
                requestData.update_products = updatedProducts.map(p => ({
                    product_id: p.product_id,
                    is_active: p.is_active,
                    notes: p.notes || null
                }));
            }

            const response = await putDataApi(`/admin/suppliers/${supplierToEdit.id}`, requestData);

            if (response.success) {
                context.openAlertBox('success', response.message || 'Cập nhật nhà cung cấp thành công!');
                onSupplierUpdated();
                handleClose();
            } else {
                context.openAlertBox('error', response?.data?.detail?.message || 'Có lỗi xảy ra khi cập nhật nhà cung cấp');
            }
        } catch (error) {
            console.error('Error updating supplier:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi cập nhật nhà cung cấp');
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setSupplierName('');
        setContactPerson('');
        setPhone('');
        setEmail('');
        setAddress('');
        setBankAccount('');
        setBankName('');
        setCreditLimit('');
        setNotes('');
        setIsActive(true);
        setExistingProducts([]);
        setAddedProducts([]);
        setRemovedProductIds([]);
        setUpdatedProducts([]);
        setSelectedCategory('');
        setSearchTerm('');
        setNameError('');
        onClose();
    };

    const formatCurrency = (value) => {
        if (!value) return '';
        return new Intl.NumberFormat('vi-VN').format(value);
    };

    const allProducts = [...existingProducts, ...addedProducts];

    const filteredProducts = products.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !existingProducts.find(ep => ep.product_id === p.id) &&
        !addedProducts.find(ap => ap.product_id === p.id)
    );

    return (
        <Dialog
            open={open}
            onClose={handleClose}
            maxWidth="lg"
            fullWidth
            PaperProps={{
                style: {
                    borderRadius: '20px',
                    maxHeight: '92vh',
                    boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
                    fontFamily: "'Montserrat', sans-serif"
                }
            }}
            BackdropComponent={Backdrop}
            BackdropProps={{
                style: {
                    backgroundColor: 'rgba(0, 0, 0, 0.75)',
                }
            }}
        >
            <DialogTitle sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '24px 32px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                borderBottom: 'none',
                fontFamily: "'Montserrat', sans-serif"
            }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box sx={{
                        width: 48,
                        height: 48,
                        borderRadius: '12px',
                        backgroundColor: 'rgba(255,255,255,0.2)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '24px'
                    }}>
                        ✏️
                    </Box>
                    <Box>
                        <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>
                            Chỉnh Sửa Nhà Cung Cấp
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9, fontSize: '13px' }}>
                            Mã: {supplierToEdit?.code}
                        </Typography>
                    </Box>
                </Box>
                <IconButton
                    onClick={handleClose}
                    sx={{
                        color: 'white',
                        backgroundColor: 'rgba(255,255,255,0.1)',
                        '&:hover': {
                            backgroundColor: 'rgba(255,255,255,0.2)',
                            transform: 'rotate(90deg)',
                            transition: 'all 0.3s ease'
                        }
                    }}
                >
                    <IoMdClose size={24} />
                </IconButton>
            </DialogTitle>

            <DialogContent sx={{ padding: '32px', overflowY: 'auto', backgroundColor: '#f8f9fc' }}>
                {fetching ? (
                    <Box sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        py: 8,
                        gap: 3
                    }}>
                        <CircularProgress size={60} sx={{ color: '#667eea' }} />
                        <Typography variant="h6" sx={{ color: '#64748b', fontWeight: 500 }}>
                            Đang tải thông tin nhà cung cấp...
                        </Typography>
                    </Box>
                ) : (
                    <form onSubmit={handleSubmit}>
                        <Grid container spacing={3}>
                            {/* Left Column - Basic Info */}
                            <Grid item xs={12} md={7}>
                                {/* Status Section */}
                                <div className={`rounded-2xl p-5 mb-4 border-2 ${isActive
                                        ? 'bg-green-50 border-green-500'
                                        : 'bg-red-50 border-red-500'
                                    }`}>
                                    <FormControlLabel
                                        control={
                                            <Switch
                                                checked={isActive}
                                                onChange={(e) => setIsActive(e.target.checked)}
                                                sx={{
                                                    '& .MuiSwitch-switchBase.Mui-checked': {
                                                        color: '#4caf50'
                                                    },
                                                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                                                        backgroundColor: '#4caf50'
                                                    }
                                                }}
                                            />
                                        }
                                        label={
                                            <div className="flex items-center gap-2">
                                                <span className="font-semibold text-gray-800">Trạng thái hoạt động</span>
                                                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${isActive
                                                        ? 'bg-green-600 text-white'
                                                        : 'bg-red-600 text-white'
                                                    }`}>
                                                    {isActive ? 'Đang hoạt động' : 'Ngừng hoạt động'}
                                                </span>
                                            </div>
                                        }
                                    />
                                </div>

                                {/* Basic Info */}
                                <div className="bg-white rounded-2xl p-6 mb-4 shadow-sm border border-gray-100">
                                    <div className="flex items-center mb-4">
                                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center text-white mr-3">
                                            <MdPerson size={22} />
                                        </div>
                                        <h3 className="text-lg font-semibold text-gray-800">Thông tin cơ bản</h3>
                                    </div>

                                    <Grid container spacing={2.5}>
                                        <Grid item xs={12}>
                                            <TextField
                                                autoFocus
                                                label="Tên Nhà Cung Cấp"
                                                fullWidth
                                                variant="outlined"
                                                value={supplierName}
                                                onChange={(e) => {
                                                    setSupplierName(e.target.value);
                                                    setNameError('');
                                                }}
                                                error={!!nameError}
                                                helperText={nameError}
                                                placeholder="Nhập tên công ty hoặc cá nhân"
                                                required
                                                sx={{
                                                    '& .MuiOutlinedInput-root': {
                                                        borderRadius: '12px',
                                                        backgroundColor: '#fafbfc'
                                                    }
                                                }}
                                            />
                                        </Grid>

                                        <Grid item xs={12} sm={6}>
                                            <TextField
                                                label="Người liên hệ"
                                                fullWidth
                                                variant="outlined"
                                                value={contactPerson}
                                                onChange={(e) => setContactPerson(e.target.value)}
                                                placeholder="Họ và tên"
                                                InputProps={{
                                                    startAdornment: (
                                                        <InputAdornment position="start">
                                                            <MdPerson color="#667eea" size={20} />
                                                        </InputAdornment>
                                                    )
                                                }}
                                                sx={{
                                                    '& .MuiOutlinedInput-root': {
                                                        borderRadius: '12px',
                                                        backgroundColor: '#fafbfc'
                                                    }
                                                }}
                                            />
                                        </Grid>

                                        <Grid item xs={12} sm={6}>
                                            <TextField
                                                label="Số điện thoại"
                                                type="tel"
                                                fullWidth
                                                variant="outlined"
                                                value={phone}
                                                onChange={(e) => setPhone(e.target.value)}
                                                placeholder="0901234567"
                                                InputProps={{
                                                    startAdornment: (
                                                        <InputAdornment position="start">
                                                            <MdPhone color="#667eea" size={20} />
                                                        </InputAdornment>
                                                    )
                                                }}
                                                sx={{
                                                    '& .MuiOutlinedInput-root': {
                                                        borderRadius: '12px',
                                                        backgroundColor: '#fafbfc'
                                                    }
                                                }}
                                            />
                                        </Grid>

                                        <Grid item xs={12}>
                                            <TextField
                                                label="Email"
                                                type="email"
                                                fullWidth
                                                variant="outlined"
                                                value={email}
                                                onChange={(e) => setEmail(e.target.value)}
                                                placeholder="contact@company.com"
                                                InputProps={{
                                                    startAdornment: (
                                                        <InputAdornment position="start">
                                                            <MdEmail color="#667eea" size={20} />
                                                        </InputAdornment>
                                                    )
                                                }}
                                                sx={{
                                                    '& .MuiOutlinedInput-root': {
                                                        borderRadius: '12px',
                                                        backgroundColor: '#fafbfc'
                                                    }
                                                }}
                                            />
                                        </Grid>

                                        <Grid item xs={12}>
                                            <TextField
                                                label="Địa chỉ"
                                                fullWidth
                                                variant="outlined"
                                                value={address}
                                                onChange={(e) => setAddress(e.target.value)}
                                                placeholder="Số nhà, đường, phường/xã, quận/huyện, tỉnh/thành phố"
                                                multiline
                                                rows={2}
                                                InputProps={{
                                                    startAdornment: (
                                                        <InputAdornment position="start" sx={{ alignSelf: 'flex-start', mt: 2 }}>
                                                            <MdLocationOn color="#667eea" size={20} />
                                                        </InputAdornment>
                                                    )
                                                }}
                                                sx={{
                                                    '& .MuiOutlinedInput-root': {
                                                        borderRadius: '12px',
                                                        backgroundColor: '#fafbfc'
                                                    }
                                                }}
                                            />
                                        </Grid>
                                    </Grid>
                                </div>

                                {/* Payment Info */}
                                <div className="bg-white rounded-2xl p-6 mb-4 shadow-sm border border-gray-100">
                                    <div className="flex items-center mb-4">
                                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-red-500 flex items-center justify-center text-white mr-3">
                                            <MdAccountBalance size={22} />
                                        </div>
                                        <h3 className="text-lg font-semibold text-gray-800">Thông tin thanh toán</h3>
                                    </div>

                                    <Grid container spacing={2.5}>
                                        <Grid item xs={12} sm={6}>
                                            <TextField
                                                label="Tên ngân hàng"
                                                fullWidth
                                                variant="outlined"
                                                value={bankName}
                                                onChange={(e) => setBankName(e.target.value)}
                                                placeholder="Vietcombank, ACB, Techcombank..."
                                                InputProps={{
                                                    startAdornment: (
                                                        <InputAdornment position="start">
                                                            <MdAccountBalance color="#f5576c" size={20} />
                                                        </InputAdornment>
                                                    )
                                                }}
                                                sx={{
                                                    '& .MuiOutlinedInput-root': {
                                                        borderRadius: '12px',
                                                        backgroundColor: '#fafbfc'
                                                    }
                                                }}
                                            />
                                        </Grid>

                                        <Grid item xs={12} sm={6}>
                                            <TextField
                                                label="Số tài khoản"
                                                fullWidth
                                                variant="outlined"
                                                value={bankAccount}
                                                onChange={(e) => setBankAccount(e.target.value)}
                                                placeholder="1234567890"
                                                InputProps={{
                                                    startAdornment: (
                                                        <InputAdornment position="start">
                                                            <MdCreditCard color="#f5576c" size={20} />
                                                        </InputAdornment>
                                                    )
                                                }}
                                                sx={{
                                                    '& .MuiOutlinedInput-root': {
                                                        borderRadius: '12px',
                                                        backgroundColor: '#fafbfc'
                                                    }
                                                }}
                                            />
                                        </Grid>

                                        <Grid item xs={12}>
                                            <TextField
                                                label="Hạn mức công nợ"
                                                type="number"
                                                fullWidth
                                                variant="outlined"
                                                value={creditLimit}
                                                onChange={(e) => setCreditLimit(e.target.value)}
                                                InputProps={{
                                                    inputProps: { min: 0 },
                                                    endAdornment: (
                                                        <InputAdornment position="end">
                                                            <Typography sx={{ color: '#667eea', fontWeight: 600 }}>
                                                                VNĐ
                                                            </Typography>
                                                        </InputAdornment>
                                                    )
                                                }}
                                                helperText={creditLimit ? `≈ ${formatCurrency(creditLimit)} VNĐ` : 'Để trống nếu không giới hạn'}
                                                sx={{
                                                    '& .MuiOutlinedInput-root': {
                                                        borderRadius: '12px',
                                                        backgroundColor: '#fafbfc'
                                                    }
                                                }}
                                            />
                                        </Grid>
                                    </Grid>
                                </div>

                                {/* Notes Section */}
                                <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                                    <div className="flex items-center mb-4">
                                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-400 to-cyan-400 flex items-center justify-center text-white mr-3">
                                            <MdNote size={22} />
                                        </div>
                                        <h3 className="text-lg font-semibold text-gray-800">Ghi chú bổ sung</h3>
                                    </div>

                                    <TextField
                                        label="Ghi chú chung"
                                        fullWidth
                                        multiline
                                        rows={4}
                                        variant="outlined"
                                        value={notes}
                                        onChange={(e) => setNotes(e.target.value)}
                                        placeholder="Thông tin bổ sung, điều khoản đặc biệt, lưu ý quan trọng về nhà cung cấp..."
                                        sx={{
                                            '& .MuiOutlinedInput-root': {
                                                borderRadius: '12px',
                                                backgroundColor: '#fafbfc'
                                            }
                                        }}
                                    />
                                </div>
                            </Grid>

                            {/* Right Column - Products */}
                            <Grid item xs={12} md={5}>
                                <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                                    <div className="flex items-center justify-between mb-4">
                                        <div className="flex items-center">
                                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center text-white mr-3">
                                                <MdInventory size={22} />
                                            </div>
                                            <div>
                                                <h3 className="text-lg font-semibold text-gray-800">Sản phẩm cung cấp</h3>
                                                <div className="flex gap-1.5 mt-1 flex-wrap">
                                                    {existingProducts.length > 0 && (
                                                        <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 font-semibold">
                                                            Hiện có: {existingProducts.length}
                                                        </span>
                                                    )}
                                                    {addedProducts.length > 0 && (
                                                        <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-semibold">
                                                            Mới: {addedProducts.length}
                                                        </span>
                                                    )}
                                                    {removedProductIds.length > 0 && (
                                                        <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700 font-semibold">
                                                            Xóa: {removedProductIds.length}
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-12 gap-3 mb-4">
                                        {/* Left Side - Category & Product List */}
                                        <div className="col-span-5 space-y-3">
                                            <FormControl fullWidth size="small">
                                                <InputLabel>Danh mục</InputLabel>
                                                <Select
                                                    value={selectedCategory}
                                                    onChange={(e) => setSelectedCategory(e.target.value)}
                                                    label="Danh mục"
                                                    sx={{
                                                        borderRadius: '10px',
                                                        backgroundColor: '#fafbfc'
                                                    }}
                                                >
                                                    <MenuItem value="">
                                                        <em>Chọn danh mục</em>
                                                    </MenuItem>
                                                    {categories.map((cat) => (
                                                        <MenuItem key={cat.id} value={cat.id}>
                                                            {cat.name}
                                                        </MenuItem>
                                                    ))}
                                                </Select>
                                            </FormControl>

                                            <TextField
                                                size="small"
                                                fullWidth
                                                placeholder="Tìm sản phẩm..."
                                                value={searchTerm}
                                                onChange={(e) => setSearchTerm(e.target.value)}
                                                InputProps={{
                                                    startAdornment: (
                                                        <InputAdornment position="start">
                                                            <MdSearch color="#94a3b8" size={20} />
                                                        </InputAdornment>
                                                    )
                                                }}
                                                sx={{
                                                    '& .MuiOutlinedInput-root': {
                                                        borderRadius: '10px',
                                                        backgroundColor: '#fafbfc'
                                                    }
                                                }}
                                            />

                                            <div className="border border-gray-200 rounded-xl max-h-96 overflow-y-auto bg-gray-50">
                                                {loadingData ? (
                                                    <div className="flex items-center justify-center py-8">
                                                        <div className="w-6 h-6 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
                                                    </div>
                                                ) : !selectedCategory ? (
                                                    <div className="text-center py-8 text-gray-400 text-sm">
                                                        <MdCategory size={32} className="mx-auto mb-2 opacity-50" />
                                                        <p>Chọn danh mục để xem sản phẩm</p>
                                                    </div>
                                                ) : filteredProducts.length === 0 ? (
                                                    <div className="text-center py-8 text-gray-400 text-sm">
                                                        <MdInventory size={32} className="mx-auto mb-2 opacity-50" />
                                                        <p>Không tìm thấy sản phẩm</p>
                                                    </div>
                                                ) : (
                                                    filteredProducts.map((product) => (
                                                        <div
                                                            key={product.id}
                                                            className="flex items-center justify-between p-2.5 border-b border-gray-200 hover:bg-white transition-colors group"
                                                        >
                                                            <span className="text-sm text-gray-700 flex-1 mr-2 line-clamp-2">
                                                                {product.name}
                                                            </span>
                                                            <button
                                                                type="button"
                                                                onClick={() => handleAddProduct(product)}
                                                                className="w-7 h-7 rounded-lg bg-purple-100 text-purple-600 hover:bg-purple-600 hover:text-white transition-all flex items-center justify-center flex-shrink-0 group-hover:scale-110"
                                                            >
                                                                <MdArrowForward size={16} />
                                                            </button>
                                                        </div>
                                                    ))
                                                )}
                                            </div>
                                        </div>

                                        {/* Right Side - Selected Products */}
                                        <div className="col-span-7">
                                            <div className="border border-purple-200 rounded-xl bg-purple-50/30 min-h-[450px] max-h-[500px] overflow-y-auto p-3">
                                                {allProducts.length === 0 ? (
                                                    <div className="flex flex-col items-center justify-center h-full text-gray-400 text-sm">
                                                        <MdInventory size={48} className="mb-3 opacity-30" />
                                                        <p className="font-medium">Chưa có sản phẩm</p>
                                                        <p className="text-xs mt-1">Chọn từ danh sách bên trái</p>
                                                    </div>
                                                ) : (
                                                    <div className="space-y-2">
                                                        {existingProducts.map((product) => (
                                                            <div
                                                                key={product.product_id}
                                                                className="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-md transition-shadow border-l-4 border-l-blue-500"
                                                            >
                                                                <div className="flex justify-between items-start mb-2">
                                                                    <div className="flex gap-2 flex-1">
                                                                        {product.product_image && (
                                                                            <img
                                                                                src={product.product_image}
                                                                                alt={product.product_name}
                                                                                className="w-12 h-12 object-cover rounded-lg border border-gray-200 flex-shrink-0"
                                                                            />
                                                                        )}
                                                                        <div className="flex-1 min-w-0">
                                                                            <div className="flex items-center gap-1 mb-1">
                                                                                <p className="text-sm font-semibold text-gray-800 line-clamp-2">
                                                                                    {product.product_name}
                                                                                </p>
                                                                                {product.product_status && (
                                                                                    <span className={`text-xs px-1.5 py-0.5 rounded flex-shrink-0 ${product.product_status === 'active'
                                                                                            ? 'bg-green-100 text-green-700'
                                                                                            : 'bg-gray-100 text-gray-600'
                                                                                        }`}>
                                                                                        {product.product_status === 'active' ? 'Active' : 'Inactive'}
                                                                                    </span>
                                                                                )}
                                                                            </div>
                                                                            <FormControlLabel
                                                                                control={
                                                                                    <Switch
                                                                                        checked={product.is_active}
                                                                                        onChange={(e) => handleUpdateExistingProduct(product.product_id, 'is_active', e.target.checked)}
                                                                                        size="small"
                                                                                        sx={{
                                                                                            '& .MuiSwitch-switchBase.Mui-checked': {
                                                                                                color: '#4caf50'
                                                                                            },
                                                                                            '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                                                                                                backgroundColor: '#4caf50'
                                                                                            }
                                                                                        }}
                                                                                    />
                                                                                }
                                                                                label={
                                                                                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${product.is_active
                                                                                            ? 'bg-green-100 text-green-700'
                                                                                            : 'bg-red-100 text-red-700'
                                                                                        }`}>
                                                                                        {product.is_active ? 'Hoạt động' : 'Tạm ngưng'}
                                                                                    </span>
                                                                                }
                                                                                sx={{ margin: 0 }}
                                                                            />
                                                                        </div>
                                                                    </div>
                                                                    <button
                                                                        type="button"
                                                                        onClick={() => handleRemoveExistingProduct(product.product_id)}
                                                                        className="w-8 h-8 rounded-lg bg-red-100 text-red-600 hover:bg-red-600 hover:text-white transition-colors flex items-center justify-center flex-shrink-0"
                                                                    >
                                                                        <MdDelete size={16} />
                                                                    </button>
                                                                </div>
                                                                <TextField
                                                                    size="small"
                                                                    fullWidth
                                                                    placeholder="Ghi chú..."
                                                                    value={product.notes}
                                                                    onChange={(e) => handleUpdateExistingProduct(product.product_id, 'notes', e.target.value)}
                                                                    variant="outlined"
                                                                    sx={{
                                                                        '& .MuiOutlinedInput-root': {
                                                                            borderRadius: '8px',
                                                                            fontSize: '13px'
                                                                        }
                                                                    }}
                                                                />
                                                            </div>
                                                        ))}

                                                        {addedProducts.map((product) => (
                                                            <div
                                                                key={product.product_id}
                                                                className="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-md transition-shadow border-l-4 border-l-green-500"
                                                            >
                                                                <div className="flex justify-between items-start mb-2">
                                                                    <div className="flex-1 mr-2">
                                                                        <div className="flex items-center gap-1.5 mb-1">
                                                                            <p className="text-sm font-semibold text-gray-800 line-clamp-2">
                                                                                {product.product_name}
                                                                            </p>
                                                                            <span className="bg-green-500 text-white text-xs px-2 py-0.5 rounded-full font-bold flex-shrink-0">
                                                                                MỚI
                                                                            </span>
                                                                        </div>
                                                                        <FormControlLabel
                                                                            control={
                                                                                <Switch
                                                                                    checked={product.is_active}
                                                                                    onChange={(e) => handleUpdateAddedProduct(product.product_id, 'is_active', e.target.checked)}
                                                                                    size="small"
                                                                                    sx={{
                                                                                        '& .MuiSwitch-switchBase.Mui-checked': {
                                                                                            color: '#4caf50'
                                                                                        },
                                                                                        '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                                                                                            backgroundColor: '#4caf50'
                                                                                        }
                                                                                    }}
                                                                                />
                                                                            }
                                                                            label={
                                                                                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${product.is_active
                                                                                        ? 'bg-green-100 text-green-700'
                                                                                        : 'bg-red-100 text-red-700'
                                                                                    }`}>
                                                                                    {product.is_active ? 'Hoạt động' : 'Tạm ngưng'}
                                                                                </span>
                                                                            }
                                                                            sx={{ margin: 0 }}
                                                                        />
                                                                    </div>
                                                                    <button
                                                                        type="button"
                                                                        onClick={() => handleRemoveAddedProduct(product.product_id)}
                                                                        className="w-8 h-8 rounded-lg bg-red-100 text-red-600 hover:bg-red-600 hover:text-white transition-colors flex items-center justify-center flex-shrink-0"
                                                                    >
                                                                        <MdDelete size={16} />
                                                                    </button>
                                                                </div>
                                                                <TextField
                                                                    size="small"
                                                                    fullWidth
                                                                    placeholder="Ghi chú..."
                                                                    value={product.notes}
                                                                    onChange={(e) => handleUpdateAddedProduct(product.product_id, 'notes', e.target.value)}
                                                                    variant="outlined"
                                                                    sx={{
                                                                        '& .MuiOutlinedInput-root': {
                                                                            borderRadius: '8px',
                                                                            fontSize: '13px'
                                                                        }
                                                                    }}
                                                                />
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </Grid>
                        </Grid>
                    </form>
                )}
            </DialogContent>

            <DialogActions sx={{
                padding: '20px 32px',
                backgroundColor: 'white',
                borderTop: '1px solid #e8eaf6',
                gap: 2
            }}>
                <Button
                    onClick={handleClose}
                    variant="outlined"
                    sx={{
                        borderRadius: '12px',
                        px: 4,
                        py: 1.2,
                        borderColor: '#e2e8f0',
                        color: '#64748b',
                        fontWeight: 600,
                        textTransform: 'none',
                        fontSize: '15px',
                        fontFamily: "'Montserrat', sans-serif",
                        '&:hover': {
                            borderColor: '#cbd5e1',
                            backgroundColor: '#f8fafc'
                        }
                    }}
                >
                    Hủy bỏ
                </Button>
                <Button
                    onClick={handleSubmit}
                    variant="contained"
                    disabled={loading || fetching || !supplierName.trim()}
                    sx={{
                        borderRadius: '12px',
                        px: 4,
                        py: 1.2,
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        fontWeight: 600,
                        textTransform: 'none',
                        fontSize: '15px',
                        fontFamily: "'Montserrat', sans-serif",
                        boxShadow: '0 4px 12px rgba(102,126,234,0.3)',
                        '&:hover': {
                            background: 'linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%)',
                            boxShadow: '0 6px 16px rgba(102,126,234,0.4)',
                            transform: 'translateY(-1px)'
                        },
                        '&:disabled': {
                            backgroundColor: '#cbd5e1',
                            color: '#94a3b8',
                            boxShadow: 'none'
                        },
                        transition: 'all 0.2s ease'
                    }}
                >
                    {loading ? (
                        <>
                            <Box
                                component="span"
                                sx={{
                                    width: 16,
                                    height: 16,
                                    border: '2px solid rgba(255,255,255,0.3)',
                                    borderTop: '2px solid white',
                                    borderRadius: '50%',
                                    display: 'inline-block',
                                    mr: 1,
                                    animation: 'spin 0.6s linear infinite',
                                    '@keyframes spin': {
                                        '0%': { transform: 'rotate(0deg)' },
                                        '100%': { transform: 'rotate(360deg)' }
                                    }
                                }}
                            />
                            Đang cập nhật...
                        </>
                    ) : (
                        '✓ Cập Nhật Nhà Cung Cấp'
                    )}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default EditSupplierModal;